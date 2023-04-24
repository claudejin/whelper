import yaml
import semver
from sys import argv
from os import remove
from shutil import rmtree
from os.path import exists, expanduser, normpath, dirname
import requests


class InstallManager:
    config_path = normpath(dirname(argv[0])) + "/resources/config.yaml"
    config_data = None

    def check_new_version(self):
        if not self.config_data:
            with open(self.config_path, "r", encoding="utf8") as f:
                self.config_data = yaml.load(f, Loader=yaml.SafeLoader)

        vinfo = (
            "https://raw.githubusercontent.com/claudejin/whelper/main/updatelist.txt"
        )
        f = requests.get(vinfo, headers={"Cache-Control": "no-cache"})
        lines = f.text.splitlines()
        latest_version = lines[0]

        print(self.config_data["version"], latest_version)
        if semver.compare(self.config_data["version"], latest_version) >= 0:
            return False

        return True

    def migrate(self):
        home_path = normpath(expanduser("~"))
        old_config_path = f"{home_path}/wconfig.txt"

        if exists(old_config_path):
            with open(old_config_path, "r", encoding="utf8") as f:
                self.config_data = yaml.load(f, Loader=yaml.SafeLoader)
                self.config_data["version"] = "0.7.8"
            remove(old_config_path)

            info_py_path = f"{home_path}/info.py"
            if exists(info_py_path):
                remove(info_py_path)

            whelper_py_path = f"{home_path}/whelper.pyw"
            if exists(whelper_py_path):
                remove(whelper_py_path)

            pycache_path = f"{home_path}/__pycache__"
            if exists(pycache_path):
                rmtree(pycache_path)

            with open(self.config_path, "w", encoding="utf8") as f:
                yaml.safe_dump(self.config_data, f)

    def update(self):
        pass


if __name__ == "__main__":
    print("Wrong access")
