
The following explains all the parameters of the submodule `calc`.
Main parameters for activating code blocks are `highlighted`.

# Fundamental coordinate systems in the code:

| Variable | Coordinates | Description |
| --- | --- | --- |
| k_grid_center | $\{x,y,z\}$ | Grid centered at origin, regardless of grid type |
| k_grid | $\{k_x,k_y,k_z\}$ | Grid for Quantum Espresso |
| k_grid_rot | $\{k_x',k_y',k_z'\}$ | Rotated grid for Quantum Espresso |
| t_grid | $\{t,\rho,\phi\}$ | Grid for polar coordinates along the path |
| v_grid | $\{t,v_N,v_B\}$ | Grid with shifted paths in $N$ and $B$ direction<br>$v_N = \text{component of the normal vector}$<br>$v_B = \text{component of the binormal vector}$ |

# Fixed parameters

## From THz study

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| u | (list) | Unit vector of the central line through origin around which rotation occurs | (1, 0, 0); u / np.linalg.norm(u) |
| a | (list) | Unit vector for initial path orthogonal to u | (0, 1, 0); a / np.linalg.norm(a) |
| v | (list) | Shift vector for initial path | (0, 0, 0) |
| R | (float) | Radius for unit vector u | 0.343927 |
| r | (float) | Radius for unit vector a | 0.2 |
| phi_steps | (int) | Number of intermediate paths between $0^\circ$ and $180^\circ$ | 20 |
| bandnumbers | (list) | Selection of bands for reading the QE XML file | (14, 15) |

## From path determination

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| coord_basis | (str) | Coordinate system used during path determination<br>"xyz" or "xyz_scaled" | "xyz" |
| a_coeffs | (list) | $a$-coefficients of $r(t)$ | [-0.7410615827179478, 1.840838706272784, -11.842134854139516, 7.412966199122343] |
| b_coeffs | (list) | $b$-coefficients of $r(t)$ | [-0.7415216975597553, 1.7940027615351415, -8.71052528076767, 287.3393435525252] |
| modeltype_path | (str) | Path model<br>"path_point1": Path for Point 1<br>"path_point2A": Path for Point 2A<br>"path_point2B": Path for Point 2B<br>"path_point3": Path for Point 3<br>"path_point1_center": Path for Point 1 along the shell center | "path_point1" |
| decimals | (float) | Specifies how many decimal places QE vectors are rounded to (default: 12) | 12 |

# Main parameters for block activation

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `plot_grid` | (bool) | 2. Plotting the grid<br>- Should the grid be plotted? | False |
| `calc_dft` | (bool) | 3. Band energy calculation via Quantum Espresso<br>- Activates energy DFT calculation via Quantum Espresso (QE) | False |
| `calc_mme` | (bool) | 4. Momentum matrix element calculation via QE<br>- Activates MME DFT calculation via QE | False |
| `analysis` | (bool) | 5. DataFrame calculation, analysis, and adjustment<br>- Activates analysis block after DFT calculation | False |
| `load_csv` | (bool) | 6. Loading pandas DataFrames<br>- Activates loading CSV files after analysis | False |
| `calc_model` | (bool) | 7. Modeling with loop over all orders | False |

# Parameters for 1. Grid Calculation

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| k0 | (list) | Offset vector for the grid at origin (zero or zero_0) | zero = (0.343927, 0.11924648, 0.11924648); zero |
| p | (float),(list) | Grid length array or float for the grid | (0.008, 0.024, 0) |
| n | (int),(list) | Number of data points array or float for the grid | (8, 25, 31) |
| grid_type | (str) | Defines grid geometry; Examples:<br>"regular" = Cartesian grid<br>"cylindrical" = Cylindrical grid<br>"path" = Polar grid along path<br>"path_grid_semi_regular" = Regular grid formed by path shift<br>"path_grid_2B" = Grid for Point 2A and Point 2B | "path" |
| datlabel | (str) | Label in file name (for folders and files) | "punkt1_path_000_center" |

Meaning of parameter p for different grid types:

| Grid type grid_type | Meaning of p | Format |
| --- | --- | --- |
| "regular" | Half edge length of grid in $x$, $y$, and $z$ direction | $[x_{\text{max}}, y_{\text{max}}, z_{\text{max}}]$ |
| "cylindrical" | Edge lengths along radius and half edge length along cylinder axis | $[r_{\text{max}}, 0, z_{\text{max}}]$ |
| "path" | Half edge length in $t$-direction and radius in polar plane | $[t_{\text{max}}, \rho_{\text{max}}, 0]$ |
| "path_grid_semi_regular" | Half edge length in $t$-direction, half edge length in $V_N$ direction, and half edge length in $V_B$ direction | $[t_{\text{max}}, V_{N_{\text{max}}}, V_{B_{\text{max}}}]$ |
| "path_grid_2B" | Half edge length in $t$-direction and radius in polar plane | $[t_{\text{max}}, \rho_{\text{max}}, 0]$ |

Meaning of parameter n for different grid types:

| Grid type grid_type | Meaning of n | Format |
| --- | --- | --- |
| "regular" | Number of data points along half edge length | $[N_x, N_y, N_z]$ |
| "cylindrical" | Number of data points along radius, number of angles, and number of data points along half edge length in cylinder axis direction | $[N_r, N_\phi, N_z]$ |
| "path" | Number of data points along half edge length of $t$-axis, along radius, and number of angles | $[N_t, N_\rho, N_\phi]$ |
| "path_grid_semi_regular" | Number of data points along half edge lengths in $t$, $V_N$, and $V_B$ directions | $[N_t, N_{V_N}, N_{V_B}]$ |
| "path_grid_2B" | Number of data points along half edge length of $t$-axis, along radius, and number of angles | $[N_t, N_\rho, N_\phi]$ |

## Grid rotation

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `rotation` | (bool) | Activates grid rotation $\{x,y,z\} \to \{k_x',k_y',k_z'\}$ | False |
| u_axis | (list) | Original principal axis of k-grid when rotation=True, e.g., (0,0,1) | |
| a_axis | (list) | Target axis of new grid when rotation=True, e.g., (0,1,1) | |

## Specifically for grid_type="cylindrical":

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| z_axis | (list) | Principal axis of cylinder | None |
| phi_sym | (int) | Number of symmetry sectors | 1 |
| R_dense | (float) | Radius of radial Gaussian density | None |
| r_sigma | (float) | Width/strength of radial Gaussian density | None |
| n_phi_min | (int) | Minimum number of $\phi$ points per symmetry sector | 2 |
| base_weight | (float) | Base value for density outside Gaussian | 0.25 |

## Specifically for grid_type="path":

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| path_phi_sym | (int) | Number of symmetry sectors, no symmetry: $\{0,1\}$ | 1 |
| path_n_phi_min | (int) | Minimum number of $\phi$ points per symmetry sector | None |
| non_equidistant | (float) | Shifted angles by non_equidistant * np.sin(np.arange(n_phi)) | None |
| path_rho_dense | (float) | Radius of radial Gaussian density | None |
| path_rho_sigma | (float) | Width/strength of radial Gaussian density | None |
| path_base_weight | (float) | Base value for density outside Gaussian | 0.25 |
| path_no_rho0 | (bool) | Points with $\rho=0$ are not defined | False |

## Specifically for grid_type="path_grid_2B":

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| path_phi_sym | (int) | Number of symmetry sectors, no symmetry: $\{0,1\}$ | 1 |
| path_phi_sigma | (float) | $\phi$-dependent Gaussian compression around Point 2B as a function of $t$ | None |
| path_rho_sigma | (float) | Width/strength of radial Gaussian density around $\rho=0$ (Point 2A) | None |
| path_rho_sigmaB | (float) | Width/strength of radial Gaussian density around $\rho=0$ (Point 2A) as a function of $t$ | None |
| path_no_rho0 | (bool) | Points with $\rho=0$ are not defined | False |

# Basic parameters for 5. and 7.

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| energy | (str) | Energy at which calculations are performed<br>"diff": Energy difference<br>"band0": Lower band<br>"band1": Upper band | "diff" |
| coord_system | (str) | Selects specific coordinate axes from DataFrame for calculations in Analysis and Modeling blocks<br>"kxyz": Original coordinate system - Axes: ("kx", "ky", "kz")<br>"xyz": Center coordinate system - Axes: ("x", "y", "z")<br>"xyz_scaled": Scaled center coordinate system on $[-1,1]$ - Axes: ("x_scaled", "y_scaled", "z_scaled")<br>"path": Coordinate systems along path $r(t)$ - Axes: ("t", "rho", "phi")<br>"tNB": Coordinate system of shifted paths $r(t)$ | "path" |

~={orange}Note:=~ If coord_system="path" but grid_type is not a path coordinate system, the axes ("t", "rho", "phi") are calculated numerically via coordinate transformation using the following parameters:

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| bounds | (list) | Interval of $t$ for minimum search | (-2, 2) |
| tol | (float) | Tolerance for non-orthogonality | 1e-7 |
| xatol | (float) | Tolerance in minimum search function | 1e-8 |

# Parameters for 5. DataFrame Calculation, Analysis, and Adjustment

## Principal Component Analysis

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `pca` | (bool) | Activates Principal Component Analysis in analysis block | False |

## Removal of zero values from data

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `no_000` | (bool) | Activates removal of zero values from data<br>if coord_system="xyz": removes $x=y=z=0$ from data before modeling<br>if coord_system="path": removes $\rho=0$ from data before modeling | False |

## Filtering DataFrame to THz-active region

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `cut_df_for_fit` | (bool) | Activates filtering of DataFrame to THz-active region | False |
| cut_value_diff | (float) | THz condition for band difference | 0.009 |
| cut_value_bands | (float) | THz condition for bands | 0.05 |
| complete_cut | (bool) | Bands are cropped exactly to THz conditions! | True |

## Calculation of intersection point $k_0$

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `find_intersection` | (bool) | Should intersection $k_0$ be calculated in DataFrame? | False |
| intersect_point | (str) | Which intersection point is concerned? | "point_1" |

## Calculation of statistical values for momentum matrix elements

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `mme_statistics` | (bool) | Activates calculation of statistical values for momentum matrix elements | False |
| merge_decimals | (int) | Number of decimal places used to compare DataFrames | 10 |
| df_key | (str) | quantity on which he statistical calculation is performed | "px_abs2_14-15" |

# Parameters for 7. Model Calculation

## Omit 0-th polynomial orders?

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| no_a0 | (bool) | Should 0-th order be omitted in polynomial models? | False |

## Maximum number of coefficients

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| max_coeffs | (int) | Maximum number of coefficients before aborting model calculations | 10000 |

## Configuration

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| modeltype | (str) | Specifies model type | "model_path_abs_4" |
| symmetry | (int),(None) | Symmetry factor in model functions | 1 |

## Orders to be calculated

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| p_order_list | (list) | $p$-orders for model calculation loop | [2, 3] |
| f_order_list | (list) | $f$-orders for model calculation loop | [17, 18] |
| l_order_list | (list) | $l$-orders for model calculation loop | [20, 21] |
| k_order_list | (list) | $k$-orders for model calculation loop | [3, 4] |
| p1_order_list | (list) | $p_1$-orders for model calculation loop | [0] |
| p2_order_list | (list) | $p_2$-orders for model calculation loop | [0] |
| p3_order_list | (list) | $p_3$-orders for model calculation loop | [0] |

## Adjustment of the (only!) constant coefficient

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `a0_correction` | (bool) | Adjustment of the (only!) constant coefficient<br>- Shift of constant order for energy at $(0,0,0)$<br>- Note: Only works if first coefficient is the (only!) constant term | False |

## Ridge solver instead of linear regression

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `ridgeCV` | (bool) | Activates Ridge solver instead of linear regression | False |
| ridge_alphas | (list) | List of alphas in Ridge procedure for testing | np.logspace(-6, 2, 9) |

## Column scaling of data matrix

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `col_weighting` | (bool) | Activates column scaling of data matrix according to GOLUB & VAN LOAN | False |

## Saving errors as CSV file

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `save_errors` | (bool) | Activates saving errors as CSV file | True |

# Other remarks:

- Grid rotation does not work in angular coordinate systems because rotation is performed using a matrix and the number of data points per axis must remain constant.
- During rotation, gradient and curvature calculations do not work (PCA). NumPy functions require a regular grid.