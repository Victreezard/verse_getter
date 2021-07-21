from json import loads
from re import findall
from urllib.request import urlopen
import cfg


class Content():
    """
    A template class that takes it attributes from a dictionary.
    """

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)

    def get_code(self, name):
        return getattr(self, name)

    def get_names(self):
        return [name for name in vars(self).keys()]


class Bible():
    """
    A class to attribute the contents of bible_data.json.
    Contains the members Version and Book.
    """

    def __init__(self, data_file=cfg.DATA_PATH):
        contents = self.load_data(data_file)
        self.Version = Content(contents.get('Versions'))
        self.Book = Content(contents.get('Books'))

    @staticmethod
    def load_data(data_file):
        """
        Return the contents of a json file as a dictionary.
        """
        with open(data_file, 'r') as file:
            data = file.read()
        return loads(data)

    def _sanitize_verse(self, string):
        pattern = r'(?<=/small> ).+(?= <)'

        result = '\n'.join([verse for verse in findall(pattern, string)])
        return result

    def get_verse(self, version, book, chapter, verse, chapter_end=None, verse_end=None):
        base_url = 'https://ibibles.net/quote.php?'
        # Replace spaces in Book names for URL encoding thing
        url = f"{base_url}{version}-{book.replace(' ', '%20')}/{chapter}:{verse}"

        if chapter_end and verse_end:
            url += f'-{chapter_end}:{verse_end}'
        elif verse_end:
            url += f'-{verse_end}'

        result = urlopen(url).read().decode('utf-8')
        return self._sanitize_verse(result)


if __name__ == "__main__":
    bible = Bible()
    verse = bible.get_verse('niv', '1 john', '1', '1', verse_end='3')
    print('\n', verse)
