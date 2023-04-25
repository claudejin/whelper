#!/usr/local/bin/python3

from core import Config, InstallManager, get_window

def main():
    config = Config()

    install_manager = InstallManager()
    install_manager.migrate_if_possible()
    
    res, response = install_manager.check_new_version(config["version"])
    if res:
        install_manager.update(config, response)

    main_window = get_window()
    main_window.run(config)

if __name__ == "__main__":
    main()