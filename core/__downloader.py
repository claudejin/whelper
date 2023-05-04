import os
import glob
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


def download_images(soup: bs, config):
    try:
        remove_previous_images(config)

        # Download
        images = get_image_nodes(soup, [".marketing"], [".about_pdt"])
        if len(images) > 0:
            i = 1
            for imgurl in images:
                print(f"    {i:02d}: {imgurl}")

                try:
                    download_image(imgurl, f"{config['save_directory']}/{i}")
                except requests.exceptions.SSLError:
                    print("      => Error: requests SSL, trying http instead")
                    imgurl = imgurl.replace("https://", "http://")
                    print(f"      => {i:02d}: {imgurl}")

                    download_image(imgurl, f"{config['save_directory']}/{i}")

                i += 1
            print(f"  DONE\n")
            return True
        else:
            print("  Error: Wrong product URL\n")
            return False
    except Exception as e:
        print(e)
