import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt

# def simple_sin_fit(xvalues, a, b, c, d):
#     return a * np.sin(b * xvalues + c) + d

# # Original sine function
# testsin = lambda x: 3 * np.sin(2 * x) + 1

# # Generate test data
# x = np.linspace(0, 10, 100)
# y = testsin(x) + np.random.normal(0, 0.5, x.shape)

# # Initial guesses for [a, b, c, d]
# initial_guess = [3, 2, 0, 1]  # Guessed based on the known form of the test function

# # Fit the data
# popt, pcov = opt.curve_fit(simple_sin_fit, x, y, p0=initial_guess)

# # Print optimized parameters
# print("Optimized parameters:", popt)

# # Plot data and fit
# plt.scatter(x, y, label='data')
# plt.plot(x, simple_sin_fit(x, *popt), label='fit', color='r')
# plt.legend()
# plt.show()

def solve_quadradic(a, b, c):
    return (-b + np.sqrt(b**2 - 4*a*c))/(2*a), (-b - np.sqrt(b**2 - 4*a*c))/(2*a)

wl_to_l1 = [0.01044297831495296, -74.71476555270314, 54132.34178807134]
p_wl_to_l1 = np.poly1d(wl_to_l1)

pos, neg = solve_quadradic(*wl_to_l1)

forward_solution = p_wl_to_l1(pos)
rev_solution = p_wl_to_l1(neg)
print(pos, neg)
print(forward_solution)
print(rev_solution)
