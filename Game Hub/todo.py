# ==================================================
# 📝 TODO SYSTEM
# ==================================================

import customtkinter as ctk
from utils import load_json, save_json

class TodoSystem:
    def __init__(self, app, parent):
        self.app=app; self.parent=parent
        self.tasks=load_json("data/todo.json"); self.build_ui(); self.render_tasks()
    def build_ui(self):
        ctk.CTkLabel(self.parent,text="📝 To-Do List",font=("Arial",32,"bold")).pack(pady=20)
        self.task_entry=ctk.CTkEntry(self.parent,placeholder_text="Enter a task...",width=400,height=40); self.task_entry.pack(pady=10)
        ctk.CTkButton(self.parent,text="Add Task",width=180,height=40,command=self.add_task).pack(pady=10)
        self.tasks_frame=ctk.CTkScrollableFrame(self.parent,width=700,height=450); self.tasks_frame.pack(padx=20,pady=20,expand=True,fill="both")
    def add_task(self):
        task=self.task_entry.get()
        if task=="": return
        self.tasks.append(task); save_json("data/todo.json",self.tasks); self.task_entry.delete(0,"end"); self.render_tasks()
    def render_tasks(self):
        for widget in self.tasks_frame.winfo_children(): widget.destroy()
        for task in self.tasks:
            row=ctk.CTkFrame(self.tasks_frame,corner_radius=15); row.pack(fill="x",pady=6)
            ctk.CTkLabel(row,text=task,font=("Arial",16)).pack(side="left",padx=15)
            ctk.CTkButton(row,text="❌",width=40,command=lambda t=task:self.delete_task(t)).pack(side="right",padx=10)
    def delete_task(self,task):
        self.tasks.remove(task); save_json("data/todo.json",self.tasks); self.render_tasks()