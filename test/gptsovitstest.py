import time
from enum import Enum
from typing import Iterator
import requests

class State(Enum):
    RUNNING = 0
    PAUSE = 1

class GPTSovits:
    def __init__(self):
        self.state = State.RUNNING # 默认状态为RUNNING

    def gpt_sovits(self, text, reffile, reftext, language, cut_punc, server_url) -> Iterator[bytes]:
        start = time.perf_counter()
        req = {
            'text': text,
            'text_language': language,
            'refer_wav_path': reffile,
            'prompt_text': reftext,
            'prompt_language': language,
            'cut_punc': cut_punc
        }
        res = requests.post(
            f"{server_url}",
            json=req,
            stream=True,
        )
        end = time.perf_counter()
        print(f"gpt_sovits Time to make POST: {end - start}s")
        if res.status_code != 200:
            print("Error:", res.text)
            return
        first = True
        for chunk in res.iter_content(chunk_size=32000):  # 1280 32K*20ms*2
            if first:
                end = time.perf_counter()
                print(f"gpt_sovits Time to first chunk: {end - start}s")
                first = False
            if chunk and self.state == State.RUNNING:
                yield chunk
        print("gpt_sovits response.elapsed:", res.elapsed)

if __name__ == '__main__':
    text = "先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。"
    server_url = "https://u413246-b54c-bf39a3f4.westb.seetacloud.com:8443"

    # 实例化类并调用方法
    sovits_instance = GPTSovits()
    tts = sovits_instance.gpt_sovits(text, None, None, "zh", None, server_url)

    # 示例对生成器的处理
    for audio_chunk in tts:
        # 在此处理音频块
        print(f"Received audio chunk of size: {len(audio_chunk)} bytes")
