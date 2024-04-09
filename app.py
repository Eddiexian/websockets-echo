import asyncio
import http
import signal
import sys

import websockets


# 儲存所有連接的WebSocket物件的容器
connected_clients = set()


async def echo(websocket, path):
    # 將新連接的WebSocket物件加入容器
    connected_clients.add(websocket)
    print(f"New connection from: {websocket.remote_address}", file=sys.stdout)

    try:
        async for message in websocket:
            # 使用遍歷迴圈向每個WebSocket物件傳送訊息（廣播）
            for client in connected_clients:
                await client.send(message)
    finally:
        # 連線結束時，從容器中移除相應的WebSocket物件
        connected_clients.remove(websocket)


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
