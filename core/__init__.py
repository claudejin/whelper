from .__installer import InstallManager
from .__config import Config


def get_window():
    from .__window import MainWindow

    return MainWindow()
