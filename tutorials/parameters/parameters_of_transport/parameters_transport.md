
Main parameters for activating the code blocks are `highlighted`.
* (list) means Python lists and NumPy arrays together

# Interpolation via BoltzTrap2

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `calc` | (bool) | Activates the calculations by BoltzTrap2 | False |
| m_values | (list) | List of m input parameters<br>m = interpolation density of the k-point grid | [10, 20, 30, 40, 50, 60, 70, 80] |
| T_list | (list) | List of temperature values | np.arange(10, 430, 10) |
| bins_values | (list) | List with the number of bins used to determine the density of states (DOS)<br>Bins = subdivision of the DOS into equal-sized sections - the bins | [3000] |
| fermipm | (float),(None) | Selects bands for interpolation near the Fermi level<br>- fermipm selects the bands within the interval $\pm$ (fermipm) around the Fermi level, but does not clip them to a specific energy range<br>None: fermipm = 15 * units.BOLTZMANN * temp.max() | None |
| erange | (float),(None) | Energy range for the density of states (DOS)<br>- only the interval of bands $\pm$ (erange) is used for calculating the density of states<br>None: erange = 15 * units.BOLTZMANN * temp.max() | None |
| margin | (float),(None) | margin clips the edges of the energy range for the DOS by the value of margin<br>- serves as the domain of definition for the chemical potentials (mur)<br>- the margin value must therefore always be smaller than erange, otherwise mur will be empty<br>- margin should not be 0, as calculation errors occur at the edge<br>None: margin = 10 * units.BOLTZMANN * temp.max() | None |


# Plots of Transport Properties

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot` | (bool) | Activates plotting of the transport properties | False |
| bins | (list) | List of bins for the plots | 3000 |
| Y_name | (str) | Quantity for the Y-axis:<br>"cv", "seebeck", "kappa", "sigma", "hall" | "seebeck" |
| X_name | (str) | Quantity for the X-axis:<br>"mu", "T", "m" | "mu" |
| xlim_values | (float,float),(None) | Restricts the plots to a specific range on the X-axis<br>None: no restriction | None |
| ylim_values | (float,float),(None) | Restricts the plots to a specific range on the Y-axis<br>None: no restriction | None |

## If X_name == "mu" or "T":

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| plot_m_list | (list) | List of m-values for the plots | m_value |
| plot_T_list | (list),(None) | If X_name=mu: List of T-curves to be plotted<br>None: room temperature | None |
| plot_mu_list | (list),(None) | If X_name=T: List of mu-curves to be plotted<br>None: Fermi energy | None |
| trace | (bool) | Should the trace of the tensor be plotted?<br>False: xx-direction for 2D quantities, xyz-direction for the Hall coefficient | False |

## If X_name == "m":

| Parameter | Data Type, Default Value | Description | Example |
| --- | --- | --- | --- |
| plot_m_list | (list) | X-axis of the plot | m_values |
| plot_T | (float),(None) | T-curve to be plotted<br>None: room temperature | 400 |
| plot_mu | (float),(None) | mu-curve to be plotted<br>None: Fermi energy | None |

## Heat Capacity/Temperature vs. Temperature

| Parameter | Data Type, Default Value | Description | Example |
| --- | --- | --- | --- |
| cv_perT_vs_T | (bool) | Special plot: Heat capacity/Temperature vs. Temperature | False |
| plot_m | (int) | m-values of the curve | 80 |


