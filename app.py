'''
Description: 
Author: YaoXianMa
Date: 2024-04-09 08:54:47
LastEditors: YaoXianMa
LastEditTime: 2024-04-09 08:55:07
'''
#!/usr/bin/env python

import asyncio
import http
import signal

import websockets


async def echo(websocket):
    print(f"New connection from: {websocket.remote_address}")
    async for message in websocket:
        await websocket.send(message)


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
    asyncio.run(main())
