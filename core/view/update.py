# https://api.github.com/repos/claudejin/whelper/releases/latest

import requests
from os import remove, makedirs
from shutil import rmtree, copyfileobj
from os.path import normpath, dirname
from zipfile import ZipFile

def update():
    res = requests.get("https://api.github.com/repos/claudejin/whelper/releases/latest", headers={"Cache-Control": "no-cache"})
    if res.status_code != 200:
        return
    res_json = res.json()

    res2 = requests.get(f"https://api.github.com/repos/claudejin/whelper/git/ref/tags/v{res_json['name']}", headers={"Cache-Control": "no-cache"})
    if res2.status_code != 200:
        return
    sha = res2.json()["object"]["sha"][:7]

    zip_url = res_json["zipball_url"]
    res = requests.get(
            zip_url,
            stream=True,
            headers={
                "User-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
                "Cache-Control": "no-cache",
            },
        )

    if res.status_code != 200:
        return
    
    filename = zip_url.split("/")[-1]

    pwd = "."
    save_filename = f"{pwd}/{filename}-tmp"
    makedirs(normpath(dirname(save_filename)), exist_ok=True)
    with open(save_filename, "wb") as f:
        copyfileobj(res.raw, f)

    with ZipFile(save_filename, 'r') as f:
        f.extractall(f"{pwd}/")
    
    remove(save_filename)
    rmtree(f"claudejin-whelper-{sha}")

update()