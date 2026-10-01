
# Tutorial for transport

* The Quantum Espresso input files are located in the `examples/B2_uspp/B2_transport` folder.
  To begin, we define the parameters in the config.py file (`Masterarbeit-NiTi-Code/src/transport/lib`).

  In my case:
```
prefix = "B2_transport"
main_directory = "/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/B2_uspp"
```

* The SCF and NSCF calculations from QE have already been performed via the terminal using the commands below.

```
mpirun -np 6 pw.x -npool 3 -in B2_transport.scf.in > B2_transport.scf.out
```
```
mpirun -np 6 pw.x -npool 3 -in B2_transport.bands.in > B2_transport.bands.out
```

* This module uses `BoltzTraP2` to interpolate Quantum Espresso data and calculate transport properties within the framework of Boltzmann transport theory.
  BoltzTraP2 interpolates onto a k-point grid with a density approximately m times that of the input. 
  If the interpolation factor m is chosen to be large, this process is highly RAM-intensive.
  The RAM is most heavily utilized during interpolation by the BoltzTrap2 function `fitde3D`. 
* To begin, we define the first parameters in the configuration file of the transport-module (`examples/B2_uspp/B2_transport`).

## Calculation

```
fermipm, erange, margin = None, None, None
calc = False
# -----------------------------------------------------------------------------------

m_values = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80] # Abbruch m=90, fitde3D
bins_values = [3000]
T_list = np.arange(10, 430, 10)
```

* The main parameter to start the interpolation is `calc`.
  With this, the interpolation is performed for each element `m` in the list `m_values` and for each element `bins` in the list `bins_values`:
* First, the band structure is interpolated if the output file from BoltzTrap2 does not yet exist. 
  The interpolation file is created by BoltzTrap2 in the QE outdir directory.
  In this example, it is created in the `tmp_B2_transport` folder. 
  * The bands are selected using the `fermipm` parameter. 
  * All bands within the interval $[-\text{fermipm}, +\text{fermipm}]$ are fully selected. No clipping of the bands occurs.
    The default setting `fermipm=None` defines a value of $(15 \cdot k_{B} \cdot \max(\text{T\_list}))$.
* Following the interpolation, the transport properties are calculated. 
  Calculating the density of states (DOS) via BoltzTrap2 requires an `erange` parameter.
  This specifies which interval around the Fermi energy is used to calculate the density of states. 
  * The default setting (`erange=None`) is defined to have the same value as fermipm. 
* The `margin` parameter clips the edges of the energy range for the density of states.
  This serves as the domain of definition for the chemical potential.
  The margin value must always be smaller than erange; otherwise, the chemical potential will be empty.
  At the same time, margin should not be 0, as calculation errors occur at the edge of the density of states. 
  * The default setting (`margin=None`) is defined as $(10 \cdot k_{B} \cdot \max(\text{T\_list}))$

## Plots

* After the calculation, calc can be set back to `False` to plot the results using `plot = True`. 
* The plot commands for the individual transport properties are already predefined.
  Individual plots can be activated or deactivated by removing or adding `#`. 
  All parameters are explained in detail in the tabular overview below.


# Parameters

Main parameters for activating the code blocks are `highlighted`.
* (list) means Python lists and NumPy arrays together

### Interpolation via BoltzTrap2

| Parameter       | Data Type      | Description    | Example                      |
| --------------- | -------------- | ---------- | -------------------------------- |
| `calc`          | (bool)         | Activates the calculations by BoltzTrap2      | False  |
| m_values        | (list)         | List of m input parameters<br>m = interpolation density of the k-point grid  | [10, 20, 30, 40, 50, 60, 70, 80] |
| T_list          | (list)         | List of temperature values                    | np.arange(10, 430, 10)       |
| bins_values     | (list)         | List with the number of bins used to determine the density of states (DOS)<br>Bins = subdivision of the DOS into equal-sized sections - the bins    | [3000]   |
| fermipm         | (float),(None) | Selects bands for interpolation near the Fermi level<br>- fermipm selects the bands within the interval $\pm$ (fermipm) around the Fermi level, but does not clip them to a specific energy range<br>None: fermipm = 15 * units.BOLTZMANN * temp.max()  | None |
| erange          | (float),(None) | Energy range for the density of states (DOS)<br>- only the interval of bands $\pm$ (erange) is used for calculating the density of states<br>None: erange = 15 * units.BOLTZMANN * temp.max() | None |
| margin          | (float),(None) | margin clips the edges of the energy range for the DOS by the value of margin<br>- serves as the domain of definition for the chemical potentials (mur)<br>- the margin value must therefore always be smaller than erange, otherwise mur will be empty<br>- margin should not be 0, as calculation errors occur at the edge<br>None: margin = 10 * units.BOLTZMANN * temp.max() | None                             |


# Plots of Transport Properties

| Parameter       | Data Type            | Description                                                                          | Example   |
| --------------- | -------------------- | ------------------------------------------------------------------------------------ | --------- |
| `plot`          | (bool)               | Activates plotting of the transport properties                                       | False     |
| bins            | (list)               | List of bins for the plots                                                           | 3000      |
| Y_name          | (str)                | Quantity for the Y-axis:<br>"cv", "seebeck", "kappa", "sigma", "hall"                | "seebeck" |
| X_name          | (str)                | Quantity for the X-axis:<br>"mu", "T", "m"                                           | "mu"      |
| xlim_values     | (float,float),(None) | Restricts the plots to a specific range on the X-axis<br>None: no restriction        | None      |
| ylim_values     | (float,float),(None) | Restricts the plots to a specific range on the Y-axis<br>None: no restriction        | None      |

## If X_name == "mu" or "T":

| Parameter        | Data Type     | Description                                                               | Example |
| ---------------- | ------------- | ------------------------------------------------------------------------- | ------- |
| plot_m_list      | (list)        | List of m-values for the plots                                            | m_value |
| plot_T_list      | (list),(None) | If X_name=mu: List of T-curves to be plotted<br>None: room temperature    | None    |
| plot_mu_list     | (list),(None) | If X_name=T: List of mu-curves to be plotted<br>None: Fermi energy        | None    |
| trace            | (bool)        | Should the trace of the tensor be plotted?<br>False: xx-direction for 2D quantities, xyz-direction for the Hall coefficient        | False   |

## If X_name == "m":

| Parameter       | Data Type, Default Value | Description                                          | Example  |
| --------------- | ------------------------ | ---------------------------------------------------- | -------- |
| plot_m_list     | (list)                   | X-axis of the plot                                   | m_values |
| plot_T          | (float),(None)           | T-curve to be plotted<br>None: room temperature      | 400      |
| plot_mu         | (float),(None)           | mu-curve to be plotted<br>None: Fermi energy         | None     |

## Heat Capacity/Temperature vs. Temperature

| Parameter        | Data Type, Default Value | Description                                                     | Example |
| ---------------- | ------------------------ | --------------------------------------------------------------- | ------- |
| cv_perT_vs_T     | (bool)                   | Special plot: Heat capacity/Temperature vs. Temperature         | False   |
| plot_m           | (int)                    | m-values of the curve                                           | 80      |


