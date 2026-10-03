# ==================================================
# 🎬 SPLASH SCREEN
# ==================================================

import customtkinter as ctk
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
        # 🎮 LOGO
        # ==================================================

        logo = ctk.CTkLabel(
            self,
            text="🎮 GAMEHUB",
            font=("Arial", 42, "bold"),
            text_color="#00ffee"
        )

        logo.pack(
            pady=(70, 20)
        )

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
