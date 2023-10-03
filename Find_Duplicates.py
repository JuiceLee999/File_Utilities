import tkinter as tk
from tkinter import filedialog
import os
import hashlib
from tkinter import messagebox
from tkinter.ttk import Progressbar
import threading

def browse_directory():
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, selected_directory)

def update_progress_bar(current_progress, total_files, progress_bar, progress_label):
    percentage = (current_progress / total_files) * 100
    progress_bar["value"] = percentage
    progress_label.config(text=f"{int(percentage)}%")
    root.update_idletasks()

def search_duplicates():
    search_directory = entry_directory.get()

    if not search_directory:
        result_label.config(text="Please enter a directory.")
        return

    def compare_files_by_name():
        file_name_map = {}

        for root, _, file_list in os.walk(search_directory):
            for filename in file_list:
                file_path = os.path.join(root, filename)
                if filename in file_name_map:
                    file_name_map[filename].append(file_path)
                else:
                    file_name_map[filename] = [file_path]

        duplicate_files = [file_list for file_list in file_name_map.values() if len(file_list) > 1]

        if duplicate_files:
            result_label.config(text=f"Found {len(duplicate_files)} set(s) of duplicate files.")
        else:
            result_label.config(text="No duplicate files found.")

        return duplicate_files

    def compare_files_by_hash():
        hash_map = {}

        for root, _, file_list in os.walk(search_directory):
            for filename in file_list:
                file_path = os.path.join(root, filename)

                try:
                    with open(file_path, "rb") as file:
                        file_hash = hashlib.md5(file.read()).hexdigest()
                        if file_hash in hash_map:
                            hash_map[file_hash].append(file_path)
                        else:
                            hash_map[file_hash] = [file_path]
                except Exception as e:
                    continue

        duplicate_files = [file_list for file_list in hash_map.values() if len(file_list) > 1]

        if duplicate_files:
            result_label.config(text=f"Found {len(duplicate_files)} set(s) of duplicate files.")
        else:
            result_label.config(text="No duplicate files found.")

        return duplicate_files

    def delete_selected_duplicates():
        selected_items = listbox_results_left.curselection()

        for index in selected_items:
            index = int(index)
            file_path = duplicate_files_left[index]
            os.remove(file_path)
            duplicate_files_left.pop(index)
            listbox_results_left.delete(index)
            current_progress += 1
            update_progress_bar(current_progress, total_files, delete_progress_bar, delete_progress_label)

        result_label.config(text=f"Deleted {current_progress} file(s).")

    def select_one_file_per_line():
        selected_items = listbox_results_left.curselection()

        if not selected_items:
            messagebox.showinfo("No Selection", "Please select at least one item.")
            return

        for index in selected_items:
            index = int(index)
            file_path = duplicate_files_left[index]
            # Here, you can implement the logic to handle the selected file
            # For example, you can open the selected file, copy it, or perform other actions.
            print(f"Selected file from left box: {file_path}")

    def update_results_list():
        listbox_results_left.delete(0, tk.END)
        listbox_results_right.delete(0, tk.END)
        for file_info in duplicate_files_left:
            listbox_results_left.insert(tk.END, file_info)
        for file_info in duplicate_files_right:
            listbox_results_right.insert(tk.END, file_info)

    # Check which comparison method is selected
    selected_option = comparison_method.get()
    if selected_option == 0:
        duplicate_files = compare_files_by_name()
    else:
        duplicate_files = compare_files_by_hash()

    # Split duplicate files into two separate lists
    duplicate_files_left = duplicate_files[:len(duplicate_files)//2]
    duplicate_files_right = duplicate_files[len(duplicate_files)//2:]

    total_files = len(duplicate_files_left) + len(duplicate_files_right)
    current_progress = 0

    # Hide the progress bar for search once the search is complete
    search_progress_bar.grid_remove()
    search_progress_label.grid_remove()

    # Display the progress bar for delete
    delete_progress_bar = Progressbar(frame, orient="horizontal", length=200, mode="determinate")
    delete_progress_bar.grid(row=7, columnspan=3, pady=10)
    delete_progress_bar["maximum"] = 100
    delete_progress_bar["value"] = 0

    delete_progress_label = tk.Label(frame, text="")
    delete_progress_label.grid(row=8, column=1)

    deleted_label = tk.Label(frame, text="")
    deleted_label.grid(row=8, column=2)

    listbox_results_left = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=10, width=40)
    listbox_results_left.grid(row=6, column=0, pady=10)

    listbox_results_right = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=10, width=40)
    listbox_results_right.grid(row=6, column=1, pady=10)

    for file_info in duplicate_files_left:
        listbox_results_left.insert(tk.END, file_info)
    for file_info in duplicate_files_right:
        listbox_results_right.insert(tk.END, file_info)

    delete_button = tk.Button(frame, text="Delete Selected", command=delete_selected_duplicates)
    delete_button.grid(row=9, column=0, columnspan=3, pady=10)

    # Create a new button to select one file per line from the left box
    select_button = tk.Button(frame, text="Select One File per Line (Left Box)", command=select_one_file_per_line)
    select_button.grid(row=10, column=0, pady=10)

# Create the main window
root = tk.Tk()
root.title("Duplicate File Finder & Deleter App")

# Create and configure the widgets
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label_directory = tk.Label(frame, text="Search Directory:")
label_directory.grid(row=0, column=0, sticky="w")

entry_directory = tk.Entry(frame)
entry_directory.grid(row=0, column=1)

browse_button = tk.Button(frame, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=2)

comparison_method = tk.IntVar()
radio_name = tk.Radiobutton(frame, text="Compare by File Name", variable=comparison_method, value=0)
radio_name.grid(row=1, column=0, columnspan=3, sticky="w")
radio_hash = tk.Radiobutton(frame, text="Compare by Hash Value", variable=comparison_method, value=1)
radio_hash.grid(row=2, column=0, columnspan=3, sticky="w")
comparison_method.set(0)  # Default to compare by file name

find_button = tk.Button(frame, text="Find Duplicates", command=search_duplicates)
find_button.grid(row=3, column=0, columnspan=3, pady=10)

result_label = tk.Label(frame, text="")
result_label.grid(row=4, columnspan=3)

# Display the progress bar for search
search_progress_bar = Progressbar(frame, orient="horizontal", length=200, mode="determinate")
search_progress_bar.grid(row=5, columnspan=3, pady=10)
search_progress_bar["maximum"] = 100
search_progress_bar["value"] = 0

search_progress_label = tk.Label(frame, text="")
search_progress_label.grid(row=6, column=1)

# Start the GUI main loop
root.mainloop()
