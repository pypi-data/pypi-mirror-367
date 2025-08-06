import keyboard
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading

# text: the text to be typed
# wpm: average typing speed, measured in words per minute 
# accuracy: float between 0 and 1, higher accuracy means less typos
# backspace_duration: time taken for backspace to be pressed
# correction_coefficient: determines how many typos are made before correcting them,
#                         lower coefficient means typos are caught quicker
# wait_key: press this key to start typing
# break_key: press this key to stop typing

# Global control variables
is_paused = False
typed_chars = 0
start_time = None

# Toggle pause
def toggle_pause():
    global is_paused
    is_paused = not is_paused
    update_status("Paused" if is_paused else "Typing...")

# Update status labels
def update_status(text):
    status_label.config(text=f"Status: {text}")
    mini_status_var.set(f"Status: {text} | {typed_chars} chars | {get_wpm()} WPM")

# Calculate typing speed
def get_wpm():
    if start_time:
        elapsed = time.time() - start_time
        return int((typed_chars / 5) / (elapsed / 60)) if elapsed > 0 else 0
    return 0

# Update live stats
def update_stats():
    if start_time:
        elapsed = int(time.time() - start_time)
        wpm = get_wpm()
        stats_label.config(text=f"Typed: {typed_chars} | Time: {elapsed}s | WPM: {wpm}")
        mini_status_var.set(f"{status_label.cget('text')} | {typed_chars} chars | {wpm} WPM")

# Typing logic
def typoses(text, total_time=None, accuracy=0.9, wait_key=None, break_key='esc',
            correction_coefficient=0.85, backspace_duration=0.04):
    global typed_chars, start_time
    typed_chars = 0
    start_time = time.time()

    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.?!()[]{}<>-_+=:;\'"@#$%^&* '
    total_chars = len(text)

    spc = total_time / total_chars 
    spc_low = spc * 0.2
    spc_high = spc * 1.8

    i = 0
    typos = 0

    if wait_key:
        update_status(f"Waiting for '{wait_key.upper()}' key...")
        while not keyboard.is_pressed(wait_key):
            time.sleep(0.1)
        while keyboard.is_pressed(wait_key):
            time.sleep(0.1)

    update_status("Typing...")

    while i < len(text):
        if keyboard.is_pressed(break_key):
            update_status("Stopped")
            return

        if is_paused:
            update_status("Paused")
            while is_paused:
                time.sleep(0.1)
            update_status("Typing...")

        if typos and (i + typos >= len(text) or random.random() < 1 - correction_coefficient ** typos):
            time.sleep(backspace_duration)
            for _ in range(typos):
                keyboard.press_and_release('backspace')
                time.sleep(backspace_duration)
            typos = 0

        if random.random() > accuracy:
            keyboard.write(random.choice(chars))
            typos += 1
        else:
            keyboard.write(text[i + typos])
            if typos:
                typos += 1
            else:
                i += 1
                typed_chars += 1
                update_stats()

        time.sleep(random.uniform(spc_low, spc_high))

# Start typing thread
def start_typing():
    try:
        text = text_input.get("1.0", tk.END).strip()
        total_time = float(time_entry.get())
        wait_key = wait_key_var.get().lower()
        pause_key = pause_key_var.get().lower()

        if not text:
            messagebox.showerror("Error", "Text input is empty.")
            return
        if pause_key == wait_key:
            messagebox.showerror("Error", "Pause and wait keys must be different.")
            return
        if total_time <= 0:
            messagebox.showerror("Error", "Total time must be positive.")
            return

        keyboard.add_hotkey(pause_key, toggle_pause)
        update_status("Waiting...")

        threading.Thread(
            target=typoses,
            args=(text,),
            kwargs={"total_time": total_time, "accuracy": 0.85, "wait_key": wait_key},
            daemon=True
        ).start()

    except ValueError:
        messagebox.showerror("Error", "Invalid number for time .")

# Toggle dark/light theme

def toggle_theme():
    dark = theme_var.get()
    bg_color = "#2e2e2e" if dark else "SystemButtonFace"
    fg_color = "white" if dark else "black"
    label_fg = "white" if dark else "gray"

    style.theme_use('clam' if dark else 'default')
    root.configure(bg=bg_color)
    frame.configure(bg=bg_color)
    mini_win.configure(bg=bg_color)

    # Update label and stat colors that cant be edited using for loop
    status_label.configure(bg=bg_color, fg=label_fg)
    stats_label.configure(bg=bg_color, fg=label_fg)
    mini_label.configure(bg=bg_color, fg=label_fg)
    theme_check.configure(bg=bg_color, fg=label_fg, selectcolor=bg_color)
    title_label.configure(bg=bg_color, fg=fg_color)
    footer_label.configure(bg=bg_color, fg=label_fg)

    # Update all labels inside the frame
    for child in frame.winfo_children():
        if isinstance(child, tk.Label) or isinstance(child, tk.Checkbutton):
            child.configure(bg=bg_color, fg=fg_color)
        elif isinstance(child, ttk.Combobox):
            style.configure("TCombobox", fieldbackground=bg_color, background=bg_color, foreground=fg_color)
        elif isinstance(child, tk.Entry):
            child.configure(bg="#1e1e1e" if dark else "white", fg=fg_color, insertbackground=fg_color)

    # Update text box separately
    text_input.configure(bg="#1e1e1e" if dark else "white", fg=fg_color, insertbackground=fg_color)
    # Update Comboboxes
    if dark:
        style.theme_use('clam')  
        style.configure("DarkCombobox.TCombobox",
            fieldbackground="#1e1e1e",  # internal text field
            background="#1e1e1e",       # dropdown list background
            foreground="white",        # text color
            arrowcolor="white",        # arrow color
            bordercolor="#555555",     # frame border (clam only)
            lightcolor="#2e2e2e",      # outer highlight
            darkcolor="#2e2e2e",       # outer shadow
            relief="flat"
        )
        style.map("DarkCombobox.TCombobox",
            fieldbackground=[('readonly', '#1e1e1e')],
            background=[('readonly', '#1e1e1e')],
            foreground=[('readonly', 'white')],
            arrowcolor=[('active', 'white'), ('!active', 'white')],
        )
    else:
        style.theme_use('default')
        style.configure("DarkCombobox.TCombobox",
            fieldbackground="white",
            background="white",
            foreground="black",
            arrowcolor="black",
            relief="flat"
        )
        style.map("DarkCombobox.TCombobox",
            fieldbackground=[('readonly', 'white')],
            background=[('readonly', 'white')],
            foreground=[('readonly', 'black')],
            arrowcolor=[('active', 'black'), ('!active', 'black')],
        )





# GUI Setup
root = tk.Tk()
root.title("Human-Like Auto Typer")
root.geometry("600x550")
root.resizable(False, False)

style = ttk.Style()
theme_var = tk.BooleanVar(value=False)

title_label = tk.Label(root, text="Paste Text to Auto-Type:")
title_label.pack(anchor='w', padx=10, pady=(10, 0))
text_input = tk.Text(root, height=15, wrap='word', font=("Courier New", 10))
text_input.pack(fill='both', padx=10, pady=5)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Total Time (seconds):").grid(row=0, column=0, padx=5)
time_entry = tk.Entry(frame)
time_entry.grid(row=0, column=1, padx=5)

tk.Label(frame, text="Wait Key:").grid(row=0, column=2, padx=5)
wait_key_var = tk.StringVar(value='f4')
wait_key_menu = ttk.Combobox(frame, textvariable=wait_key_var,
                             values=[f'f{i}' for i in range(1, 13)],
                             state='readonly', width=5, style="DarkCombobox.TCombobox")
wait_key_menu.grid(row=0, column=3, padx=5)


tk.Label(frame, text="Pause Key:").grid(row=1, column=0, padx=5, pady=5)
pause_key_var = tk.StringVar(value='f2')
pause_key_menu = ttk.Combobox(frame, textvariable=pause_key_var,
                              values=[f'f{i}' for i in range(1, 13)],
                              state='readonly', width=5, style="DarkCombobox.TCombobox")
pause_key_menu.grid(row=1, column=1, padx=5)

start_button = tk.Button(root, text="Start Auto Typing", command=start_typing, bg="#4CAF50", fg="white", font=("Arial", 12))
start_button.pack(pady=10)

# Live Status and Stats
status_label = tk.Label(root, text="Status: Idle", fg="gray")
status_label.pack(pady=(0, 5))
stats_label = tk.Label(root, text="Typed: 0 | Time: 0s | WPM: 0", fg="gray")
stats_label.pack()

# Theme toggle
checked_var= tk.IntVar(value=1)
theme_check= tk.Checkbutton(root, text="Dark Mode", variable= theme_var , command= toggle_theme)
theme_check.pack(pady=(5, 10))
# Footer
footer_label = tk.Label(root, text="Press ESC to stop | Default pause: F2", fg="gray")
footer_label.pack(pady=(10, 5))

# Mini Floating Window
mini_win = tk.Toplevel(root)
mini_win.title("AutoTyper Mini")
mini_win.geometry("250x60+30+30")
mini_win.attributes('-topmost', True)
mini_win.resizable(False, False)
mini_status_var = tk.StringVar(value="Status: Idle")
mini_label = tk.Label(mini_win, textvariable=mini_status_var, font=("Arial", 9), fg="gray")
mini_label.pack(padx=10, pady=10)

# Run the GUI
def main():
    
    root.mainloop()

if __name__ == "__main__":
    main()
