import PySimpleGUI as sg
import sys
from bible_api import get_verse
from json import loads
from os.path import abspath, join
from re import compile, I, M


class Bible():
    """
    A class to attribute the contents of bible_info.json.
    """

    def __init__(self, bible_info_file='bible_info.json'):
        bible_info = self._load_bible_info(bible_info_file)
        for k, v in bible_info.items():
            setattr(self, k, v)

    def _load_bible_info(self, bible_info_file):
        """
        Return the contents of bible_info.json as a dictionary.
        """
        with open(self._get_resource_path(bible_info_file), 'r') as file:
            bible_info = file.read()
        return loads(bible_info)

    def _get_resource_path(self, relative_path):
        """
        Get absolute path to resource.
        Source: https://stackoverflow.com/a/13790741
        """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = abspath('.')
        return join(base_path, relative_path)


class VerseGetter():
    WARNING = '**'

    def __init__(self, output_file='verse_output.txt'):
        self.output_file = output_file
        self.Bible = Bible()

    def write_output(self, content=''):
        """
        Overwrite the output_file with the given string.
        Writes empty by the default.
        """
        with open(self.output_file, 'w') as file:
            file.write(content)

    def _get_and_write_verse(self, verse_args):
        """
        Convenience function that gets and writes a verse to the output_file.
        """
        result_verse = get_verse(*verse_args)
        if not result_verse:
            raise(Exception('Verse not found'))
        self.write_output(
            f'{verse_args[1]} {verse_args[2]}:{verse_args[3]}\n{result_verse}')

    def _parse_chapterverse(self, text, fullmatch=True):
        """
        Extract and return the Chapter and Verse in a list from the given text.

        :param text: text to extract chapter and verse from
        :type message: (str)
        :param fullmatch: If True then text must only be two numbers with space in between
        else it will return the first match it finds :type fullmatch: (bool)
        :return: Chapter and Verse :rtype: list
        """
        pattern = compile(r'\d+ \d+')
        if fullmatch:
            if pattern.fullmatch(text):
                return text.split()
        else:
            text = pattern.findall(text)[0]
            if text:
                return text.split()

        raise(Exception('Incorrect format for Chapter and Verse'))

    def _get_verse_args(self):
        """
        Retrieve and return the verse, book, chapter and verse from the UI.
        """
        if not values[version_combo]:
            raise(Exception('Please select a Version'))
        version = self.Bible.Versions.get(values[version_combo])

        if not values[book_listbox]:
            raise(Exception('Please select a Book'))
        book = values[book_listbox][0]

        if not values[chapterverse_input]:
            raise(Exception('Please enter a Chapter and Verse'))
        values[chapterverse_input] = values[chapterverse_input].strip()
        window.Element(chapterverse_input).update(
            value=values[chapterverse_input])
        chapter, verse = self._parse_chapterverse(values[chapterverse_input])
        return version, book, chapter, verse

    def extract_verses(self, text):
        """
        Return a list of verses from a given text.
        """
        verse_pattern = compile(r'(([123] )?[\w.]+ \d+:\d+)', I)
        verses = verse_pattern.findall(text)
        # findall will return 3 groups per match. Get first groups, remove dots, replace colons.
        verses = [verse[0].replace('.', '').replace(':', ' ')
                  for verse in verses]
        # split up chapter and verse
        split_pattern = compile(r' (?=\d+ \d+)')
        results = [split_pattern.split(verse) for verse in verses]
        # join Bible books as one string to easily search for each book match
        books = '\n'.join(self.Bible.Books.keys())
        for index, result in enumerate(results):
            p = compile(f'^{result[0]}\w*', M)
            match = p.findall(books)
            # If a match is found join the whole book name and chapter verse
            # Else insert a Warning symbol before adding to the list
            if len(match) == 1:
                results[index] = f'{match[0]} {result[1]}'
            else:
                results[index] = f"{' '.join(result)} {self.WARNING}"
        return results


if __name__ == "__main__":
    vg = VerseGetter()

    sg.theme('Black')
    sg.set_options(font='30')

    next_button = '⮞'
    prev_button = '⮜'
    get_button = 'GET'
    list_verse_button = 'List Verse'
    version_combo = 'Version'
    book_listbox = 'Book'
    chapterverse_input = 'Chapter and Verse'
    get_col = sg.Col([
        [sg.Frame(
            version_combo,
            [[sg.Combo([key for key in vg.Bible.Versions],
                       default_value=list(vg.Bible.Versions.keys())[0],
                       k=version_combo)
              ]]
        )],
        [sg.Frame(
            book_listbox,
            [[sg.LB(sorted([book for book in vg.Bible.Books]),
                    size=(None, 20),
                    k=book_listbox)
              ]]
        )],
        [sg.Frame(
            chapterverse_input,
            [[
                sg.In(size=(10, None), k=chapterverse_input),
                sg.B(get_button), sg.B(prev_button),
                sg.B(next_button), sg.B(list_verse_button)
            ]]
        )]
    ])

    move_up_button = '⮝'
    move_down_button = '⮟'
    show_button = 'Show'
    remove_button = 'Remove'
    edit_button = 'Edit'
    clear_button = 'Clear List'
    extract_button = 'Extract Verses'
    validate_button = 'Validate Verses'
    verse_listbox = 'Verse List'
    verse_list = []
    move_col = sg.Col(
        [
            [sg.B(move_up_button)],
            [sg.B(move_down_button)]
        ],
        vertical_alignment='center'
    )
    list_col = sg.Col(
        [
            [sg.Frame(
                verse_listbox,
                [
                    [sg.LB(verse_list, size=(None, 20),
                           k=verse_listbox), move_col],
                    [sg.B(show_button), sg.B(edit_button), sg.B(remove_button)],
                    [sg.B(extract_button), sg.B(clear_button)],
                    [sg.B(validate_button)]
                ]
            )]
        ],
        vertical_alignment='top'
    )

    layout = [[get_col, sg.VSep(), list_col]]
    window = sg.Window('Get that verse', layout)

    while True:
        try:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                vg.write_output()
                break

            elif event in (get_button, next_button, prev_button):
                verse_args = vg._get_verse_args()
                if event != get_button:
                    verse_args = list(verse_args)
                    if event == next_button:
                        verse_args[3] = str(int(verse_args[3]) + 1)
                    elif event == prev_button:
                        verse_args[3] = str(int(verse_args[3]) - 1)
                    window.Element(chapterverse_input).Update(
                        value=f'{verse_args[2]} {verse_args[3]}')

                vg._get_and_write_verse(verse_args)

            elif event == list_verse_button:
                verse_list.append(' '.join(vg._get_verse_args()))
                window.Element(verse_listbox).Update(values=verse_list)

            elif event == show_button and values[verse_listbox]:
                verse_args = values[verse_listbox][0].split(' ')
                # Concatenate if Book has a leading number (e.g., 1 John)
                if verse_args[1].isdecimal():
                    verse_args[1] += ' ' + verse_args.pop(2)

                vg._get_and_write_verse(verse_args)

                window.Element(book_listbox).set_value([verse_args[1]])
                window.Element(chapterverse_input).Update(
                    value=f'{verse_args[2]} {verse_args[3]}')

            # Limitations:
            # 1. If there are similar verses it will always change the first one
            # 2. For now, it can't verify the validity of the new verse
            elif event == edit_button and values[verse_listbox]:
                old_verse = values[verse_listbox][0]
                new_verse = sg.popup_get_text(
                    f'Modify verse: {old_verse}',
                    default_text=old_verse,
                    no_titlebar=True)
                # Replace the old with the new
                if new_verse:
                    verse_list[verse_list.index(old_verse)] = new_verse
                    window.Element(verse_listbox).Update(values=verse_list)

            elif event == remove_button and values[verse_listbox]:
                verse_list.remove(values[verse_listbox][0])
                window.Element(verse_listbox).Update(values=verse_list)

            elif event in (move_up_button, move_down_button) and values[verse_listbox]:
                old_pos = verse_list.index(values[verse_listbox][0])
                if event == move_up_button and old_pos > 0:
                    addend = -1
                elif event == move_down_button and old_pos < len(verse_list) - 1:
                    addend = 1
                else:
                    continue
                verse_to_move = verse_list.pop(old_pos)
                verse_list.insert(old_pos + addend, verse_to_move)
                window.Element(verse_listbox).update(values=verse_list)
                window.Element(verse_listbox).set_value(
                    verse_list[verse_list.index(verse_to_move)])

            elif event == clear_button and verse_list:
                if sg.popup_ok_cancel('Delete ALL verses in the list?', no_titlebar=True) == 'OK':
                    verse_list.clear()
                    window.Element(verse_listbox).Update(values=verse_list)

            elif event == extract_button:
                text = sg.popup_get_text(
                    'Enter text containing bible verses', no_titlebar=True)
                if text:
                    verses = vg.extract_verses(text)
                    # Include the currently selected Version then add the extracted verses to the list
                    verse_list.extend(
                        [f'{vg.Bible.Versions.get(values[version_combo])} {verse}' for verse in verses])
                    window.Element(verse_listbox).update(values=verse_list)

            elif event == validate_button and verse_list:
                invalid_verses = []
                for index, verse in enumerate(verse_list):
                    # Split verse into args
                    verse_args = verse.split(' ')
                    # Combine books with leading numbers (e.g., 1 John)
                    if verse_args[1].isdecimal():
                        verse_args[1] += ' ' + verse_args.pop(2)
                    # Validate, add to invalid list if invalid
                    if not get_verse(*verse_args):
                        invalid_verses.append(verse_list[index])
                        verse_list[index] += vg.WARNING
                    sg.one_line_progress_meter(
                        'Validating verses', index + 1, len(verse_list))
                if invalid_verses:
                    sg.popup_error('Invalid verses found!', '\n'.join(
                        invalid_verses), no_titlebar=True)
                    window.Element(verse_listbox).update(values=verse_list)

        except Exception as e:
            vg.write_output()
            line_error = sys.exc_info()[2].tb_lineno
            sg.popup(f"Line {line_error}: {e}", text_color='Red', )

    window.close()
