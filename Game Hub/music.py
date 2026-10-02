# ==================================================
# 🎵 MUSIC SYSTEM
# ==================================================

import customtkinter as ctk
import pygame
import os

from tkinter import filedialog

from utils import load_json, save_json


# ==================================================
# 🎵 MUSIC PLAYER CLASS
# ==================================================

class MusicPlayer:

    def __init__(self, app, parent):

        self.app = app

        self.parent = parent

        # ==================================================
        # 🎵 PYGAME
        # ==================================================

        pygame.mixer.init()

        # ==================================================
        # 📂 DATA
        # ==================================================

        self.music_list = load_json(
            "data/music_playlist.json"
        )

        self.current_music = ""

        self.current_index = 0

        self.is_paused = False

        self.repeat = False

        self.shuffle = False

        # ==================================================
        # 🎨 UI
        # ==================================================

        self.build_ui()

        self.render_playlist()

    # ==================================================
    # 🎨 BUILD UI
    # ==================================================

    def build_ui(self):

        ctk.CTkLabel(
            self.parent,
            text="🎵 Music Player",
            font=("Arial", 32, "bold")
        ).pack(pady=20)

        self.music_name_label = ctk.CTkLabel(
            self.parent,
            text="No Music Selected",
            font=("Arial", 18)
        )

        self.music_name_label.pack(pady=10)

        # ==================================================
        # ➕ ADD MUSIC
        # ==================================================

        ctk.CTkButton(
            self.parent,
            text="➕ Add Music",
            width=180,
            height=40,
            command=self.add_music
        ).pack(pady=10)

        # ==================================================
        # 📜 PLAYLIST
        # ==================================================

        self.playlist_frame = ctk.CTkScrollableFrame(
            self.parent,
            width=650,
            height=250
        )

        self.playlist_frame.pack(pady=15)

        # ==================================================
        # 🎛 CONTROLS
        # ==================================================

        controls = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        controls.pack(pady=10)

        ctk.CTkButton(
            controls,
            text="⏮",
            width=60,
            command=self.previous_music
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            controls,
            text="▶",
            width=60,
            command=self.play_music
        ).grid(row=0, column=1, padx=5)

        ctk.CTkButton(
            controls,
            text="⏸",
            width=60,
            command=self.pause_music
        ).grid(row=0, column=2, padx=5)

        ctk.CTkButton(
            controls,
            text="⏹",
            width=60,
            command=self.stop_music
        ).grid(row=0, column=3, padx=5)

        ctk.CTkButton(
            controls,
            text="⏭",
            width=60,
            command=self.next_music
        ).grid(row=0, column=4, padx=5)

        # ==================================================
        # 🔀 SHUFFLE
        # ==================================================

        self.shuffle_button = ctk.CTkButton(
            self.parent,
            text="🔀 Shuffle: OFF",
            width=180,
            command=self.toggle_shuffle
        )

        self.shuffle_button.pack(pady=5)

        # ==================================================
        # 🔁 REPEAT
        # ==================================================

        self.repeat_button = ctk.CTkButton(
            self.parent,
            text="🔁 Repeat: OFF",
            width=180,
            command=self.toggle_repeat
        )

        self.repeat_button.pack(pady=5)

        # ==================================================
        # 🔊 VOLUME
        # ==================================================

        ctk.CTkLabel(
            self.parent,
            text="🔊 Volume"
        ).pack(pady=10)

        self.volume_slider = ctk.CTkSlider(
            self.parent,
            from_=0,
            to=1,
            command=self.change_volume
        )

        self.volume_slider.set(0.5)

        self.volume_slider.pack(pady=10)

    # ==================================================
    # ➕ ADD MUSIC
    # ==================================================

    def add_music(self):

        file_path = filedialog.askopenfilename(
            title="Select Music",
            filetypes=[("MP3 Files", "*.mp3")]
        )

        if file_path:

            self.music_list.append(file_path)

            save_json(
                "data/music_playlist.json",
                self.music_list
            )

            self.render_playlist()

    # ==================================================
    # 📜 PLAYLIST
    # ==================================================

    def render_playlist(self):

        for widget in self.playlist_frame.winfo_children():

            widget.destroy()

        for index, music_path in enumerate(self.music_list):

            row = ctk.CTkFrame(
                self.playlist_frame,
                corner_radius=15
            )

            row.pack(fill="x", pady=5)

            music_name = os.path.basename(music_path)

            ctk.CTkLabel(
                row,
                text=music_name,
                font=("Arial", 15)
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                row,
                text="▶",
                width=40,
                command=lambda p=music_path, i=index:
                self.select_music(p, i)
            ).pack(side="right", padx=5)

            ctk.CTkButton(
                row,
                text="❌",
                width=40,
                command=lambda p=music_path:
                self.delete_music(p)
            ).pack(side="right", padx=5)

    # ==================================================
    # 🎵 SELECT MUSIC
    # ==================================================

    def select_music(self, path, index):

        self.current_music = path

        self.current_index = index

        music_name = os.path.basename(path)

        self.music_name_label.configure(
            text=music_name
        )

        pygame.mixer.music.load(path)

        pygame.mixer.music.play()

    # ==================================================
    # ▶ PLAY
    # ==================================================

    def play_music(self):

        if self.current_music != "":

            pygame.mixer.music.load(
                self.current_music
            )

            pygame.mixer.music.play()

    # ==================================================
    # ⏸ PAUSE
    # ==================================================

    def pause_music(self):

        pygame.mixer.music.pause()

        self.is_paused = True

    # ==================================================
    # ⏯ RESUME
    # ==================================================

    def resume_music(self):

        if self.is_paused:

            pygame.mixer.music.unpause()

            self.is_paused = False

    # ==================================================
    # ⏹ STOP
    # ==================================================

    def stop_music(self):

        pygame.mixer.music.stop()

    # ==================================================
    # ⏭ NEXT
    # ==================================================

    def next_music(self):

        if len(self.music_list) == 0:

            return

        self.current_index += 1

        if self.current_index >= len(self.music_list):

            self.current_index = 0

        path = self.music_list[
            self.current_index
        ]

        self.select_music(
            path,
            self.current_index
        )

    # ==================================================
    # ⏮ PREVIOUS
    # ==================================================

    def previous_music(self):

        if len(self.music_list) == 0:

            return

        self.current_index -= 1

        if self.current_index < 0:

            self.current_index = len(
                self.music_list
            ) - 1

        path = self.music_list[
            self.current_index
        ]

        self.select_music(
            path,
            self.current_index
        )

    # ==================================================
    # ❌ DELETE MUSIC
    # ==================================================

    def delete_music(self, path):

        self.music_list.remove(path)

        save_json(
            "data/music_playlist.json",
            self.music_list
        )

        self.render_playlist()

    # ==================================================
    # 🔀 SHUFFLE
    # ==================================================

    def toggle_shuffle(self):

        self.shuffle = not self.shuffle

        if self.shuffle:

            self.shuffle_button.configure(
                text="🔀 Shuffle: ON"
            )

        else:

            self.shuffle_button.configure(
                text="🔀 Shuffle: OFF"
            )

    # ==================================================
    # 🔁 REPEAT
    # ==================================================

    def toggle_repeat(self):

        self.repeat = not self.repeat

        if self.repeat:

            self.repeat_button.configure(
                text="🔁 Repeat: ON"
            )

        else:

            self.repeat_button.configure(
                text="🔁 Repeat: OFF"
            )

    # ==================================================
    # 🔊 VOLUME
    # ==================================================

    def change_volume(self, value):

        pygame.mixer.music.set_volume(value)