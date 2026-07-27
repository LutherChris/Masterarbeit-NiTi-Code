import numpy as np
import matplotlib.pylab as plt
from BoltzTraP2 import units


plt.figure()
xdata = np.linspace(-0.1, 0.1, 1000)
def ydata(x):
    return x / (15*units.BOLTZMANN)

plt.plot(xdata, ydata(xdata))
plt.xlabel(r"Energie [Ha] $15K_BT_{max}$", fontsize="12")
plt.ylabel(r"$T_{max}$ [K]", fontsize="12")
plt.grid()
plt.tight_layout()
plt.show()
