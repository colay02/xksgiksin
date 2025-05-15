import requests as rq
import json
import time
import psutil
import threading
rq.packages.urllib3.disable_warnings()


class LOLhelp:
    def __init__(self, window_handler):
        self.loaded = False
        for try_cnt in range(5):
            try:
                self.token, self.port = self.get_info()
                print(self.token, self.port)
            except Exception:
                print(f'retring to get lol lobby, cnt = {try_cnt}')
                window_handler(f"正在连接客户端 (Retrying ... {try_cnt + 1}/5)")
                time.sleep(1)
            finally:
                if self.token == '':
                    print(f'retring to get lol lobby, cnt = {try_cnt}')
                    window_handler(f"正在连接客户端 (Retrying ... {try_cnt + 1}/5)")
                    time.sleep(1)
                else:
                    self.loaded = True
                    break
        self.url_base = f'https://riot:{self.token}@127.0.0.1:{self.port}'
        self.auto_choose = 0
        self.auto_choose_champion = 0
        self.auto_accept = 0

    def get_info(self):
        # get process info
        pid = 0
        aaa = psutil.pids()
        for i in aaa:
            na = psutil.Process(i).name()
            if(na=='LeagueClientUx.exe'):
                pid=i

        p = psutil.Process(pid)
        lst = p.cmdline()
        token,port = '',''
        for i in lst:
            if(i.find('--remoting-auth-token')!=-1):
                token = i.split('=')[1]
            if(i.find('--app-port')!=-1):
                port = i.split('=')[1]
        print("lolhepler created", token, port)
        return token, port
    
    def open_room(self, roomType = "PRACTICETOOL"):
        '''
        roomType = "PRACTICETOOL" or "CLASSIC"
        '''
        url = self.url_base + '/lol-lobby/v2/lobby'
        data_practice_5v5 = '''
        {
            "customGameLobby": {
                "configuration": {
                    "gameMode": "%s",
                    "gameMutator": "",
                    "gameServerRegion": "",
                    "mapId": 11,
                    "mutators": {
                        "id": 1
                    },
                    "spectatorPolicy": "AllAllowed",
                    "teamSize": 5
            },
            "lobbyName": "LeagueLobby 5V5 PRACTICETOOL-41",
            "lobbyPassword": null
            },
            "isCustom": true
        }
        ''' % (roomType)

        resp = rq.post(url, data_practice_5v5, verify=False)
        print(resp.text)

    def add_bots(self, bots:list):
        url = self.url_base + '/lol-lobby/v1/lobby/custom/bots'
        for i in bots:
            data = '{"botDifficulty": "'+i[2]+'","championId":' + str(i[0]) + ',"teamId": "'+ ('100' if i[1]==1 else '200') +'"}'
            print(data)
            resp = rq.post(url, data, verify=False)
            print(resp.text)

    def start_game(self):
        url = self.url_base + '/lol-lobby/v1/lobby/custom/start-champ-select'
        resp = rq.post(url, verify=False)
        # print(resp.text)

    def select_champion(self, championId):
        url = self.url_base + '/lol-champ-select/v1/session/actions/' + str(self.get_session_id())
        resp = rq.patch(url, '{"championId":'+str(championId)+'}', verify=False)
        # print(resp.text)

    def lock_champion(self):
        url = self.url_base + '/lol-champ-select/v1/session/actions/' + str(self.get_session_id()) + '/complete'
        resp = rq.post(url,verify=False)

    def get_session_id(self):
        url = self.url_base + '/lol-champ-select/v1/session'
        resp = rq.get(url, verify=False)
        resp_json = json.loads(resp.text)
        if(not resp_json.get('actions',None)):
            return -1
        localPlayerCellId = resp_json['localPlayerCellId']
        for i in resp_json['actions'][0]:
            if(i.get('actorCellId') == localPlayerCellId):
                return i.get('id')

    def get_ready_check(self):
        url = self.url_base + '/lol-matchmaking/v1/ready-check'
        resp = rq.get(url, verify=False)
        resp_json = json.loads(resp.text)
        return resp_json.get('state')

    def match_accept(self):
        url = self.url_base + '/lol-matchmaking/v1/ready-check/accept'
        resp = rq.post(url, verify=False)
        
    def get_selected_champion_skin(self):
        url = self.url_base + "/lol-champ-select/v1/pickable-skin-ids"
        resp = rq.get(url, verify=False)
        return resp.json()
    
    def get_selected_champion_id(self):
        url = self.url_base + "/lol-champ-select/v1/current-champion"
        resp = rq.get(url, verify=False)
        return resp.json()
    
    def get_current_summoner(self):
        while True:
            try:
                url = self.url_base + "/lol-summoner/v1/current-summoner"
                resp = rq.get(url, verify=False).json()
                if resp.get("summonerId", None) is not None:
                    return resp['summonerId']
                else:
                    print('retring to get summoner id.')
                    time.sleep(2)
                    continue
            except:
                print('retring to get summoner id.')
                time.sleep(2)
                pass

