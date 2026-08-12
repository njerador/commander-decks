import json
from pathlib import Path
from collections import defaultdict

DECKS_DIR = Path("decks")
OVERVIEW_FILE = DECKS_DIR / "decks-overview.json"
OUTPUT_FILE = DECKS_DIR / "card-index.json"


def main():
    with open(OVERVIEW_FILE, "r", encoding="utf-8") as f:
        decks = json.load(f)

    card_index = defaultdict(lambda: {
        "name": None,
        "decks": []
    })

    for deck in decks:
        deck_number = deck["deck_number"]
        deck_name = deck["name"]

        # Mainboard
        for card in deck.get("mainboard", []):
            name = card.get("name")

            if not name:
                continue

            key = name.lower()

            card_index[key]["name"] = name

            # Nur einmal pro Deck eintragen
            if not any(
                d["deck_number"] == deck_number
                for d in card_index[key]["decks"]
            ):
                card_index[key]["decks"].append({
                    "deck_number": deck_number,
                    "deck_name": deck_name,
                    "quantity": card.get("quantity", 1),
                    "board": "mainboard"
                })

        # Commander
        for card in deck.get("commanders", []):
            name = card.get("name")

            if not name:
                continue

            key = name.lower()

            card_index[key]["name"] = name

            if not any(
                d["deck_number"] == deck_number
                for d in card_index[key]["decks"]
            ):
                card_index[key]["decks"].append({
                    "deck_number": deck_number,
                    "deck_name": deck_name,
                    "quantity": card.get("quantity", 1),
                    "board": "commander"
                })

    # Nach Kartenname sortieren
    sorted_index = dict(
        sorted(
            card_index.items(),
            key=lambda item: item[1]["name"].lower()
        )
    )

    # Anzahl der Decks ergänzen
    for card in sorted_index.values():
        card["deck_count"] = len(card["decks"])

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            sorted_index,
            f,
            ensure_ascii=False,
            indent=2
        )

    # Statistik
    total_cards = len(sorted_index)

    cards_in_multiple = sum(
        1
        for card in sorted_index.values()
        if card["deck_count"] >= 2
    )

    cards_in_one = sum(
        1
        for card in sorted_index.values()
        if card["deck_count"] == 1
    )

    print("================================")
    print("KARTEN-INDEX")
    print("================================")
    print(f"Decks verarbeitet: {len(decks)}")
    print(f"Verschiedene Karten insgesamt: {total_cards}")
    print(f"Karten in genau 1 Deck: {cards_in_one}")
    print(f"Karten in mindestens 2 Decks: {cards_in_multiple}")
    print(f"Ausgabe: {OUTPUT_FILE}")
    print("================================")


if __name__ == "__main__":
    main()
