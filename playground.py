import tkinter as tk
from tkinter import ttk, filedialog
import os
import hashlib
from threading import Thread
import time
import customtkinter

# Function to browse for a directory
def browse_directory():
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, selected_directory)

# Function to compare files in a directory by their MD5 hash
def compare_files_by_hash(directory):
    hash_map = {}
    duplicate_files = []

    # Recursively walk through the directory
    for root, _, file_list in os.walk(directory):
        for filename in file_list:
            file_path = os.path.join(root, filename)

            try:
                # Calculate the MD5 hash of each file
                with open(file_path, "rb") as file:
                    file_hash = hashlib.md5(file.read()).hexdigest()
                    if file_hash in hash_map:
                        hash_map[file_hash].append(file_path)
                    else:
                        hash_map[file_hash] = [file_path]
            except Exception as e:
                continue

    # Find and return duplicate files
    for file_list in hash_map.values():
        if len(file_list) > 1:
            duplicate_files.extend(file_list)

    return duplicate_files

# Function to format file size
def get_file_size_formatted(file_path):
    size_bytes = os.path.getsize(file_path)
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

# Function to display a window listing duplicate files
def list_duplicates_window(duplicate_files):
    list_window = tk.Toplevel(root)
    list_window.title("Duplicate Files")

    def delete_selected_duplicates():
        selected_items = listbox_results.curselection()

        for index in selected_items[::-1]:
            index = int(index)
            file_path = duplicate_files[index]
            os.remove(file_path)
            duplicate_files.pop(index)
            listbox_results.delete(index)

        result_label.config(text=f"Deleted {len(selected_items)} file(s).")

    def close_window():
        list_window.destroy()

    def select_every_other():
        for i in range(0, len(duplicate_files), 2):
            listbox_results.selection_set(i)

    def select_every_third():
        for i in range(0, len(duplicate_files), 3):
            listbox_results.selection_set(i)

    def select_all():
        listbox_results.select_set(0, tk.END)

    # Create a Canvas widget for scrolling
    canvas = customtkinter.CTkCanvas(list_window, height=300, width=500)
    canvas.pack(pady=10)

    # Add a Scrollbar for the Canvas
    scrollbar = customtkinter.CTkScrollbar(list_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a Frame inside the Canvas
    frame = customtkinter.CTkFrame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    # Create a Listbox inside the Frame
    listbox_results = customtkinter.CTkListbox(frame, selectmode=tk.MULTIPLE, height=120, width=120)
    listbox_results.pack()

    # Display the duplicated files
    for index, file_path in enumerate(duplicate_files, start=1):
        file_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
        file_info = f"{file_hash[:8]} - {file_path} - Size: {get_file_size_formatted(file_path)}"
        listbox_results.insert(tk.END, file_info)

    delete_button = customtkinter.CTk.Button(list_window, text="Delete Selected", command=delete_selected_duplicates)
    delete_button.pack(pady=10)

    close_button = customtkinter.CTkButton(list_window, text="Close", command=close_window)
    close_button.pack(pady=10)

    # Add buttons for selecting items
    select_every_other_button = customtkinter.CTkButton(list_window, text="Select Every Other", command=select_every_other)
    select_every_other_button.pack(pady=5)

    select_every_third_button = customtkinter.CTkButton(list_window, text="Select Every Third", command=select_every_third)
    select_every_third_button.pack(pady=5)

    select_all_button = customtkinter.CTkButton(list_window, text="Select All", command=select_all)
    select_all_button.pack(pady=5)

    # Configure the Canvas to update its scroll region
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Function to search for duplicate files and display progress
def search_duplicates():
    search_directory = entry_directory.get()

    if not search_directory:
        result_label.config(text="Please enter a directory.")
        return

    duplicate_files = []  # Initialize an empty list to hold duplicate files

    def search_and_list_duplicates():
        nonlocal duplicate_files  # Use nonlocal since we are modifying the outer duplicate_files

        duplicate_files = compare_files_by_hash(search_directory)

        if duplicate_files:
            result_label.config(text=f"Found {len(duplicate_files)} duplicate file(s).")
            list_duplicates_window(duplicate_files)
        else:
            result_label.config(text="No duplicate files found.")

    search_thread = Thread(target=search_and_list_duplicates)
    search_thread.start()

    start_time = time.time()  # Record the start time

    total_files = len(duplicate_files)

    search_progress_bar = Progressbar(frame, orient="horizontal", length=200, mode="determinate")
    search_progress_bar.grid(row=3, columnspan=3, pady=10)
    search_progress_bar["maximum"] = 100
    search_progress_bar["value"] = 0

    search_progress_label = customtkinter.CTkLabel(frame, text="")
    search_progress_label.grid(row=4, column=1)

    # Create a label to display the elapsed time
    time_label = customtkinter.CTkLabel(frame, text="")
    time_label.grid(row=4, column=2)

def close_main_window():
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Modern Duplicate File Finder & Deleter App")

# Add a custom icon for the file dialog (replace 'icon_path' with your icon file path)
# icon_path = os.path.abspath("/images/juice_lee_icon.ico")
# root.iconbitmap(icon_path)

frame = customtkinter.CTkFrame(root, padding=10)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

label_directory = customtkinter.CTkLabel(frame, text="Search Directory:")
label_directory.grid(row=0, column=0, sticky=tk.W)

entry_directory = customtkinter.CTkEntry(frame)
entry_directory.grid(row=0, column=1, sticky=(tk.W, tk.E))

browse_button = customtkinter.CTkButton(frame, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=2, sticky=tk.W)

find_button = customtkinter.CTkButton(frame, text="Find Duplicates", command=search_duplicates)
find_button.grid(row=1, column=0, columnspan=3, pady=10)

result_label = customtkinter.CTkLabel(frame, text="")
result_label.grid(row=2, columnspan=3)

close_button = customtkinter.CTkButton(frame, text="Close", command=root.quit)
close_button.grid(row=5, columnspan=3, pady=10)

root.mainloop()
