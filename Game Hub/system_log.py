# ==================================================
# GAMEHUB — SYSTEM LOG / MONITOR
# ==================================================

import os
import sqlite3
import threading
import time
import subprocess
from datetime import datetime

import customtkinter as ctk
import psutil

from icons import get_icon
from performance import get_gpu_usage, get_gpu_name


DB_PATH = "data/system_log.db"
SAMPLE_INTERVAL = 5
UI_REFRESH_INTERVAL = 1000
DB_REFRESH_INTERVAL = 5000


class SystemLogService:
    """Background system sampler with lightweight SQLite persistence."""

    def __init__(self):
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.last_disk = None
        self.last_net = None
        self.last_sample_time = None
        self.cpu_high_since = None
        self.ram_high_since = None
        self.gpu_high_since = None
        self.last_event = None
        self._ensure_db()
        self._migrate_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    epoch REAL NOT NULL,
                    cpu REAL NOT NULL,
                    ram REAL NOT NULL,
                    ram_used INTEGER NOT NULL,
                    ram_total INTEGER NOT NULL,
                    gpu REAL,
                    disk_read REAL NOT NULL,
                    disk_write REAL NOT NULL,
                    net_down REAL NOT NULL,
                    net_up REAL NOT NULL,
                    process_count INTEGER NOT NULL,
                    severity TEXT NOT NULL,
                    cpu_temp REAL,
                    gpu_temp REAL,
                    ping REAL,
                    disk_free INTEGER,
                    uptime REAL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    epoch REAL NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    details TEXT NOT NULL
                )
            """)
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_samples_epoch ON samples(epoch)"
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_epoch ON events(epoch)"
            )
            db.commit()

    def _migrate_db(self):
        try:
            with sqlite3.connect(DB_PATH) as db:
                columns = {row[1] for row in db.execute("PRAGMA table_info(samples)")}
                for name, kind in (
                    ("cpu_temp", "REAL"), ("gpu_temp", "REAL"),
                    ("ping", "REAL"), ("disk_free", "INTEGER"),
                    ("uptime", "REAL")
                ):
                    if name not in columns:
                        db.execute(f"ALTER TABLE samples ADD COLUMN {name} {kind}")
                db.commit()
        except Exception:
            pass

    @staticmethod
    def _cpu_temperature():
        try:
            sensors = psutil.sensors_temperatures()
            for entries in sensors.values():
                values = [float(x.current) for x in entries if x.current is not None]
                if values:
                    return max(values)
        except Exception:
            pass
        return None

    @staticmethod
    def _gpu_temperature():
        try:
            command = "(Get-Counter '\\GPU Engine(*)\\Temperature' -ErrorAction SilentlyContinue).CounterSamples | Select-Object -First 1 -ExpandProperty CookedValue"
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                capture_output=True, text=True, timeout=1.5
            )
            raw = result.stdout.strip().replace(",", ".")
            if raw:
                value = float(raw)
                return value if 0 < value < 150 else None
        except Exception:
            pass
        return None

    @staticmethod
    def _ping_value():
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "700", "1.1.1.1"],
                capture_output=True, text=True, timeout=1.2
            )
            if result.returncode != 0:
                return None
            for token in result.stdout.replace("<", " ").split():
                if token.lower().startswith("time="):
                    return float(token.split("=", 1)[1].replace("ms", ""))
        except Exception:
            pass
        return None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(
            target=self._run,
            name="GameHubSystemLog",
            daemon=True
        )
        self.thread.start()

    def stop(self):
        self.running = False

    @staticmethod
    def _rate(current, previous, elapsed):
        if previous is None or elapsed <= 0:
            return 0.0
        return max(0.0, (current - previous) / elapsed / (1024 * 1024))

    @staticmethod
    def _severity(cpu, ram, gpu, cpu_temp=None, gpu_temp=None, ping=None):
        values = [cpu, ram]
        if gpu is not None:
            values.append(gpu)

        peak = max(values)

        if peak >= 95 or (cpu_temp is not None and cpu_temp >= 90) or (gpu_temp is not None and gpu_temp >= 90):
            return "CRITICAL"
        if peak >= 85 or (cpu_temp is not None and cpu_temp >= 80) or (gpu_temp is not None and gpu_temp >= 80) or (ping is not None and ping >= 200):
            return "HIGH"
        if peak >= 70 or (cpu_temp is not None and cpu_temp >= 70) or (gpu_temp is not None and gpu_temp >= 70) or (ping is not None and ping >= 100):
            return "ELEVATED"
        return "NORMAL"

    def _ping(self):
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "700", "1.1.1.1"],
                capture_output=True,
                text=True,
                timeout=1.2
            )
            if result.returncode != 0:
                return None

            text = result.stdout.lower()
            marker = "time="
            if marker in text:
                raw = text.split(marker, 1)[1].split("ms", 1)[0]
                return float(raw.strip().replace("<", "").replace("=", ""))
        except Exception:
            pass
        return None

    def _sample(self):
        now = time.time()
        elapsed = (
            now - self.last_sample_time
            if self.last_sample_time is not None
            else SAMPLE_INTERVAL
        )

        disk = psutil.disk_io_counters()
        net = psutil.net_io_counters()

        disk_read = self._rate(
            disk.read_bytes,
            self.last_disk.read_bytes if self.last_disk else None,
            elapsed
        )
        disk_write = self._rate(
            disk.write_bytes,
            self.last_disk.write_bytes if self.last_disk else None,
            elapsed
        )
        net_down = self._rate(
            net.bytes_recv,
            self.last_net.bytes_recv if self.last_net else None,
            elapsed
        )
        net_up = self._rate(
            net.bytes_sent,
            self.last_net.bytes_sent if self.last_net else None,
            elapsed
        )

        self.last_disk = disk
        self.last_net = net
        self.last_sample_time = now

        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        gpu = get_gpu_usage()
        cpu_temp = self._cpu_temperature()
        gpu_temp = self._gpu_temperature()
        ping = self._ping_value()
        disk_free = psutil.disk_usage(os.path.abspath(os.sep)).free
        uptime = max(0, now - psutil.boot_time())
        severity = self._severity(cpu, memory.percent, gpu, cpu_temp, gpu_temp, ping)

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "epoch": now,
            "cpu": float(cpu),
            "ram": float(memory.percent),
            "ram_used": int(memory.used),
            "ram_total": int(memory.total),
            "gpu": None if gpu is None else float(gpu),
            "disk_read": disk_read,
            "disk_write": disk_write,
            "net_down": net_down,
            "net_up": net_up,
            "process_count": len(psutil.pids()),
            "severity": severity,
            "cpu_temp": cpu_temp,
            "gpu_temp": gpu_temp,
            "ping": ping,
            "disk_free": disk_free,
            "uptime": uptime
        }

    def _write_sample(self, sample):
        with sqlite3.connect(DB_PATH) as db:
            db.execute("""
                INSERT INTO samples (
                    timestamp, epoch, cpu, ram, ram_used, ram_total,
                    gpu, disk_read, disk_write, net_down, net_up,
                    process_count, severity, cpu_temp, gpu_temp, ping, disk_free, uptime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sample["timestamp"], sample["epoch"],
                sample["cpu"], sample["ram"],
                sample["ram_used"], sample["ram_total"],
                sample["gpu"], sample["disk_read"], sample["disk_write"],
                sample["net_down"], sample["net_up"],
                sample["process_count"], sample["severity"], sample["cpu_temp"], sample["gpu_temp"], sample["ping"], sample["disk_free"], sample["uptime"]
            ))
            db.commit()

    def _event_if_needed(self, sample):
        now = sample["epoch"]
        thresholds = (
            ("CPU", sample["cpu"], "cpu_high_since"),
            ("RAM", sample["ram"], "ram_high_since"),
            ("GPU", sample["gpu"], "gpu_high_since"),
        )

        for name, value, attr in thresholds:
            if value is None:
                setattr(self, attr, None)
                continue

            if value >= 85:
                started = getattr(self, attr)
                if started is None:
                    setattr(self, attr, now)
                elif now - started >= 15:
                    if self.last_event != (name, sample["severity"]):
                        details = f"{name} remained at {value:.0f}%+ for at least 15 seconds."
                        self._write_event(
                            sample["timestamp"],
                            now,
                            sample["severity"],
                            "High System Load",
                            details
                        )
                        self.last_event = (name, sample["severity"])
            else:
                setattr(self, attr, None)

        if sample["severity"] == "NORMAL":
            self.last_event = None

    def _write_event(self, timestamp, epoch, severity, title, details):
        with sqlite3.connect(DB_PATH) as db:
            db.execute(
                "INSERT INTO events(timestamp, epoch, severity, title, details) "
                "VALUES (?, ?, ?, ?, ?)",
                (timestamp, epoch, severity, title, details)
            )
            db.commit()

    def _run(self):
        psutil.cpu_percent(interval=None)

        while self.running:
            started = time.time()
            try:
                sample = self._sample()
                self._write_sample(sample)
                self._event_if_needed(sample)
            except Exception:
                pass

            delay = max(0.2, SAMPLE_INTERVAL - (time.time() - started))
            time.sleep(delay)

    @staticmethod
    def latest():
        try:
            with sqlite3.connect(DB_PATH) as db:
                row = db.execute("""
                    SELECT timestamp, cpu, ram, ram_used, ram_total, gpu,
                           disk_read, disk_write, net_down, net_up,
                           process_count, severity, cpu_temp, gpu_temp, ping, disk_free, uptime
                    FROM samples
                    ORDER BY epoch DESC
                    LIMIT 1
                """).fetchone()
            return row
        except Exception:
            return None

    @staticmethod
    def samples_since(seconds):
        cutoff = time.time() - seconds
        try:
            with sqlite3.connect(DB_PATH) as db:
                return db.execute("""
                    SELECT epoch, cpu, ram, gpu, severity
                    FROM samples
                    WHERE epoch >= ?
                    ORDER BY epoch ASC
                """, (cutoff,)).fetchall()
        except Exception:
            return []

    @staticmethod
    def recent_events(limit=12):
        try:
            with sqlite3.connect(DB_PATH) as db:
                return db.execute("""
                    SELECT timestamp, severity, title, details
                    FROM events
                    ORDER BY epoch DESC
                    LIMIT ?
                """, (limit,)).fetchall()
        except Exception:
            return []

    @staticmethod
    def top_processes(limit=6):
        rows = []
        for process in psutil.process_iter(["pid", "name", "memory_percent"]):
            try:
                rows.append((
                    process.info["name"] or "Unknown",
                    float(process.info["memory_percent"] or 0)
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        rows.sort(key=lambda item: item[1], reverse=True)
        return rows[:limit]


class SystemLogPage:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.service = SystemLogService()
        self.range_seconds = 3600
        self.build_ui()
        self.service.start()
        self.refresh_live()
        self.refresh_history()
        self.refresh_processes()

    def build_ui(self):
        header = ctk.CTkFrame(self.parent, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(22, 10))

        title = ctk.CTkFrame(header, fg_color="transparent")
        title.pack(side="left")

        ctk.CTkLabel(
            title, text="System Log",
            image=get_icon("log", 28),
            compound="left",
            font=("Arial", 32, "bold"),
            text_color="#00ffee"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title,
            text="Real-time system monitoring and historical performance",
            font=("Arial", 13),
            text_color="gray"
        ).pack(anchor="w", pady=(3, 0))

        self.status_label = ctk.CTkLabel(
            header, text="● MONITORING",
            font=("Arial", 12, "bold"),
            text_color="#00ff88"
        )
        self.status_label.pack(side="right", padx=10)

        cards = ctk.CTkFrame(self.parent, fg_color="transparent")
        cards.pack(fill="x", padx=25, pady=5)

        primary_cards = ctk.CTkFrame(cards, fg_color="transparent")
        primary_cards.pack(fill="x")

        self.cpu_value = self._metric_card(primary_cards, "CPU", "#00ffee")
        self.ram_value = self._metric_card(primary_cards, "RAM", "#ffaa00")
        self.gpu_value = self._metric_card(primary_cards, "GPU", "#aa66ff")
        self.disk_value = self._metric_card(primary_cards, "DISK I/O", "#00ff88")
        self.net_value = self._metric_card(primary_cards, "NETWORK", "#4488ff")
        self.load_value = self._metric_card(primary_cards, "STATUS", "#ff5555")

        secondary_cards = ctk.CTkFrame(cards, fg_color="transparent")
        secondary_cards.pack(fill="x", pady=(7, 0))

        self.temp_value = self._metric_card(secondary_cards, "TEMPERATURE", "#ff8844")
        self.ping_value = self._metric_card(secondary_cards, "PING", "#44aaff")

        ctk.CTkLabel(
            secondary_cards,
            text="Hardware sensors are shown only when Windows exposes them.",
            font=("Arial", 10),
            text_color="#666666"
        ).pack(side="right", padx=8, pady=8)

        middle = ctk.CTkFrame(self.parent, fg_color="transparent")
        middle.pack(fill="both", expand=True, padx=25, pady=10)

        chart_card = ctk.CTkFrame(
            middle, corner_radius=18, border_width=1,
            border_color="#252d2d"
        )
        chart_card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        chart_header = ctk.CTkFrame(chart_card, fg_color="transparent")
        chart_header.pack(fill="x", padx=18, pady=(12, 4))

        ctk.CTkLabel(
            chart_header, text="Performance History",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        range_frame = ctk.CTkFrame(chart_header, fg_color="transparent")
        range_frame.pack(side="right")

        for label, seconds in (
            ("1H", 3600), ("6H", 21600),
            ("24H", 86400), ("7D", 604800)
        ):
            ctk.CTkButton(
                range_frame, text=label, width=48, height=28,
                corner_radius=8, fg_color="#202727",
                hover_color="#00aa88",
                command=lambda s=seconds: self.set_range(s)
            ).pack(side="left", padx=2)

        self.chart = ctk.CTkCanvas(
            chart_card, bg="#111111", highlightthickness=0
        )
        self.chart.pack(fill="both", expand=True, padx=12, pady=10)
        self.chart.bind("<Configure>", lambda _e: self.draw_chart())

        side = ctk.CTkFrame(
            middle, width=300, corner_radius=18,
            border_width=1, border_color="#252d2d"
        )
        side.pack(side="right", fill="both", padx=(6, 0))
        side.pack_propagate(False)

        events_header = ctk.CTkFrame(side, fg_color="transparent")
        events_header.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            events_header, text="Performance Events",
            font=("Arial", 18, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            events_header,
            text="Load spikes, warnings and critical system events",
            font=("Arial", 10),
            text_color="#777777"
        ).pack(anchor="w", pady=(2, 0))

        self.events = ctk.CTkScrollableFrame(side, fg_color="transparent")
        self.events.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        bottom = ctk.CTkFrame(self.parent, fg_color="transparent")
        bottom.pack(fill="x", padx=25, pady=(0, 18))

        process_card = ctk.CTkFrame(
            bottom, corner_radius=18, border_width=1,
            border_color="#252d2d"
        )
        process_card.pack(fill="x")

        process_header = ctk.CTkFrame(process_card, fg_color="transparent")
        process_header.pack(fill="x", padx=18, pady=(10, 4))

        ctk.CTkLabel(
            process_header, text="Top Processes by RAM",
            font=("Arial", 16, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            process_header,
            text="Highest RAM usage — updates automatically",
            font=("Arial", 10),
            text_color="#777777"
        ).pack(side="left", padx=(12, 0))

        process_table = ctk.CTkFrame(process_card, fg_color="transparent")
        process_table.pack(fill="x", padx=14, pady=(2, 14))
        process_table.grid_columnconfigure(0, weight=1)
        process_table.grid_columnconfigure(1, weight=0, minsize=100)

        ctk.CTkLabel(
            process_table,
            text="PROCESS",
            font=("Arial", 10, "bold"),
            text_color="#777777",
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=(0, 5))

        ctk.CTkLabel(
            process_table,
            text="RAM",
            font=("Arial", 10, "bold"),
            text_color="#777777",
            anchor="e"
        ).grid(row=0, column=1, sticky="e", padx=(8, 12), pady=(0, 5))

        self.process_rows = ctk.CTkFrame(
            process_table, fg_color="transparent"
        )
        self.process_rows.grid(
            row=1, column=0, columnspan=2, sticky="ew"
        )
        self.process_rows.grid_columnconfigure(0, weight=1)



    def _metric_card(self, parent, title, accent):
        card = ctk.CTkFrame(
            parent, height=78, corner_radius=15,
            border_width=1, border_color="#252d2d"
        )
        card.pack(side="left", fill="x", expand=True, padx=4)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text=title, font=("Arial", 11, "bold")
        ).pack(pady=(8, 0))

        value = ctk.CTkLabel(
            card, text="—", font=("Arial", 21, "bold"),
            text_color=accent
        )
        value.pack()
        return value

    def set_range(self, seconds):
        self.range_seconds = seconds
        self.refresh_history()

    @staticmethod
    def _gb(value):
        return value / (1024 ** 3)

    def refresh_live(self):
        row = self.service.latest()

        if row:
            (
                timestamp, cpu, ram, ram_used, ram_total, gpu,
                disk_read, disk_write, net_down, net_up,
                process_count, severity, cpu_temp, gpu_temp, ping, disk_free, uptime
            ) = row

            self.cpu_value.configure(text=f"{cpu:.0f}%")
            self.ram_value.configure(
                text=f"{ram:.0f}%  •  {self._gb(ram_used):.1f} GB"
            )
            self.gpu_value.configure(
                text="—" if gpu is None else f"{gpu:.0f}%"
            )
            self.disk_value.configure(
                text=f"R {disk_read:.1f}  W {disk_write:.1f} MB/s"
            )
            self.net_value.configure(
                text=f"↓ {net_down:.1f}  ↑ {net_up:.1f} MB/s"
            )
            self.load_value.configure(text=severity)
            if cpu_temp is not None or gpu_temp is not None:
                self.temp_value.configure(text=f"{cpu_temp:.0f}°C" if cpu_temp is not None else "N/A")
            else:
                self.temp_value.configure(text="N/A")
            self.ping_value.configure(text="—" if ping is None else f"{ping:.0f} ms")

            colors = {
                "NORMAL": "#00ff88",
                "ELEVATED": "#ffaa00",
                "HIGH": "#ff7700",
                "CRITICAL": "#ff4444"
            }
            self.load_value.configure(
                text_color=colors.get(severity, "#00ff88")
            )

        self.parent.after(UI_REFRESH_INTERVAL, self.refresh_live)

    def refresh_history(self):
        self.draw_chart()

        for widget in self.events.winfo_children():
            widget.destroy()

        for timestamp, severity, title, details in self.service.recent_events():
            ctk.CTkLabel(
                self.events,
                text=f"{timestamp[11:19]}  •  {severity}",
                font=("Arial", 10, "bold"),
                text_color=(
                    "#ff4444" if severity == "CRITICAL"
                    else "#ff7700" if severity == "HIGH"
                    else "#ffaa00"
                )
            ).pack(anchor="w", padx=6, pady=(6, 0))

            ctk.CTkLabel(
                self.events,
                text=f"{title}\n{details}",
                justify="left",
                anchor="w",
                wraplength=245,
                text_color="#bbbbbb"
            ).pack(fill="x", padx=6, pady=(0, 4))

        self.parent.after(DB_REFRESH_INTERVAL, self.refresh_history)

    def refresh_processes(self):
        try:
            rows = self.service.top_processes()

            for widget in self.process_rows.winfo_children():
                widget.destroy()

            if not rows:
                ctk.CTkLabel(
                    self.process_rows,
                    text="No process data available.",
                    font=("Arial", 11),
                    text_color="#777777"
                ).pack(anchor="w", padx=8, pady=6)
            else:
                for index, (name, memory) in enumerate(rows):
                    row = ctk.CTkFrame(
                        self.process_rows,
                        fg_color="#151a1a",
                        corner_radius=8,
                        height=36
                    )
                    row.grid(row=index, column=0, sticky="ew", pady=2)
                    row.grid_columnconfigure(0, weight=1)
                    row.grid_propagate(False)

                    ctk.CTkLabel(
                        row,
                        text=name[:55],
                        font=("Arial", 11, "bold"),
                        text_color="#dddddd",
                        anchor="w"
                    ).grid(
                        row=0, column=0, sticky="ew",
                        padx=(12, 8)
                    )

                    ctk.CTkLabel(
                        row,
                        text=f"{memory:.1f}%",
                        font=("Arial", 11, "bold"),
                        text_color="#ffaa00",
                        anchor="e",
                        width=80
                    ).grid(
                        row=0, column=1, sticky="e",
                        padx=(8, 12)
                    )

        except Exception:
            pass

        self.parent.after(5000, self.refresh_processes)

    def draw_chart(self):
        if not hasattr(self, "chart"):
            return

        canvas = self.chart
        canvas.delete("all")

        width = max(canvas.winfo_width(), 500)
        height = max(canvas.winfo_height(), 260)
        left, right, top, bottom = 45, 18, 18, 30
        plot_w = width - left - right
        plot_h = height - top - bottom

        for percent in (0, 25, 50, 75, 100):
            y = top + plot_h * (1 - percent / 100)
            canvas.create_line(
                left, y, width - right, y,
                fill="#222929"
            )
            canvas.create_text(
                18, y, text=str(percent),
                fill="#666666", font=("Arial", 8)
            )

        rows = self.service.samples_since(self.range_seconds)
        if not rows:
            canvas.create_text(
                width / 2, height / 2,
                text="Collecting history...",
                fill="#777777", font=("Arial", 14)
            )
            return

        series = (
            ("CPU", 1, "#00ffee"),
            ("RAM", 2, "#ffaa00"),
            ("GPU", 3, "#aa66ff")
        )

        for name, index, color in series:
            points = []
            for i, row in enumerate(rows):
                value = row[index]
                if value is None:
                    continue
                x = left + (i / max(1, len(rows) - 1)) * plot_w
                y = top + plot_h * (1 - max(0, min(100, value)) / 100)
                points.extend((x, y))

            if len(points) >= 4:
                canvas.create_line(
                    *points, fill=color, width=2, smooth=True
                )

        legend_x = max(left + 10, width - 230)
        for index, (name, _, color) in enumerate(series):
            x = legend_x + index * 70
            canvas.create_oval(
                x, 8, x + 8, 16, fill=color, outline=""
            )
            canvas.create_text(
                x + 13, 12, text=name,
                fill="#aaaaaa", font=("Arial", 9), anchor="w"
            )

    def destroy(self):
        self.service.stop()
