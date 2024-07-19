import numpy as np


# 示例字节流
chunk = b'\x00\x01\x02\x03\x04\x05\x06\x07'
# 打印结果
print("Original chunk:", type(chunk))
values = np.frombuffer(chunk, dtype=np.float16)
for value in values:
    print("np.float16 array:", "{:.10f}".format(value))

# 从字节流创建 np.float16 数组，转换为 np.float32 并归一化
streams = values.astype(np.float32)
for stream in streams:
    print("np.float32 array:", "{:.10f}".format(stream))


chunk = b'\x01\x00\xfe\xff'
streams1 = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32767
for stream in streams1:
    print("np.float32 归一 array:", "{:.10f}".format(stream))