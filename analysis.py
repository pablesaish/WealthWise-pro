import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

class AnalysisView:
    def __init__(self, container, db, user_id):
        self.container = container
        self.db = db
        self.user_id = user_id

    def show(self):
        ctk.CTkLabel(self.container, text=f"Monthly Deep Analysis", font=("Arial", 24, "bold")).pack(pady=15)
        
        tabs = ctk.CTkTabview(self.container)
        tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Split current month into 4 weeks
        wks = [("Week 1", 1, 7), ("Week 2", 8, 14), ("Week 3", 15, 21), ("Week 4", 22, 31)]
        for name, s, e in wks:
            tabs.add(name)
            self.build_table(tabs.tab(name), s, e)

    def build_table(self, master, s, e):
        cols = ("ID", "Amount", "Category", "Description", "Date")
        tree = ttk.Treeview(master, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, pady=10)

        m, y = datetime.now().month, datetime.now().year
        data = self.db.execute("SELECT id, amount, category, description, date FROM expense WHERE user_id=%s AND MONTH(date)=%s AND YEAR(date)=%s AND DAY(date) BETWEEN %s AND %s", (self.user_id, m, y, s, e)).fetchall()
        for d in data: tree.insert("", "end", values=d)

        ctk.CTkButton(master, text="Delete Entry", fg_color="#e74c3c", command=lambda: self.delete(tree)).pack(pady=5)

    def delete(self, tree):
        selected = tree.selection()
        if not selected: return
        self.db.execute("DELETE FROM expense WHERE id=%s", (tree.item(selected[0])['values'][0],))
        self.db.commit()
        for w in self.container.winfo_children(): w.destroy()
        self.show()