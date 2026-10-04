# ==================================================
# 🏠 HOME PAGE
# ==================================================

import customtkinter as ctk
from icons import get_icon
import psutil
import random
from performance import get_gpu_usage, get_gpu_name
from session import GamingSessionWindow

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
        # TOP BAR + CLOCK

        top_frame = ctk.CTkFrame(
            self.parent,
            height=78,
            corner_radius=18,
            border_width=1,
            border_color="#252d2d"
        )

        top_frame.pack(
            fill="x",
            padx=20,
            pady=(4, 8)
        )
        top_frame.pack_propagate(False)

        ctk.CTkButton(
            top_frame,
            text="Session",
            image=get_icon("session", 20),
            compound="left",
            width=115,
            height=42,
            corner_radius=12,
            fg_color="#202727",
            hover_color="#00aa88",
            font=("Arial", 12, "bold"),
            command=lambda: GamingSessionWindow(self.app)
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            top_frame,
            text="",
            image=get_icon("settings", 18),
            width=48,
            height=42,
            corner_radius=12,
            fg_color="#202727",
            hover_color="#00aa88",
            font=("Arial", 18, "bold"),
            command=lambda: SettingsWindow(self.app)
        ).pack(side="right", padx=10)

        self.clock_label = ctk.CTkLabel(
            top_frame,
            text="00:00:00",
            font=("Arial", 34, "bold"),
            text_color="#00ff88"
        )
        self.clock_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        ctk.CTkLabel(
            top_frame,
            text="GameHub",
            font=("Arial", 11, "bold"),
            text_color="#00ffee"
        ).place(
            relx=0.5,
            rely=0.83,
            anchor="center"
        )

        # DASHBOARD GRID
        # ==============================================

        dashboard = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        dashboard.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=0
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
            pady=(0, 4)
        )

        # Games

        self.games_card = ctk.CTkFrame(
            row1,
          width=220,
          height=130,
            corner_radius=20,
            border_width=1,
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
            text="Games",
            font=("Arial", 20, "bold")
        ).pack(
            pady=(10, 5)
        )

        self.games_count = ctk.CTkLabel(
            self.games_card,
            text="0",
            font=("Arial", 36, "bold"),
            text_color="#00ffee"
        )

        self.games_count.pack()

        # CPU

        self.cpu_card = ctk.CTkFrame(
            row1,
           width=220,
           height=130,
            corner_radius=20,
            border_width=1,
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
            text="CPU",
            font=("Arial", 24)
        ).pack(
            pady=(9, 5)
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
            border_width=1,
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
            text="RAM",
            font=("Arial", 24)
        ).pack(
            pady=(9, 5)
        )

        self.ram_card_label = ctk.CTkLabel(
            self.ram_card,
            text="0%",
            font=("Arial", 40, "bold"),
            text_color="#ffaa00"
        )

        self.ram_card_label.pack()

        # GPU

        self.gpu_card = ctk.CTkFrame(
            row1,
            width=220,
            height=130,
            corner_radius=20,
            border_width=1,
            border_color="#aa66ff"
        )
        self.gpu_card.pack(
            side="left",
            padx=10,
            expand=True,
            fill="both"
        )

        ctk.CTkLabel(
            self.gpu_card,
            text="GPU",
            font=("Arial", 24)
        ).pack(pady=(9, 5))

        self.gpu_card_label = ctk.CTkLabel(
            self.gpu_card,
            text="—",
            font=("Arial", 40, "bold"),
            text_color="#aa66ff"
        )
        self.gpu_card_label.pack()

        # ==============================================
        # ✨ CARD HOVER
        # ==============================================

        dashboard_cards = [
            self.games_card,
            self.cpu_card,
            self.ram_card,
            self.gpu_card
        ]

        for card in dashboard_cards:
            normal_border = card.cget("border_color")
            normal_fg = card.cget("fg_color")
            card.bind(
                "<Enter>",
                lambda _e, c=card: c.configure(
                    fg_color="#171d1d",
                    border_width=2
                ),
                add="+"
            )
            card.bind(
                "<Leave>",
                lambda _e, c=card, fg=normal_fg, bc=normal_border: c.configure(
                    fg_color=fg,
                    border_width=1,
                    border_color=bc
                ),
                add="+"
            )

        # ==============================================
        # LIVE PERFORMANCE PANEL
        # ==============================================

        performance_frame = ctk.CTkFrame(
            dashboard,
            corner_radius=20,
            border_width=1,
            border_color="#252d2d"
        )
        performance_frame.pack(fill="both", expand=True, pady=4)

        performance_header = ctk.CTkFrame(
            performance_frame,
            fg_color="transparent"
        )
        performance_header.pack(fill="x", padx=20, pady=(8, 2))

        ctk.CTkLabel(
            performance_header,
            text="Live System Monitor",
            image=get_icon("monitor", 20),
            compound="left",
            font=("Arial", 22, "bold")
        ).pack(side="left")

        self.gpu_status_label = ctk.CTkLabel(
            performance_header,
            text="GPU: detecting...",
            font=("Arial", 12),
            text_color="gray"
        )
        self.gpu_status_label.pack(side="right")

        self.performance_canvas = ctk.CTkCanvas(
            performance_frame,
            height=135,
            bg="#111111",
            highlightthickness=0
        )
        self.performance_canvas.pack(fill="both", expand=True, padx=18, pady=(0, 6))

        self.performance_history = {
            "CPU": [0] * 60,
            "RAM": [0] * 60,
            "GPU": [0] * 60
        }

        # ==============================================
        # BOTTOM ROW
        # ==============================================

        bottom_row = ctk.CTkFrame(
            dashboard,
            fg_color="transparent"
        )

        bottom_row.pack(
            fill="x",
            pady=5
        )

        # Quote

        quote_frame = ctk.CTkFrame(
            bottom_row,
            corner_radius=20,
            border_width=1,
            border_color="#252d2d"
        )

        quote_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 6)
        )
        quote_frame.configure(height=132)
        quote_frame.pack_propagate(False)

        ctk.CTkLabel(
            quote_frame,
            text="Daily Quote",
            image=get_icon("quote", 20),
            compound="left",
            font=("Arial", 22, "bold")
        ).pack(
            pady=(8, 4)
        )

        random_quote = random.choice(
            self.quotes
        )

        ctk.CTkLabel(
            quote_frame,
            text=random_quote,
            wraplength=400,
            font=("Arial", 18, "bold")
        ).pack(
            pady=(8, 4)
        )

        # Quick Actions

        quick_frame = ctk.CTkFrame(
            bottom_row,
            height=145,
            corner_radius=20,
            border_width=1,
            border_color="#252d2d"
        )

        quick_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(6, 0)
        )
        quick_frame.pack_propagate(False)

        ctk.CTkLabel(
            quick_frame,
            text="Quick Actions",
            font=("Arial", 18, "bold")
        ).pack(pady=(10, 7))

        quick_buttons = ctk.CTkFrame(
            quick_frame,
            fg_color="transparent"
        )
        quick_buttons.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 8)
        )

        quick_buttons.grid_columnconfigure((0, 1, 2), weight=1, uniform="quick")
        quick_buttons.grid_rowconfigure(0, weight=1)

        quick_actions = (
            ("Session", "session", lambda: GamingSessionWindow(self.app)),
            ("Statistics", "stats", lambda: self.app.show_page("stats")),
            ("Music", "music", lambda: self.app.show_page("music"))
        )

        for column, (label, icon_name, command) in enumerate(quick_actions):
            ctk.CTkButton(
                quick_buttons,
                text=label,
                image=get_icon(icon_name, 17),
                compound="left",
                height=54,
                corner_radius=12,
                fg_color="#202727",
                hover_color="#00aa88",
                font=("Arial", 12, "bold"),
                command=command
            ).grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=4
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
        gpu = get_gpu_usage()

        self.cpu_card_label.configure(text=f"{cpu:.0f}%")
        self.ram_card_label.configure(text=f"{ram:.0f}%")

        gpu_name = get_gpu_name()

        if gpu is None:
            self.gpu_card_label.configure(text="—")
            status = "GPU: usage unavailable"
            if gpu_name:
                status = f"GPU: {gpu_name} • usage unavailable"
            self.gpu_status_label.configure(text=status)
        else:
            self.gpu_card_label.configure(text=f"{gpu:.0f}%")
            if gpu_name:
                self.gpu_status_label.configure(
                    text=f"GPU: {gpu_name} • {gpu:.0f}%"
                )
            else:
                self.gpu_status_label.configure(text=f"GPU: {gpu:.0f}%")

        for key, value in (
            ("CPU", cpu),
            ("RAM", ram),
            ("GPU", gpu if gpu is not None else 0)
        ):
            self.performance_history[key].append(float(value))
            self.performance_history[key] = self.performance_history[key][-60:]

        self.draw_performance_chart()

        try:
            games = load_json("data/games.json")
            self.games_count.configure(text=str(len(games)))
        except Exception:
            pass

        self.parent.after(1200, self.update_performance)

    def draw_performance_chart(self):

        canvas = self.performance_canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 500)
        height = max(canvas.winfo_height(), 175)

        left, right, top, bottom = 38, 15, 12, 28
        plot_w = width - left - right
        plot_h = height - top - bottom

        for percent in (0, 25, 50, 75, 100):
            y = top + plot_h * (1 - percent / 100)
            canvas.create_line(left, y, width - right, y, fill="#222929")
            canvas.create_text(
                18, y, text=str(percent),
                fill="#666666", font=("Arial", 8)
            )

        for name, values, label_color in (
            ("CPU", self.performance_history["CPU"], "#00ffee"),
            ("RAM", self.performance_history["RAM"], "#ffaa00"),
            ("GPU", self.performance_history["GPU"], "#aa66ff")
        ):
            points = []
            step = plot_w / max(1, len(values) - 1)

            for index, value in enumerate(values):
                x = left + index * step
                y = top + plot_h * (1 - max(0, min(100, value)) / 100)
                points.extend((x, y))

            canvas.create_line(
                *points, fill=label_color, width=2, smooth=True
            )

        legend_x = width - 245
        for index, (name, label_color) in enumerate((
            ("CPU", "#00ffee"),
            ("RAM", "#ffaa00"),
            ("GPU", "#aa66ff")
        )):
            x = legend_x + index * 72
            canvas.create_oval(
                x, 7, x + 8, 15,
                fill=label_color, outline=""
            )
            canvas.create_text(
                x + 14, 11, text=name,
                fill="#aaaaaa", font=("Arial", 9), anchor="w"
            )
