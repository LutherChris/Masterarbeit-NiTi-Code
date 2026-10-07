The following explains all the parameters of the submodule `path`.
Main parameters for activating code blocks are `highlighted`.

# Fixed Initial Parameters

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| point | (str) | Point in the BZ, e.g., "punkt1"<br>- determines which functions are loaded for filtering and fitting | "punkt1" |
| bandnumbers | (list) | Selection of bands for reading the QE XML file | (14, 15) |
| modeltype | (str) | Folder of the first DataFrame for the iteration | "out-Dateien" |
| model_energy | (str) | Energy axis by which the DataFrame is filtered | "diff" |
| k0=zero | (list) | =zero, offset vector for the grid at the coordinate origin | (0.343927, 0.11924648, 0.11924648) |
| p | (float),(list) | Grid length array or float of the first DataFrame | 0.015 |
| n | (int),(list) | Number-of-data-points array or float of the first DataFrame | 11 |
| datlabel | (str) | datlabel of the first DataFrame | "punkt1_000" |
| coord_system | (str) | Coordinate system in which the fit is performed | "xyz" |
| model_axis | (str) | Axis along which the path is parameterized<br>- Point 1: "x"<br>- Point 2: "t" | "x" |

# Iteration Parameters

## Calculation of the First Path

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| x_order_0 | (int) | Order in x-direction of the path model; Example Point 1: 0 | None |
| y_order_0 | (int) | Order in y-direction of the path model; Example Point 1: 4 | 4 |
| z_order_0 | (int) | Order in z-direction of the path model; Example Point 1: 4 | 4 |
| no_a0_0 | (bool) | Should the 0th order be omitted in the polynomial models? | True |
| filter_intersection_0 | (bool) | Should the region near the (111)-direction at Point 2 be removed? | False |
| filter_tol_0 | (float) | Numerical tolerance for comparison in (111)-direction | 1e-6 |
| cut_energy_0 | (float) | Filters energies to be smaller than cut_energy | 1e-3 |
| plot_nk_model_0 | (int) | Number of data points for plotting the path | 1000 |
| plot_path_0 | (bool) | Should the calculated path be plotted? | False |
| calc_path_0 | (bool) | Activates the calculation of the path via fitting | False |

## Calculation of the New Grid

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| delta | (float) | Defines grid boundaries of the new grid along the path<br>Example Point 1: grid boundaries in y and z directions (symmetric)<br> | 0.00005 |
| n_grid | (list) | Number of data points in (x,y,z) direction | (50, 10, 10) |
| path_step | (int) | Iteration step number; new datlabel names are generated via path_step | 2 |
| alpha | (float) | Transparency of grid points from the DataFrame in the plot | 0.05 |
| plot_grid | (bool) | Should the new grid be plotted? | False |
| path_grid | (bool) | Activates definition of the new grid | False |
| calc_dft | (bool) | Activates calculation of the new grid via QE and saves new DF | False |
| load_new_csv | (bool) | load_new_csv: (bool) | False |

## Calculation of the New Path

- Parameters analogous to the first path, but with _1 instead of _0

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| x_order_1 | (int) | Order in x-direction of the path model; Example Point 1: 0 | None |
| y_order_1 | (int) | Order in y-direction of the path model; Example Point 1: 4 | 4 |
| z_order_1 | (int) | Order in z-direction of the path model; Example Point 1: 4 | 4 |
| no_a0_1 | (bool) | Should the 0th order be omitted in the polynomial models? | True |
| filter_intersection_1 | (bool) | Should the region near the (111)-direction at Point 2 be removed? | False |
| filter_tol_1 | (float) | Numerical tolerance for comparison in (111)-direction | 1e-6 |
| cut_energy_1 | (float) | Filters energies to be smaller than cut_energy | 1e-3 |
| plot_nk_model_1 | (int) | Number of data points for plotting the path | 1000 |
| plot_path_1 | (bool) | Should the calculated path be plotted? | False |
| calc_path_1 | (bool) | Activates the calculation of the path via fitting | False |

# Additional Plots

- The plots always use the last active DataFrame

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| plot_titel | (str) | Title for the plots | "Differenz der Bänder" |

## 4D Plots

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_data` | (bool) | Activates the plot | False |
| black_plot | (bool) | All points are colored black | False |
| plot_cut_value | (float) | Filters the DataFrame: energy axis < plot_cut_value | 0.005 |
| plot_thz_cut_diff | (bool) | Activates filtering of the DataFrame by plot_cut_value | False |
| energy_4D | (str) | Sets the energy axis of the plot (also filtered by this) | "diff" |

## Plotting Both Paths Simultaneously

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_path_both` | (bool) | Plots old and new path simultaneously | False |

## Energy in THz-Active Region

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| cut_value_diff | (float) | Energy in eV to which the band difference is trimmed | 0.01241 |
| cut_value_bands | (float) | Energy in eV to which the bands are trimmed | 0.05 |
| `final_analysis_point2` | (bool) | Activates analysis at Point 2 | False |
| plot_analysis_point2 | (bool) | Plot of intervals along the path | False |
| `calc_point_2A_2B` | (bool) | Activates calculation of intersection points of 2A and 2B | False |
| plot_2A_2B | (bool) | Plot of 3D space curves 2A and 2B | False |
| `final_analysis_point1` | (bool) | Activates analysis at Point 1 | False |
| plot_analysis_point1 | (bool) | Plot of intervals along the path | False |