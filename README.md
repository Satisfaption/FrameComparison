# Frame Checker 

This tool is designed to assist runners doing encounter manipulations for **Pokemon LeafGreen** using *ConstructiveCynicism's Manipulation Tool*.

It monitors a selectable screen region (such as an emulator window or video feed) and continuously compares it against a target reference frame. Once a match is detected, the capture window freezes on that exact frame and highlights it with a green border—eliminating the need for manual frame-by-frame VOD checks.

> **Note:** Currently, this version only supports **LeafGreen** due to the custom HSV saturation mask. **FireRed** support will be added in a future update! (Once I get my hands on the Route)


## Walkthrough

### 1. Keybind Configuration

After saving keybinds, a crosshair overlay will appear allowing you to click and drag over your target capture area.
link to config image

* **Stop Key:** Immediately stops active capture and minimizes the monitor window. Useful when the Manip-Tool is 90% confident, and the Frame Checker didn't catch it but you still want to continue.
* **Restart Key:** Restores the monitor from the minimized state and resumes frame capture in the background without stealing active focus from your game.
* **Quit Key:** Exits the application.

> **Config File:** Your keybinds are saved to `config.json` in the application folder. To reconfigure your hotkeys, simply edit or delete this file and restart the app.

### 2. Select Capture Area

Once keybinds are saved, a crosshair overlay appears which lets you choose your target area to capture.
#### Tips for best results:
* Position your emulator or video player on screen **before** selecting the region.
* Drag a box that tightly wraps around the game frame area. (between the top bar with 'File', 'Play', etc. and the bottom bar with 'v0.6', 'PSR', etc.)
* Avoid moving or resizing your game window after selecting the region (otherwise restart and select again)

### 3. Select Target Image

After locking in your capture area, a file dialog will prompt you to select your reference target frame image.
#### Tips for best results:
* Ensure there are no video compression artifacts or UI overlays obscuring the game frame.
* Take target snapshots with your video player scaled roughly same as your active emulator display. 

For example: Open a VOD of hitting the frame, resize the video player until the emulator is the same size as when playing, then advance to the target frame and take a snapshot.

**Bad image:**
![bad image](images/badexample.png)

**Good image:**
![good image](images/LeafGreenFrameTarget.png)

Once selected, the app generates a temporary debug mask file (`debug_mask_output.png`) to extract high-contrast shape outlines for matching. 

![Mask Example Image](images/debug_mask_output.png)

You don't need to do anything with this file, but you can inspect it in your directory to confirm clean shape extraction.

**That's it. You are ready to run!**