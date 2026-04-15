import customtkinter as ctk
from datetime import datetime
import calendar

class RecoveryView:
    def __init__(self, container, db, user_id, limit):
        self.container, self.db, self.user_id, self.limit = container, db, user_id, float(limit)

    def show(self):
        now = datetime.now()
        self.db.execute("SELECT SUM(amount) FROM expense WHERE user_id=%s AND date LIKE %s", (self.user_id, f"{now.strftime('%Y-%m')}%"))
        res = self.db.cursor.fetchone()[0]
        spent = float(res) if res else 0.0
        
        ctk.CTkLabel(self.container, text="🛡️ YOUR BUDGET HEALTH", font=("Impact", 36), text_color="#ef4444").pack(pady=30)
        
        panel = ctk.CTkFrame(self.container, fg_color="#070b14", corner_radius=30, border_width=3, border_color="#ef4444")
        panel.pack(fill="both", padx=60, pady=20, expand=True)

        is_over = spent > self.limit
        msg = "⚠️ ALERT: YOU HAVE CROSSED YOUR LIMIT!" if is_over else "✅ GREAT: YOU ARE WITHIN BUDGET"
        color = "#ef4444" if is_over else "#00ff99"
        
        ctk.CTkLabel(panel, text=msg, font=("Arial", 22, "bold"), text_color=color).pack(pady=30)

        meter = ctk.CTkProgressBar(panel, progress_color=color, width=500, height=20)
        meter.set(min(spent/self.limit, 1) if self.limit > 0 else 0); meter.pack(pady=10)

        if is_over:
            debt = spent - self.limit
            days_left = max(1, calendar.monthrange(now.year, now.month)[1] - now.day)
            advice = f"You are ₹{int(debt)} over your monthly target.\nTry spending ₹{int(debt/days_left)} less each day to catch up!"
            ctk.CTkLabel(panel, text=advice, font=("Arial", 16), text_color="white", justify="center").pack(pady=20)
        else:
            ctk.CTkLabel(panel, text="Your money is safe. Keep following your daily limit!", font=("Arial", 14), text_color="gray").pack(pady=40)