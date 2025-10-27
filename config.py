import os

MEGABYTE = (2 ** 10) ** 2

class Config(object):
    SECRET_KEY = "fluent-forever"
    # GOOGLE_IMAGES_LANGUAGE = "French"
    WIKTIONARY_LANGUAGE = "english"
    NUM_GOOGLE_IMAGES = 5
    TEMP_DIR_NAME = "temp"
    TEMP_DIR = os.path.join(os.getcwd(), "app", TEMP_DIR_NAME)
    MAX_IMAGE_SIZE = (400, 400)
    MAX_FORM_MEMORY_SIZE = 50 * MEGABYTE
    AVAILABLE_LANGUAGES = [
        "English",
        "Russian",
        "French",
        "Spanish",
        "German",
        "Italian",
    ]
    LANGUAGE_CODES = {
        "Russian": "ru",
        "French": "fr",
        "English": "en",
        "Spanish": "es",
        "German": "de",
        "Italian": "it",
    }
