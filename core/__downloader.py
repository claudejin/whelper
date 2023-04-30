import os
import glob
import shutil
import requests
from bs4 import BeautifulSoup as bs


def open_and_save(imgurl, savepath):
    ext = imgurl.split(".")[-1]
    if len(ext) > 4:
        ext = "jpg"

    img_blob = requests.get(
        imgurl,
        stream=True,
        headers={
            "User-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36"
        },
    )
    if img_blob.status_code == 200:
        with open(f"{savepath}.{ext}", "wb") as f:
            shutil.copyfileobj(img_blob.raw, f)
    else:
        print("    Error: Image Couldn't be retrieved")


def get_image_list(url_string):
    res = requests.get(url_string, stream=True)
    if res.status_code != 200:
        return []

    # parsing soup object
    soup = bs(res.text, "html.parser")

    # get images under marketing div
    marketing_container = soup.find(class_="marketing")
    if not marketing_container:
        return []
    marketing_images = marketing_container.find_all("img")

    # exclude images under about_pdt div
    pdt_container = soup.find(class_="about_pdt")
    if pdt_container:
        pdt_images = pdt_container.find_all("img")
    else:
        pdt_images = []

    # final image list
    images = [img for img in marketing_images if img not in pdt_images]
    return images


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
        images = get_image_list(url_string)
        if len(images) > 0:
            i = 1
            for img in images:
                imgurl = img["src"].split("?")[0]
                print(f"    {i:02d}: {imgurl}")
                if imgurl[:2] == "//":
                    imgurl = f"https:{imgurl}"
                    print(f"      => Adding https: in the front")

                try:
                    open_and_save(imgurl, f"{config['save_directory']}/{i}")
                except requests.exceptions.SSLError:
                    print("      => Error: requests SSL, trying http instead")
                    imgurl = imgurl.replace("https://", "http://")
                    print(f"      => {i:02d}: {imgurl}")

                    open_and_save(imgurl, f"{config['save_directory']}/{i}")

                i += 1
            print(f"    DONE\n")
            return True
        else:
            print("    Error: Wrong product URL\n")
            return False
    except Exception as e:
        print(e)
