from os.path import abspath, join
from json import loads
import sys


def resolve_path(func):
    """
    Get absolute path to resource.
    Reference: https://stackoverflow.com/a/13790741
    """
    def wrapper(relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = abspath('.')
        return func(join(base_path, relative_path))
    return wrapper


@resolve_path
def load_data(data_file):
    """
    Return the contents of bible_info.json as a dictionary.
    """
    with open(data_file, 'r') as file:
        data = file.read()
    return loads(data)


if __name__ == "__main__":
    test = load_data('bible_info.json')
    print(test.get('Versions'))
