# 测试用户模式 - Jupyter中的摄像头使用
# =====================================
#
# 这是用户在Jupyter中实际使用的代码示例
# Camera类会自动检测后端服务，用户无需关心后端

from aitoolkit_cam import Camera
import cv2
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("=" * 60)
print("🔬 摄像头用户模式测试")
print("=" * 60)
print("这是用户在Jupyter中使用的标准代码")
print("Camera会自动检测后端服务，如果没有则使用简单模式")
print("=" * 60)

try:
    # 用户的标准代码 - 无需修改
    with Camera(source=0, width=640, height=480, max_frames=50) as cam:
        url = cam.start()  # 自动检测后端或启动内置服务器
        print(f"✅ 摄像头启动成功")
        print(f"📺 视频流地址: {url}")
        print(f"🔧 运行模式: {'后端模式' if not cam._simple_mode else '简单模式'}")
        print(f"📊 将处理 {cam.max_frames} 帧后自动停止")
        print("-" * 60)

        frame_count = 0
        for frame in cam:  # 迭代获取帧
            if frame is None:
                continue
                
            # 用户的OpenCV处理逻辑
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 80, 160)
            display_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            # 显示处理后的帧
            cam.show(display_frame)
            
            frame_count += 1
            
            # 显示进度
            if frame_count % 10 == 0:
                print(f"📈 已处理 {frame_count}/{cam.max_frames} 帧")

        print(f"\n✅ 处理完成，总共处理了 {frame_count} 帧")

except KeyboardInterrupt:
    print("\n⚠️  用户中断了处理")
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("🏁 摄像头已停止")
    print("=" * 60)
    print("✨ 测试完成 - 这就是用户在Jupyter中使用的完整流程")
    print("用户代码始终保持不变，后端服务对用户透明")
    print("=" * 60) 