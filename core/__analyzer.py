import numpy as np
from PIL import Image

def count_image_cuts(filepath):
    img = np.array(Image.open(filepath))
    h, w, _ = img.shape

    last_line_start = 0
    last_color = img[0, 0, :]
    lines = []

    for idx, line in zip(range(len(img)), img):
        if idx == last_line_start:
            last_color = line[0]
        
        is_line = np.all(np.all(line == last_color, axis=-1))

        if not is_line:
            if last_line_start > 0 and (idx - last_line_start) > 50:
                # print(f"Line: height {idx-last_line_start} ({last_line_start} ~ {idx-1})")
                lines.append((last_line_start, idx))
            last_line_start = idx+1
    
    print(f"{filepath}: {len(lines)+1} cuts")

if __name__ == "__main__":
    for i in range(1, 16):
        count_image_cuts(f"C:/Users/2018409/Desktop/wconcept/{i}.jpg")