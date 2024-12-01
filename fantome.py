import requests
import subprocess
import shutil
import os
import logging

mod_tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mod-tools.exe")

def get_fantome(champion_id, skin_id):
    url = f"https://raw.githubusercontent.com/koobzaar/lol-skins-developer/refs/heads/main/{champion_id}/{skin_id}.fantome"
    response = requests.get(url)
    os.makedirs("temp", exist_ok=True)
    if response.status_code == 200:
        with open("temp/temp.fantome", "wb") as f:
            f.write(response.content)
        return True
    else:
        print(response, url)
        return False
    
def merge_fantome(game_path: str):
    shutil.rmtree("temp/unzipped")
    os.makedirs("temp/unzipped", exist_ok=True)
    subprocess.run(f"{mod_tools_path} import temp/temp.fantome temp/unzipped", shell=True, stdout=subprocess.DEVNULL)
    print("Successfully unzipped.")
    subprocess.run(f"{mod_tools_path} mkoverlay temp temp/profile --mods:unzipped --game:{game_path}", shell=True, stdout=subprocess.DEVNULL)
    print("Successfully merged.")

def runpatcher():
    return subprocess.Popen(f"{mod_tools_path} runoverlay temp/profile nouse", shell=True, stdout=subprocess.DEVNULL)
    
    
if __name__ == '__main__':
    print(get_fantome(104, 2))
    # merge_fantome(r"E:\games\WeGameApps\英雄联盟\Game")
    runpatcher()