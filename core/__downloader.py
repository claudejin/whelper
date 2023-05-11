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
        image_urls = get_image_nodes(soup, [".marketing"], [".about_pdt"])
        if not image_urls:
            print("  Error: Wrong product URL\n")
            return []
        
        i = 1
        images = []
        for img_url in image_urls:
            print(f"    {i:02d}: {img_url}")

            try:
                images.append(download_image(img_url, f"{config['save_directory']}/{i}"))
            except requests.exceptions.SSLError:
                print("      => Error: requests SSL, trying http instead")
                img_url = img_url.replace("https://", "http://")
                print(f"      => {i:02d}: {img_url}")

                images.append(download_image(img_url, f"{config['save_directory']}/{i}"))

            i += 1
        print(f"  DONE\n")
        return [img for img in images if img]
            
    except Exception as e:
        print(e)
