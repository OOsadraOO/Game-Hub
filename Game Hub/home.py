# ==================================================
# 🏠 HOME PAGE
# ==================================================

import customtkinter as ctk
import psutil
import random

from utils import load_json
from settings import SettingsWindow
from datetime import datetime


class HomePage:

    def __init__(self, app, parent):

        self.app = app
        self.parent = parent

        self.quotes = [

            "Small progress is still progress.",
            "Stay focused and never give up.",
            "Gamers never quit.",
            "Discipline beats motivation.",
            "Push yourself every day.",
            "Victory requires patience.",
            "Level up your life."

        ]

        self.build_ui()

        self.update_clock()
        self.update_performance()

    # ==================================================
    # BUILD UI
    # ==================================================

    def build_ui(self):

        # ==============================================
        # TOP BAR
        # ==============================================

        top_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        top_frame.pack(
            fill="x",
            padx=25,
            pady=15
        )

        ctk.CTkLabel(
            top_frame,
            text="🎮 GameHub Dashboard",
            font=("Arial", 34, "bold"),
            text_color="#00ffee"
        ).pack(
            side="left"
        )

        ctk.CTkButton(
        top_frame,
        text="⚙",
        width=50,
        height=50,
        corner_radius=15,
        command=lambda: SettingsWindow(self.app)
        ).pack(
        side="right"
        )

        # ==============================================
        # CLOCK
        # ==============================================

        self.clock_label = ctk.CTkLabel(
            self.parent,
            text="00:00:00",
            font=("Arial", 55, "bold"),
            text_color="#00ff88"
        )

        self.clock_label.pack(
            pady=(5, 20)
        )

        # ==============================================
        # DASHBOARD GRID
        # ==============================================

        dashboard = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        dashboard.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        # ==============================================
        # ROW 1
        # ==============================================

        row1 = ctk.CTkFrame(
            dashboard,
            fg_color="transparent"
        )

        row1.pack(
            fill="x",
            pady=10
        )

        # Games

        self.games_card = ctk.CTkFrame(
            row1,
          width=220,
          height=130,
            corner_radius=20,
            border_width=2,
            border_color="#00ffee"
        )

        self.games_card.pack(
            side="left",
            padx=10,
            expand=True,
            fill="both"
        )

        ctk.CTkLabel(
            self.games_card,
            text="🎮 Games",
            font=("Arial", 24)
        ).pack(
            pady=15
        )

        self.games_count = ctk.CTkLabel(
            self.games_card,
            text="0",
            font=("Arial", 40, "bold"),
            text_color="#00ffee"
        )

        self.games_count.pack()

        # Tasks

        self.tasks_card = ctk.CTkFrame(
            row1,
            width=220,
            height=130,
            corner_radius=20,
            border_width=2,
            border_color="#ff00ff"
        )

        self.tasks_card.pack(
            side="left",
            padx=10,
            expand=True,
            fill="both"
        )

        ctk.CTkLabel(
            self.tasks_card,
            text="📝 Tasks",
            font=("Arial", 24)
        ).pack(
            pady=15
        )

        self.tasks_count = ctk.CTkLabel(
            self.tasks_card,
            text="0",
            font=("Arial", 40, "bold"),
            text_color="#ff00ff"
        )

        self.tasks_count.pack()

        # CPU

        self.cpu_card = ctk.CTkFrame(
            row1,
           width=220,
           height=130,
            corner_radius=20,
            border_width=2,
            border_color="#00ff88"
        )

        self.cpu_card.pack(
            side="left",
            padx=10,
            expand=True,
            fill="both"
        )

        ctk.CTkLabel(
            self.cpu_card,
            text="🖥 CPU",
            font=("Arial", 24)
        ).pack(
            pady=15
        )

        self.cpu_card_label = ctk.CTkLabel(
            self.cpu_card,
            text="0%",
            font=("Arial", 40, "bold"),
            text_color="#00ff88"
        )

        self.cpu_card_label.pack()

        # RAM

        self.ram_card = ctk.CTkFrame(
            row1,
            width=220,
            height=130,
            corner_radius=20,
            border_width=2,
            border_color="#ffaa00"
        )

        self.ram_card.pack(
            side="left",
            padx=10,
            expand=True,
            fill="both"
        )

        ctk.CTkLabel(
            self.ram_card,
            text="💾 RAM",
            font=("Arial", 24)
        ).pack(
            pady=15
        )

        self.ram_card_label = ctk.CTkLabel(
            self.ram_card,
            text="0%",
            font=("Arial", 40, "bold"),
            text_color="#ffaa00"
        )

        self.ram_card_label.pack()

        # ==============================================
        # PERFORMANCE PANEL
        # ==============================================

        performance_frame = ctk.CTkFrame(
            dashboard,
            corner_radius=20
        )

        performance_frame.pack(
            fill="x",
            pady=15
        )

        ctk.CTkLabel(
            performance_frame,
            text="📊 Performance Monitor",
            font=("Arial", 24, "bold")
        ).pack(
            pady=15
        )

        self.cpu_label = ctk.CTkLabel(
            performance_frame,
            text="CPU: 0%"
        )

        self.cpu_label.pack()

        self.cpu_bar = ctk.CTkProgressBar(
            performance_frame,
            width=700
        )

        self.cpu_bar.pack(
            pady=5
        )

        self.ram_label = ctk.CTkLabel(
            performance_frame,
            text="RAM: 0%"
        )

        self.ram_label.pack()

        self.ram_bar = ctk.CTkProgressBar(
            performance_frame,
            width=700
        )

        self.ram_bar.pack(
            pady=(5, 20)
        )

        # ==============================================
        # BOTTOM ROW
        # ==============================================

        bottom_row = ctk.CTkFrame(
            dashboard,
            fg_color="transparent"
        )

        bottom_row.pack(
            fill="x",
            pady=10
        )

        # Quote

        quote_frame = ctk.CTkFrame(
            bottom_row,
            corner_radius=20
        )

        quote_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10
        )

        ctk.CTkLabel(
            quote_frame,
            text="💬 Daily Quote",
            font=("Arial", 22, "bold")
        ).pack(
            pady=10
        )

        random_quote = random.choice(
            self.quotes
        )

        ctk.CTkLabel(
            quote_frame,
            text=random_quote,
            wraplength=400,
            font=("Arial", 18)
        ).pack(
            pady=15
        )

        # Weather

        weather_frame = ctk.CTkFrame(
            bottom_row,
            corner_radius=20
        )

        weather_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10
        )

        ctk.CTkLabel(
            weather_frame,
            text="🌤 Weather",
            font=("Arial", 22, "bold")
        ).pack(
            pady=10
        )

        ctk.CTkLabel(
            weather_frame,
            text="Coming Soon",
            font=("Arial", 18)
        ).pack(
            pady=15
        )

    # ==================================================
    # CLOCK
    # ==================================================

    def update_clock(self):

        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        self.clock_label.configure(
            text=current_time
        )

        self.parent.after(
            1000,
            self.update_clock
        )

    # ==================================================
    # PERFORMANCE
    # ==================================================

    def update_performance(self):

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory().percent

        self.cpu_label.configure(
            text=f"CPU: {cpu}%"
        )

        self.cpu_bar.set(
            cpu / 100
        )

        self.ram_label.configure(
            text=f"RAM: {ram}%"
        )

        self.ram_bar.set(
            ram / 100
        )

        self.cpu_card_label.configure(
            text=f"{cpu}%"
        )

        self.ram_card_label.configure(
            text=f"{ram}%"
        )
        try:

            games = load_json(
            "data/games.json"
            )

            self.games_count.configure(
                text=str(len(games))
            )

        except:
            pass

        try:

            tasks = load_json(
                "data/todo.json"
            )

            self.tasks_count.configure(
                text=str(len(tasks))
            )

        except:
            pass
        self.parent.after(
            1000,
            self.update_performance
        )
