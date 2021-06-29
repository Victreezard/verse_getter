import PySimpleGUI as sg
import sys
from bible_api import get_verse
from json import loads
from os.path import abspath, join
from re import fullmatch, findall


bible_info_file = 'bible_info.json'
verse_output_file = 'verse_output.txt'


def _get_resource_path(relative_path):
    """ Get absolute path to resource
    Source: https://stackoverflow.com/a/13790741 """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath('.')

    return join(base_path, relative_path)


def _parse_chapterverse(label):
    pattern = {'one_verse': r'^\d+ \d+$',
               'one_chapter_multi_verse': r'^\d+ \d+-\d+$',
               'multi_chapter_multi_verse': r'^\d+ \d+-\d+ \d+$',
               'numbers': r'\d+'}

    result = findall(pattern['numbers'], label)
    if fullmatch(pattern['one_verse'], label):
        chapter, verse = result
        return chapter, verse, '', ''
    elif fullmatch(pattern['one_chapter_multi_verse'], label):
        chapter, verse, verse_end = result
        if verse >= verse_end:
            raise(Exception('Error in Verse Numbering'))
        return chapter, verse, '', verse_end
    elif fullmatch(pattern['multi_chapter_multi_verse'], label):
        chapter, verse, chapter_end, verse_end = result
        if chapter >= chapter_end:
            raise(Exception('Error in Chapter Numbering'))
        return chapter, verse, chapter_end, verse_end
    else:
        raise(Exception('Error in Chapter and/or Verse content'))


def _get_verse_args():
    if not values[version_combo]:
        raise(Exception('Please select Version'))
    version = bible_info['Versions'][values[version_combo]]

    if not values[book_listbox]:
        raise(Exception('Please select Book'))
    book = values[book_listbox][0]

    if not values[chapterverse_input]:
        raise(Exception('Please enter Chapter and Verse'))
    values[chapterverse_input] = values[chapterverse_input].strip()
    window.Element(chapterverse_input).update(value=values[chapterverse_input])
    chapter, verse, chapter_end, verse_end = _parse_chapterverse(
        values[chapterverse_input])
    return version, book, chapter, verse, chapter_end, verse_end


def _write_verse(content):
    with open(verse_output_file, 'w') as file:
        if not content:
            file.write('')
        else:
            file.write(content)


with open(_get_resource_path(bible_info_file), 'r') as file:
    bible_info = file.read()
bible_info = loads(bible_info)

sg.theme('Black')
sg.set_options(font='30')

next_button = '⮞'
prev_button = '⮜'
move_up_button = '⮝'
move_down_button = '⮟'
get_button = 'GET'
list_verse_button = 'List Verse'
version_combo = 'Version'
book_listbox = 'Book'
chapterverse_input = 'Chapter and Verse'
get_col = sg.Col([
    [sg.Frame(version_combo, [
              [sg.Combo([key for key in bible_info['Versions']],
                        default_value=list(bible_info['Versions'].keys())[0],
                        k=version_combo)]])],
    [sg.Frame(book_listbox, [[sg.LB(sorted(
        [book for book in bible_info['Books']]), size=(None, 20), k=book_listbox)]])],
    [sg.Frame(chapterverse_input, [[sg.In(size=(10, None), k=chapterverse_input), sg.B(
        get_button), sg.B(prev_button), sg.B(next_button), sg.B(list_verse_button)]])]
])

show_button = 'Show Verse'
remove_button = 'Remove Verse'
verse_listbox = 'Verse List'
verse_list = []
move_col = sg.Col(
    [[sg.B(move_up_button)], [sg.B(move_down_button)]],
    vertical_alignment='center'
)
list_col = sg.Col([
    [sg.Frame(
        verse_listbox,
        [
            [sg.LB(verse_list, size=(None, 20), k=verse_listbox), move_col],
            [sg.B(show_button), sg.B(remove_button)]
        ]
    )]
], vertical_alignment='top')

layout = [[get_col, sg.VSep(), list_col]]

window = sg.Window('Get that verse', layout)

while True:
    try:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            _write_verse('')
            break

        elif event == get_button or event == next_button or event == prev_button:
            verse_args = _get_verse_args()
            if event != get_button:
                verse_args = list(verse_args)
                if event == next_button:
                    verse_args[3] = str(int(verse_args[3]) + 1)
                elif event == prev_button:
                    verse_args[3] = str(int(verse_args[3]) - 1)
                window.Element(chapterverse_input).Update(
                    value=f'{verse_args[2]} {verse_args[3]}')

            result_verse = get_verse(*verse_args)
            if not result_verse:
                raise(Exception('Bible Verse not found'))
            _write_verse(
                f'{verse_args[1]} {verse_args[2]}:{verse_args[3]}\n{result_verse}')

        elif event == list_verse_button:
            verse_list.append(' '.join(_get_verse_args()))
            window.Element(verse_listbox).Update(values=verse_list)

        elif event == show_button and values[verse_listbox]:
            verse_args = values[verse_listbox][0].split(' ')
            # Concatenate if Book has a leading number (e.g., 1 John)
            if verse_args[1].isdecimal():
                verse_args[1] += ' ' + verse_args.pop(2)

            result_verse = get_verse(*verse_args)
            if not result_verse:
                raise(Exception('Bible Verse not found'))
            _write_verse(
                f'{verse_args[1]} {verse_args[2]}:{verse_args[3]}\n{result_verse}')

            window.Element(book_listbox).set_value([verse_args[1]])
            window.Element(chapterverse_input).Update(
                value=f'{verse_args[2]} {verse_args[3]}')

        elif event == remove_button and values[verse_listbox]:
            verse_list.remove(values[verse_listbox][0])
            window.Element(verse_listbox).Update(values=verse_list)

        elif (event == move_up_button or event == move_down_button) and values[verse_listbox]:
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
            window.Element(verse_listbox).set_value(verse_list[verse_list.index(verse_to_move)])

    except Exception as e:
        _write_verse('')
        line_error = sys.exc_info()[2].tb_lineno
        sg.popup(f"Line {line_error}: {e}", text_color='Red', )

window.close()
