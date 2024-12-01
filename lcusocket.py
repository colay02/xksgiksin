import asyncio
import inspect
import json
import os
import re
import subprocess
import threading
import time
import traceback
from asyncio import CancelledError
from collections import deque
import psutil

import aiohttp
from aioconsole import ainput
import requests
class LcuWebSocket():
    def __init__(self, token, port):
        self.token, self.port = token, int(port)
        self.events = []
        self.subscribes = []

    def subscribe(self, event: str, uri: str = '', type: tuple = ('Update', 'Create', 'Delete')):
        def wrapper(func):
            self.events.append(event)
            self.subscribes.append({
                'uri': uri,
                'type': type,
                'callable': func
            })
            return func

        return wrapper

    def matchUri(self, data):
        for s in self.subscribes:
            # If the 'uri' or 'type' is empty, it matches any event.
            if not (s.get('uri') or s.get('type')) or (
                    data.get('uri') == s['uri'] and data.get('eventType') in s['type']):
                # logger.info(s['uri'], TAG)
                # logger.debug(data, TAG)
                asyncio.create_task(s['callable'](data))
                # return

    async def runWs(self):
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth('riot', self.token),
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json'
            }
        )
        address = f'wss://127.0.0.1:{self.port}/'
        self.ws = await self.session.ws_connect(address, ssl=False)

        # see: https://hextechdocs.dev/getting-started-with-the-lcu-websocket/
        for event in self.events:
            await self.ws.send_json([5, event])

        while True:
            # break
            msg = await self.ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT and msg.data != '':
                data = json.loads(msg.data)[2]
                self.matchUri(data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                # logger.info("WebSocket closed", TAG)
                break

        await self.session.close()

    async def start(self):
        if "OnJsonApiEvent" in self.events:
            raise AssertionError(
                "You should not use OnJsonApiEvent to subscribe to all events. If you wish to debug "
                "the program, comment out this line.")
        # 防止阻塞 connector.start()
        print('asdflk')
        self.task = asyncio.create_task(self.runWs())

    async def close(self):
        self.task.cancel()
        await self.session.close()