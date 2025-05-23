import tkinter as tk
from tkinter import ttk

# Example table data (18 rows x 9 columns)
table_data = [
    ["A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1", "I1"],
    ["A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "I2"],
    ["A3", "B3", "C3", "D3", "E3", "F3", "G3", "H3", "I3"],
    ["A4", "B4", "C4", "D4", "E4", "F4", "G4", "H4", "I4"],
    ["A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5", "I5"],
    ["A6", "B6", "C6", "D6", "E6", "F6", "G6", "H6", "I6"],
    ["A7", "B7", "C7", "D7", "E7", "F7", "G7", "H7", "I7"],
    ["A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8", "I8"],
    ["A9", "B9", "C9", "D9", "E9", "F9", "G9", "H9", "I9"],
    ["A10", "B10", "C10", "D10", "E10", "F10", "G10", "H10", "I10"],
    ["A11", "B11", "C11", "D11", "E11", "F11", "G11", "H11", "I11"],
    ["A12", "B12", "C12", "D12", "E12", "F12", "G12", "H12", "I12"],
    ["A13", "B13", "C13", "D13", "E13", "F13", "G13", "H13", "I13"],
    ["A14", "B14", "C14", "D14", "E14", "F14", "G14", "H14", "I14"],
    ["A15", "B15", "C15", "D15", "E15", "F15", "G15", "H15", "I15"],
    ["A16", "B16", "C16", "D16", "E16", "F16", "G16", "H16", "I16"],
    ["A17", "B17", "C17", "D17", "E17", "F17", "G17", "H17", "I17"],
    ["A18", "B18", "C18", "D18", "E18", "F18", "G18", "H18", "I18"]
]

def main():
    root = tk.Tk()
    root.title("Dropdown Example")

    # Extract the column names as options for the dropdown
    options = [f"Column {i+1}" for i in range(len(table_data[0]))]

    selected_column = tk.StringVar()

    def update_dropdown(*args):
        column_index = options.index(selected_column.get())
        dropdown_values = [row[column_index] for row in table_data]
        dropdown.configure(values=dropdown_values)

    selected_column.trace("w", update_dropdown)

    column_dropdown = ttk.Combobox(root, textvariable=selected_column, values=options)
    column_dropdown.pack()

    dropdown = ttk.Combobox(root)
    dropdown.pack()

    update_dropdown()

    root.mainloop()

if __name__ == "__main__":
    main()
