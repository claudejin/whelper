#!/usr/local/bin/python3

from tkinter import *
from bs4 import BeautifulSoup as bs
import requests # request img from web
import shutil # save img locally
import os
import glob
import yaml

version = "0.5"
config_path = os.path.expanduser("~/wconfig.txt")

if __name__ == "__main__":
    with open(config_path, "r", encoding="utf8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    save_directory = config["save_directory"]

    window = Tk()
    window.title(f"whelper v{version}")
    window.geometry("640x200")
    window.resizable(False, False)

    label = Label(window,text='url')
    label.pack()

    url=Entry(window)
    url.pack(fill='x')
    url.focus()

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

    def download_images(*args):
        print(f"## DOWNLOAD from: {url.get()}")
        # Delete previous images
        if config["delete_previous_images"]:
            for i in range(config["delete_previous_items"]+1):
                for e in config["extensions"]:
                    for p in glob.glob(f"{save_directory}/{i}.{e}"):
                        os.remove(p)

        # Parse page
        res = requests.get(url.get(), stream = True)
        if res.status_code == 200:
            soup = bs(res.text, "html.parser")
            container = soup.find_all(class_="marketing")[0]
            images = container.find_all("img")

            i = 1
            for img in images:
                imgurl = img['src'].split('?')[0]
                print(f"    {i:02d}: {imgurl}")

                try:
                    open_and_save(imgurl, f"{save_directory}/{i}")
                except requests.exceptions.SSLError:
                    print("      => Error: requests SSL, trying http instead")
                    imgurl = imgurl.replace('https://', 'http://')
                    print(f"      => {i:02d}: {imgurl}")

                    open_and_save(imgurl, f"{save_directory}/{i}")

                i += 1
        else:
            print("    Error: Wrong product URL")
        
        print()
        url.delete(0, 'end')
    
    button=Button(window, text="download", command=download_images)
    button.pack()
    url.bind("<Return>", download_images)

    # The following three commands are needed so the window pops
    # up on top on Windows...
    # window.iconify()
    # window.update()
    # window.deiconify()
    window.mainloop()
