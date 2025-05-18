import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class CodeReviewGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Architecture Design Change Visualization")
        self.root.geometry("900x600")

        # Create two sections: Left (Menu) and Right (Visualization)
        self.create_sections()

        # Initialize data structure to hold changes
        self.changes = []

        # Initialize zoom level and pan position
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

        # Initialize variables for module positions
        self.module_positions = {}

    def create_sections(self):
        # Left Section: Menu
        self.left_frame = tk.Frame(self.root, bg="lightgrey", width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.left_frame, text="MENU", bg="lightgrey", font=("Arial", 16, "bold")).pack(pady=10)
        menu_options = [
            "Module File Addition",
            "Module File Deletion",
            "Class Addition",
            "Class Deletion",
            "Move Class",
            "Move Method",
            "Modified Constructor"
        ]

        for option in menu_options:
            btn = tk.Button(
                self.left_frame,
                text=option,
                width=25,
                bg="white",
                command=lambda opt=option: self.add_change(opt)
            )
            btn.pack(pady=5)

        # Right Section: Visualization
        self.right_frame = tk.Frame(self.root, bg="white")
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.right_frame, bg="white", scrollregion=(0, 0, 2000, 2000))
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Add scrollbars
        self.scroll_x = tk.Scrollbar(self.right_frame, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y = tk.Scrollbar(self.right_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        # Bind mouse events for zooming, panning, and showing change details
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)
        self.canvas.bind("<ButtonRelease-1>", self.stop_pan)
        self.canvas.bind("<Double-1>", self.show_change_details)

    def add_change(self, change_type):
        self.changes.append(change_type)
        self.update_visualization()

    def update_visualization(self):
        self.canvas.delete("all")  # Clear previous visualization
        x, y = 50, 50
        prev_item = None

        for change in self.changes:
            fill_color = self.get_fill_color(change)
            outline_color = self.get_outline_color(change)
            current_item = self.canvas.create_rectangle(
                x, y, x + 200, y + 50, fill=fill_color, outline=outline_color, tags=("module",)
            )
            self.canvas.create_text(x + 100, y + 25, text=change, font=("Arial", 10))
            self.module_positions[current_item] = (x, y)

            if prev_item:
                # Draw a curved line connecting the previous item to the current one
                self.draw_curved_line(prev_item, current_item)

            prev_item = current_item
            y += 100  # Move down for the next item

        # Update canvas size and scrollable region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_fill_color(self, change):
        if "Addition" in change:
            return "lightgreen"
        elif "Deletion" in change:
            return "lightcoral"
        else:
            return "lightyellow"

    def get_outline_color(self, change):
        if "Addition" in change:
            return "green"
        elif "Deletion" in change:
            return "red"
        else:
            return "black"

    def zoom(self, event):
        # Zoom in or out based on mouse wheel scroll
        if event.delta > 0:
            scale_factor = 1.1
        else:
            scale_factor = 1 / 1.1

        # Calculate the new zoom level
        new_zoom_level = self.zoom_level * scale_factor

        # Limit the zoom level to a reasonable range
        if 0.1 <= new_zoom_level <= 10.0:
            self.zoom_level = new_zoom_level

            # Get the current scroll position
            scroll_x = self.scroll_x.get()[0]
            scroll_y = self.scroll_y.get()[0]

            # Calculate the center of the canvas
            center_x = self.canvas.winfo_width() / 2
            center_y = self.canvas.winfo_height() / 2

            # Convert canvas coordinates to world coordinates
            world_center_x = self.canvas.canvasx(center_x)
            world_center_y = self.canvas.canvasy(center_y)

            # Scale the canvas around the center of the mouse pointer
            self.canvas.scale("all", world_center_x, world_center_y, scale_factor, scale_factor)

            # Update the scrollbars
            self.canvas.xview_moveto(scroll_x)
            self.canvas.yview_moveto(scroll_y)

    def start_pan(self, event):
        # Store the initial pan position
        self.pan_x = event.x
        self.pan_y = event.y

    def pan(self, event):
        # Calculate the pan distance and update the canvas position
        dx = event.x - self.pan_x
        dy = event.y - self.pan_y
        self.canvas.move("all", dx, dy)
        self.pan_x = event.x
        self.pan_y = event.y

    def stop_pan(self, event):
        # Reset the pan position
        self.pan_x = 0
        self.pan_y = 0

    def show_change_details(self, event):
        # Find the item that was clicked on
        item = self.canvas.find_closest(event.x, event.y)[0]
        
        # Get the text of the clicked item
        change_details = self.canvas.itemcget(item, "text")
        
        # Display the change details in a popup
        popup = tk.Toplevel(self.root)
        popup.title("Change Details")
        tk.Label(popup, text=change_details, font=("Arial", 12)).pack(padx=20, pady=20)

    def draw_curved_line(self, prev_item, current_item):
        # Get the coordinates of the previous and current items
        prev_x, prev_y = self.module_positions[prev_item]
        x, y = self.module_positions[current_item]

        # Calculate the control points for the curved line
        control_x = (prev_x + x) / 2
        control_y = (prev_y + y) / 2

        # Draw the curved line
        self.canvas.create_line(
            prev_x + 100, prev_y + 25, control_x, control_y, x + 100, y + 25,
            smooth=True, width=2, arrow=tk.LAST, fill="black"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeReviewGUI(root)
    root.mainloop()