import pylablib as pll
from pylablib.devices import PrincetonInstruments
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import threading
import time

# Initialize camera
cam = PrincetonInstruments.PicamCamera()

# Set exposure time and region of interest
cam.set_attribute_value("Exposure Time", 100)  # in ms
# cam.set_roi(0, 1024, 579, 579+35, 1, 35)
cam.set_roi(0, 1024, 579, 579+35, 1, 35)
# cam.set_roi()

# Initialize the Tkinter window
root = tk.Tk()
root.title("Camera Acquisition")

# Matplotlib figure
fig, ax = plt.subplots()
plot_data, = ax.plot([], [], 'r-')
ax.vlines([50], 0, 70000)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Variables for camera control
stop_flag = threading.Event()

def update_plot(data):
    if data is None:
        return
    
    # print('1')
    # ax.vlines([50], min(plot_data.get_xdata()), max(plot_data.get_ydata()))
    # print(max(data))

    # print(data)
    # print(len(data[:, 0]))
    # print(len(data[0, :]))
    if len(data) == 1:
        data = data[0]
    # print(len(data))
    plot_data.set_data(np.arange(len(data)), data)

    # print('2')

    ax.relim()

    # print('3')
    ax.autoscale_view()

    # print('4')
    canvas.draw()

def acquire_one_frame():
    cam.setup_acquisition(mode='snap', nframes=1)
    cam.start_acquisition()
    cam.wait_for_frame()
    frame = cam.read_oldest_image()
    update_plot(frame)
    cam.stop_acquisition()

def continuous_acquisition():
    stop_flag.clear()
    cam.setup_acquisition(mode='sequence', nframes=100)
    cam.start_acquisition()

    while not stop_flag.is_set():
        try:
            frame = cam.read_oldest_image()
            update_plot(frame)
            time.sleep(0.01)  # Delay for smooth GUI updating
        except Exception as e:
            print(f"Acquisition error: {e}")
            break

    cam.stop_acquisition()

def start_continuous_acquisition():
    acq_thread = threading.Thread(target=continuous_acquisition)
    acq_thread.daemon = True
    acq_thread.start()

def stop_continuous_acquisition():
    stop_flag.set()

# CLI Entry box
def process_command():
    command = cli_entry.get().strip()
    if command == "acquire":
        acquire_one_frame()
    elif command == "run":
        start_continuous_acquisition()
    elif command == "stop":
        stop_continuous_acquisition()
    elif command == "exit":
        cam.close()
        root.quit()
    cli_entry.delete(0, tk.END)

# CLI for command input
cli_label = tk.Label(root, text="Enter command (acquire/run/stop/exit):")
cli_label.pack()

cli_entry = tk.Entry(root)
cli_entry.pack()
cli_entry.bind("<Return>", lambda event: process_command())

# Start the Tkinter main loop
root.mainloop()
