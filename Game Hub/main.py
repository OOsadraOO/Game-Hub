# ==================================================
# 🎮 GAMEHUB MAIN
# ==================================================

import customtkinter as ctk
import json
import os

from config import *
from theme import animate_rgb
from icons import get_icon, get_tk_icon

from splash import SplashScreen

from home import HomePage
from launcher import GameLauncher
from music import MusicPlayer
from timer import TimerSystem
from todo import TodoSystem
from stats import StatsPage
from system_log import SystemLogPage
from account_db import AccountDB
from auth import AuthWindow
from user_data import UserDataStore
from utils import set_active_user, clear_active_user

# ==================================================
# 🎨 CUSTOMTKINTER
# ==================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ==================================================
# 🚀 MAIN APP
# ==================================================

class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        # ==================================================
        # 🪟 WINDOW
        # ==================================================

        self.title(APP_NAME)

        self._window_icon = get_tk_icon("logo", 64)
        self.iconphoto(False, self._window_icon)

        width = 1450
        height = 900

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = 1200
        window_height = 700

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        print("SCREEN:", screen_width, screen_height)
        print("WINDOW:", window_width, window_height)
        print("POS:", x, y)

        self.geometry(
            f"{window_width}x{window_height}+{x}+{y}"
        )

        self.update_idletasks()

        print(self.geometry())

        self.minsize(
            1200,
            750
        )

        self.configure(
            fg_color="#111111"
        )

        # ==================================================
        # 🎬 SPLASH
        # ==================================================

        self.account_db = AccountDB()
        self.user_data = UserDataStore()
        self.current_user = None
        self.session_token = None
        self.remember_path = os.path.join("data", "remember_me.json")

        self.withdraw()

        splash = SplashScreen(self)

        self.after(2500, self._finish_startup)

        # ==================================================
        # GRID
        # ==================================================

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        # ==================================================
        # SIDEBAR
        # ==================================================

        self.sidebar = ctk.CTkFrame(
            self,
            width=225,
            corner_radius=0,
            border_width=1,
            border_color="#222828"
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nswe",
            padx=(5,0)
        )

        self.sidebar.grid_propagate(False)

        # ==================================================
        # LOGO
        # ==================================================

        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        logo_frame.pack(
            pady=(28, 22)
        )

        ctk.CTkLabel(
            logo_frame,
            image=get_icon("logo", 56),
            text=""
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            logo_frame,
            text="GameHub",
            font=("Arial", 30, "bold"),
            text_color="#00ffee"
        ).pack()

        # ==================================================
        # NAVIGATION
        # ==================================================

        nav_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        nav_frame.pack(
            fill="x",
            padx=18,
            pady=10
        )

        buttons = [
            ("Home", "home", "home"),
            ("Launcher", "launcher", "launcher"),
            ("Music", "music", "music"),
            ("Timer", "timer", "timer"),
            ("To-Do", "todo", "todo"),
            ("Stats", "stats", "stats"),
            ("System Log", "system_log", "log")
        ]

        self.nav_buttons = []
        self.nav_pages = []

        for text, page, icon_name in buttons:

            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                image=get_icon(icon_name, 18),
                compound="left",
                anchor="w",
                height=50,
                corner_radius=14,
                font=("Arial", 15, "bold"),
                fg_color="#171c1c",
                hover_color="#202b2b",
                border_width=1,
                border_color="#273131",
                command=lambda p=page: self.show_page(p)
            )

            btn.pack(
                fill="x",
                pady=8
            )

            self.nav_buttons.append(btn)
            self.nav_pages.append(page)

        # ==================================================
        # VERSION
        # ==================================================

        version_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        version_frame.pack(
            side="bottom",
            pady=20
        )

        ctk.CTkLabel(
            version_frame,
            text="GAMEHUB  •  v2.0",
            text_color="#667070"
        ).pack()

        # ==================================================
        # MAIN CONTAINER
        # ==================================================

        self.container = ctk.CTkFrame(
            self,
            fg_color="#0f1212",
            corner_radius=0
        )

        self.container.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.container.grid_rowconfigure(
            0,
            weight=1
        )

        self.container.grid_columnconfigure(
            0,
            weight=1
        )

        # ==================================================
        # PAGES
        # ==================================================

        self.pages = {}

        # HOME

        self.pages["home"] = ctk.CTkFrame(
            self.container,
            fg_color="#111111"
        )

        HomePage(
            self,
            self.pages["home"]
        )

        # LAUNCHER

        self.pages["launcher"] = ctk.CTkFrame(
            self.container,
            fg_color="#111111"
        )

        GameLauncher(
            self,
            self.pages["launcher"]
        )

        # MUSIC

        self.pages["music"] = ctk.CTkFrame(
            self.container,
            fg_color="#111111"
        )

        MusicPlayer(
            self,
            self.pages["music"]
        )

        # TIMER

        self.pages["timer"] = ctk.CTkFrame(
            self.container,
            fg_color="#111111"
        )

        TimerSystem(
            self,
            self.pages["timer"]
        )

        # TODO

        self.pages["todo"] = ctk.CTkFrame(
            self.container,
            fg_color="#111111"
        )

        TodoSystem(
            self,
            self.pages["todo"]
        )

        # STATS

        self.pages["stats"] = ctk.CTkFrame(
            self.container,
            fg_color="#111111"
        )

        StatsPage(
            self,
            self.pages["stats"]
        )

        # ==================================================
        # SYSTEM LOG

        self.pages["system_log"] = ctk.CTkFrame(
            self.container,
            fg_color="#111111"
        )

        self.system_log_page = SystemLogPage(
            self,
            self.pages["system_log"]
        )

        # START PAGE
        # ==================================================

        self.show_page("home")

        # Command Palette
        self.bind("<Control-k>", self.open_command_palette)

        # ==================================================
        # RGB EFFECT
        # ==================================================

        animate_rgb(self)

    # ==================================================
    # ACCOUNT / AUTH
    # ==================================================

    def _finish_startup(self):
        self.deiconify()
        self.after(80, self.open_auth)

    def open_auth(self):
        if self.current_user is not None:
            return
        AuthWindow(self, self.account_db, self.on_login)

    def load_remembered_token(self):
        try:
            with open(self.remember_path, "r", encoding="utf-8") as file:
                return json.load(file).get("token")
        except Exception:
            return None

    def save_remembered_token(self, token):
        os.makedirs(os.path.dirname(self.remember_path), exist_ok=True)
        if token:
            with open(self.remember_path, "w", encoding="utf-8") as file:
                json.dump({"token": token}, file)
        else:
            try:
                os.remove(self.remember_path)
            except FileNotFoundError:
                pass

    def on_login(self, user, token):
        self.user_data.migrate_legacy(user["id"])
        set_active_user(user["id"])
        self.current_user = user
        self.session_token = token
        self.save_remembered_token(token)
        self.show_page("home")

    def logout(self):
        if self.session_token:
            self.account_db.revoke_session(self.session_token)
        self.session_token = None
        self.current_user = None
        clear_active_user()
        self.save_remembered_token(None)
        self.open_auth()

    def refresh_current_user(self):
        if self.current_user:
            fresh = self.account_db.get_user(self.current_user["id"])
            if fresh:
                self.current_user = fresh

    def open_command_palette(self, _event=None):

        window = ctk.CTkToplevel(self)
        window.title("Command Palette")
        window.geometry("520x430")
        window.grab_set()

        ctk.CTkLabel(
            window,
            text="⌘  Command Palette",
            font=("Arial", 24, "bold"),
            text_color="#00ffee"
        ).pack(pady=(22, 12))

        search = ctk.CTkEntry(
            window,
            placeholder_text="Search commands...",
            height=42,
            corner_radius=12
        )
        search.pack(fill="x", padx=25, pady=(0, 12))
        search.focus_set()

        commands = [
            ("Go Home", "home", lambda: self.show_page("home")),
            ("Open Launcher", "launcher", lambda: self.show_page("launcher")),
            ("Open Music", "music", lambda: self.show_page("music")),
            ("Open Timer", "timer", lambda: self.show_page("timer")),
            ("Open To-Do", "todo", lambda: self.show_page("todo")),
            ("Open Statistics", "stats", lambda: self.show_page("stats")),
            ("Open System Log", "system_log", lambda: self.show_page("system_log")),
        ]

        rows = ctk.CTkScrollableFrame(window, corner_radius=15)
        rows.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        def render():
            for widget in rows.winfo_children():
                widget.destroy()

            query = search.get().lower().strip()

            for label, icon_name, command in commands:
                if query and query not in label.lower():
                    continue

                def run(cmd=command):
                    window.destroy()
                    cmd()

                ctk.CTkButton(
                    rows,
                    text=label,
                    image=get_icon(icon_name, 18),
                    compound="left",
                    height=42,
                    corner_radius=10,
                    fg_color="#202727",
                    hover_color="#00aa88",
                    anchor="w",
                    command=run
                ).pack(fill="x", pady=4)

        search.bind("<KeyRelease>", lambda _e: render())
        render()

    # ==================================================
    # PAGE SWITCH
    # ==================================================

    def show_page(self, page_name):

        for page in self.pages.values():
            page.grid_forget()

        self.pages[page_name].grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        for button, page in zip(self.nav_buttons, self.nav_pages):
            if page == page_name:
                button.configure(
                    fg_color="#00aa88",
                    hover_color="#00ccaa"
                )
            else:
                button.configure(
                    fg_color="#171c1c",
                    hover_color="#202b2b",
                    border_color="#273131"
                )


# ==================================================
# 🚀 RUN
# ==================================================

if __name__ == "__main__":

    app = App()

    app.mainloop()
