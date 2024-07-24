import asyncio
import logging
import time
from typing import Iterator

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gpt_sovits(text, language, server_url) -> Iterator[bytes]:
    start = time.perf_counter()
    req={
        'text':text,
        'text_language':language,
        'prompt_language':language
    }
    res = requests.post(
        f"{server_url}",
        json=req,
        stream=True,
    )
    end = time.perf_counter()
    print(f"gpt_sovits Time to make POST: {end-start}s")

    if res.status_code != 200:
        print("Error:", res.text)
        return

    first = True
    for chunk in res.iter_content(chunk_size=32000): # 1280 32K*20ms*2
        print("chunk:", type(chunk))
        if first:
            end = time.perf_counter()
            print(f"gpt_sovits Time to first chunk: {end-start}s")
            first = False
        if chunk:
            yield chunk

    print("gpt_sovits response.elapsed:", res.elapsed)


if __name__ == "__main__":
    url = "https://u413246-b3e2-cae92fc3.westb.seetacloud.com:8443/"  # 替换为实际的信令服务器 URL
    gpt_sovits(text='先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。', language='zh', server_url=url)
