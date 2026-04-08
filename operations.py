import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

class OperationsView:
    def __init__(self, container, db, user_id, callback):
        self.container = container
        self.db = db
        self.user_id = user_id
        self.cb = callback

    def show(self):
        ctk.CTkLabel(self.container, text="➕ Add Spending", font=("Arial", 24, "bold")).pack(pady=40)
        amt = ctk.CTkEntry(self.container, placeholder_text="Amount", width=300); amt.pack(pady=10)
        cat = ctk.CTkOptionMenu(self.container, values=["Food", "Transport", "Shopping", "Entertainment"], width=300); cat.pack(pady=10)
        desc = ctk.CTkEntry(self.container, placeholder_text="Description", width=300); desc.pack(pady=10)

        def save():
            self.db.execute("INSERT INTO expense (user_id, amount, category, description, date) VALUES (%s,%s,%s,%s,%s)",
                            (self.user_id, amt.get(), cat.get(), desc.get(), datetime.now().strftime('%Y-%m-%d')))
            self.db.commit()
            messagebox.showinfo("Success", "Added!")
            self.cb()

        ctk.CTkButton(self.container, text="Save", command=save, width=300).pack(pady=20)