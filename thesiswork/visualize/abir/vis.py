import tkinter as tk
from tkinter import Canvas

def draw_module(canvas, x, y, name, action):
    """Draw a rectangle for a module and label it."""
    color = {"added": "green", "modified": "yellow", "deleted": "red"}.get(action, "gray")
    canvas.create_rectangle(x, y, x+100, y+50, fill=color)
    canvas.create_text(x+50, y+25, text=name)

def visualize():
    """Example visualization of changes."""
    canvas.delete("all")
    draw_module(canvas, 50, 50, "Module1", "added")
    draw_module(canvas, 200, 50, "Module2", "modified")
    draw_module(canvas, 350, 50, "Module3", "deleted")
    # Add arrows
    canvas.create_line(100, 75, 200, 75, arrow=tk.LAST)

root = tk.Tk()
root.title("Architecture Change Visualization")

# Left menu
frame_left = tk.Frame(root, width=200, height=400, bg="lightgray")
frame_left.pack(side="left", fill="y")

button_visualize = tk.Button(frame_left, text="Visualize Changes", command=visualize)
button_visualize.pack(pady=20)

# Right canvas
canvas = Canvas(root, width=800, height=400, bg="white")
canvas.pack(side="right", fill="both", expand=True)

root.mainloop()
