import json
from pathlib import Path

DECKS_DIR = Path("decks")
OUTPUT_FILE = DECKS_DIR / "decks-overview.json"

decks = []

for deck_number in range(1, 11):
    filename = DECKS_DIR / f"deck-{deck_number:02d}.json"

    if not filename.exists():
        print(f"WARNUNG: {filename} nicht gefunden.")
        continue

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        boards = data.get("boards", {})

        # Commander aus boards.commanders.cards
        commander_cards = boards.get("commanders", {}).get("cards", {})

        commanders = []

        if isinstance(commander_cards, dict):
            for entry in commander_cards.values():
                card = entry.get("card", {})
                name = card.get("name")

                if name:
                    commanders.append(name)

        # Mainboard
        mainboard = boards.get("mainboard", {})
        mainboard_count = mainboard.get("count", 0)

        # Farben
        color_identity = data.get("colorIdentity", [])

        # Bracket
        bracket = data.get("bracket")

        # Letzte Änderung
        last_updated = data.get("lastUpdatedAtUtc")

        deck_info = {
            "deck_number": deck_number,
            "file": filename.name,
            "moxfield_id": data.get("publicId"),
            "name": data.get("name"),
            "commanders": commanders,
            "color_identity": color_identity,
            "bracket": bracket,
            "mainboard_count": mainboard_count,
            "last_updated": last_updated,
            "public_url": data.get("publicUrl")
        }

        decks.append(deck_info)

    except Exception as e:
        print(f"FEHLER bei Deck {deck_number}: {e}")

# Übersicht speichern
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(decks, f, indent=2, ensure_ascii=False)

print("================================")
print(f"{len(decks)} Decks verarbeitet.")
print(f"Übersicht: {OUTPUT_FILE}")
print("================================")

for deck in decks:
    commanders = ", ".join(deck["commanders"]) if deck["commanders"] else "NICHT GEFUNDEN"
    colors = ", ".join(deck["color_identity"]) if deck["color_identity"] else "FARBLOS"

    print(f"Deck {deck['deck_number']}: {deck['name']}")
    print(f"Commander: {commanders}")
    print(f"Farben: {colors}")
    print(f"Bracket: {deck['bracket']}")
    print(f"Karten im Mainboard: {deck['mainboard_count']}")
    print(f"Letzte Änderung: {deck['last_updated']}")
    print()
