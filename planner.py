import customtkinter as ctk
import json
import os
from tkinter import Text, font

class PlannerView:
    def __init__(self, container):
        self.container = container
        self.db_path = "diary_rich_data.json"
        self.current_spread = 0
        self.total_pages = 50
        self.pages = {str(i): "" for i in range(1, 51)}
        self.load_data()

        self.colors = {
            "bg": "#020617",
            "accent": "#f59e0b",
            "essentials": "#3b82f6",
            "personal": "#f59e0b",
            "savings": "#10b981",
            "card": "#0f172a",
            "paper": "#fdfcf0",
            "cover": "#1e3a8a",
            "ink": "#1e293b",
            "margin": "#f87171",
            "rule": "#e2e4db",
            "highlight": "#fef08a"
        }

    def load_data(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    self.pages.update(json.load(f))
            except: pass

    def save_data(self):
        p1, p2 = str((self.current_spread*2)+1), str((self.current_spread*2)+2)
        try:
            self.pages[p1] = self.left_text.get("1.0", "end-1c")
            self.pages[p2] = self.right_text.get("1.0", "end-1c")
            with open(self.db_path, "w") as f:
                json.dump(self.pages, f)
        except: pass

    def show(self):
        self.main_scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # --- BUDGET SECTION (Top) ---
        self.render_budget_engine()

        # --- DIARY SECTION (Long Vertical) ---
        self.render_physical_diary()

    def render_budget_engine(self):
        header = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        header.pack(pady=(20, 10))
        ctk.CTkLabel(header, text="⚡ NEURAL", font=("Impact", 35), text_color=self.colors['accent']).pack(side="left")
        ctk.CTkLabel(header, text=" PLANNER", font=("Impact", 35), text_color="white").pack(side="left")

        input_card = ctk.CTkFrame(self.main_scroll, fg_color=self.colors['card'], corner_radius=20, border_width=1, border_color="#1e293b")
        input_card.pack(fill="x", padx=40, pady=10)

        self.period_var = ctk.StringVar(value="Monthly")
        ctk.CTkSegmentedButton(input_card, values=["Daily", "Monthly"], variable=self.period_var, selected_color=self.colors['accent']).pack(pady=10)

        self.amt_in = ctk.CTkEntry(input_card, placeholder_text="₹ Amount", width=200, height=40, font=("Arial", 16, "bold"), justify="center")
        self.amt_in.pack(pady=5)

        self.calc_btn = ctk.CTkButton(input_card, text="GENERATE ANALYSIS", fg_color=self.colors['accent'], text_color="black", command=self.run_simulation)
        self.calc_btn.pack(pady=15)

        self.res_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.res_frame.pack(fill="x", padx=60)
        self.bars = {}
        self.labels = {}
        for k, n, c in [("ess", "ESSENTIALS", "#3b82f6"), ("per", "PERSONAL", "#f59e0b"), ("sav", "SAVINGS", "#10b981")]:
            f = ctk.CTkFrame(self.res_frame, fg_color="transparent")
            f.pack(fill="x", pady=2)
            self.labels[k] = ctk.CTkLabel(f, text=f"{n}: ₹0", font=("Arial", 12, "bold"))
            self.labels[k].pack(side="left")
            self.bars[k] = ctk.CTkProgressBar(f, progress_color=c, height=8)
            self.bars[k].set(0)
            self.bars[k].pack(side="right", fill="x", expand=True, padx=(15, 0))

    def render_physical_diary(self):
        # Tools Header (Bold/Highlight)
        tool_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        tool_frame.pack(fill="x", padx=40, pady=(40, 0))
        
        ctk.CTkLabel(tool_frame, text="📓 DAILY JOURNAL", font=("Impact", 22), text_color=self.colors['accent']).pack(side="left")
        
        # Format Buttons
        ctk.CTkButton(tool_frame, text="B", width=30, font=("Arial", 13, "bold"), command=lambda: self.format_text("bold")).pack(side="right", padx=5)
        ctk.CTkButton(tool_frame, text="🖍", width=30, font=("Arial", 13), command=lambda: self.format_text("highlight")).pack(side="right", padx=5)

        # Nav
        nav = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        nav.pack(fill="x", padx=40, pady=5)
        ctk.CTkButton(nav, text="◀ FLIP", width=60, fg_color=self.colors['cover'], command=lambda: self.animate_flip(-1)).pack(side="left")
        self.pg_lbl = ctk.CTkLabel(nav, text="PGS 1-2", font=("Arial", 12, "bold"))
        self.pg_lbl.pack(side="left", expand=True)
        ctk.CTkButton(nav, text="FLIP ▶", width=60, fg_color=self.colors['cover'], command=lambda: self.animate_flip(1)).pack(side="right")

        # LONG VERTICAL COVER
        self.book_cover = ctk.CTkFrame(self.main_scroll, fg_color=self.colors['cover'], corner_radius=15, height=700)
        self.book_cover.pack(fill="x", padx=40, pady=10)
        self.book_cover.pack_propagate(False)

        self.spread = ctk.CTkFrame(self.book_cover, fg_color="transparent")
        self.spread.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_page = self.draw_page(self.spread, "left")
        ctk.CTkFrame(self.spread, width=2, fg_color="#000").pack(side="left", fill="y")
        self.right_page = self.draw_page(self.spread, "right")

        self.load_spread_text()

    def draw_page(self, parent, side):
        canvas = ctk.CTkCanvas(parent, bg=self.colors['paper'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        # Header logic
        canvas.create_rectangle(20, 20, 80, 45, fill="#4b5563", outline="")
        canvas.create_text(50, 32, text="NOTES", fill="white", font=("Arial", 10, "bold"))
        canvas.create_text(240, 32, text="Date: ...................", fill="#9ca3af")

        # LONG RULING
        for y in range(65, 700, 28):
            canvas.create_line(20, y, 400, y, fill=self.colors['rule'])
        canvas.create_line(18, 0, 18, 700, fill=self.colors['margin'], width=1)

        # Text Widget with Formatting Support
        txt = Text(canvas, bg=self.colors['paper'], fg=self.colors['ink'], borderwidth=0, 
                   font=("Comic Sans MS", 13), padx=20, spacing3=10, undo=True, highlightthickness=0)
        canvas.create_window(0, 60, window=txt, anchor="nw", width=340, height=640)

        # Configure Tags
        txt.tag_configure("bold", font=("Comic Sans MS", 13, "bold"))
        txt.tag_configure("highlight", background="#fde047")

        if side == "left": self.left_text = txt
        else: self.right_text = txt
        return canvas

    def format_text(self, tag):
        try:
            widget = self.container.focus_get()
            if isinstance(widget, Text):
                current_tags = widget.tag_names("sel.first")
                if tag in current_tags: widget.tag_remove(tag, "sel.first", "sel.last")
                else: widget.tag_add(tag, "sel.first", "sel.last")
        except: pass

    def animate_flip(self, direction):
        self.save_data()
        
        # Quick Flip Animation Effect
        def shrink(step):
            if step > 0:
                self.spread.pack_forget()
                self.container.after(20, lambda: expand(step-1))
            else:
                self.flip_logic(direction)
                self.spread.pack(fill="both", expand=True, padx=10, pady=10)

        def expand(step):
            shrink(0) # Logic sequence to update text while hidden

        shrink(5)

    def flip_logic(self, direction):
        new_val = self.current_spread + direction
        if 0 <= new_val < (self.total_pages // 2):
            self.current_spread = new_val
            self.load_spread_text()

    def load_spread_text(self):
        p1, p2 = str((self.current_spread*2)+1), str((self.current_spread*2)+2)
        for t, p in [(self.left_text, p1), (self.right_text, p2)]:
            t.delete("1.0", "end")
            t.insert("1.0", self.pages.get(p, ""))
        self.pg_lbl.configure(text=f"PGS {p1}-{p2}")

    def run_simulation(self):
        try:
            v = float(self.amt_in.get())
            self.calc_btn.configure(state="disabled", text="ANALYZING...")
            self.container.after(600, lambda: self.animate_results(v))
        except: pass

    def animate_results(self, val):
        v_ess, v_per, v_sav = val*0.5, val*0.3, val*0.2
        for i in range(21):
            r = i/20
            self.container.after(i*25, lambda ratio=r: self.update_bars(ratio, v_ess, v_per, v_sav))
        self.calc_btn.configure(state="normal", text="RE-GENERATE")

    def update_bars(self, r, e, p, s):
        self.bars['ess'].set(r*0.5*2)
        self.bars['per'].set(r*0.3*3.3)
        self.bars['sav'].set(r*0.2*5)
        self.labels['ess'].configure(text=f"ESSENTIALS: ₹{int(e*r)}")
        self.labels['per'].configure(text=f"PERSONAL:  ₹{int(p*r)}")
        self.labels['sav'].configure(text=f"SAVINGS:   ₹{int(s*r)}")