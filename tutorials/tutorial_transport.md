
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
    The default setting `fermipm=None` defines a value of $15 \cdot k_{B} \cdot$ max(T_list).
* Following the interpolation, the transport properties are calculated. 
  Calculating the density of states (DOS) via BoltzTrap2 requires an `erange` parameter.
  This specifies which interval around the Fermi energy is used to calculate the density of states. 
  * The default setting (`erange=None`) is defined to have the same value as fermipm. 
* The `margin` parameter clips the edges of the energy range for the density of states.
  This serves as the domain of definition for the chemical potential.
  The margin value must always be smaller than erange; otherwise, the chemical potential will be empty.
  At the same time, margin should not be 0, as calculation errors occur at the edge of the density of states. 
  * The default setting (`margin=None`) is defined as $10 \cdot k_{B} \cdot$ max(T_list).

## Plots

* After the calculation, calc can be set back to `False` to plot the results using `plot = True`. 
* The plot commands for the individual transport properties are already predefined.
  Individual plots can be activated or deactivated by removing or adding `#`. 
  All parameters are explained in detail in the tabular overview `parameters/parameters_of_transport/parameters_transport.md`.


