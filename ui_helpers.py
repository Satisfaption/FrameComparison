import cv2
import ctypes
from tkinter import filedialog
import tkinter as tk


def select_target_file():
    """Prompts the user to pick a target frame image file."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.askopenfilename(
        title="Select Clean Target Frame Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("All Files", "*.*")]
    )
    root.destroy()
    return path


def minimize_cv_window(window_name):
    """Minimizes the specified OpenCV window to the taskbar."""
    hwnd = ctypes.windll.user32.FindWindowW(None, window_name)
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 6)


def restore_cv_window_background(window_name):
    """Restores the OpenCV window without stealing active focus."""
    hwnd = ctypes.windll.user32.FindWindowW(None, window_name)
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 4)


def is_window_closed(window_name):
    """Safely checks if the OpenCV window was closed by the user."""
    try:
        return cv2.getWindowProperty(window_name, cv2.WND_PROP_AUTOSIZE) < 0
    except cv2.error:
        return True


# --- DRAG REGION SELECTION TOOL ---
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def get_physical_cursor():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def select_screen_region():
    v_left = ctypes.windll.user32.GetSystemMetrics(76)
    v_top = ctypes.windll.user32.GetSystemMetrics(77)
    v_width = ctypes.windll.user32.GetSystemMetrics(78)
    v_height = ctypes.windll.user32.GetSystemMetrics(79)

    root = tk.Tk()
    root.attributes('-alpha', 0.5)
    root.attributes('-topmost', True)
    root.config(cursor="none")
    root.overrideredirect(True)
    root.geometry(f"{v_width}x{v_height}+{v_left}+{v_top}")

    canvas = tk.Canvas(root, bg="grey", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    start_x = start_y = 0
    rect_id = None
    selection = {}

    GAP, ARM_LEN = 10, 30
    hline = canvas.create_line(0, 0, 0, 0, fill="yellow", dash=(6, 4), width=2)
    vline = canvas.create_line(0, 0, 0, 0, fill="yellow", dash=(6, 4), width=2)
    center_dot = canvas.create_oval(0, 0, 0, 0, fill="red", outline="white", width=1.5)

    c_left = canvas.create_line(0, 0, 0, 0, fill="red", width=4)
    c_right = canvas.create_line(0, 0, 0, 0, fill="red", width=4)
    c_top = canvas.create_line(0, 0, 0, 0, fill="red", width=4)
    c_bottom = canvas.create_line(0, 0, 0, 0, fill="red", width=4)

    def update_crosshair(cx, cy):
        lx, ly = cx - v_left, cy - v_top
        canvas.coords(hline, 0, ly, v_width, ly)
        canvas.coords(vline, lx, 0, lx, v_height)
        canvas.coords(center_dot, lx - 2, ly - 2, lx + 2, ly + 2)
        canvas.coords(c_left, lx - GAP - ARM_LEN, ly, lx - GAP, ly)
        canvas.coords(c_right, lx + GAP, ly, lx + GAP + ARM_LEN, ly)
        canvas.coords(c_top, lx, ly - GAP - ARM_LEN, lx, ly - GAP)
        canvas.coords(c_bottom, lx, ly + GAP, lx, ly + GAP + ARM_LEN)

    def on_pointer_motion(event):
        update_crosshair(*get_physical_cursor())

    def on_button_press(event):
        nonlocal start_x, start_y, rect_id
        start_x, start_y = get_physical_cursor()
        rect_id = canvas.create_rectangle(0, 0, 1, 1, outline='cyan', width=4)

    def on_move_press(event):
        cur_x, cur_y = get_physical_cursor()
        canvas.coords(rect_id, start_x - v_left, start_y - v_top, cur_x - v_left, cur_y - v_top)
        update_crosshair(cur_x, cur_y)

    def on_button_release(event):
        end_x, end_y = get_physical_cursor()
        left, top = min(start_x, end_x), min(start_y, end_y)
        width, height = abs(end_x - start_x), abs(end_y - start_y)

        if width > 10 and height > 10:
            selection.update({"top": top, "left": left, "width": width, "height": height})
        root.destroy()

    canvas.bind("<Motion>", on_pointer_motion)
    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move_press)
    canvas.bind("<ButtonRelease-1>", on_button_release)
    root.bind("<Escape>", lambda e: root.destroy())

    root.mainloop()
    return selection