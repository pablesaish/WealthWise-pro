import customtkinter as ctk
from database import Database
from auth import AuthSystem
from dashboard import DashboardView
from analysis import AnalysisView
from operations import OperationsView
from recovery import RecoveryView
from settings import SettingsView
from datetime import datetime
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class WealthWiseMain(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WealthWise Pro | Student OS")
        self.geometry("1300x850")
        
        self.db = Database()
        self.user_id = None
        self.username = ""
        self.limit = 5000
        self.daily_limit = 500

        self.auth = AuthSystem(self, self.db, self.on_login_success)
        self.auth.draw_screen()

    def on_login_success(self, user_data):
        self.user_id, self.username, self.limit, self.daily_limit = user_data
        self.setup_ui_layout()

    # ✅ FIXED FUNCTION
    def setup_ui_layout(self):
        for w in self.winfo_children():
            w.destroy()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#0a0a0a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            self.sidebar,
            text="💎 WealthWise Pro",
            font=("Arial", 20, "bold"),
            text_color="#2ecc71"
        ).pack(pady=(40, 5))
        
        self.clock_lbl = ctk.CTkLabel(
            self.sidebar, text="", font=("Arial", 11), text_color="gray"
        )
        self.clock_lbl.pack(pady=(0, 20))
        self.run_clock()

        # Navigation
        nav = [
            ("🏠 Dashboard", self.go_dash),
            ("📈 Analysis", self.go_analysis),
            ("➕ Add", self.go_add),
            ("🛡️ Recovery", self.go_recovery),
            ("⚙️ Goals", self.go_settings),
            ("🚪 Logout", self.logout)  # ✅ correct
        ]
        
        for t, c in nav:
            ctk.CTkButton(
                self.sidebar,
                text=t,
                fg_color="transparent",
                anchor="w",
                command=c
            ).pack(fill="x", padx=15, pady=5)

        # Content Area
        self.content = ctk.CTkFrame(self, fg_color="#121212", corner_radius=15)
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.go_dash()

    # ✅ LOGOUT FUNCTION (clean)
    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
    
        if confirm:
            self.user_id = None
            self.username = ""
            self.limit = 5000
            self.daily_limit = 500

            for w in self.winfo_children():
                w.destroy()

            self.auth = AuthSystem(self, self.db, self.on_login_success)
            self.auth.draw_screen("login")

    def run_clock(self):
        if hasattr(self, 'clock_lbl'):
            self.clock_lbl.configure(
                text=datetime.now().strftime("%A, %d %b %H:%M:%S")
            )
            self.after(1000, self.run_clock)

    def go_dash(self):
        self.view_handler(
            DashboardView(self.content, self.db, self.user_id, self.limit, self.daily_limit)
        )

    def go_analysis(self):
        self.view_handler(AnalysisView(self.content, self.db, self.user_id))

    def go_add(self):
        self.view_handler(OperationsView(self.content, self.db, self.user_id, self.go_dash))

    def go_recovery(self):
        self.view_handler(RecoveryView(self.content, self.db, self.user_id, self.limit))

    def go_settings(self):
        self.view_handler(SettingsView(
            self.content, self.db, self.user_id,
            self.limit, self.daily_limit,
            self.update_limits
        ))

    def update_limits(self, m, d):
        self.limit, self.daily_limit = int(m), int(d)
        self.go_dash()

    def view_handler(self, view_obj):
        for w in self.content.winfo_children():
            w.destroy()
        view_obj.show()


if __name__ == "__main__":
    app = WealthWiseMain()
    app.mainloop()