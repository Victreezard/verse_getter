from json import loads
from re import findall
from typing import Dict, Union
from urllib.parse import quote
from urllib.request import urlopen
import cfg


class Content():
    "A template class that takes it attributes from a dictionary."

    def __init__(self, dictionary: Dict[str, str]):
        for k, v in dictionary.items():
            setattr(self, k, v)

    def get_id(self, name: str) -> str:
        return getattr(self, name)

    def get_names(self, index: int = None) -> Union[list, int]:
        """
        If index is an integer then it will return the attribute with the corresponding index.
        If index is None it will return a list of all attribute names.
        """
        names = list(vars(self).keys())
        if index is None:
            return names

        try:
            return names[index]
        except Exception as e:
            print(e)


class Bible():
    """
    A class to attribute the contents of bible_data.json.
    Contains the members Version and Book.
    """

    def __init__(self, data_file: str = cfg.DATA_PATH):
        contents = self.load_data(data_file)
        self.Version = Content(contents.get('Versions'))
        self.Book = Content(contents.get('Books'))
        self.base_url = cfg.URL

    @staticmethod
    def load_data(data_file: str) -> Dict[str, str]:
        """
        Return the contents of a json file as a dictionary.
        """
        with open(data_file, 'r') as file:
            data = file.read()
        return loads(data)

    def _sanitize_verse(self, string: str) -> str:
        pattern = r'(?<=</small> ).+(?=<br>)'
        result = '\n'.join(findall(pattern, string))
        return result

    def get_verse(self, version: str, book: str, chapter:str, verse:str, *args: str) -> str:
        # Change cases for aesthetics
        bible_verse = f"{version.upper()}-{book.title()}/{chapter}:{verse}"

        if len(args) == 1:
            bible_verse += f'-{args[0]}'
        elif len(args) == 2:
            bible_verse += f'-{args[0]}:{args[1]}'

        url = quote(self.base_url + bible_verse, safe=cfg.SAFE)
        with urlopen(url) as response:
            passage = self._sanitize_verse(response.read().decode())
            if passage:
                # Remove forward slash and first dash for aesthetics
                bible_verse = bible_verse.replace('/', ' ').replace('-', ' ', 1)
                return bible_verse + '\n' + passage


if __name__ == "__main__":
    bible = Bible()
    verse = bible.get_verse('niv', 'john', '3', '16')
    print(verse)
