import customtkinter as ctk
from database import Database
from auth import AuthSystem
from dashboard import DashboardView
from analysis import AnalysisView
from operations import OperationsView
from recovery import RecoveryView
from settings import SettingsView
from planner import PlannerView 
from datetime import datetime
from tkinter import messagebox

class WealthWiseMain(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WealthWise Pro | NEURAL HUB")
        self.geometry("1400x900")
        
        # 1. Start Database
        self.db = Database()
        
        # 2. Trigger Login (Does not create sidebar yet)
        self.init_auth_system()

    def init_auth_system(self):
        """Clears the screen and starts the authentication flow"""
        for w in self.winfo_children(): 
            w.destroy()
        
        self.user_id = None
        self.username = None
        
        # Initialize Auth System
        self.auth = AuthSystem(self, self.db, self.on_login_success)
        self.auth.draw_screen("login")

    def on_login_success(self, user_data):
        """Called by AuthSystem upon successful validation"""
        self.user_id, self.username, self.limit, self.daily_limit = user_data
        self.setup_ui_layout()

    def setup_ui_layout(self):
        """Builds the main Dashboard interface after login"""
        for w in self.winfo_children(): 
            w.destroy()
            
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 🚀 HIGH-TECH SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color="#070b14", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="💎 WEALTHWISE", font=("Impact", 28), text_color="#00ff99").pack(pady=(40, 10))
        
        # MONITOR BOX (Clock and User Info)
        mon = ctk.CTkFrame(self.sidebar, fg_color="#0f172a", corner_radius=15, border_width=1, border_color="#1e293b")
        mon.pack(fill="x", padx=20, pady=10)
        
        self.clock_lbl = ctk.CTkLabel(mon, text="", font=("Consolas", 14), text_color="#00ff99")
        self.clock_lbl.pack(pady=8)
        self.run_clock() # Start the loop
        
        ctk.CTkLabel(mon, text=f"LOGGED AS: {self.username.upper()}", font=("Arial", 11, "bold"), text_color="gray").pack(pady=(0, 10))

        # NAV BUTTONS
        nav = [
            ("🏠 VIEW DASHBOARD", self.go_dash),
            ("📓 PLAN BUDGET", self.go_planner),
            ("📈 SPENDING DATA", self.go_analysis),
            ("➕ ADD TRANSACTION", self.go_add),
            ("🛡️ BUDGET CLINIC", self.go_recovery),
            ("⚙️ CHANGE TARGETS", self.go_settings),
            ("🚪 EXIT HUB", self.logout)
        ]
        
        for t, c in nav:
            ctk.CTkButton(self.sidebar, text=t, height=52, corner_radius=15, fg_color="transparent", 
                          hover_color="#1e293b", anchor="w", font=("Arial", 16, "bold"), command=c).pack(fill="x", padx=15, pady=6)

        # CONTENT PANEL (The 'Screen' where views change)
        self.content = ctk.CTkFrame(self, fg_color="#020617", corner_radius=30, border_width=2, border_color="#1e293b")
        self.content.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        
        self.go_dash()

    def run_clock(self):
        """Standard recursive clock loop with safety check"""
        try:
            # Only update if the widget actually exists (Prevents errors after logout)
            if hasattr(self, 'clock_lbl') and self.clock_lbl.winfo_exists():
                self.clock_lbl.configure(text=datetime.now().strftime("%d %b | %H:%M:%S"))
                self.after(1000, self.run_clock)
        except:
            pass

    def view_handler(self, v):
        """Clears the center panel and shows the requested View class"""
        for w in self.content.winfo_children(): 
            w.destroy()
        v.show()

    # --- NAVIGATION HANDLERS ---
    def go_dash(self): 
        self.view_handler(DashboardView(self.content, self.db, self.user_id, self.limit, self.daily_limit))
    
    def go_planner(self):
        # Calls the updated PlannerView with AI + Notebook
        self.view_handler(PlannerView(self.content))
        
    def go_analysis(self): 
        self.view_handler(AnalysisView(self.content, self.db, self.user_id))
    
    def go_add(self): 
        self.view_handler(OperationsView(self.content, self.db, self.user_id, self.go_dash))
    
    def go_recovery(self): 
        self.view_handler(RecoveryView(self.content, self.db, self.user_id, self.limit))
    
    def go_settings(self): 
        self.view_handler(SettingsView(self.content, self.db, self.user_id, self.limit, self.daily_limit, self.update_limits))

    def update_limits(self, m, d): 
        """Callback to update global limits from SettingsView"""
        self.limit, self.daily_limit = float(m), float(d)
        self.go_dash()

    def logout(self): 
        """Safely shuts down the dashboard and re-runs auth"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to end the session?"):
            self.init_auth_system()

if __name__ == "__main__":
    app = WealthWiseMain()
    app.mainloop()