import json
from pathlib import Path

DECKS_DIR = Path("decks")
OUTPUT_FILE = DECKS_DIR / "analysis-export.json"


def extract_card(entry):
    """Extrahiert nur die für die Deckanalyse relevanten Kartendaten."""

    if not isinstance(entry, dict):
        return None

    card = entry.get("card", entry)

    if not isinstance(card, dict):
        return None

    return {
        "name": card.get("name"),
        "mana_cost": card.get("mana_cost"),
        "cmc": card.get("cmc"),
        "type_line": card.get("type_line"),
        "oracle_text": card.get("oracle_text"),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "colors": card.get("colors"),
        "color_identity": card.get("color_identity"),
        "quantity": entry.get("quantity", 1)
    }


def extract_board(board):
    """Unterstützt sowohl Dict- als auch Listen-Strukturen."""

    cards = []

    if isinstance(board, dict):
        entries = board.get("cards", {})

        if isinstance(entries, dict):
            entries = entries.values()

    elif isinstance(board, list):
        entries = board

    else:
        entries = []

    for entry in entries:
        card = extract_card(entry)

        if card:
            cards.append(card)

    return cards


result = {}

deck_files = sorted(DECKS_DIR.glob("deck-*.json"))

for path in deck_files:

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Falls die Datei unerwartet eine Liste enthält
    if isinstance(data, list):

        if len(data) == 1 and isinstance(data[0], dict):
            data = data[0]

        else:
            print(f"WARNUNG: {path} enthält eine Liste und wird übersprungen.")
            continue

    if not isinstance(data, dict):
        print(f"WARNUNG: {path} besitzt kein gültiges JSON-Objekt.")
        continue

    boards = data.get("boards", {})

    if not isinstance(boards, dict):
        boards = {}

    deck = {
        "name": data.get("name"),
        "format": data.get("format"),
        "bracket": data.get("bracket"),
        "colors": data.get("colors"),
        "colorIdentity": data.get("colorIdentity"),
        "commander": extract_board(
            boards.get("commanders")
        ),
        "mainboard": extract_board(
            boards.get("mainboard")
        )
    }

    result[path.stem] = deck


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        result,
        f,
        ensure_ascii=False,
        separators=(",", ":")
    )


print("================================")
print("ANALYSE-EXPORT")
print("================================")
print(f"Decks verarbeitet: {len(result)}")

for deck_id, deck in result.items():
    print(
        f"{deck_id}: "
        f"{deck['name']} | "
        f"Commander: {len(deck['commander'])} | "
        f"Mainboard: {sum(c['quantity'] for c in deck['mainboard'])}"
    )

print(f"Ausgabe: {OUTPUT_FILE}")
print("================================")
