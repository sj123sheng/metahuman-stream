import argparse
import logging
import threading
from typing import Optional

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
import aiohttp
import asyncio

from aiortc.contrib.media import PlayerStreamTrack

from webrtc import HumanPlayer
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


def player_worker_thread(
            quit_event,
            loop,
            container,
            audio_track,
            video_track
    ):
        print(f"player_worker_thread")

class HumanPlayer:

    def __init__(
            self, nerfreal=None, format=None, options=None, timeout=None, loop=False, decode=True
    ):
        self.__thread: Optional[threading.Thread] = None
        self.__thread_quit: Optional[threading.Event] = None

        # examine streams
        self.__audio = PlayerStreamTrack(self, kind="audio")
        self.__video = PlayerStreamTrack(self, kind="video")

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

    def _start(self, track: PlayerStreamTrack) -> None:
        print(f"webrtc start kind:{track.kind}")
        logger.info(f"logger debug webrtc start kind:{track.kind}")
        if self.__thread is None:
            self.__thread_quit = threading.Event()
            self.__thread = threading.Thread(
                name="media-player",
                target=player_worker_thread,
                args=(
                    self.__thread_quit,
                    asyncio.get_event_loop(),
                    self.__container,
                    self.__audio,
                    self.__video
                ),
            )
            self.__thread.start()

    def _stop(self, track: PlayerStreamTrack) -> None:
        if self.__thread is not None:
            self.__thread_quit.set()
            self.__thread.join()
            self.__thread = None

        if self.__container is not None:
            self.__container = None

async def run(push_url):
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    player = HumanPlayer()  # 假设传递 'nerfreal' 作为音视频源
    audio_sender = pc.addTrack(player.audio)
    video_sender = pc.addTrack(player.video)

    await pc.setLocalDescription(await pc.createOffer())

    answer = await post(push_url, pc.localDescription.sdp)
    if answer:
        await pc.setRemoteDescription(RTCSessionDescription(sdp=answer, type='answer'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pose', type=str, default="data/data_kf.json")
    opt = parser.parse_args()
    # 示例使用方法
    push_url = "http://118.31.45.70/rtc/v1/whip/?app=live&stream=livestream&secret=123"  # 替换为实际的信令服务器 URL
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run(push_url))
    loop.run_forever()
