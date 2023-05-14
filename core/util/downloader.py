import os
import glob
import requests
from bs4 import BeautifulSoup as bs
from io import BytesIO
from PIL import Image


def detect_youtube(soup: bs):
    movies = soup.find_all("iframe")
    youtube_html = []
    if movies:
        for m in movies:
            if not m.has_attr("src"):
                continue
            if "youtube" not in m["src"]:
                continue
            youtube_html.append(str(m.parent).replace("\n", ""))

    return youtube_html


def download_images(soup: bs, config):
    try:
        __remove_previous_images(config)

        # Download
        image_urls = __get_image_nodes(soup, [".marketing"], [".about_pdt"])
        if not image_urls:
            print("  Error: Wrong product URL\n")
            return []

        i = 1
        images = []
        for img_url in image_urls:
            print(f"    {i:02d}: {img_url}")

            try:
                images.append(
                    __download_image(img_url, f"{config['save_directory']}/{i}")
                )
            except requests.exceptions.SSLError:
                print("      => Error: requests SSL, trying http instead")
                img_url = img_url.replace("https://", "http://")
                print(f"      => {i:02d}: {img_url}")

                images.append(
                    __download_image(img_url, f"{config['save_directory']}/{i}")
                )

            i += 1
        print(f"  DONE\n")
        return [img for img in images if img]

    except Exception as e:
        print(e)

    return []


def __remove_previous_images(config):
    # Remove previous images
    if config["delete_previous_images"]:
        for i in range(config["delete_previous_items"] + 1):
            for e in config["extensions"]:
                for p in glob.glob(f"{config['save_directory']}/{i}.{e}"):
                    os.remove(p)


def __get_image_nodes(soup: bs, include_filters=[], exclude_filters=[]):
    def apply_filter(soup, filters):
        nodes = []
        for filter in filters:
            if filter[0] == ".":
                container = soup.find(class_=filter[1:])
            elif filter[0] == "#":
                container = soup.find(id=filter[1:])
            else:
                container = soup.find(filter)

            if not container:
                continue

            nodes += container.find_all("img")
        return nodes

    # parsing soup object

    included_images = apply_filter(soup, include_filters)
    excluded_images = apply_filter(soup, exclude_filters)

    # final image list
    images = [img for img in included_images if img not in excluded_images]
    img_urls = []
    for img in images:
        img_url = img["src"].split("?")[0]
        if img_url[:2] == "//":
            img_url = f"https:{img_url}"
            print(f"      => Adding https: in the front")
        img_urls.append(img_url)

    return img_urls


def __download_image(url, savepath):
    ext = url.split(".")[-1]
    if len(ext) > 4:
        ext = "jpg"

    img_blob = requests.get(
        url,
        stream=True,
        headers={
            "User-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36"
        },
    )

    if img_blob.status_code != 200:
        print("    Error: Image Couldn't be retrieved")
        return None

    img = Image.open(BytesIO(img_blob.content))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(f"{savepath}.jpg")

    return img
