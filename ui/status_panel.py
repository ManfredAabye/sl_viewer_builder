import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from ttkbootstrap import Frame


class StatusPanel(Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)

        self.output = ScrolledText(self, height=20, wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)

    def append(self, message: str) -> None:
        self.output.insert(tk.END, f"{message}\n")
        self.output.see(tk.END)
