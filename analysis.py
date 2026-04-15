import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from fpdf import FPDF

class AnalysisView:
    def __init__(self, container, db, user_id):
        self.container, self.db, self.user_id = container, db, user_id
        self.tabs_map = {} # To keep track of tables across tabs

    def show(self):
        # 1. HEADER SECTION
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(30, 10))
        
        ctk.CTkLabel(header, text="📊 TRANSACTION LEDGER", font=("Impact", 32), text_color="#3b82f6").pack(side="left")
        
        # Action Buttons
        btn_f = ctk.CTkFrame(header, fg_color="transparent")
        btn_f.pack(side="right")

        ctk.CTkButton(btn_f, text="📄 EXPORT PDF", width=120, fg_color="#00ff99", text_color="black", 
                      font=("Arial", 12, "bold"), command=self.export_pdf).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_f, text="❌ DELETE SELECTED", width=120, fg_color="#ef4444", 
                      font=("Arial", 12, "bold"), command=self.delete_item).pack(side="left", padx=5)

        # 2. THEME THE TABLE (Force Dark Mode)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#070b14", 
                        foreground="white", 
                        fieldbackground="#070b14", 
                        rowheight=35, 
                        borderwidth=0, 
                        font=("Arial", 11))
        style.configure("Treeview.Heading", background="#1e293b", foreground="white", borderwidth=0, font=("Arial", 12, "bold"))
        style.map("Treeview", background=[('selected', '#3b82f6')])

        # 3. WEEK-WISE PHASES (TABS)
        self.tabs = ctk.CTkTabview(self.container, fg_color="#070b14", border_width=2, border_color="#1e293b",
                                   segmented_button_selected_color="#3b82f6",
                                   segmented_button_unselected_hover_color="#1e293b")
        self.tabs.pack(fill="both", expand=True, padx=40, pady=20)
        
        phases = [("Week 1 (1-7)", 1, 7), ("Week 2 (8-14)", 8, 14), ("Week 3 (15-21)", 15, 21), ("Week 4 (22-31)", 22, 31)]
        
        for name, s, e in phases:
            tab = self.tabs.add(name)
            self.create_phase_table(tab, s, e, name)

    def create_phase_table(self, master, start_day, end_day, name):
        cols = ("ID", "Amount", "Category", "Note", "Date")
        tree = ttk.Treeview(master, columns=cols, show="headings", height=12)
        
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tabs_map[name] = {"tree": tree, "start": start_day, "end": end_day}
        self.refresh_phase(name)

    def refresh_phase(self, name):
        tab_data = self.tabs_map[name]
        tree, s, e = tab_data["tree"], tab_data["start"], tab_data["end"]
        
        # Clear current rows
        for item in tree.get_children(): tree.delete(item)
        
        # Fetch filtered data
        month = datetime.now().month
        self.db.execute("SELECT id, amount, category, description, date FROM expense "
                        "WHERE user_id=%s AND MONTH(date)=%s AND DAY(date) BETWEEN %s AND %s ORDER BY date DESC", 
                        (self.user_id, month, s, e))
        
        for row in self.db.cursor.fetchall():
            tree.insert("", "end", values=row)

    def delete_item(self):
        # Get active tab's table
        current_tab_name = self.tabs.get()
        tree = self.tabs_map[current_tab_name]["tree"]
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please click on a row to delete.")
            return
            
        item_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Permanently remove transaction #{item_id}?"):
            self.db.execute("DELETE FROM expense WHERE id=%s", (item_id,))
            self.db.commit()
            self.refresh_phase(current_tab_name) # Auto refresh current tab

    def export_pdf(self):
        try:
            self.db.execute("SELECT date, category, amount, description FROM expense WHERE user_id=%s ORDER BY date DESC", (self.user_id,))
            rows = self.db.cursor.fetchall()
            
            pdf = FPDF()
            pdf.add_page()
            
            # Title Box
            pdf.set_fill_color(30, 41, 59) # Navy Blue
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 15, "WEALTHWISE FINANCIAL AUDIT LOG", 0, 1, 'C', 1)
            
            pdf.ln(10)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", 'B', 12)
            
            # Table Header
            pdf.cell(30, 10, "DATE", 1)
            pdf.cell(40, 10, "CATEGORY", 1)
            pdf.cell(30, 10, "AMOUNT", 1)
            pdf.cell(90, 10, "DESCRIPTION", 1)
            pdf.ln()
            
            pdf.set_font("Arial", '', 10)
            for r in rows:
                pdf.cell(30, 10, str(r[0]), 1)
                pdf.cell(40, 10, str(r[1]), 1)
                pdf.cell(30, 10, f"Rs.{r[2]}", 1)
                pdf.cell(90, 10, str(r[3]), 1)
                pdf.ln()
            
            pdf.output("My_Wealth_Report.pdf")
            messagebox.showinfo("Exported", "High-priority financial report generated and saved locally.")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Ensure all libraries are installed. Error: {e}")