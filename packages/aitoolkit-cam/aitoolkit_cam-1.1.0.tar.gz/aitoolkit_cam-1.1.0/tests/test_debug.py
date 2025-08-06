# 调试测试 - 逐步检查功能
# =========================
#
# 这个测试逐步检查每个功能点，帮助定位问题

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_imports():
    """测试导入"""
    print("🔍 测试1: 检查模块导入...")
    try:
        import cv2
        print("   ✅ OpenCV导入成功")
        
        import requests
        print("   ✅ requests导入成功")
        
        from aitoolkit_cam import Camera
        print("   ✅ Camera类导入成功")
        
        from aitoolkit_cam import add_camera_routes, camera_manager
        print("   ✅ FastAPI集成模块导入成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_camera_hardware():
    """测试摄像头硬件"""
    print("\n🔍 测试2: 检查摄像头硬件...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"   ✅ 摄像头可用，分辨率: {w}x{h}")
                cap.release()
                return True
            else:
                print("   ⚠️  摄像头打开但无法读取帧")
                cap.release()
                return False
        else:
            print("   ❌ 无法打开摄像头设备")
            return False
    except Exception as e:
        print(f"   ❌ 摄像头检测失败: {e}")
        return False

def test_backend_detection():
    """测试后端服务检测"""
    print("\n🔍 测试3: 检查后端服务...")
    try:
        import requests
        
        # 检查常见端口
        backends = [
            ("http://localhost:8000/camera", "FastAPI后端"),
            ("http://127.0.0.1:8000/camera", "FastAPI后端"),
            ("http://localhost:5000/camera", "Flask后端"),
        ]
        
        for url, name in backends:
            try:
                response = requests.get(f"{url}/status", timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 检测到{name}在运行")
                    print(f"      地址: {url}")
                    print(f"      状态: {data}")
                    return url
            except:
                continue
        
        print("   ℹ️  未检测到后端服务")
        print("      这是正常的，Camera会使用简单模式")
        return None
    except Exception as e:
        print(f"   ❌ 后端检测失败: {e}")
        return None

def test_camera_creation():
    """测试Camera对象创建"""
    print("\n🔍 测试4: 创建Camera对象...")
    try:
        from aitoolkit_cam import Camera
        cam = Camera(source=0, width=640, height=480, max_frames=5)
        print(f"   ✅ Camera对象创建成功")
        print(f"   模式: {'简单模式' if cam._simple_mode else '后端模式'}")
        if hasattr(cam, '_backend_url') and cam._backend_url:
            print(f"   后端URL: {cam._backend_url}")
        return cam
    except Exception as e:
        print(f"   ❌ Camera创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_camera_workflow():
    """测试完整的摄像头工作流程"""
    print("\n🔍 测试5: 完整工作流程...")
    try:
        from aitoolkit_cam import Camera
        import cv2
        
        print("   创建Camera实例...")
        cam = Camera(source=0, width=640, height=480, max_frames=3)
        
        print("   启动摄像头...")
        url = cam.start()
        print(f"   ✅ 启动成功，URL: {url}")
        
        print("   测试帧读取和处理...")
        frame_count = 0
        for frame in cam:
            if frame is None:
                continue
            
            # 简单处理
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            processed = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            # 显示
            cam.show(processed)
            
            frame_count += 1
            print(f"   📈 处理帧 {frame_count}/3")
            
            if frame_count >= 3:
                break
        
        print("   停止摄像头...")
        cam.stop()
        print("   ✅ 工作流程测试成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastapi_integration():
    """测试FastAPI集成"""
    print("\n🔍 测试6: FastAPI集成...")
    try:
        from fastapi import FastAPI
        from aitoolkit_cam import add_camera_routes, camera_manager
        
        # 创建测试应用
        app = FastAPI()
        add_camera_routes(app, prefix="/camera")
        
        print("   ✅ FastAPI路由添加成功")
        print("   ✅ camera_manager可用")
        print(f"   当前状态: {'运行中' if camera_manager.is_running else '未运行'}")
        
        return True
    except Exception as e:
        print(f"   ❌ FastAPI集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 aitoolkit_cam 功能调试测试")
    print("=" * 60)
    print("这个测试会逐步检查各个功能模块")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("摄像头硬件", test_camera_hardware),
        ("后端服务检测", lambda: test_backend_detection() is not None),
        ("Camera对象创建", lambda: test_camera_creation() is not None),
        ("完整工作流程", test_camera_workflow),
        ("FastAPI集成", test_fastapi_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print()
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ 测试 '{test_name}' 异常: {e}")
            results.append((test_name, False))
    
    # 总结报告
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:<15}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n📈 总计: {passed}/{total} 测试通过 ({success_rate:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！摄像头功能正常")
        print("✨ 可以安全使用 aitoolkit_cam")
    elif passed >= total * 0.8:
        print("\n⚠️  大部分测试通过，基本功能可用")
        print("📝 建议查看失败的测试项")
    else:
        print("\n❌ 多个测试失败，请检查环境配置")
        print("🔧 建议检查摄像头设备、依赖安装等")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 