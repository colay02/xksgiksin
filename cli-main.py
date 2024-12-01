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

from loloperations import LOLhelp
from lcusocket import LcuWebSocket
from fantome import runpatcher, get_fantome, merge_fantome


helper = LOLhelp()
listener = LcuWebSocket(helper.token, helper.port)
listener.current_champion_id = -1
listener.current_summoner_id = helper.get_current_summoner()['summonerId']
print(listener.current_summoner_id)

skin_json = json.load(open("champion.json", "r", encoding='utf-8'))

@listener.subscribe(event='OnJsonApiEvent_lol-champ-select_v1_session',
                                 uri='/lol-champ-select/v1/session',
                                 type=('Update',))
async def onChampSelectChanged(event):
    global state
    myteam = event['data']['myTeam']
    for summoner in myteam:
        if summoner['summonerId'] == listener.current_summoner_id and listener.current_champion_id != summoner['championId'] and summoner['championId'] > 0:
            listener.current_champion_id = summoner['championId']
            print(f"now choose is {skin_json[str(listener.current_champion_id)]}")
        
    

async def main():
    print("cmd:\nrun: start patching.\nstop: stop patching.\n[num]: select skin.")
    tsk = asyncio.create_task(listener.start())
    
    process = None
    current_skin_id = -1
    while True:
        x = await ainput(' > ')
        if x == 'run':
            if process:
                print("patcher is running.")
            elif listener.current_champion_id > 0 and current_skin_id > 0:
                process = runpatcher()
            else:
                print("please select skin first.")
        elif x == 'stop':
            if process:
                os.system('taskkill /t /f /pid {}'.format(process.pid))
                process = None
                current_skin_id = -1
            else:
                print("no patcher is running.")
        else:
            if listener.current_champion_id > 0:
                current_skin_id = int(x)
                print(get_fantome(listener.current_champion_id, current_skin_id))
                merge_fantome(r"E:\games\WeGameApps\英雄联盟\Game")
                print("ok!")
            else:
                print("please select champion first.")

asyncio.run(main())

