import av
import cv2
import numpy as np
import resampy
from av import VideoFrame, AudioFrame

video_file = "/Users/xiling/Downloads/数字人V2/MuseTalk/lx.mp4"

container = av.open(video_file)

for frame in container.decode():
    # print(type(frame))
    if (type(frame) == VideoFrame):
        # 转换 frame 为 numpy 数组
        img = frame.to_ndarray(format='yuv420p')

        # 使用 OpenCV 转换色彩空间
        bgr_img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_I420)

        # 将转换后的 numpy 数组创建为 VideoFrame
        video_frame = VideoFrame.from_ndarray(bgr_img, format='bgr24')
        print(video_frame.format)
        print(video_frame.planes)
    elif (type(frame) == AudioFrame):
        # 转换 frame 中的数据类型为 int16
        audio_data = frame.to_ndarray().astype(np.int16)
        stream = resampy.resample(x=audio_data, sr_orig=44100, sr_new=16000)
        print(type(stream))
        print(stream.shape[0])
        new_frame = AudioFrame(format='s16', layout='mono', samples=stream.shape[0])
        new_frame.planes[0].update(audio_data.tobytes())
        new_frame.sample_rate = 16000
        print(new_frame.sample_rate)
        print(new_frame.time_base)
        print(new_frame.pts)

#
# for audio_frame in audio_frames:
#     frame,type = audio_frame
#     frame = (frame * 32767).astype(np.int16)
#     new_frame = AudioFrame(format='s16', layout='mono', samples=frame.shape[0])
#     new_frame.planes[0].update(frame.tobytes())
#     new_frame.sample_rate=16000
#     stream = resampy.resample(x=stream, sr_orig=sample_rate, sr_new=self.sample_rate)