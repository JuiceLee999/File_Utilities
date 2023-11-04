import os
import cv2
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter import Scale, Button
import threading
from tqdm import tqdm  # Import tqdm for the progress bar

class DarkImageMoverApp:
    def __init__(self, root):
        self.root = root
        root.title("Dark Image Mover")

        # Initialize processing state
        self.processing = False
        self.paused = False

        # Create labels and buttons
        self.create_ui()

    def create_ui(self):
        self.source_folder_label = tk.Label(self.root, text="Select Source Folder:")
        self.source_folder_label.pack()
        self.source_folder_var = tk.StringVar()
        self.source_folder_entry = tk.Entry(self.root, textvariable=self.source_folder_var, state="readonly")
        self.source_folder_entry.pack()
        self.select_source_folder_button = tk.Button(self.root, text="Select Source Folder", command=self.select_source_folder)
        self.select_source_folder_button.pack()

        self.destination_folder_label = tk.Label(self.root, text="Select Destination Folder:")
        self.destination_folder_label.pack()
        self.destination_folder_var = tk.StringVar()
        self.destination_folder_entry = tk.Entry(self.root, textvariable=self.destination_folder_var, state="readonly")
        self.destination_folder_entry.pack()
        self.select_destination_folder_button = tk.Button(self.root, text="Select Destination Folder", command=self.select_destination_folder)
        self.select_destination_folder_button.pack()

        # Add a slider to select the darkness threshold
        self.threshold_label = tk.Label(self.root, text="Darkness Threshold:")
        self.threshold_label.pack()
        self.threshold_slider = Scale(self.root, from_=0, to=255, orient="horizontal")
        self.threshold_slider.set(50)  # Set the default threshold
        self.threshold_slider.pack()

        # Add buttons to control processing
        self.start_button = Button(self.root, text="Start Processing", command=self.start_processing)
        self.start_button.pack()
        self.pause_button = Button(self.root, text="Pause Processing", command=self.pause_processing)
        self.pause_button.pack()
        self.stop_button = Button(self.root, text="Stop Processing", command=self.stop_processing)
        self.stop_button.pack()

    def select_source_folder(self):
        source_folder_path = filedialog.askdirectory()
        if source_folder_path:
            self.source_folder_var.set(source_folder_path)

    def select_destination_folder(self):
        destination_folder_path = filedialog.askdirectory()
        if destination_folder_path:
            self.destination_folder_var.set(destination_folder_path)

    def is_extremely_dark(self, image, threshold=50):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.mean(gray)[0] < threshold

    def move_dark_images(self, source_folder, destination_folder, threshold, progress_var, progress_label):
        for root_folder, _, files in os.walk(source_folder):
            total_files = len(files)
            processed_files = 0

            for i, filename in enumerate(files):
                if not self.processing or self.paused:
                    break

                filepath = os.path.join(root_folder, filename)
                image = cv2.imread(filepath)

                if image is not None:
                    if self.is_extremely_dark(image, threshold):
                        destination_path = os.path.join(destination_folder, filename)
                        shutil.move(filepath, destination_path)

                processed_files += 1

                # Update progress
                progress = int((processed_files / total_files) * 100)
                progress_var.set(progress)
                progress_label.config(text=f"{progress}%")
                self.root.update()  # Update the GUI

    def start_processing(self):
        self.processing = True
        self.paused = False
        source_folder = self.source_folder_var.get()
        destination_folder = self.destination_folder_var.get()
        threshold = self.threshold_slider.get()  # Get the selected threshold value

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Create a progress bar widget
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(self.root, length=300, mode="determinate", variable=progress_var)
        progress_bar.pack()

        progress_label = tk.Label(self.root, text="0%")
        progress_label.pack()

        def process_thread():
            self.move_dark_images(source_folder, destination_folder, threshold, progress_var, progress_label)
            self.processing = False
            progress_label.config(text="100%")
            progress_var.set(100)
            progress_bar.destroy()  # Remove the progress bar when done
            if not self.paused:
                messagebox.showinfo("Done", "Dark images moved successfully!")

        # Create a thread to run the processing
        processing_thread = threading.Thread(target=process_thread)
        processing_thread.start()

    def pause_processing(self):
        self.paused = not self.paused

    def stop_processing(self):
        self.processing = False
        self.paused = False

if __name__ == "__main__":
    root = tk.Tk()
    app = DarkImageMoverApp(root)
    root.mainloop()
