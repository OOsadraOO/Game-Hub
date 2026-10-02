# ==================================================
# ⏱ TIMER SYSTEM
# ==================================================

import customtkinter as ctk
import threading
import time
from utils import format_time, show_notification

class TimerSystem:
    def __init__(self, app, parent):
        self.app=app; self.parent=parent; self.time_left=25*60; self.timer_running=False; self.build_ui()
    def build_ui(self):
        ctk.CTkLabel(self.parent,text="⏱ Pomodoro Timer",font=("Arial",32,"bold")).pack(pady=20)
        self.timer_label=ctk.CTkLabel(self.parent,text="25:00",font=("Arial",90,"bold"),text_color="#00ff88"); self.timer_label.pack(pady=40)
        self.minutes_entry=ctk.CTkEntry(self.parent,placeholder_text="Minutes",width=180,height=40); self.minutes_entry.pack(pady=10)
        ctk.CTkButton(self.parent,text="▶ Start",width=180,height=40,command=self.start_timer).pack(pady=10)
        ctk.CTkButton(self.parent,text="⏸ Pause",width=180,height=40,command=self.pause_timer).pack(pady=10)
        ctk.CTkButton(self.parent,text="🔄 Reset",width=180,height=40,command=self.reset_timer).pack(pady=10)
    def start_timer(self):
        if not self.timer_running:
            try: self.time_left=int(self.minutes_entry.get())*60
            except: pass
            self.timer_running=True; threading.Thread(target=self.run_timer,daemon=True).start()
    def run_timer(self):
        while self.time_left>0 and self.timer_running:
            self.timer_label.configure(text=format_time(self.time_left)); time.sleep(1); self.time_left-=1
        if self.time_left<=0:
            self.timer_label.configure(text="TIME UP!"); show_notification("GameHub Timer","Timer Finished!")
    def pause_timer(self): self.timer_running=False
    def reset_timer(self):
        self.timer_running=False; self.time_left=25*60; self.timer_label.configure(text="25:00")