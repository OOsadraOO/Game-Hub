import customtkinter as ctk
from config import DEFAULT_TIMER_MINUTES

class TimerSystem:
    def __init__(self, app, parent):
        self.app=app; self.parent=parent; self.seconds=DEFAULT_TIMER_MINUTES*60; self.running=False
        self.label=ctk.CTkLabel(parent,text=self.format_time(),font=("Arial",55,"bold")); self.label.pack(pady=60)
        ctk.CTkButton(parent,text="▶ Start",command=self.start).pack(pady=10)
        ctk.CTkButton(parent,text="↺ Reset",command=self.reset).pack(pady=10)
    def format_time(self): return f"{self.seconds//60:02d}:{self.seconds%60:02d}"
    def start(self):
        if not self.running: self.running=True; self.tick()
    def tick(self):
        if not self.running: return
        if self.seconds>0: self.seconds-=1; self.label.configure(text=self.format_time()); self.parent.after(1000,self.tick)
        else: self.running=False
    def reset(self): self.running=False; self.seconds=DEFAULT_TIMER_MINUTES*60; self.label.configure(text=self.format_time())
