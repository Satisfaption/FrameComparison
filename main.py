import sys
import cv2
import keyboard
import mss
import numpy as np

from config import load_or_setup_hotkeys, DEBUG_MASK_FILE
from ui_helpers import (
    select_screen_region,
    select_target_file,
    minimize_cv_window,
    restore_cv_window_background,
    is_window_closed
)
from image_processing import extract_shape_mask, compare_frames


def run():
    # Load configuration and target region
    hotkeys = load_or_setup_hotkeys()
    stop_key = hotkeys.get("stop", "f6")
    restart_key = hotkeys.get("restart", "f7")
    quit_key = hotkeys.get("quit", "q")

    selected_bbox = select_screen_region()
    if not selected_bbox:
        sys.exit()

    t_width, t_height = selected_bbox['width'], selected_bbox['height']

    # Select and load target template image
    target_path = select_target_file()
    if not target_path:
        sys.exit()

    template = cv2.imread(target_path)
    if template is None:
        sys.exit()
    # Resize / comparison may need improvement so different sizes can be matched
    if template.shape[0] != t_height or template.shape[1] != t_width:
        template = cv2.resize(template, (t_width, t_height))

    template_mask = extract_shape_mask(template)

    try:
        cv2.imwrite(DEBUG_MASK_FILE, template_mask)
    except Exception:
        pass

    MATCH_THRESHOLD = 0.72
    monitor_window = "GSE Frame Monitor"
    cv2.namedWindow(monitor_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(monitor_window, t_width, t_height)

    state = {"running": True, "restart": False, "quit": False}

    def on_stop():
        state["running"] = False
        if not is_window_closed(monitor_window):
            minimize_cv_window(monitor_window)

    def on_restart():
        state["restart"] = True
        if not is_window_closed(monitor_window):
            restore_cv_window_background(monitor_window)

    keyboard.add_hotkey(stop_key, on_stop)
    keyboard.add_hotkey(restart_key, on_restart)
    keyboard.add_hotkey(quit_key, lambda: state.update({"quit": True}))

    with mss.MSS() as sct:
        def main_loop():
            last_frame_display = np.zeros((t_height, t_width, 3), dtype=np.uint8)
            frame_count = 0

            while True:
                if state["quit"] or is_window_closed(monitor_window):
                    return "quit"

                if state["restart"]:
                    state["restart"] = False
                    state["running"] = True
                    return "restart"

                if state["running"]:
                    search_grab = np.array(sct.grab(selected_bbox))
                    search_bgr = cv2.cvtColor(search_grab, cv2.COLOR_BGRA2BGR)
                    confidence = compare_frames(search_bgr, template_mask)

                    if confidence >= MATCH_THRESHOLD:
                        display_box = search_bgr.copy()
                        cv2.rectangle(display_box, (0, 0), (t_width - 1, t_height - 1), (0, 255, 0), 4)
                        cv2.putText(display_box, f"FRAME HIT! ({confidence * 100:.1f}%)", (10, 35),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                        cv2.imshow(monitor_window, display_box)
                        cv2.waitKey(1)
                        state["running"] = False
                        last_frame_display = display_box.copy()
                        continue

                    frame_count += 1
                    if frame_count % 6 == 0:
                        display_box = search_bgr.copy()
                        cv2.rectangle(display_box, (0, 0), (t_width - 1, t_height - 1), (0, 0, 255), 4)
                        cv2.putText(display_box, f"Tracking... ({confidence * 100:.1f}%)", (10, 35),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                        cv2.imshow(monitor_window, display_box)
                        cv2.waitKey(1)
                else:
                    stopped_display = last_frame_display.copy()
                    cv2.putText(stopped_display, f"[STOPPED - {restart_key.upper()} to restart]",
                                (10, t_height - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.imshow(monitor_window, stopped_display)
                    cv2.waitKey(50)

        while True:
            if main_loop() != "restart":
                break

    keyboard.unhook_all()
    cv2.destroyAllWindows()
    sys.exit()


if __name__ == "__main__":
    run()