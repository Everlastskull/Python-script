"""Suivi des articles déjà envoyés, pour dédoublonner les sources scrapées
(qui n'ont pas de date de publication fiable à comparer à une fenêtre de temps).
Le fichier state.json est committé par le workflow après chaque run réussi.
"""

import json
import os

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")
MAX_ENTRIES = 3000


def load_seen():
    if not os.path.exists(STATE_PATH):
        return []
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_seen(seen_list):
    trimmed = seen_list[-MAX_ENTRIES:]
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2, ensure_ascii=False)
        f.write("\n")
