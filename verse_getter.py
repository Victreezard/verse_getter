from time import perf_counter
import bible_data as bible
import obspython as obs
import re
import urllib.error
import urllib.request

base_url = 'https://ibibles.net/quote.php?'

# ---------------Custom Functions---------------


def extract_verse(data: str) -> str:
    """Extract the verse from the HTML body"""
    return re.findall("(?<=</small>).+(?=<br>)", data)[0].strip()


def update_source(bible_verse: str, url: str) -> str:
    """Get the verse from the Bible Display API and update the Text Source"""
    source = obs.obs_get_source_by_name(source_name)
    text = ""
    if source:
        try:
            # Call API
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                print(f"{data=}")
                text = bible_verse + "\n" + extract_verse(data)
                # Update Text Source
                settings = obs.obs_data_create()
                obs.obs_data_set_string(settings, "text", text)
                obs.obs_source_update(source, settings)
                obs.obs_data_release(settings)

        except urllib.error.URLError as err:
            obs.script_log(obs.LOG_ERROR,
                           "Error opening URL '" + url + "': " + err.reason)
            obs.remove_current_callback()

        obs.obs_source_release(source)

    return text


def get_verse(op=None) -> str:
    """
    Build the bible verse format and the complete URL for the API call
    op defines whether to increment (if True) or decrement (if False) the verse number
    """
    global version
    global book
    global chapter_verse

    ver = bible.VERSION.get(version)
    bk = bible.BOOK.get(book)

    ch_verse = chapter_verse.strip()
    if op is None:
        ch_verse = re.sub(" +", ":", ch_verse)
    else:
        if op is True:
            operand = 1
        elif op is False:
            operand = -1
        # Add or Subtract verse number
        chapter, verse = re.sub(" +", " ", ch_verse).split(" ")
        verse = int(verse) + operand
        chapter_verse = f"{chapter} {verse}"
    ch_verse = chapter_verse.replace(" ", ":")

    bible_verse = f"{ver.upper()} {book.title()} {ch_verse}"
    url = f"{base_url}{ver}-{bk}/{ch_verse}"
    print(f"{url=}")
    return update_source(bible_verse, url)


def get_pressed(props, prop):
    time_start = perf_counter()

    verse = get_verse()

    time_stop = perf_counter()
    time_elapsed = str(time_stop-time_start)
    obs.obs_data_set_string(settings_copy, "info_text",
                            formatted_time := f"{time_elapsed=!s}")
    obs.obs_data_set_string(settings_copy, "result_text", verse)
    print(formatted_time)

    return True


def next_pressed(props, prop):
    verse = get_verse(op=True)
    obs.obs_data_set_string(settings_copy, "chapter_verse", chapter_verse)
    obs.obs_data_set_string(settings_copy, "result_text", verse)

    return True


def prev_pressed(props, prop):
    verse = get_verse(op=False)
    obs.obs_data_set_string(settings_copy, "chapter_verse", chapter_verse)
    obs.obs_data_set_string(settings_copy, "result_text", verse)

    return True


# ---------------Script Global Functions---------------


def script_description():
    return """Verse Getter"""

def script_defaults(settings):
    """Sets the default values of the Script's properties when 'Defaults' button is pressed"""
    obs.obs_data_set_default_string(settings, "source", "Verse")
    obs.obs_data_set_default_string(
        settings, "version", "New International Version")
    obs.obs_data_set_default_string(settings, "book", "Genesis")
    obs.obs_data_set_default_string(settings, "chapter_verse", "")


def script_update(settings):
    global source_name
    source_name = obs.obs_data_get_string(settings, "source")
    global version
    version = obs.obs_data_get_string(settings, "version")
    global book
    book = obs.obs_data_get_string(settings, "book")
    global chapter_verse
    chapter_verse = obs.obs_data_get_string(settings, "chapter_verse")

    global settings_copy
    settings_copy = settings


def script_properties():
    props = obs.obs_properties_create()
    # Text Source List
    p = obs.obs_properties_add_list(props, "source", "Text Source",
                                    obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            match source_id:
                case "text_gdiplus" | "text_ft2_source":
                    name = obs.obs_source_get_name(source)
                    obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)
    # Version List
    p = obs.obs_properties_add_list(props, "version", "Version", obs.OBS_COMBO_TYPE_EDITABLE,
                                    obs.OBS_COMBO_FORMAT_STRING)
    for ver in bible.VERSION:
        obs.obs_property_list_add_string(p, ver, bible.VERSION.get(ver))
    # Book List
    p = obs.obs_properties_add_list(props, "book", "Book", obs.OBS_COMBO_TYPE_EDITABLE,
                                    obs.OBS_COMBO_FORMAT_STRING)
    for bk in bible.BOOK:
        obs.obs_property_list_add_string(p, bk, bible.BOOK.get(bk))
    # Chapter and Verse Textbox
    obs.obs_properties_add_text(
        props, "chapter_verse", "Chapter & Verse", obs.OBS_TEXT_DEFAULT)
    # Action Buttons
    obs.obs_properties_add_button(
        props, "get_button", "Get Verse", get_pressed)
    obs.obs_properties_add_button(
        props, "next_button", "Next Verse", next_pressed)
    obs.obs_properties_add_button(
        props, "prev_button", "Previous Verse", prev_pressed)

    obs.obs_properties_add_text(props, "info_text", "", obs.OBS_TEXT_INFO)
    obs.obs_properties_add_text(props, "result_text", "Result", obs.OBS_TEXT_MULTILINE)

    return props
