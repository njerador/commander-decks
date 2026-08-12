import json
import glob
import os


OUTPUT_FILE = "decks/decks-overview.json"


def extract_cards(board):
    """
    Moxfield speichert Boards als Dictionary.
    Wir holen daraus die Kartennamen.
    """
    cards = []

    if isinstance(board, dict):
        for card_id, card_data in board.items():
            if isinstance(card_data, dict):
                name = card_data.get("name")

                if name:
                    cards.append(name)

    elif isinstance(board, list):
        for card_data in board:
            if isinstance(card_data, dict):
                name = card_data.get("name")

                if name:
                    cards.append(name)

    return cards


decks = []


for filename in sorted(glob.glob("decks/deck-*.json")):

    try:

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        deck_number = int(
            os.path.basename(filename)
            .replace("deck-", "")
            .replace(".json", "")
        )

        # Commander
        commanders = extract_cards(
            data.get("boards", {}).get("commanders", {})
        )

        # Mainboard
        mainboard = extract_cards(
            data.get("boards", {}).get("mainboard", {})
        )

        # Sideboard
        sideboard = extract_cards(
            data.get("boards", {}).get("sideboard", {})
        )

        deck = {
            "deck_number": deck_number,
            "file": os.path.basename(filename),

            "moxfield_id": data.get("publicId"),

            "name": data.get("name"),

            "commanders": commanders,

            "colors": data.get("colors", []),

            "color_identity": data.get("colorIdentity", []),

            "bracket": data.get("bracket"),

            "created_at": data.get("createdAtUtc"),

            "last_updated": data.get("lastUpdatedAtUtc"),

            "mainboard_card_count": len(mainboard),

            "sideboard_card_count": len(sideboard),

            "mainboard": mainboard,

            "sideboard": sideboard
        }

        decks.append(deck)

    except Exception as e:

        print(f"Fehler bei {filename}: {e}")


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    json.dump(
        decks,
        f,
        indent=2,
        ensure_ascii=False
    )


print()
print("================================")
print(f"{len(decks)} Decks verarbeitet.")
print(f"Übersicht: {OUTPUT_FILE}")
print("================================")

for deck in decks:

    print()
    print(
        f"Deck {deck['deck_number']}: "
        f"{deck['name']}"
    )

    print(
        f"Commander: "
        f"{', '.join(deck['commanders']) or 'NICHT GEFUNDEN'}"
    )

    print(
        f"Farben: "
        f"{', '.join(deck['colors']) or 'colorless'}"
    )

    print(
        f"Bracket: "
        f"{deck['bracket']}"
    )

    print(
        f"Karten im Mainboard: "
        f"{deck['mainboard_card_count']}"
    )
