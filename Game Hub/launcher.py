# ==================================================
# 🎮 GAME LAUNCHER
# ==================================================

import customtkinter as ctk
import subprocess
import os
import win32gui
import win32ui
import win32con
from datetime import datetime

from PIL import Image, ImageTk
from win32api import GetSystemMetrics
from tkinter import filedialog
from tkinter import messagebox
from utils import load_json, save_json


class GameLauncher:

    def __init__(self, app, parent):

        self.app = app
        self.search_var = ctk.StringVar()
        self.parent = parent
        self.icon_cache = {}
        
        self.games = load_json(
            "data/games.json"
        )

        self.stats = load_json(
            "data/game_stats.json"
        )

        self.build_ui()
        self.render_games()

    # ==================================================
    # ✨ HOVER EFFECT
    # ==================================================

    def _bind_hover(self, widget, normal, hover, border_normal=None, border_hover=None):

        def on_enter(_event=None):
            try:
                widget.configure(fg_color=hover)
                if border_hover is not None:
                    widget.configure(border_color=border_hover)
            except Exception:
                pass

        def on_leave(_event=None):
            try:
                widget.configure(fg_color=normal)
                if border_normal is not None:
                    widget.configure(border_color=border_normal)
            except Exception:
                pass

        widget.bind("<Enter>", on_enter, add="+")
        widget.bind("<Leave>", on_leave, add="+")

    def _bind_card_hover(self, card, children):

        normal = "#1b1b1b"
        hover = "#202525"
        border_normal = "#2c2c2c"
        border_hover = "#00ffee"

        self._bind_hover(
            card,
            normal,
            hover,
            border_normal,
            border_hover
        )

        for child in children:
            try:
                child.bind("<Enter>", lambda _e, c=card: c.configure(fg_color="#202525", border_color="#00ffee"), add="+")
                child.bind("<Leave>", lambda _e, c=card: c.configure(fg_color="#1b1b1b", border_color="#2c2c2c"), add="+")
            except Exception:
                pass

    # ==================================================
    # 🎨 UI
    # ==================================================

    def build_ui(self):

        ctk.CTkLabel(
            self.parent,
            text="🎮 Game Launcher",
            font=("Arial", 32, "bold"),
            text_color="#00ffee"
        ).pack(
            pady=(12, 8)
        )
        
        # ==================================================
        # HEADER
        # ==================================================

        header = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            pady=(8,10)
        )

        # ---------------- Search ----------------

        self.search_entry = ctk.CTkEntry(

            header,

            width=360,

            height=42,

            textvariable=self.search_var,

            placeholder_text="🔍  Search games..."
        )

        self.search_entry.pack(
            side="left",
            padx=5
        )
        # ==================================================
        # 📊 STATS CARDS
        # ==================================================

        stats_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        stats_frame.pack(
            fill="x",
            padx=20,
            pady=(2, 10)
        )

        # ---------- Games ----------

        games_card = ctk.CTkFrame(
            stats_frame,
            width=125,
            height=72,
            corner_radius=16,
            border_width=1,
            border_color="#2c2c2c",
            fg_color="#181b1b"
        )

        games_card.pack(
            side="left",
            padx=6
        )

        games_card.pack_propagate(False)

        ctk.CTkLabel(
            games_card,
            text="🎮 Games",
            font=("Arial",12)
        ).pack(pady=(8,0))

        self.total_games_label = ctk.CTkLabel(
            games_card,
            text="0",
            font=("Arial",24,"bold"),
            text_color="#00ffee"
        )

        self.total_games_label.pack()


        # ---------- Launches ----------

        launch_card = ctk.CTkFrame(
            stats_frame,
            width=125,
            height=72,
            corner_radius=16,
            border_width=1,
            border_color="#2c2c2c",
            fg_color="#181b1b"
        )

        launch_card.pack(
            side="left",
            padx=6
        )

        launch_card.pack_propagate(False)

        ctk.CTkLabel(
            launch_card,
            text="🚀 Launches",
            font=("Arial",12)
        ).pack(pady=(8,0))

        self.total_launches_label = ctk.CTkLabel(
            launch_card,
            text="0",
            font=("Arial",24,"bold"),
            text_color="#ffb000"
        )

        self.total_launches_label.pack()


        # ---------- Favorites ----------

        favorite_card = ctk.CTkFrame(
            stats_frame,
            width=120,
            height=70,
            corner_radius=15,
            fg_color="#1b1b1b"
        )

        favorite_card.pack(
            side="left",
            padx=6
        )

        favorite_card.pack_propagate(False)

        ctk.CTkLabel(
            favorite_card,
            text="⭐ Favorites",
            font=("Arial",12)
        ).pack(pady=(8,0))

        self.favorite_label = ctk.CTkLabel(
            favorite_card,
            text="0",
            font=("Arial",24,"bold"),
            text_color="#ff44ff"
        )

        self.favorite_label.pack()


        # ---------- Last Played ----------

        last_card = ctk.CTkFrame(
            stats_frame,
            width=195,
            height=72,
            corner_radius=16,
            border_width=1,
            border_color="#2c2c2c",
            fg_color="#181b1b" 
        )

        last_card.pack(
            side="right",
            padx=6
        )

        last_card.pack_propagate(False)

        ctk.CTkLabel(
            last_card,
            text="🕒 Last Played",
            font=("Arial",12)
        ).pack(pady=(8,0))

        self.last_game_label = ctk.CTkLabel(
            last_card,
            text="None",
            font=("Arial",18,"bold"),
            text_color="#55ff88"
        )

        self.last_game_label.pack()

        self.search_entry.bind(
            "<KeyRelease>",
            lambda e: self.render_games()
        )

        # ---------------- Add ----------------

        ctk.CTkButton(

            header,

            text="➕ Add Game",

            width=145,

            height=42,
            corner_radius=12,
            font=("Arial", 13, "bold"),
            hover_color="#00ccaa",

            command=self.add_game

        ).pack(
            side="right",
            padx=5
        )

        # ---------------- Refresh ----------------

        ctk.CTkButton(

            header,

            text="↻",

            width=46,

            height=42,
            corner_radius=12,
            font=("Arial", 18, "bold"),

            command=self.render_games

        ).pack(
            side="right",
            padx=5
        )

        self.games_frame = ctk.CTkScrollableFrame(
            self.parent,
            width=1000,
            height=500,
            corner_radius=18
        )

        self.games_frame.pack(
            padx=20,
            pady=(8, 20),
            fill="both",
            expand=True
        )

    # ==================================================
    # ➕ ADD GAME
    # ==================================================

    def add_game(self):

        file_path = filedialog.askopenfilename(
            title="Select Game EXE",
            filetypes=[
                ("Executable Files", "*.exe")
            ]
        )

        if not file_path:
            return

        game_name = os.path.basename(
            file_path
        )

        self.games.append({
            "name": game_name,
            "path": file_path
        })

        save_json(
            "data/games.json",
            self.games
        )

        self.render_games()

    # ==================================================
    # ❌ DELETE GAME
    # ==================================================

    def delete_game(self, game):

        self.games.remove(game)

        save_json(
            "data/games.json",
            self.games
        )

        self.render_games()
    
    # ==================================================
    # 🖼 GET EXE ICON
    # ==================================================

    def get_icon(self, exe_path):

        try:

            large, small = win32gui.ExtractIconEx(exe_path, 0)

            if not large:
                return None

            hicon = large[0]

            ico_x = GetSystemMetrics(win32con.SM_CXICON)
            ico_y = GetSystemMetrics(win32con.SM_CYICON)

            hdc = win32ui.CreateDCFromHandle(
                win32gui.GetDC(0)
            )

            hbmp = win32ui.CreateBitmap()

            hbmp.CreateCompatibleBitmap(
                hdc,
                ico_x,
                ico_y
            )

            hdc_mem = hdc.CreateCompatibleDC()

            hdc_mem.SelectObject(hbmp)

            win32gui.DrawIconEx(
                hdc_mem.GetHandleOutput(),
                0,
                0,
                hicon,
                ico_x,
                ico_y,
                0,
                None,
                win32con.DI_NORMAL
            )

            bmpinfo = hbmp.GetInfo()
            bmpstr = hbmp.GetBitmapBits(True)

            image = Image.frombuffer(
                "RGBA",
                (
                    bmpinfo["bmWidth"],
                    bmpinfo["bmHeight"]
                ),
                bmpstr,
                "raw",
                "BGRA",
                0,
                1
            )

            win32gui.DestroyIcon(hicon)

            return ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(48,48)
            )

        except:
            return None
    # ==================================================
    # 🃏 GAME CARD
    # ==================================================

    def create_game_card(self, game):

        card = ctk.CTkFrame(
            self.games_frame,
            corner_radius=20,
            border_width=1,
            border_color="#2c2c2c",
            fg_color=("#1b1b1b", "#1b1b1b")
        )

        card.pack(
            fill="x",
            padx=8,
            pady=7
        )

        # =========================
        # TOP
        # =========================

        top = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        top.pack(
            fill="x",
            padx=15,
            pady=(15, 10)
        )

        icon_image = self.get_icon(
            game["path"]
        )

        if icon_image:

            icon = ctk.CTkLabel(
                top,
                image=icon_image,
                text=""
            )

            icon.image = icon_image

        else:

            icon = ctk.CTkLabel(
                top,
                text="🎮",
                font=("Arial",36)
            )

        icon.pack(side="left")

        # INFO

        info = ctk.CTkFrame(
            top,
            fg_color="transparent"
        )

        info.pack(
            side="left",
            padx=15,
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            info,
            text=game["name"],
            font=("Arial", 22, "bold")
        ).pack(anchor="w")

        short_path = game["path"]

        if len(short_path) > 45:
            short_path = "..." + short_path[-42:]

        ctk.CTkLabel(
            info,
            text=short_path,
            font=("Arial", 12),
            text_color="gray"
        ).pack(anchor="w")

        # FAVORITE

        if "favorite" not in game:
            game["favorite"] = False

        fav_text = "⭐" if game["favorite"] else "☆"

        fav_btn = ctk.CTkButton(
            top,
            text=fav_text,
            width=40,
            fg_color="transparent",
            hover_color=("#333333", "#333333"),
            command=lambda g=game: self.toggle_favorite(g)
        )

        fav_btn.pack(side="right")

        # =========================
        # STATS
        # =========================

        stats = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        stats.pack(
            fill="x",
            padx=20,
            pady=5
        )

        launches = self.stats.get(
            game["name"],
            0
        )

        last_played = game.get(
            "last_played",
            "Never"
        )

        ctk.CTkLabel(
            stats,
            text=f"🚀  {launches}",
            font=("Arial", 16, "bold"),
            text_color="#ffb000"
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            stats,
            text=f"🕒 Last Played: {last_played}",
            font=("Arial", 14)
        ).pack(side="left", padx=25)

        # =========================
        # BUTTONS
        # =========================

        buttons = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=15,
            pady=(10, 15)
        )

        ctk.CTkButton(
            buttons,
            text="▶ Play",
            width=120,
            height=38,
            corner_radius=11,
            font=("Arial", 13, "bold"),
            fg_color="#00aa88",
            hover_color="#00ccaa",
            command=lambda g=game: self.launch_game(g)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons,
            text="✏ Edit",
            width=100,
            height=38,
            corner_radius=11,
            font=("Arial", 13, "bold"),
            fg_color="#3a3f42",
            hover_color="#50575b",
            command=lambda g=game: self.edit_game(g)
        ).pack(side="left", padx=5)

        delete_button = ctk.CTkButton(
            buttons,
            text="🗑 Delete",
            width=100,
            height=38,
            corner_radius=11,
            font=("Arial", 13, "bold"),
            fg_color="#9e2b35",
            hover_color="#c63b46",
            command=lambda g=game: self.confirm_delete(g)
        )
        delete_button.pack(side="right", padx=5)

        self._bind_card_hover(
            card,
            [top, info, icon, stats, buttons]
        )

        # ==================================================
        # ✏ EDIT
        # ==================================================

    def edit_game(self, game):

        window = ctk.CTkToplevel(self.app)

        window.title("Edit Game")

        window.geometry("500x250")

        ctk.CTkLabel(
            window,
            text="Game Name"
        ).pack(pady=(15, 5))

        name_entry = ctk.CTkEntry(
            window,
            width=350
        )

        name_entry.insert(0, game["name"])

        name_entry.pack()

        ctk.CTkLabel(
            window,
            text="Game Path"
        ).pack(pady=(15, 5))

        path_entry = ctk.CTkEntry(
            window,
            width=350
        )

        path_entry.insert(0, game["path"])

        path_entry.pack()

        def save_changes():

            old_name = game["name"]

            new_name = name_entry.get()

            game["name"] = new_name
            game["path"] = path_entry.get()

            if old_name != new_name:

                if old_name in self.stats:
                    self.stats[new_name] = self.stats.pop(old_name)

            save_json(
                "data/games.json",
                self.games
            )

            save_json(
                "data/game_stats.json",
                self.stats
            )

            self.render_games()

            window.destroy()


        ctk.CTkButton(
            window,
            text="Save",
            command=save_changes
        ).pack(pady=20)

    # ==========================================
    # 🗑 CONFIRM DELETE
    # ==========================================

    def confirm_delete(self, game):
            
        answer = messagebox.askyesno(
            "Delete Game",
            f"Delete {game['name']} ?"
        )

        if answer:
            self.delete_game(game)


    # ==========================================
    # 🗑 DELETE GAME
    # ==========================================

    def delete_game(self, game):

        self.games.remove(game)

        save_json(
            "data/games.json",
            self.games
        )

        self.render_games()
    # ==================================================
    # 📜 RENDER
    # ==================================================

    def render_games(self):

        latest_game = None

        for game in self.games:

            if "last_played" not in game:
                continue

            if latest_game is None:
                latest_game = game

            elif game["last_played"] > latest_game["last_played"]:
                latest_game = game

        if latest_game:

            self.last_game_label.configure(
                text=f"{latest_game['name']}"
            )

        else:

            self.last_game_label.configure(
                text="None"
            )
        # ==========================
        # Statistics
        # ==========================

        self.total_games_label.configure(
            text=str(len(self.games))
        )

        self.total_launches_label.configure(
            text=str(sum(self.stats.values()))
        )

        favorites = sum(
            1
            for game in self.games
            if game.get("favorite", False)
        )

        self.favorite_label.configure(
            text=str(favorites)
        )


        for widget in self.games_frame.winfo_children():
            widget.destroy()

        search = self.search_var.get().lower()

        games = sorted(
            self.games,
            key=lambda g: not g.get("favorite", False)
        )

        for game in games:

            if search not in game["name"].lower():
                continue

            self.create_game_card(game)
            
        
    def toggle_favorite(self, game):

        game["favorite"] = not game.get("favorite", False)

        save_json(
            "data/games.json",
            self.games
        )

        self.render_games()
    # ==================================================
    # ▶ LAUNCH
    # ==================================================

    def launch_game(self, game):

        try:

            path = game["path"]

            if "VALORANT" in path.upper():

                riot_path = (
                    r"C:Riot GamesRiot ClientRiotClientServices.exe"
                )

                subprocess.Popen([
                    riot_path,
                    "--launch-product=valorant",
                    "--launch-patchline=live"
                ])

            else:

                subprocess.Popen(
                    path,
                    shell=True
                )

            game_name = game["name"]

            if game_name not in self.stats:
                self.stats[game_name] = 0

            self.stats[game_name] += 1

            save_json(
                "data/game_stats.json",
                self.stats
            )
            game["last_played"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            save_json(
                "data/games.json",
                self.games
            )
            self.render_games()

        except Exception as e:

            print(
                "Launch Error:",
                e
            )
