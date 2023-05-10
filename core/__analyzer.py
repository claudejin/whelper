import numpy as np
from PIL import Image
from os.path import exists

def count_image_cuts(filepath):
    img = np.array(Image.open(filepath))
    img_height, img_width, _ = img.shape

    def is_blank_line(line, color = None):
        if color is None:
            color = line[0, :]
        return np.all(np.all(line == color, axis=-1))

    def find_next_blank(img, start_from):
        h, _, _ = img.shape

        cur_row = start_from
        while cur_row < h:
            if is_blank_line(img[cur_row]):
                break

            cur_row += 1
        
        return cur_row
    
    def find_blank_height(img, start_from):
        h, _, _ = img.shape
        color = img[start_from, 0, :]

        cur_row = start_from
        while cur_row < h:
            if not is_blank_line(img[cur_row], color):
                break

            cur_row += 1
        
        return (cur_row - start_from)
    
    lines = []
    cur_row = next_blank_start_from = cur_blank_start_from = cur_row = find_next_blank(img, 0)
    while cur_row < img_height:
        cur_row += find_blank_height(img, cur_blank_start_from)

        while True:
            next_blank_start_from = find_next_blank(img, cur_row)
            if next_blank_start_from >= img_height or (next_blank_start_from - cur_row) >= (img_width/2):
                break
            cur_row += find_blank_height(img, next_blank_start_from)
            
        # print(f"Blank {len(lines)+1}: {cur_blank_start_from} ~ {cur_row}")
        lines.append((cur_blank_start_from, cur_row))
        cur_blank_start_from = cur_row = next_blank_start_from
    
    if lines and lines[0][0] == 0:
        lines = lines[1:]
    if lines and lines[-1][1] == img_height:
        lines = lines[:-1]

    print(f"{filepath}: {len(lines)+1} cuts")

def stack_cuts(start, end, exclude = []):
    stacked = 0
    to_stack = []

    def make_stack(images, i):
        out = Image.fromarray(np.vstack(images))
        out.save(f"stacked_{i}.jpg")

    for i in range(start, end+1):
        if i in exclude:
            continue

        if len(to_stack) < 9:
            if not exists(f"{i}.jpg"):
                break
            
            img = Image.open(f"{i}.jpg")
            if len(to_stack) > 0:
                sw, sh = img.size
                h, w, c = to_stack[0].shape
                img = img.resize((w, int(sh * w/sw)))
            a = np.array(img)
            to_stack.append(a)
            print(i, a.shape)
            h, w, c = to_stack[0].shape
            white_bar = np.ones((200, w, c), dtype=np.uint8)*255
            to_stack.append(white_bar)
        
        if len(to_stack) == 10:
            stacked += 1
            make_stack(to_stack, stacked)
            to_stack = []

    if len(to_stack) > 0:
        make_stack(to_stack, stacked+1)

if __name__ == "__main__":
    # for i in range(1, 16):
    #     count_image_cuts(f"/Users/claude/Desktop/wconcept/{i}.jpg")
    # stack_cuts(3, 36)
    pass