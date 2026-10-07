The following explains all the parameters of the module. `(list)` means Python lists or NumPy arrays.

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| gnufile | (str) | Filename of the gnuplot file from QE | "B2_fermi.dat.gnu" |
| fermi_energy | (float) | Fermi energy from QE | 16.8868 |
| plot_fermilevel | (bool) | Should the Fermi level be plotted? | True |
| x_coordinates | (list) | Path coordinates of the high-symmetry-points | [0, 0.5000, 1.0000, 1.7071, 2.5731] |
| x_labels | (list)  | Path coordinate labels | ["\$\\Gamma\$", "X", "M", "\$\\Gamma\$", "R"] |
| y_lim | (list)  | Y-axis is only plotted within the range of y_lim[0] and y_lim[1] (in eV) | [-2.0, 2.0] |