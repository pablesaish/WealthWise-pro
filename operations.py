import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

class OperationsView:
    def __init__(self, container, db, user_id, callback):
        self.container, self.db, self.user_id, self.cb = container, db, user_id, callback

    def show(self):
        ctk.CTkLabel(self.container, text="➕ ADD NEW EXPENSE", font=("Impact", 34), text_color="#00ff99").pack(pady=40)
        
        frame = ctk.CTkFrame(self.container, corner_radius=25, fg_color="#070b14", border_width=2, border_color="#1e293b")
        frame.pack(pady=10, padx=60, fill="both")

        ctk.CTkLabel(frame, text="How much did you spend?", font=("Arial", 14), text_color="#64748b").pack(pady=(30, 0))
        amt = ctk.CTkEntry(frame, placeholder_text="0.00", width=400, height=55, font=("Consolas", 20), fg_color="#020617"); amt.pack(pady=10)
        
        ctk.CTkLabel(frame, text="What was it for?", font=("Arial", 14), text_color="#64748b").pack(pady=(15, 0))
        cat = ctk.CTkOptionMenu(frame, values=["🍔 FOOD", "🚕 TRANSPORT", "💡 BILLS", "🎮 FUN", "🎓 STUDIES", "📦 OTHER"], 
                                width=400, height=45, fg_color="#1e293b", button_color="#3b82f6"); cat.pack(pady=10)
        
        ctk.CTkLabel(frame, text="Brief Description", font=("Arial", 14), text_color="#64748b").pack(pady=(15, 0))
        desc = ctk.CTkEntry(frame, placeholder_text="Enter detail...", width=400, height=55, fg_color="#020617"); desc.pack(pady=10)

        def finalize():
            try:
                v = float(amt.get())
                self.db.execute("INSERT INTO expense (user_id, amount, category, description, date) VALUES (%s,%s,%s,%s,%s)",
                                (self.user_id, v, cat.get(), desc.get(), datetime.now().strftime('%Y-%m-%d')))
                self.db.commit()
                messagebox.showinfo("Success", "Expense added to your records.")
                self.cb()
            except:
                messagebox.showerror("Error", "Please enter a valid amount.")

        ctk.CTkButton(frame, text="✅ SAVE EXPENSE", font=("Arial", 16, "bold"), 
                      fg_color="#00ff99", text_color="black", height=55, width=400, command=finalize).pack(pady=40)