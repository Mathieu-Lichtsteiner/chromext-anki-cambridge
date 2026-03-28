# Cambridge to Anki Chrome Extension

This is a minimal Manifest V3 Chrome extension.

## What it does

- Works from a Cambridge Dictionary word page.
- Fetches your Anki deck list through AnkiConnect.
- Lets you choose the target deck.
- Sends the current Cambridge URL and selected deck to a custom AnkiConnect action named `cambridgeAddFromUrl`.

## Install

1. Open `chrome://extensions/`
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select this folder.

## Requirement

This extension expects a small Anki-side bridge to exist, exposing the AnkiConnect action:

- `cambridgeAddFromUrl(url, deckName)`

That bridge is included separately in the `cambridge-anki-bridge` artifact.
