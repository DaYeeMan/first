import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)
torch.manual_seed(42)

# Generate Data
n_lf = 100
n_hf = 20
X_lf = np.linspace(0, 1, n_lf).reshape(-1, 1)
X_hf = np.linspace(0, 1, n_hf).reshape(-1, 1)

def f_hf(x): return np.sin(8 * np.pi * x) + x
def f_lf(x): return 0.5 * np.sin(8 * np.pi * x) + x**2

Y_lf = f_lf(X_lf)
Y_hf = f_hf(X_hf)
delta = Y_hf - f_lf(X_hf)  # True residual for training the teacher

# Convert to PyTorch tensors
X_lf_torch = torch.tensor(X_lf, dtype=torch.float32)
X_hf_torch = torch.tensor(X_hf, dtype=torch.float32)
Y_lf_torch = torch.tensor(Y_lf, dtype=torch.float32)
Y_hf_torch = torch.tensor(Y_hf, dtype=torch.float32)
delta_torch = torch.tensor(delta, dtype=torch.float32)

# Define simple MLP model
def make_mlp():
    return nn.Sequential(
        nn.Linear(1, 50),
        nn.Tanh(),
        nn.Linear(50, 50),
        nn.Tanh(),
        nn.Linear(50, 1)
    )

teacher = make_mlp()
student = make_mlp()

# --- 1. Train Teacher on delta ---
optimizer_teacher = optim.Adam(teacher.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

# --- Baseline: Train a model only on HF data ---
baseline = make_mlp()
optimizer_baseline = optim.Adam(baseline.parameters(), lr=1e-3)

for epoch in range(2000):
    optimizer_baseline.zero_grad()
    out = baseline(X_hf_torch)
    loss = loss_fn(out, Y_hf_torch)
    loss.backward()
    optimizer_baseline.step()

for epoch in range(2000):
    optimizer_teacher.zero_grad()
    out = teacher(X_hf_torch)
    loss = loss_fn(out, delta_torch)
    loss.backward()
    optimizer_teacher.step()

# --- 2. Train Student on LF data, supervised by (LF + teacher prediction) ---
with torch.no_grad():
    teacher_pred_on_lf = teacher(X_lf_torch)  # weak label
    weak_labels = Y_lf_torch + teacher_pred_on_lf

optimizer_student = optim.Adam(student.parameters(), lr=1e-3)

for epoch in range(3000):
    optimizer_student.zero_grad()
    student_pred = student(X_lf_torch)
    loss = loss_fn(student_pred, weak_labels)
    loss.backward()
    optimizer_student.step()

# --- Evaluation ---
X_test = np.linspace(0, 1, 200).reshape(-1, 1)
X_test_torch = torch.tensor(X_test, dtype=torch.float32)

with torch.no_grad():
    y_hf_true = f_hf(X_test)
    y_lf_pred = f_lf(X_test)
    y_teacher_res = teacher(X_test_torch).numpy()
    y_student_pred = student(X_test_torch).numpy()
    y_bfwl_pred = f_lf(X_test) + y_teacher_res
    y_baseline_pred = baseline(X_test_torch).numpy()

# --- Plot ---
plt.figure(figsize=(10, 6))
plt.plot(X_test, y_hf_true, label='HF Ground Truth', linewidth=2)
plt.plot(X_test, y_lf_pred, label='LF Function', linestyle='--')
plt.plot(X_test, y_student_pred, label='BFWL Student Output', linestyle='-')
plt.plot(X_test, y_bfwl_pred, label='LF + Teacher Residual', linestyle=':')
plt.plot(X_test, y_baseline_pred, label='HF Only Model', linestyle='-.', color='magenta')
plt.scatter(X_hf, Y_hf, label='HF Training Points', color='black', zorder=10)
plt.legend()
plt.title("BFWL vs HF-Only Model on Toy Function")
plt.xlabel("x")
plt.ylabel("f(x)")
plt.grid(True)
plt.show()
