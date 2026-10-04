import customtkinter as ctk
from utils import load_json


class StatsPage:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.build_ui()
        self.refresh()

    def build_ui(self):
        ctk.CTkLabel(
            self.parent, text="📊  Gaming Statistics",
            font=("Arial", 32, "bold"), text_color="#00ffee"
        ).pack(anchor="w", padx=32, pady=(24, 4))

        ctk.CTkLabel(
            self.parent, text="Your GameHub activity at a glance",
            font=("Arial", 13), text_color="gray"
        ).pack(anchor="w", padx=32, pady=(0, 18))

        summary = ctk.CTkFrame(self.parent, fg_color="transparent")
        summary.pack(fill="x", padx=25, pady=5)

        self.total_time = self._summary_card("⏱ Total Playtime", summary)
        self.total_launches = self._summary_card("🚀 Total Launches", summary)
        self.favorite_count = self._summary_card("⭐ Favorites", summary)

        card = ctk.CTkFrame(
            self.parent, corner_radius=20,
            border_width=1, border_color="#252d2d"
        )
        card.pack(fill="both", expand=True, padx=32, pady=18)

        ctk.CTkLabel(
            card, text="Playtime by Game",
            font=("Arial", 20, "bold")
        ).pack(anchor="w", padx=22, pady=(18, 5))

        self.chart = ctk.CTkCanvas(
            card, bg="#111111", highlightthickness=0
        )
        self.chart.pack(fill="both", expand=True, padx=15, pady=15)
        self.chart.bind("<Configure>", lambda _e: self.draw_chart())

    def _summary_card(self, title, parent):
        card = ctk.CTkFrame(
            parent, height=85, corner_radius=16,
            border_width=1, border_color="#2c2c2c", fg_color="#181b1b"
        )
        card.pack(side="left", fill="x", expand=True, padx=6)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=title, font=("Arial", 12)).pack(pady=(10, 0))
        label = ctk.CTkLabel(
            card, text="0", font=("Arial", 24, "bold"), text_color="#00ffee"
        )
        label.pack()
        return label

    def refresh(self):
        games = load_json("data/games.json") or []
        stats = load_json("data/game_stats.json") or {}
        playtime = load_json("data/playtime.json") or {}

        total_seconds = sum(int(value or 0) for value in playtime.values())
        hours, remainder = divmod(total_seconds, 3600)

        self.total_time.configure(text=f"{hours}h {remainder // 60:02d}m")
        self.total_launches.configure(text=str(sum(stats.values())))
        self.favorite_count.configure(
            text=str(sum(1 for g in games if g.get("favorite", False)))
        )

        self.playtime = playtime
        self.draw_chart()
        self.parent.after(3000, self.refresh)

    def draw_chart(self):
        if not hasattr(self, "chart"):
            return

        self.chart.delete("all")
        width = max(self.chart.winfo_width(), 500)
        height = max(self.chart.winfo_height(), 300)

        values = sorted(
            [(name, int(seconds or 0)) for name, seconds in self.playtime.items()],
            key=lambda item: item[1],
            reverse=True
        )[:8]

        if not values:
            self.chart.create_text(
                width / 2, height / 2,
                text="Launch a game to start building statistics.",
                fill="#777777", font=("Arial", 14)
            )
            return

        left, right, top, bottom = 55, 25, 25, 55
        chart_w = width - left - right
        chart_h = height - top - bottom
        max_value = max(v for _, v in values) or 1
        gap = 14
        bar_w = max(24, (chart_w - gap * (len(values) - 1)) / len(values))

        for i, (name, value) in enumerate(values):
            x1 = left + i * (bar_w + gap)
            x2 = x1 + bar_w
            bar_h = (value / max_value) * (chart_h - 25)
            y1 = height - bottom - bar_h
            y2 = height - bottom

            self.chart.create_rectangle(
                x1, y1, x2, y2, fill="#00aa88", outline=""
            )
            self.chart.create_text(
                (x1 + x2) / 2, y1 - 10,
                text=f"{value // 60}m",
                fill="#dddddd", font=("Arial", 10, "bold")
            )

            short = name if len(name) <= 12 else name[:10] + "…"
            self.chart.create_text(
                (x1 + x2) / 2, height - bottom + 18,
                text=short, fill="#888888", font=("Arial", 9)
            )
