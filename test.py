import requests  # request img from web
from os import makedirs
from os.path import dirname

new_file = f"https://raw.githubusercontent.com/claudejin/whelper/main/whelper.pyw"
res = requests.get(new_file, headers={"Cache-Control": "no-cache"})
if res.status_code == 200:
    makedirs(dirname("hi/new_file"), exist_ok=True)
