import numpy as np
from PIL import Image
from os.path import exists


def stack_cuts(stack_set_idx, images, start, end, exclude, config):
    stacked = 0
    to_stack = []

    def make_stack(images, i):
        out = Image.fromarray(np.vstack(images))

        filepath = f"{config['save_directory']}/stacked_{stack_set_idx}_{i}.jpg"
        out.save(filepath)
        print("saved:", filepath)

    for i in range(start, end + 1):
        if i in exclude:
            continue

        if len(to_stack) < 9:
            filepath = f"{config['save_directory']}/{i}.jpg"
            if not exists(filepath):
                continue

            img = Image.open(filepath)
            if len(to_stack) > 0:
                sw, sh = img.size
                h, w, c = to_stack[0].shape
                img = img.resize((w, int(sh * w / sw)))
            a = np.array(img)
            to_stack.append(a)
            print(i, a.shape)
            h, w, c = to_stack[0].shape
            white_bar = np.ones((200, w, c), dtype=np.uint8) * 255
            to_stack.append(white_bar)

        if len(to_stack) == 10:
            stacked += 1
            make_stack(to_stack, stacked)
            to_stack = []

    if len(to_stack) > 0:
        make_stack(to_stack, stacked + 1)
