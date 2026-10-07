The following explains all the parameters of the module:
Main parameters for activating the code blocks are `highlighted`.
* (list) means Python lists and NumPy arrays together

# general parameters

| Parameter | Data Type | Description | Example  |
| ---| --- | --- | --- |
| diff_value | (float) | Parameter of the convergence criterion in meV | 2 |

# Convergence with respect to "ecutwfc"

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `ecutwfc` | (bool) | Activates convergence with respect to "ecutwfc" | True |
| cutoff_list | (list) | List of different ecutwfc values | np.arange(20,51,1) |

# Convergence with respect to "nk" in "K_POINTS automatic nk nk nk 1 1 1"

| Parameter | Data Type | Description | Example |
| --- | ----| --- | --- |
| `k_points` | (bool) | Activates convergence with respect to "K_POINTS automatic" | True |
| nk_list_K_POINTS | (list) | List of different nk values | np.arange(2, 23, 1) |

# Convergence with respect to "celldm(1)"

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `celldm` | (bool) | Activates convergence with respect to "celldm" | True |
| celldm_list | (list) | List of different celldm values | np.arange(5.5626, 5.6627, 0.01) |

# Convergence with respect to smearing

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `smearing` | (bool)    | Activates convergence with respect to smearing | True |
| key_smearing | (str) | Smearing type available: "gauss", "marzari-vanderbilt", "methfessel-paxton" | "gauss" |
| degauss_list | (list) | List of different degauss values | np.arange(0.01, 0.105, 0.01) |
| nk_list_smearing | (list) | List of different nk values | [18, 19, 20] |

# Plots

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot` | (bool) | Activates plots | True |
| key_plot | (str) | Which convergence curve should be plotted? available: "celldm", "ecutwfc", "k_points", "smearing" | "smearing" |
| nk_list_smearing_plot | (list) | If key_plot="smearing", which nk values should be plotted? | nk_list_smearing |