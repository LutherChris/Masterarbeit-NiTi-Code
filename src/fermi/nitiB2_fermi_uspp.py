from lib.run_fermi import run

# ###################################################################################
# Parameter des Plots
# ###################################################################################

gnufile = "nitiB2_fermi.dat.gnu"
fermi_energy = 16.5866
plot_fermilevel = True
x_coordinates = [0, 0.5000, 1.0000, 1.7071, 2.5731]
x_labels = ["$\\Gamma$", "X", "M", "$\\Gamma$", "R"]

if __name__ == "__main__":
    run(cfg=__import__(__name__))