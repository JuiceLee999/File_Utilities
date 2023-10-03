import tkinter as tk
from tkinter import filedialog
import os
import glob
import tkinter.messagebox as messagebox
from tkinter.ttk import Progressbar
import threading

def browse_directory():
    selected_directory = filedialog.askdirectory()
    if selected_directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, selected_directory)

def update_progress_bar(current_progress, total_files, progress_bar, progress_label, deleted_label):
    percentage = (current_progress / total_files) * 100
    progress_bar["value"] = percentage
    progress_label.config(text=f"{int(percentage)}%")
    root.update_idletasks()

def search_files():
    search_criteria = entry_criteria.get()
    search_directory = entry_directory.get()

    if not search_criteria or not search_directory:
        result_label.config(text="Please enter both criteria and directory.")
        return

    def search():
        nonlocal current_progress

        try:
            result_text.delete(1.0, tk.END)  # Clear previous results

            # Use os.walk to search for files matching the criteria in the directory and its subdirectories
            for root, _, file_list in os.walk(search_directory):
                for filename in file_list:
                    if search_criteria in filename:
                        result_text.insert(tk.END, os.path.join(root, filename) + "\n")

                        # Update progress bar
                        current_progress += 1
                        update_progress_bar(current_progress, total_files, progress_bar, progress_label, deleted_label)

            result_label.config(text=f"Found {current_progress} file(s).")

            # Hide the progress bar when the search is complete
            progress_bar.grid_remove()
            progress_label.grid_remove()
            deleted_label.grid_remove()

        except Exception as e:
            result_label.config(text=f"An error occurred: {str(e)}")

    total_files = sum([len(files) for _, _, files in os.walk(search_directory)])
    current_progress = 0

    progress_bar = Progressbar(frame, orient="horizontal", length=200, mode="determinate")
    progress_bar.grid(row=5, columnspan=3, pady=10)
    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    progress_label = tk.Label(frame, text="")
    progress_label.grid(row=6, column=1)

    deleted_label = tk.Label(frame, text="")
    deleted_label.grid(row=6, column=2)

    threading.Thread(target=search).start()

def delete_files():
    search_criteria = entry_criteria.get()
    search_directory = entry_directory.get()

    if not search_criteria or not search_directory:
        result_label.config(text="Please enter both criteria and directory.")
        return

    def delete():
        nonlocal current_progress

        try:
            # Use os.walk to search for files matching the criteria in the directory and its subdirectories
            for root, _, file_list in os.walk(search_directory):
                for filename in file_list:
                    if search_criteria in filename:
                        file_path = os.path.join(root, filename)
                        os.remove(file_path)

                        # Update progress bar and file count
                        current_progress += 1
                        update_progress_bar(current_progress, total_files, progress_bar, progress_label, deleted_label)
                        deleted_label.config(text=f"Deleted {current_progress} file(s)")

            result_label.config(text=f"Deleted {current_progress} file(s).")
            result_text.delete(1.0, tk.END)  # Clear the result text after deletion

            # Hide the progress bar when the deletion is complete
            progress_bar.grid_remove()
            progress_label.grid_remove()
            deleted_label.grid_remove()

        except Exception as e:
            result_label.config(text=f"An error occurred: {str(e)}")

    total_files = sum([len(files) for _, _, files in os.walk(search_directory)])
    current_progress = 0

    progress_bar = Progressbar(frame, orient="horizontal", length=200, mode="determinate")
    progress_bar.grid(row=5, columnspan=3, pady=10)
    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    progress_label = tk.Label(frame, text="")
    progress_label.grid(row=6, column=1)

    deleted_label = tk.Label(frame, text="")
    deleted_label.grid(row=6, column=2)

    threading.Thread(target=delete).start()

# Create the main window
root = tk.Tk()
root.iconbitmap("images/juice_lee_icon.ico")
root.title("Juiceyware - Search and Destroy")

# Create and configure the widgets
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label_criteria = tk.Label(frame, text="Search Criteria:")
label_criteria.grid(row=0, column=0, sticky="w")

entry_criteria = tk.Entry(frame)
entry_criteria.grid(row=0, column=1)

label_directory = tk.Label(frame, text="Search Directory:")
label_directory.grid(row=1, column=0, sticky="w")

entry_directory = tk.Entry(frame)
entry_directory.grid(row=1, column=1)

browse_button = tk.Button(frame, text="Browse", command=browse_directory)
browse_button.grid(row=1, column=2)

search_button = tk.Button(frame, text="Search", command=search_files)
search_button.grid(row=2, column=0)

delete_button = tk.Button(frame, text="Delete", command=delete_files)
delete_button.grid(row=2, column=1)

result_label = tk.Label(frame, text="")
result_label.grid(row=3, columnspan=3)

result_text = tk.Text(frame, height=10, width=50)
result_text.grid(row=4, columnspan=3)

# Start the GUI main loop
root.mainloop()
