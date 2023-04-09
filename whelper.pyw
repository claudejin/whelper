#!/usr/local/bin/python3

from tkinter import *
from functools import partial
from bs4 import BeautifulSoup as bs
import requests # request img from web
import shutil # save img locally
import os
import glob
import yaml
import semver

################################################################################
version = "0.7.0"
config_path = os.path.expanduser("~/wconfig.txt")
initial_message = ""
################################################################################

def check_new_version():
    # Check latest version
    vinfo = "https://raw.githubusercontent.com/claudejin/whelper/main/updatelist.txt"
    f = requests.get(vinfo)
    lines = f.text.splitlines()
    latest_version = lines[0]

    # Compare versions
    print("Current version:", version, "Latest version:", latest_version)
    if semver.compare(version, latest_version) >= 0: return
    
    # Download updated files
    for filename in lines[1:]:
        new_file = f"https://raw.githubusercontent.com/claudejin/whelper/main/{filename}"
        res = requests.get(new_file)
        if res.status_code == 200:
            with open(f"{filename}",'w', encoding="utf8") as f:
                f.write(res.text)
    
    initial_message = f"최신 버전 {latest_version}로 업데이트 되었습니다. 다시 시작하세요!"

def open_and_save(imgurl, savepath):
    ext = imgurl.split('.')[-1]
    if len(ext) > 4:
        ext = "jpg"

    img_blob = requests.get(imgurl, stream = True, headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'})
    if img_blob.status_code == 200:
        with open(f"{savepath}.{ext}",'wb') as f:
            shutil.copyfileobj(img_blob.raw, f)
    else:
        print("    Error: Image Couldn\'t be retrieved")

def get_image_list(url_string):
    res = requests.get(url_string, stream = True)
    if res.status_code != 200:
        return []
    
    # parsing soup object
    soup = bs(res.text, "html.parser")
    
    # get images under marketing div
    marketing_container = soup.find_all(class_="marketing")[0]
    marketing_images = marketing_container.find_all("img")

    # exclude images under about_pdt div
    pdt_container = soup.find_all(class_="about_pdt")[0]
    pdt_images = pdt_container.find_all("img")  

    # final image list
    images = [img for img in marketing_images if img not in pdt_images]
    return images

def download_images(*args):
    config, url = args
    save_directory = config["save_directory"]

    # Delete previous images
    if config["delete_previous_images"]:
        for i in range(config["delete_previous_items"]+1):
            for e in config["extensions"]:
                for p in glob.glob(f"{save_directory}/{i}.{e}"):
                    os.remove(p)
    
    print(f"## DOWNLOAD from: {url.get()}")

    # Download
    images = get_image_list(url.get())
    if len(images) > 0:
        i = 1
        for img in images:
            imgurl = img['src'].split('?')[0]
            print(f"    {i:02d}: {imgurl}")
            if imgurl[:2] == "//":
                imgurl = f"https:{imgurl}"
                print(f"      => Adding https: in the front")

            try:
                open_and_save(imgurl, f"{save_directory}/{i}")
            except requests.exceptions.SSLError:
                print("      => Error: requests SSL, trying http instead")
                imgurl = imgurl.replace('https://', 'http://')
                print(f"      => {i:02d}: {imgurl}")

                open_and_save(imgurl, f"{save_directory}/{i}")

            i += 1
        print(f"    DONE\n")
        url.delete(0, 'end')
    else:
        print("    Error: Wrong product URL\n")
        url.delete(0, 'end')
        url.insert(0, "Error: Wrong product URL")

def main():
    # TODO: config 파일이 존재하지 않을 경우, 서버에서 디폴트 파일 가져오도록 구현
    with open(config_path, "r", encoding="utf8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    window = Tk()
    window.title(f"whelper v{version}")
    window.geometry("640x200")
    window.resizable(False, False)

    label = Label(window,text='url')
    label.pack()

    url=Entry(window)
    url.pack(fill='x')
    url.focus()
    url.insert(0, initial_message)
    
    button=Button(window, text="download", command=partial(download_images, config, url))
    button.pack()
    url.bind("<Return>", partial(download_images, config, url))

    window.mainloop()

if __name__ == "__main__":
    check_new_version()
    main()