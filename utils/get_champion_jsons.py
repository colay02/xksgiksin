# 用于获取最新皮肤 json
import requests
import os
from tqdm import tqdm
import json
url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
url_base = 'http://game.gtimg.cn/images/lol/act/img/js/hero/{cn}.js'


def check_resources_file():
    return all([os.path.exists(file) for file in ["resources/champion.json", "resources/champion_skin.json", "resources/version.txt"]])

def get_local_version():
    with open("resources/version.txt", "r") as f:
        version = f.read()
    return version

def get_lol_version():
    champion_json_raw = requests.get(url).json()
    return champion_json_raw['version']

def download_all(update_handler):
    os.makedirs("resources", exist_ok=True)
    # 更新英雄文件
    champion_json_raw = requests.get(url).json()

    champion_json = []
    for champion in champion_json_raw['hero']:
        champion_json.append({'key': champion['heroId'], 'title': champion['title'], 'name': champion['name']})

    json.dump(champion_json, open("resources/champion.json", "w", encoding='utf-8'), indent=4, ensure_ascii=False)

    # 更新皮肤文件
    
    skin_dict = {}

    for i, champion in enumerate(champion_json):
        champion_id = champion['key']
        nowjson = requests.get(url_base.format(cn=champion_id)).json()
        skin_dict[champion_id] = []
        for skin in nowjson['skins']:
            skin_dict[champion_id].append((skin['name'], int(skin['skinId'][-3:]), skin['chromas']))
        update_handler(f"{i}/{len(champion_json)}")


    # print(skin_dict['Aatrox'])
    json.dump(skin_dict, open("resources/champion_skin.json", "w", encoding='utf-8'), indent=4, ensure_ascii=False)
    
    # 更新版本文件
    with open("resources/version.txt", "w") as f:
        f.write(champion_json_raw['version'])