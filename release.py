RELEASE_VERSION = "0.7.3"
UPDATE_FILELIST = ["whelper.pyw", "info.py"]

if __name__ == "__main__":
    with open("updatelist.txt", "w") as f:
        f.write("\n".join([RELEASE_VERSION] + UPDATE_FILELIST))

    with open("info.py", "w") as f:
        f.write(f"version = \"{RELEASE_VERSION}\"")