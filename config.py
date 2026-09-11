import os
import sys
import json
import ctypes
import tkinter as tk
from tkinter import messagebox

# DPI Awareness Setup
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DEBUG_MASK_FILE = os.path.join(BASE_DIR, "debug_mask_output.png")


def load_or_setup_hotkeys():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass

    root = tk.Tk()
    root.title("Hotkey Configuration")
    root.attributes('-topmost', True)

    screen_width = root.winfo_screenwidth()
    scale_factor = max(1.0, screen_width / 1920)
    root.tk.call('tk', 'scaling', scale_factor * 1.33)

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    tk.Label(
        main_frame,
        text="No config file found.\nPlease assign your preferred hotkeys:",
        justify="center"
    ).pack(pady=(0, 15))

    input_frame = tk.Frame(main_frame)
    input_frame.pack(pady=5)

    tk.Label(input_frame, text="Stop Key:").grid(row=0, column=0, sticky="e", padx=5, pady=4)
    entry_stop = tk.Entry(input_frame, width=10)
    entry_stop.insert(0, "f6")
    entry_stop.grid(row=0, column=1, pady=4)

    tk.Label(input_frame, text="Restart Key:").grid(row=1, column=0, sticky="e", padx=5, pady=4)
    entry_restart = tk.Entry(input_frame, width=10)
    entry_restart.insert(0, "f7")
    entry_restart.grid(row=1, column=1, pady=4)

    tk.Label(input_frame, text="Quit Key:").grid(row=2, column=0, sticky="e", padx=5, pady=4)
    entry_quit = tk.Entry(input_frame, width=10)
    entry_quit.insert(0, "q")
    entry_quit.grid(row=2, column=1, pady=4)

    hotkeys = {}

    def save_and_close():
        nonlocal hotkeys
        hotkeys = {
            "stop": entry_stop.get().strip().lower() or 'f6',
            "restart": entry_restart.get().strip().lower() or 'f7',
            "quit": entry_quit.get().strip().lower() or 'q'
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(hotkeys, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save configuration: {e}")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    tk.Button(main_frame, text="Save & Continue", command=save_and_close, padx=10, pady=5).pack(pady=(15, 0))

    root.update_idletasks()
    w, h = root.winfo_reqwidth(), root.winfo_reqheight()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.resizable(False, False)

    root.mainloop()
    if not hotkeys:
        sys.exit(0)
    return hotkeys