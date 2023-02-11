#!/usr/local/bin/python3

import subprocess as sp

if __name__ == "__main__":
    sp.getoutput("pyinstaller -w -F whelper.pyw")
    sp.getoutput("cp -r dist/whelper.app build/")
    sp.getoutput("cp wconfig.txt build/")
    sp.getoutput("rm -r build/whelper")
    sp.getoutput("rm -r dist")
    sp.getoutput("rm whelper.spec")