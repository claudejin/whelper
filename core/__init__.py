from ._installer import InstallManager


def get_window():
    from ._window import MainWindow

    return MainWindow()
