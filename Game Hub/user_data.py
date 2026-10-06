# ==================================================
# GAMEHUB USER DATA STORE
# ==================================================

import json
import os
import shutil

USER_FILES = (
    "games.json", "game_stats.json", "playtime.json",
    "todo.json", "music_playlist.json", "game_profiles.json"
)

class UserDataStore:
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir

    def user_dir(self, user_id):
        path = os.path.join(self.base_dir, "users", str(user_id))
        os.makedirs(path, exist_ok=True)
        return path

    def path(self, user_id, filename):
        if filename not in USER_FILES:
            raise ValueError("Unsupported user data file.")
        return os.path.join(self.user_dir(user_id), filename)

    def migrate_legacy(self, user_id):
        target_dir = self.user_dir(user_id)
        migrated = []
        for filename in USER_FILES:
            source = os.path.join(self.base_dir, filename)
            target = os.path.join(target_dir, filename)
            if os.path.exists(source) and not os.path.exists(target):
                shutil.copy2(source, target)
                migrated.append(filename)
        return migrated

    def delete(self, user_id):
        path = os.path.join(self.base_dir, "users", str(user_id))
        if os.path.isdir(path):
            shutil.rmtree(path)

    def load(self, user_id, filename, default=None):
        path = self.path(user_id, filename)
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, ValueError, TypeError):
            return default

    def save(self, user_id, filename, data):
        path = self.path(user_id, filename)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
