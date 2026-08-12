import json
import glob
import os

OUTPUT_FILE = "decks/decks-overview.json"

decks = []

for filename in sorted(glob.glob("decks/deck-*.json")):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        deck_number = os.path.basename(filename).replace("deck-", "").replace(".json", "")

        commanders = []

        for card in data.get("commanders", []):
            name = card.get("name")
            if name:
                commanders.append(name)

        deck = {
            "deck_number": int(deck_number),
            "file": os.path.basename(filename),
            "moxfield_id": data.get("publicId"),
            "name": data.get("name"),
            "commanders": commanders,
            "last_updated": data.get("lastUpdatedAt"),
        }

        decks.append(deck)

    except Exception as e:
        print(f"Fehler bei {filename}: {e}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(decks, f, indent=2, ensure_ascii=False)

print(f"{len(decks)} Decks verarbeitet.")
print(f"Übersicht gespeichert unter: {OUTPUT_FILE}")
