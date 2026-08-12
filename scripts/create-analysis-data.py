import json
from pathlib import Path

SOURCE_DIR = Path("decks")
OUTPUT_FILE = SOURCE_DIR / "analysis-data.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_card(card):
    return {
        "name": card.get("name"),
        "mana_cost": card.get("mana_cost"),
        "cmc": card.get("cmc"),
        "type_line": card.get("type_line"),
        "oracle_text": card.get("oracle_text"),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "colors": card.get("colors", []),
        "color_identity": card.get("color_identity", []),
        "quantity": card.get("quantity", 1),
    }


def normalize_deck(deck_data):
    result = {
        "name": deck_data.get("name"),
        "format": deck_data.get("format"),
        "bracket": deck_data.get("bracket"),
        "colors": deck_data.get("colors", []),
        "colorIdentity": deck_data.get("colorIdentity", []),
        "commander": [],
        "mainboard": [],
    }

    for card in deck_data.get("commander", []):
        result["commander"].append(normalize_card(card))

    for card in deck_data.get("mainboard", []):
        result["mainboard"].append(normalize_card(card))

    return result


def main():
    analysis_data = {}

    deck_files = sorted(
        p for p in SOURCE_DIR.glob("*.json")
        if p.name not in {
            "analysis-data.json",
            "card-index.json"
        }
    )

    for path in deck_files:
        data = load_json(path)

        # Unterstützt sowohl:
        # { "name": "...", ... }
        # als auch:
        # [ { "name": "...", ... } ]
        if isinstance(data, list):
            if not data:
                continue
            deck_data = data[0]
        elif isinstance(data, dict):
            deck_data = data
        else:
            continue

        deck_name = deck_data.get("name")

        if not deck_name:
            deck_name = path.stem

        deck_id = path.stem

        analysis_data[deck_id] = normalize_deck(deck_data)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            analysis_data,
            f,
            ensure_ascii=False,
            separators=(",", ":")
        )

    print(
        f"Analysis data erstellt: {OUTPUT_FILE} "
        f"({len(analysis_data)} Decks)"
    )


if __name__ == "__main__":
    main()
