import asyncio
import fractions
import time
from typing import Tuple, Union

from av import VideoFrame
from av.frame import Frame
from av.packet import Packet

from aiortc import MediaStreamTrack

AUDIO_PTIME = 0.020  # 20ms audio packetization
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / 25  # 30fps
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)
SAMPLE_RATE = 32000
AUDIO_TIME_BASE = fractions.Fraction(1, SAMPLE_RATE)


class PlayerStreamTrackTest(MediaStreamTrack):
    """
    A video track that returns an animated flag.
    """

    def __init__(self, player, kind):
        super().__init__()  # don't forget this!
        self.kind = kind
        self._player = player
        self._queue = asyncio.Queue()
        self.timelist = []  #记录最近包的时间戳
        if self.kind == 'video':
            self.framecount = 0
            self.lasttime = time.perf_counter()
            self.totaltime = 0

    _start: float
    _timestamp: int

    async def next_timestamp(self) -> Tuple[int, fractions.Fraction]:
        if self.readyState != "live":
            raise Exception

        if self.kind == 'video':
            if hasattr(self, "_timestamp"):
                self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
                wait = self._start + (self._timestamp / VIDEO_CLOCK_RATE) - time.time()
                if wait > 0:
                    await asyncio.sleep(wait)
            else:
                self._start = time.time()
                self._timestamp = 0
                self.timelist.append(self._start)
                print('video start:', self._start)
            return self._timestamp, VIDEO_TIME_BASE
        else:  #audio
            if hasattr(self, "_timestamp"):
                self._timestamp += int(AUDIO_PTIME * SAMPLE_RATE)
                wait = self._start + (self._timestamp / SAMPLE_RATE) - time.time()
                if wait > 0:
                    await asyncio.sleep(wait)
            else:
                self._start = time.time()
                self._timestamp = 0
                self.timelist.append(self._start)
                print('audio start:', self._start)
            return self._timestamp, AUDIO_TIME_BASE

    async def recv(self) -> Union[Frame, Packet]:
        self._player._start(self)
        frame = await self._queue.get()
        # print(f'recv:{frame.pts}')
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        if frame is None:
            self.stop()
            raise Exception
        if self.kind == 'video':
            self.totaltime += (time.perf_counter() - self.lasttime)
            self.framecount += 1
            self.lasttime = time.perf_counter()
            if self.framecount == 100:
                print(f"------actual avg final fps:{self.framecount / self.totaltime:.4f}")
                self.framecount = 0
                self.totaltime = 0
        return frame

    def push_video_frame(self, frame, loop):
        frame = VideoFrame.from_ndarray(frame, format='bgr24')
        asyncio.run_coroutine_threadsafe(self._queue.put(frame), loop)

    def push_frame(self, frame, loop):
        asyncio.run_coroutine_threadsafe(self._queue.put(frame), loop)