import numpy as np
# -----------------------------------------------------------------------------------
from lib.run_thz_plot import run

# ###################################################################################
# Parameters from the calculation
# ###################################################################################
a = (0,1,0)
a = a / np.linalg.norm(a)
r = 0.2

R_list = np.arange(0.33, 0.371, 0.00125)
#R_list = [0.34625]

nks_list= [100]
phi_steps = 48
datlabel = "point1"

print(R_list)
# -----------------------------------------------------------------------------------
# Tricontour und trisurf-Plots
# "tricontour_diff" "tricontour_band0" "tricontour_band1" "tricontour_limit_diff"
# "trisurf_diff"    "trisurf_band0"    "trisurf_band1"    "trisurf_all_bands"
# -----------------------------------------------------------------------------------
contourplot = False
plottype_contourplot = "tricontour_limit_diff"
levels = 30
peaks = False
xlim_values_contourplot = None
ylim_values_contourplot = None


# -----------------------------------------------------------------------------------
# Plot of the bands along one of the paths
# -----------------------------------------------------------------------------------
plotbands = False
deg = 45
sym = True
xlim_values_plotbands = None
ylim_values_plotbands = None
#xlim_values_plotbands = (0.15, 0.19)
#ylim_values_plotbands = (-0.06, 0.06)

# -----------------------------------------------------------------------------------
# Plot as a function of the rotation angle
# -----------------------------------------------------------------------------------
plot_vs_phi = False

# -----------------------------------------------------------------------------------
# Plot as a function of R
# -----------------------------------------------------------------------------------
plot_vs_R = False
philabel = True
symmetry = 4
thz_area_R = False
# -----------------------------------------------------------------------------------
# 3D - Plot as a function of R and phi
# "diff"     "bands"     "R"
# -----------------------------------------------------------------------------------
plot_vs_phi_R = False
plottype_phi_R = "diff"
thz_area_3D = False

if __name__ == "__main__":
    run(cfg=__import__(__name__))