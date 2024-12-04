import requests
import subprocess
import shutil
import os
import logging
import tempfile
from utils.convert import get_resource_path

mod_tools_path = get_resource_path("backend/mod-tools.exe")
temp_path = get_resource_path("temp")

def get_fantome(champion_id, skin_id):
    url = f"http://skin.khoray.top/lol-skins-developer/{champion_id}/{skin_id}.fantome"
    response = requests.get(url)
    os.makedirs(f"{temp_path}", exist_ok=True)
    if response.status_code == 200:
        with open(f"{temp_path}/temp.fantome", "wb") as f:
            f.write(response.content)
        return True
    else:
        print(response, url)
        return False
    
def merge_fantome(game_path: str):
    shutil.rmtree(f"{temp_path}/unzipped", ignore_errors=True)
    os.makedirs(f"{temp_path}/unzipped", exist_ok=True)
    subprocess.run(f"{mod_tools_path} import {temp_path}/temp.fantome {temp_path}/unzipped", shell=True, stdout=subprocess.DEVNULL)
    print("Successfully unzipped.")
    subprocess.run(f"{mod_tools_path} mkoverlay {temp_path} {temp_path}/profile --mods:unzipped --game:{game_path}", shell=True, stdout=subprocess.DEVNULL)
    print("Successfully merged.")

def runpatcher():
    return subprocess.Popen(f"{mod_tools_path} runoverlay {temp_path}/profile nouse", shell=True)
    
    
if __name__ == '__main__':
    print(get_fantome(104, 2))
    # merge_fantome(r"E:\games\WeGameApps\英雄联盟\Game")
    runpatcher()