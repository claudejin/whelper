from tkinter import *
from functools import partial
from bs4 import BeautifulSoup as bs
import requests  # request img from web
import shutil  # save img locally
import os
import glob
import yaml
import semver

################################################################################
initial_message = ""
################################################################################


class MainWindow:
    def run(self, config_data):
        self.config = config_data
        self.main(self.check_new_version())

    def check_new_version(self):
        # Check latest version
        vinfo = (
            "https://raw.githubusercontent.com/claudejin/whelper/main/updatelist.txt"
        )
        f = requests.get(vinfo, headers={"Cache-Control": "no-cache"})
        lines = f.text.splitlines()
        latest_version = lines[0]

        # Compare versions
        print(
            "Current version:",
            self.config["version"],
            "Latest version:",
            latest_version,
        )
        if semver.compare(self.config["version"], latest_version) >= 0:
            return (False, latest_version)

        # Download updated files
        for filename in lines[1:]:
            new_file = (
                f"https://raw.githubusercontent.com/claudejin/whelper/main/{filename}"
            )
            res = requests.get(new_file, headers={"Cache-Control": "no-cache"})
            if res.status_code == 200:
                with open(f"{filename}", "w", encoding="utf8") as f:
                    f.write(res.text)

        return (True, latest_version)

    def open_and_save(self, imgurl, savepath):
        ext = imgurl.split(".")[-1]
        if len(ext) > 4:
            ext = "jpg"

        img_blob = requests.get(
            imgurl,
            stream=True,
            headers={
                "User-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36"
            },
        )
        if img_blob.status_code == 200:
            with open(f"{savepath}.{ext}", "wb") as f:
                shutil.copyfileobj(img_blob.raw, f)
        else:
            print("    Error: Image Couldn't be retrieved")

    def get_image_list(self, url_string):
        res = requests.get(url_string, stream=True)
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

    def download_images(self, *args):
        url = args[0], args[1]
        save_directory = self.config["save_directory"]

        # Delete previous images
        if self.config["delete_previous_images"]:
            for i in range(self.config["delete_previous_items"] + 1):
                for e in self.config["extensions"]:
                    for p in glob.glob(f"{save_directory}/{i}.{e}"):
                        os.remove(p)

        print(f"## DOWNLOAD from: {url.get()}")

        # Download
        images = self.get_image_list(url.get())
        if len(images) > 0:
            i = 1
            for img in images:
                imgurl = img["src"].split("?")[0]
                print(f"    {i:02d}: {imgurl}")
                if imgurl[:2] == "//":
                    imgurl = f"https:{imgurl}"
                    print(f"      => Adding https: in the front")

                try:
                    self.open_and_save(imgurl, f"{save_directory}/{i}")
                except requests.exceptions.SSLError:
                    print("      => Error: requests SSL, trying http instead")
                    imgurl = imgurl.replace("https://", "http://")
                    print(f"      => {i:02d}: {imgurl}")

                    self.open_and_save(imgurl, f"{save_directory}/{i}")

                i += 1
            print(f"    DONE\n")
            url.delete(0, "end")
        else:
            print("    Error: Wrong product URL\n")
            url.delete(0, "end")
            url.insert(0, "Error: Wrong product URL")

    def main(self, updated):
        # TODO: config 파일이 존재하지 않을 경우, 서버에서 디폴트 파일 가져오도록 구현
        window = Tk()
        window.title(f"whelper v" + self.config["version"])
        window.geometry("640x200")
        window.resizable(False, False)

        label = Label(window, text="url")
        label.pack()

        url = Entry(window)
        url.pack(fill="x")
        url.focus()

        if updated[0]:
            initial_message = f"최신 버전 {updated[1]}로 업데이트 되었습니다. 다시 시작하세요!"
            url.insert(0, initial_message)
        else:
            button = Button(
                window,
                text="download",
                command=partial(self.download_images, self, url),
            )
            button.pack()
            url.bind("<Return>", partial(self.download_images, self, url))

        window.mainloop()
