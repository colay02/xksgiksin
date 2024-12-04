# 用于获取最新皮肤 json
import requests
from tqdm import tqdm
import json
url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
champion_json_raw = requests.get(url).json()

champion_json = []
for champion in champion_json_raw['hero']:
    champion_json.append({'key': champion['heroId'], 'title': champion['title'], 'name': champion['name']})

json.dump(champion_json, open("champion.json", "w", encoding='utf-8'), indent=4, ensure_ascii=False)


url_base = 'http://game.gtimg.cn/images/lol/act/img/js/hero/{cn}.js'

skin_dict = {}

for champion in tqdm(champion_json):
    champion_id = champion['key']
    nowjson = requests.get(url_base.format(cn=champion_id)).json()
    skin_dict[champion_id] = []
    for skin in nowjson['skins']:
        skin_dict[champion_id].append((skin['name'], int(skin['skinId'][-3:]), skin['chromas']))


# print(skin_dict['Aatrox'])
json.dump(skin_dict, open("champion_skin.json", "w", encoding='utf-8'), indent=4, ensure_ascii=False)
        