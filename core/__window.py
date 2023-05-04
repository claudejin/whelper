from tkinter import *
from functools import partial
from core.components import AnimatedGif, BackgroundTask
from .__downloader import download_images


class MainWindow:
    def run(self, config):
        self.config = config

        self.window = window = Tk()
        window.title(f"whelper v" + self.config["version"])
        window.geometry("510x200")
        window.resizable(False, False)

        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=10)
        window.columnconfigure(2, weight=1)

        self.animation = AnimatedGif(
            window, f"{config['resources']}/spinning_earth.gif"
        )
        self.animation.grid(row=0, column=0, columnspan=3, pady=16)

        bgtask = BackgroundTask(self.background_task)

        url_label = Label(window, text="Product URL")
        url_label.grid(row=1, column=0, padx=8)

        self.url = Entry(window)
        self.url.grid(row=1, column=1, columnspan=2, sticky="we", padx=8)
        self.url.bind("<Return>", bgtask.start)
        self.url.focus()

        download_button = Button(
            window,
            text="다운로드",
            command=bgtask.start,
        )
        download_button.grid(row=2, column=0, columnspan=3, sticky="we", padx=8, pady=4)

        self.message = Label(window, text="", foreground="red")
        self.message.grid(row=3, column=0, columnspan=2, padx=8, sticky="w", pady=4)

        setting_button = Button(window, text="설정")
        setting_button.grid(row=3, column=2, sticky="we", padx=8, pady=4)

        window.mainloop()

    def background_task(self, is_running_func):
        self.animation.enable_animation()

        url_string = self.url.get()
        if download_images(url_string, self.config):
            self.message.configure(text="성공", foreground="green")
            self.window.after(3000, partial(self.message.configure, text=""))
        else:
            self.message.configure(text="실패", foreground="red")

        self.url.delete(0, "end")
        self.animation.cancel_animation()
