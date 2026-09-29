
# Tutorial for conv

* This tutorial uses a NiTi calculation as an example.
  The Quantum Espresso input files are located in the `examples/nitiB2_uspp/nitiB2_conv` folder.
  To begin, we define the variables in the config.py file (`Masterarbeit-NiTi-Code/src/conv/lib`).
  In my case:
```
prefix = "nitiB2_conv"
main_directory = f"/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/nitiB2_uspp"
num_cores = 6
num_pool = 3
```

* This module is used to perform the convergence of the self-consistency calculation.
  The total energy is calculated based on the following QE parameters:
  * the namelist parameter ecutwfc
  * the card parameter nk in K_POINTS automatic: (nk nk nk 1 1 1)
  * the namelist parameter celldm(1)
  * the namelist parameter degauss for various smearing methods and nk

* Please open the Python file `Masterarbeit-NiTi-Code/src/conv/example_conv.py`.

* The blocks are activated via main variables with the same names.
  The variation of the QE parameters is defined via lists.

> Example\
> The main variable `ecutwfc=True` activates the convergence calculation with respect to ecutwfc.\
> The variable `cutoff_list=` defines the variation of the parameter.\
>`cutoff_list = np.arange(20,51,1)` varies the parameter between 20 and 50 in increments of 1.

* When the program is executed, the QE input file is modified for each list entry.
  The QE calculation is then performed, and the total converged energy is extracted from the output file.
  The energies, along with the list entries, are saved as a CSV file in the subfolder `conv_results` inside the `<prefix>=nitiB2_conv`-Folder.

* Convergence with respect to other parameters occurs analogously. 
  Only with smearing must the respective smearing type be manually defined beforehand in the QE input file. 
  The Python program will warn if this has been forgotten.

* After the calculation, the respective convergence curve can be plotted using the main variable `plot=True`.
  The variable `key_plot` defines the x-axis of the plot.

* The plot tests a defined convergence criterion.
* For an accuracy of 2 meV/cell, `diff_value=2` the following conditions are fulfilled:
  * $\text{max}( |E_{n-2} - E_{n-1}| , |E_{n} - E_{n-1}| ) < 2 \text{meV}$
  * $\text{max}( |E_{n-1} - E_{n}| , |E_{n+1} - E_{n}| ) < 2 \text{meV}$
  * $\text{max}( |E_{n} - E_{n+1}| , |E_{n+2} - E_{n}| ) < 2 \text{meV}$

## Parameters of conv

The following explains all the parameters of the module:
Main parameters for activating the code blocks are `highlighted`.
* (list) means Python lists and NumPy arrays together

### general parameters

| Parameter      | Data Type | Description                                   | Example  |
| -------------- | --------- | --------------------------------------------- | -------- |
| diff_value     | (float)   | Parameter of the convergence criterion in meV | 2        |

### Convergence with respect to "ecutwfc"

| Parameter       | Data Type | Description                                     | Example            |
| --------------- | --------- | ----------------------------------------------- | ------------------ |
| `ecutwfc`       | (bool)    | Activates convergence with respect to "ecutwfc" | True               |
| cutoff_list     | (list)    | List of different ecutwfc values                | np.arange(20,51,1) |

### Convergence with respect to "nk" in "K_POINTS automatic nk nk nk 1 1 1"

| Parameter            | Data Type | Description                                                | Example             |
| -------------------- | --------- | ---------------------------------------------------------- | ------------------- |
| `k_points`           | (bool)    | Activates convergence with respect to "K_POINTS automatic" | True                |
| nk_list_K_POINTS     | (list)    | List of different nk values                                | np.arange(2, 23, 1) |

### Convergence with respect to "celldm(1)"

| Parameter       | Data Type | Description                                    | Example                         |
| --------------- | --------- | ---------------------------------------------- | ------------------------------- |
| `celldm`        | (bool)    | Activates convergence with respect to "celldm" | True                            |
| celldm_list     | (list)    | List of different celldm values                | np.arange(5.5626, 5.6627, 0.01) |

### Convergence with respect to smearing

| Parameter            | Data Type | Description                                                                 | Example                      |
| -------------------- | --------- | --------------------------------------------------------------------------- | ---------------------------- |
| `smearing`           | (bool)    | Activates convergence with respect to smearing                              | True                         |
| key_smearing         | (str)     | Smearing type available: "gauss", "marzari-vanderbilt", "methfessel-paxton" | "gauss"                      |
| degauss_list         | (list)    | List of different degauss values                                            | np.arange(0.01, 0.105, 0.01) |
| nk_list_smearing     | (list)    | List of different nk values                                                 | [18, 19, 20]                 |

# Plots

| Parameter                 | Data Type | Description       | Example          |
| ------------------------- | --------- | ----------------- | ---------------- |
| `plot`                    | (bool)    | Activates plots   | True            |
| key_plot    | (str)     | Which convergence curve should be plotted? available: "celldm", "ecutwfc", "k_points", "smearing"  | "smearing"       |
| nk_list_smearing_plot | (list)    | If key_plot="smearing", which nk values should be plotted?      | nk_list_smearing |
