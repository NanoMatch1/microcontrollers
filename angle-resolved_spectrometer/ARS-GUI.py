import tkinter as tk
from tkinter import ttk
import numpy as np
import time

class SpectrometerGUI(tk.Tk):
    def __init__(self, spectrometer):
        super().__init__()
        self.spectrometer = spectrometer
        self.title("Angle-Resolved Spectrometer Control")
        self.geometry("600x500")

        # Specular vs. Uncoupled mode
        self.mode = tk.StringVar(value="specular")
        self.create_mode_switch()

        # Angle control
        self.create_angle_control()

        # Scan setup with mutually exclusive axis selection and dynamic parameter display
        self.create_scan_setup()

        # Tree representation of scan configuration
        self.create_scan_tree()

    def create_mode_switch(self):
        mode_frame = ttk.LabelFrame(self, text="Measurement Mode", padding=(10, 10))
        mode_frame.pack(padx=10, pady=10, fill="x")

        specular_rb = ttk.Radiobutton(mode_frame, text="Specular", variable=self.mode, value="specular", command=self.update_mode)
        uncoupled_rb = ttk.Radiobutton(mode_frame, text="Uncoupled", variable=self.mode, value="uncoupled", command=self.update_mode)

        specular_rb.pack(side="left", padx=5, pady=5)
        uncoupled_rb.pack(side="left", padx=5, pady=5)

    def create_angle_control(self):
        angle_frame = ttk.LabelFrame(self, text="Manual Angle Control", padding=(10, 10))
        angle_frame.pack(padx=10, pady=10, fill="x")

        self.x_angle = tk.DoubleVar()
        self.y_angle = tk.DoubleVar()

        x_label = ttk.Label(angle_frame, text="X Axis (deg):")
        x_entry = ttk.Entry(angle_frame, textvariable=self.x_angle, width=10)
        y_label = ttk.Label(angle_frame, text="Y Axis (deg):")
        y_entry = ttk.Entry(angle_frame, textvariable=self.y_angle, width=10)
        goto_button = ttk.Button(angle_frame, text="Goto", command=self.goto_angles)

        x_label.grid(row=0, column=0, padx=5, pady=5)
        x_entry.grid(row=0, column=1, padx=5, pady=5)
        y_label.grid(row=0, column=2, padx=5, pady=5)
        y_entry.grid(row=0, column=3, padx=5, pady=5)
        goto_button.grid(row=0, column=4, padx=5, pady=5)

    def create_scan_setup(self):
        self.scan_frame = ttk.LabelFrame(self, text="Scan Setup", padding=(10, 10))
        self.scan_frame.pack(padx=10, pady=10, fill="x")

        # Primary and Secondary Axis selection using mutually exclusive radio buttons
        self.primary_axis = tk.StringVar(value="X")
        self.secondary_axis = tk.StringVar(value="Y")

        primary_axis_label = ttk.Label(self.scan_frame, text="Primary Axis:")
        primary_x_rb = ttk.Radiobutton(self.scan_frame, text="X", variable=self.primary_axis, value="X", command=self.update_secondary_axis)
        primary_y_rb = ttk.Radiobutton(self.scan_frame, text="Y", variable=self.primary_axis, value="Y", command=self.update_secondary_axis)

        secondary_axis_label = ttk.Label(self.scan_frame, text="Secondary Axis:")
        self.secondary_x_rb = ttk.Radiobutton(self.scan_frame, text="X", variable=self.secondary_axis, value="X", state="normal")
        self.secondary_y_rb = ttk.Radiobutton(self.scan_frame, text="Y", variable=self.secondary_axis, value="Y", state="normal")

        primary_axis_label.grid(row=0, column=0, padx=5, pady=5)
        primary_x_rb.grid(row=0, column=1, padx=5, pady=5)
        primary_y_rb.grid(row=0, column=2, padx=5, pady=5)

        secondary_axis_label.grid(row=1, column=0, padx=5, pady=5)
        self.secondary_x_rb.grid(row=1, column=1, padx=5, pady=5)
        self.secondary_y_rb.grid(row=1, column=2, padx=5, pady=5)

        # Angle settings for the scan
        start_angle_label = ttk.Label(self.scan_frame, text="1 Start Angle (deg):")
        stop_angle_label = ttk.Label(self.scan_frame, text="1 Stop Angle (deg):")
        resolution_label = ttk.Label(self.scan_frame, text="1 Step Resolution (deg):")

        self.primary_start_angle = tk.DoubleVar()
        self.primary_stop_angle = tk.DoubleVar()
        self.primary_resolution = tk.DoubleVar()

        self.secondary_start_angle = tk.DoubleVar()
        self.secondary_stop_angle = tk.DoubleVar()
        self.secondary_resolution = tk.DoubleVar()

        # Trace changes in the angle values and update UI when edited
        self.primary_start_angle.trace_add("write", self.update_scan_tree)
        self.primary_stop_angle.trace_add("write", self.update_scan_tree)
        self.primary_resolution.trace_add("write", self.update_scan_tree)
        self.secondary_start_angle.trace_add("write", self.update_scan_tree)
        self.secondary_stop_angle.trace_add("write", self.update_scan_tree)
        self.secondary_resolution.trace_add("write", self.update_scan_tree)

        start_angle_entry = ttk.Entry(self.scan_frame, textvariable=self.primary_start_angle, width=10)
        stop_angle_entry = ttk.Entry(self.scan_frame, textvariable=self.primary_stop_angle, width=10)
        resolution_entry = ttk.Entry(self.scan_frame, textvariable=self.primary_resolution, width=10)

        start_angle_label.grid(row=2, column=0, padx=5, pady=5)
        start_angle_entry.grid(row=2, column=1, padx=5, pady=5)
        stop_angle_label.grid(row=2, column=2, padx=5, pady=5)
        stop_angle_entry.grid(row=2, column=3, padx=5, pady=5)
        resolution_label.grid(row=2, column=4, padx=5, pady=5)
        resolution_entry.grid(row=2, column=5, padx=5, pady=5)

        self.secondary_start_angle_entry = ttk.Entry(self.scan_frame, textvariable=self.secondary_start_angle, width=10)
        self.secondary_stop_angle_entry = ttk.Entry(self.scan_frame, textvariable=self.secondary_stop_angle, width=10)
        self.secondary_resolution_entry = ttk.Entry(self.scan_frame, textvariable=self.secondary_resolution, width=10)

        # Secondary row for uncoupled mode (initially hidden)
        self.secondary_start_angle_label = ttk.Label(self.scan_frame, text="2 Start Angle (deg):")
        self.secondary_stop_angle_label = ttk.Label(self.scan_frame, text="2 Stop Angle (deg):")
        self.secondary_resolution_label = ttk.Label(self.scan_frame, text="2 Step Resolution (deg):")

        start_scan_button = ttk.Button(self.scan_frame, text="Start Scan", command=self.start_scan)
        start_scan_button.grid(row=4, column=0, columnspan=6, pady=10)

        # Initially hide secondary axis controls
        self.toggle_secondary_axis_params(False)

    def create_scan_tree(self):
        tree_frame = ttk.LabelFrame(self, text="Scan Configuration", padding=(10, 10))
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.scan_tree = ttk.Treeview(tree_frame, columns=("Axis", "Start", "Stop", "Resolution"), show="headings")
        self.scan_tree.heading("Axis", text="Axis")
        self.scan_tree.heading("Start", text="Start Angle (deg)")
        self.scan_tree.heading("Stop", text="Stop Angle (deg)")
        self.scan_tree.heading("Resolution", text="Step Resolution (deg)")
        self.scan_tree.pack(fill="both", expand=True)

    def update_scan_tree(self, *args):
        self.scan_tree.delete(*self.scan_tree.get_children())
        # Update the scan tree with the selected scan configuration
        if self.mode.get() == "specular":
            self.scan_tree.insert("", "end", values=("X/Y", self.primary_start_angle.get(), self.primary_stop_angle.get(), self.primary_resolution.get()))
        if self.mode.get() == "uncoupled":
            self.scan_tree.insert("", "end", values=(self.primary_axis.get(), self.primary_start_angle.get(), self.primary_stop_angle.get(), self.primary_resolution.get()))
            self.scan_tree.insert("", "end", values=(self.secondary_axis.get(), self.secondary_start_angle.get(), self.secondary_stop_angle.get(), self.secondary_resolution.get()))

    def update_mode(self):
        mode = self.mode.get()
        print(f"Switched to {mode} mode.")
        if mode == "uncoupled":
            self.toggle_secondary_axis_params(True)
        else:
            self.toggle_secondary_axis_params(False)

    def update_secondary_axis(self):
        primary = self.primary_axis.get()

        # Disable the secondary axis option corresponding to the primary axis
        if primary == "X":
            self.secondary_x_rb.config(state="disabled")
            self.secondary_y_rb.config(state="normal")
            self.secondary_axis.set("Y")
        else:
            self.secondary_x_rb.config(state="normal")
            self.secondary_y_rb.config(state="disabled")
            self.secondary_axis.set("X")

    def toggle_secondary_axis_params(self, show):
        """Show or hide secondary axis parameters."""
        if show:
            self.secondary_start_angle_label.grid(row=3, column=0, padx=5, pady=5)
            self.secondary_start_angle_entry.grid(row=3, column=1, padx=5, pady=5)
            self.secondary_stop_angle_label.grid(row=3, column=2, padx=5, pady=5)
            self.secondary_stop_angle_entry.grid(row=3, column=3, padx=5, pady=5)
            self.secondary_resolution_label.grid(row=3, column=4, padx=5, pady=5)
            self.secondary_resolution_entry.grid(row=3, column=5, padx=5, pady=5)
        else:
            self.secondary_start_angle_label.grid_remove()
            self.secondary_start_angle_entry.grid_remove()
            self.secondary_stop_angle_label.grid_remove()
            self.secondary_stop_angle_entry.grid_remove()
            self.secondary_resolution_label.grid_remove()
            self.secondary_resolution_entry.grid_remove()

    def goto_angles(self):
        x = self.x_angle.get()
        y = self.y_angle.get()
        print(f"Moving to X: {x} deg, Y: {y} deg")
        self.update_scan_tree()
        self.spectrometer.go_to_angle(x, y)

    def start_scan(self):
        primary = self.primary_axis.get()
        secondary = self.secondary_axis.get()
        primary_start = self.primary_start_angle.get()
        primary_stop = self.primary_stop_angle.get()
        primary_resolution = self.primary_resolution.get()

        if self.mode.get() == "specular":
            self.run_specular_scan(primary_start, primary_stop, primary_resolution)
        elif self.mode.get() == "uncoupled":
            secondary_start = self.secondary_start_angle.get()
            secondary_stop = self.secondary_stop_angle.get()
            secondary_resolution = self.secondary_resolution.get()
            self.run_uncoupled_scan(primary_start, primary_stop, primary_resolution, secondary_start, secondary_stop, secondary_resolution)

    def run_specular_scan(self, start, stop, resolution):
        print(f"Running specular scan from {start}° to {stop}° with resolution {resolution}°.")
        for angle in range(int(start), int(stop), int(resolution)):
            print(f"Moving both axes to {angle}°")
            self.spectrometer.go_to_angle(angle, angle)
            # Simulate data collection or user pause
            input("Press Enter to continue to next angle...")

    def run_uncoupled_scan(self, p_start, p_stop, p_res, s_start, s_stop, s_res):
        print(f"Running uncoupled scan with primary axis from {p_start}° to {p_stop}° and secondary axis from {s_start}° to {s_stop}°.")
        for sec_angle in range(int(s_start), int(s_stop), int(s_res)):
            print(f"Moving secondary axis to {sec_angle}°")
            self.spectrometer.go_to_angle(None, sec_angle)  # Move only Y axis
            for pri_angle in range(int(p_start), int(p_stop), int(p_res)):
                print(f"Moving primary axis to {pri_angle}°")
                self.spectrometer.go_to_angle(pri_angle, sec_angle)  # Move both axes in sync
                # Simulate data collection or user pause
                input("Press Enter to continue to next primary axis angle...")

# For testing purposes, we'll create a dummy Spectrometer class
class DummySpectrometer:
    def go_to_angle(self, x, y):
        if x is None:
            print(f"Moving Y axis to {y}°")
        elif y is None:
            print(f"Moving X axis to {x}°")
        else:
            print(f"Moving X axis to {x}° and Y axis to {y}°")

# Instantiate the GUI with the dummy spectrometer
spectrometer = DummySpectrometer()
app = SpectrometerGUI(spectrometer)
app.mainloop()
