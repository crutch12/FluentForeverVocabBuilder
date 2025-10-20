import base64
import os
import html

import requests

from app import app

cfg = app.config


class AnkiConnect:
    # URL = "http://anki-desktop:8765/"
    URL = "http://host.docker.internal:8765/"
    VERSION = 6

    def invoke(self, action, params=None):
        
        
        payload = {"action": action, "version": self.VERSION}
        if params:
            payload["params"] = params
        response = requests.request("POST", self.URL, json=payload).json()
        if len(response) != 2:
            raise Exception("response has an unexpected number of fields")
        if "error" not in response:
            raise Exception("response is missing required error field")
        if "result" not in response:
            raise Exception("response is missing required result field")
        if response["error"] is not None:
            raise Exception(response["error"])
        return response["result"]

    def get_deck_names(self):
        return self.invoke("deckNames")

    def store_media_file(self, src_file_path, word):
        action = "storeMediaFile"
        sanitized_word = "".join(
            [c for c in word if c.isalpha() or c.isdigit() or c == " " or c == "-"]
        ).rstrip()
        ext = os.path.splitext(src_file_path)[1]
        dst = "{}{}".format(sanitized_word, ext)

        with open(src_file_path, "rb") as f:
            b64_output = base64.b64encode(f.read()).decode("utf-8")
        params = {"filename": dst, "data": b64_output}

        self.invoke(action, params)
        return dst

    @staticmethod
    def format_notes(notes):
        html_notes = "<br>".join(html.escape(notes.strip()).split("\n"))
        if not html_notes:
            return ""
        return "<div>{}</div>".format(html_notes)

    def add_note(
        self,
        deck_name,
        word,
        image_paths,
        ipa_transcription,
        definition,
        example,
        notes_front,
        notes_back,
        recording_file_path,
        reverse,
    ):
        stored_images = []
        for i, image_path in enumerate(image_paths):
            stored_images.append(
                self.store_media_file(image_path, "{}-{}".format(word, i))
            )

        picture_field = ""
        for stored_image in stored_images:
            picture_field += '<img src="{}">'.format(stored_image)

        formatted_ipa_transcription = self.format_notes(ipa_transcription)
        formatted_definition = self.format_notes(definition)
        formatted_example = self.format_notes(example)
        formatted_notes_front = self.format_notes(notes_front)
        formatted_notes_back = self.format_notes(notes_back)

        pronunciation_field = ""
        if recording_file_path:
            stored_audio_filename = self.store_media_file(recording_file_path, word)
            pronunciation_field = "[sound:{}]".format(stored_audio_filename)

        reverse = "y" if reverse else ""

        front_lines = [
            picture_field,
            formatted_notes_front,
            formatted_definition,
            "e.g. " + formatted_example if formatted_example else "",
        ]

        back_lines = [
            word,
            formatted_ipa_transcription,
            pronunciation_field,
            "e.g. " + formatted_example if formatted_example else "",
            formatted_notes_back,
        ]

        params = {
            "note": {
                "deckName": deck_name,
                "modelName": "Basic (optional reversed card)",
                "fields": {
                    "Front": "<br>".join(s.strip() for s in front_lines if s.strip()),
                    "Back": "<br>".join(s.strip() for s in back_lines if s.strip()),
                    "Add Reverse": reverse,
                },
                "tags": [],
            }
        }

        print(params)

        note_id = self.invoke("addNote", params)
        return note_id

    def sync(
        self,
    ):
        params = {
            # "fullSync": True  # Optional: True forces full sync
        }

        sync_result = self.invoke("sync", params)
        return sync_result
