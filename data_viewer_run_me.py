import numpy as np
import matplotlib.pyplot as plt
import os
import time
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Correct import for Tkinter integration
# File path
scriptDir = os.path.dirname(__file__)
file_path = os.path.join(scriptDir, 'transient', 'transient_data.npy')
print(file_path)

# File path
# file_path = 'integer_data.npy'

# Function to update the plot with new data
def update_plot(data, line, ax):
    line.set_xdata(np.arange(len(data)))  # X-axis as index values
    line.set_ydata(data)  # Y-axis as the loaded data
    ax.relim()  # Recalculate limits
    ax.autoscale_view()  # Rescale axes to show the data
    plt.draw()  # Redraw the plot

# Function to constantly check for file and update the plot
def monitor_file(line, ax):
    while True:
        try:
            if os.path.exists(file_path):
                # Load data from the file
                try:
                    data = np.load(file_path)
                except Exception as e:
                    print(f"Error loading data from file {file_path}: {e}")
                    # data = np.zeros(100)
                    time.sleep(1)
                    continue
                # print(f"Loaded data: {data}")
                
                # Update the plot
                update_plot(data, line, ax)
            # else:
                # print(f"File {file_path} not found. Checking again...")
        except PermissionError:
            print(f"Permission denied to access file {file_path}.")
        time.sleep(0.1)  # Wait for 1 second before checking again

# Main function to start the Tkinter GUI
def start_gui():
    # Set up the main window
    root = tk.Tk()
    root.title("Live Data Plotter")

    # Create a Matplotlib figure embedded in Tkinter
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'r-')  # Initialize an empty plot
    ax.vlines([50], 0, 70000)
    
    # Set up a Tkinter canvas for Matplotlib
    canvas = FigureCanvasTkAgg(fig, master=root)  # Corrected way to create canvas
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Start a background thread to monitor the file and update the plot
    thread = threading.Thread(target=monitor_file, args=(line, ax), daemon=True)
    thread.start()

    # Start the Tkinter event loop
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    start_gui()
