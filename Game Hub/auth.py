# ==================================================
# GAMEHUB AUTHENTICATION UI
# ==================================================

import customtkinter as ctk
from account_db import AccountDB


class AuthWindow(ctk.CTkToplevel):
    def __init__(self, parent, account_db, on_login):
        super().__init__(parent)
        self.parent_app = parent
        self.account_db = account_db
        self.on_login = on_login
        self.remember_token = None

        self.title("GameHub • Account")
        self.geometry("520x650")
        self.minsize(480, 620)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(parent)
        self.grab_set()

        self._center()
        self.build_ui()
        self.try_remembered_login()

    def _center(self):
        self.update_idletasks()
        width, height = 520, 650
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def build_ui(self):
        self.configure(fg_color="#0f1212")

        ctk.CTkLabel(
            self, text="GAMEHUB", font=("Arial", 32, "bold"),
            text_color="#00ffee"
        ).pack(pady=(32, 4))

        ctk.CTkLabel(
            self, text="Your gaming space. One account.",
            font=("Arial", 13), text_color="#7d8989"
        ).pack(pady=(0, 22))

        tabs = ctk.CTkSegmentedButton(
            self, values=["Sign In", "Register"],
            command=self.switch_mode, height=42
        )
        tabs.pack(fill="x", padx=35)
        tabs.set("Sign In")
        self.tabs = tabs

        self.form = ctk.CTkFrame(
            self, corner_radius=20, border_width=1, border_color="#252d2d"
        )
        self.form.pack(fill="both", expand=True, padx=35, pady=20)

        self.status = ctk.CTkLabel(
            self.form, text="", text_color="#ff6b6b",
            wraplength=390, font=("Arial", 12)
        )

        self.render_signin()

    def clear_form(self):
        for widget in self.form.winfo_children():
            widget.destroy()

    def field(self, label, show=None):
        ctk.CTkLabel(
            self.form, text=label, font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=24, pady=(18, 6))
        entry = ctk.CTkEntry(self.form, height=42, corner_radius=12, show=show)
        entry.pack(fill="x", padx=24)
        return entry

    def render_signin(self):
        self.clear_form()
        ctk.CTkLabel(
            self.form, text="Welcome back",
            font=("Arial", 24, "bold"), text_color="#00ffee"
        ).pack(pady=(24, 2))

        ctk.CTkLabel(
            self.form, text="Sign in to continue to GameHub",
            text_color="#7d8989"
        ).pack(pady=(0, 6))

        self.username_entry = self.field("Username")
        self.password_entry = self.field("Password", "•")

        self.remember_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.form, text="Remember me",
            variable=self.remember_var
        ).pack(anchor="w", padx=24, pady=18)

        ctk.CTkButton(
            self.form, text="Sign In", height=46, corner_radius=12,
            fg_color="#00aa88", hover_color="#00ccaa",
            font=("Arial", 13, "bold"), command=self.sign_in
        ).pack(fill="x", padx=24, pady=(4, 10))

        self.status = ctk.CTkLabel(
            self.form, text="", text_color="#ff6b6b",
            wraplength=390
        )
        self.status.pack(pady=(2, 16))

        self.password_entry.bind("<Return>", lambda _e: self.sign_in())
        self.username_entry.focus_set()

    def render_register(self):
        self.clear_form()
        ctk.CTkLabel(
            self.form, text="Create your account",
            font=("Arial", 24, "bold"), text_color="#00ffee"
        ).pack(pady=(22, 2))

        ctk.CTkLabel(
            self.form, text="Create a local GameHub profile",
            text_color="#7d8989"
        ).pack(pady=(0, 4))

        self.username_entry = self.field("Username")
        self.password_entry = self.field("Password", "•")
        self.confirm_entry = self.field("Confirm password", "•")

        ctk.CTkLabel(
            self.form,
            text="8+ characters • at least one letter and one number",
            text_color="#697575", font=("Arial", 11)
        ).pack(pady=(8, 10))

        ctk.CTkButton(
            self.form, text="Create Account", height=46, corner_radius=12,
            fg_color="#00aa88", hover_color="#00ccaa",
            font=("Arial", 13, "bold"), command=self.register
        ).pack(fill="x", padx=24, pady=(2, 10))

        self.status = ctk.CTkLabel(
            self.form, text="", text_color="#ff6b6b",
            wraplength=390
        )
        self.status.pack(pady=(2, 16))

        self.confirm_entry.bind("<Return>", lambda _e: self.register())
        self.username_entry.focus_set()

    def switch_mode(self, value):
        if value == "Register":
            self.render_register()
        else:
            self.render_signin()

    def show_error(self, message):
        self.status.configure(text=message, text_color="#ff6b6b")

    def show_success(self, message):
        self.status.configure(text=message, text_color="#00ff88")

    def sign_in(self):
        user = self.account_db.authenticate(
            self.username_entry.get(), self.password_entry.get()
        )
        if not user:
            self.show_error("Invalid username or password.")
            return

        token = None
        if self.remember_var.get():
            token = self.account_db.create_session(user["id"])

        self.complete_login(user, token)

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not username:
            self.show_error("Please enter a username.")
            self.username_entry.focus_set()
            return

        if not password:
            self.show_error("Please enter a password.")
            self.password_entry.focus_set()
            return

        if password != confirm:
            self.show_error("Passwords do not match.")
            self.confirm_entry.focus_set()
            return

        try:
            ok, message, user = self.account_db.create_user(username, password)
            if not ok or user is None:
                self.show_error(message or "Could not create the account.")
                return

            token = self.account_db.create_session(user["id"])
            self.show_success("Account created. Signing you in…")
            self.after(250, lambda: self.complete_login(user, token))
        except Exception as exc:
            # Keep registration failures inside the UI instead of silently
            # terminating the button callback.
            self.show_error(f"Registration failed: {exc}")

    def try_remembered_login(self):
        # The token is intentionally stored by the main app, not inside the UI.
        token = self.parent_app.load_remembered_token()
        if not token:
            return
        user = self.account_db.get_user_by_token(token)
        if user:
            self.complete_login(user, token)

    def complete_login(self, user, token):
        self.remember_token = token
        self.grab_release()
        self.destroy()
        self.on_login(user, token)

    def cancel(self):
        self.grab_release()
        self.destroy()
        self.parent_app.destroy()
