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
        self.default_size = (510, 200)
        self.additional_size = 160
        self.additional_cnt = 0

        self.window = window = Tk()
        window.iconphoto(True, PhotoImage(file=f"{config['resources']}/student.png"))
        window.title(f"whelper v" + self.config["version"])
        window.geometry(f"{self.default_size[0]}x{self.default_size[1]}")
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

        self.message = Label(window, text="", foreground="red")
        self.message.grid(row=3, column=0, columnspan=2, padx=8, sticky="w", pady=4)

        setting_button = Button(window, text="설정", state="disabled")
        setting_button.grid(row=3, column=2, sticky="we", padx=8, pady=4)

        self.youtube_frame = Frame(window)

        youtube_scroller = Scrollbar(self.youtube_frame)
        self.youtube_codes = Text(
            self.youtube_frame, yscrollcommand=youtube_scroller.set, height=10
        )
        youtube_scroller.config(command=self.youtube_codes.yview)
        youtube_scroller.pack(
            side="right", fill="y"
        )  # .grid(row=0, column=1, sticky="nse")
        self.youtube_codes.pack(
            side="left", fill="both"
        )  # .grid(row=0, column=0, sticky="nsew")

        self.stack_frame = LabelFrame(window, text="합치기")
        self.stack_frame.columnconfigure(0, weight=1)

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
        ).grid(row=1, column=2, sticky="we", padx=8, pady=4)
        self.stack_overwrite = IntVar()
        Checkbutton(
            self.stack_frame, text="기존 스택 덮어쓰기", variable=self.stack_overwrite
        ).grid(row=1, column=3, padx=8, pady=4)

        window.mainloop()

    def download(self, is_running_func):
        self.animation.enable_animation()

        self.youtube_codes.delete(0.0, "end")
        self.message.configure(text="")
        self.additional_cnt = 0
        self.window.geometry(
            f"{self.default_size[0]}x{self.default_size[1]+self.additional_cnt*self.additional_size}"
        )

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
                        row=4, column=0, columnspan=3, sticky="nsew", padx=8, pady=4
                    )
                    self.additional_cnt += 1
                    self.window.geometry(
                        f"{self.default_size[0]}x{self.default_size[1]+self.additional_cnt*self.additional_size}"
                    )
                else:
                    self.youtube_frame.grid_forget()

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
                    self.stack_overwrite.set(1)
                    self.stack_set_idx = 0
                    self.stack_frame.grid(
                        row=5, column=0, columnspan=3, sticky="nsew", padx=12, pady=4
                    )
                    self.additional_cnt += 1
                    self.window.geometry(
                        f"{self.default_size[0]}x{self.default_size[1]+self.additional_cnt*self.additional_size}"
                    )
                else:
                    self.stack_frame.grid_forget()
        except Exception as e:
            self.message.configure(text="에러 발생: 다운로드", foreground="red")
            print("Download", repr(e))
        finally:
            self.animation.cancel_animation()
            self.url.focus()

    def stack_images(self, is_running_func):
        self.animation.enable_animation()

        try:
            if self.stack_overwrite.get() == 1:
                self.stack_set_idx = 1
            else:
                self.stack_set_idx += 1

            start = int(self.stack_start.get().strip())
            end = int(self.stack_end.get().strip())
            exclude = [int(i) for i in self.stack_exclude.get().strip().split()]

            print(start, end, exclude)
            stack_cuts(
                self.stack_set_idx, self.images, start, end, exclude, self.config
            )

            if start < end:
                self.message.configure(
                    text=f"성공: 합치기 (stacked_{self.stack_set_idx})",
                    foreground="green",
                )
                self.window.after(3000, lambda: self.message.configure(text=""))
                self.stack_start.delete(0, "end")
                self.stack_end.delete(0, "end")
                self.stack_exclude.delete(0, "end")
            else:
                raise Exception("stack failure")

        except Exception as e:
            self.message.configure(
                text=f"에러 발생: 합치기 (stacked_{self.stack_set_idx})",
                foreground="red",
            )
            print("Stack images", repr(e))
        finally:
            self.animation.cancel_animation()
            self.url.focus()
