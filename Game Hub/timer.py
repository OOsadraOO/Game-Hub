# ==================================================
# ⏱ GAMEHUB TIMER
# ==================================================

import customtkinter as ctk
from icons import get_icon

from utils import format_time, show_notification


class TimerSystem:

    def __init__(self, app, parent):
        self.app = app
        self.parent = parent

        self.default_minutes = 25
        self.time_left = self.default_minutes * 60
        self.total_seconds = self.time_left
        self.timer_running = False
        self.timer_job = None
        self.pulse_state = False
        self.pulse_job = None

        self.build_ui()
        self.update_display()

    # ==================================================
    # 🎨 UI
    # ==================================================

    def build_ui(self):

        # Header
        header = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        header.pack(fill="x", padx=35, pady=(25, 5))

        ctk.CTkLabel(
            header,
            text="⏱  Focus Timer",
            font=("Arial", 34, "bold"),
            text_color="#00ffee"
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            header,
            text="● READY",
            font=("Arial", 14, "bold"),
            text_color="#00ff88"
        )
        self.status_label.pack(side="right", pady=10)

        ctk.CTkLabel(
            self.parent,
            text="Set a session, start focusing, and let GameHub handle the rest.",
            font=("Arial", 15),
            text_color="gray"
        ).pack(anchor="w", padx=38, pady=(0, 18))

        # Main content
        content = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        content.pack(fill="both", expand=True, padx=35, pady=5)

        # Timer card
        timer_card = ctk.CTkFrame(
            content,
            corner_radius=24,
            border_width=1,
            border_color="#00ffee"
        )
        timer_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        ctk.CTkLabel(
            timer_card,
            text="CURRENT SESSION",
            font=("Arial", 13, "bold"),
            text_color="gray"
        ).pack(pady=(30, 5))

        self.timer_label = ctk.CTkLabel(
            timer_card,
            text="25:00",
            font=("Arial", 76, "bold"),
            text_color="#00ff88"
        )
        self.timer_label.pack(pady=(5, 10))

        self.progress = ctk.CTkProgressBar(
            timer_card,
            height=12,
            corner_radius=8,
            progress_color="#00ffee"
        )
        self.progress.pack(fill="x", padx=55, pady=(5, 18))
        self.progress.set(1)

        self.session_label = ctk.CTkLabel(
            timer_card,
            text="25 minute session",
            font=("Arial", 15),
            text_color="gray"
        )
        self.session_label.pack(pady=(0, 18))

        controls = ctk.CTkFrame(
            timer_card,
            fg_color="transparent"
        )
        controls.pack(pady=(0, 28))

        self.start_button = ctk.CTkButton(
            controls,
            text="▶  Start",
            width=135,
            height=45,
            corner_radius=14,
            font=("Arial", 15, "bold"),
            fg_color="#00aa77",
            hover_color="#00cc88",
            command=self.start_timer
        )
        self.start_button.grid(row=0, column=0, padx=6)

        self.pause_button = ctk.CTkButton(
            controls,
            text="⏸  Pause",
            width=135,
            height=45,
            corner_radius=14,
            font=("Arial", 15, "bold"),
            command=self.pause_timer
        )
        self.pause_button.grid(row=0, column=1, padx=6)

        ctk.CTkButton(
            controls,
            text="↻  Reset",
            width=110,
            height=45,
            corner_radius=14,
            font=("Arial", 15, "bold"),
            fg_color="#202727",
            hover_color="#3a4545",
            command=self.reset_timer
        ).grid(row=0, column=2, padx=6)

        # Settings card
        settings_card = ctk.CTkFrame(
            content,
            width=300,
            corner_radius=24,
            border_width=1,
            border_color="#252d2d"
        )
        settings_card.pack(
            side="right",
            fill="y",
            padx=(12, 0)
        )
        settings_card.pack_propagate(False)

        ctk.CTkLabel(
            settings_card,
            text="SESSION LENGTH",
            font=("Arial", 15, "bold"),
            text_color="#00ffee"
        ).pack(anchor="w", padx=25, pady=(28, 15))

        presets = [
            ("5 min", 5),
            ("15 min", 15),
            ("25 min", 25),
            ("60 min", 60)
        ]

        preset_frame = ctk.CTkFrame(
            settings_card,
            fg_color="transparent"
        )
        preset_frame.pack(fill="x", padx=20)

        for index, (label, minutes) in enumerate(presets):
            ctk.CTkButton(
                preset_frame,
                text=label,
                height=40,
                corner_radius=12,
                fg_color="#202727",
                hover_color="#00aa88",
                command=lambda m=minutes: self.set_minutes(m)
            ).grid(
                row=index // 2,
                column=index % 2,
                padx=4,
                pady=4,
                sticky="ew"
            )

        preset_frame.grid_columnconfigure(0, weight=1)
        preset_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            settings_card,
            text="Custom minutes",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 8))

        self.minutes_entry = ctk.CTkEntry(
            settings_card,
            placeholder_text="e.g. 30",
            height=42,
            corner_radius=12
        )
        self.minutes_entry.pack(fill="x", padx=25)

        ctk.CTkButton(
            settings_card,
            text="Set Custom Time",
            height=40,
            corner_radius=12,
            command=self.set_custom_time
        ).pack(fill="x", padx=25, pady=10)

        self.message_label = ctk.CTkLabel(
            settings_card,
            text="Choose a preset or enter your own time.",
            font=("Arial", 12),
            text_color="gray",
            wraplength=240
        )
        self.message_label.pack(
            padx=25,
            pady=(12, 20)
        )

    # ==================================================
    # ⏱ TIMER LOGIC
    # ==================================================

    def set_minutes(self, minutes):
        if self.timer_running:
            self.message_label.configure(
                text="Pause or reset the current session before changing its length."
            )
            return

        self.default_minutes = minutes
        self.time_left = minutes * 60
        self.total_seconds = self.time_left
        self.minutes_entry.delete(0, "end")
        self.minutes_entry.insert(0, str(minutes))
        self.status_label.configure(text="● READY", text_color="#00ff88")
        self.message_label.configure(text=f"{minutes}-minute session selected.")
        self.update_display()

    def set_custom_time(self):
        try:
            minutes = int(self.minutes_entry.get().strip())
            if minutes <= 0 or minutes > 1440:
                raise ValueError
        except (ValueError, TypeError):
            self.message_label.configure(
                text="Enter a whole number between 1 and 1440 minutes."
            )
            return

        self.set_minutes(minutes)

    def start_timer(self):
        if self.timer_running:
            return

        if self.time_left <= 0:
            self.reset_timer()

        self.timer_running = True
        self.status_label.configure(
            text="● RUNNING",
            text_color="#00ff88"
        )
        self.start_pulse()
        self.start_button.configure(state="disabled")
        self.message_label.configure(text="Focus mode is active.")
        self.schedule_tick()

    def schedule_tick(self):
        if not self.timer_running:
            return

        self.update_display()

        if self.time_left <= 0:
            self.finish_timer()
            return

        self.time_left -= 1
        self.timer_job = self.parent.after(1000, self.schedule_tick)

    def pause_timer(self):
        if not self.timer_running:
            return

        self.timer_running = False
        self.stop_pulse()

        if self.timer_job is not None:
            self.parent.after_cancel(self.timer_job)
            self.timer_job = None

        self.status_label.configure(
            text="● PAUSED",
            text_color="#ffaa00"
        )
        self.start_button.configure(state="normal")
        self.message_label.configure(text="Session paused. Press Start to continue.")
        self.update_display()

    def reset_timer(self):
        self.timer_running = False
        self.stop_pulse()

        if self.timer_job is not None:
            try:
                self.parent.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None

        self.time_left = self.default_minutes * 60
        self.total_seconds = self.time_left

        self.status_label.configure(
            text="● READY",
            text_color="#00ff88"
        )
        self.start_button.configure(state="normal")
        self.message_label.configure(
            text=f"{self.default_minutes}-minute session ready."
        )
        self.update_display()

    def finish_timer(self):
        self.timer_running = False
        self.timer_job = None
        self.stop_pulse()
        self.time_left = 0

        self.status_label.configure(
            text="● COMPLETE",
            text_color="#00ffee"
        )
        self.start_button.configure(state="normal")
        self.message_label.configure(
            text="Session complete. Nice work!"
        )

        self.update_display()
        show_notification(
            "GameHub Timer",
            "Focus session finished!"
        )

    def start_pulse(self):
        if self.pulse_job is not None:
            return
        self.pulse_tick()

    def pulse_tick(self):
        if not self.timer_running:
            self.pulse_job = None
            return

        self.pulse_state = not self.pulse_state
        self.status_label.configure(
            text_color="#00ffee" if self.pulse_state else "#00ff88"
        )
        self.pulse_job = self.parent.after(650, self.pulse_tick)

    def stop_pulse(self):
        if self.pulse_job is not None:
            try:
                self.parent.after_cancel(self.pulse_job)
            except Exception:
                pass
            self.pulse_job = None
        self.pulse_state = False

    def update_display(self):
        self.timer_label.configure(
            text=format_time(max(0, self.time_left))
        )

        if self.total_seconds > 0:
            remaining_ratio = self.time_left / self.total_seconds
            self.progress.set(max(0, min(1, remaining_ratio)))

        minutes = self.total_seconds // 60
        self.session_label.configure(
            text=f"{minutes} minute session"
        )
