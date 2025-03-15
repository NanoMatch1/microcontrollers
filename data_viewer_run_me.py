import numpy as np
import matplotlib.pyplot as plt
import os
import time
import threading
import tkinter as tk
import traceback
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LiveDataPlotter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.autoscale_enabled = True
        self.updating = True
        self.roi = None  # Region of Interest for autoscaling

        self.data_mode = "Image"
        self.spectrum_roi = (75,85)


        # Initialize Tkinter and Matplotlib
        self.root = tk.Tk()
        self.root.title("Live Data Plotter")

        # Create a Matplotlib figure embedded in Tkinter
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')  # Initialize an empty plot
        self.ax.vlines([50], 0, 70000)
        
        # Set up a Tkinter canvas for Matplotlib
        self._build_canvas()

        # Create control buttons and entry fields
        self.create_controls()

        # Start a background thread to monitor the file and update the plot
        self.monitor_thread = threading.Thread(target=self.monitor_file, daemon=True)
        self.monitor_thread.start()
    
    def _build_canvas(self):
        """ Destroy the old canvas, create a new figure, and add it back into the GUI. """
        if hasattr(self, "canvas"):  # Check if canvas exists before destroying
            self.canvas.get_tk_widget().destroy()  # Remove the old canvas from Tkinter
        
        # Create new figure and axis
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def toggle_data_mode(self):
        """ Toggle between 1D spectrum and 2D image display """
        self.data_mode = "Spectrum" if self.data_mode == "Image" else "Image"

        self._build_canvas()  # Rebuild the entire Matplotlib canvas

        if self.data_mode == "Spectrum":
            spectrum = self.frame_to_spectrum()
            self.ax.plot(np.arange(len(spectrum)), spectrum, 'r-')  # Plot 1D spectrum
        else:
            self.ax.imshow(self.data, cmap='plasma')  # Plot 2D image
        
        self.ax.set_title(self.data_mode)
        self.canvas.draw()

        # Update button text
        self.data_mode_button.config(text=self.data_mode)

    def create_controls(self):
        # Create a frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Autoscale toggle button
        autoscale_button = tk.Button(button_frame, text="Toggle Autoscale", command=self.toggle_autoscale)
        autoscale_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Start/Stop button for updating
        self.update_button = tk.Button(button_frame, text="Start/Stop Update", command=self.toggle_update)
        self.update_button.pack(side=tk.LEFT, padx=5, pady=5)

        # ROI selection for autoscale
        tk.Label(button_frame, text="ROI Start:").pack(side=tk.LEFT)
        self.roi_start = tk.Entry(button_frame, width=5)
        self.roi_start.pack(side=tk.LEFT)
        tk.Label(button_frame, text="ROI End:").pack(side=tk.LEFT)
        self.roi_end = tk.Entry(button_frame, width=5)
        self.roi_end.pack(side=tk.LEFT)
        
        # ROI Set button
        roi_button = tk.Button(button_frame, text="Set ROI", command=self.set_roi)
        roi_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Reset Autoscale button
        reset_button = tk.Button(button_frame, text="Reset Autoscale", command=self.reset_autoscale)
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        # data mode button

        self.data_mode_button = tk.Button(button_frame, text="{}".format(self.data_mode), command=self.toggle_data_mode)
        self.data_mode_button.pack(side=tk.LEFT, padx=5, pady=5)

    def toggle_autoscale(self):
        self.autoscale_enabled = not self.autoscale_enabled

    def toggle_update(self):
        self.updating = not self.updating
        if self.updating:
            # change button colour to green
            self.update_button.config(bg='green')
        else:
            # change button colour to red
            self.update_button.config(bg='red')

    def set_roi(self):
        try:
            min_x = int(self.roi_start.get())
            max_x = int(self.roi_end.get())
            self.roi = (min_x, max_x)
        except ValueError:
            print("Invalid ROI values")

    def reset_autoscale(self):
        self.roi = None
        self.ax.relim()
        self.ax.autoscale_view()

    def update_plot(self, data):
        # Plot the full data
        x_values = np.arange(len(data))
        self.line.set_xdata(x_values)
        self.line.set_ydata(data)

        # If autoscaling is enabled, adjust the Y-axis based on the ROI or full data
        if self.autoscale_enabled:
            if self.roi:  # Scale Y-axis based on ROI
                min_x, max_x = self.roi
                roi_data = data[min_x:max_x]
                y_min, y_max = np.min(roi_data), np.max(roi_data)
                self.ax.set_ylim(y_min, y_max)
            else:
                self.ax.relim()
                self.ax.autoscale_view()
        
        # Redraw the plot on the Tkinter canvas
        self.canvas.draw()

    def update_image(self, data):
        """ Update the displayed image with autoscaling based on the selected ROI. """
        self.ax.clear()  # Clear previous plot

        # Define the region of interest for autoscaling
        if self.roi:
            min_x, max_x = self.roi
            roi_data = data[min_x:max_x, :]  # Extract only the region of interest
        else:
            roi_data = data  # Use full data if no ROI is set

        # Determine the intensity limits based on ROI
        vmin, vmax = np.min(roi_data), np.max(roi_data)

        # Plot the image with autoscaled colormap
        self.ax.imshow(data, cmap='plasma', vmin=vmin, vmax=vmax)

        self.canvas.draw()  # Refresh the Tkinter canvas

    def frame_to_spectrum(self, roi=None):
        # Calculate the sum of each frame and store in the first column
        if not roi:
            roi = self.spectrum_roi

        spectrum_data = np.average(self.data[roi[0]:roi[1]], axis=0)
        return spectrum_data


    def monitor_file(self):
        while True:
            if self.updating:
                try:
                    if os.path.exists(self.file_path):
                        # Load data from the file
                        try:
                            self.data = np.load(self.file_path)
                            if len(self.data.shape) == 3:
                                self.data = self.data[:, :, 0]
                        except Exception as e:
                            print(f"Error loading data from file {self.file_path}: {e}")
                            time.sleep(1)
                            continue

                        if self.data_mode == "Image":
                            self.update_image(self.data)
                        else:
                            spectrum = self.frame_to_spectrum()
                            self.update_plot(spectrum)
                except PermissionError:
                    print(f"Permission denied to access file {self.file_path}.")
                except Exception as e:
                    print(f"Error processing file:\n{traceback.format_exc()}")
            time.sleep(0.1)  # Wait before checking again


    def start(self):
        # Start the Tkinter event loop
        self.root.mainloop()

# Run the GUI
if __name__ == "__main__":
    # Replace with your actual file path
    scriptDir = os.path.dirname(__file__)
    file_path = os.path.join(scriptDir, 'transient', 'transient_data.npy')

    plotter = LiveDataPlotter(file_path)
    plotter.start()
