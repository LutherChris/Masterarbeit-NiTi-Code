The following explains all the parameters of the submodule `plot`.
Main parameters for activating code blocks are `highlighted`.

# Values from e.g. "calc" for loading the DataFrames

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| p | (float),(list) | Grid length array or float of the grid | (0.008, 0.024, 0) |
| n | (int),(list) | Number of data points array or float of the grid | (8,25,31) |
| grid_type | (str) | Defines the shape of the grid | "path" |
| datlabel | (str) | Label in filename (for folders and files) | "punkt1_path_000_center" |
| a_coeffs | (list), None | Coefficients of the space curve | None |
| b_coeffs | (list), None | Coefficients of the space curve | None |
| modeltype_path | (str) | Path model for coordinate transformation {t,vN,vB} --> {t,rho,phi}, if `coord_system="tNB"` | "path_point3" |

# Basic Configuration

## Model and Symmetry

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| coord_system | (str) | Defines the coordinate system used for plotting<br>"kxyz": Original coordinate system<br>"xyz": Coordinate system at the center<br>"xyz_scaled": Scaled coordinate system at the center to [-1,1]<br>"path": Coordinate system along the path r(t)<br>"tNB": Coordinate system of shifted paths r(t) | "xyz" |
| modeltype | (str) | Defines the model type (for file folder) | "model_path_abs_4" |
| symmetry | (int),(None) | Symmetry of the data from the model fit | 1 |
| no_a0 | (bool) | Was the first coefficient omitted in the model fit? | False |

## Orders

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| p_order | (int) | p-order of the model | 2 |
| f_order | (int) | f-order of the model | 17 |
| l_order | (int) | l-order of the model | 20 |
| k_order | (int) | k-order of the model | 3 |
| p1_order | (int) | p1-order of the model | 0 |
| p2_order | (int) | p2-order of the model | 0 |
| p3_order | (int) | p3-order of the model | 0 |

# Trimming of the Energy DataFrame

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `thz_cut_diff` | (bool) | Filters band difference according to criterion < cut_value_diff | True |
| `thz_cut_band0` | (bool) | Filters lower band according to criterion > - cut_value_bands | True |
| `thz_cut_band1` | (bool) | Filters upper band according to criterion < cut_value_bands | True |
| cut_value_diff | (float) | For the band difference in eV | 0.009 |
| cut_value_bands | (float) | For the bands in eV | 0.05 |

# Plot Configuration

## Energy Axis for All Plots

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| plot_energy_axis | (str) | Energy axis for all plots | "diff" |
| plot_titel | (str) | Title of the 4D plot | "" |

# 2D Slider Plots

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_2Dplots` | (bool) | Activates plot of 2D slider plots | False |
| plot_model | (bool) | Should model data points be plotted? | True |
| axis_2D | (str) | x-axis in 2D slider plot | "phi" |
| nk_model | (int) | Number of model points in 2D slider plot | 1000 |
| error | (bool) | Target axis in 2D slider plot are errors | False |

# 3D Slider Plots

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_3Dplot` | (bool) | Activates plot of 3D surface plots | False |
| axis_3D | (str) | Axis of the slider (perpendicular to plotted plane) | "x" |

# 4D Plots

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_4Dplots` | (bool) | Activates 4D plots | False |
| black_plot | (bool) | Colorbar becomes completely black | False |
| plot_cube | (bool) | Plots the cube edges as lines | False |

# 4D Plots_mme_in_thz

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_4Dplots_mme_in_thz` | (bool) | Activates 4D plots of momentum matrix elements | False |
| merge_decimals | (int),(None) | Activates coordinate system mapping | 5 |

# Plot of Gradients and Curvature

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_gradient` | (bool) | Activates plot of gradients | False |
| plot_curv | (bool) | Activates plot of curvature vectors | False |
| step | (int) | Density of gradient and curvature vectors | 5 |

# 2D Error Plots

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_errors_2D` | (bool) | Activates error plot for different model orders | False |
| axis1 | (str) | Order axis in plot; Example: "p_order" | "len_diff" |
| max_error_2D | (float),(None) | Pre-filters DataFrame according to error_energy < max_error | None |
| thz_range | (bool) | Plot errors in THz-active region | True |

# 3D Wireframe Error Plots

| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| `plot_errors_3D` | (bool) | Activates 3D wireframe error plot for model orders | False |
| axis1_3D | (str) | First order axis in plot; Example: "p_order" | "p_order" |
| axis2_3D | (str) | Second order axis in plot; Example: "l_order" | "k_order" |
| max_error_3D | (float),(None) | Pre-filters DataFrame according to error_energy < max_error | None |
| thz_range_3D | (bool) | Plot errors in THz-active region | True |