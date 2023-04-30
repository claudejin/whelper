from tkinter import *
from functools import partial
from bs4 import BeautifulSoup as bs
import requests  # request img from web
import shutil  # save img locally
import os
import glob
from core.components import AnimatedGif, BackgroundTask


class MainWindow:
    def run(self, config):
        self.config = config

        self.window = window = Tk()
        window.title(f"whelper v" + self.config["version"])
        window.geometry("640x200")
        window.resizable(False, False)

        label = Label(window, text="Product URL")
        label.pack()

        url = Entry(window)
        url.pack(fill="x", padx=16, pady=8)
        url.focus()

        bgtask = BackgroundTask(self.download_images)

        button = Button(
            window,
            text="Download",
            command=partial(bgtask.start, url),
        )
        button.pack()
        url.bind("<Return>", partial(bgtask.start, url))

        self.animation = AnimatedGif(
            window, "/Users/minah/whelper/resources/small_globe.gif"
        )
        self.animation.pack()
        # Button(window, text="start animation", command=self.animation.enable_animation).pack()
        # Button(window, text="stop animation", command=self.animation.cancel_animation).pack()

        window.mainloop()

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

    def remove_previous_images(self):
        # Remove previous images
        if self.config["delete_previous_images"]:
            for i in range(self.config["delete_previous_items"] + 1):
                for e in self.config["extensions"]:
                    for p in glob.glob(f"{self.config['save_directory']}/{i}.{e}"):
                        os.remove(p)

    def download_images(self, is_running_func, *args):
        self.animation.enable_animation()

        try:
            url = args[0]

            self.remove_previous_images()

            url_string = url.get().strip()
            if not url_string:
                print("## Invalid url")
                self.animation.cancel_animation()
                return

            print(f"## DOWNLOAD from: {url_string}")

            # Download
            images = self.get_image_list(url_string)
            if len(images) > 0:
                i = 1
                for img in images:
                    imgurl = img["src"].split("?")[0]
                    print(f"    {i:02d}: {imgurl}")
                    if imgurl[:2] == "//":
                        imgurl = f"https:{imgurl}"
                        print(f"      => Adding https: in the front")

                    try:
                        self.open_and_save(
                            imgurl, f"{self.config['save_directory']}/{i}"
                        )
                    except requests.exceptions.SSLError:
                        print("      => Error: requests SSL, trying http instead")
                        imgurl = imgurl.replace("https://", "http://")
                        print(f"      => {i:02d}: {imgurl}")

                        self.open_and_save(
                            imgurl, f"{self.config['save_directory']}/{i}"
                        )

                    i += 1
                print(f"    DONE\n")
                url.delete(0, "end")
            else:
                print("    Error: Wrong product URL\n")
                url.delete(0, "end")
                url.insert(0, "Error: Wrong product URL")
        except Exception as e:
            print(e)
        finally:
            self.animation.cancel_animation()
