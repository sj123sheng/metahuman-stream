import argparse
import logging
import threading
import asyncio
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer
import aiohttp
import av
from av import VideoFrame, AudioFrame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置必要的全局变量
video_file = "/Users/xiling/Downloads/数字人V2/3d.mp4"
pcs = set()


class PlayerStreamTrack(MediaStreamTrack):
    def __init__(self, kind):
        super().__init__()  # 初始化父类
        self.kind = kind
        self._queue = asyncio.Queue()

    async def recv(self):
        frame = await self._queue.get()
        return frame

    async def push_frame(self, frame):
        asyncio.run_coroutine_threadsafe(self._queue.put(frame), asyncio.get_event_loop())


class MediaPlayerWrapper:
    def __init__(self):
        self.video_track = PlayerStreamTrack(kind="video")
        self.audio_track = PlayerStreamTrack(kind="audio")
        self.container = av.open(video_file)

    def start(self):
        self.video_thread = threading.Thread(target=self._video_worker)
        self.audio_thread = threading.Thread(target=self._audio_worker)
        self.video_thread.start()
        self.audio_thread.start()

    async def _video_worker(self):
        for frame in self.container.decode(video=0):
            img = frame.to_ndarray(format='yuv420p')
            bgr_img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_I420)
            video_frame = VideoFrame.from_ndarray(bgr_img, format='bgr24')
            video_frame.time_base = frame.time_base
            await self.video_track.push_frame(video_frame)

    async def _audio_worker(self):
        for frame in self.container.decode(audio=0):
            audio_data = frame.to_ndarray().astype(np.int16)
            audio_frame = AudioFrame.from_ndarray(audio_data, format='s16')
            audio_frame.time_base = frame.time_base
            await self.audio_track.push_frame(audio_frame)


# 定义异步的 post 函数
async def post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        print(f'Error: {e}')
        return None


async def run(push_url):
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    media_player = MediaPlayerWrapper()
    media_player.start()
    video_sender = pc.addTrack(media_player.video_track)
    audio_sender = pc.addTrack(media_player.audio_track)

    await pc.setLocalDescription(await pc.createOffer())

    answer = await post(push_url, pc.localDescription.sdp)
    if answer:
        await pc.setRemoteDescription(RTCSessionDescription(sdp=answer, type='answer'))


if __name__ == "__main__":

    signaling_url = "http://118.31.45.70/rtc/v1/whip/?app=live&stream=livestream&secret=123"  # 替换为实际的信令服务器 URL

    # 设置事件循环
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(signaling_url))
    loop.run_forever()
