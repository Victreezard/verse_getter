from os.path import abspath, join
from typing import Tuple
import sys


def resolve_path(relative_path: str) -> str:
    """
    Returns the absolute path to a resource.
    Reference: https://stackoverflow.com/a/13790741
    """
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath('.')
    return join(base_path, relative_path)


URL = 'https://ibibles.net/quote.php?'
RESOURCES = 'resources'  # directory name
BIBLE_DATA = 'bible_data.json'  # contains bible versions and books
ICON = 'tlag.ico'
OUTPUT = 'verse_output.txt'
SAFE = '/:?'

DATA_PATH = resolve_path(join(RESOURCES, BIBLE_DATA))
ICON_PATH = resolve_path(join(RESOURCES, ICON))

# Type aliases
Verse_Args = Tuple[str, str, str, str]
