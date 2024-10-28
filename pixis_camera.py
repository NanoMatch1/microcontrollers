import pylablib as pll
from pylablib.devices import PrincetonInstruments
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import threading
import time
import os


class PIXISCam:

    def __init__(self, Microscope=None):
        try:
            self.microscope = Microscope
            self.transientDir = self.microscope.transientDir

            self.cam = PrincetonInstruments.PicamCamera()
            self.cam.set_attribute_value("Exposure Time", 1000)
            # self.cam.set_roi(0, 1024, 579, 579 + 35, 1, 35)
            self.cam.set_roi(0, 1024, 100, 100 + 900, 1, 900)
            self.camera_lock = threading.Lock()  # Initialize a lock
            self.stop_flag = threading.Event() # Initialize a stop flag
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            self.cam = None

        self.command_history = []  # List to store command history
        self.history_index = -1    # Index to track the current position in the history
        self.prompt_text = ">"  # Prompt text to indicate where the user types

    def _initialise_ui(self):
        # Initialize the Tkinter window
        self.root = tk.Tk()
        self.root.title("Camera Acquisition")

        # Matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.plot_data, = self.ax.plot([], [], 'r-')
        self.ax.vlines([50], 0, 70000)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)

        # Variables for camera control
        # self.stop_flag = threading.Event()

        # Terminal display for command input/output
        self.terminal_display = tk.Text(self.root, height=20, width=50)
        self.terminal_display.grid(row=0, column=1, padx=10, pady=10, rowspan=4)
        self.terminal_display.bind("<Return>", self.process_command)
        self.terminal_display.bind("<Up>", self.recall_previous_command)
        self.terminal_display.bind("<Down>", self.recall_next_command)
        self.terminal_display.bind("<Key>", self.prevent_modifying_above_prompt)

        self.terminal_display.config(state=tk.NORMAL)
        self.write_prompt()

    def _update_plot(self, data):
        if data is None:
            return

        if len(data) == 1:  # quick fix for data formatting. Return this to the function
            data = data[0]

        self.plot_data.set_data(np.arange(len(data)), data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        return data
    
    def test_acquire_series(self):
        self.microscope.data = []
        for x in range(3):
            print('Run a thread to move mocrsocpe')
            frame = self.acquire_one_frame()
            self._update_plot(frame)   
            self.microscope.data.append([x, frame])
            print("Acquired frame {}".format(x))

        print("Acquired all frames")


    def acquire_one_frame(self):
        self.cam.setup_acquisition(mode='sequence', nframes=2)
        self.cam.start_acquisition()
        self.cam.wait_for_frame()
        frame = self.cam.read_oldest_image()
        self.cam.stop_acquisition()
        self.cam.clear_acquisition()
        if frame is None:
            return
        data = frame[0]
        # data = self._update_plot(frame)
        return data

    def continuous_acquisition(self):
        '''Acquires frames continuously until the stop flag is set. Saves the data to the transient file for plotting.'''
        self.stop_flag.clear()
        self.cam.setup_acquisition(mode='sequence', nframes=100)
        self.cam.start_acquisition()
        self.write_dir = self.microscope.transientDir

        while not self.stop_flag.is_set():
            try:
                with self.camera_lock:
                    self.cam.wait_for_frame()
                    frame = self.cam.read_oldest_image()
                # data = self._update_plot(frame)
                if frame is None:
                    continue

                data = np.array(frame[0], dtype=np.int32)
                np.save(os.path.join(self.transientDir, "transient_data.npy"), data)
                time.sleep(0.001)
            except Exception as e:
                # self.log_terminal(f"Acquisition error: {e}")
                print(f"Acquisition error: {e}")
                break

        self.cam.stop_acquisition()

    def start_continuous_acquisition(self):
        acq_thread = threading.Thread(target=self.continuous_acquisition)
        acq_thread.daemon = True
        acq_thread.start()
        print("Started continuous acquisition.")

    def stop_continuous_acquisition(self):
        print("Stopping continuous acquisition.")
        self.stop_flag.set()

    def log_terminal(self, message):
        """Append messages to the terminal display and write a new prompt."""
        self.terminal_display.config(state=tk.NORMAL)
        self.terminal_display.insert(tk.END, f"{message}\n")
        self.terminal_display.config(state=tk.DISABLED)
        self.terminal_display.see(tk.END)  # Scroll to the bottom
        self.write_prompt()

    def write_prompt(self):
        """Write a prompt to indicate where the user can type."""
        self.terminal_display.config(state=tk.NORMAL)
        self.terminal_display.insert(tk.END, self.prompt_text)
        self.terminal_display.config(state=tk.DISABLED)
        self.terminal_display.mark_set(tk.INSERT, tk.END)
        self.terminal_display.config(state=tk.NORMAL)
        self.terminal_display.focus()

    def get_current_input(self):
        """Get the user input since the last prompt."""
        prompt_idx = self.terminal_display.search(self.prompt_text, "1.0", tk.END)
        if prompt_idx:
            command = self.terminal_display.get(f"{prompt_idx}+{len(self.prompt_text)}c", tk.END).strip()
            return command
        return ""

    def prevent_modifying_above_prompt(self, event):
        """Prevent the user from modifying text above the current command prompt."""
        prompt_idx = self.terminal_display.search(self.prompt_text, "1.0", tk.END)
        if self.terminal_display.compare(tk.INSERT, "<", f"{prompt_idx}+{len(self.prompt_text)}c"):
            return "break"  # Prevent editing above the prompt

    def process_command(self, event=None):
        """Process the command input from the terminal display when Enter is pressed."""
        com = self.get_current_input()
        command = com.split('\n')[-1].strip('>')
        self.terminal_display.config(state=tk.NORMAL)

        if command:
            self.command_history.append(command)
            self.history_index = len(self.command_history)  # Reset history index

        self.terminal_display.insert(tk.END, "\n")  # Move to the next line
        self.terminal_display.config(state=tk.DISABLED)

        # Process commands in a non-blocking manner
        if command == "acquire":
            threading.Thread(target=self.acquire_one_frame).start()
        elif command == "test":
            threading.Thread(target=self.test_acquire_series).start()
        elif command == "run":
            threading.Thread(target=self.start_continuous_acquisition).start()
        elif command == "stop":
            self.stop_continuous_acquisition()
        elif command == "exit":
            self.stop_continuous_acquisition()
            if self.cam:
                self.cam.close()
            self.root.quit()
        else:
            self.log_terminal(f"Error: {e}")
            # try:
                # threading.Thread(self.microscope.process_coms(command)).start()
            # except Exception as e:

        self.write_prompt()  # Show the next prompt

    def recall_previous_command(self, event):
        """Recall the previous command when Up arrow is pressed."""
        if self.history_index > 0:
            self.history_index -= 1
            previous_command = self.command_history[self.history_index]
            self.replace_current_input(previous_command)
        return "break"  # Prevents default Tkinter behavior

    def recall_next_command(self, event):
        """Recall the next command when Down arrow is pressed."""
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            next_command = self.command_history[self.history_index]
            self.replace_current_input(next_command)
        elif self.history_index == len(self.command_history) - 1:
            self.history_index += 1
            self.replace_current_input("")
        return "break"  # Prevents default Tkinter behavior

    def replace_current_input(self, text):
        """Replace the current input with the given text."""
        self.terminal_display.config(state=tk.NORMAL)
        prompt_idx = self.terminal_display.search(self.prompt_text, "1.0", tk.END)
        if prompt_idx:
            self.terminal_display.delete(f"{prompt_idx}+{len(self.prompt_text)}c", tk.END)
            self.terminal_display.insert(tk.END, text)
        self.terminal_display.config(state=tk.DISABLED)
        self.terminal_display.mark_set(tk.INSERT, tk.END)
        self.terminal_display.focus()

    def _ui_layout(self):
        '''Layout the UI elements. Call within the start_ui method.'''
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=5)

    def start_ui(self):
        self._initialise_ui()
        self._ui_layout()

        # Start the Tkinter main loop
        self.root.mainloop()

