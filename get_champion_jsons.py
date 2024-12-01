import requests
from tqdm import tqdm
import json
url = "https://ddragon.leagueoflegends.com/cdn/14.23.1/data/zh_CN/champion.json"
champion_json = requests.get(url).json()

json.dump(champion_json, open("champion.json", "w", encoding='utf-8'), indent=4, ensure_ascii=False)


# url_base = 'https://ddragon.leagueoflegends.com/cdn/14.23.1/data/zh_CN/champion/{cn}.json'

# skin_dict = {}

# for name in tqdm(champion_json['data']):
#     nowjson = requests.get(url_base.format(cn=name)).json()
#     champion_id = champion_json['data'][name]['key']
#     skin_dict[champion_id] = []
#     for skin in nowjson['data'][name]['skins']:
#         skin_dict[champion_id].append((skin['name'], skin['num'], skin['chromas']))


# # print(skin_dict['Aatrox'])
# json.dump(skin_dict, open("champion.json", "w", encoding='utf-8'), indent=4, ensure_ascii=False)
        