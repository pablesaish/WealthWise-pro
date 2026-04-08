# import customtkinter as ctk
# import calendar
# from datetime import datetime

# class RecoveryView:
#     def __init__(self, container, db, user_id, limit):
#         self.container = container
#         self.db = db
#         self.user_id = user_id
#         self.limit = limit

#     def show(self):
#         # Calculate current state
#         this_month = datetime.now().strftime('%Y-%m')
#         self.db.execute("SELECT SUM(amount) FROM expense WHERE user_id=%s AND date LIKE %s", (self.user_id, f"{this_month}%"))
#         spent = self.db.cursor.fetchone()[0] or 0
        
#         # UI Heading
#         ctk.CTkLabel(self.container, text="🛡️ Financial Recovery Clinic", font=("Arial", 24, "bold"), text_color="#f39c12").pack(pady=20)

#         # Recovery Logic Box
#         box = ctk.CTkFrame(self.container, border_width=2, corner_radius=20, border_color="#f39c12")
#         box.pack(pady=30, padx=50, fill="both")

#         if spent > self.limit:
#             # Over-budget logic
#             debt = spent - self.limit
#             today = datetime.now().day
#             days_in_month = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
#             days_left = days_in_month - today
            
#             daily_recovery = debt / (days_left if days_left > 0 else 1)

#             ctk.CTkLabel(box, text="🚨 CRISIS MODE ACTIVE", text_color="#e74c3c", font=("Arial", 20, "bold")).pack(pady=15)
            
#             message = (f"You are ₹{debt} OVER your monthly limit!\n\n"
#                        f"📅 DAYS REMAINING: {days_left}\n"
#                        f"🛠️ ACTION PLAN:\n"
#                        f"You must save exactly ₹{int(daily_recovery)} PER DAY\n"
#                        f"extra to reach break-even by the end of this month.\n\n"
#                        f"AI RECOMMENDATION:\nStop all 'Shopping' and 'Entertainment' \ncategories for the next {days_left} days.")
            
#             ctk.CTkLabel(box, text=message, font=("Arial", 16), justify="left").pack(pady=20, padx=20)
            
#         else:
#             # Healthy logic
#             ctk.CTkLabel(box, text="✅ HEALTH STATUS: STABLE", text_color="#2ecc71", font=("Arial", 20, "bold")).pack(pady=30)
#             ctk.CTkLabel(box, text="You are currently within your safety budget.\nNo emergency recovery required.", font=("Arial", 15)).pack(pady=10)
            
#             # Recommendation
#             ctk.CTkLabel(box, text="TIP: Add your extra money to your Savings Stash!", text_color="gray").pack(pady=20)

import customtkinter as ctk
from datetime import datetime
import calendar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class RecoveryView:
    def __init__(self, container, db, user_id, limit):
        self.container = container
        self.db = db
        self.user_id = user_id
        self.limit = limit

    def show(self):
        for w in self.container.winfo_children():
            w.destroy()

        # ================= MAIN SCROLL =================
        main = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        main.pack(fill="both", expand=True)

        # ================= HEADER =================
        ctk.CTkLabel(
            main,
            text="🧠 RECOVERY CONTROL ROOM",
            font=("Arial", 28, "bold"),
            text_color="#f39c12"
        ).pack(pady=20)

        # ================= DATA =================
        this_month = datetime.now().strftime('%Y-%m')
        self.db.execute(
            "SELECT amount, category, date FROM expense WHERE user_id=%s AND date LIKE %s",
            (self.user_id, f"{this_month}%")
        )
        data = self.db.cursor.fetchall()

        spent = sum([x[0] for x in data]) if data else 0
        debt = max(0, spent - self.limit)

        today = datetime.now().day
        days_in_month = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
        days_left = max(1, days_in_month - today)

        daily_save = int(debt / days_left) if debt > 0 else 0
        monthly_target = debt

        # ================= RISK BAR =================
        percent = min(spent / self.limit, 1) if self.limit > 0 else 0

        risk = ctk.CTkFrame(main, corner_radius=15)
        risk.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(risk, text="SYSTEM RISK LEVEL", font=("Arial", 14)).pack(anchor="w", padx=15, pady=5)

        bar = ctk.CTkProgressBar(risk)
        bar.set(percent)
        bar.pack(fill="x", padx=15, pady=5)

        status = "SAFE" if percent < 0.7 else "WARNING" if percent < 1 else "DANGER"
        ctk.CTkLabel(risk, text=f"STATUS: {status}", text_color="#e74c3c").pack(anchor="e", padx=15)

        # ================= BIG CARDS =================
        cards = ctk.CTkFrame(main, fg_color="transparent")
        cards.pack(fill="x", padx=20, pady=15)

        def create_card(parent, title, value):
            card = ctk.CTkFrame(parent, corner_radius=20, width=200, height=120)
            card.pack(side="left", expand=True, padx=10)

            ctk.CTkLabel(card, text=title, font=("Arial", 13)).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=value, font=("Arial", 24, "bold")).pack()

        create_card(cards, "💸 TOTAL SPENT", f"₹{spent}")
        create_card(cards, "🚨 OVERSPENT", f"₹{debt}")
        create_card(cards, "📅 DAILY SAVE", f"₹{daily_save}")
        create_card(cards, "🎯 MONTH TARGET", f"₹{monthly_target}")

        # ================= GRAPH =================
        graph_frame = ctk.CTkFrame(main, corner_radius=15)
        graph_frame.pack(fill="both", padx=20, pady=20)

        ctk.CTkLabel(graph_frame, text="SPENDING TREND (LAST 7 DAYS)", font=("Arial", 16, "bold")).pack(pady=10)

        last7 = data[-7:] if len(data) >= 7 else data
        amounts = [x[0] for x in last7]
        days = [f"D{i+1}" for i in range(len(amounts))]

        fig = Figure(figsize=(6, 3))
        ax = fig.add_subplot(111)
        ax.plot(days, amounts, marker='o')
        ax.set_title("Trend")
        ax.set_ylabel("₹")

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", padx=10, pady=10)

        # ================= CONTROL PANEL =================
        panel = ctk.CTkFrame(main, corner_radius=20)
        panel.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            panel,
            text="🚨 CRISIS CONTROL PANEL",
            font=("Arial", 18, "bold"),
            text_color="#e74c3c"
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # -------- TOP MINI CARDS --------
        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=10)

        def mini_card(parent, title, value, color):
            f = ctk.CTkFrame(parent, corner_radius=15)
            f.pack(side="left", expand=True, padx=8)

            ctk.CTkLabel(f, text=title, font=("Arial", 11), text_color="gray").pack(pady=(8, 2))
            ctk.CTkLabel(f, text=value, font=("Arial", 16, "bold"), text_color=color).pack(pady=(0, 8))

        mini_card(top, "Over Budget", f"₹{debt}", "#e74c3c")
        mini_card(top, "Days Left", f"{days_left}", "#f39c12")
        mini_card(top, "Daily Fix", f"₹{daily_save}", "#2ecc71")

        # -------- ACTION PLAN --------
        action = ctk.CTkFrame(panel, corner_radius=15)
        action.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            action,
            text="🎯 RECOVERY ACTION PLAN",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        ctk.CTkLabel(
            action,
            text=f"• Save ₹{daily_save} every day\n"
                 f"• Recover ₹{monthly_target} before month ends\n"
                 f"• Spend only on essentials",
            justify="left",
            font=("Arial", 12)
        ).pack(anchor="w", padx=15, pady=5)

        # -------- RULES --------
        rules = ctk.CTkFrame(panel, corner_radius=15)
        rules.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            rules,
            text="⚙️ SYSTEM RULES",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        ctk.CTkLabel(
            rules,
            text="• No impulse spending\n"
                 "• If you miss 1 day → double next day\n"
                 "• Track every expense",
            justify="left",
            font=("Arial", 12)
        ).pack(anchor="w", padx=15, pady=5)

        # -------- WARNING --------
        warn = ctk.CTkFrame(panel, corner_radius=15)
        warn.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            warn,
            text="⚠️ WARNING",
            text_color="#e74c3c",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        ctk.CTkLabel(
            warn,
            text="If you continue this pattern, your monthly spending will exceed limits significantly.",
            wraplength=900,
            justify="left"
        ).pack(anchor="w", padx=15, pady=5)