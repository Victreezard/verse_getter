from re import findall
from urllib.request import urlopen


def _sanitize_verse(string):
    pattern = r'(?<=>).+(?= <)'
    replace_pattern = '</small>'

    result = [verse.replace(replace_pattern, '')
              for verse in findall(pattern, string)]
    return '\n'.join(result)


def get_verse(version, book, chapter, verse, chapter_end=None, verse_end=None):
    base_url = 'https://ibibles.net/quote.php?'
    url = f'{base_url}{version}-{book}/{chapter}:{verse}'

    if chapter_end and verse_end:
        url += f'-{chapter_end}:{verse_end}'
    elif verse_end:
        url += f'-{verse_end}'

    result = urlopen(url).read().decode('utf-8')
    return _sanitize_verse(result)


if __name__ == "__main__":
    verse = get_verse('niv', 'john', '1', '1', verse_end='3')
    print('\n', verse)
