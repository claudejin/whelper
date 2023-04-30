from tkinter import PhotoImage, TclError, Label


class AnimatedGif(Label):
    master = None
    cancel_id = None

    def __init__(self, master, image_file_path):
        super(AnimatedGif, self).__init__(master)
        self.master = master

        # Read in all the frames of a multi-frame gif image.
        self._frames = []

        frame_num = 0  # Number of next frame to read.
        while True:
            try:
                frame = PhotoImage(
                    file=image_file_path, format="gif -index {}".format(frame_num)
                )
            except TclError:
                break
            self._frames.append(frame)
            frame_num += 1

        self.configure(image=self._frames[0])

    def update_label_image(self, ms_delay, frame_num):
        self.configure(image=self._frames[frame_num])
        frame_num = (frame_num + 1) % len(self._frames)
        self.cancel_id = self.master.after(
            ms_delay, self.update_label_image, ms_delay, frame_num
        )

    def enable_animation(self):
        if self.cancel_id is None:  # Animation not started?
            ms_delay = 1000 // len(self._frames)  # Show all frames in 1000 ms.
            self.cancel_id = self.master.after(
                ms_delay, self.update_label_image, ms_delay, 0
            )

    def cancel_animation(self):
        if self.cancel_id is not None:  # Animation started?
            self.master.after_cancel(self.cancel_id)
            self.cancel_id = None
