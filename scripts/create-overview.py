import json
from pathlib import Path
from datetime import datetime

DECKS_DIR = Path("decks")
OUTPUT_FILE = DECKS_DIR / "decks-overview.json"


def get_board_cards(data, board_name):
    """
    Gibt die Karten eines Boards als Liste zurück.
    Moxfield speichert Boards als:
    {
        "count": ...,
        "cards": {
            "id": {
                "quantity": 1,
                "boardType": "...",
                "card": {...}
            }
        }
    }
    """
    board = data.get("boards", {}).get(board_name, {})

    if not isinstance(board, dict):
        return []

    cards = board.get("cards", {})

    if not isinstance(cards, dict):
        return []

    result = []

    for entry in cards.values():
        card = entry.get("card", {})
        quantity = entry.get("quantity", 1)

        if not card:
            continue

        result.append({
            "name": card.get("name"),
            "quantity": quantity,
            "card_id": card.get("id"),
            "unique_card_id": card.get("uniqueCardId"),
            "scryfall_id": card.get("scryfall_id"),
            "mana_cost": card.get("mana_cost"),
            "cmc": card.get("cmc"),
            "type_line": card.get("type_line"),
            "colors": card.get("colors", []),
            "color_identity": card.get("color_identity", []),
        })

    return result


def get_commanders(data):
    return get_board_cards(data, "commanders")


def get_mainboard(data):
    return get_board_cards(data, "mainboard")


def get_total_quantity(cards):
    return sum(card["quantity"] for card in cards)


def get_unique_count(cards):
    return len(cards)


def get_colors(data):
    return data.get("colorIdentity", [])


def get_last_updated(data):
    return data.get("lastUpdatedAtUtc")


def get_bracket(data):
    return data.get("bracket")


def load_deck(deck_file):
    with open(deck_file, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    overview = []

    deck_files = sorted(DECKS_DIR.glob("deck-*.json"))

    for deck_file in deck_files:
        try:
            data = load_deck(deck_file)

            deck_number = int(
                deck_file.stem.replace("deck-", "")
            )

            name = data.get("name", deck_file.stem)

            commanders = get_commanders(data)
            mainboard = get_mainboard(data)

            commander_count = get_total_quantity(commanders)
            mainboard_count = get_total_quantity(mainboard)
            total_count = commander_count + mainboard_count

            unique_mainboard = get_unique_count(mainboard)

            colors = get_colors(data)
            bracket = get_bracket(data)
            last_updated = get_last_updated(data)

            deck_info = {
                "deck_number": deck_number,
                "file": deck_file.name,
                "moxfield_id": data.get("publicId"),
                "name": name,

                "commanders": commanders,
                "commander_count": commander_count,

                "mainboard": mainboard,
                "mainboard_count": mainboard_count,
                "unique_mainboard_cards": unique_mainboard,

                "total_cards": total_count,

                "colors": colors,
                "bracket": bracket,
                "last_updated": last_updated,
            }

            overview.append(deck_info)

            # Ausgabe
            commander_names = [
                card["name"]
                for card in commanders
            ]

            if commander_names:
                commander_text = ", ".join(commander_names)
            else:
                commander_text = "NICHT GEFUNDEN"

            expected_total = 100

            if total_count == expected_total:
                status = "OK"
            elif total_count < expected_total:
                status = f"FEHLEN {expected_total - total_count}"
            else:
                status = f"{total_count - expected_total} ZU VIEL"

            print(f"Deck {deck_number}: {name}")
            print(f"Commander: {commander_text}")
            print(
                f"Farben: {', '.join(colors) if colors else 'keine'}"
            )
            print(f"Bracket: {bracket}")
            print(f"Karten im Mainboard: {mainboard_count}")
            print(f"Verschiedene Mainboard-Karten: {unique_mainboard}")
            print(f"Gesamt mit Commander: {total_count}")
            print(f"Deckgröße: {status}")
            print(f"Letzte Änderung: {last_updated}")
            print()

        except Exception as e:
            print(
                f"FEHLER bei {deck_file.name}: {e}"
            )

    overview.sort(
        key=lambda x: x["deck_number"]
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            overview,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("================================")
    print(f"{len(overview)} Decks verarbeitet.")
    print(f"Übersicht: {OUTPUT_FILE}")
    print("================================")


if __name__ == "__main__":
    main()
