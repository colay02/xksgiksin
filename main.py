import tkinter as tk
import subprocess
import os
import threading
import winreg
from pathlib import Path
import ttkbootstrap as ttk
# from tkinter import ttk
from utils.convert import *
from utils.fantome import get_fantome, merge_fantome, runpatcher
from utils.get_champion_jsons import check_resources_file, download_all, get_lol_version, get_local_version
from connector.lcusocket import LcuWebSocket
from connector.loloperations import LOLhelp
from PIL import Image, ImageTk
import asyncio
import ctypes



class Window:
    def __init__(self) -> None:
        # 创建主窗口
        self.root = tk.Tk()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP)
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(side=tk.BOTTOM)
        # ttk.Style().theme_use("vista")
        self.root.title("换肤")

        if not ctypes.windll.shell32.IsUserAnAdmin():
            self.skin_label = ttk.Label(self.main_frame, text="请用管理员模式打开程序")
            self.skin_label.grid(row=0, column=0, padx=10, pady=5)
            self.root.mainloop()
            return

        # 创建第一个下拉框
        self.champion_label = ttk.Label(self.main_frame, text="选择英雄：")
        self.champion_label.grid(row=0 ,column=0, padx=10, pady=5)

        self.champion_combo = ttk.Combobox(self.main_frame, values=["(请选择)"], state="readonly")
        self.champion_combo.grid(row=0, column=1, padx=0, pady=5)
        self.champion_combo.set("(请选择)")
        self.champion_combo.bind("<<ComboboxSelected>>", self.on_champion_combo_select)
        
        self.get_champion_button = ttk.Button(self.main_frame, text="获取当前英雄", command=self.get_and_select_champion)
        self.get_champion_button.grid(row=0, column=2, padx=10, pady=5)

        # 创建第二个下拉框
        self.skin_label = ttk.Label(self.main_frame, text="选择皮肤：")
        self.skin_label.grid(row=1, column=0, padx=10, pady=5)

        self.skin_combo = ttk.Combobox(self.main_frame, values=["(请选择英雄)"], state="readonly")
        self.skin_combo.grid(row=1, column=1, padx=0, pady=5)
        self.skin_combo.set("(请选择英雄)")

        # 创建两个并排按钮
        # self.load_button = tk.Button(self.root, text="加载皮肤", width=10, command=self.load_skin)
        # self.load_button.grid(row=2, column=0, padx=10, pady=10)

        self.run_button = ttk.Button(self.main_frame, text="启动", width=10, command=self.run_pathcer)
        self.run_button.grid(row=1, column=2, padx=10, pady=5)

        # 显示选中的值
        self.info_label = ttk.Label(self.info_frame, text="", anchor="w")
        self.info_label.pack(pady=10, anchor='w', side='left')
        
        def open_event():
            # 锁定ui
            self.champion_combo.config(state='disable')
            self.skin_combo.config(state='disable')
            self.get_champion_button.config(state='disable')
            self.run_button.config(state='disable')

            # 检查皮肤json更新
            if not check_resources_file() or get_local_version() != get_lol_version():
                self.info_label.config(text='正在更新皮肤资源')
                
                def handler(progress_text):
                    self.info_label.config(text=f'正在更新 ({progress_text})')
                download_all(handler)
                
                self.info_label.config(text='更新完成')

            load_resource_file()
            self.champion_combo.config(values=["(请选择)"] + get_champion_list())
            
            # 开启自动选英雄
            self.control = Control()
            self.info_label.config(text='正在连接到客户端')
            def window_handler(retry_str):
                self.info_label.config(text=retry_str)
            self.helper = LOLhelp(window_handler)
            if self.helper.loaded:
                self.info_label.config(text='已连接到客户端')
                threading.Thread(target=interact_with_lol, args=(self.control, self, )).start()
            else:
                self.info_label.config(text='没有连接到英雄联盟客户端，请手动选择英雄')
                
            # 恢复ui
            self.champion_combo.config(state='readonly')
            self.skin_combo.config(state='readonly')
            self.get_champion_button.config(state='normal' if self.helper.loaded else 'disabled')
            self.run_button.config(state='normal')
                
        threading.Thread(target=open_event).start()
        
        # patcher 进程管理
        self.process = None

        # 是否已经加载
        self.is_load = False
        
        # 获取英雄联盟路径
        self.game_path = self.getLoLPathByRegistry()
        print(f"found gamepath: {self.game_path}")
        
        # 启动主循环
        ico = Image.open(get_resource_path('neeko.ico'))
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
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

    
    def run_pathcer(self):
        if self.process is None:
            champion_name = self.champion_combo.get()
            print(champion_name)
            if champion_name.find("-") != -1:
                champion_id = champion_name2id(champion_name.split()[0])
                skin_id = skin_name2id(int(champion_id), self.skin_combo.get())
            else:
                champion_id = -1
                skin_id = -1
            if champion_id != -1 and skin_id != -1:
                def thread_wrapper():
                    self.champion_combo.config(state='disable')
                    self.skin_combo.config(state='disable')
                    self.get_champion_button.config(state='disable')
                    self.run_button.config(state='disable')
                    
                    self.info_label.config(text='(Step 1/2): 获取皮肤文件中')
                    get_fantome(champion_id, skin_id)
                    self.info_label.config(text="(Step 2/2): 合并皮肤文件中")
                    merge_fantome(self.game_path)
                    
                    
                    self.process = runpatcher()
                    
                    self.info_label.config(text="运行中")
                    self.run_button.config(state='normal')
                    self.run_button.config(text="停止")
                threading.Thread(target=thread_wrapper).start()
            else:
                self.info_label.config(text="错误：请选择英雄和皮肤")
            
        else:
            subprocess.run('taskkill /t /f /pid {}'.format(self.process.pid), shell=True)
            self.process = None
            
            self.champion_combo.config(state='readonly')
            self.skin_combo.config(state='readonly')
            self.get_champion_button.config(state='normal' if self.helper.loaded else 'disabled')
            
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
        if not self.helper.loaded:
            self.info_label.config(text='没有连接到英雄联盟客户端，请手动选择英雄')
            return
        
        id_json = self.helper.get_selected_champion_id()
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
    listener = LcuWebSocket(window.helper.token, window.helper.port)
    listener.current_champion_id = -1
    listener.current_summoner_id = window.helper.get_current_summoner()
    print(listener.current_summoner_id)

    @listener.subscribe(event='OnJsonApiEvent_lol-champ-select_v1_session',
                                    uri='/lol-champ-select/v1/session',
                                    type=('Update',))
    async def onChampSelectChanged(event):
        if window.process:
            return
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
    window = Window()
