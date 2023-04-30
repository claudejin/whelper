import semver
from os import remove, makedirs
from shutil import rmtree, copyfileobj
from os.path import exists, expanduser, normpath, dirname
import requests
import pip


class InstallManager:
    def migrate_if_possible(self):
        home_path = normpath(expanduser("~"))

        info_py_path = f"{home_path}/info.py"
        if exists(info_py_path):
            remove(info_py_path)

        # whelper_py_path = f"{home_path}/whelper.pyw"
        # if exists(whelper_py_path):
        #     remove(whelper_py_path)

        pycache_path = f"{home_path}/__pycache__"
        if exists(pycache_path):
            rmtree(pycache_path)

    def check_new_version(self, current_version):
        vinfo = (
            "https://raw.githubusercontent.com/claudejin/whelper/main/updatelist.txt"
        )
        res = requests.get(vinfo, headers={"Cache-Control": "no-cache"})
        if res.status_code != 200:
            return False

        lines = res.text.splitlines()
        latest_version = lines[0]

        # Compare versions
        print(
            "Current version:",
            current_version,
            "Latest version:",
            latest_version,
        )
        if semver.compare(current_version, latest_version) >= 0:
            return False, []

        return True, lines

    def update(self, config, response):
        print(response)
        # Download updated files
        for filename in response[1:]:
            if filename[:3] == "pip":
                pip.main(["install", filename.split()[1]])
                continue

            new_file = (
                f"https://raw.githubusercontent.com/claudejin/whelper/main/{filename}"
            )
            res = requests.get(
                new_file,
                stream=True,
                headers={
                    "User-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
                    "Cache-Control": "no-cache",
                },
            )
            if res.status_code == 200:
                makedirs(normpath(dirname(filename)), exist_ok=True)
                if new_file.split(".")[-1] in ["py", "pyw", "yaml"]:
                    with open(f"{filename}", "w", encoding="utf8") as f:
                        f.write(res.text)
                else:
                    with open(f"{filename}", "wb") as f:
                        copyfileobj(res.raw, f)

        config["version"] = response[0]
        config.save()


if __name__ == "__main__":
    print("Wrong access")
