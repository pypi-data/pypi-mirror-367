# Copyright (C) 2025 codimoc, codimoc@prismoid.uk

import tkinter as tk
from tkinter import VERTICAL, ttk
from pyrl_complete.apps import _context
from pyrl_complete.apps.notebook import create_notebook


def main():
    root = create_main_window()
    main_frame = create_main_frame(root)
    log_window = create_log_window(main_frame)
    notebook = create_notebook(main_frame)
    # position the notebook in the top part of main_frame..
    notebook.grid(row=0, column=0, sticky="nsew")
    # and the log in the bottom part
    log_window.grid(row=1, column=0, sticky="nsew")
    root.mainloop()


def create_main_window():
    root = tk.Tk()
    root.title("Rule tester")
    root.geometry("800x600")
    return root


def create_main_frame(root):
    main_frame = tk.Frame(root, background="lightyellow", padx=10, pady=10)
    main_frame.pack(fill="both", expand=True, padx=5, pady=5)
    main_frame.rowconfigure(0, weight=3)
    main_frame.rowconfigure(1, weight=1)
    main_frame.columnconfigure(0, weight=1)
    return main_frame


def create_log_window(parent):
    log_window = tk.Frame(parent, background="lightyellow")
    title = tk.Label(log_window, text="Log Activity", background="lightyellow")
    title.pack(padx=5, pady=5)
    scroll = ttk.Scrollbar(log_window, orient=VERTICAL)
    log_content = tk.Listbox(log_window, yscrollcommand=scroll.set)
    scroll.config(command=log_content.yview)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    log_content.pack(fill=tk.BOTH, expand=True)
    _context["log_content"] = log_content
    return log_window


if __name__ == "__main__":
    main()
