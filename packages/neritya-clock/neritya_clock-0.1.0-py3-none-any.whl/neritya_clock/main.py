# neritya_clock/main.py

import tkinter as tk
from time import strftime

def main():
    # ---------------- CONFIG ---------------- #
    DIGIT_FONT = ("Calibri", 64, "bold")
    DIGIT_FG = "#00FF00"         # Green
    CARD_BG = "#222222"          # Dark grey
    ROOT_BG = "#000000"          # Black background

    CARD_WIDTH = 80
    CARD_HEIGHT = 100
    CARD_PAD = 10

    def update_time():
        current_time = strftime('%H%M')
        for i, digit in enumerate(current_time):
            digit_labels[i].config(text=digit)
        root.after(1000, update_time)

    def start_drag(event):
        root.x = event.x
        root.y = event.y

    def do_drag(event):
        x = event.x_root - root.x
        y = event.y_root - root.y
        root.geometry(f"+{x}+{y}")

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg=ROOT_BG)

    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<Button-1>", start_drag)
    root.bind("<B1-Motion>", do_drag)

    container = tk.Frame(root, bg=ROOT_BG)
    container.pack(padx=10, pady=10)

    digit_labels = []

    for _ in range(4):
        frame = tk.Frame(container, bg=CARD_BG, width=CARD_WIDTH, height=CARD_HEIGHT)
        frame.pack(side=tk.LEFT, padx=5)
        frame.pack_propagate(False)

        label = tk.Label(
            frame,
            text="0",
            font=DIGIT_FONT,
            fg=DIGIT_FG,
            bg=CARD_BG,
            anchor="center"
        )
        label.pack(expand=True, fill="both")

        digit_labels.append(label)

    update_time()
    root.mainloop()
