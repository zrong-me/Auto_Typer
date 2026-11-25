
import tkinter as tk
from tkinter import ttk
import threading
import time
import keyboard
from pynput.keyboard import Controller, Key

# NEXORA AUTO TYPER

SPEEDS = {
    "Slow": 0.15,
    "Normal": 0.05,
    "Fast": 0.015,
    "Very Fast": 0.005,
}

controller = Controller()
running = threading.Event()
busy = threading.Lock()

root = tk.Tk()
root.title("NEXORA Auto Typer")
root.geometry("460x440")
root.resizable(False, False)
root.attributes("-topmost", True)


def status(message):
    if root.winfo_exists():
        root.after(
            0,
            lambda: status_label.config(text=message)
        )


def start_typing():
    if busy.locked():
        return

    text = text_box.get("1.0", "end-1c")

    if not text.strip():
        status("Please enter text.")
        return

    delay = SPEEDS[speed_var.get()]

    threading.Thread(
        target=type_worker,
        args=(text, delay),
        daemon=True
    ).start()


def stop_typing():
    running.clear()
    status("Stopped")


def type_worker(text, delay):
    if not busy.acquire(blocking=False):
        return

    try:
        running.set()
        status("Starting in 3 seconds...")

        for _ in range(30):
            if not running.is_set():
                return
            time.sleep(0.1)

        status("Typing...")

        # Local testing: repeat a limited number of times.
        while running.is_set():
            if not running.is_set():
                break

            for char in text:
                if not running.is_set():
                    break

                controller.type(char)
                time.sleep(delay)

            if not running.is_set():
                break

            controller.press(Key.enter)
            controller.release(Key.enter)

        if running.is_set():
            status("Completed.")

    except Exception as error:
        status(f"Error: {error}")

    finally:
        running.clear()
        busy.release()


def close_app():
    running.clear()
    keyboard.unhook_all_hotkeys()
    root.destroy()


# TITLE
tk.Label(
    root,
    text="NEXORA AUTO TYPER",
    font=("Arial", 19, "bold")
).pack(pady=15)

# TEXT
tk.Label(root, text="Your text:").pack(anchor="w", padx=20)

text_box = tk.Text(
    root,
    height=9,
    width=50,
    font=("Arial", 11)
)
text_box.pack(padx=20, pady=8)

# SPEED
speed_frame = tk.Frame(root)
speed_frame.pack(pady=8)

tk.Label(speed_frame, text="Speed:").pack(side="left", padx=5)

speed_var = tk.StringVar(value="Fast")

ttk.Combobox(
    speed_frame,
    textvariable=speed_var,
    values=list(SPEEDS.keys()),
    state="readonly",
    width=12
).pack(side="left")

# BUTTONS
buttons = tk.Frame(root)
buttons.pack(pady=12)

tk.Button(
    buttons,
    text="START",
    width=15,
    height=2,
    bg="#168a50",
    fg="white",
    command=start_typing
).pack(side="left", padx=7)

tk.Button(
    buttons,
    text="STOP",
    width=15,
    height=2,
    bg="#c0392b",
    fg="white",
    command=stop_typing
).pack(side="left", padx=7)

# STATUS
status_label = tk.Label(
    root,
    text="Ready",
    font=("Arial", 10, "bold")
)
status_label.pack(pady=8)

tk.Label(
    root,
    text="ALT + S = START   |   ALT + A = STOP"
).pack()

tk.Label(
    root,
    text="Always on top",
    fg="gray"
).pack(pady=8)

# HOTKEYS
keyboard.add_hotkey("alt+s", start_typing)
keyboard.add_hotkey("alt+a", stop_typing)

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
