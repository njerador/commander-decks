import json
from pathlib import Path

DECKS_DIR = Path("decks")
OUTPUT_FILE = DECKS_DIR / "decks-overview.json"

decks = []


def extract_card(entry):
    card = entry.get("card", {})

    return {
        "name": card.get("name"),
        "quantity": entry.get("quantity", 1),
        "board": entry.get("boardType"),
        "mana_cost": card.get("mana_cost"),
        "cmc": card.get("cmc"),
        "type_line": card.get("type_line"),
        "oracle_text": card.get("oracle_text"),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "colors": card.get("colors", []),
        "color_identity": card.get("color_identity", []),
        "scryfall_id": card.get("scryfall_id"),
        "set": card.get("set"),
        "set_name": card.get("set_name")
    }


for deck_number in range(1, 11):
    filename = DECKS_DIR / f"deck-{deck_number:02d}.json"

    if not filename.exists():
        print(f"WARNUNG: {filename} nicht gefunden.")
        continue

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        boards = data.get("boards", {})

        # ==============================
        # COMMANDERS
        # ==============================

        commander_cards = boards.get("commanders", {}).get("cards", {})
        commanders = []

        if isinstance(commander_cards, dict):
            for entry in commander_cards.values():
                commanders.append(extract_card(entry))

        # ==============================
        # MAINBOARD
        # ==============================

        mainboard_data = boards.get("mainboard", {})
        mainboard_cards = mainboard_data.get("cards", {})

        mainboard = []

        if isinstance(mainboard_cards, dict):
            for entry in mainboard_cards.values():
                mainboard.append(extract_card(entry))

        # ==============================
        # SIDEBOARD
        # ==============================

        sideboard_data = boards.get("sideboard", {})
        sideboard_cards = sideboard_data.get("cards", {})

        sideboard = []

        if isinstance(sideboard_cards, dict):
            for entry in sideboard_cards.values():
                sideboard.append(extract_card(entry))

        # ==============================
        # DECK INFORMATION
        # ==============================

        deck_info = {
            "deck_number": deck_number,
            "file": filename.name,
            "moxfield_id": data.get("publicId"),
            "name": data.get("name"),
            "description": data.get("description"),
            "format": data.get("format"),
            "public_url": data.get("publicUrl"),

            "commanders": commanders,

            "color_identity": data.get("colorIdentity", []),

            "bracket": data.get("bracket"),

            "mainboard_count": mainboard_data.get("count", 0),

            "last_updated": data.get("lastUpdatedAtUtc"),

            "mainboard": mainboard,

            "sideboard": sideboard
        }

        decks.append(deck_info)

    except Exception as e:
        print(f"FEHLER bei Deck {deck_number}: {e}")


# ==============================
# OVERVIEW SPEICHERN
# ==============================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(decks, f, indent=2, ensure_ascii=False)


# ==============================
# AUSGABE
# ==============================

print("================================")
print(f"{len(decks)} Decks verarbeitet.")
print(f"Übersicht: {OUTPUT_FILE}")
print("================================")

for deck in decks:

    commander_names = [
        commander["name"]
        for commander in deck["commanders"]
    ]

    commanders = ", ".join(commander_names)
    colors = ", ".join(deck["color_identity"])

    unique_cards = len(deck["mainboard"])

    total_cards = sum(
        card["quantity"]
        for card in deck["mainboard"]
    )

    print(f"Deck {deck['deck_number']}: {deck['name']}")
    print(f"Commander: {commanders}")
    print(f"Farben: {colors}")
    print(f"Bracket: {deck['bracket']}")
    print(f"Karten im Mainboard: {total_cards}")
    print(f"Verschiedene Mainboard-Karten: {unique_cards}")
    print(f"Letzte Änderung: {deck['last_updated']}")
    print()
