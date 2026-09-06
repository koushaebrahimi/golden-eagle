# -*- coding: utf-8 -*-
"""
Golden Eagle - Daily Work Time Recording System
Complete final version with logo banner, bilingual UI, and auto-sum subtasks.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import re
import sys
import json

from golden_eagle_core import (
    create_empty_day_record, get_date_key, load_all_days, save_all_days,
    validate_day, sum_task_hours, get_total_actual_hours, compute_shortfall_overwork,
    generate_monthly_report, DATA_FILE
)

from lang import _, set_language, get_weekdays, get_day_types, get_suggested_tasks

# ========== Language Selection ==========
LANG_FILE = "golden_eagle_lang.json"

def load_language():
    try:
        with open(LANG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('language', 'persian')
    except:
        return 'persian'

def save_language(lang):
    try:
        with open(LANG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'language': lang}, f)
    except:
        pass

# ========== Font Detection ==========
def get_font():
    if sys.platform == "win32":
        return "Tahoma"
    return "Helvetica"

# ========== Time conversion ==========
def time_to_float(t: str) -> float:
    if not t or not t.strip():
        return 0.0
    t = t.strip()
    if re.match(r'^\d{1,2}:\d{2}$', t):
        h, m = map(int, t.split(':'))
        return h + m/60.0
    try:
        return float(t)
    except:
        return 0.0

def float_to_time(hours: float) -> str:
    if hours <= 0:
        return "00:00"
    h = int(hours)
    m = int(round((hours - h) * 60))
    if m == 60:
        h += 1
        m = 0
    return f"{h:02d}:{m:02d}"

def is_valid_time(t: str) -> bool:
    if not t or not t.strip():
        return False
    return bool(re.match(r'^\d{1,2}:\d{2}$', t.strip()))

# ========== Main Application ==========
class GoldenEagleApp(tk.Tk):
    def __init__(self, language='persian'):
        super().__init__()
        
        set_language(language)
        save_language(language)
        
        self.title("GOLDEN EAGLE")
        self.geometry("1100x850")
        self.minsize(1000, 800)
        
        self.font_family = get_font()
        print(f"✅ Using font: {self.font_family}")
        print(f"✅ Language: {language}")
        
        self.default_font = (self.font_family, 14)
        self.option_add('*Font', self.default_font)
        
        style = ttk.Style()
        style.configure("TLabel", font=(self.font_family, 14))
        style.configure("TButton", font=(self.font_family, 13))
        style.configure("TEntry", font=(self.font_family, 14))
        style.configure("TCombobox", font=(self.font_family, 14))
        style.configure("TSpinbox", font=(self.font_family, 14))
        style.configure("Treeview", font=(self.font_family, 13), rowheight=35)
        style.configure("Treeview.Heading", font=(self.font_family, 13, "bold"))
        style.configure("TLabelframe.Label", font=(self.font_family, 15, "bold"))
        
        self.all_records = load_all_days()
        self.current_record = None
        self.current_date_key = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        # ===== GOLDEN EAGLE BANNER =====
        banner_frame = ttk.Frame(main)
        banner_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo text with gold color
        logo_label = tk.Label(
            banner_frame, 
            text="🦅 GOLDEN EAGLE", 
            font=(self.font_family, 28, "bold"),
            foreground="#b7950b"  # Gold color
        )
        logo_label.pack(pady=5)
        
        # Subtitle
        subtitle = tk.Label(
            banner_frame,
            text=_("Daily Work Time Recording System"),
            font=(self.font_family, 12),
            foreground="#5d6d7e"
        )
        subtitle.pack()
        
        # Separator line
        ttk.Separator(main, orient='horizontal').pack(fill=tk.X, pady=5)
        # ===== END BANNER =====
        
        # ===== Top Section =====
        top_frame = ttk.LabelFrame(main, text=_("Day Information"), padding=15)
        top_frame.pack(fill=tk.X, pady=8)
        
        row1 = ttk.Frame(top_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text=_("Date (Day/Month/Year):")).pack(side=tk.LEFT, padx=5)
        self.day_spin = ttk.Spinbox(row1, from_=1, to=31, width=6)
        self.day_spin.pack(side=tk.LEFT, padx=2)
        ttk.Label(row1, text="/").pack(side=tk.LEFT)
        self.month_spin = ttk.Spinbox(row1, from_=1, to=12, width=6)
        self.month_spin.pack(side=tk.LEFT, padx=2)
        ttk.Label(row1, text="/").pack(side=tk.LEFT)
        self.year_spin = ttk.Spinbox(row1, from_=1390, to=1450, width=8)
        self.year_spin.pack(side=tk.LEFT, padx=2)
        self.year_spin.set("1403")
        
        ttk.Label(row1, text=_("Weekday:")).pack(side=tk.LEFT, padx=(20,5))
        self.weekday_var = tk.StringVar()
        self.weekday_cb = ttk.Combobox(row1, textvariable=self.weekday_var, values=get_weekdays(), width=12, state="readonly")
        self.weekday_cb.pack(side=tk.LEFT, padx=2)
        
        row2 = ttk.Frame(top_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text=_("Day Type:")).pack(side=tk.LEFT, padx=5)
        self.day_type_var = tk.StringVar(value=get_day_types()[0])
        self.day_type_cb = ttk.Combobox(row2, textvariable=self.day_type_var, values=get_day_types(), width=14, state="readonly")
        self.day_type_cb.pack(side=tk.LEFT, padx=2)
        self.day_type_cb.bind("<<ComboboxSelected>>", self._on_day_type_change)
        
        ttk.Label(row2, text=_("In Time:")).pack(side=tk.LEFT, padx=(20,5))
        self.in_entry = ttk.Entry(row2, width=10)
        self.in_entry.pack(side=tk.LEFT, padx=2)
        self.in_entry.insert(0, "08:00")
        
        ttk.Label(row2, text=_("Out Time:")).pack(side=tk.LEFT, padx=(20,5))
        self.out_entry = ttk.Entry(row2, width=10)
        self.out_entry.pack(side=tk.LEFT, padx=2)
        self.out_entry.insert(0, "16:00")
        
        row3 = ttk.Frame(top_frame)
        row3.pack(fill=tk.X, pady=8)
        ttk.Button(row3, text=_("Load Day"), command=self._load_day, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text=_("Save Day"), command=self._save_day, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text=_("Delete Day"), command=self._delete_day, width=14).pack(side=tk.LEFT, padx=5)
        
        # ===== Middle: Treeview =====
        task_frame = ttk.LabelFrame(main, text=_("Tasks and Subtasks"), padding=15)
        task_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        
        # Fixed column identifiers (never translated)
        columns = ("Row", "Name", "Hours", "Description")
        self.tree = ttk.Treeview(task_frame, columns=columns, show="tree headings", height=12)
        
        # Set headings with translated text
        self.tree.heading("Row", text=_("Row"))
        self.tree.heading("Name", text=_("Name"))
        self.tree.heading("Hours", text=_("Hours (HH:MM)"))
        self.tree.heading("Description", text=_("Description"))
        
        # Configure columns
        self.tree.column("Row", width=70, anchor="center")
        self.tree.column("Name", width=220, anchor="w")
        self.tree.column("Hours", width=130, anchor="center")
        self.tree.column("Description", width=330, anchor="w")
        
        vsb = ttk.Scrollbar(task_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        hsb = ttk.Scrollbar(task_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        task_frame.grid_rowconfigure(0, weight=1)
        task_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        ctrl_frame = ttk.Frame(task_frame)
        ctrl_frame.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")
        ttk.Button(ctrl_frame, text=_("Add Task"), command=self._add_task, width=14).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text=_("Add Subtask"), command=self._add_subtask, width=14).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text=_("Delete Row"), command=self._delete_row, width=14).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text=_("Edit Row"), command=self._edit_row, width=14).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text=_("Auto-calc Task Hours"), command=self._auto_calc_task_hours, width=20).pack(side=tk.LEFT, padx=3)
        
        # ===== Bottom =====
        bottom_frame = ttk.Frame(main)
        bottom_frame.pack(fill=tk.X, pady=8)
        
        self.status_label = ttk.Label(bottom_frame, text=_("Status: Ready"), foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(bottom_frame, text=_("Monthly Report"), command=self._monthly_report, width=16).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text=_("Check Consistency"), command=self._check_consistency, width=16).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text=_("View All Days"), command=self._view_all_days, width=16).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text=_("Exit"), command=self.quit, width=12).pack(side=tk.RIGHT, padx=5)
    
    # ========== Helper Methods ==========
    def _get_date_from_entries(self):
        try:
            d = int(self.day_spin.get())
            m = int(self.month_spin.get())
            y = int(self.year_spin.get())
            if 1 <= d <= 31 and 1 <= m <= 12:
                return y, m, d
        except:
            pass
        return None, None, None
    
    def _get_date_key_from_entries(self):
        y, m, d = self._get_date_from_entries()
        if y and m and d:
            return f"{y:04d}-{m:02d}-{d:02d}"
        return None
    
    def _load_day(self):
        key = self._get_date_key_from_entries()
        if not key:
            messagebox.showerror(_("Error"), _("Invalid date."))
            return
        if key in self.all_records:
            self.current_record = self.all_records[key]
            self.current_date_key = key
            self._populate_form(self.current_record)
            self.status_label.config(text=f"Status: Day {key} loaded.", foreground="green")
        else:
            if messagebox.askyesno(_("Not Found"), f"Day {key} does not exist. Create a new day?"):
                self.current_record = None
                self.current_date_key = None
                self._clear_form()
                y, m, d = self._get_date_from_entries()
                self.day_spin.set(str(d))
                self.month_spin.set(str(m))
                self.year_spin.set(str(y))
                self.weekday_var.set("")
                self.day_type_var.set(get_day_types()[0])
                self.status_label.config(text="Status: New day", foreground="blue")
            else:
                self.status_label.config(text="Status: Cancelled", foreground="orange")
    
    def _populate_form(self, rec):
        self.day_spin.set(str(rec["day"]))
        self.month_spin.set(str(rec["month"]))
        self.year_spin.set(str(rec["year"]))
        self.weekday_var.set(rec.get("weekday", ""))
        
        day_type_persian = rec.get("day_type", "")
        if get_language() == 'persian':
            self.day_type_var.set(day_type_persian)
        else:
            day_map = {"عادی": "Normal", "مرخصی": "Leave", "تعطیل رسمی": "Holiday", "اضافه کار": "Overtime", "دورکاری": "Remote"}
            self.day_type_var.set(day_map.get(day_type_persian, "Normal"))
        
        self.in_entry.delete(0, tk.END)
        self.in_entry.insert(0, rec.get("in_time", ""))
        self.out_entry.delete(0, tk.END)
        self.out_entry.insert(0, rec.get("out_time", ""))
        self._clear_tree()
        for task in rec.get("tasks", []):
            self._insert_task(task)
        self._on_day_type_change()
    
    def _clear_form(self):
        self.day_spin.set("")
        self.month_spin.set("")
        self.year_spin.set("")
        self.weekday_var.set("")
        self.day_type_var.set(get_day_types()[0])
        self.in_entry.delete(0, tk.END)
        self.out_entry.delete(0, tk.END)
        self._clear_tree()
    
    def _clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    # ========== TASK INSERTION ==========
    def _insert_task(self, task_dict, parent=""):
        """Insert a task dict into tree, displaying hours as HH:MM."""
        name = task_dict.get("name", "")
        hours = task_dict.get("hours", 0.0)
        desc = task_dict.get("description", "")
        subtasks = task_dict.get("subtasks", [])
        
        # Insert the parent task
        time_str = float_to_time(hours)
        values = ("", name, time_str, desc)
        item = self.tree.insert(parent, "end", values=values)
        
        # Insert subtasks
        for sub in subtasks:
            sub_name = sub.get("name", "")
            sub_hours = sub.get("hours", 0.0)
            sub_desc = sub.get("description", "")
            sub_time_str = float_to_time(sub_hours)
            self.tree.insert(item, "end", values=("", sub_name, sub_time_str, sub_desc))
        
        # Auto-calculate parent hours from subtasks
        if subtasks:
            total_sub = sum(sub.get("hours", 0.0) for sub in subtasks)
            self.tree.set(item, "Hours", float_to_time(total_sub))
            self._update_task_hours_in_tree(item, total_sub)
        
        self._update_row_numbers()
    
    def _update_task_hours_in_tree(self, item, hours):
        """Update the hours value stored in the tree item."""
        values = list(self.tree.item(item, "values"))
        values[2] = float_to_time(hours)
        self.tree.item(item, values=values)
    
    def _update_row_numbers(self):
        counter = 0
        def recurse(parent=""):
            nonlocal counter
            for child in self.tree.get_children(parent):
                counter += 1
                self.tree.set(child, "Row", str(counter))
                recurse(child)
        recurse()
    
    def _get_task_dict_from_tree(self, item):
        name = self.tree.item(item, "values")[1]
        hours_str = self.tree.item(item, "values")[2]
        hours = time_to_float(hours_str)
        desc = self.tree.item(item, "values")[3]
        subtasks = []
        for child in self.tree.get_children(item):
            sub_name = self.tree.item(child, "values")[1]
            sub_hours_str = self.tree.item(child, "values")[2]
            sub_hours = time_to_float(sub_hours_str)
            sub_desc = self.tree.item(child, "values")[3]
            subtasks.append({"name": sub_name, "hours": sub_hours, "description": sub_desc})
        return {"name": name, "hours": hours, "description": desc, "subtasks": subtasks}
    
    def _collect_tasks_from_tree(self):
        tasks = []
        for child in self.tree.get_children(""):
            task = self._get_task_dict_from_tree(child)
            if task["subtasks"]:
                total = sum(sub["hours"] for sub in task["subtasks"])
                task["hours"] = total
            tasks.append(task)
        return tasks
    
    def _auto_calc_task_hours(self):
        """Recalculate all parent task hours from their subtasks."""
        for child in self.tree.get_children(""):
            task = self._get_task_dict_from_tree(child)
            if task["subtasks"]:
                total = sum(sub["hours"] for sub in task["subtasks"])
                self.tree.set(child, "Hours", float_to_time(total))
                self._update_task_hours_in_tree(child, total)
        self.status_label.config(text="Status: Task hours updated.", foreground="green")
    
    # ========== Task Management ==========
    def _add_task(self):
        dialog = tk.Toplevel(self)
        dialog.title(_("Add Task"))
        dialog.geometry("400x220")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text=_("Task Name:")).pack(pady=5)
        name_var = tk.StringVar()
        combo = ttk.Combobox(dialog, textvariable=name_var, values=get_suggested_tasks(), state="normal", width=30)
        combo.pack(pady=5)
        
        ttk.Label(dialog, text=_("Hours (optional):")).pack(pady=5)
        hours_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=hours_var, width=10).pack(pady=5)
        
        ttk.Label(dialog, text="⚠️ If you add subtasks later, parent hours will be auto-calculated.", 
                  font=("Helvetica", 10), foreground="orange").pack()
        
        def add():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror(_("Error"), "Task name cannot be empty.")
                return
            hours = time_to_float(hours_var.get())
            new_task = {"name": name, "hours": hours, "description": "", "subtasks": []}
            self._insert_task(new_task)
            dialog.destroy()
        
        ttk.Button(dialog, text=_("Add"), command=add, width=12).pack(pady=10)
    
    def _add_subtask(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror(_("Error"), "Please select a main task.")
            return
        parent = selected[0]
        if self.tree.parent(parent) != "":
            messagebox.showerror(_("Error"), "Subtask can only be added to a main task.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title(_("Add Subtask"))
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text=_("Subtask Name:")).pack(pady=5)
        name_var = tk.StringVar()
        combo = ttk.Combobox(dialog, textvariable=name_var, values=get_suggested_tasks(), state="normal", width=30)
        combo.pack(pady=5)
        
        ttk.Label(dialog, text=_("Hours:")).pack(pady=5)
        hours_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=hours_var, width=10).pack(pady=5)
        
        def add():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror(_("Error"), "Subtask name cannot be empty.")
                return
            hours = time_to_float(hours_var.get())
            # Insert subtask
            self.tree.insert(parent, "end", values=("", name, float_to_time(hours), ""))
            self._update_row_numbers()
            self._auto_calc_task_hours()
            dialog.destroy()
        
        ttk.Button(dialog, text=_("Add"), command=add, width=12).pack(pady=10)
    
    def _delete_row(self):
        selected = self.tree.selection()
        if not selected:
            return
        if messagebox.askyesno(_("Delete"), "Are you sure you want to delete the selected row(s)?"):
            for item in selected:
                self.tree.delete(item)
            self._update_row_numbers()
            self._auto_calc_task_hours()
    
    def _edit_row(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        values = self.tree.item(item, "values")
        
        dialog = tk.Toplevel(self)
        dialog.title(_("Edit Row"))
        dialog.geometry("450x250")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text=_("Name:")).grid(row=0, column=0, padx=5, pady=8, sticky="e")
        name_var = tk.StringVar(value=values[1])
        ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=5, pady=8)
        
        ttk.Label(dialog, text=_("Hours (HH:MM):")).grid(row=1, column=0, padx=5, pady=8, sticky="e")
        hours_var = tk.StringVar(value=values[2])
        ttk.Entry(dialog, textvariable=hours_var, width=10).grid(row=1, column=1, padx=5, pady=8, sticky="w")
        
        ttk.Label(dialog, text=_("Description:")).grid(row=2, column=0, padx=5, pady=8, sticky="e")
        desc_var = tk.StringVar(value=values[3])
        ttk.Entry(dialog, textvariable=desc_var, width=30).grid(row=2, column=1, padx=5, pady=8)
        
        has_children = len(self.tree.get_children(item)) > 0
        if has_children:
            ttk.Label(dialog, text="⚠️ This task has subtasks, hours are calculated automatically.", 
                      font=("Helvetica", 10), foreground="orange").grid(row=3, column=0, columnspan=2, pady=8)
        
        def save_edit():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showerror(_("Error"), "Name cannot be empty.")
                return
            new_hours = time_to_float(hours_var.get())
            new_desc = desc_var.get().strip()
            
            has_children = len(self.tree.get_children(item)) > 0
            if has_children:
                # If task has subtasks, ignore hours input and auto-calc
                self.tree.item(item, values=("", new_name, values[2], new_desc))
                self._auto_calc_task_hours()
            else:
                self.tree.item(item, values=("", new_name, float_to_time(new_hours), new_desc))
            
            self._update_row_numbers()
            dialog.destroy()
        
        ttk.Button(dialog, text=_("Save"), command=save_edit, width=12).grid(row=4, column=0, columnspan=2, pady=12)
    
    # ========== Day Type Change ==========
    def _on_day_type_change(self, event=None):
        dt = self.day_type_var.get()
        if get_language() == 'persian':
            leave = "مرخصی"
            holiday = "تعطیل رسمی"
        else:
            leave = "Leave"
            holiday = "Holiday"
        
        if dt in (holiday, leave):
            self.in_entry.config(state="disabled")
            self.out_entry.config(state="disabled")
            if dt == leave:
                if messagebox.askyesno(_("Leave"), "Leave days usually have no tasks. Clear tasks?"):
                    self._clear_tree()
            elif dt == holiday:
                self._clear_tree()
        else:
            self.in_entry.config(state="normal")
            self.out_entry.config(state="normal")
    
    # ========== Save / Delete ==========
    def _save_day(self):
        y, m, d = self._get_date_from_entries()
        if not (y and m and d):
            messagebox.showerror(_("Error"), _("Invalid date."))
            return
        key = get_date_key({"year": y, "month": m, "day": d})
        weekday = self.weekday_var.get()
        day_type_ui = self.day_type_var.get()
        
        if get_language() == 'persian':
            day_type = day_type_ui
        else:
            day_map = {"Normal": "عادی", "Leave": "مرخصی", "Holiday": "تعطیل رسمی", "Overtime": "اضافه کار", "Remote": "دورکاری"}
            day_type = day_map.get(day_type_ui, "عادی")
        
        in_time = self.in_entry.get().strip()
        out_time = self.out_entry.get().strip()
        
        if get_language() == 'persian':
            normal_types = ("عادی", "اضافه کار")
        else:
            normal_types = ("Normal", "Overtime")
        
        if day_type_ui in normal_types:
            if not (is_valid_time(in_time) and is_valid_time(out_time)):
                messagebox.showerror(_("Error"), "Invalid in/out time (format HH:MM).")
                return
        
        tasks = self._collect_tasks_from_tree()
        
        record = create_empty_day_record(
            year=y, month=m, day=d,
            weekday=weekday,
            day_type=day_type,
            in_time=in_time,
            out_time=out_time,
            tasks=tasks
        )
        
        valid, errors = validate_day(record)
        if not valid:
            if not messagebox.askyesno(_("Error"), "Inconsistencies:\n" + "\n".join(errors) + "\nSave anyway?"):
                return
        
        if key in self.all_records and not messagebox.askyesno(_("Confirm"), f"Day {key} already exists. Overwrite?"):
            return
        
        self.all_records[key] = record
        save_all_days(self.all_records)
        self.current_record = record
        self.current_date_key = key
        self.status_label.config(text=f"Status: Day {key} saved.", foreground="green")
        messagebox.showinfo(_("Success"), _("Day saved successfully."))
    
    def _delete_day(self):
        key = self._get_date_key_from_entries()
        if not key:
            return
        if key not in self.all_records:
            messagebox.showerror(_("Error"), _("Day not found in database."))
            return
        if messagebox.askyesno(_("Delete"), f"Are you sure you want to delete day {key}?"):
            del self.all_records[key]
            save_all_days(self.all_records)
            self._clear_form()
            self.status_label.config(text=f"Status: Day {key} deleted.", foreground="orange")
    
    # ========== Consistency Check ==========
    def _check_consistency(self):
        key = self._get_date_key_from_entries()
        if not key:
            return
        if key not in self.all_records:
            messagebox.showerror(_("Error"), _("Day not found in database."))
            return
        rec = self.all_records[key]
        valid, errors = validate_day(rec)
        actual = get_total_actual_hours(rec)
        task_sum = sum_task_hours(rec)
        short, over = compute_shortfall_overwork(rec)
        
        msg = f"Actual hours: {actual:.2f}\nTotal task hours: {task_sum:.2f}\nShortfall: {short:.2f}\nOverwork: {over:.2f}"
        if valid:
            msg += "\nStatus: Consistent."
        else:
            msg += "\nStatus: Errors:\n" + "\n".join(errors)
            if abs(task_sum - actual) > 0.01 and messagebox.askyesno("Inconsistency", "Add remaining hours to 'Hourly Leave'?"):
                residual = actual - task_sum
                if residual > 0:
                    new_task = {"name": "Hourly Leave", "hours": residual, "description": "Auto-added", "subtasks": []}
                    self.all_records[key]["tasks"].append(new_task)
                    save_all_days(self.all_records)
                    messagebox.showinfo(_("Done"), f"{residual:.2f} hours added to 'Hourly Leave'.")
                    self._load_day()
        messagebox.showinfo(_("Consistency Check"), msg)
    
    # ========== View All Days ==========
    def _view_all_days(self):
        if not self.all_records:
            messagebox.showinfo(_("Information"), _("No days recorded."))
            return
        
        window = tk.Toplevel(self)
        window.title(_("View All Days"))
        window.geometry("1100x600")
        window.transient(self)
        
        columns = (_("Date"), _("Day Type"), _("In Time"), _("Out Time"), _("Total Hours"), _("Shortfall"), _("Overwork"), _("Task Count"))
        tree = ttk.Treeview(window, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor="center")
        
        vsb = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        sorted_records = sorted(self.all_records.values(), key=lambda r: (r["year"], r["month"], r["day"]))
        
        for rec in sorted_records:
            date_str = f"{rec['day']}/{rec['month']}/{rec['year']}"
            day_type = rec.get("day_type", "")
            in_time = rec.get("in_time", "")
            out_time = rec.get("out_time", "")
            actual = get_total_actual_hours(rec)
            short, over = compute_shortfall_overwork(rec)
            task_count = len(rec.get("tasks", []))
            tree.insert("", "end", values=(
                date_str, day_type, in_time, out_time,
                f"{actual:.2f}", f"{short:.2f}", f"{over:.2f}", task_count
            ))
        
        ttk.Button(window, text=_("Close"), command=window.destroy, width=12).pack(pady=12)
    
    # ========== Monthly Report ==========
    def _monthly_report(self):
        month = simpledialog.askinteger(_("Report"), _("Month (number):"), minvalue=1, maxvalue=12)
        if not month:
            return
        year = simpledialog.askinteger(_("Report"), _("Year:"), minvalue=1390, maxvalue=1450)
        if not year:
            return
        csv_data, pdf_data = generate_monthly_report(year, month, self.all_records)
        if csv_data is None:
            messagebox.showinfo(_("Report"), _("No data for this month."))
            return
        save_csv = messagebox.askyesno(_("Save CSV"), _("Save CSV file?"))
        save_pdf = False
        if pdf_data is not None:
            save_pdf = messagebox.askyesno(_("Save PDF"), _("Save PDF file?"))
        if save_csv:
            file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file:
                with open(file, "w", encoding="utf-8-sig") as f:
                    f.write(csv_data)
                messagebox.showinfo(_("Success"), _("CSV saved."))
        if save_pdf and pdf_data:
            file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if file:
                with open(file, "wb") as f:
                    f.write(pdf_data)
                messagebox.showinfo(_("Success"), _("PDF saved."))
        if not (save_csv or (save_pdf and pdf_data)):
            messagebox.showinfo(_("Cancelled"), _("Report not saved."))

# ========== Run ==========
if __name__ == "__main__":
    # Simple language selection
    import tkinter.simpledialog as simpledialog
    
    temp_root = tk.Tk()
    temp_root.withdraw()
    
    lang_choice = simpledialog.askstring(
        "Language / زبان",
        "Enter 'english' or 'persian':\n\n"
        "English: type 'english'\n"
        "فارسی: نوع 'persian'",
        parent=temp_root
    )
    
    temp_root.destroy()
    
    if lang_choice is None or lang_choice.lower() not in ['english', 'persian']:
        lang_choice = 'persian'
    
    app = GoldenEagleApp(language=lang_choice.lower())
    app.mainloop()