from os.path import abspath, join
import sys


def resolve_path(relative_path):
    """
    Get absolute path to resource.
    Reference: https://stackoverflow.com/a/13790741
    """
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath('.')
    return join(base_path, relative_path)


RESOURCES = 'resources'  # directory name
BIBLE_DATA = 'bible_data.json'  # contains bible versions and books
ICON = 'tlag.ico'
OUTPUT = 'verse_output.txt'

DATA_PATH = resolve_path(join(RESOURCES, BIBLE_DATA))
ICON_PATH = resolve_path(join(RESOURCES, ICON))
