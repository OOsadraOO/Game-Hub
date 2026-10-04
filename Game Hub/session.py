import customtkinter as ctk
from datetime import datetime
from utils import load_json, save_json, show_notification


class GamingSessionWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("🎮 Gaming Session")
        self.geometry("520x430")
        self.grab_set()

        self.running = False
        self.elapsed = 0
        self.job = None

        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(
            self,
            text="🎮  Gaming Session Mode",
            font=("Arial", 28, "bold"),
            text_color="#00ffee"
        ).pack(pady=(28, 8))

        ctk.CTkLabel(
            self,
            text="Track a focused gaming session without leaving GameHub.",
            font=("Arial", 13),
            text_color="gray",
            wraplength=420
        ).pack(pady=(0, 22))

        self.time_label = ctk.CTkLabel(
            self,
            text="00:00:00",
            font=("Arial", 52, "bold"),
            text_color="#00ff88"
        )
        self.time_label.pack(pady=15)

        self.status_label = ctk.CTkLabel(
            self,
            text="● READY",
            font=("Arial", 14, "bold"),
            text_color="#00ff88"
        )
        self.status_label.pack()

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(pady=25)

        self.start_button = ctk.CTkButton(
            controls,
            text="▶ Start Session",
            width=150,
            height=44,
            corner_radius=12,
            fg_color="#00aa88",
            hover_color="#00ccaa",
            command=self.toggle
        )
        self.start_button.grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            controls,
            text="↻ Reset",
            width=110,
            height=44,
            corner_radius=12,
            fg_color="#202727",
            hover_color="#3a4545",
            command=self.reset
        ).grid(row=0, column=1, padx=6)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.running = True
            self.status_label.configure(
                text="● SESSION ACTIVE",
                text_color="#00ffee"
            )
            self.start_button.configure(text="⏸ Pause")
            self.tick()

    def tick(self):
        if not self.running:
            return

        self.elapsed += 1
        hours, remainder = divmod(self.elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_label.configure(
            text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        self.job = self.after(1000, self.tick)

    def stop(self):
        self.running = False
        if self.job:
            try:
                self.after_cancel(self.job)
            except Exception:
                pass
            self.job = None

        self.status_label.configure(
            text="● PAUSED",
            text_color="#ffaa00"
        )
        self.start_button.configure(text="▶ Resume")

    def reset(self):
        self.stop()
        self.elapsed = 0
        self.time_label.configure(text="00:00:00")
        self.status_label.configure(text="● READY", text_color="#00ff88")
        self.start_button.configure(text="▶ Start Session")
