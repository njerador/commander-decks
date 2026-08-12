import json
from pathlib import Path

DECKS_DIR = Path("decks")
OUTPUT_FILE = DECKS_DIR / "analysis-export.json"

result = {}

for path in sorted(DECKS_DIR.glob("deck-*.json")):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    deck = {
        "name": data.get("name"),
        "format": data.get("format"),
        "bracket": data.get("bracket"),
        "colors": data.get("colors"),
        "colorIdentity": data.get("colorIdentity"),
        "commander": [],
        "mainboard": []
    }

    boards = data.get("boards", {})

    # Commander
    commanders = boards.get("commanders", {})
    for entry in commanders.get("cards", {}).values():
        card = entry.get("card", {})
        deck["commander"].append({
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
        })

    # Mainboard
    mainboard = boards.get("mainboard", {})
    for entry in mainboard.get("cards", {}).values():
        card = entry.get("card", {})
        deck["mainboard"].append({
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
        })

    result[path.stem] = deck

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

print("================================")
print("ANALYSE-EXPORT")
print("================================")
print(f"Decks exportiert: {len(result)}")
print(f"Ausgabe: {OUTPUT_FILE}")
print("================================")
