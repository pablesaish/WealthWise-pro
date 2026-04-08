# import customtkinter as ctk
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from datetime import datetime, timedelta

# class DashboardView:
#     def __init__(self, container, db, user_id, m_limit, d_limit):
#         self.container = container
#         self.db = db
#         self.user_id = user_id
#         self.m_limit = m_limit
#         self.d_limit = d_limit

#     def show(self):
#         now = datetime.now()
#         month_spent = self.db.execute("SELECT SUM(amount) FROM expense WHERE user_id=%s AND date LIKE %s", (self.user_id, f"{now.strftime('%Y-%m')}%")).fetchone()[0] or 0
#         today_spent = self.db.execute("SELECT SUM(amount) FROM expense WHERE user_id=%s AND date=%s", (self.user_id, now.strftime('%Y-%m-%d'))).fetchone()[0] or 0

#         # UI Header
#         head = ctk.CTkFrame(self.container, fg_color="transparent")
#         head.pack(fill="x", pady=20, padx=20)
#         ctk.CTkLabel(head, text=f"Dashboard", font=("Arial", 26, "bold")).pack(side="left")
#         ctk.CTkLabel(head, text=f"📅 {now.strftime('%B %Y')}", font=("Arial", 14), text_color="#2ecc71").pack(side="right")

#         # Top Cards
#         row = ctk.CTkFrame(self.container, fg_color="transparent")
#         row.pack(fill="x", padx=10)
#         self.card(row, "Today Spent", f"₹{today_spent}", "#e74c3c" if today_spent > self.d_limit else "#2ecc71")
#         self.card(row, "Month Spent", f"₹{month_spent}", "#e74c3c" if month_spent > self.m_limit else "#3498db")
#         self.card(row, "Daily Cap", f"₹{self.d_limit}", "#9b59b6")

#         # Line Graph (Real-time trends)
#         graph = ctk.CTkFrame(self.container, fg_color="#1a1a1a", corner_radius=15)
#         graph.pack(fill="both", expand=True, padx=20, pady=20)
        
#         days, vals = [], []
#         for i in range(6, -1, -1):
#             dt = (now - timedelta(days=i)).strftime('%Y-%m-%d')
#             self.db.execute("SELECT SUM(amount) FROM expense WHERE user_id=%s AND date=%s", (self.user_id, dt))
#             days.append((now - timedelta(days=i)).strftime('%a'))
#             vals.append(self.db.cursor.fetchone()[0] or 0)

#         fig, ax = plt.subplots(figsize=(5,3), facecolor='#1a1a1a')
#         ax.set_facecolor('#1a1a1a')
#         ax.plot(days, vals, color='#2ecc71', marker='o')
#         ax.tick_params(colors='white')
        
#         canvas = FigureCanvasTkAgg(fig, graph)
#         canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

#     def card(self, m, t, v, c):
#         f = ctk.CTkFrame(m, border_width=1, border_color="#333", height=120)
#         f.pack(side="left", fill="x", expand=True, padx=10)
#         ctk.CTkLabel(f, text=t, font=("Arial", 12), text_color="gray").pack(pady=(15,0))
#         ctk.CTkLabel(f, text=v, font=("Arial", 24, "bold"), text_color=c).pack(pady=10)

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

class DashboardView:
    def __init__(self, container, db, user_id, m_limit, d_limit):
        self.container = container
        self.db = db
        self.user_id = user_id
        self.m_limit = m_limit
        self.d_limit = d_limit

    def show(self):
        now = datetime.now()

        # ===== SAFE DATA FETCH =====
        month_spent = self.safe_fetch(
            "SELECT SUM(amount) FROM expense WHERE user_id=%s AND date LIKE %s",
            (self.user_id, f"{now.strftime('%Y-%m')}%")
        )

        today_spent = self.safe_fetch(
            "SELECT SUM(amount) FROM expense WHERE user_id=%s AND date=%s",
            (self.user_id, now.strftime('%Y-%m-%d'))
        )

        # ===== HEADER =====
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(
            header,
            text="📊 CONTROL DASHBOARD",
            font=("Consolas", 28, "bold"),
            text_color="#00ffcc"
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=now.strftime("%B %Y"),
            font=("Consolas", 14),
            text_color="#888"
        ).pack(side="right")

        # ===== CARDS =====
        cards = ctk.CTkFrame(self.container, fg_color="transparent")
        cards.pack(fill="x", padx=20)

        self.metric_card(cards, "TODAY", today_spent, self.d_limit, "#ff4d4d")
        self.metric_card(cards, "MONTH", month_spent, self.m_limit, "#00ffcc")
        self.metric_card(cards, "DAILY LIMIT", self.d_limit, self.d_limit, "#ffaa00")

        # ===== GRAPH PANEL =====
        graph_frame = ctk.CTkFrame(
            self.container,
            fg_color="#0f172a",
            corner_radius=20,
            border_width=1,
            border_color="#1f2937"
        )
        graph_frame.pack(fill="both", expand=True, padx=25, pady=20)

        ctk.CTkLabel(
            graph_frame,
            text="📈 SPENDING TREND (LAST 7 DAYS)",
            font=("Consolas", 16, "bold"),
            text_color="#00ffcc"
        ).pack(anchor="w", padx=15, pady=10)

        # ===== GRAPH DATA (FIXED) =====
        days, vals = [], []

        for i in range(6, -1, -1):
            dt = (now - timedelta(days=i)).strftime('%Y-%m-%d')

            self.db.execute(
                "SELECT SUM(amount) FROM expense WHERE user_id=%s AND date=%s",
                (self.user_id, dt)
            )

            result = self.db.cursor.fetchone()[0]

            # 🔥 CRITICAL FIX
            if result is None:
                value = 0
            else:
                value = float(result)

            days.append((now - timedelta(days=i)).strftime('%a'))
            vals.append(value)

        # ===== GRAPH =====
        fig, ax = plt.subplots(figsize=(6,3), facecolor='#0f172a')
        ax.set_facecolor('#0f172a')

        ax.plot(days, vals, linewidth=2, marker='o')
        ax.fill_between(days, vals, alpha=0.2)

        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('#333')
        ax.spines['left'].set_color('#333')
        ax.set_title("Spending Pattern", color="white")

        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ===== SAFE FETCH FUNCTION =====
    def safe_fetch(self, query, params):
        self.db.execute(query, params)
        result = self.db.cursor.fetchone()[0]
        return float(result) if result is not None else 0

    # ===== METRIC CARD =====
    def metric_card(self, parent, title, value, limit, color):
        frame = ctk.CTkFrame(
            parent,
            fg_color="#111827",
            corner_radius=20,
            border_width=1,
            border_color="#1f2937"
        )
        frame.pack(side="left", expand=True, fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            frame,
            text=title,
            font=("Consolas", 12),
            text_color="#888"
        ).pack(anchor="w", padx=15, pady=(10, 0))

        ctk.CTkLabel(
            frame,
            text=f"₹{int(value)}",
            font=("Consolas", 28, "bold"),
            text_color=color
        ).pack(anchor="w", padx=15, pady=5)

        # Progress bar (safe)
        progress = (float(value) / float(limit)) if limit != 0 else 0
        progress = min(progress, 1)

        bar = ctk.CTkProgressBar(frame, progress_color=color)
        bar.set(progress)
        bar.pack(fill="x", padx=15, pady=(5, 10))

        status = "SAFE" if value <= limit else "OVERLOAD"

        ctk.CTkLabel(
            frame,
            text=f"Status: {status}",
            font=("Consolas", 11),
            text_color=color if status == "SAFE" else "#ff4d4d"
        ).pack(anchor="w", padx=15, pady=(0, 10))