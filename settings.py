import customtkinter as ctk
from tkinter import messagebox

class SettingsView:
    def __init__(self, container, db, user_id, cur_m, cur_d, cb):
        self.container = container
        self.db = db
        self.user_id = user_id
        self.cur_m, self.cur_d = cur_m, cur_d
        self.cb = cb

    def show(self):
        ctk.CTkLabel(self.container, text="⚙️ Limits & Goals", font=("Arial", 24, "bold")).pack(pady=30)
        m = ctk.CTkEntry(self.container, placeholder_text=f"Month Limit ({self.cur_m})", width=300); m.pack(pady=10)
        d = ctk.CTkEntry(self.container, placeholder_text=f"Day Limit ({self.cur_d})", width=300); d.pack(pady=10)
        
        def save():
            self.db.execute("UPDATE users SET monthly_limit=%s, daily_limit=%s WHERE id=%s", (m.get() or self.cur_m, d.get() or self.cur_d, self.user_id))
            self.db.commit()
            messagebox.showinfo("OK", "Limits updated!")
            self.cb(m.get() or self.cur_m, d.get() or self.cur_d)
        
        ctk.CTkButton(self.container, text="Update Goals", command=save, width=300).pack(pady=20)