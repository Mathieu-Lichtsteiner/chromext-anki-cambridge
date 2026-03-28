const ANKI_ENDPOINTS = [
  'http://127.0.0.1:8765',
  'http://localhost:8765'
];
const ANKI_VERSION = 5;
const CUSTOM_ACTION = 'cambridgeAddFromUrl';

const currentWordEl = document.getElementById('currentWord');
const currentUrlEl = document.getElementById('currentUrl');
const deckSelectEl = document.getElementById('deckSelect');
const addButtonEl = document.getElementById('addButton');
const statusEl = document.getElementById('status');

let currentUrl = '';
let activeEndpoint = ANKI_ENDPOINTS[0];

function setStatus(message, type = 'info') {
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
}

function isCambridgeDictionaryUrl(url) {
  try {
    const parsed = new URL(url);
    return (
      parsed.hostname === 'dictionary.cambridge.org' &&
      parsed.pathname.startsWith('/dictionary/')
    );
  } catch {
    return false;
  }
}

async function getCurrentTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.url ?? '';
}

function extractWord(url) {
  try {
    const parsed = new URL(url);
    const segments = parsed.pathname.split('/').filter(Boolean);
    return segments.length > 0 ? decodeURIComponent(segments[segments.length - 1]) : null;
  } catch {
    return null;
  }
}
  for (const endpoint of ANKI_ENDPOINTS) {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, version: ANKI_VERSION, params })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status} ${response.statusText}`);
      }

      const body = await response.json();
      if (body.error) {
        throw new Error(body.error);
      }

      activeEndpoint = endpoint;
      return body.result;
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError ?? new Error('Could not reach AnkiConnect.');
}

function populateDecks(decks, selectedDeck) {
  deckSelectEl.innerHTML = '';

  for (const deck of decks) {
    const option = document.createElement('option');
    option.value = deck;
    option.textContent = deck;
    if (deck === selectedDeck) {
      option.selected = true;
    }
    deckSelectEl.appendChild(option);
  }

  deckSelectEl.disabled = false;
}

async function loadDecks() {
  const [decks, saved] = await Promise.all([
    invokeAnkiConnect('deckNames'),
    chrome.storage.local.get(['lastDeck'])
  ]);

  const selectedDeck = decks.includes(saved.lastDeck) ? saved.lastDeck : decks[0];
  populateDecks(decks, selectedDeck);
  addButtonEl.disabled = false;
  setStatus(`Connected to AnkiConnect at ${activeEndpoint}.`, 'info');
}

async function handleAddClick() {
  addButtonEl.disabled = true;
  setStatus('Adding Cambridge entry to Anki…', 'info');

  const deckName = deckSelectEl.value;
  await chrome.storage.local.set({ lastDeck: deckName });

  try {
    const result = await invokeAnkiConnect(CUSTOM_ACTION, {
      url: currentUrl,
      deckName
    });

    const added = result?.added ?? 0;
    const word = result?.word ? ` for “${result.word}”` : '';
    setStatus(`Added ${added} card(s)${word}.`, 'success');
  } catch (error) {
    setStatus(error.message, 'error');
  } finally {
    addButtonEl.disabled = false;
  }
}

async function init() {
  try {
    currentUrl = await getCurrentTabUrl();

    const word = extractWord(currentUrl);
    currentWordEl.textContent = word ?? 'Unknown word';
    currentUrlEl.textContent = currentUrl;

    if (!isCambridgeDictionaryUrl(currentUrl)) {
      setStatus('Open a Cambridge Dictionary word page first.', 'error');
      return;
    }

    await loadDecks();
  } catch (error) {
    setStatus(error.message, 'error');
  }
}

deckSelectEl.addEventListener('change', async () => {
  await chrome.storage.local.set({ lastDeck: deckSelectEl.value });
});
addButtonEl.addEventListener('click', handleAddClick);
document.addEventListener('DOMContentLoaded', init);
