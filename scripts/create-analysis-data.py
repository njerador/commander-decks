import json
from pathlib import Path

DECKS_DIR = Path("decks")
OUTPUT_FILE = DECKS_DIR / "analysis-data.json"


def extract_card(entry):
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


def load_deck(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        if len(data) == 1 and isinstance(data[0], dict):
            data = data[0]
        else:
            raise ValueError("JSON enthält unerwartete Listenstruktur")

    if not isinstance(data, dict):
        raise ValueError("JSON enthält kein gültiges Objekt")

    boards = data.get("boards", {})

    if not isinstance(boards, dict):
        boards = {}

    commanders = extract_board(
        boards.get("commanders")
    )

    mainboard = extract_board(
        boards.get("mainboard")
    )

    sideboard = extract_board(
        boards.get("sideboard")
    )

    return {
        "name": data.get("name"),
        "format": data.get("format"),
        "bracket": data.get("bracket"),
        "colors": data.get("colors"),
        "color_identity": data.get("colorIdentity"),
        "commander": commanders,
        "mainboard": mainboard,
        "sideboard": sideboard
    }


def main():
    result = {}

    deck_files = sorted(
        DECKS_DIR.glob("deck-*.json")
    )

    for path in deck_files:
        try:
            deck = load_deck(path)
            result[path.stem] = deck

        except Exception as e:
            print(
                f"WARNUNG: {path.name} konnte nicht verarbeitet werden:"
            )
            print(f"  {e}")

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            separators=(",", ":")
        )

    print("================================")
    print("ANALYSE-DATEN")
    print("================================")
    print(f"Decks verarbeitet: {len(result)}")

    for deck_id, deck in result.items():

        commander_count = sum(
            card["quantity"]
            for card in deck["commander"]
        )

        mainboard_count = sum(
            card["quantity"]
            for card in deck["mainboard"]
        )

        print(
            f"{deck_id}: "
            f"{deck['name']} | "
            f"Commander: {commander_count} | "
            f"Mainboard: {mainboard_count}"
        )

    print("--------------------------------")
    print(f"Ausgabe: {OUTPUT_FILE}")
    print("================================")


if __name__ == "__main__":
    main()
