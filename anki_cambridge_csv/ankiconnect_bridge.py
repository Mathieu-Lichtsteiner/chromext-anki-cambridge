"""Expose Cambridge scraping through AnkiConnect.

Drop this file into your installed `anki_cambridge` add-on folder and then
import it from that add-on's `__init__.py` *after* `from . import main`.
"""

from __future__ import annotations

import sys
from urllib.parse import urlparse

from aqt import mw
from aqt.qt import QTimer

from anki import notes

from .Cambridge import CDDownloader
from . import styles
from .utils import fill_note, fields, prepare_model

CUSTOM_ACTION = "cambridgeAddFromUrl"


def _find_ankiconnect_instance():
    for module in list(sys.modules.values()):
        if module is None:
            continue

        ac = getattr(module, "ac", None)
        if ac is None:
            continue

        if getattr(ac.__class__, "__name__", "") != "AnkiConnect":
            continue

        if not hasattr(module, "AnkiConnect"):
            continue

        return ac

    return None


def _is_cambridge_dictionary_url(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.scheme in {"http", "https"}
        and parsed.netloc == "dictionary.cambridge.org"
        and parsed.path.startswith("/dictionary/")
    )


def _add_word_to_deck(word_entry, deck_name: str):
    collection = mw.col
    model = prepare_model(collection, fields, styles.model_css)
    note = notes.Note(collection, model)
    note.model()["did"] = collection.decks.id(deck_name)
    fill_note(word_entry, note)
    collection.addNote(note)


def _cambridge_add_from_url_impl(url: str, deckName: str | None = None):
    if not url:
        raise Exception("Missing Cambridge URL.")

    if not _is_cambridge_dictionary_url(url):
        raise Exception("Only dictionary.cambridge.org word pages are supported.")

    deck_name = deckName or "Cambridge"

    downloader = getattr(mw, "cddownloader", None)
    if downloader is None:
        downloader = CDDownloader()
        mw.cddownloader = downloader

    downloader.clean_up()
    downloader.user_url = url
    downloader.get_word_defs()

    if not downloader.word_data:
        raise Exception("No definitions were extracted from the Cambridge page.")

    added = 0
    for entry in downloader.word_data:
        _add_word_to_deck(entry, deck_name)
        added += 1

    try:
        mw.reset()
    except Exception:
        pass

    return {
        "added": added,
        "deckName": deck_name,
        "word": downloader.word or downloader.word_data[0].word_title,
        "url": url,
    }


def _install_bridge() -> bool:
    ac = _find_ankiconnect_instance()
    if ac is None:
        return False

    if hasattr(ac.__class__, CUSTOM_ACTION):
        return True

    def cambridgeAddFromUrl(self, url, deckName=None):
        return _cambridge_add_from_url_impl(url, deckName)

    cambridgeAddFromUrl.api = True
    cambridgeAddFromUrl.versions = ()
    setattr(ac.__class__, CUSTOM_ACTION, cambridgeAddFromUrl)
    return True


def _install_bridge_when_ready():
    if not _install_bridge():
        QTimer.singleShot(2000, _install_bridge_when_ready)


QTimer.singleShot(2000, _install_bridge_when_ready)
