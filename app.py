import asyncio
import http
import signal
import sys

import websockets


# 儲存所有連接的WebSocket物件的容器
connected_clients = set()


async def echo(websocket, path):
    # 将新连接的WebSocket对象加入容器
    connected_clients.add(websocket)
    print(f"New connection from: {websocket.remote_address}", file=sys.stdout)

    try:
        async for message in websocket:
            # 使用循环向每个WebSocket对象发送消息（广播）
            for client in connected_clients:
                await client.send(message)
    finally:
        # 从容器中移除相应的WebSocket对象
        connected_clients.remove(websocket)
        # 发送关闭帧以结束连接
        await websocket.close()


async def health_check(path, request_headers):
    if path == "/healthz":
        return http.HTTPStatus.OK, [], b"OK\n"


async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(
        echo,
        host="",
        port=8080,
        process_request=health_check,
    ):
        await stop


if __name__ == "__main__":
    print("Server is running", file=sys.stdout)
    asyncio.run(main())
