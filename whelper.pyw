#!/usr/local/bin/python3

import core
from core import InstallManager

def main():
    install_manager = InstallManager()
    if install_manager.check_new_version():
        install_manager.update()

    main_window = core.get_window()
    main_window.run()

if __name__ == "__main__":
    main()