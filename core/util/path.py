import pathlib


def get_files_recursive(basepath, regex="*"):
    return [p for p in pathlib.Path(basepath).rglob(regex)]


def clear_pycache():
    # https://stackoverflow.com/a/41386937
    [p.unlink() for p in get_files_recursive(".", "*.py[co]")]
    [p.rmdir() for p in get_files_recursive(".", "__pycache__")]


def get_project_files():
    core = [str(p) for p in get_files_recursive("./core", "*.py")]
    resources = [str(p) for p in get_files_recursive("./resources")]
    return sorted(core + resources)


def clear_old_py():
    [p.unlink() for p in get_files_recursive("./core", "*.py")]
    [p.rmdir() for p in get_files_recursive("./core")]
