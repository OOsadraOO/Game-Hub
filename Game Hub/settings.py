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

        account_card = ctk.CTkFrame(
            self,
            corner_radius=18,
            border_width=1,
            border_color="#252d2d"
        )
        account_card.pack(fill="x", padx=25, pady=8)

        ctk.CTkLabel(
            account_card,
            text="Account",
            font=("Arial", 17, "bold")
        ).pack(anchor="w", padx=20, pady=(16, 2))

        username = self.parent_app.current_user.get("username", "User")
        ctk.CTkLabel(
            account_card,
            text=f"Signed in as  •  {username}",
            text_color="#00ffee",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 12))

        account_buttons = ctk.CTkFrame(account_card, fg_color="transparent")
        account_buttons.pack(fill="x", padx=16, pady=(0, 16))
        account_buttons.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            account_buttons,
            text="Change Username",
            height=38,
            corner_radius=10,
            command=self.change_username
        ).grid(row=0, column=0, padx=4, sticky="ew")

        ctk.CTkButton(
            account_buttons,
            text="Change Password",
            height=38,
            corner_radius=10,
            command=self.change_password
        ).grid(row=0, column=1, padx=4, sticky="ew")

        ctk.CTkButton(
            account_buttons,
            text="Delete Account",
            height=38,
            corner_radius=10,
            fg_color="#8c3030",
            hover_color="#b33b3b",
            command=self.delete_account
        ).grid(row=1, column=0, columnspan=2, padx=4, pady=(8, 0), sticky="ew")

        ctk.CTkButton(
            account_buttons,
            text="Sign Out",
            height=38,
            corner_radius=10,
            fg_color="#6b2525",
            hover_color="#8c3030",
            command=self.sign_out
        ).grid(row=0, column=2, padx=4, sticky="ew")

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


    def _account_dialog(self, title, fields, callback):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("430x360")
        dialog.minsize(400, 330)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=title,
            font=("Arial", 22, "bold"), text_color="#00ffee"
        ).pack(pady=(24, 18))

        entries = []
        for label, show in fields:
            ctk.CTkLabel(
                dialog, text=label,
                font=("Arial", 12, "bold")
            ).pack(anchor="w", padx=25, pady=(8, 5))
            entry = ctk.CTkEntry(dialog, height=40, corner_radius=10, show=show)
            entry.pack(fill="x", padx=25)
            entries.append(entry)

        status = ctk.CTkLabel(dialog, text="", wraplength=360)
        status.pack(pady=12)

        def submit():
            ok, message = callback([entry.get() for entry in entries])
            status.configure(
                text=message,
                text_color="#00ff88" if ok else "#ff6b6b"
            )
            if ok:
                dialog.after(600, dialog.destroy)

        ctk.CTkButton(
            dialog, text="Save", height=42,
            fg_color="#00aa88", hover_color="#00ccaa",
            command=submit
        ).pack(fill="x", padx=25, pady=(0, 18))

        entries[0].focus_set()

    def change_username(self):
        current = self.parent_app.current_user
        def callback(values):
            ok, message = self.parent_app.account_db.change_username(
                current["id"], values[0]
            )
            if ok:
                self.parent_app.refresh_current_user()
                self.after(650, self.refresh_account_ui)
            return ok, message

        self._account_dialog(
            "Change Username",
            [("New username", None)],
            callback
        )

    def change_password(self):
        user_id = self.parent_app.current_user["id"]
        def callback(values):
            if values[1] != values[2]:
                return False, "New passwords do not match."
            ok, message = self.parent_app.account_db.change_password(
                user_id, values[0], values[1]
            )
            if ok:
                self.after(700, self._force_relogin)
            return ok, message

        self._account_dialog(
            "Change Password",
            [
                ("Current password", "•"),
                ("New password", "•"),
                ("Confirm new password", "•")
            ],
            callback
        )

    def refresh_account_ui(self):
        self.destroy()
        SettingsWindow(self.parent_app)

    def delete_account(self):
        user_id = self.parent_app.current_user["id"]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Delete GameHub Account")
        dialog.geometry("440x380")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Delete Account",
            font=("Arial", 24, "bold"), text_color="#ff6b6b"
        ).pack(pady=(28, 8))

        ctk.CTkLabel(
            dialog,
            text="This permanently removes your account and all personal GameHub data.\nSystem Log data is not part of the account and will remain.",
            wraplength=370, justify="center", text_color="#b8c0c0"
        ).pack(pady=(0, 18))

        password = ctk.CTkEntry(
            dialog, height=42, corner_radius=10,
            placeholder_text="Enter your current password", show="•"
        )
        password.pack(fill="x", padx=28, pady=8)

        confirm = ctk.CTkEntry(
            dialog, height=42, corner_radius=10,
            placeholder_text="Type DELETE to confirm"
        )
        confirm.pack(fill="x", padx=28, pady=8)

        status = ctk.CTkLabel(dialog, text="", wraplength=360)
        status.pack(pady=8)

        def submit():
            if confirm.get().strip() != "DELETE":
                status.configure(text="Type DELETE exactly to confirm.", text_color="#ff6b6b")
                return

            if not self.parent_app.account_db.authenticate(
                self.parent_app.current_user["username"], password.get()
            ):
                status.configure(text="Current password is incorrect.", text_color="#ff6b6b")
                return

            self.parent_app.account_db.delete_user(user_id)
            self.parent_app.save_remembered_token(None)
            self.parent_app.session_token = None
            self.parent_app.current_user = None
            from utils import clear_active_user
            clear_active_user()
            dialog.grab_release()
            dialog.destroy()
            self.destroy()
            self.parent_app.open_auth()

        ctk.CTkButton(
            dialog, text="Delete Account Permanently", height=44,
            fg_color="#8c3030", hover_color="#b33b3b",
            command=submit
        ).pack(fill="x", padx=28, pady=14)

        password.focus_set()

    def _force_relogin(self):
        self.destroy()
        self.parent_app.logout()

    def sign_out(self):
        self.destroy()
        self.parent_app.logout()

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
