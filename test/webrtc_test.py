import asyncio
import glob
import logging
import os
import threading
import time
from typing import Optional

import aiohttp
import av
import cv2
import numpy as np
import resampy
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from av import VideoFrame, AudioFrame
from tqdm import tqdm
import soundfile as sf
from test.PlayerStreamTrackTest import PlayerStreamTrackTest

# from webrtc import HumanPlayer
global nerfreal
pcs = set()

logging.basicConfig()
logger = logging.getLogger(__name__)


# 定义异步的 post 函数
async def post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        print(f'Error: {e}')
        return None


video_file = "/Users/xiling/Downloads/数字人V2/下载.wav"


def player_worker_thread(
        player,
        quit_event,
        loop,
        container,
        audio_track,
        video_track
):
    print("1")


class HumanPlayer:

    def __init__(
            self, nerfreal=None, format=None, options=None, timeout=None, loop=False, decode=True
    ):
        self.__thread: Optional[threading.Thread] = None
        self.__thread_quit: Optional[threading.Event] = None

        # examine streams
        self.__audio = PlayerStreamTrackTest(self, kind="audio")
        self.__video = PlayerStreamTrackTest(self, kind="video")

        self.__container = nerfreal

    @property
    def audio(self) -> MediaStreamTrack:
        """
        A :class:`aiortc.MediaStreamTrack` instance if the file contains audio.
        """
        return self.__audio

    @property
    def video(self) -> MediaStreamTrack:
        """
        A :class:`aiortc.MediaStreamTrack` instance if the file contains video.
        """
        return self.__video

    def _start(self, track: PlayerStreamTrackTest) -> None:
        # print(f"webrtc start kind:{track.kind}")
        # logger.info(f"logger debug webrtc start kind:{track.kind}")
        if self.__thread is None:
            self.__thread_quit = threading.Event()
            self.__thread = threading.Thread(
                name="media-player",
                target=player_worker_thread,
                args=(
                    self,
                    self.__thread_quit,
                    asyncio.get_event_loop(),
                    self.__container,
                    self.__audio,
                    self.__video
                ),
            )
            self.__thread.start()

    def _stop(self, track: PlayerStreamTrackTest) -> None:
        if self.__thread is not None:
            self.__thread_quit.set()
            self.__thread.join()
            self.__thread = None

        if self.__container is not None:
            self.__container = None


async def run(push_url, player):
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # player = HumanPlayer()  # 假设传递 'nerfreal' 作为音视频源
    audio_sender = pc.addTrack(player.audio)
    video_sender = pc.addTrack(player.video)

    await pc.setLocalDescription(await pc.createOffer())

    answer = await post(push_url, pc.localDescription.sdp)
    if answer:
        await pc.setRemoteDescription(RTCSessionDescription(sdp=answer, type='answer'))


def generate_video_frames2(player, loop):
    input_img_list = glob.glob(
        os.path.join('/Users/xiling/Downloads/数字人V2/MuseTalk/avator/avator_10/full_imgs', '*.[jpJP][pnPN]*[gG]'))
    input_img_list = sorted(input_img_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    print('reading images...')
    for img_path in tqdm(input_img_list):
        frame = cv2.imread(img_path)
        # 将帧推送到 player 的视频轨道
        player.video.push_video_frame(frame, loop)


def generate_media_tracks(player, loop):
    container = av.open(video_file)  # 打开视频文件
    stream_video = None # next(s for s in container.streams if s.type == 'video')  # 获取视频流
    stream_audio = next((s for s in container.streams if s.type == 'audio'), None)  # 获取音频流，如果不存在则为None

    for packet in container.demux(stream_video, stream_audio):  # 按顺序解复用视频和音频帧
        for frame in packet.decode():
            if isinstance(frame, VideoFrame):
                # 处理视频帧，类似你现有的逻辑
                img = frame.to_ndarray(format='yuv420p')
                # 使用 OpenCV 转换色彩空间
                bgr_img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_I420)
                player.video.push_frame(VideoFrame.from_ndarray(bgr_img, format='bgr24'), loop)  # 推送视频帧到轨道
            elif isinstance(frame, AudioFrame) and stream_audio is not None:
                # 处理音频帧
                # audio_data = frame.to_ndarray().astype(np.int16)  # 转换为int16
                new_data = resampy.resample(frame.to_ndarray(), 32000, 16000)
                # 创建新的AudioFrame，假设单声道，采样率为原音频帧的采样率
                new_data = (new_data * 32767).astype(np.int16)
                new_frame = AudioFrame(format='s16', layout='mono', samples=frame.samples)
                new_frame.planes[0].update(new_data.tobytes())
                new_frame.sample_rate=16000
                player.audio.push_frame(new_frame, loop)

                # 直接推送音频帧到轨道
                # player.audio.push_frame(frame, loop)  # 假定PlayerStreamTrackTest支持直接推送AudioFrame

    container.close()

def generate_video_frames(player, loop):
    cap = cv2.VideoCapture("/Users/xiling/Downloads/数字人V2/3d.mp4")  # 或者使用摄像头 eg. cv2.VideoCapture(0)
    # cap = cv2.VideoCapture(0)  # 或者使用摄像头 eg. cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # 将帧推送到 player 的视频轨道
        player.video.push_video_frame(frame, loop)
        # 可以根据帧率适当 sleep
        time.sleep(1 / 25)  # 假设25 FPS

    cap.release()


def generate_video_frames3(player, loop):
    container = av.open(video_file)
    for frame in container.decode():
        # print(type(frame))
        if isinstance(frame, VideoFrame):
            # 转换 frame 为 numpy 数组
            img = frame.to_ndarray(format='yuv420p')

            # 使用 OpenCV 转换色彩空间
            bgr_img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_I420)

            # 将转换后的 numpy 数组创建为 VideoFrame
            video_frame = VideoFrame.from_ndarray(bgr_img, format='bgr24')
            player.video.push_frame(video_frame, loop)
        elif isinstance(frame, AudioFrame):
            # 获取音频数据为int16（如果原始不是s16，这一步可能需要额外的转换步骤）
            # 注意：此处简化处理，实际根据具体情况调整
            audio_data = frame.to_ndarray().astype(np.int16)
            #
            # # 如果需要改变采样率，这里可以加入重采样逻辑
            # # 但请注意，直接使用resampy可能需要先将数据转换为适当格式
            # # 以下是一个简化的示意，实际实现可能更复杂
            sample_rate_new = 16000
            if frame.sample_rate != sample_rate_new:
                audio_data = resampy.resample(audio_data, frame.sample_rate, sample_rate_new)
            #
            # 创建新的AudioFrame，假设单声道，采样率为原音频帧的采样率
            new_audio_frame = AudioFrame(format='s16', layout='mono', samples=frame.samples)
            new_audio_frame.planes[0].update(audio_data.tobytes())
            new_audio_frame.sample_rate = sample_rate_new  # 确保设置正确的采样率
            player.audio.push_frame(new_audio_frame, loop)


if __name__ == '__main__':
    # 示例使用方法
    push_url = "http://118.31.45.70/rtc/v1/whip/?app=live&stream=livestream&secret=123"  # 替换为实际的信令服务器 URL
    # push_url = "srt://mj-push.linkheer.com:1105?streamid=#!::h=mj-push.linkheer.com,r=/miaojie/xilingtest1?auth_key=1721789483-0-0-50ca3f8cb19091b59c81de0d97f49cfb,m=publish"  # 替换为实际的信令服务器 URL
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    audio_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(audio_loop)

    player = HumanPlayer()
    # 启动推送视频帧的线程
    video_thread = threading.Thread(target=generate_video_frames, args=(player, loop))
    video_thread.start()

    loop.run_until_complete(run(push_url, player))
    # loop.run_forever()
