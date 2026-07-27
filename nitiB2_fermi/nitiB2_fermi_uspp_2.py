from lib.run_fermi import run

# ###################################################################################
# Parameter des Plots
# ###################################################################################

gnufile = "nitiB2_fermi_2.dat.gnu"
fermi_energy = 16.5866
plot_fermilevel=True
x_coordinates = [0, 0.8660, 1.3660, 1.8660, 2.3660]
x_labels = ["$\\Gamma$", "R", "M", "X", "$\\Gamma$"]

if __name__ == "__main__":
    run(cfg=__import__(__name__))