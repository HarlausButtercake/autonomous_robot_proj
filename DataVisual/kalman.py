import numpy as np
import matplotlib.pyplot as plt

# Define the system parameters
dt = 1.0  # time step
A = np.array([[1, dt], [0, 1]])  # state transition matrix
H = np.array([[1, 0]])  # measurement matrix
Q = np.array([[0.1, 0], [0, 0.1]])  # process noise covariance
R = np.array([[1]])  # measurement noise covariance

# Initial state
x_init = np.array([[0], [0]])  # initial state (position = 0, velocity = 0)

# Generate some noisy measurements
num_steps = 100
true_positions = np.linspace(0, 10, num_steps)
measurements = true_positions + np.random.normal(0, 0.5, num_steps)

# Create arrays to store the estimated states
filtered_positions = np.zeros(num_steps)
filtered_velocities = np.zeros(num_steps)

# Initialize the Kalman filter
x = x_init
P = np.eye(2)  # initial state covariance

# Kalman filter loop
for i in range(num_steps):
    # Predict
    x_pred = np.dot(A, x)
    P_pred = np.dot(np.dot(A, P), A.T) + Q

    # Update
    y = measurements[i] - np.dot(H, x_pred)
    S = np.dot(np.dot(H, P_pred), H.T) + R
    K = np.dot(np.dot(P_pred, H.T), np.linalg.inv(S))
    x = x_pred + np.dot(K, y)
    P = P_pred - np.dot(np.dot(K, H), P_pred)

    # Save the filtered state
    filtered_positions[i] = x[0]
    filtered_velocities[i] = x[1]

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(true_positions, label='True Position')
plt.plot(measurements, label='Noisy Measurement', alpha=0.5)
plt.plot(filtered_positions, label='Filtered Position', linestyle='--')
plt.xlabel('Time')
plt.ylabel('Position')
plt.title('Kalman Filter Example')
plt.legend()
plt.grid(True)
plt.show()