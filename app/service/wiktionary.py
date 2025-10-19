import tempfile
import requests
from urllib.request import urlopen, Request
import os
import re

from app import app

cfg = app.config


def get_pronunciation_audio(word, language_code):
    # ex: https://ru.wiktionary.org/w/api.php?action=query&titles=%D1%82%D0%B5%D1%81%D1%82&generator=images
    url = f"https://{language_code}.wiktionary.org/w/api.php"

    params = {
        "action": "query",
        "prop": "imageinfo",
        "generator": "images",
        "titles": word,
        "format": "json",
        "iiprop": "url",
    }

    response = requests.get(
        headers={"User-Agent": "BeFluentVocabHelper"},
        url=url,
        params=params,
    )
    print(response.status_code, response.content)
    data = response.json()

    audio_urls = []
    if "query" in data:
        for file_page in data["query"]["pages"].values():
            title = file_page["title"]
            if title.endswith(".ogg"):
                print("file_page", file_page)
                try:
                    audio_url = file_page["imageinfo"][0]["url"]
                    audio_urls.append(audio_url)
                except KeyError:
                    pass

    # return the first audio containing "language_code" in the title, otherwise return the first audio
    if len(audio_urls) == 0:
        return []

    # Check if any audio URL contains the language code in the title (this prevents cases where we get audio from other languages)
    for audio_url in audio_urls:
        title = audio_url.split("/")[-1]
        if title.lower().startswith(language_code):
            return audio_url
    return audio_urls[0]


def download_audio(url):
    temp_dir = os.path.join(os.getcwd(), cfg["TEMP_DIR"])
    print("url", url)
    # add header to urlopen request
    data = urlopen(
        url=Request(
            url,
            headers={"User-Agent": "BeFluentVocabHelper"},
        )
    ).read()

    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".ogg", dir=temp_dir
    ) as f:
        f.write(data)
        return f

def get_ipa_transcriptions(word, language_code):
    # ex: https://en.wiktionary.org/w/api.php?action=query&prop=revisions&titles=cat&rvprop=content&format=json
    url = f"https://{language_code}.wiktionary.org/w/api.php"

    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "titles": word,
        "format": "json",
    }

    response = requests.get(
        headers={"User-Agent": "BeFluentVocabHelper"},
        url=url,
        params=params,
    )
    print(response.status_code, response.content)
    data = response.json()

    if "query" in data:
        for page in data["query"]["pages"].values():
            if "revisions" in page:
                revisions = page["revisions"]
                if revisions and len(revisions) > 0 and "*" in revisions[0]:
                    # Regex to capture the IPA transcription between slashes
                    pattern = r"\{\{IPA\|" + language_code + r"\|(\/.*\/)"

                    matches = re.findall(pattern, revisions[0]["*"])

                    if language_code == 'en':
                        # US transcription in priority
                        matches = re.findall(r"a=US.*" + pattern, revisions[0]["*"]) + matches

                    print("matches", matches)

                    return matches
    return []

def search(query, language):
    language_code = cfg["LANGUAGE_CODES"][language]
    audio_url = get_pronunciation_audio(
        query, language_code
    )
    audio_filename = None
    if audio_url:
        audio_filename = download_audio(audio_url).name

    ipa_transcriptions = get_ipa_transcriptions(
        query, language_code
    )

    ipa_transcription = None
    if len(ipa_transcriptions) > 0:
        ipa_transcription = ipa_transcriptions[0]
        ipa_transcription = ipa_transcription.replace("|","\n")

    return {"audio_filename": audio_filename, "ipa_transcription": ipa_transcription}
