import tkinter as tk
import subprocess
import os
import threading
import winreg
from pathlib import Path
from tkinter import ttk
from utils.convert import *
from utils.fantome import get_fantome, merge_fantome, runpatcher
from connector.lcusocket import LcuWebSocket
from connector.loloperations import LOLhelp
import asyncio
import ctypes

class Window:
    def __init__(self) -> None:
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("换肤")
        
        if not ctypes.windll.shell32.IsUserAnAdmin():
            self.skin_label = tk.Label(self.root, text="请用管理员模式打开程序")
            self.skin_label.grid(row=0, column=0, padx=10, pady=10)
            self.root.mainloop()
            return

        # 开启自动选英雄
        self.control = Control()
        self.start_auto_select()

        # 创建第一个下拉框
        self.champion_label = tk.Label(self.root, text="选择英雄:")
        self.champion_label.grid(row=0, column=0, padx=10, pady=10)

        self.champion_combo = ttk.Combobox(self.root, values=["(请选择)"] + get_champion_list(), state="readonly")
        self.champion_combo.grid(row=0, column=1, padx=10, pady=10)
        self.champion_combo.set("(请选择)")
        self.champion_combo.bind("<<ComboboxSelected>>", self.on_champion_combo_select)
        
        self.get_champion_button = tk.Button(self.root, text="获取当前英雄", command=self.get_and_select_champion)
        self.get_champion_button.grid(row=0, column=2, padx=10, pady=10)

        # 创建第二个下拉框
        self.skin_label = tk.Label(self.root, text="选择皮肤：")
        self.skin_label.grid(row=1, column=0, padx=10, pady=10)

        self.skin_combo = ttk.Combobox(self.root, values=["(请选择英雄)"], state="readonly")
        self.skin_combo.grid(row=1, column=1, padx=10, pady=10)
        self.skin_combo.set("(请选择英雄)")

        # 创建两个并排按钮
        self.load_button = tk.Button(self.root, text="加载皮肤", width=10, command=self.load_skin)
        self.load_button.grid(row=2, column=0, padx=10, pady=10)

        self.run_button = tk.Button(self.root, text="启动", width=10, command=self.run_pathcer)
        self.run_button.grid(row=2, column=1, padx=10, pady=10)

        # 显示选中的值
        self.info_label = tk.Label(self.root, text="", justify="left")
        self.info_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # patcher 进程管理
        self.process = None

        # 是否已经加载
        self.is_load = False
        
        # 获取英雄联盟路径
        self.game_path = self.getLoLPathByRegistry()
        print(f"found gamepath: {self.game_path}")
        
        # 启动主循环
        
        self.root.mainloop()
        if self.process:
            os.system('taskkill /t /f /pid {}'.format(self.process.pid))
            self.process = None
            
        self.control.running = False
        
    def getLoLPathByRegistry(self) -> str:
        """
        从注册表获取LOL的安装路径

        ** 只能获取到国服的路径, 外服不支持 **

        无法获取时返回空串
        """
        mainKey = winreg.HKEY_CURRENT_USER
        subKey = "SOFTWARE\Tencent\LOL"
        valueName = "InstallPath"

        try:
            with winreg.OpenKey(mainKey, subKey) as k:
                installPath, _ = winreg.QueryValueEx(k, valueName)
                path = str(Path(f"{installPath}\Game").absolute()
                        ).replace("\\", "/")
                return f"{path[:1].upper()}{path[1:]}"
        except FileNotFoundError:
            print("reg path or val does not exist.")
        except WindowsError as e:
            print(f"occurred while reading the registry: {e}")
        except Exception as e:
            print("unknown error reading registry", e)

        return ""        

    def start_auto_select(self):
        # 监听事件：
        listen_thread = threading.Thread(target=interact_with_lol, args=(self.control, self, ))
        listen_thread.start()
        
    
    def load_skin(self):
        champion_name = self.champion_combo.get()
        print(champion_name)
        if champion_name.find("-") != -1:
            champion_id = champion_name2id(champion_name.split()[0])
            skin_id = skin_name2id(int(champion_id), self.skin_combo.get())
        else:
            champion_id = -1
            skin_id = -1
        if champion_id != -1 and skin_id != -1:
            get_fantome(champion_id, skin_id)
            self.info_label.config(text="获取皮肤文件成功。")
            merge_fantome(self.game_path)
            self.info_label.config(text="加载皮肤成功。")
            self.is_load = True
        else:
            self.info_label.config(text="错误：请选择英雄和皮肤")
    
    def run_pathcer(self):
        if not self.is_load:
            self.info_label.config(text="错误：请先加载")
            return
        if self.process is None:
            self.process = runpatcher()
            
            self.champion_combo.config(state='disable')
            self.skin_combo.config(state='disable')
            self.load_button.config(state='disable')
            
            self.info_label.config(text="运行中。。。")
            self.run_button.config(text="停止")
        else:
            subprocess.run('taskkill /t /f /pid {}'.format(self.process.pid), shell=True)
            self.process = None
            
            self.champion_combo.config(state='readonly')
            self.skin_combo.config(state='readonly')
            self.load_button.config(state='normal')
            
            self.info_label.config(text="已停止")
            self.run_button.config(text="启动")

    def on_champion_combo_select(self, _):
        champion_name = self.champion_combo.get()
        if champion_name.find("-") != -1:
            champion_id = champion_name2id(champion_name.split()[0])
            skin_name_list = [i[0] for i in get_skin_by_champion_id(champion_id)]
            self.skin_combo.config(values=skin_name_list)
            self.skin_combo.set(skin_name_list[0])
        else:
            self.skin_combo = ttk.Combobox(self.root, values=["(请选择英雄)"], state="readonly")
            self.skin_combo.set("(请选择英雄)")
            
    def get_and_select_champion(self):
        
        id_json = helper.get_selected_champion_id()
        try:
            id_json = int(id_json)
            if id_json > 0:
                self.champion_combo.set(champion_id2name(id_json) + " - " + champion_id2title(id_json))
                self.on_champion_combo_select(0)
        except Exception:
            pass
        

class Control:
    def __init__(self) -> None:
        self.running = True

def interact_with_lol(control, window: Window):
    listener = LcuWebSocket(helper.token, helper.port)
    listener.current_champion_id = -1
    listener.current_summoner_id = helper.get_current_summoner()
    print(listener.current_summoner_id)

    @listener.subscribe(event='OnJsonApiEvent_lol-champ-select_v1_session',
                                    uri='/lol-champ-select/v1/session',
                                    type=('Update',))
    async def onChampSelectChanged(event):
        myteam = event['data']['myTeam']
        for summoner in myteam:
            if summoner['summonerId'] == listener.current_summoner_id and listener.current_champion_id != summoner['championId'] and summoner['championId'] > 0:
                listener.current_champion_id = summoner['championId']
                window.champion_combo.set(champion_id2name(listener.current_champion_id) + " - " + champion_id2title(listener.current_champion_id))
                window.on_champion_combo_select(0)

    async def start_c():
        asyncio.create_task(listener.start())
        cnt = 0
        while control.running:
            cnt += 1
            # print(cnt)
            await asyncio.sleep(1)
        asyncio.create_task(listener.close())

    asyncio.run(start_c())

if __name__ == '__main__':
    helper = LOLhelp()
    window = Window()
