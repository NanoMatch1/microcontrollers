import pylablib as pll
from pylablib.devices import PrincetonInstruments
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import threading
import time

# Initialize camera

class PIXISCam:

    def __init__(self, Microscope):
        try:
            self.microscope = Microscope
            self.cam = PrincetonInstruments.PicamCamera()
            self.cam.set_attribute_value("Exposure Time", 100)
            self.cam.set_roi(0, 1024, 579, 579+35, 1, 35)
            self.camera_lock = threading.Lock()  # Initialize a lock
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            self.cam = None

    def _initialise_ui(self):
        # Initialize the Tkinter window
        self.root = tk.Tk()
        self.root.title("Camera Acquisition")

        # Matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.plot_data, = self.ax.plot([], [], 'r-')
        self.ax.vlines([50], 0, 70000)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Variables for camera control
        self.stop_flag = threading.Event()

    def _update_plot(self, data):
        if data is None:
            return

        self.plot_data.set_data(np.arange(len(data)), data)

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def acquire_one_frame(self):
        self.cam.setup_acquisition(mode='snap', nframes=1)
        self.cam.start_acquisition()
        self.cam.wait_for_frame()
        frame = self.cam.read_oldest_image()
        if frame is None:
            return
        
        if len(frame) == 1:
            frame = frame[0]

        self._update_plot(frame)
        self.cam.stop_acquisition()
        
        return frame

    def continuous_acquisition(self):
        self.stop_flag.clear()
        self.cam.setup_acquisition(mode='sequence', nframes=100)
        self.cam.start_acquisition()

        while not self.stop_flag.is_set():
            try:
                with self.camera_lock:
                    frame = self.cam.read_oldest_image()
                self._update_plot(frame)
                time.sleep(0.01)
            except Exception as e:
                print(f"Acquisition error: {e}")
                break

        self.cam.stop_acquisition()
    
    def start_continuous_acquisition(self):
        acq_thread = threading.Thread(target=self.continuous_acquisition)
        acq_thread.daemon = True
        acq_thread.start()

    def stop_continuous_acquisition(self):
        self.stop_flag.set()

    def process_filename(self):
        self.microscope.series_filename = self.cli_filename.get().strip()

    def start_ui(self):
        self._initialise_ui()
        self.cli_entry = tk.Entry(self.root)
        self.cli_entry.pack()
        self.cli_entry.bind("<Return>", lambda event: process_command())
        self.cli_filename = tk.Entry(self.root)
        self.cli_filename.pack()
        self.cli_filename.bind("<Return>", lambda event: self.process_filename())

        cli_label = tk.Label(self.root, text="Enter command (acquire/run/stop/exit):")
        cli_label.pack()

        def process_command():
            command = self.cli_entry.get().strip()

            if command == "acquire":
                self.acquire_one_frame()
            elif command == "run":
                self.start_continuous_acquisition()
            elif command == "stop":
                self.stop_continuous_acquisition()
            if command == "exit":
                self.stop_continuous_acquisition()  # Ensure acquisition is stopped
                if self.cam:
                    self.cam.close()
                self.root.quit()

            self.cli_entry.delete(0, tk.END)

        # Start the Tkinter main loop
        self.root.mainloop()

    

# cam = PrincetonInstruments.PicamCamera()

# 
# Initialize the Tkinter window
# root = tk.Tk()
# root.title("Camera Acquisition")

# # Matplotlib figure
# fig, ax = plt.subplots()
# plot_data, = ax.plot([], [], 'r-')
# ax.vlines([50], 0, 70000)
# canvas = FigureCanvasTkAgg(fig, master=root)
# canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# # Variables for camera control
# stop_flag = threading.Event()

# def update_plot(data):
#     if data is None:
#         return
    
#     # print('1')
#     # ax.vlines([50], min(plot_data.get_xdata()), max(plot_data.get_ydata()))
#     # print(max(data))

#     # print(data)
#     # print(len(data[:, 0]))
#     # print(len(data[0, :]))
#     if len(data) == 1:
#         data = data[0]
#     # print(len(data))
#     plot_data.set_data(np.arange(len(data)), data)

#     # print('2')

#     ax.relim()

#     # print('3')
#     ax.autoscale_view()

#     # print('4')
#     canvas.draw()

# def acquire_one_frame():
#     cam.setup_acquisition(mode='snap', nframes=1)
#     cam.start_acquisition()
#     cam.wait_for_frame()
#     frame = cam.read_oldest_image()
#     update_plot(frame)
#     cam.stop_acquisition()

# def continuous_acquisition():
#     stop_flag.clear()
#     cam.setup_acquisition(mode='sequence', nframes=100)
#     cam.start_acquisition()

#     while not stop_flag.is_set():
#         try:
#             frame = cam.read_oldest_image()
#             update_plot(frame)
#             time.sleep(0.01)  # Delay for smooth GUI updating
#         except Exception as e:
#             print(f"Acquisition error: {e}")
#             break

#     cam.stop_acquisition()

# def start_continuous_acquisition():
#     acq_thread = threading.Thread(target=continuous_acquisition)
#     acq_thread.daemon = True
#     acq_thread.start()

# def stop_continuous_acquisition():
#     stop_flag.set()

# # CLI Entry box
# def process_command():
#     command = cli_entry.get().strip()
#     if command == "acquire":
#         acquire_one_frame()
#     elif command == "run":
#         start_continuous_acquisition()
#     elif command == "stop":
#         stop_continuous_acquisition()
#     elif command == "exit":
#         cam.close()
#         root.quit()
#     cli_entry.delete(0, tk.END)

# # CLI for command input
# cli_label = tk.Label(root, text="Enter command (acquire/run/stop/exit):")
# cli_label.pack()

# cli_entry = tk.Entry(root)
# cli_entry.pack()
# cli_entry.bind("<Return>", lambda event: process_command())

# Start the Tkinter main loop
# root.mainloop()
