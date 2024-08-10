import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Create figure for plotting
fig, ax = plt.subplots()
xs = []  # List to store x-axis values (time steps)
ys = []  # List to store y-axis values (data points)

# Initialize plot
line, = ax.plot(xs, ys, 'r-')  # 'r-' means red line

def init():
    ax.set_xlim(0, 10)  # Set initial x-axis limits
    ax.set_ylim(0, 1)  # Set initial y-axis limits
    return line,

def update_data(new_data_point):
    # Append new data points to the lists
    xs.append(len(xs))
    ys.append(new_data_point)
    
    # Update line data
    line.set_data(xs, ys)
    
    # Adjust x-axis and y-axis limits dynamically
    ax.set_xlim(0, len(xs))
    ax.set_ylim(0, max(ys) + 0.1)
    
    return line,

def data_gen():
    while True:
        yield np.random.random()  # Replace with your actual data collection logic

# Create an animation
ani = animation.FuncAnimation(fig, update_data, data_gen, init_func=init, blit=True, interval=100)

# Display the plot
plt.show()
