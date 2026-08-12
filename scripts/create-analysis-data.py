import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DECKS_DIR = BASE_DIR / "decks"
OUTPUT_FILE = DECKS_DIR / "analysis-data.json"


def extract_cards(board):
    """Extrahiert nur die für die Deckanalyse relevanten Kartendaten."""
    if not isinstance(board, dict):
        return []

    cards = board.get("cards", {})

    if not isinstance(cards, dict):
        return []

    result = []

    for entry in cards.values():
        card = entry.get("card", {})

        if not isinstance(card, dict):
            continue

        result.append({
            "name": card.get("name"),
            "quantity": entry.get("quantity", 1),
            "mana_cost": card.get("mana_cost"),
            "cmc": card.get("cmc"),
            "type_line": card.get("type_line"),
            "oracle_text": card.get("oracle_text"),
            "power": card.get("power"),
            "toughness": card.get("toughness"),
            "colors": card.get("colors", []),
            "color_identity": card.get("color_identity", []),
            "set": card.get("set"),
            "board": entry.get("boardType"),
        })

    # Alphabetisch sortieren
    result.sort(key=lambda x: (x["name"] or "").lower())

    return result


def extract_commanders(board):
    """Extrahiert die Commander."""
    if not isinstance(board, dict):
        return []

    cards = board.get("cards", {})

    if not isinstance(cards, dict):
        return []

    result = []

    for entry in cards.values():
        card = entry.get("card", {})

        if not isinstance(card, dict):
            continue

        result.append({
            "name": card.get("name"),
            "mana_cost": card.get("mana_cost"),
            "cmc": card.get("cmc"),
            "type_line": card.get("type_line"),
            "oracle_text": card.get("oracle_text"),
            "power": card.get("power"),
            "toughness": card.get("toughness"),
            "colors": card.get("colors", []),
            "color_identity": card.get("color_identity", []),
        })

    return result


def process_deck(deck_number):
    filename = DECKS_DIR / f"deck-{deck_number:02d}.json"

    if not filename.exists():
        print(f"WARNUNG: {filename} nicht gefunden.")
        return None

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    boards = data.get("boards", {})

    commanders = extract_commanders(
        boards.get("commanders")
    )

    mainboard = extract_cards(
        boards.get("mainboard")
    )

    sideboard = extract_cards(
        boards.get("sideboard")
    )

    return {
        "deck_number": deck_number,
        "name": data.get("name"),
        "format": data.get("format"),
        "bracket": data.get("bracket"),
        "colors": data.get("colors", []),
        "color_identity": data.get("colorIdentity", []),
        "created_at": data.get("createdAtUtc"),
        "last_updated": data.get("lastUpdatedAtUtc"),

        "commanders": commanders,

        "mainboard_count": sum(
            card["quantity"] for card in mainboard
        ),

        "mainboard_unique": len(mainboard),

        "mainboard": mainboard,

        "sideboard": sideboard,
    }


def main():
    print("================================")
    print("ERSTELLE ANALYSE-DATEN")
    print("================================")

    decks = []

    for deck_number in range(1, 11):
        deck = process_deck(deck_number)

        if deck:
            decks.append(deck)

            commander_names = ", ".join(
                c["name"] for c in deck["commanders"]
            ) or "NICHT GEFUNDEN"

            print(
                f"Deck {deck_number}: {deck['name']}"
            )

            print(
                f"Commander: {commander_names}"
            )

            print(
                f"Karten: {deck['mainboard_count']}"
            )

    output = {
        "generated_from": "Moxfield deck JSON files",
        "deck_count": len(decks),
        "decks": decks
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("================================")
    print(f"{len(decks)} Decks exportiert.")
    print(f"Ausgabe: {OUTPUT_FILE}")
    print("================================")


if __name__ == "__main__":
    main()
