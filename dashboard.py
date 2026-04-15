# import customtkinter as ctk
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from datetime import datetime
# import calendar

# class DashboardView:
#     def __init__(self, container, db, user_id, m_limit, d_limit):
#         self.container, self.db, self.user_id = container, db, user_id
#         self.m_limit, self.d_limit = float(m_limit), float(d_limit)

#     def show(self):
#         # 1. Calculation Neural Logic
#         now = datetime.now()
#         this_month = now.strftime('%Y-%m')
#         self.db.execute("SELECT amount FROM expense WHERE user_id=%s AND date LIKE %s", (self.user_id, f"{this_month}%"))
#         res = self.db.cursor.fetchall()
#         spent = sum(float(x[0]) for x in res) if res else 0.0
        
#         remaining = self.m_limit - spent
#         days_in_mo = calendar.monthrange(now.year, now.month)[1]
#         days_left = max(1, days_in_mo - now.day)
#         safe_amt = remaining / days_left

#         # 2. UI Layout
#         ctk.CTkLabel(self.container, text="📊 HOW IS YOUR MONEY DOING?", font=("Impact", 36), text_color="#00ff99").pack(pady=25)

#         cards_frame = ctk.CTkFrame(self.container, fg_color="transparent")
#         cards_frame.pack(fill="x", padx=40)

#         # ADVICE BOX (Easy English)
#         adv = ctk.CTkFrame(cards_frame, fg_color="#10172a", border_width=2, border_color="#3b82f6", corner_radius=20)
#         adv.pack(side="left", fill="both", expand=True, padx=10)
#         ctk.CTkLabel(adv, text="💡 SMART ADVICE", font=("Arial", 12, "bold"), text_color="#3b82f6").pack(pady=10)
        
#         msg = f"Spend ₹{int(safe_amt)} Today" if remaining > 0 else "❌ BUDGET EMPTY! STOP."
#         msg_color = "#00ff99" if remaining > 0 else "#ef4444"
        
#         ctk.CTkLabel(adv, text=msg, font=("Arial", 22, "bold"), text_color=msg_color).pack(pady=5)
#         ctk.CTkLabel(adv, text="Recommended to survive till end of month.", font=("Arial", 11), text_color="gray").pack(pady=(0,10))

#         # BUDGET USED CARD
#         use = ctk.CTkFrame(cards_frame, fg_color="#070b14", border_width=1, border_color="#1e293b", corner_radius=20)
#         use.pack(side="right", fill="both", expand=True, padx=10)
#         ctk.CTkLabel(use, text="BUDGET USED THIS MONTH", text_color="gray", font=("Arial", 11)).pack(pady=10)
#         ctk.CTkLabel(use, text=f"₹{int(spent)} / ₹{int(self.m_limit)}", font=("Arial", 22, "bold"), text_color="#00ff99").pack()
#         prog = min(spent/self.m_limit, 1) if self.m_limit > 0 else 0
#         pb = ctk.CTkProgressBar(use, progress_color="#00ff99", height=10)
#         pb.set(prog); pb.pack(fill="x", padx=30, pady=20)

#         # 3. LIVE BAR CHART
#         fig_frame = ctk.CTkFrame(self.container, fg_color="#070b14", corner_radius=25, border_width=1, border_color="#1e293b")
#         fig_frame.pack(fill="both", expand=True, padx=40, pady=25)
        
#         fig, ax = plt.subplots(figsize=(6, 3), facecolor='#020617')
#         ax.set_facecolor('#020617')
        
#         # Color coding: Spent is red, leftover is neon green
#         ax.bar(['Already Spent', 'Money Still Left'], [spent, max(0, remaining)], color=['#ef4444', '#00ff99'], width=0.5)
        
#         ax.tick_params(colors='white')
#         for spine in ax.spines.values(): spine.set_color('#1e293b')
#         ax.set_title("Remaining Balance Visualizer", color="white")

#         canvas = FigureCanvasTkAgg(fig, fig_frame)
#         canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


import customtkinter as ctk
from datetime import datetime
import calendar

class DashboardView:
    def __init__(self, container, db, user_id, m_limit, d_limit):
        self.container, self.db, self.user_id = container, db, user_id
        self.m_limit, self.d_limit = float(m_limit), float(d_limit)
        
        # NEON GREEN COLOR PALETTE
        self.colors = {
            "bg": "#010409",
            "glass": "#0d1117",
            "accent": "#00ff99",      # Hyper Green
            "accent_dim": "#006644",
            "critical": "#ff3131",    # Red for failure only
            "border": "#30363d",
            "text": "#e6edf3",
            "dim_text": "#8b949e"
        }

    def show(self):
        # 1. CORE LOGIC
        now = datetime.now()
        this_month = now.strftime('%Y-%m')
        self.db.execute("SELECT amount, category, date FROM expense WHERE user_id=%s AND date LIKE %s ORDER BY date DESC", (self.user_id, f"{this_month}%"))
        res = self.db.cursor.fetchall()
        
        spent = sum(float(x[0]) for x in res) if res else 0.0
        remaining = max(0, self.m_limit - spent)
        percent_used = (spent / self.m_limit) if self.m_limit > 0 else 1.0
        
        days_in_mo = calendar.monthrange(now.year, now.month)[1]
        days_left = max(1, days_in_mo - now.day)
        safe_amt = remaining / days_left
        
        # Check system health
        is_failing = remaining <= 0
        current_theme_color = self.colors['critical'] if is_failing else self.colors['accent']

        # MAIN WRAPPER
        self.wrapper = ctk.CTkScrollableFrame(self.container, fg_color=self.colors['bg'], scrollbar_button_color=self.colors['accent_dim'])
        self.wrapper.pack(fill="both", expand=True)

        # --- [TITLE BAR] ---
        title_frame = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        title_frame.pack(fill="x", padx=40, pady=(30, 20))
        
        ctk.CTkLabel(title_frame, text="TERMINAL : DASHBOARD_0.1", font=("Courier New", 14), text_color=self.colors['accent_dim']).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="QUANTUM WEALTH CORE", font=("Impact", 45), text_color=self.colors['text']).pack(anchor="w")

        # --- [SECTION 1: THE BIG HUD CARDS] ---
        stats_frame = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=10)

        # Monthly Fuel (Card 1)
        c1 = self.create_neon_card(stats_frame, "SYSTEM BUDGET", f"₹{int(self.m_limit)}", f"Balance: ₹{int(remaining)}")
        c1.grid(row=0, column=0, padx=10, sticky="nsew")

        # Safety Pulse (Card 2)
        advice_txt = "HALT SPENDING" if is_failing else f"₹{int(safe_amt)} / DAY"
        c2 = self.create_neon_card(stats_frame, "DAILY SURVIVAL PULSE", advice_text=advice_txt, 
                                   sub_text="Live AI optimization rate", color=current_theme_color)
        c2.grid(row=0, column=1, padx=10, sticky="nsew")

        # System Integrity (Card 3)
        c3 = self.create_neon_card(stats_frame, "RESOURCES DEPLETED", f"{int(percent_used*100)}%", 
                                   f"Usage efficiency {100-int(percent_used*100)}%", color=current_theme_color)
        c3.grid(row=0, column=2, padx=10, sticky="nsew")

        stats_frame.grid_columnconfigure((0,1,2), weight=1)

        # --- [SECTION 2: CENTERPIECE POWER BAR] ---
        energy_frame = ctk.CTkFrame(self.wrapper, fg_color=self.colors['glass'], corner_radius=20, border_width=1, border_color=self.colors['border'])
        energy_frame.pack(fill="x", padx=40, pady=30)
        
        header = ctk.CTkFrame(energy_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="MONETARY ENERGY CORE", font=("Impact", 22), text_color=self.colors['text']).pack(side="left")
        ctk.CTkLabel(header, text=f"{int(spent)} EXPENDED / {int(remaining)} RESERVED", font=("Arial", 12, "bold"), text_color=self.colors['dim_text']).pack(side="right")
        
        # Dual Segmented Progress (Next Level Visualization)
        pb = ctk.CTkProgressBar(energy_frame, height=25, fg_color="#1a1a1a", progress_color=current_theme_color, corner_radius=0)
        pb.set(percent_used)
        pb.pack(fill="x", padx=20, pady=(5, 30))

        # --- [SECTION 3: DATA STREAM (Transaction Peek)] ---
        data_frame = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        data_frame.pack(fill="x", padx=40, pady=(0, 50))
        
        # Recent logs look like terminal lines
        ctk.CTkLabel(data_frame, text="Recent Neural Logs [TRANSACTIONS]", font=("Courier New", 12), text_color=self.colors['accent_dim']).pack(anchor="w", pady=5)
        
        log_box = ctk.CTkFrame(data_frame, fg_color=self.colors['glass'], corner_radius=15, border_width=1, border_color=self.colors['border'])
        log_box.pack(fill="both", expand=True)

        if not res:
            ctk.CTkLabel(log_box, text="> No data stream detected for current month", font=("Courier New", 13), text_color=self.colors['dim_text']).pack(pady=40)
        else:
            for item in res[:5]: # Top 5 latest
                f = ctk.CTkFrame(log_box, fg_color="transparent")
                f.pack(fill="x", padx=20, pady=10)
                
                status_char = "⚡" if float(item[0]) < 1000 else "☢"
                color = self.colors['accent'] if float(item[0]) < 1000 else self.colors['critical']
                
                ctk.CTkLabel(f, text=f"{status_char} ENTRY :: {item[1].upper()}", font=("Courier New", 14, "bold"), text_color="white").pack(side="left")
                ctk.CTkLabel(f, text=f"(-) ₹{item[0]}", font=("Courier New", 14, "bold"), text_color=color).pack(side="right")
                ctk.CTkLabel(f, text=f"LOG_TIME: {item[2]}", font=("Courier New", 10), text_color=self.colors['dim_text']).pack(side="right", padx=30)
                
                # Faint separator
                line = ctk.CTkFrame(log_box, height=1, fg_color=self.colors['border'])
                line.pack(fill="x", padx=20)

    def create_neon_card(self, parent, title, advice_text, sub_text, color=None):
        if color is None: color = self.colors['accent']
        
        card = ctk.CTkFrame(parent, fg_color=self.colors['glass'], corner_radius=15, border_width=1, border_color=self.colors['border'])
        
        # Inner Glowing accent (tiny top border)
        glow = ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=0)
        glow.pack(fill="x", pady=(0, 0))

        ctk.CTkLabel(card, text=title, font=("Courier New", 11, "bold"), text_color=self.colors['dim_text']).pack(pady=(15, 0))
        ctk.CTkLabel(card, text=advice_text, font=("Impact", 35), text_color=color).pack(pady=5)
        ctk.CTkLabel(card, text=sub_text, font=("Arial", 10), text_color=self.colors['dim_text']).pack(pady=(0, 20))
        
        return card