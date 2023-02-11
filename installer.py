#!/usr/local/bin/python3

import subprocess as sp
import os
import platform

config_path = os.path.expanduser("%USERPROFILE%/wconfig.txt" if platform.system() == "Windows" else "~/wconfig.txt")

if __name__ == "__main__":
    sp.getoutput("pip3 install BeautifulSoup4 requests pyyaml")
    sp.getoutput(f"cp wconfig.txt {config_path}")