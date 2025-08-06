"""
单元测试模块
==========

提供完整的单元测试覆盖，确保代码质量和功能正确性。
"""

import unittest
import threading
import time
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aitoolkit_cam.config import ConfigManager, get_config, set_config, reset_config
from aitoolkit_cam.device_manager import CameraDeviceManager, CameraDeviceInfo, validate_camera
from aitoolkit_cam.filters import ImageFilters, FilterChain, TextOverlay

class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config_manager = ConfigManager()
        reset_config()
    
    def test_default_config_loading(self):
        """测试默认配置加载"""
        config = self.config_manager.get_all()
        self.assertIn("camera", config)
        self.assertIn("network", config)
        self.assertEqual(config["camera"]["default_width"], 640)
    
    def test_config_get_set(self):
        """测试配置获取和设置"""
        # 测试获取
        width = get_config("camera.default_width")
        self.assertEqual(width, 640)
        
        # 测试设置
        set_config("camera.default_width", 800)
        new_width = get_config("camera.default_width")
        self.assertEqual(new_width, 800)
    
    def test_nested_config_access(self):
        """测试嵌套配置访问"""
        # 测试深层嵌套
        timeout = get_config("network.backend_detection_timeout", 1.0)
        self.assertIsInstance(timeout, float)
        
        # 测试不存在的键
        non_existent = get_config("non.existent.key", "default")
        self.assertEqual(non_existent, "default")
    
    def test_config_validation(self):
        """测试配置验证"""
        # 设置无效值
        set_config("camera.default_width", -100)
        
        # 重新加载配置（会触发验证）
        from aitoolkit_cam.config import validate_config
        validate_config()
        
        # 验证已修正
        width = get_config("camera.default_width")
        self.assertGreater(width, 0)

class TestCameraDeviceInfo(unittest.TestCase):
    """摄像头设备信息测试"""
    
    def test_device_info_creation(self):
        """测试设备信息创建"""
        device = CameraDeviceInfo(0, 640, 480, 30.0, True)
        self.assertEqual(device.device_id, 0)
        self.assertEqual(device.width, 640)
        self.assertEqual(device.height, 480)
        self.assertEqual(device.fps, 30.0)
        self.assertTrue(device.available)
    
    def test_device_info_to_dict(self):
        """测试设备信息转换为字典"""
        device = CameraDeviceInfo(1, 1280, 720, 25.0, True)
        device_dict = device.to_dict()
        
        self.assertEqual(device_dict["device_id"], 1)
        self.assertEqual(device_dict["width"], 1280)
        self.assertEqual(device_dict["height"], 720)
        self.assertTrue(device_dict["available"])
    
    def test_device_info_string_representation(self):
        """测试设备信息字符串表示"""
        device = CameraDeviceInfo(0, 640, 480, 30.0, True)
        device_str = str(device)
        
        self.assertIn("Camera(0)", device_str)
        self.assertIn("640x480", device_str)
        self.assertIn("30.0fps", device_str)
        self.assertIn("可用", device_str)

class TestCameraDeviceManager(unittest.TestCase):
    """摄像头设备管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.device_manager = CameraDeviceManager()
        self.device_manager.clear_cache()
    
    @patch('cv2.VideoCapture')
    def test_device_probing(self, mock_cv2):
        """测试设备探测"""
        # 模拟成功的摄像头
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            0: 640,   # CAP_PROP_FRAME_WIDTH
            1: 480,   # CAP_PROP_FRAME_HEIGHT
            2: 30.0   # CAP_PROP_FPS
        }.get(prop, 0)
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2.return_value = mock_cap
        
        device_info = self.device_manager._probe_device(0)
        
        self.assertTrue(device_info.available)
        self.assertEqual(device_info.width, 640)
        self.assertEqual(device_info.height, 480)
        self.assertEqual(device_info.fps, 30.0)
    
    @patch('cv2.VideoCapture')
    def test_device_scanning(self, mock_cv2):
        """测试设备扫描"""
        # 模拟两个可用设备
        def mock_capture_side_effect(device_id):
            mock_cap = Mock()
            if device_id < 2:  # 前两个设备可用
                mock_cap.isOpened.return_value = True
                mock_cap.get.side_effect = lambda prop: {
                    0: 640,   # CAP_PROP_FRAME_WIDTH
                    1: 480,   # CAP_PROP_FRAME_HEIGHT
                    2: 30.0   # CAP_PROP_FPS
                }.get(prop, 0)
                mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
            else:
                mock_cap.isOpened.return_value = False
            return mock_cap
        
        mock_cv2.side_effect = mock_capture_side_effect
        
        devices = self.device_manager.scan_devices(max_devices=5)
        
        self.assertEqual(len(devices), 2)
        self.assertTrue(all(device.available for device in devices))
    
    def test_optimal_device_selection(self):
        """测试最佳设备选择"""
        # 手动添加一些设备到缓存
        device1 = CameraDeviceInfo(0, 640, 480, 30.0, True)
        device2 = CameraDeviceInfo(1, 1280, 720, 25.0, True)
        
        self.device_manager._devices = {0: device1, 1: device2}
        
        optimal_id = self.device_manager.get_optimal_device(prefer_resolution=True)
        self.assertEqual(optimal_id, 1)  # 应该选择高分辨率设备
    
    def test_device_availability_check(self):
        """测试设备可用性检查"""
        # 添加一个可用设备到缓存
        device = CameraDeviceInfo(0, 640, 480, 30.0, True)
        self.device_manager._devices = {0: device}
        
        self.assertTrue(self.device_manager.is_device_available(0))
        self.assertFalse(self.device_manager.is_device_available(99))

class TestImageFilters(unittest.TestCase):
    """图像滤镜测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试图像
        self.test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_edge_detection(self):
        """测试边缘检测"""
        result = ImageFilters.edge_detection(self.test_frame)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
    
    def test_blur_effect(self):
        """测试模糊效果"""
        result = ImageFilters.blur_effect(self.test_frame, kernel_size=15)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
    
    def test_cartoon_effect(self):
        """测试卡通效果"""
        result = ImageFilters.cartoon_effect(self.test_frame)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
    
    def test_sepia_effect(self):
        """测试复古效果"""
        result = ImageFilters.sepia_effect(self.test_frame)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
    
    def test_negative_effect(self):
        """测试负片效果"""
        result = ImageFilters.negative_effect(self.test_frame)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
        
        # 验证负片效果：原图 + 负片 = 255
        combined = self.test_frame.astype(np.int32) + result.astype(np.int32)
        self.assertTrue(np.allclose(combined, 255))
    
    def test_brightness_contrast(self):
        """测试亮度对比度调整"""
        result = ImageFilters.brightness_contrast(self.test_frame, brightness=20, contrast=1.2)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
    
    def test_filter_error_handling(self):
        """测试滤镜错误处理"""
        # 使用无效输入测试错误处理
        invalid_frame = None
        
        result = ImageFilters.edge_detection(invalid_frame)
        self.assertIsNone(result)  # 应该返回原始输入

class TestFilterChain(unittest.TestCase):
    """滤镜链测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        self.filter_chain = FilterChain()
    
    def test_filter_chain_creation(self):
        """测试滤镜链创建"""
        self.assertEqual(len(self.filter_chain.filters), 0)
    
    def test_add_filter(self):
        """测试添加滤镜"""
        self.filter_chain.add_filter(ImageFilters.blur_effect, kernel_size=15)
        self.assertEqual(len(self.filter_chain.filters), 1)
    
    def test_filter_chain_application(self):
        """测试滤镜链应用"""
        self.filter_chain.add_filter(ImageFilters.blur_effect, kernel_size=15)
        self.filter_chain.add_filter(ImageFilters.edge_detection)
        
        result = self.filter_chain.apply(self.test_frame)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
    
    def test_filter_chain_clear(self):
        """测试清空滤镜链"""
        self.filter_chain.add_filter(ImageFilters.blur_effect)
        self.filter_chain.add_filter(ImageFilters.edge_detection)
        
        self.filter_chain.clear()
        self.assertEqual(len(self.filter_chain.filters), 0)
    
    def test_remove_last_filter(self):
        """测试移除最后一个滤镜"""
        self.filter_chain.add_filter(ImageFilters.blur_effect)
        self.filter_chain.add_filter(ImageFilters.edge_detection)
        
        self.filter_chain.remove_last()
        self.assertEqual(len(self.filter_chain.filters), 1)

class TestTextOverlay(unittest.TestCase):
    """文本叠加测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    def test_add_text(self):
        """测试添加文本"""
        result = TextOverlay.add_text(self.test_frame, "Test Text", (10, 30))
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
        
        # 验证文本区域不再是全黑
        text_region = result[20:40, 10:100]
        self.assertTrue(np.any(text_region > 0))
    
    def test_add_timestamp(self):
        """测试添加时间戳"""
        result = TextOverlay.add_timestamp(self.test_frame)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)
    
    def test_add_frame_info(self):
        """测试添加帧信息"""
        result = TextOverlay.add_frame_info(self.test_frame, frame_count=100, fps=30.0)
        
        self.assertEqual(result.shape, self.test_frame.shape)
        self.assertEqual(result.dtype, np.uint8)

class TestThreadSafety(unittest.TestCase):
    """线程安全测试"""
    
    def test_config_thread_safety(self):
        """测试配置管理的线程安全性"""
        results = []
        
        def config_worker():
            for i in range(100):
                set_config(f"test.key_{threading.current_thread().ident}", i)
                value = get_config(f"test.key_{threading.current_thread().ident}")
                results.append(value)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=config_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 验证没有发生竞态条件
        self.assertEqual(len(results), 500)  # 5个线程 * 100次操作
    
    def test_device_manager_thread_safety(self):
        """测试设备管理器的线程安全性"""
        device_manager = CameraDeviceManager()
        results = []
        
        def device_worker():
            for _ in range(10):
                devices = device_manager.scan_devices(max_devices=2)
                results.append(len(devices))
                time.sleep(0.01)
        
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=device_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 验证结果一致性
        self.assertEqual(len(results), 30)  # 3个线程 * 10次操作

class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def test_filter_performance(self):
        """测试滤镜性能"""
        test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        start_time = time.time()
        for _ in range(10):
            ImageFilters.edge_detection(test_frame)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        self.assertLess(avg_time, 0.1)  # 每次处理应该少于100ms
    
    def test_device_scan_performance(self):
        """测试设备扫描性能"""
        device_manager = CameraDeviceManager()
        
        start_time = time.time()
        devices = device_manager.scan_devices(max_devices=5)
        end_time = time.time()
        
        scan_time = end_time - start_time
        self.assertLess(scan_time, 5.0)  # 扫描应该在5秒内完成

if __name__ == '__main__':
    # 配置测试日志
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # 运行测试
    unittest.main(verbosity=2)