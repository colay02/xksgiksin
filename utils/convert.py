import json
import os
import sys

def get_resource_path(name):
    """ 获得资源的绝对路径 """
    try:
        # PyInstaller 创建临时文件夹时会将路径存入 sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # 不是 exe 执行环境，未找到 sys._MEIPASS，使用当前路径
        base_path = os.path.abspath(".")
    return os.path.join(base_path, name)

champion_json = json.load(open(get_resource_path("champion.json"), 'r', encoding='utf-8'))
skin_json = json.load(open(get_resource_path("champion_skin.json"), 'r', encoding='utf-8'))

def skin_name2id(champion_id: int, name: str):
    skins = skin_json[str(champion_id)]
    for skin in skins:
        if skin[0] == name:
            return skin[1]
    return -1

def champion_name2id(name: str):
    champions = champion_json['data']
    for champion in champions.values():
        if champion['name'] == name:
            return int(champion['key'])
    return -1

def champion_id2name(id: int):
    champions = champion_json['data']
    for champion in champions.values():
        if champion['key'] == str(id):
            return champion['name']
    return -1

def champion_id2title(id: int):
    champions = champion_json['data']
    for champion in champions.values():
        if champion['key'] == str(id):
            return champion['title']
    return -1

def get_champion_list():
    ret = []
    champions = champion_json['data']
    for champion in champions.values():
        ret.append(champion['name'] + " - " + champion['title'])
    return ret

def get_skin_by_champion_id(champion_id: int):
    return skin_json[str(champion_id)]