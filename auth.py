# import customtkinter as ctk
# from tkinter import messagebox

# class AuthSystem:
#     def __init__(self, parent, db, on_success):
#         self.parent = parent
#         self.db = db
#         self.on_success = on_success

#     def draw_screen(self, mode="login"):
#         for widget in self.parent.winfo_children(): widget.destroy()
        
#         frame = ctk.CTkFrame(self.parent, width=400, height=500, corner_radius=20)
#         frame.place(relx=0.5, rely=0.5, anchor="center")
        
#         ctk.CTkLabel(frame, text="💎 WealthWise", font=("Arial", 30, "bold"), text_color="#2ecc71").pack(pady=(40, 5))
#         ctk.CTkLabel(frame, text="Sign In" if mode=="login" else "Register Account", font=("Arial", 16)).pack(pady=(0, 30))

#         u_in = ctk.CTkEntry(frame, placeholder_text="Username", width=280, height=45); u_in.pack(pady=10)
#         p_in = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=280, height=45); p_in.pack(pady=10)

#         if mode == "login":
#             ctk.CTkButton(frame, text="Login", width=280, height=45, 
#                           command=lambda: self.login(u_in.get(), p_in.get())).pack(pady=20)
#             ctk.CTkButton(frame, text="Create Account", fg_color="transparent", 
#                           command=lambda: self.draw_screen("register")).pack()
#         else:
#             ctk.CTkButton(frame, text="Register", width=280, height=45, 
#                           command=lambda: self.register(u_in.get(), p_in.get())).pack(pady=20)
#             ctk.CTkButton(frame, text="Back to Login", fg_color="transparent", 
#                           command=lambda: self.draw_screen("login")).pack()

#     def login(self, u, p):
#         try:
#             # Note: selecting 4 items here to match main.py expectation
#             res = self.db.execute(
#                 "SELECT id, username, monthly_limit, daily_limit FROM users WHERE username=%s AND password=%s", 
#                 (u, p)
#             ).fetchone()
            
#             if res: 
#                 self.on_success(res)
#             else: 
#                 messagebox.showerror("Error", "Invalid Username or Password")
#         except Exception as e:
#             messagebox.showerror("SQL Error", f"Check if daily_limit column exists: {e}")

#     def register(self, u, p):
#         try:
#             self.db.execute("INSERT INTO users (username, password, monthly_limit, daily_limit) VALUES (%s, %s, 5000, 500)", (u, p))
#             self.db.commit()
#             messagebox.showinfo("Success", "Registered! Now Login.")
#             self.draw_screen("login")
#         except Exception as e:
#             messagebox.showerror("Error", f"Username might exist or Database error: {e}")

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

class AuthSystem:
    def __init__(self, parent, db, on_success):
        self.parent = parent
        self.db = db
        self.on_success = on_success

        # ✅ Load background once (VERY IMPORTANT)
        self.bg_image = ctk.CTkImage(
            light_image=Image.open("bg.png"),
            dark_image=Image.open("bg.png"),
            size=(1300, 850)
        )

    def draw_screen(self, mode="login"):
        # Clear screen
        for widget in self.parent.winfo_children():
            widget.destroy()

        # ✅ BACKGROUND IMAGE
        bg_label = ctk.CTkLabel(self.parent, image=self.bg_image, text="")
        bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ✅ LOGIN CARD
        frame = ctk.CTkFrame(
            self.parent,
            width=420,
            height=520,
            corner_radius=25,
            fg_color="#111111"
        )
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # ✅ TITLE
        ctk.CTkLabel(
            frame,
            text="💎 WealthWise Pro",
            font=("Arial", 28, "bold"),
            text_color="#2ecc71"
        ).pack(pady=(40, 5))

        ctk.CTkLabel(
            frame,
            text="Sign In" if mode == "login" else "Create Account",
            font=("Arial", 16),
            text_color="gray"
        ).pack(pady=(0, 30))

        # ✅ INPUTS
        u_in = ctk.CTkEntry(frame, placeholder_text="Username", width=300, height=45)
        u_in.pack(pady=10)

        p_in = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300, height=45)
        p_in.pack(pady=10)

        # ✅ BUTTONS
        if mode == "login":
            ctk.CTkButton(
                frame,
                text="Login",
                width=300,
                height=45,
                fg_color="#2ecc71",
                hover_color="#27ae60",
                command=lambda: self.login(u_in.get(), p_in.get())
            ).pack(pady=20)

            ctk.CTkButton(
                frame,
                text="Create Account",
                fg_color="transparent",
                text_color="#2ecc71",
                command=lambda: self.draw_screen("register")
            ).pack()

        else:
            ctk.CTkButton(
                frame,
                text="Register",
                width=300,
                height=45,
                fg_color="#3498db",
                hover_color="#2980b9",
                command=lambda: self.register(u_in.get(), p_in.get())
            ).pack(pady=20)

            ctk.CTkButton(
                frame,
                text="Back to Login",
                fg_color="transparent",
                text_color="#2ecc71",
                command=lambda: self.draw_screen("login")
            ).pack()

    # ✅ LOGIN
    def login(self, u, p):
        try:
            res = self.db.execute(
                "SELECT id, username, monthly_limit, daily_limit FROM users WHERE username=%s AND password=%s",
                (u, p)
            ).fetchone()

            if res:
                self.on_success(res)
            else:
                messagebox.showerror("Error", "Invalid Username or Password")

        except Exception as e:
            messagebox.showerror("SQL Error", f"{e}")

    # ✅ REGISTER
    def register(self, u, p):
        try:
            self.db.execute(
                "INSERT INTO users (username, password, monthly_limit, daily_limit) VALUES (%s, %s, 5000, 500)",
                (u, p)
            )
            self.db.commit()

            messagebox.showinfo("Success", "Registered! Now Login.")
            self.draw_screen("login")

        except Exception as e:
            messagebox.showerror("Error", f"{e}")