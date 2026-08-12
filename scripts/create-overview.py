import json


with open("decks/deck-01.json", "r", encoding="utf-8") as f:
    data = json.load(f)

boards = data.get("boards", {})

print("================================")
print("DIAGNOSE BOARD-STRUKTUR")
print("================================")

for board_name in ["commanders", "mainboard", "sideboard"]:

    board = boards.get(board_name)

    print()
    print(f"=== {board_name.upper()} ===")
    print(f"Typ: {type(board).__name__}")

    if isinstance(board, dict):

        print(f"Anzahl Einträge: {len(board)}")
        print(f"Keys: {list(board.keys())[:10]}")

        for key, value in list(board.items())[:3]:

            print()
            print(f"KEY: {key}")
            print(f"Wert-Typ: {type(value).__name__}")
            print(f"Wert: {value}")

    elif isinstance(board, list):

        print(f"Anzahl Einträge: {len(board)}")

        for item in board[:3]:

            print()
            print(f"Element-Typ: {type(item).__name__}")
            print(f"Element: {item}")

    else:

        print(f"Wert: {board}")

print()
print("================================")
print("ENDE DIAGNOSE")
print("================================")
