#!/usr/bin/env python3
"""
FastAPI 摄像头后端服务
====================

提供摄像头功能的 FastAPI 后端服务。

运行方式:
    python examples/fastapi_demo.py

API 接口:
    - GET /camera/status  - 获取摄像头状态
    - GET /camera/start   - 启动摄像头
    - GET /camera/stop    - 停止摄像头
    - GET /camera/stream  - 视频流
    - GET /docs          - API 文档
"""

import uvicorn
from fastapi import FastAPI
from aitoolkit_cam import add_camera_routes

# 创建 FastAPI 应用
app = FastAPI(
    title="摄像头后端服务",
    description="提供摄像头功能的后端API服务",
    version="1.0.0"
)

# 添加摄像头路由
add_camera_routes(app, prefix="/camera")

def main():
    """启动服务器"""
    print("🚀 启动 FastAPI 摄像头后端服务...")
    print("📍 API 接口:")
    print("  GET /camera/status  - 获取摄像头状态")
    print("  GET /camera/start   - 启动摄像头")
    print("  GET /camera/stop    - 停止摄像头")
    print("  GET /camera/stream  - 视频流")
    print("  GET /docs          - API 文档")
    print("按 Ctrl+C 停止服务器")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n服务器已停止")

if __name__ == "__main__":
    main()