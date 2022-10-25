import bible_data as bible
import obspython as obs
import re
import urllib.parse
import urllib.request

base_url = 'https://ibibles.net/quote.php?'

# ---------------Custom Functions---------------


def extract_verse(data: str) -> str:
    """Extract the verse from the HTML body"""
    return re.findall("(?<=</small>).+(?=<br>)", data)[0].strip()


def update_source(bible_verse: str, url: str):
    """Get the verse from the Bible Display API and update the Text Source"""
    source = obs.obs_get_source_by_name(source_name)
    if source is not None:
        try:
            # Call API
            print(f"URL: {url}")
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                print(data)
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


def get_verse(op=None):
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
    update_source(bible_verse, url)


def get_pressed(props, prop):
    get_verse()


def next_pressed(props, prop):
    get_verse(op=True)


def prev_pressed(props, prop):
    get_verse(op=False)

# ---------------Script Global Functions---------------


def script_description():
    return """Verse Getter
Note: Chapter & Verse does not change when Next or Prev button is pressed."""


def script_defaults(settings):
    """Sets the default values of the Script's properties when 'Defaults' button is pressed"""
    obs.obs_data_set_default_string(settings, "source", "Verse")
    obs.obs_data_set_default_string(
        settings, "version", "New International Version")
    obs.obs_data_set_default_string(settings, "book", "Genesis")
    obs.obs_data_set_default_string(settings, "chapter_verse", "")


def script_update(settings):
    global source_name
    global version
    global book
    global chapter_verse

    source_name = obs.obs_data_get_string(settings, "source")
    version = obs.obs_data_get_string(settings, "version")
    book = obs.obs_data_get_string(settings, "book")
    chapter_verse = obs.obs_data_get_string(settings, "chapter_verse")


def script_properties():
    props = obs.obs_properties_create()
    # Text Source List
    p = obs.obs_properties_add_list(props, "source", "Text Source",
                                    obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
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

    return props
