#!/usr/local/bin/python3

from core.util.config import Config
from core.controller.installer import InstallManager
from core.view import get_main_window
from sys import argv
from os.path import dirname
from os import name as platform_name

def main():
    try:
        if platform_name == "nt":
            import ctypes
            myappid = u'minbeau.tools.whelper' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        print(e)
    finally:
        pass

    config = Config()
    config["pwd"] = dirname(argv[0])

    install_manager = InstallManager()
    install_manager.migrate_if_possible()
    
    res, response = install_manager.check_new_version(config["version"])
    if res:
        install_manager.run(config, response)

    main_window = get_main_window()
    main_window.run(config)

if __name__ == "__main__":
    #main()
    from core.util.path import clear_pycache
    clear_pycache()