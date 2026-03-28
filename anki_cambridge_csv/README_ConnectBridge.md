# Cambridge AnkiConnect Bridge

The existing `anki_cambridge` add-on already knows how to create notes from a Cambridge link, but it defaults cards into a fixed `Cambridge` deck. This bridge adds a custom AnkiConnect action so a browser extension can pass both:

- the Cambridge URL
- the chosen target deck

## Files

- `ankiconnect_bridge.py`
- `__init__.py.patch`

## Install into the existing `anki_cambridge` add-on

1. Open your installed `anki_cambridge` add-on folder.
2. Copy `ankiconnect_bridge.py` into that folder.
3. Edit `__init__.py`.
4. Add this line **after** `from . import main`:

```python
from . import ankiconnect_bridge
```

## New AnkiConnect action

After Anki restarts, AnkiConnect will expose:

```json
{
  "action": "cambridgeAddFromUrl",
  "version": 5,
  "params": {
    "url": "https://dictionary.cambridge.org/dictionary/english/example",
    "deckName": "My Deck"
  }
}
```

## Behavior

- Validates that the URL is a Cambridge Dictionary word page.
- Uses the installed Cambridge add-on scraper.
- Adds **all parsed definitions** from that page into the chosen deck.
- Uses the Cambridge note model and media handling already present in the add-on.
