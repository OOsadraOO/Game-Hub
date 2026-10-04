# ==================================================
# 🎵 GAMEHUB MUSIC PLAYER
# ==================================================

import os
import random
import customtkinter as ctk
import pygame

from tkinter import filedialog
from utils import load_json, save_json


class MusicPlayer:

    def __init__(self, app, parent):
        self.app = app
        self.parent = parent

        try:
            pygame.mixer.init()
        except pygame.error:
            pass

        self.music_list = load_json("data/music_playlist.json") or []
        self.current_music = ""
        self.current_index = -1
        self.is_paused = False
        self.repeat = False
        self.shuffle = False
        self.volume = 0.5
        self.track_length = 0.0
        self.user_seeking = False

        self.build_ui()
        self.render_playlist()
        pygame.mixer.music.set_volume(self.volume)
        self.update_timeline()

    def build_ui(self):
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(24, 8))

        ctk.CTkLabel(
            header,
            text="🎵  Music Player",
            font=("Arial", 32, "bold"),
            text_color="#00ffee"
        ).pack(side="left")

        self.track_count_label = ctk.CTkLabel(
            header,
            text="0 tracks",
            font=("Arial", 13),
            text_color="gray"
        )
        self.track_count_label.pack(side="right", pady=8)

        content = ctk.CTkFrame(self.parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=32, pady=(8, 28))

        now_card = ctk.CTkFrame(
            content,
            corner_radius=24,
            border_width=1,
            border_color="#00ffee"
        )
        now_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            now_card,
            text="NOW PLAYING",
            font=("Arial", 13, "bold"),
            text_color="#00ffee"
        ).pack(pady=(28, 10))

        self.music_name_label = ctk.CTkLabel(
            now_card,
            text="No music selected",
            font=("Arial", 24, "bold"),
            wraplength=500
        )
        self.music_name_label.pack(padx=30, pady=(5, 6))

        self.status_label = ctk.CTkLabel(
            now_card,
            text="Ready",
            font=("Arial", 13),
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 25))

        # ==================================================
        # ⏱ TIMELINE / SEEK
        # ==================================================

        timeline_frame = ctk.CTkFrame(now_card, fg_color="transparent")
        timeline_frame.pack(fill="x", padx=55, pady=(4, 8))

        time_row = ctk.CTkFrame(timeline_frame, fg_color="transparent")
        time_row.pack(fill="x")

        self.current_time_label = ctk.CTkLabel(
            time_row, text="0:00", font=("Arial", 11), text_color="gray"
        )
        self.current_time_label.pack(side="left")

        self.total_time_label = ctk.CTkLabel(
            time_row, text="0:00", font=("Arial", 11), text_color="gray"
        )
        self.total_time_label.pack(side="right")

        self.timeline_slider = ctk.CTkSlider(
            timeline_frame, from_=0, to=1, height=14, command=self.seek_music
        )
        self.timeline_slider.set(0)
        self.timeline_slider.pack(fill="x", pady=(4, 0))
        self.timeline_slider.bind("<Button-1>", self.start_seek)
        self.timeline_slider.bind("<ButtonRelease-1>", self.finish_seek)

        controls = ctk.CTkFrame(now_card, fg_color="transparent")
        controls.pack(pady=8)

        buttons = [
            ("⏮", self.previous_music, 52),
            ("▶", self.play_music, 58),
            ("⏯", self.pause_or_resume, 58),
            ("⏹", self.stop_music, 58),
            ("⏭", self.next_music, 52),
        ]
        for column, (text, command, width) in enumerate(buttons):
            ctk.CTkButton(
                controls,
                text=text,
                width=width,
                height=46,
                corner_radius=14,
                font=("Arial", 16, "bold"),
                fg_color="#202727",
                hover_color="#00aa88",
                command=command
            ).grid(row=0, column=column, padx=4)

        modes = ctk.CTkFrame(now_card, fg_color="transparent")
        modes.pack(pady=(22, 12))

        self.shuffle_button = ctk.CTkButton(
            modes,
            text="🔀  Shuffle OFF",
            width=145,
            height=38,
            corner_radius=12,
            fg_color="#202727",
            hover_color="#00aa88",
            command=self.toggle_shuffle
        )
        self.shuffle_button.grid(row=0, column=0, padx=5)

        self.repeat_button = ctk.CTkButton(
            modes,
            text="🔁  Repeat OFF",
            width=145,
            height=38,
            corner_radius=12,
            fg_color="#202727",
            hover_color="#00aa88",
            command=self.toggle_repeat
        )
        self.repeat_button.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(
            now_card,
            text="Volume",
            font=("Arial", 13, "bold")
        ).pack(pady=(18, 5))

        self.volume_slider = ctk.CTkSlider(
            now_card,
            from_=0,
            to=1,
            height=16,
            command=self.change_volume
        )
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(fill="x", padx=70, pady=(0, 28))

        playlist_card = ctk.CTkFrame(
            content,
            width=380,
            corner_radius=24,
            border_width=1,
            border_color="#252d2d"
        )
        playlist_card.pack(side="right", fill="y", padx=(10, 0))
        playlist_card.pack_propagate(False)

        playlist_header = ctk.CTkFrame(
            playlist_card,
            fg_color="transparent"
        )
        playlist_header.pack(fill="x", padx=20, pady=(20, 12))

        ctk.CTkLabel(
            playlist_header,
            text="Playlist",
            font=("Arial", 20, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            playlist_header,
            text="+ Add",
            width=90,
            height=34,
            corner_radius=10,
            command=self.add_music
        ).pack(side="right")

        self.playlist_frame = ctk.CTkScrollableFrame(
            playlist_card,
            corner_radius=15
        )
        self.playlist_frame.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 14)
        )

    def add_music(self):
        paths = filedialog.askopenfilenames(
            title="Select Music",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.ogg"),
                ("MP3 Files", "*.mp3"),
                ("All Files", "*.*")
            ]
        )
        if not paths:
            return

        for path in paths:
            if path not in self.music_list:
                self.music_list.append(path)

        save_json("data/music_playlist.json", self.music_list)
        self.render_playlist()

        if self.current_index == -1 and self.music_list:
            self.select_music(self.music_list[0], 0, autoplay=False)

    def render_playlist(self):
        for widget in self.playlist_frame.winfo_children():
            widget.destroy()

        count = len(self.music_list)
        self.track_count_label.configure(
            text=f"{count} track{'s' if count != 1 else ''}"
        )

        if not self.music_list:
            ctk.CTkLabel(
                self.playlist_frame,
                text="Your playlist is empty.\nAdd some music to get started.",
                font=("Arial", 14),
                text_color="gray",
                justify="center"
            ).pack(expand=True, pady=70)
            return

        for index, path in enumerate(self.music_list):
            name = os.path.basename(path)
            selected = index == self.current_index

            row = ctk.CTkFrame(
                self.playlist_frame,
                corner_radius=14,
                fg_color=("#19302d" if selected else "#151818"),
                border_width=1,
                border_color=("#00aa88" if selected else "#242b2b")
            )
            row.pack(fill="x", pady=4)

            play_row_button = ctk.CTkButton(
                row,
                text="▶",
                width=38,
                height=34,
                corner_radius=10,
                fg_color="#00aa88" if selected else "#202727",
                hover_color="#00ccaa",
                command=lambda p=path, i=index: self.select_music(p, i)
            )
            play_row_button.pack(side="left", padx=(7, 5), pady=7)

            ctk.CTkLabel(
                row,
                text=name,
                anchor="w",
                font=("Arial", 13, "bold" if selected else "normal")
            ).pack(side="left", fill="x", expand=True, padx=4)

            ctk.CTkButton(
                row,
                text="×",
                width=32,
                height=32,
                corner_radius=9,
                fg_color="transparent",
                hover_color="#7a2020",
                command=lambda p=path: self.delete_music(p)
            ).pack(side="right", padx=7)

    def select_music(self, path, index, autoplay=True):
        if not os.path.exists(path):
            self.status_label.configure(text="File not found", text_color="#ff6666")
            return

        self.current_music = path
        self.current_index = index
        self.is_paused = False

        self.music_name_label.configure(text=os.path.basename(path))
        self.status_label.configure(text="Playing" if autoplay else "Selected", text_color="#00ff88")
        self.render_playlist()

        try:
            pygame.mixer.music.load(path)
            self.track_length = 0.0
            try:
                self.track_length = max(0.0, float(pygame.mixer.Sound(path).get_length()))
            except pygame.error:
                pass
            self.timeline_slider.configure(to=max(self.track_length, 1.0))
            self.timeline_slider.set(0)
            self.current_time_label.configure(text="0:00")
            self.total_time_label.configure(text=self.format_time(self.track_length))
            if autoplay:
                pygame.mixer.music.play()
        except pygame.error as error:
            self.status_label.configure(text=f"Could not play file: {error}", text_color="#ff6666")

    def play_music(self):
        if not self.current_music and self.music_list:
            self.select_music(self.music_list[0], 0)
            return

        if not self.current_music:
            self.status_label.configure(text="Add music to your playlist first.", text_color="gray")
            return

        if self.is_paused:
            self.pause_or_resume()
            return

        try:
            pygame.mixer.music.load(self.current_music)
            pygame.mixer.music.play()
            self.status_label.configure(text="Playing", text_color="#00ff88")
        except pygame.error:
            self.status_label.configure(text="Unable to play this file.", text_color="#ff6666")

    def pause_or_resume(self):
        if not self.current_music:
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.status_label.configure(text="Playing", text_color="#00ff88")
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.status_label.configure(text="Paused", text_color="#ffaa00")

    def pause_music(self):
        if self.current_music:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.status_label.configure(text="Paused", text_color="#ffaa00")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_paused = False
        if self.current_music:
            self.status_label.configure(text="Stopped", text_color="gray")

    def next_music(self):
        if not self.music_list:
            return

        if self.shuffle and len(self.music_list) > 1:
            choices = [i for i in range(len(self.music_list)) if i != self.current_index]
            index = random.choice(choices)
        else:
            index = (self.current_index + 1) % len(self.music_list)

        self.select_music(self.music_list[index], index)

    def previous_music(self):
        if not self.music_list:
            return

        index = (self.current_index - 1) % len(self.music_list)
        self.select_music(self.music_list[index], index)

    def delete_music(self, path):
        if path not in self.music_list:
            return

        deleted_index = self.music_list.index(path)
        self.music_list.remove(path)

        if path == self.current_music:
            pygame.mixer.music.stop()
            self.current_music = ""
            self.current_index = -1
            self.is_paused = False
            self.music_name_label.configure(text="No music selected")
            self.status_label.configure(text="Ready", text_color="gray")
        elif deleted_index < self.current_index:
            self.current_index -= 1

        save_json("data/music_playlist.json", self.music_list)
        self.render_playlist()

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self.shuffle_button.configure(
            text=f"🔀  Shuffle {'ON' if self.shuffle else 'OFF'}"
        )

    def toggle_repeat(self):
        self.repeat = not self.repeat
        self.repeat_button.configure(
            text=f"🔁  Repeat {'ON' if self.repeat else 'OFF'}"
        )

    def change_volume(self, value):
        self.volume = float(value)
        pygame.mixer.music.set_volume(self.volume)

    
    # ==================================================
    # ⏱ TIMELINE / SEEK
    # ==================================================

    @staticmethod
    def format_time(seconds):
        seconds = max(0, int(seconds))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def start_seek(self, _event=None):
        self.user_seeking = True

    def finish_seek(self, _event=None):
        self.user_seeking = False
        self.seek_music(self.timeline_slider.get())

    def seek_music(self, value):
        if not self.current_music or self.track_length <= 0:
            return
        position = max(0.0, min(float(value), self.track_length))
        self.current_time_label.configure(text=self.format_time(position))
        if self.user_seeking:
            return
        try:
            pygame.mixer.music.set_pos(position)
            self.is_paused = False
            self.status_label.configure(text="Playing", text_color="#00ff88")
        except pygame.error:
            pass

    def update_timeline(self):
        if self.current_music and not self.user_seeking and not self.is_paused and self.track_length > 0:
            position = pygame.mixer.music.get_pos() / 1000.0
            position = max(0.0, min(position, self.track_length))
            self.timeline_slider.set(position)
            self.current_time_label.configure(text=self.format_time(position))
        self.parent.after(400, self.update_timeline)
