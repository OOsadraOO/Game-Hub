import customtkinter as ctk
from icons import get_icon
from utils import load_json, save_json


class SettingsWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent_app = parent
        self.settings = load_json("data/settings.json") or {
            "appearance": "dark",
            "rgb_enabled": True,
            "session_notifications": True
        }

        self.title("⚙ GameHub Settings")
        self.geometry("520x500")
        self.minsize(480, 450)
        self.grab_set()

        self.build_ui()

    def build_ui(self):

        ctk.CTkLabel(
            self,
            text="⚙  GameHub Settings",
            font=("Arial", 30, "bold"),
            text_color="#00ffee"
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self,
            text="Customize the GameHub experience",
            font=("Arial", 13),
            text_color="gray"
        ).pack(pady=(0, 25))

        appearance_card = ctk.CTkFrame(
            self,
            corner_radius=18,
            border_width=1,
            border_color="#252d2d"
        )
        appearance_card.pack(fill="x", padx=25, pady=8)

        ctk.CTkLabel(
            appearance_card,
            text="Appearance",
            font=("Arial", 17, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        self.theme = ctk.CTkOptionMenu(
            appearance_card,
            values=["Dark", "Light", "System"],
            command=self.change_theme
        )
        self.theme.set(self.settings.get("appearance", "dark").title())
        self.theme.pack(fill="x", padx=20, pady=(0, 18))

        behavior_card = ctk.CTkFrame(
            self,
            corner_radius=18,
            border_width=1,
            border_color="#252d2d"
        )
        behavior_card.pack(fill="x", padx=25, pady=8)

        ctk.CTkLabel(
            behavior_card,
            text="Behavior",
            font=("Arial", 17, "bold")
        ).pack(anchor="w", padx=20, pady=(18, 8))

        self.rgb_switch = ctk.CTkSwitch(
            behavior_card,
            text="RGB sidebar border",
            command=self.save
        )
        if self.settings.get("rgb_enabled", True):
            self.rgb_switch.select()
        self.rgb_switch.pack(anchor="w", padx=20, pady=8)

        self.notification_switch = ctk.CTkSwitch(
            behavior_card,
            text="Session notifications",
            command=self.save
        )
        if self.settings.get("session_notifications", True):
            self.notification_switch.select()
        self.notification_switch.pack(anchor="w", padx=20, pady=(0, 18))

        ctk.CTkButton(
            self,
            text="Save Settings",
            image=get_icon("settings", 18),
            compound="left",
            height=44,
            corner_radius=12,
            fg_color="#00aa88",
            hover_color="#00ccaa",
            font=("Arial", 13, "bold"),
            command=self.save
        ).pack(fill="x", padx=25, pady=18)

        self.status = ctk.CTkLabel(
            self,
            text="Settings are saved locally.",
            text_color="gray"
        )
        self.status.pack()

    def change_theme(self, value):
        mode = value.lower()
        ctk.set_appearance_mode(mode)
        self.settings["appearance"] = mode
        self.save()

    def save(self):
        self.settings["rgb_enabled"] = bool(self.rgb_switch.get())
        self.settings["session_notifications"] = bool(
            self.notification_switch.get()
        )
        save_json("data/settings.json", self.settings)
        self.status.configure(text="✓ Settings saved")
