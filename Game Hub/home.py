# ==================================================
# 🏠 HOME PAGE (PRO VERSION)
# ==================================================

import customtkinter as ctk
import psutil
import random

from utils import load_json
from datetime import datetime
from settings import SettingsWindow


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

    def build_ui(self):

        top_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        top_frame.pack(fill="x", padx=25, pady=15)

        ctk.CTkLabel(
            top_frame,
            text="🎮 GameHub Dashboard",
            font=("Arial", 34, "bold"),
            text_color="#00ffee"
        ).pack(side="left")

        ctk.CTkButton(
            top_frame,
            text="⚙",
            width=50,
            height=50,
            corner_radius=15,
            command=lambda: SettingsWindow(self.app)
        ).pack(side="right")

        self.clock_label = ctk.CTkLabel(
            self.parent,
            text="00:00:00",
            font=("Arial", 55, "bold"),
            text_color="#00ff88"
        )
        self.clock_label.pack(pady=(5, 20))

        dashboard = ctk.CTkFrame(self.parent, fg_color="transparent")
        dashboard.pack(fill="both", expand=True, padx=25, pady=10)

        row1 = ctk.CTkFrame(dashboard, fg_color="transparent")
        row1.pack(fill="x", pady=10)

        cards = [
            ("🎮 Games", "#00ffee"),
            ("📝 Tasks", "#ff00ff"),
            ("🖥 CPU", "#00ff88"),
            ("💾 RAM", "#ffaa00")
        ]

        self.card_labels = []

        for title, color in cards:
            card = ctk.CTkFrame(
                row1,
                corner_radius=20,
                border_width=2,
                border_color=color
            )
            card.pack(side="left", padx=10, expand=True, fill="both")

            ctk.CTkLabel(card, text=title, font=("Arial", 24)).pack(pady=15)

            lbl = ctk.CTkLabel(
                card,
                text="0",
                font=("Arial", 40, "bold"),
                text_color=color
            )
            lbl.pack()

            self.card_labels.append(lbl)

        self.games_count = self.card_labels[0]
        self.tasks_count = self.card_labels[1]
        self.cpu_card_label = self.card_labels[2]
        self.ram_card_label = self.card_labels[3]

        performance = ctk.CTkFrame(dashboard, corner_radius=20)
        performance.pack(fill="x", pady=15)

        ctk.CTkLabel(
            performance,
            text="📊 Performance Monitor",
            font=("Arial", 24, "bold")
        ).pack(pady=15)

        self.cpu_label = ctk.CTkLabel(performance, text="CPU: 0%")
        self.cpu_label.pack()

        self.cpu_bar = ctk.CTkProgressBar(performance, width=700)
        self.cpu_bar.pack(pady=5)

        self.ram_label = ctk.CTkLabel(performance, text="RAM: 0%")
        self.ram_label.pack()

        self.ram_bar = ctk.CTkProgressBar(performance, width=700)
        self.ram_bar.pack(pady=(5, 20))

    def update_clock(self):

        self.clock_label.configure(
            text=datetime.now().strftime("%H:%M:%S")
        )

        self.parent.after(1000, self.update_clock)

    def update_performance(self):

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        self.cpu_label.configure(text=f"CPU: {cpu}%")
        self.ram_label.configure(text=f"RAM: {ram}%")

        self.cpu_bar.set(cpu / 100)
        self.ram_bar.set(ram / 100)

        self.cpu_card_label.configure(text=f"{cpu}%")
        self.ram_card_label.configure(text=f"{ram}%")

        try:
            games = load_json("data/games.json")
            self.games_count.configure(text=str(len(games)))
        except:
            pass

        try:
            tasks = load_json("data/todo.json")
            self.tasks_count.configure(text=str(len(tasks)))
        except:
            pass

        self.parent.after(1000, self.update_performance)