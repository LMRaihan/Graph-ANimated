import tkinter as tk
from tkinter import ttk

# TABLE 5: Semantic operations, their presence (% of commits) in different groups of changes and classification impacts.
table_data = [
    ["MA", "Module file addition", "6 5", "4 3", "~ ~", "4 4", 40, "(+)"],
    ["MD", "Module file deletion", "~ ~","3 3","~ ~", "~ ~", 39, "(+)"],
    ["CA", "New class addition", "37 33","23 21","12 12", "47 47", 46 ,"(-)"],
    ["CD", "Class deletion", "3 4", "16 15","2 1", "12", 39,"(+)"],
    ["MVC", "Move class", "3 4", "14 16", "1 1","11 10",38,"(+)"],
    ["MCNM","Modify class+ new method + cross module dependency", "18 17","10 9","12 12","25 26",42,"(~)"],
    ["MCDM", "Modify class + delete method + remove module dependency", "2 1", "6 5", "1 1", "7 7", 39, "(+)"],
    ["MCNMA", "Modify class + new method + new lib connection", "21 25", "11 18", "14 14", "22 21", 36, "(+)"],
    ["MCDMA", "Modify class + delete method + removing lib connection", "2 1", "6 5", "4 1", "5 7", 39, "(+)"],
    ["MVM", "Move method", "2 1", "4 3", "2 2", "~ ~", 39, "(+)"],
    ["CMD", "Modified constructor", "4 4", "5 5", "3 3", "5 5", 40, "(+)"],
    ["MCC", "Modified class with cross module connection", "58 57", "50 45", "48 48", "56 56", 37,"(+)"],
    ["MCD", "Modified class, cross module disconnection", "22 18", "51 50", "14 14", "30 31", 32, "(+)"],
    ["MCAC", "Modified class with lib connection", "57 68", "40 49", "54 54", "72 71", 44.2, "(-)"],
    ["MCAD", "Modified class with lib disconnection", "19 22", "43 49", "22 22", "28 29", 33, "(+)"],
    ["MMC", "Modified config with cross module connection","11 10", "14 13", "4 4", "20 20",41, "(~)"],
    ["MMD", "Modified config, cross module disconnection", "3 6", "11 11", "~ ~", "5 5", 37, "(+)"]
]

def main():
    # Create main Tkinter window
    root = tk.Tk()
    root.title("Dropdown List Example")
    root.geometry("500x300")  # Set window size to 500x300 pixels

    # Extract items (first column) from table data
    items = [row[0] for row in table_data]

    # Initialize selected item variable
    selected_item = tk.StringVar()

    def update_dropdown(*args):
        # Get selected item from dropdown
        selected_value = selected_item.get()
        
        # Check if selected item != empty
        if selected_value:
            try:
                # Find index of selected item in the items list
                item_index = items.index(selected_value)
                
                # Get description and quantity from table data
                meaning = table_data[item_index][1]
                perfect = table_data[item_index][2]
                prevent = table_data[item_index][3]
                correct = table_data[item_index][4]
                adapt = table_data[item_index][5]
                grouping = table_data[item_index][6]
                inclusion = table_data[item_index][7]
                
                # Update label text with description and quantity
                label.config(text=f"\nMeaning: {meaning}\nPerfect: {perfect}\nPrevent: {prevent}\nCorrect: {correct}\nAdapt: {adapt}\nGrouping F1(Excluding): {grouping}\nInclusion Impact Base(base 42): {inclusion}  \n")
            except ValueError:
                # Handle case when selected item != found in items list
                label.config(text="Item not found")
        else:
            # Clear label text if no item is selected
            label.config(text="")
            
    selected_item.trace("w", update_dropdown)

    # Create the drop-down list
    dropdown = ttk.Combobox(root, textvariable=selected_item, values=items)
    dropdown.pack()

    # Create label to display description and quantity
    label = tk.Label(root, text="")
    label.pack()

    # Create exit button
    exit_button = ttk.Button(root, text="Exit", command=root.quit)
    exit_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
