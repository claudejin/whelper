import semver
from os import remove, makedirs
from shutil import rmtree, copyfileobj
from os.path import exists, expanduser, normpath, dirname
import requests
from sys import executable
import subprocess as sp

from tkinter import Tk, PhotoImage, Label
from core.view.components import AnimatedGif
from core.util.task import BackgroundTask


class InstallManager:
    def migrate_if_possible(self):
        home_path = normpath(expanduser("~"))

        info_py_path = f"{home_path}/info.py"
        if exists(info_py_path):
            remove(info_py_path)

        # whelper_py_path = f"{home_path}/whelper.pyw"
        # if exists(whelper_py_path):
        #     remove(whelper_py_path)

        pycache_path = f"{home_path}/__pycache__"
        if exists(pycache_path):
            rmtree(pycache_path)

    def check_new_version(self, current_version):
        vinfo = (
            "https://raw.githubusercontent.com/claudejin/whelper/main/updatelist.txt"
        )
        res = requests.get(vinfo, headers={"Cache-Control": "no-cache"})
        if res.status_code != 200:
            return False

        lines = res.text.splitlines()
        latest_version = lines[0]

        # Compare versions
        print(
            "Current version:",
            current_version,
            "Latest version:",
            latest_version,
        )
        if semver.compare(current_version, latest_version) >= 0:
            return False, []

        return True, lines

    def update(self, config, response):
        print(response)
        # Download updated files
        try:
            for i, filename in zip(range(len(response) - 1), response[1:]):
                self.message.configure(text=f"업데이트 중... ({i} /{len(response)-1})")
                if filename[:3] == "pip":
                    sp.check_call(
                        [executable, "-m", "pip", "install", filename.split()[1]]
                    )
                    continue

                print(filename)

                new_file = f"https://raw.githubusercontent.com/claudejin/whelper/main/{filename}"

                res = requests.get(
                    new_file,
                    stream=True,
                    headers={
                        "User-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
                        "Cache-Control": "no-cache",
                    },
                )

                if res.status_code == 200:
                    save_filename = f"{config['pwd']}/{filename}"
                    makedirs(normpath(dirname(save_filename)), exist_ok=True)
                    if new_file.split(".")[-1] in ["py", "pyw", "yaml"]:
                        with open(save_filename, "w", encoding="utf8") as f:
                            f.write(res.text)
                    else:
                        with open(save_filename, "wb") as f:
                            copyfileobj(res.raw, f)

            config["version"] = response[0]
            config.save()
        except Exception as e:
            print(e)
            return False

        return True

    def run(self, config, response):
        self.config = config

        self.window = window = Tk()
        window.iconphoto(True, PhotoImage(file=f"{config['resources']}/student.png"))
        window.title("whelper updater to v" + self.config["version"])
        window.overrideredirect(True)

        window_height = 160
        window_width = 160
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (window_width / 2))
        y_coordinate = int((screen_height / 2) - (window_height / 2))
        window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        window.resizable(False, False)

        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        window.rowconfigure(1, weight=1)

        self.animation = AnimatedGif(
            window, f"{config['resources']}/spinning_earth.gif"
        )
        self.animation.grid(row=0, column=0, pady=8)

        self.message = Label(window, text=f"업데이트 중... (0 /{len(response)-1})")
        self.message.grid(row=1, column=0, pady=8)

        bgtask = BackgroundTask()
        bgtask.start(self.download, config, response)

        window.mainloop()

    def download(self, is_running_func, config, response):
        self.animation.enable_animation()

        try:
            if self.update(config, response):
                self.message.configure(text="성공: 업데이트", foreground="green")
                self.window.after(1000, lambda: self.window.destroy())
            else:
                raise Exception("download failure")

        except Exception as e:
            self.message.configure(text="에러 발생: 업데이트", foreground="red")
            print(e)
        finally:
            self.animation.cancel_animation()


if __name__ == "__main__":
    print("Wrong access")
