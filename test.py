# -*- coding: utf-8 -*-
"""
Simple Tkinter test app.
"""

import tkinter as tk
from tkinter import ttk

class TestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tkinter Test")
        self.root.geometry("400x300")
        
        # Label
        label = tk.Label(self.root, text="✅ Tkinter is working!", font=("Helvetica", 20))
        label.pack(pady=50)
        
        # Button
        button = ttk.Button(self.root, text="Click Me", command=self.on_click)
        button.pack(pady=20)
        
        # Status
        self.status = tk.Label(self.root, text="Ready", font=("Helvetica", 12))
        self.status.pack(pady=10)
        
        self.root.mainloop()
    
    def on_click(self):
        self.status.config(text="Button clicked! 🎉")

if __name__ == "__main__":
    app = TestApp()
