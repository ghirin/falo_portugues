import json
import os
import random
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DB_FILE = "vocabulary.dat"


def load_vocab():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


# Глобальная очередь карточек для текущей сессии
session_cards = []


@app.route("/")
def index():
    global session_cards
    # При обновлении страницы запускаем новую сессию
    session_cards = load_vocab()
    random.shuffle(session_cards)
    return render_template("index.html")


@app.route("/next_card", methods=["POST"])
def next_card():
    global session_cards

    # Получаем оценку за прошлую карточку (если она была)
    data = request.json or {}
    status = data.get("status")  # "know" или "dont_know"

    if status == "dont_know" and session_cards:
        # Если не знаем, переносим текущую карточку в конец
        card = session_cards.pop(0)
        session_cards.append(card)
    elif status == "know" and session_cards:
        # Если знаем, удаляем из сессии
        session_cards.pop(0)

    if not session_cards:
        return jsonify({"finished": True, "remaining": 0})

    # Отдаем следующую карточку
    current = session_cards[0]
    return jsonify(
        {"finished": False, "pt": current["pt"], "ru": current["ru"], "remaining": len(session_cards)}
    )


if __name__ == "__main__":
    app.run(debug=True)