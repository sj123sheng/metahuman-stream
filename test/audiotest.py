import numpy as np
import requests
import resampy
import soundfile

def download_ogg_stream(url, output_file):
    """
    从 URL 下载 OGG 音频流并保存到本地文件

    参数:
    url (str): 音频流的 URL
    output_file (str): 本地文件路径，用于保存下载的音频
    """
    # 发起 GET 请求以获取音频流
    response = requests.get(url, stream=True)

    # 检查请求是否成功
    if response.status_code == 200:
        # 以二进制写入模式打开输出文件
        with open(output_file, 'wb') as file:
            incomplete_chunk = b''
            # 逐块写入数据，以防止内存占用过高
            for chunk in response.iter_content(chunk_size=32000):
                if chunk:
                    print("Chunk original : ", len(chunk))
                    # 合并不完整的数据块与当前的数据块
                    chunk = incomplete_chunk + chunk

                    # 检查是否可以处理当前数据块
                    if len(chunk) % 2 != 0:
                        # 如果不能处理，将最后一个字节缓存到 incomplete_chunk
                        incomplete_chunk = chunk[-1:]
                        chunk = chunk[:-1]
                    else:
                        # 数据块大小为 2 的倍数，清空 incomplete_chunk
                        incomplete_chunk = b''

                    if len(chunk) > 0:
                        # 将字节流转换为半精度浮点数流
                        print("Chunk len : ", len(chunk))
                        stream = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768
                        stream = resampy.resample(x=stream, sr_orig=32000, sr_new=16000)
                        print(f"np.float16 streamlen:{len(stream)}")
                        streamlen = stream.shape[0]
                        print(f"np.float16 array:{streamlen} {stream[:2]}")
                        idx=0
                        chunk_size = 320
                        while streamlen >= chunk_size:
                            data = stream[idx:idx+chunk_size]
                            print(f"before write streamlen:{streamlen} idx:{idx} data:{len(data)}")
                            streamlen -= chunk_size
                            idx += chunk_size
                            print(f"after write streamlen:{streamlen} idx:{idx}")

                        # file.write(chunk)
        print(f"音频流已成功保存到 {output_file}.")
    else:
        print(f"请求失败，状态码：{response.status_code}")

# 测试函数
if __name__ == "__main__":
    # 需要下载的音频流 URL
    audio_stream_url = 'https://u413246-88e9-e4e900bd.westb.seetacloud.com:8443/?text=先帝创业未半而中道崩殂。&text_language=zh'

    # 保存音频流的本地文件路径
    output_file_path = "output_audio.ogg"

    # 调用函数以下载并保存音频流
    download_ogg_stream(audio_stream_url, output_file_path)
