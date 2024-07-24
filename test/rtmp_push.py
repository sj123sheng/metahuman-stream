import time

import cv2

# subprocess 模块允许我们启动一个新进程，并连接到它们的输入/输出/错误管道，从而获取返回值。
import subprocess


# 视频读取对象
cap = cv2.VideoCapture("/Users/xiling/Downloads/数字人V2/3d.mp4")

# 读取一帧
ret, frame = cap.read()

video = "/Users/xiling/Downloads/数字人V2/3d.mp4"
# 推流地址
rtmp = "rtmp://118.31.45.70/live/livestream?secret=123"

# 推流参数
command = ['ffmpeg',
           '-y',
           '-f', 'rawvideo',
           '-vcodec','rawvideo',
           '-pix_fmt', 'bgr24',
           '-s', '720*560',			# 根据输入视频尺寸填写
           '-r', '25',
           '-i', '-',
           '-c:v', 'h264',
           '-pix_fmt', 'yuv420p',
           '-preset', 'ultrafast',
           '-f', 'flv',
           rtmp]

# 创建、管理子进程
pipe = subprocess.Popen(command, stdin=subprocess.PIPE)
size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

# 循环读取
while cap.isOpened():
    # 读取一帧
    ret, frame = cap.read()
    if frame is None:
        print('read frame err!')
        continue

    # 显示一帧
    cv2.imshow("frame", frame)

    # 按键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # 读取尺寸、推流
    img=cv2.resize(frame,size)
    pipe.stdin.write(img.tobytes())

# 关闭窗口
cv2.destroyAllWindows()

# 停止读取
cap.release()