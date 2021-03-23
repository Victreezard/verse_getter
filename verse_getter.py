import PySimpleGUI as sg
import os
from bible_api import get_verse
from json import loads
from re import fullmatch, findall
from sys import exc_info


current_dir = os.path.dirname(__file__)
bible_info_filename = 'bible_info.json'
display_verse_rel_path = 'text/display_verse.txt'
display_verse_full_path = os.path.normpath(os.path.join(current_dir, os.pardir, os.pardir,
                                                        display_verse_rel_path))

with open(os.path.join(current_dir, bible_info_filename), 'r') as file:
    bible_info = file.read()
bible_info = loads(bible_info)


def _group_radio(dict, group_id, group_size, width=10, height=10):
    radio_list = []
    keys = list(sorted(dict.keys()))
    total_item_counter = 0
    sublist_counter = 0

    while total_item_counter < len(keys):
        sublist_item_counter = 0
        radio_list.append([])
        while sublist_item_counter < group_size and total_item_counter < len(keys):
            radio_list[sublist_counter].append(sg.Radio(keys[total_item_counter],
                                                        group_id, k=keys[total_item_counter], size=(width, height)))
            total_item_counter += 1
            sublist_item_counter += 1
        sublist_counter += 1

    return radio_list


def _parse_chapterverse(label):
    pattern = {'one_verse': r'^\d+:\d+$',
               'one_chapter_multi_verse': r'^\d+:\d+-\d+$',
               'multi_chapter_multi_verse': r'^\d+:\d+-\d+:\d+$',
               'numbers': r'\d+'}

    result = findall(pattern['numbers'], label)
    if fullmatch(pattern['one_verse'], label):
        chapter, verse = result
        return chapter, verse, None, None
    elif fullmatch(pattern['one_chapter_multi_verse'], label):
        chapter, verse, verse_end = result
        if verse >= verse_end:
            raise(Exception('Error in Verse Numbering'))
        return chapter, verse, None, verse_end
    elif fullmatch(pattern['multi_chapter_multi_verse'], label):
        chapter, verse, chapter_end, verse_end = result
        if chapter >= chapter_end:
            raise(Exception('Error in Chapter Numbering'))
        return chapter, verse, chapter_end, verse_end
    else:
        raise(Exception('Error in Chapter and/or Verse content'))


def _write_verse(content):
    with open(display_verse_full_path, 'w') as file:
        if not content:
            file.write('')
        else:
            file.write(f"{content['label']}\n{content['verse']}")


sg.theme('DarkBlue')
submit_button = 'GO!'
exit_button = 'Exit'
version_combo = 'Version'
chapterverse_input = 'ChapterVerse'

layout = [
    [sg.Text('Select Version'), sg.Combo([key for key in bible_info['Versions']],
                                         k=version_combo, size=(40, 10))],
    [sg.HorizontalSeparator()],
    [sg.Text('Select Book')],
    [sg.HorizontalSeparator()],
    [sg.Text('Select Chapter and Verse'), sg.InputText(k=chapterverse_input)],
    [sg.Button(submit_button), sg.Button(exit_button)]
]

book_list = _group_radio(
    dict=bible_info['Books'], group_id=0, group_size=6, width=12)
[layout.insert(3, book_list[i]) for i in range(len(book_list) - 1, -1, -1)]

window = sg.Window('Bible Display API', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == exit_button:
        _write_verse('')
        break
    elif event == submit_button:
        try:
            if not values[version_combo]:
                raise(Exception('Please select Version'))
            version = values[version_combo]

            book = ''
            for _ in values:
                if values[_] == True:
                    book = _
            if not book:
                raise(Exception('Please select Book'))

            chapter, verse, chapter_end, verse_end = _parse_chapterverse(
                values[chapterverse_input])

            result_verse = get_verse(bible_info['Versions'][version], bible_info['Books']
                                     [book], chapter, verse, chapter_end, verse_end)
            if not result_verse:
                raise(Exception('Bible Verse not found'))
            content = {
                'label': f'{book} {values[chapterverse_input]}', 'verse': result_verse}

            _write_verse(content)

        except Exception as e:
            _write_verse('')
            line_error = exc_info()[2].tb_lineno
            sg.popup(f"Line {line_error}: {e}", text_color='Red', )

window.close()
