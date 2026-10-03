# ==================================================
# 🧰 UTILS
# ==================================================

import json
import os
from plyer import notification


# ==================================================
# 📂 LOAD JSON
# ==================================================

def load_json(path):

    try:

        with open(path, "r") as file:

            return json.load(file)

    except:

        return []


# ==================================================
# 💾 SAVE JSON
# ==================================================

def save_json(path, data):

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
