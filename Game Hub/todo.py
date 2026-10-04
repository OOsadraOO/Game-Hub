# ==================================================
# 📝 GAMEHUB TO-DO
# ==================================================

import customtkinter as ctk

from utils import load_json, save_json


class TodoSystem:

    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        raw_tasks = load_json("data/todo.json") or []

        if raw_tasks and isinstance(raw_tasks[0], dict):
            self.tasks = raw_tasks
        else:
            self.tasks = [
                {"text": task, "completed": False}
                for task in raw_tasks
            ]

        self.filter_mode = "all"

        self.build_ui()
        self.render_tasks()

    def build_ui(self):
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(24, 8))

        ctk.CTkLabel(
            header,
            text="📝  To-Do",
            font=("Arial", 32, "bold"),
            text_color="#00ffee"
        ).pack(side="left")

        self.count_label = ctk.CTkLabel(
            header,
            text="0 tasks",
            font=("Arial", 13),
            text_color="gray"
        )
        self.count_label.pack(side="right", pady=8)

        add_card = ctk.CTkFrame(
            self.parent,
            corner_radius=20,
            border_width=1,
            border_color="#252d2d"
        )
        add_card.pack(fill="x", padx=32, pady=(8, 12))

        self.task_entry = ctk.CTkEntry(
            add_card,
            placeholder_text="What needs to be done?",
            height=44,
            corner_radius=12
        )
        self.task_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(16, 8),
            pady=16
        )
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        ctk.CTkButton(
            add_card,
            text="+ Add Task",
            width=120,
            height=44,
            corner_radius=12,
            fg_color="#00aa88",
            hover_color="#00ccaa",
            font=("Arial", 13, "bold"),
            command=self.add_task
        ).pack(side="right", padx=(8, 16), pady=16)

        toolbar = ctk.CTkFrame(self.parent, fg_color="transparent")
        toolbar.pack(fill="x", padx=32, pady=(0, 10))

        self.filter_buttons = {}
        for label, mode in [("All", "all"), ("Active", "active"), ("Completed", "completed")]:
            button = ctk.CTkButton(
                toolbar,
                text=label,
                width=100,
                height=36,
                corner_radius=10,
                fg_color="#00aa88" if mode == self.filter_mode else "transparent",
                hover_color="#00aa88",
                command=lambda m=mode: self.set_filter(m)
            )
            button.pack(side="left", padx=(0, 7))
            self.filter_buttons[mode] = button

        ctk.CTkButton(
            toolbar,
            text="Clear Completed",
            width=130,
            height=36,
            corner_radius=10,
            command=self.clear_completed
        ).pack(side="right")

        self.tasks_frame = ctk.CTkScrollableFrame(
            self.parent,
            corner_radius=18,
            border_width=1,
            border_color="#252d2d"
        )
        self.tasks_frame.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=(0, 28)
        )

    def add_task(self):
        task = self.task_entry.get().strip()
        if not task:
            return

        self.tasks.append({
            "text": task,
            "completed": False
        })
        save_json("data/todo.json", self.tasks)
        self.task_entry.delete(0, "end")
        self.filter_mode = "all"
        self.render_tasks()

    def set_filter(self, mode):
        self.filter_mode = mode
        self.render_tasks()

    def render_tasks(self):
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        active_count = sum(
            1 for task in self.tasks
            if not task.get("completed", False)
        )
        completed_count = len(self.tasks) - active_count
        self.count_label.configure(
            text=f"{len(self.tasks)} tasks  •  {active_count} active"
        )

        for mode, button in self.filter_buttons.items():
            button.configure(
                fg_color="#00aa88" if mode == self.filter_mode else "transparent"
            )

        visible = []
        for index, task in enumerate(self.tasks):
            is_completed = task.get("completed", False)

            if self.filter_mode == "active" and is_completed:
                continue
            if self.filter_mode == "completed" and not is_completed:
                continue

            visible.append((index, task.get("text", ""), is_completed))

        if not visible:
            message = {
                "all": "No tasks yet. Add your first task above.",
                "active": "No active tasks.",
                "completed": "No completed tasks."
            }[self.filter_mode]

            ctk.CTkLabel(
                self.tasks_frame,
                text=message,
                font=("Arial", 15),
                text_color="gray"
            ).pack(pady=90)
            return

        for index, task, is_completed in visible:
            self.create_task_row(index, task, is_completed)

    def create_task_row(self, index, task, is_completed):
        row = ctk.CTkFrame(
            self.tasks_frame,
            corner_radius=15,
            border_width=1,
            border_color="#242b2b"
        )
        row.pack(fill="x", pady=5)

        checkbox = ctk.CTkCheckBox(
            row,
            text="",
            width=28,
            command=lambda i=index: self.toggle_task(i)
        )
        checkbox.pack(side="left", padx=(15, 5), pady=12)

        if is_completed:
            checkbox.select()

        label = ctk.CTkLabel(
            row,
            text=task,
            anchor="w",
            font=("Arial", 15),
            text_color="gray" if is_completed else None
        )
        label.pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkButton(
            row,
            text="Delete",
            width=72,
            height=32,
            corner_radius=9,
            fg_color="transparent",
            hover_color="#9e2b35",
            command=lambda i=index: self.delete_task(i)
        ).pack(side="right", padx=12)

    def toggle_task(self, index):
        if index < 0 or index >= len(self.tasks):
            return

        self.tasks[index]["completed"] = not self.tasks[index].get(
            "completed",
            False
        )

        save_json("data/todo.json", self.tasks)
        self.render_tasks()

    def delete_task(self, task):
        if isinstance(task, int):
            index = task
        else:
            try:
                index = self.tasks.index(task)
            except ValueError:
                return

        self.tasks.pop(index)

        save_json("data/todo.json", self.tasks)
        self.render_tasks()

    def clear_completed(self):
        if not any(task.get("completed", False) for task in self.tasks):
            return

        self.tasks = [
            task for task in self.tasks
            if not task.get("completed", False)
        ]

        save_json("data/todo.json", self.tasks)
        self.render_tasks()
