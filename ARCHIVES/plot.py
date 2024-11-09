import numpy as np
import matplotlib.pyplot as plt
import math

x = np.linspace(100, math.pi, 400)
y1 = np.cos(x + 2*math.pi * 1/3 - math.pi/3)
y2 = np.cos(x + 2*math.pi * 2/3) 
y3 = np.cos(x + 2*math.pi * 3/3) 

fig, ax = plt.subplots()
ax.plot(x, y1)
ax.plot(x, y2)
ax.plot(x, y3)

plt.show()
