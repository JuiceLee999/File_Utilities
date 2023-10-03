from msilib.schema import DuplicateFile
import tkinter as tk
from tkinter import ttk, filedialog
import os
import hashlib
from threading import Thread
import time
import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

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
    duplicate_files = [file_list for file_list in hash_map.values() if len(file_list) > 1]
    return [file for sublist in duplicate_files for file in sublist]

# Function to format file size
def get_file_size_formatted(file_path):
    size_bytes = os.path.getsize(file_path)
    units = ['bytes', 'KB', 'MB', 'GB']
    unit_index = 0
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1
    return f"{size_bytes:.2f} {units[unit_index]}"

# Function to display duplicate files in the same window
def list_duplicates_same_window(duplicate_files):
    result_label.configure(text=f"Duplicate Files ({len(duplicate_files)} found):")
    
    # Create a text widget for the results
    text_widget = customtkinter.CTkTextbox(frame, wrap=tk.WORD, width=800)
    text_widget.grid(row=4, column=0, columnspan=6, padx=10, pady=10, sticky="nsew")

    for index, file_path in enumerate(duplicate_files, start=1):
        file_hash = hashlib.md5(open(file_path, "rb").read()).hexdigest()
        file_info = f"{index}. {file_hash[:8]} - {file_path} - Size: {get_file_size_formatted(file_path)}\n"
        text_widget.insert(tk.END, file_info)

    text_widget.grid_rowconfigure(0, weight=1)
    text_widget.grid_columnconfigure(0, weight=1)

    # Create buttons for selecting and deleting files
    select_every_other_button = customtkinter.CTkButton(frame, text="Select Every Other", command=lambda: select_items(2))
    select_every_other_button.grid(row=5, column=0, padx=5, sticky="nsew")

    select_every_third_button = customtkinter.CTkButton(frame, text="Select Every Third", command=lambda: select_items(3))
    select_every_third_button.grid(row=5, column=1, padx=5, sticky="nsew")

    select_all_button = customtkinter.CTkButton(frame, text="Select All", command=select_all)
    select_all_button.grid(row=5, column=2, padx=5, sticky="nsew")

    delete_button = customtkinter.CTkButton(frame, text="Delete Selected", command=delete_selected_duplicates)
    delete_button.grid(row=5, column=3, padx=5, sticky="nsew")

# Function to delete selected duplicates in the listbox
def delete_selected_duplicates():
    selected_items = listbox_results.curselection()

    for index in selected_items[::-1]:
        index = int(index)
        file_path = duplicate_files[index]
        os.remove(file_path)
        duplicate_files.pop(index)
        listbox_results.delete(index)

    result_label.config(text=f"Deleted {len(selected_items)} file(s).")

# Function to select files based on a step value
def select_items(step):
    for i in range(0, len(DuplicateFile), step):
        listbox_results.selection_set(i)

# Function to select all files
def select_all():
    listbox_results.select_set(0, tk.END)

# Function to search for duplicate files
def search_duplicates():
    search_directory = entry_directory.get()

    if not search_directory:
        result_label.configure(text="Please enter a directory.")
        return

    duplicate_files = []  # Initialize an empty list to hold duplicate files

    def search_and_list_duplicates():
        nonlocal duplicate_files  # Use nonlocal since we are modifying the outer duplicate_files

        duplicate_files.extend(compare_files_by_hash(search_directory))

        if duplicate_files:
            list_duplicates_same_window(duplicate_files)
        else:
            result_label.config(text="No duplicate files found.")

    search_thread = Thread(target=search_and_list_duplicates)
    search_thread.start()

    start_time = time.time()  # Record the start time

    # Create a label to display the elapsed time
    time_label = customtkinter.CTkLabel(frame, text="")
    time_label.grid(row=5, column=5)

# Create the main window
root = customtkinter.CTk()
root.title("Modern Duplicate File Finder & Deleter App")

frame = customtkinter.CTkFrame(master=root)
frame.grid(row=0, column=0, sticky="nsew")

# Configure row and column weights for responsiveness
for i in range(6):
    frame.grid_rowconfigure(i, weight=1)
    frame.grid_columnconfigure(i, weight=1)

label_directory = customtkinter.CTkLabel(frame, text="Search Directory:")
label_directory.grid(row=0, column=0, sticky="w")

entry_directory = customtkinter.CTkEntry(frame)
entry_directory.grid(row=0, column=1, sticky="ew")

browse_button = customtkinter.CTkButton(frame, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=2, sticky="w")

find_button = customtkinter.CTkButton(frame, text="Find Duplicates", command=search_duplicates)
find_button.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

result_label = customtkinter.CTkLabel(frame, text="")
result_label.grid(row=3, column=0, columnspan=6, sticky="nsew")

close_button = customtkinter.CTkButton(frame, text="Close", command=root.quit)
close_button.grid(row=6, column=0, columnspan=6, pady=10, sticky="nsew")

root.mainloop()
