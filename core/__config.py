import yaml
from sys import argv
from os import remove, makedirs
from os.path import exists, expanduser, normpath, dirname


class Config:
    __config_path = normpath(dirname(argv[0])) + "/resources/config.yaml"
    __config_data = None

    def __init__(self):
        self.__config_data = self.__load_yaml(self.__config_path)
        self.__migrate_if_possible()

        # Revise them
        self.__config_data["save_directory"] = normpath(
            expanduser(self.__config_data["save_directory"])
        )
        self.__config_data["resources"] = f"{normpath(dirname(argv[0]))}/resources/"
        makedirs(self.__config_data["save_directory"], exist_ok=True)
        self.save()

    def __getitem__(self, key):
        return self.__config_data[key]

    def __setitem__(self, key, val):
        self.__config_data[key] = val

    def __load_yaml(self, filepath):
        with open(filepath, "r", encoding="utf8") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def save(self):
        if not self.__config_data:
            return

        with open(self.__config_path, "w", encoding="utf8") as f:
            yaml.safe_dump(self.__config_data, f)

    def __migrate_if_possible(self):
        home_path = normpath(expanduser("~"))
        old_config_path = f"{home_path}/wconfig.txt"

        if not exists(old_config_path):
            return

        old_config_data = self.__load_yaml(old_config_path)
        remove(old_config_path)

        # Load previous configurations
        for key, val in old_config_data.items():
            self.__config_data[key] = val

        print("Config migrated")
