"""Expose Cambridge scraping through AnkiConnect.

Drop this file into your installed `anki_cambridge` add-on folder and then
import it from that add-on's `__init__.py` *after* `from . import main`.
"""

from __future__ import annotations

import sys
from urllib.parse import urlparse

from aqt import mw
from aqt.qt import QTimer, QDialog

from .Cambridge import CDDownloader
from .gui import WordDefDialogue

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

    word = downloader.word or downloader.word_data[0].word_title

    # Show the native selection dialog so the user can pick definitions
    dlg = WordDefDialogue(downloader.word_data, word, deck_name=deck_name)

    # If there was only a single definition, WordDefDialogue auto-adds it
    if not dlg.single_word:
        result = dlg.exec()
        if result != QDialog.DialogCode.Accepted:
            return {"added": 0, "deckName": deck_name, "word": word, "url": url}

    added = len(dlg.selected_defs)

    try:
        mw.reset()
    except Exception:
        pass

    return {
        "added": added,
        "deckName": deck_name,
        "word": word,
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
