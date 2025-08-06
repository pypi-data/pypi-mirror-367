# aitoolkit_cam

简单易用的摄像头库，专为ARM设备和Jupyter环境设计。

## 🚀 特性

- **零配置使用** - 自动检测后端服务，智能选择运行模式
- **用户代码不变** - Jupyter中的代码保持完全不变
- **一行FastAPI集成** - 轻松集成到现有FastAPI应用
- **多种架构支持** - 简单模式、后端集成、Producer/Hub分布式
- **完整向后兼容** - 支持所有原有使用方式
- **高级图像处理** - 内置多种图像滤镜和文本叠加功能
- **设备管理** - 智能检测和选择最佳摄像头设备
- **配置管理** - 灵活的配置系统，支持自定义设置

## 📦 安装

```bash
# 基本安装
pip install aitoolkit-cam

# 安装带FastAPI支持的版本
pip install aitoolkit-cam[fastapi]

# 安装开发版本（包含测试工具）
pip install aitoolkit-cam[dev]

# 安装所有功能
pip install aitoolkit-cam[all]
```

## 🎯 快速开始

### 基本使用（Jupyter/独立）

```python
from aitoolkit_cam import Camera
import cv2

# 用户代码保持不变，自动适配运行环境
with Camera(source=0, max_frames=100) as cam:
    url = cam.start()  # 自动检测后端或启动内置服务
    print(f"视频流: {url}")
    
    for frame in cam:
        # OpenCV处理
        edges = cv2.Canny(frame, 80, 160)
        display_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # 显示处理后的帧
        cam.show(display_frame)
```

### FastAPI集成（一行集成）

```python
from fastapi import FastAPI
from aitoolkit_cam import add_camera_routes

app = FastAPI()

# 只需一行代码即可集成摄像头功能！
add_camera_routes(app, prefix="/camera")

# 现在你的FastAPI应用有了完整的摄像头功能：
# - GET  /camera/        - 控制页面
# - GET  /camera/stream  - MJPEG视频流  
# - GET  /camera/start   - 启动摄像头
# - GET  /camera/stop    - 停止摄像头
# - GET  /camera/status  - 获取状态
# - POST /camera/upload  - 接收处理后的帧
```

### 使用内置滤镜

```python
from aitoolkit_cam import Camera, ImageFilters, TextOverlay

with Camera(source=0) as cam:
    cam.start()
    
    for frame in cam:
        # 应用边缘检测滤镜
        edges = ImageFilters.edge_detection(frame, 80, 160)
        
        # 添加时间戳
        result = TextOverlay.add_timestamp(edges)
        
        # 显示处理后的帧
        cam.show(result)
```

### 使用滤镜链

```python
from aitoolkit_cam import Camera, FilterChain, ImageFilters

# 创建滤镜链
filter_chain = FilterChain()
filter_chain.add_filter(ImageFilters.blur_effect, kernel_size=5)
filter_chain.add_filter(ImageFilters.edge_detection, low_threshold=50, high_threshold=150)
filter_chain.add_filter(ImageFilters.brightness_contrast, brightness=10, contrast=1.2)

with Camera(source=0) as cam:
    cam.start()
    
    for frame in cam:
        # 应用滤镜链
        result = filter_chain.apply(frame)
        
        # 显示处理后的帧
        cam.show(result)
```

### 设备管理

```python
from aitoolkit_cam import list_available_cameras, get_optimal_camera, Camera

# 列出所有可用摄像头
devices = list_available_cameras()
for device in devices:
    print(f"设备 {device.device_id}: {device.width}x{device.height} @ {device.fps}fps")

# 获取最佳摄像头设备
optimal_device = get_optimal_camera()

# 使用最佳设备
with Camera(source=optimal_device) as cam:
    cam.start()
    # ...处理逻辑...
```

### 配置管理

```python
from aitoolkit_cam import get_config, set_config, save_config, load_config

# 获取配置
width = get_config("camera.default_width")  # 默认640
fps = get_config("camera.default_fps")      # 默认20

# 修改配置
set_config("camera.default_width", 1280)
set_config("camera.default_height", 720)

# 保存配置到文件
save_config("my_config.json")

# 加载配置
load_config("my_config.json")
```

## 🏗️ 架构模式

### 1. 智能自适应模式（推荐）

Camera类自动检测运行环境：

- **有后端服务** → 自动连接到FastAPI后端
- **无后端服务** → 启动内置Flask服务器

```python
# 用户代码完全相同，系统自动适配
with Camera() as cam:
    url = cam.start()  # 智能选择模式
    # ... 处理逻辑 ...
```

### 2. FastAPI集成模式

将摄像头功能集成到现有FastAPI应用：

```python
# 后端服务（管理员启动）
from fastapi import FastAPI
from aitoolkit_cam import add_camera_routes

app = FastAPI()
add_camera_routes(app)

if __name__ == "__main__":
    import uvicorn
    # 支持多个端口：18001, 5000, 6000, 7000, 8000, 9000
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```python
# 用户代码（Jupyter中）
with Camera() as cam:  # 自动检测多个端口的后端服务
    url = cam.start()  # 连接到第一个可用的后端服务
    # ... 处理逻辑 ...
```

**🔍 多端口自动检测**

aitoolkit_cam 支持自动检测多个端口的后端服务：

- **默认检测端口**：18001, 5000, 6000, 7000, 8000, 9000
- **检测顺序**：按配置文件中的顺序依次检测
- **自动连接**：连接到第一个响应的服务
- **灵活配置**：可通过配置文件自定义端口列表

```python
# 启动不同端口的后端服务
python examples/multi_port_backend_demo.py --port 6000
python examples/multi_port_backend_demo.py --port 7000

# 用户代码自动检测并连接
with Camera() as cam:
    url = cam.start()  # 自动连接到可用服务
```

### 3. Producer/Hub分布式模式

支持传统的分布式架构：

```python
# Hub服务器
from aitoolkit_cam import Hub
hub = Hub(port=5000)
hub.run()
```

```python
# Producer客户端
from aitoolkit_cam import Camera
with Camera(hub_url="http://hub-server:5000") as cam:
    # ... 分布式处理 ...
```

## 📝 API参考

### Camera类

```python
Camera(
    source=0,           # 摄像头设备ID
    width=640,          # 视频宽度
    height=480,         # 视频高度
    fps=20,             # 帧率
    max_frames=None,    # 最大帧数（None=无限）
    port=9000           # 简单模式使用的端口
)
```

**方法：**
- `start()` - 启动摄像头，返回视频流URL
- `stop()` - 停止摄像头
- `read(timeout=1.0)` - 读取原始帧
- `show(frame)` - 显示处理后的帧
- `frame_count` - 当前帧计数

**支持的语法：**
- `with Camera() as cam:` - 上下文管理器
- `for frame in cam:` - 迭代器模式

### 图像处理

```python
# 滤镜
ImageFilters.edge_detection(frame, low_threshold=50, high_threshold=150)
ImageFilters.blur_effect(frame, kernel_size=15)
ImageFilters.cartoon_effect(frame)
ImageFilters.sepia_effect(frame)
ImageFilters.negative_effect(frame)
ImageFilters.brightness_contrast(frame, brightness=0, contrast=1.0)
ImageFilters.color_filter(frame, color_mask=(255, 255, 255))
ImageFilters.emboss_effect(frame)
ImageFilters.motion_blur(frame, size=15, angle=0)

# 文本叠加
TextOverlay.add_text(frame, text, position=(10, 30), font_scale=1.0)
TextOverlay.add_timestamp(frame)
TextOverlay.add_frame_info(frame, frame_count, fps=30.0)

# 滤镜链
chain = FilterChain()
chain.add_filter(ImageFilters.blur_effect, kernel_size=5)
chain.add_filter(ImageFilters.edge_detection)
result = chain.apply(frame)

# 预定义滤镜
vintage_filter = create_vintage_filter()
artistic_filter = create_artistic_filter()
dramatic_filter = create_dramatic_filter()
```

### 设备管理

```python
# 列出可用摄像头
devices = list_available_cameras()

# 获取最佳摄像头
device_id = get_optimal_camera()

# 验证摄像头设备
is_valid = validate_camera(device_id)

# 获取设备信息
info = get_camera_info(device_id)

# 获取设备能力
capabilities = get_camera_capabilities(device_id)
```

### 配置管理

```python
# 获取配置
value = get_config("section.key", default_value)

# 设置配置
set_config("section.key", new_value)

# 加载配置文件
load_config("config.json")

# 保存配置到文件
save_config("config.json")

# 重置为默认配置
reset_config()
```

### FastAPI集成函数

```python
add_camera_routes(app, prefix="/camera")
setup_background_processing(app, frame_processor=None, fps=20)
```

## 🔧 使用场景

### 场景1：Jupyter实验环境

```python
# 研究人员在Jupyter中使用
with Camera(max_frames=100) as cam:
    cam.start()
    for frame in cam:
        # 实时图像处理实验
        result = my_algorithm(frame)
        cam.show(result)
```

### 场景2：Web应用集成

```python
# 集成到现有Web应用
app = FastAPI()
add_camera_routes(app)

# 用户通过Web界面控制摄像头
# 访问 /camera/ 查看控制页面
# 访问 /camera/stream 查看视频流
```

### 场景3：分布式处理

```python
# 多个摄像头节点连接到中央Hub
# 适合监控、多点采集等场景
```

## 🚦 测试

项目包含完整的测试套件：

```bash
# 单元测试
python -m unittest tests/test_unit.py

# 功能调试测试
python tests/test_debug.py

# 用户模式测试
python tests/test_simple_mode.py

# 后端服务测试  
python tests/test_backend_service.py
```

## 🐳 Docker支持

项目提供了Docker支持，可以轻松部署：

```bash
# 构建Docker镜像
docker build -t aitoolkit-cam .

# 运行Docker容器
docker run -p 8000:8000 aitoolkit-cam

# 使用docker-compose
docker-compose up
```

## 📋 开发指南

### 测试步骤

1. **单元测试**：
   ```bash
   python -m unittest tests/test_unit.py
   ```

2. **独立测试**：
   ```bash
   python tests/test_simple_mode.py
   ```

3. **集成测试**：
   ```bash
   # 终端1：启动后端
   python tests/test_backend_service.py
   
   # 终端2：运行用户代码
   python tests/test_simple_mode.py
   ```

### 故障排除

如果遇到问题：

1. 运行调试测试：`python tests/test_debug.py`
2. 检查摄像头设备是否可用
3. 确认网络端口未被占用
4. 查看日志输出

## 📖 更多示例

查看 `examples/` 目录中的完整示例：

- `basic_usage.py` - 基本使用示例
- `advanced_features.py` - 高级功能示例
- `fastapi_integration.py` - FastAPI集成示例
- `config_management.py` - 配置管理示例

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License