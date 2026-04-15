import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import bcrypt

class AuthSystem:
    def __init__(self, parent, db, on_success):
        self.parent = parent
        self.db = db
        self.on_success = on_success
        try:
            self.bg_image = ctk.CTkImage(light_image=Image.open("bg.png"), dark_image=Image.open("bg.png"), size=(1300, 850))
        except: self.bg_image = None

    def draw_screen(self, mode="login"):
        for w in self.parent.winfo_children(): w.destroy()
        if self.bg_image:
            ctk.CTkLabel(self.parent, image=self.bg_image, text="").place(relx=0, rely=0, relwidth=1, relheight=1)
        
        frame = ctk.CTkFrame(self.parent, width=420, height=520, corner_radius=25, fg_color="#0f172a", border_width=2, border_color="#1e293b")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="💎 WealthWise Pro", font=("Arial", 30, "bold"), text_color="#10b981").pack(pady=(40, 5))
        u_in = ctk.CTkEntry(frame, placeholder_text="Username", width=300, height=45); u_in.pack(pady=10)
        p_in = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300, height=45); p_in.pack(pady=10)

        if mode == "login":
            ctk.CTkButton(frame, text="LOGIN", width=300, height=45, fg_color="#10b981", command=lambda: self.login(u_in.get(), p_in.get())).pack(pady=20)
            ctk.CTkButton(frame, text="Create Account", fg_color="transparent", command=lambda: self.draw_screen("register")).pack()
        else:
            ctk.CTkButton(frame, text="REGISTER", width=300, height=45, fg_color="#3b82f6", command=lambda: self.register(u_in.get(), p_in.get())).pack(pady=20)
            ctk.CTkButton(frame, text="Back to Login", fg_color="transparent", command=lambda: self.draw_screen("login")).pack()

    def login(self, u, p):
        self.db.execute("SELECT id, username, monthly_limit, daily_limit, password FROM users WHERE username=%s", (u,))
        res = self.db.cursor.fetchone()
        if res:
            try:
                if bcrypt.checkpw(p.encode('utf-8'), res[4].encode('utf-8')):
                    self.on_success(res[:4]); return
            except: 
                if p == res[4]: self.on_success(res[:4]); return
        messagebox.showerror("Error", "Access Denied")

    def register(self, u, p):
        hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            self.db.execute("INSERT INTO users (username, password, monthly_limit, daily_limit) VALUES (%s,%s,5000,500)", (u, hashed))
            self.db.commit(); messagebox.showinfo("Success", "Account Encrypted!"); self.draw_screen("login")
        except Exception as e: messagebox.showerror("Error", f"Trace: {e}")