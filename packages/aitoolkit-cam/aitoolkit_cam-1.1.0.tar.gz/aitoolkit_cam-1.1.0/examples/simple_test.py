#!/usr/bin/env python3
"""
简单摄像头测试
============

最简单的摄像头使用示例

运行方式:
    python examples/simple_test.py
"""

from aitoolkit_cam import Camera

# 最简单的使用方式
with Camera(max_frames=500) as cam:
    url = cam.start()
    print(f"摄像头启动: {url}")
    
    for frame in cam:
        if frame is not None:
            cam.show(frame)