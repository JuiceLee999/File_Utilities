import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess

# Function to select the source folder
def select_source_folder():
    source_folder = filedialog.askdirectory()
    source_entry.delete(0, tk.END)
    source_entry.insert(0, source_folder)

# Function to select the destination folder
def select_destination_folder():
    destination_folder = filedialog.askdirectory()
    destination_entry.delete(0, tk.END)
    destination_entry.insert(0, destination_folder)

# Function to copy files/folders using xcopy
def copy_files():
    source_folder = source_entry.get()
    destination_folder = destination_entry.get()

    if source_folder and destination_folder:
        try:
            cmd = f'xcopy "{source_folder}" "{destination_folder}" /E /I /Y /Q'
            subprocess.run(cmd, shell=True)
            result_label.config(text="Files/Folders copied successfully!")
        except Exception as e:
            result_label.config(text=f"Error: {str(e)}")
    else:
        result_label.config(text="Please select source and destination folders.")

# Create the main window
root = tk.Tk()
root.title("File Copier")

# Create and pack GUI components
source_label = tk.Label(root, text="Source Folder:")
source_label.pack()

source_entry = tk.Entry(root, width=50)
source_entry.pack()

source_button = tk.Button(root, text="Browse", command=select_source_folder)
source_button.pack()

destination_label = tk.Label(root, text="Destination Folder:")
destination_label.pack()

destination_entry = tk.Entry(root, width=50)
destination_entry.pack()

destination_button = tk.Button(root, text="Browse", command=select_destination_folder)
destination_button.pack()

copy_button = tk.Button(root, text="Copy Files/Folders", command=copy_files)
copy_button.pack()

result_label = tk.Label(root, text="")
result_label.pack()

# Start the GUI main loop
root.mainloop()