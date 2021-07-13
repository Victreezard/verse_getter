from bible import Bible
from re import compile, I, M
import cfg
import sys
import PySimpleGUI as sg


class VerseGetter():
    def __init__(self, output_file=cfg.OUTPUT):
        self.WARNING = '**'
        self.output_file = output_file
        self.Bible = Bible()

    def write_output(self, content=''):
        """
        Overwrite the output_file with the given string.
        Writes empty by the default.
        """
        with open(self.output_file, 'w') as file:
            file.write(content)

    def _produce(self, verse_args):
        """
        Convenience function that gets and writes a verse to the output_file.
        """
        result_verse = self.Bible.get_verse(*verse_args)
        if not result_verse:
            raise(Exception('Verse not found'))
        result_verse = f'{verse_args[1]} {verse_args[2]}:{verse_args[3]}\n{result_verse}'
        self.write_output(result_verse)
        return result_verse

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

    def _compile_args(self):
        """
        Retrieve and return the verse, book, chapter and verse from the UI.
        """
        if not values[VERSION_COMBO]:
            raise(Exception('Please select a Version'))
        version = self.Bible.Version.get_code(values[VERSION_COMBO])

        if not values[BOOK_LB]:
            raise(Exception('Please select a Book'))
        book = values[BOOK_LB][0]

        if not values[CHVERSE_IN]:
            raise(Exception('Please enter a Chapter and Verse'))
        values[CHVERSE_IN] = values[CHVERSE_IN].strip()
        window.Element(CHVERSE_IN).update(
            value=values[CHVERSE_IN])
        chapter, verse = self._parse_chapterverse(values[CHVERSE_IN])
        return version, book, chapter, verse

    def extract(self, text):
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
        books = '\n'.join(self.Bible.Book.get_names())
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

    def validate(self, verse_list):
        invalid_verses = []
        for index, verse in enumerate(verse_list):
            # Split verse into args
            verse_args = verse.split(' ')
            # Combine books with leading numbers (e.g., 1 John)
            if verse_args[1].isdecimal():
                verse_args[1] += ' ' + verse_args.pop(2)
            # Validate, add to invalid list if invalid
            if not self.Bible.get_verse(*verse_args):
                invalid_verses.append(verse_list[index])
                verse_list[index] += self.WARNING
            sg.one_line_progress_meter('Validating verses', index + 1, len(verse_list))
        return invalid_verses, verse_list


if __name__ == "__main__":
    vg = VerseGetter()

    sg.theme('Black')
    sg.set_options(font='30')

    # First Column
    NEXT_B = '⮞'
    PREV_B = '⮜'
    GET_B = 'GET'
    LIST_B = 'List Verse'
    VERSION_COMBO = 'Version'
    BOOK_LB = 'Book'
    CHVERSE_IN = 'Chapter and Verse'
    GET_COL = sg.Col([
        [sg.Fr(
            VERSION_COMBO,
            [[sg.Combo(vg.Bible.Version.get_names(),
                       default_value=vg.Bible.Version.get_names()[0],
                       k=VERSION_COMBO)
              ]]
        )],
        [sg.Fr(
            BOOK_LB,
            [[sg.LB(sorted(vg.Bible.Book.get_names()),
                    size=(None, 20),
                    k=BOOK_LB)
              ]]
        )],
        [sg.Fr(
            CHVERSE_IN,
            [[
                sg.In(size=(10, None), k=CHVERSE_IN),
                sg.B(GET_B), sg.B(PREV_B),
                sg.B(NEXT_B), sg.B(LIST_B)
            ]]
        )]
    ])

    # Second Column
    MV_UP_B = '⮝'
    MV_DOWN_B = '⮟'
    SHOW_B = 'Show'
    REMOVE_B = 'Remove'
    EDIT_B = 'Edit'
    CLEAR_B = 'Clear List'
    EXTRACT_B = 'Extract Verses'
    VALIDATE_B = 'Validate Verses'
    VERSE_LB = 'Verse List'
    verse_list = []
    MV_COL = sg.Col(
        [
            [sg.B(MV_UP_B)],
            [sg.B(MV_DOWN_B)]
        ],
        vertical_alignment='center'
    )
    LIST_COL = sg.Col(
        [
            [sg.Fr(
                VERSE_LB,
                [
                    [sg.LB(verse_list, size=(None, 20),
                           k=VERSE_LB), MV_COL],
                    [sg.B(SHOW_B), sg.B(EDIT_B), sg.B(REMOVE_B)],
                    [sg.B(EXTRACT_B), sg.B(CLEAR_B)],
                    [sg.B(VALIDATE_B)]
                ]
            )]
        ],
        vertical_alignment='top'
    )

    # Output Row
    OUTPUT_T = 'DisplayVerse'
    OUTPUT_FR = sg.Fr(OUTPUT_T, [[sg.Text('', (70, 5), auto_size_text=True,
                                          justification='center', k=OUTPUT_T)]])

    layout = [[GET_COL, sg.VSep(), LIST_COL], [OUTPUT_FR]]
    window = sg.Window('Get that verse', layout, icon=cfg.ICON_PATH)

    while True:
        try:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                vg.write_output()
                break

            elif event in (GET_B, NEXT_B, PREV_B):
                verse_args = vg._compile_args()
                if event != GET_B:
                    verse_args = list(verse_args)
                    if event == NEXT_B:
                        verse_args[3] = str(int(verse_args[3]) + 1)
                    elif event == PREV_B:
                        verse_args[3] = str(int(verse_args[3]) - 1)
                    window.Element(CHVERSE_IN).update(
                        value=f'{verse_args[2]} {verse_args[3]}')

                result_verse = vg._produce(verse_args)
                window.Element(OUTPUT_T).update(value=result_verse)

            elif event == LIST_B:
                verse_list.append(' '.join(vg._compile_args()))
                window.Element(VERSE_LB).update(values=verse_list)

            elif event == SHOW_B and values[VERSE_LB]:
                verse_args = values[VERSE_LB][0].split(' ')
                # Concatenate if Book has a leading number (e.g., 1 John)
                if verse_args[1].isdecimal():
                    verse_args[1] += ' ' + verse_args.pop(2)

                result_verse = vg._produce(verse_args)

                window.Element(BOOK_LB).set_value([verse_args[1]])
                window.Element(CHVERSE_IN).update(
                    value=f'{verse_args[2]} {verse_args[3]}')
                window.Element(OUTPUT_T).update(value=result_verse)

            # Limitations:
            # 1. If there are similar verses it will always change the first one
            # 2. For now, it can't verify the validity of the new verse
            elif event == EDIT_B and values[VERSE_LB]:
                old_verse = values[VERSE_LB][0]
                new_verse = sg.popup_get_text(
                    f'Modify verse: {old_verse}',
                    default_text=old_verse,
                    no_titlebar=True)
                # Replace the old with the new
                if new_verse:
                    verse_list[verse_list.index(old_verse)] = new_verse
                    window.Element(VERSE_LB).update(values=verse_list)

            elif event == REMOVE_B and values[VERSE_LB]:
                verse_list.remove(values[VERSE_LB][0])
                window.Element(VERSE_LB).update(values=verse_list)

            elif event in (MV_UP_B, MV_DOWN_B) and values[VERSE_LB]:
                old_pos = verse_list.index(values[VERSE_LB][0])
                if event == MV_UP_B and old_pos > 0:
                    addend = -1
                elif event == MV_DOWN_B and old_pos < len(verse_list) - 1:
                    addend = 1
                else:
                    continue
                verse_to_move = verse_list.pop(old_pos)
                verse_list.insert(old_pos + addend, verse_to_move)
                window.Element(VERSE_LB).update(values=verse_list)
                window.Element(VERSE_LB).set_value(
                    verse_list[verse_list.index(verse_to_move)])

            elif event == CLEAR_B and verse_list:
                if sg.popup_ok_cancel('Delete ALL verses in the list?', no_titlebar=True) == 'OK':
                    verse_list.clear()
                    window.Element(VERSE_LB).update(values=verse_list)

            elif event == EXTRACT_B:
                text = sg.popup_get_text(
                    'Enter text containing bible verses', no_titlebar=True)
                if text:
                    verses = vg.extract(text)
                    # Include the currently selected Version then add the extracted verses to the list
                    verse_list.extend(
                        [f'{vg.Bible.Version.get_code(values[VERSION_COMBO])} {verse}' for verse in verses])
                    window.Element(VERSE_LB).update(values=verse_list)

            elif event == VALIDATE_B and verse_list:
                invalid_verses, verse_list = vg.validate(verse_list)
                if invalid_verses:
                    sg.popup_error('Invalid verses found!', '\n'.join(
                        invalid_verses), no_titlebar=True)
                    window.Element(VERSE_LB).update(values=verse_list)

        except Exception as e:
            vg.write_output()
            line_error = sys.exc_info()[2].tb_lineno
            sg.popup(f"Line {line_error}: {e}", text_color='Red', )

    window.close()
