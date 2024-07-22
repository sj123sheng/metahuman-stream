import asyncio
import aiohttp_cors
from aiohttp import web

async def stream_data(request):
    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/event-stream'
    # response.headers['Cache-Control'] = 'no-cache'
    # response.headers['Connection'] = 'keep-alive'
    await response.prepare(request)

    try:
        messages = [
            "data: 你好！这是第 1 条消息\n\n",
            "data:这是Markdown示例：\n\ndata: **加粗** 和 *斜体*\n\n",
            "data:计算结果是 \\(19 \\times 2 + \\frac{8}{2} = 42\\)。\n\n"
        ]

        for message in messages:
            await response.write(message.encode('utf-8'))
            await asyncio.sleep(1)
        print("Stream finished successfully")
    except asyncio.CancelledError:
        print('Client disconnected')
    except Exception as e:
        print(f'Unexpected error: {e}')
    finally:
        try:
            await response.write_eof()
        except Exception as e:
            print(f'Connection error on write_eof: {e}')
    return response

app = web.Application()
app.router.add_get('/stream', stream_data)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

for route in app.router.routes():
    cors.add(route)

if __name__ == '__main__':
    web.run_app(app, host="127.0.0.1", port=8000)
