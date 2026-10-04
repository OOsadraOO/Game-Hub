import customtkinter as ctk
from utils import load_json, save_json


class GameProfileWindow(ctk.CTkToplevel):
    def __init__(self, parent, game):
        super().__init__(parent)
        self.game = game
        self.profiles = load_json("data/game_profiles.json") or {}
        self.title(f"🎮 {game['name']} Profile")
        self.geometry("620x620")
        self.minsize(560, 520)
        self.grab_set()
        self.build_ui()

    def build_ui(self):
        profile = self.profiles.get(self.game["name"], {})

        ctk.CTkLabel(
            self, text=f"🎮  {self.game['name']}",
            font=("Arial", 28, "bold"), text_color="#00ffee"
        ).pack(pady=(25, 6))

        ctk.CTkLabel(
            self, text="Game Profile", font=("Arial", 13), text_color="gray"
        ).pack(pady=(0, 20))

        form = ctk.CTkFrame(
            self, corner_radius=20, border_width=1, border_color="#252d2d"
        )
        form.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        self.genre = self._field(form, "Genre", profile.get("genre", ""))
        self.platform = self._field(form, "Platform", profile.get("platform", "PC"))
        self.status = self._field(form, "Status", profile.get("status", "Playing"))

        ctk.CTkLabel(
            form, text="Notes", font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=22, pady=(15, 7))

        self.notes = ctk.CTkTextbox(form, height=170, corner_radius=12)
        self.notes.pack(fill="x", padx=22)
        self.notes.insert("1.0", profile.get("notes", ""))

        ctk.CTkButton(
            form, text="💾 Save Profile", height=44, corner_radius=12,
            fg_color="#00aa88", hover_color="#00ccaa",
            font=("Arial", 13, "bold"), command=self.save_profile
        ).pack(fill="x", padx=22, pady=22)

    def _field(self, parent, label, value):
        ctk.CTkLabel(
            parent, text=label, font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=22, pady=(15, 7))

        entry = ctk.CTkEntry(parent, height=40, corner_radius=12)
        entry.pack(fill="x", padx=22)
        entry.insert(0, value)
        return entry

    def save_profile(self):
        self.profiles[self.game["name"]] = {
            "genre": self.genre.get().strip(),
            "platform": self.platform.get().strip(),
            "status": self.status.get().strip(),
            "notes": self.notes.get("1.0", "end").strip()
        }
        save_json("data/game_profiles.json", self.profiles)
        self.destroy()
