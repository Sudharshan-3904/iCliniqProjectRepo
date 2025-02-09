import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def select_file():
    # Opens a file dialog for the user to select an Excel or CSV file.
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    file_path = filedialog.askopenfilename(
        title="Select a CSV or Excel file",
        filetypes=(("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls"))
    )

    if file_path:
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            data = pd.read_excel(file_path)
        else:
            messagebox.showerror("Error", "Unsupported file format. Please select CSV or Excel.")
            return None

        return data
    else:
        messagebox.showinfo("No File", "No file was selected.")
        return None


def analyze_file(data):
    """
    Displays basic analysis of the data, including:
    - Data preview (first few rows)
    - Data types of attributes
    - Summary statistics (if applicable)
    """
    print("\n--- File Analysis ---")
    print("Number of rows and columns: ", data.shape)
    print("\nColumn Names:")
    print(data.columns)
    print("\nData Types:")
    print(data.dtypes)
    print("\nPreview of Data:")
    print(data.head())
    print("\nSummary Statistics:")
    print(data.describe())


def filter_data(data):
    """
    Filters the data based on user input.
    Prompts the user to select a column and filter condition.
    """
    column = input("Enter the column name you want to filter by: ")

    if column not in data.columns:
        print("Invalid column name. Please try again.")
        return data

    condition = input(f"Enter the condition for filtering '{column}' (e.g., > 50, == 'Value'): ")

    try:
        filtered_data = data.query(f"`{column}` {condition}")
        print(f"\n--- Filtered Data (by {column} {condition}) ---")
        print(filtered_data.head())
        return filtered_data
    except Exception as e:
        print(f"Error applying filter: {e}")
        return data


def sort_data(data):
    """
    Sorts the data based on user input.
    Prompts the user to select a column and sorting order.
    """
    column = input("Enter the column name you want to sort by: ")

    if column not in data.columns:
        print("Invalid column name. Please try again.")
        return data

    ascending = input("Sort in ascending order? (y/n): ").lower() == 'y'

    sorted_data = data.sort_values(by=column, ascending=ascending)
    print(f"\n--- Sorted Data (by {column}, ascending={ascending}) ---")
    print(sorted_data.head())
    return sorted_data


def main():
    data = select_file()

    if data is not None:
        analyze_file(data)

        while True:
            choice = input("\nDo you want to filter or sort the data? (filter/sort/exit): ").lower()

            if choice == 'filter':
                data = filter_data(data)
            elif choice == 'sort':
                data = sort_data(data)
                #print(data.head())
            elif choice == 'exit':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please select 'filter', 'sort', or 'exit'.")


if __name__ == "__main__":
    main()
