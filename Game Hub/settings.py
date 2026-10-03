import customtkinter as ctk


class SettingsWindow(ctk.CTkToplevel):

    def __init__(self,parent):

        super().__init__(parent)

        self.title("Settings")

        self.geometry("500x400")

        self.grab_set()

        title = ctk.CTkLabel(

            self,

            text="⚙ Settings",

            font=("Arial",30,"bold")
        )

        title.pack(pady=20)

        # THEME

        ctk.CTkLabel(
            self,
            text="Theme"
        ).pack()

        self.theme = ctk.CTkOptionMenu(

            self,

            values=[
                "Dark",
                "Light"
            ],

            command=self.change_theme
        )

        self.theme.pack(pady=10)

        # RGB

        self.rgb_switch = ctk.CTkSwitch(

            self,

            text="RGB Border"
        )

        self.rgb_switch.select()

        self.rgb_switch.pack(
            pady=20
        )

    def change_theme(self,value):

        if value=="Dark":

            ctk.set_appearance_mode("dark")

        else:

            ctk.set_appearance_mode("light")
