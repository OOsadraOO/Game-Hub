# ==================================================
# 🎬 SPLASH SCREEN
# ==================================================

import customtkinter as ctk
import tkinter as tk
import time


class SplashScreen(ctk.CTkToplevel):

    def __init__(self, parent):

        super().__init__(parent)

        self.update_idletasks()

        # ==================================================
        # 📐 SIZE
        # ==================================================

        width = 650
        height = 350

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(
            f"{width}x{height}+{x}+{y}"
        )

        # ==================================================
        # 🎨 WINDOW
        # ==================================================

        self.overrideredirect(True)

        self.configure(
            fg_color="#111111"
        )

        # ==================================================
        # 🎮 MAIN GAMEHUB ICON + LOGO
        # ==================================================

        logo_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        logo_frame.pack(pady=(42, 16))

        icon = tk.Canvas(
            logo_frame,
            width=92,
            height=72,
            bg="#111111",
            highlightthickness=0
        )
        icon.pack()

        # Clean geometric GameHub gamepad mark.
        icon.create_rectangle(
            16, 18, 76, 56,
            outline="#00ffee",
            width=3
        )
        icon.create_oval(
            8, 24, 28, 55,
            outline="#00ffee",
            width=3
        )
        icon.create_oval(
            64, 24, 84, 55,
            outline="#00ffee",
            width=3
        )
        icon.create_line(
            28, 37, 42, 37,
            fill="#00ffee",
            width=4
        )
        icon.create_line(
            35, 30, 35, 44,
            fill="#00ffee",
            width=4
        )
        icon.create_oval(
            57, 31, 63, 37,
            fill="#00ff88",
            outline=""
        )
        icon.create_oval(
            67, 39, 73, 45,
            fill="#00ff88",
            outline=""
        )

        ctk.CTkLabel(
            logo_frame,
            text="GAMEHUB",
            font=("Arial", 40, "bold"),
            text_color="#00ffee"
        ).pack(pady=(2, 0))

        # ==================================================
        # 📊 BAR
        # ==================================================

        self.progress = ctk.CTkProgressBar(
            self,
            width=400,
            height=15
        )

        self.progress.pack(
            pady=20
        )

        self.progress.set(0)

        # ==================================================
        # 💬 TEXT
        # ==================================================

        self.loading_text = ctk.CTkLabel(
            self,
            text="Loading...",
            font=("Arial", 18)
        )

        self.loading_text.pack()

        # ==================================================
        # 🚀 ANIMATION
        # ==================================================

        self.update()

        for i in range(101):

            self.progress.set(i / 100)

            self.loading_text.configure(
                text=f"Loading... {i}%"
            )

            self.update()

            time.sleep(0.015)

        self.destroy()
