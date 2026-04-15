import customtkinter as ctk
from tkinter import messagebox

class SettingsView:
    def __init__(self, c, db, u_id, cm, cd, cb):
        self.con, self.db, self.uid, self.cm, self.cd, self.cb = c, db, u_id, cm, cd, cb

    def show(self):
        ctk.CTkLabel(self.con, text="⚙️ CALIBRATE TARGETS", font=("Impact", 28)).pack(pady=40)
        m = ctk.CTkEntry(self.con, placeholder_text=f"Month Target: ₹{self.cm}", width=300); m.pack(pady=10)
        d = ctk.CTkEntry(self.con, placeholder_text=f"Daily Cap: ₹{self.cd}", width=300); d.pack(pady=10)
        
        def s():
            nm, nd = m.get() or self.cm, d.get() or self.cd
            self.db.execute("UPDATE users SET monthly_limit=%s, daily_limit=%s WHERE id=%s", (nm, nd, self.uid))
            self.db.commit(); messagebox.showinfo("OK", "Updated!"); self.cb(nm, nd)
            
        ctk.CTkButton(self.con, text="SAVE GOALS", command=s, width=300).pack(pady=30)