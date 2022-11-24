from time import perf_counter
import bible_data as bible
import obspython as obs
import re
import urllib.error
import urllib.request

base_url = "https://www.biblegateway.com/usage/votd/rss/votd.rdf?$31"

# ---------------Custom Functions---------------


def extract_bible_verse(data: str) -> str:
    """Extract the verse from the HTML body"""
    results = re.findall(
        r"(?<=<title>).+:.+(?=</title>)|(?<=&ldquo;).+(?=&rdquo;)", data)
    # print(f"{results=}")
    title = results[0]
    verse = re.sub(r" {2,}", " ", results[1])
    verse = re.sub(r"\[[\w ]+\] ", "", verse)
    # print(f"{title=}")
    # print(f"{verse=}")
    return verse + "\n\n" + title


def update_source(data: str) -> None:
    """Update the Text Source"""
    source = obs.obs_get_source_by_name(source_name)
    if source:
        try:
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, "text", data)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)

        except urllib.error.URLError as err:
            obs.script_log(obs.LOG_WARNING,
                           "Error opening URL '" + base_url + "': " + err.reason)
            obs.remove_current_callback()

        obs.obs_source_release(source)


def get_verse() -> str:
    """Get Verse of the Day from BibleGateway RSS"""
    data = ""
    try:
        # Call API
        # print(f"{base_url=}")
        with urllib.request.urlopen(base_url) as response:
            data = response.read().decode('utf-8')
            # print(f"{data=}")
            data = extract_bible_verse(data)

    except urllib.error.URLError as err:
        obs.script_log(obs.LOG_WARNING,
                       "Error opening URL '" + base_url + "': " + err.reason)
        obs.remove_current_callback()

    return data


def activate_callback(props, prop):
    time_start = perf_counter()

    update_source(get_verse())

    time_stop = perf_counter()
    time_elapsed = str(time_stop-time_start)
    obs.obs_data_set_string(settings_copy, "info_text",
                            formatted_time := f"{time_elapsed=!s}")
    print(formatted_time)

    return True


# ---------------Script Global Functions---------------


def script_description():
    return """Verse of the Day - BibleGateway RSS
TODO: Add other bible verse sources"""


def script_defaults(settings):
    """Sets the default values of the Script's properties when 'Defaults' button is pressed"""
    obs.obs_data_set_default_string(settings, "source", "Verse of the Week")
    obs.obs_data_set_default_string(
        settings, "version", "New International Version")


def script_update(settings):
    global source_name
    source_name = obs.obs_data_get_string(settings, "source")
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
    # Action Buttons
    obs.obs_properties_add_button(
        props, "get_button", "Get Verse", activate_callback)

    obs.obs_properties_add_text(props, "info_text", "", obs.OBS_TEXT_INFO)

    return props
