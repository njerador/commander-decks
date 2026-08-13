import json
import subprocess
from pathlib import Path

ANALYSIS_FILE = Path("decks/analysis-data.json")
OUTPUT_FILE = Path("decks/changes.json")


def load_json_text(text):
    if not text:
        return {}
    data = json.loads(text)
    return data if isinstance(data, dict) else {}


def load_previous_analysis():
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{ANALYSIS_FILE}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return load_json_text(result.stdout)
    except subprocess.CalledProcessError:
        return {}


def card_counts(cards):
    counts = {}
    if not isinstance(cards, list):
        return counts

    for card in cards:
        if not isinstance(card, dict):
            continue
        name = card.get("name")
        if not name:
            continue
        quantity = card.get("quantity", 1)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1
        counts[name] = counts.get(name, 0) + quantity

    return counts


def deck_changes(old_deck, new_deck):
    old_main = card_counts(old_deck.get("mainboard", []) if isinstance(old_deck, dict) else [])
    new_main = card_counts(new_deck.get("mainboard", []) if isinstance(new_deck, dict) else [])

    old_commanders = card_counts(old_deck.get("commander", []) if isinstance(old_deck, dict) else [])
    new_commanders = card_counts(new_deck.get("commander", []) if isinstance(new_deck, dict) else [])

    old_cards = old_main.copy()
    new_cards = new_main.copy()

    for name, quantity in old_commanders.items():
        old_cards[name] = old_cards.get(name, 0) + quantity
    for name, quantity in new_commanders.items():
        new_cards[name] = new_cards.get(name, 0) + quantity

    added = []
    removed = []

    for name in sorted(set(old_cards) | set(new_cards)):
        delta = new_cards.get(name, 0) - old_cards.get(name, 0)
        if delta > 0:
            added.append({"name": name, "quantity": delta})
        elif delta < 0:
            removed.append({"name": name, "quantity": -delta})

    return {"added": added, "removed": removed}


def main():
    with ANALYSIS_FILE.open("r", encoding="utf-8") as f:
        current = load_json_text(f.read())

    previous = load_previous_analysis()

    changes = {}

    for deck_id in sorted(set(previous) | set(current)):
        if deck_id == "analysis-export":
            continue

        old_deck = previous.get(deck_id, {})
        new_deck = current.get(deck_id, {})
        change = deck_changes(old_deck, new_deck)

        if change["added"] or change["removed"]:
            changes[deck_id] = change

    result = {
        "generated_from": "decks/analysis-data.json",
        "decks_changed": len(changes),
        "changes": changes,
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
