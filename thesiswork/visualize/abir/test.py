import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog

class CodeReviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Review Tracking and Visualization")
        self.root.geometry("1200x800")

        # Initialize the changes dictionary
        self.changes = {
            'modules': [],
            'classes': [],
            'constructors': [],
            'methods': []
        }

        # Create a notebook for different sections
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create frames for different sections
        self.overview_frame = ttk.Frame(self.notebook)
        self.details_frame = ttk.Frame(self.notebook)

        # Add frames to notebook
        self.notebook.add(self.overview_frame, text="Overview")
        self.notebook.add(self.details_frame, text="Details")

        # Left Menu (Overview Frame)
        self.left_menu = ttk.Frame(self.overview_frame)
        self.left_menu.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Right Section (Details Frame)
        self.right_section = ttk.Frame(self.details_frame)
        self.right_section.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Populate Left Menu
        self.populate_left_menu()

        # Populate Right Section
        self.populate_right_section()

    def populate_left_menu(self):
        self.tree = ttk.Treeview(self.left_menu, columns=('Name', 'Type'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Type', text='Type')
        self.tree.pack(side=tk.LEFT, fill=tk.Y)

        scrollbar = ttk.Scrollbar(self.left_menu, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.bind('<<TreeviewSelect>>', self.on_select_item)

        # Add some sample data
        self.add_sample_data()

    def populate_right_section(self):
        self.details_text = scrolledtext.ScrolledText(self.right_section, wrap=tk.WORD, width=80, height=30)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # Buttons for adding, modifying, and deleting items
        self.add_button = ttk.Button(self.right_section, text="Add", command=self.add_item)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.modify_button = ttk.Button(self.right_section, text="Modify", command=self.modify_item)
        self.modify_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = ttk.Button(self.right_section, text="Delete", command=self.delete_item)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

    def add_sample_data(self):
        self.add_item('module1', 'Module')
        self.add_item('Class1', 'Class')
        self.add_item('Constructor1', 'Constructor')
        self.add_item('Method1', 'Method')

    def add_item(self, name=None, item_type=None):
        if not name:
            name = simpledialog.askstring("Input", f"Enter the {item_type} name:")
        if not item_type:
            item_type = simpledialog.askstring("Input", "Enter the item type (Module, Class, Constructor, Method):")

        if name and item_type:
            # Ensure the item_type is correctly pluralized
            item_type_key = item_type.lower() + 's'
            if item_type_key in self.changes:
                self.changes[item_type_key].append((name, 'Added'))
                self.tree.insert('', tk.END, values=(name, item_type))
                messagebox.showinfo("Success", f"{item_type} '{name}' added successfully.")
            else:
                messagebox.showerror("Error", f"Invalid item type: {item_type}")

    def modify_item(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = selected_item[0]
            name, item_type = self.tree.item(item_id, 'values')
            new_name = simpledialog.askstring("Input", f"Enter the new name for {item_type} '{name}':")
            if new_name:
                # Ensure the item_type is correctly pluralized
                item_type_key = item_type.lower() + 's'
                if item_type_key in self.changes:
                    self.changes[item_type_key].append((name, 'Modified'))
                    self.tree.item(item_id, values=(new_name, item_type))
                    messagebox.showinfo("Success", f"{item_type} '{name}' modified to '{new_name}' successfully.")
                else:
                    messagebox.showerror("Error", f"Invalid item type: {item_type}")
        else:
            messagebox.showwarning("Warning", "Please select an item to modify.")

    def delete_item(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = selected_item[0]
            name, item_type = self.tree.item(item_id, 'values')
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {item_type} '{name}'?")
            if confirm:
                # Ensure the item_type is correctly pluralized
                item_type_key = item_type.lower() + 's'
                if item_type_key in self.changes:
                    self.changes[item_type_key].append((name, 'Deleted'))
                    self.tree.delete(item_id)
                    messagebox.showinfo("Success", f"{item_type} '{name}' deleted successfully.")
                else:
                    messagebox.showerror("Error", f"Invalid item type: {item_type}")
        else:
            messagebox.showwarning("Warning", "Please select an item to delete.")

    def on_select_item(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = selected_item[0]
            name, item_type = self.tree.item(item_id, 'values')
            details = f"Details of {item_type} '{name}':\n"
            item_type_key = item_type.lower() + 's'
            changes = [f"{name} {action}" for name, action in self.changes[item_type_key] if name == name]
            details += "\n".join(changes)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, details)

    def on_add_button_click(self):
        item_type = simpledialog.askstring("Input", "Enter the item type (Module, Class, Constructor, Method):")
        if item_type:
            if item_type.lower() in ['module', 'class', 'constructor', 'method']:
                self.add_item(None, item_type)
            else:
                messagebox.showerror("Error", "Invalid item type. Please choose from Module, Class, Constructor, Method.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeReviewApp(root)
    root.mainloop()