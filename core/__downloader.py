import os
import glob
import shutil
import requests
from bs4 import BeautifulSoup as bs
from .util import get_image_nodes, download_image


def remove_previous_images(config):
    # Remove previous images
    if config["delete_previous_images"]:
        for i in range(config["delete_previous_items"] + 1):
            for e in config["extensions"]:
                for p in glob.glob(f"{config['save_directory']}/{i}.{e}"):
                    os.remove(p)


def download_images(url_string, config):
    try:
        remove_previous_images(config)

        url_string = url_string.strip()
        if not url_string:
            print("## Invalid url")
            return False

        print(f"## DOWNLOAD from: {url_string}")

        # Download
        images = get_image_nodes(url_string, [".marketing"], [".about_pdt"])
        if len(images) > 0:
            i = 1
            for imgurl in images:
                try:
                    download_image(imgurl, f"{config['save_directory']}/{i}")
                except requests.exceptions.SSLError:
                    print("      => Error: requests SSL, trying http instead")
                    imgurl = imgurl.replace("https://", "http://")
                    print(f"      => {i:02d}: {imgurl}")

                    download_image(imgurl, f"{config['save_directory']}/{i}")

                i += 1
            print(f"    DONE\n")
            return True
        else:
            print("    Error: Wrong product URL\n")
            return False
    except Exception as e:
        print(e)
