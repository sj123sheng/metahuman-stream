import requests
import pyaudio

def stream_audio(url: str):
    # 初始化 PyAudio
    p = pyaudio.PyAudio()

    # 打开音频流 (假设采样率为 32kHz，单声道，16-bit 采样)
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=32000,
                    output=True)

    try:
        # 使用 requests 获取音频流
        response = requests.get(url, stream=True)

        if response.status_code != 200:
            print("Failed to get audio stream. HTTP Status code:", response.status_code)
            return

        # 读取并播放音频数据
        for data in response.iter_content(chunk_size=1024):
            if data:
                stream.write(data)
    except Exception as e:
        print("An error occurred while streaming audio:", str(e))
    finally:
        # 停止和关闭流
        stream.stop_stream()
        stream.close()

        # 终止 PyAudio
        p.terminate()

if __name__ == '__main__':
    # 流式传输音频的 URL
    stream_url = 'https://u413246-b54c-bf39a3f4.westb.seetacloud.com:8443/?text=先帝创业未半而中道崩殂，今天下三分，益州疲弊，此诚危急存亡之秋也。&text_language=zh'

    # 调用函数流式播放音频
    stream_audio(stream_url)
