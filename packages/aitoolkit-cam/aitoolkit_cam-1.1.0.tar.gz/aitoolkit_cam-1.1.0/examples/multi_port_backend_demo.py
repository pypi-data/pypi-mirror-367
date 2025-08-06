#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多端口后端服务演示
==================

演示如何在不同端口启动 FastAPI 后端服务
aitoolkit_cam 会自动检测并连接到可用的服务

支持的端口：18001, 5000, 6000, 7000, 8000, 9000
"""

from fastapi import FastAPI
from aitoolkit_cam import add_camera_routes, setup_background_processing
import uvicorn
import argparse
import sys

def create_app(port: int) -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=f"摄像头服务 - 端口 {port}",
        description="集成了 aitoolkit_cam 的摄像头服务",
        version="1.0.0"
    )
    
    # 添加摄像头路由
    add_camera_routes(app)
    
    # 设置后台处理
    setup_background_processing(app)
    
    @app.get("/")
    async def root():
        return {
            "message": f"摄像头服务运行在端口 {port}",
            "camera_control": f"http://localhost:{port}/camera/",
            "video_stream": f"http://localhost:{port}/camera/stream",
            "api_docs": f"http://localhost:{port}/docs"
        }
    
    return app

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="多端口后端服务演示")
    parser.add_argument(
        "--port", 
        type=int, 
        choices=[18001, 5000, 6000, 7000, 8000, 9000],
        default=8000,
        help="服务端口 (支持: 18001, 5000, 6000, 7000, 8000, 9000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="服务主机地址"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 启动摄像头后端服务")
    print(f"📍 端口: {args.port}")
    print(f"🌐 主机: {args.host}")
    print("=" * 50)
    
    # 创建应用
    app = create_app(args.port)
    
    print(f"📋 服务信息:")
    print(f"  🏠 主页:           http://{args.host}:{args.port}/")
    print(f"  📹 摄像头控制:     http://{args.host}:{args.port}/camera/")
    print(f"  🎥 视频流:         http://{args.host}:{args.port}/camera/stream")
    print(f"  📚 API文档:        http://{args.host}:{args.port}/docs")
    print(f"  ✅ 状态检查:       http://{args.host}:{args.port}/camera/status")
    print()
    print("💡 提示: aitoolkit_cam 会自动检测并连接到此服务")
    print("🔄 按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 启动服务
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()