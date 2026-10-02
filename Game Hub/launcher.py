# ==================================================
# 🎮 GAME LAUNCHER
# ==================================================

import customtkinter as ctk
import subprocess
import os

from tkinter import filedialog

from utils import load_json, save_json


class GameLauncher:

    def __init__(self, app, parent):

        self.app = app
        self.parent = parent

        self.games = load_json(
            "data/games.json"
        )

        self.stats = load_json(
            "data/game_stats.json"
        )

        self.build_ui()
        self.render_games()

    # ==================================================
    # 🎨 UI
    # ==================================================

    def build_ui(self):

        ctk.CTkLabel(
            self.parent,
            text="🎮 Game Launcher",
            font=("Arial", 32, "bold")
        ).pack(
            pady=(20, 10)
        )

        self.count_label = ctk.CTkLabel(
            self.parent,
            text=f"Games Installed: {len(self.games)}",
            font=("Arial", 18)
        )

        self.count_label.pack(
            pady=(0, 10)
        )

        ctk.CTkButton(
            self.parent,
            text="➕ Add Game",
            width=200,
            height=45,
            command=self.add_game
        ).pack(
            pady=10
        )

        self.games_frame = ctk.CTkScrollableFrame(
            self.parent,
            width=1000,
            height=500
        )

        self.games_frame.pack(
            padx=20,
            pady=20,
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
    # 📜 RENDER
    # ==================================================

    def render_games(self):

        self.count_label.configure(
            text=f"Games Installed: {len(self.games)}"
        )

        for widget in self.games_frame.winfo_children():
            widget.destroy()

        for game in self.games:

            row = ctk.CTkFrame(
                self.games_frame,
                corner_radius=20,
                border_width=1
            )

            row.pack(
                fill="x",
                pady=8,
                padx=5
            )

            info_frame = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )

            info_frame.pack(
                side="left",
                padx=15,
                pady=10
            )

            ctk.CTkLabel(
                info_frame,
                text=f"🎮 {game['name']}",
                font=("Arial", 18, "bold")
            ).pack(
                anchor="w"
            )

            ctk.CTkLabel(
                info_frame,
                text=game["path"],
                font=("Arial", 12),
                text_color="gray"
            ).pack(
                anchor="w"
            )

            launches = self.stats.get(
                game["name"],
                0
            )

            ctk.CTkLabel(
                row,
                text=f"🚀 {launches}",
                font=("Arial", 16)
            ).pack(
                side="left",
                padx=20
            )

            ctk.CTkButton(
                row,
                text="▶ Play",
                width=120,
                command=lambda g=game:
                self.launch_game(g)
            ).pack(
                side="right",
                padx=10
            )

            ctk.CTkButton(
                row,
                text="🗑",
                width=50,
                fg_color="#aa2222",
                hover_color="#cc3333",
                command=lambda g=game:
                self.delete_game(g)
            ).pack(
                side="right",
                padx=10
            )

    # ==================================================
    # ▶ LAUNCH
    # ==================================================

    def launch_game(self, game):

        try:

            path = game["path"]

            if "VALORANT" in path.upper():

                riot_path = (
                    r"C:\Riot Games\Riot Client\RiotClientServices.exe"
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

            self.render_games()

        except Exception as e:

            print(
                "Launch Error:",
                e
            )