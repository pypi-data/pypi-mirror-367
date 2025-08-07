import Clothoids
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------
# Example: create and evaluate a clothoid curve
# ------------------------------------------------

curve = Clothoids.ClothoidCurve("curve")
x_ini     = 0.0  # Initial x-coordinate (m)
y_ini     = 0.0  # Initial y-coordinate (m)
theta_ini = 0.0  # Initial absolute orientation (rad)
x_fin     = 4.0  # Final x-coordinate (m)
y_fin     = 4.0  # Final y-coordinate (m)
theta_fin = 0.0  # Final absolute orientation (rad)
curve.build_G1(x_ini, y_ini, theta_ini, x_fin, y_fin, theta_fin)

s_values = np.arange(0, curve.length(), 0.01, dtype=np.float64)
points = np.zeros((s_values.size, 2))
curvatures = np.zeros(s_values.size, dtype=np.float64)

for i in range(s_values.size):
    points[i, :] = curve.eval(s_values[i])
    curvatures[i] = curve.kappa(s_values[i])

# plot the x,y points of the clothoid curve
plt.figure(figsize=(8, 6))
plt.title("Clothoid Curve Evaluation")
plt.plot(points[:, 0], points[:, 1])
plt.xlabel("x (m)")
plt.ylabel("y (m)")
plt.grid()
plt.axis('equal')
plt.show()

# plot the curvature values
plt.figure(figsize=(8, 6))
plt.title("Clothoid Curvature Evaluation")
plt.plot(s_values, curvatures, 'bo', markersize=2)
plt.xlabel("s (m)")
plt.ylabel("Curvature (1/m)")
plt.grid()
plt.show()

# ------------------------------------------------
# Example: create and evaluate a clothoid list
# ------------------------------------------------

curve_list = Clothoids.ClothoidList("curve_list")
interp_point_x = np.array([0.0, 1.0, 1.0, 0.0], dtype=np.float64)
interp_point_y = np.array([0.0, 0.0, 1.0, 1.0], dtype=np.float64)
curve_list.build_G1(interp_point_x, interp_point_y)

s_values = np.arange(0, curve_list.length(), 0.01, dtype=np.float64)
points = np.zeros((s_values.size, 2))

for i in range(s_values.size):
    points[i, :] = curve_list.eval(s_values[i])

# plot the x,y points of the clothoid list
plt.figure(figsize=(8, 6))
plt.title("Clothoid List Evaluation")
plt.xlabel("x (m)")
plt.ylabel("y (m)")
plt.grid()
plt.axis('equal')
plt.plot(points[:, 0], points[:, 1])
plt.show()
