import json
from pathlib import Path


SOURCE_DIR = Path("decks")
OUTPUT_FILE = SOURCE_DIR / "analysis-data.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_face(face):
    """
    Normalisiert eine einzelne Kartenseite.
    Wird hauptsächlich für MDFCs, Transform-Karten usw. verwendet.
    """
    if not isinstance(face, dict):
        return face

    return {
        "name": face.get("name"),
        "mana_cost": face.get("mana_cost"),
        "cmc": face.get("cmc"),
        "type_line": face.get("type_line"),
        "oracle_text": face.get("oracle_text"),
        "power": face.get("power"),
        "toughness": face.get("toughness"),
        "colors": face.get("colors", []),
        "color_indicator": face.get("color_indicator", []),
        "color_identity": face.get("color_identity", []),
        "artist": face.get("artist"),
        "flavor_text": face.get("flavor_text"),
        "image_uris": face.get("image_uris", {}),
    }


def normalize_card(card, quantity=1):
    """
    Normalisiert eine Karte.

    Wichtig:
    - quantity kommt beim Moxfield-Export aus dem äußeren Karten-Eintrag.
    - card_faces werden vollständig übernommen.
    - Dadurch bleiben MDFCs wie
      'Bala Ged Recovery // Bala Ged Sanctuary'
      und
      'Vorinclex // The Grand Evolution'
      als eine Karte mit beiden Seiten erhalten.
    """
    if not isinstance(card, dict):
        return None

    raw_faces = card.get("card_faces", [])

    normalized_faces = []

    if isinstance(raw_faces, list):
        for face in raw_faces:
            normalized_face = normalize_face(face)
            if normalized_face is not None:
                normalized_faces.append(normalized_face)

    result = {
        "name": card.get("name"),
        "mana_cost": card.get("mana_cost"),
        "cmc": card.get("cmc"),
        "type_line": card.get("type_line"),
        "oracle_text": card.get("oracle_text"),
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "colors": card.get("colors", []),
        "color_identity": card.get("color_identity", []),
        "quantity": quantity,
        "layout": card.get("layout"),
        "card_faces": normalized_faces,
        "color_indicator": card.get("color_indicator", []),
    }

    return result


def normalize_board_cards(cards):
    """
    Verarbeitet die Moxfield-Struktur:

    boards
      -> mainboard
        -> cards
          -> <unique id>
            -> quantity
            -> card
    """
    result = []

    if not isinstance(cards, dict):
        return result

    for entry in cards.values():
        if not isinstance(entry, dict):
            continue

        card = entry.get("card")

        if not isinstance(card, dict):
            continue

        quantity = entry.get("quantity", 1)

        normalized = normalize_card(
            card,
            quantity=quantity
        )

        if normalized is not None:
            result.append(normalized)

    return result


def normalize_deck(deck_data):
    """
    Unterstützt die tatsächliche Moxfield-Struktur.

    Moxfield:
        main = Commander
        boards.mainboard.cards = Mainboard

    Zusätzlich werden einige alternative Strukturen unterstützt,
    damit ältere/anders exportierte Deckdateien nicht sofort
    unbrauchbar werden.
    """
    result = {
        "name": deck_data.get("name"),
        "format": deck_data.get("format"),
        "bracket": deck_data.get("bracket"),
        "colors": deck_data.get("colors", []),
        "colorIdentity": deck_data.get("colorIdentity", []),
        "commander": [],
        "mainboard": [],
    }

    # ---------------------------------------------------------
    # COMMANDER
    # ---------------------------------------------------------

    commander = deck_data.get("main")

    if isinstance(commander, dict):
        normalized_commander = normalize_card(
            commander,
            quantity=1
        )

        if normalized_commander is not None:
            result["commander"].append(normalized_commander)

    elif isinstance(commander, list):
        for card in commander:
            normalized_commander = normalize_card(
                card,
                quantity=1
            )

            if normalized_commander is not None:
                result["commander"].append(normalized_commander)

    # Falls eine Datei eine direkte "commander"-Liste besitzt,
    # verwenden wir diese zusätzlich, sofern oben nichts gefunden
    # wurde.
    if not result["commander"]:
        old_commanders = deck_data.get("commander", [])

        if isinstance(old_commanders, list):
            for card in old_commanders:
                normalized_commander = normalize_card(
                    card,
                    quantity=1
                )

                if normalized_commander is not None:
                    result["commander"].append(normalized_commander)

    # ---------------------------------------------------------
    # MAINBOARD
    # ---------------------------------------------------------

    boards = deck_data.get("boards", {})

    if isinstance(boards, dict):

        mainboard = boards.get("mainboard", {})

        if isinstance(mainboard, dict):
            cards = mainboard.get("cards", {})

            result["mainboard"] = normalize_board_cards(cards)

    # Unterstützung für ältere direkte Mainboard-Strukturen
    if not result["mainboard"]:

        old_mainboard = deck_data.get("mainboard", [])

        if isinstance(old_mainboard, list):

            for card in old_mainboard:

                # Falls es sich bereits um einen vollständigen
                # Moxfield-Eintrag handelt:
                if isinstance(card, dict) and "card" in card:

                    normalized = normalize_card(
                        card.get("card"),
                        quantity=card.get("quantity", 1)
                    )

                else:
                    normalized = normalize_card(
                        card,
                        quantity=1
                    )

                if normalized is not None:
                    result["mainboard"].append(normalized)

    return result


def get_deck_data(data):
    """
    Unterstützt:
    { ... }
    und
    [ { ... } ]

    Bei Listen wird der erste Eintrag verwendet.
    """
    if isinstance(data, list):

        if not data:
            return None

        first = data[0]

        if isinstance(first, dict):
            return first

        return None

    if isinstance(data, dict):
        return data

    return None


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

        try:
            data = load_json(path)

        except Exception as e:
            print(
                f"FEHLER beim Lesen von {path}: {e}"
            )
            continue

        deck_data = get_deck_data(data)

        if deck_data is None:
            print(
                f"Übersprungen: {path} "
                f"(kein gültiges Deck-Format)"
            )
            continue

        deck_id = path.stem

        normalized_deck = normalize_deck(deck_data)

        analysis_data[deck_id] = normalized_deck

        commander_count = len(
            normalized_deck["commander"]
        )

        mainboard_count = sum(
            card.get("quantity", 1)
            for card in normalized_deck["mainboard"]
        )

        mdfc_count = sum(
            1
            for card in (
                normalized_deck["commander"]
                + normalized_deck["mainboard"]
            )
            if len(card.get("card_faces", [])) > 1
        )

        print(
            f"{deck_id}: "
            f"{mainboard_count} Mainboard-Karten, "
            f"{commander_count} Commander, "
            f"{mdfc_count} Karten mit mehreren Faces"
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            analysis_data,
            f,
            ensure_ascii=False,
            separators=(",", ":")
        )

    print()
    print(
        f"Analysis data erstellt: {OUTPUT_FILE} "
        f"({len(analysis_data)} Decks)"
    )


if __name__ == "__main__":
    main()
