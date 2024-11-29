import tkinter as tk
from tkinter import messagebox
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def parse_function(fs):
    try:
        fs = fs.replace('^', '**')
        x = sp.Symbol('x')
        parsed_func = sp.lambdify(x, sp.simplify(fs), 'numpy')
        return parsed_func
    except Exception as e:
        messagebox.showerror("Function Parsing Error", f"Unable to parse function: {e}")
        return None

def central_difference(f, x, h=0.01):
    try:
        derivative = (f(x+h) - f(x-h)) / (2*h)
        return derivative
    except Exception as e:
        messagebox.showerror("Differentiation Error", f"Error in numerical differentiation: {e}")
        return None

def monte_carlo_integration(f, a, b, n=10000):
    try:
        x = np.random.uniform(a, b, n)
        y = f(x)
        integral = (b-a) * np.mean(y)
        return integral
    except Exception as e:
        messagebox.showerror("Integration Error", f"Error in numerical integration: {e}")
        return None

def differentiate():
    try:
        func_str = function_entry.get()
        x_str = x_entry.get()
        
        if not func_str or not x_str:
            messagebox.showwarning("Input Error", "Please enter both function and x value.")
            return
        
        f = parse_function(func_str)
        if not f:
            return
        
        x = float(x_str)
        
        derivative = central_difference(f, x)
        
        if derivative is not None:
            result_label.config(text=f"Derivative at x = {x}: {derivative:.6f}")
    except ValueError:
        messagebox.showerror("Input Error", "Invalid x value. Please enter a number.")
    except Exception as e:
        messagebox.showerror("Differentiation Error", str(e))

def integrate():
    try:
        func_str = function_entry.get()
        a_str = a_entry.get()
        b_str = b_entry.get()
        
        if not func_str or not a_str or not b_str:
            messagebox.showwarning("Input Error", "Please enter a function and both bounds.")
            return
        
        f = parse_function(func_str)
        if not f:
            return
        
        a = float(a_str)
        b = float(b_str)
        
        if a >= b:
            messagebox.showerror("Bound Error", "Lower bound must be less than upper bound.")
            return
        
        integral = monte_carlo_integration(f, a, b)
        
        if integral is not None:
            result_label.config(text=f"Integral from {a} to {b}: {integral:.6f}")
    except ValueError:
        messagebox.showerror("Input Error", "Invalid bounds.")
    except Exception as e:
        messagebox.showerror("Integration Error", str(e))

def plot_function():
    fs = function_entry.get()

    if not fs:
        messagebox.showwarning("Input Error", "Please enter a function.")
        return
    
    f = parse_function(fs)
    if not f:
        return
    
    plot_window = tk.Toplevel(root)
    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.linspace(-10, 10, 200)
    
    y = f(x)
    ax.plot(x, y, label=f'f(x) = {fs}')
    ax.set_title(f'Function: {fs}')
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.grid(True)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.legend()
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Create the main window
root = tk.Tk()
root.title("Numerical Methods Application")

# Create widgets
function_label = tk.Label(root, text="Enter function f(x):")
function_entry = tk.Entry(root, width=50)

x_label = tk.Label(root, text="Enter x for differentiation:")
x_entry = tk.Entry(root, width=20)
diff_button = tk.Button(root, text="Differentiate", command=differentiate)

a_label = tk.Label(root, text="Enter lower bound a:")
a_entry = tk.Entry(root, width=20)
b_label = tk.Label(root, text="Enter upper bound b:")
b_entry = tk.Entry(root, width=20)
integrate_button = tk.Button(root, text="Integrate", command=integrate)

# Plot button
plot_button = tk.Button(root, text="Plot Function", command=plot_function)

result_label = tk.Label(root, text="Result will be shown here.")

# Layout widgets
function_label.pack()
function_entry.pack()

x_label.pack()
x_entry.pack()
diff_button.pack()

a_label.pack()
a_entry.pack()
b_label.pack()
b_entry.pack()
integrate_button.pack()

# Add plot button to layout
plot_button.pack()

result_label.pack()

# Run the application
root.mainloop()