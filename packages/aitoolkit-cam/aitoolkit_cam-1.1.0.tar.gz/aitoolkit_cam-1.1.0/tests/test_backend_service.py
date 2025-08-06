# 测试后端服务 - FastAPI集成
# =============================
#
# 演示如何将摄像头功能集成到现有FastAPI应用中
# 管理员运行此服务，用户代码自动连接

from fastapi import FastAPI
from aitoolkit_cam import add_camera_routes, setup_background_processing
import uvicorn
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建FastAPI应用 - 模拟现有业务系统
app = FastAPI(title="业务系统 + 摄像头集成", version="1.0.0")

# ========== 现有业务API ==========
@app.get("/")
async def root():
    """业务系统主页"""
    return {
        "message": "欢迎使用业务系统",
        "services": {
            "business_api": "/api/business",
            "camera_control": "/camera/",
            "camera_stream": "/camera/stream"
        }
    }

@app.get("/api/business/health")
async def business_health():
    """业务健康检查"""
    return {"status": "healthy", "service": "business_system"}

@app.get("/api/business/users")
async def get_users():
    """业务API示例"""
    return {
        "users": [
            {"id": 1, "name": "张三"},
            {"id": 2, "name": "李四"}
        ]
    }

# ========== 摄像头功能集成 ==========
# 只需要这一行代码就能将摄像头功能集成到现有FastAPI应用中！

add_camera_routes(app, prefix="/camera")

# 可选：设置后台自动处理（如果需要服务器端持续处理帧）
def edge_detection_processor(frame):
    """服务器端帧处理函数"""
    import cv2
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

# 启用后台处理（可选）
# setup_background_processing(app, frame_processor=edge_detection_processor, fps=20)

# ==========================================

def start_backend():
    """启动后端服务"""
    print("=" * 70)
    print("🚀 启动业务系统后端服务（已集成摄像头功能）")
    print("=" * 70)
    print("集成完成！只需要一行代码：add_camera_routes(app)")
    print()
    print("📍 服务地址:")
    print("  🏠 业务系统主页:     http://localhost:8000/")
    print("  📹 摄像头控制页面:   http://localhost:8000/camera/")
    print("  🎥 视频流地址:       http://localhost:8000/camera/stream")
    print("  📚 API文档:         http://localhost:8000/docs")
    print()
    print("=" * 70)
    print("✅ 后端服务已启动，等待用户连接...")
    print()
    print("📋 测试步骤:")
    print("1. 在另一个终端运行: python tests/test_simple_mode.py")
    print("2. 用户代码会自动检测并连接到此后端服务")
    print("3. 访问 http://localhost:8000/camera/ 查看控制页面")
    print("=" * 70)
    
    # 启动FastAPI服务器
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        if "bind" in str(e) and "8000" in str(e):
            print(f"\n❌ 端口8000已被占用，请先停止其他服务或使用其他端口")
            print("可以使用: uvicorn.run(app, port=8001)")
        else:
            print(f"\n❌ 启动失败: {e}")

if __name__ == "__main__":
    start_backend() 