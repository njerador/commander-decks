#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DECKS_DIR = ROOT / "decks"
OUTPUT_FILE = DECKS_DIR / "analysis-export.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_card_name(card):
    if not isinstance(card, dict):
        return None

    # Moxfield-/Export-Strukturen
    if isinstance(card.get("card"), dict):
        name = card["card"].get("name")
        if name:
            return name

    return card.get("name")


def normalize_card(card):
    """
    Reduziert eine Karte auf die Informationen, die für die
    Deckanalyse tatsächlich benötigt werden.
    """
    if not isinstance(card, dict):
        return None

    source = card.get("card", card)

    if not isinstance(source, dict):
        return None

    result = {
        "name": source.get("name"),
        "mana_cost": source.get("mana_cost"),
        "cmc": source.get("cmc"),
        "type_line": source.get("type_line"),
        "oracle_text": source.get("oracle_text"),
        "power": source.get("power"),
        "toughness": source.get("toughness"),
        "colors": source.get("colors", []),
        "color_identity": source.get("color_identity", []),
        "set": source.get("set"),
        "set_name": source.get("set_name"),
    }

    # Menge aus Moxfield-Daten übernehmen
    quantity = card.get("quantity", 1)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1

    result["quantity"] = quantity

    return result


def find_commander(deck):
    """
    Ermittelt den Commander aus den vorhandenen Moxfield-Daten.
    """

    boards = deck.get("boards", {})

    # Moxfield verwendet normalerweise commanders / commanders board.
    possible_boards = [
        boards.get("commanders"),
        boards.get("commander"),
        deck.get("commanders"),
        deck.get("commander"),
    ]

    for board in possible_boards:
        if not board:
            continue

        cards = board.get("cards", {}) if isinstance(board, dict) else board

        if isinstance(cards, dict):
            for card_data in cards.values():
                card = normalize_card(card_data)
                if card:
                    return card

        elif isinstance(cards, list):
            for card_data in cards:
                card = normalize_card(card_data)
                if card:
                    return card

    # Fallback: Moxfield markiert Karten teilweise direkt
    mainboard = boards.get("mainboard", {})
    cards = mainboard.get("cards", {}) if isinstance(mainboard, dict) else {}

    if isinstance(cards, dict):
        for card_data in cards.values():
            if card_data.get("isCommander"):
                card = normalize_card(card_data)
                if card:
                    return card

    return None


def get_mainboard(deck):
    boards = deck.get("boards", {})
    mainboard = boards.get("mainboard", {})

    if isinstance(mainboard, dict):
        cards = mainboard.get("cards", {})

        if isinstance(cards, dict):
            return cards.values()

        if isinstance(cards, list):
            return cards

    return []


def process_deck(path):
    deck = load_json(path)

    commander = find_commander(deck)

    mainboard_cards = []

    for card_data in get_mainboard(deck):
        card = normalize_card(card_data)

        if card is None:
            continue

        # Commander nicht zusätzlich im Mainboard ausgeben
        if commander and card["name"] == commander["name"]:
            continue

        mainboard_cards.append(card)

    deck_name = deck.get("name") or path.stem

    return {
        "id": deck.get("id"),
        "name": deck_name,
        "description": deck.get("description", ""),
        "commander": commander,
        "mainboard": mainboard_cards,
        "mainboard_count": sum(
            card.get("quantity", 1) for card in mainboard_cards
        ),
    }


def main():
    decks = []

    for path in sorted(DECKS_DIR.glob("deck-*.json")):
        try:
            deck = process_deck(path)
            decks.append(deck)
            print(
                f"{path.name}: "
                f"{deck['name']} | "
                f"Commander: "
                f"{deck['commander']['name'] if deck['commander'] else 'NICHT ERKANNT'} | "
                f"Mainboard: {deck['mainboard_count']}"
            )

        except Exception as e:
            print(f"FEHLER bei {path.name}: {e}")

    output = {
        "version": 2,
        "decks_processed": len(decks),
        "decks": decks,
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print()
    print("ANALYSE-EXPORT")
    print(f"Decks verarbeitet: {len(decks)}")
    print(f"Ausgabe: {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
