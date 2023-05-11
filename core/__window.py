from tkinter import *
import requests
from bs4 import BeautifulSoup as bs
from core.components import AnimatedGif, BackgroundTask
from .__downloader import download_images, detect_youtube
from .util import stack_cuts
from functools import partial


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

        bgtask = BackgroundTask()

        url_label = Label(window, text="Product URL")
        url_label.grid(row=1, column=0, padx=8)

        self.url = Entry(window)
        self.url.grid(row=1, column=1, columnspan=2, sticky="we", padx=8)
        self.url.bind("<Return>", partial(bgtask.start, self.download))
        self.url.focus()

        download_button = Button(
            window,
            text="다운로드",
            command=partial(bgtask.start, self.download),
        )
        download_button.grid(row=2, column=0, columnspan=3, sticky="we", padx=8, pady=4)

        self.youtube_frame = Frame(window)

        youtube_scroller = Scrollbar(self.youtube_frame)
        self.youtube_codes = Text(
            self.youtube_frame, yscrollcommand=youtube_scroller.set, height=10
        )
        youtube_scroller.config(command=self.youtube_codes.yview)
        self.youtube_codes.grid(row=0, column=0, sticky="nsew")
        youtube_scroller.grid(row=0, column=1, sticky="nsw")

        self.message = Label(window, text="", foreground="red")
        self.message.grid(row=4, column=0, columnspan=2, padx=8, sticky="w", pady=4)

        setting_button = Button(window, text="설정", state="disabled")
        setting_button.grid(row=4, column=2, sticky="we", padx=8, pady=4)

        self.stack_frame = LabelFrame(window, text="합치기")

        Label(self.stack_frame, text="시작").grid(row=0, column=0, padx=4, pady=4)
        self.stack_start = Entry(self.stack_frame)
        self.stack_start.grid(row=0, column=1, sticky="we", padx=4, pady=4)
        Label(self.stack_frame, text="종료").grid(row=0, column=2, padx=4, pady=4)
        self.stack_end = Entry(self.stack_frame)
        self.stack_end.grid(row=0, column=3, sticky="we", padx=4, pady=4)
        Label(self.stack_frame, text="제외").grid(row=1, column=0, padx=4, pady=4)
        self.stack_exclude = Entry(self.stack_frame)
        self.stack_exclude.grid(row=1, column=1, sticky="we", padx=4, pady=4)
        Button(
            self.stack_frame,
            text="실행",
            command=partial(bgtask.start, self.stack_images),
        ).grid(row=1, column=2, columnspan=2, sticky="we", padx=8, pady=4)

        window.mainloop()

    def download(self, is_running_func):
        self.animation.enable_animation()

        self.youtube_codes.delete(0.0, "end")
        self.message.configure(text="")

        try:
            url_string = self.url.get().strip()
            if not url_string:
                print("## Invalid url")
                return False

            print(f"## DOWNLOAD from: {url_string}")
            res = requests.get(url_string, stream=True)
            if res.status_code == 200:
                soup = bs(res.text, "html.parser")

                codes = detect_youtube(soup)
                if codes:
                    self.youtube_codes.insert(0.0, "\n\n".join(codes))
                    self.youtube_frame.grid(
                        row=3, column=0, columnspan=3, sticky="nsew", padx=8, pady=4
                    )
                    self.window.geometry("510x360")
                else:
                    self.youtube_frame.grid_forget()
                    self.window.geometry("510x200")

                self.images = download_images(soup, self.config)
                if self.images:
                    self.message.configure(
                        text=f"성공: 다운로드 {len(self.images)}개", foreground="green"
                    )
                    self.window.after(3000, lambda: self.message.configure(text=""))
                    self.url.delete(0, "end")
                else:
                    raise Exception("download failure")

                if len(self.images) > 1:
                    self.stack_frame.grid(
                        row=5, column=0, columnspan=3, sticky="nsew", padx=12, pady=4
                    )
                    self.window.geometry("510x360")
                else:
                    self.stack_frame.grid_forget()
                    self.window.geometry("510x200")

        except Exception as e:
            self.message.configure(text="에러 발생", foreground="red")
            print(e)
        finally:
            self.animation.cancel_animation()

    def stack_images(self, is_running_func):
        self.animation.enable_animation()

        try:
            start = int(self.stack_start.get().strip())
            end = int(self.stack_end.get().strip())
            exclude = [int(i) for i in self.stack_exclude.get().strip().split()]

            print(start, end, exclude)
            stack_cuts(self.images, start, end, exclude, self.config)

            if start < end:
                self.message.configure(text=f"성공: 합치기", foreground="green")
                self.window.after(3000, lambda: self.message.configure(text=""))
                self.stack_start.delete(0, "end")
                self.stack_end.delete(0, "end")
                self.stack_exclude.delete(0, "end")
            else:
                raise Exception("stack failure")

        except Exception as e:
            self.message.configure(text="에러 발생", foreground="red")
            print(e)
        finally:
            self.animation.cancel_animation()
