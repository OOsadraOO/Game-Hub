# ==================================================
# 🧰 UTILS
# ==================================================

import json
import os

_ACTIVE_USER_ID = None
_USER_DATA_FILES = {
    "games.json", "game_stats.json", "playtime.json", "todo.json",
    "music_playlist.json", "game_profiles.json"
}

def set_active_user(user_id):
    global _ACTIVE_USER_ID
    _ACTIVE_USER_ID = user_id

def clear_active_user():
    global _ACTIVE_USER_ID
    _ACTIVE_USER_ID = None

def _resolve_data_path(path):
    if _ACTIVE_USER_ID is None:
        return path
    filename = os.path.basename(path)
    if filename in _USER_DATA_FILES:
        return os.path.join("data", "users", str(_ACTIVE_USER_ID), filename)
    return path

from plyer import notification


# ==================================================
# 📂 LOAD JSON
# ==================================================

def load_json(path):

    try:

        path = _resolve_data_path(path)
        with open(path, "r") as file:

            return json.load(file)

    except:

        return []


# ==================================================
# 💾 SAVE JSON
# ==================================================

def save_json(path, data):

    path = _resolve_data_path(path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as file:

        json.dump(data, file, indent=4)


# ==================================================
# 🔔 SHOW NOTIFICATION
# ==================================================

def show_notification(title, message):

    try:

        notification.notify(
            title=title,
            message=message,
            timeout=5
        )

    except:

        print(title, message)


# ==================================================
# 📁 ENSURE FOLDER EXISTS
# ==================================================

def ensure_folder(path):

    if not os.path.exists(path):

        os.makedirs(path)


# ==================================================
# 🕒 FORMAT TIME
# ==================================================

def format_time(seconds):

    mins = seconds // 60

    secs = seconds % 60

    return f"{mins:02}:{secs:02}"
