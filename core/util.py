import shutil
import requests
from bs4 import BeautifulSoup as bs


def get_image_nodes(url, include_filters=[], exclude_filters=[]):
    res = requests.get(url, stream=True)
    if res.status_code != 200:
        return []

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
    soup = bs(res.text, "html.parser")
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


def download_image(url, savepath):
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
        return False

    with open(f"{savepath}.{ext}", "wb") as f:
        shutil.copyfileobj(img_blob.raw, f)

    return True
