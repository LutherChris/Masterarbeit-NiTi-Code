The following explains all the parameters of the submodule `use`.
Main parameters for activating code blocks are `highlighted`.

# Creation of the Grid

| Parameter | Data Type | Description | Example |
| --------- | ------------- | --------------------------------- | -------------------------------------------- |
| k0 | (list) | Band crossing at the Fermi energy | (0.5, 0.5, 0.09513568) |
| axis_1 | (NumPy array) | Division of coordinate axis 1 | np.linspace(-0.007, 0.007, 30) |
| axis_2 | (NumPy array) | Division of coordinate axis 2 | np.linspace(0, 0.016, 30) |
| axis_3 | (NumPy array) | Division of coordinate axis 3 | np.linspace(0, 2*np.pi, 140, endpoint=False) |
| grid_type | (str) | Definition of the grid type | "path" |

- Available grids:
	- regular Cartesian grid: `grid_type = "regular"`
	- regular cylindrical grid: `grid_type = "cylindrical"`
	- regular path grid: `grid_type = "path"`
	- regular path grid for points 2A and 2B: `grid_type = "path_grid_2B"`

- In the case of path grids:

| Parameter | Data Type | Description | Example |
| -------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| a_coeffs | (list) | $a$-coefficients of $r(t)$ | [-0.7410615827179478, 1.840838706272784, -11.842134854139516, 7.412966199122343] |
| b_coeffs | (list) | $b$-coefficients of $r(t)$ | [-0.7415216975597553, 1.7940027615351415, -8.71052528076767, 287.3393435525252] |
| modeltype_path | (str) | Model of the path<br>"path_point1": Path for point 1<br>"path_point2A": Path for point 2A<br>"path_point2B": Path for point 2B<br>"path_point3": Path for point 3<br>"path_point1_center": Path for point 1 along the center of the shell | "path_point1" |

# Calculation of Model Energies

- see ("Overview of All Parameters (calc)")

| Parameter | Data Type | Description | Example |
| --------- | ------------ | ---------------------------------------------------------------- | ------------------ |
| modeltype | (str) | Sets the model type | "model_path_abs_4" |
| symmetry | (int),(None) | Symmetry factor in the model functions | 1 |
| no_a0 | (bool) | Should the $0$-th order be omitted in the polynomial models? | False |

- Orders:

| Parameter | Data Type | Description | Example |
| ------------ | -------- | ---------------------- | -------- |
| p_order | (int) | $p$-order of the model | 2 |
| f_order | (int) | $f$-order of the model | 17 |
| l_order | (int) | $l$-order of the model | 20 |
| k_order | (int) | $k$-order of the model | 3 |
| p1_order | (int) | $p1$-order of the model | 0 |
| p2_order | (int) | $p2$-order of the model | 0 |
| p3_order | (int) | $p3$-order of the model | 0 |

# Loading Model Coefficients

| Parameter | Data Type | Description | Example |
| ------------------------- | -------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `load_coeffs_from_path` | (bool) | Should the model coefficients be loaded from a file path? | True |
| path_coeffs | (str) | Specifies the file path. | "/home/chris/Dokumente/Digitaler Anhang/Modellkoeffizienten/Ordnungen/uspp/Punkt 3/diff/2-3-1/nitiB2_model_coeffs_diff.txt" |

- If `load_coeffs_from_path = False`:
	- `p`, `n`, `datlabel`, `energy` from `Overview of All Parameters (calc)`

# Saving Model Energies

| Parameter | Data Type | Description | Example |
| ------------------ | -------- | -------------------------------------------------------- | ----------------------------------- |
| `save_dataframe` | (bool) | Activates saving the model energies as a CSV file | True |
| path_save | (str) | Specifies the file path for saving. | "/home/chris/Schreibtisch/save.csv" |

# Plotting the Data

| Parameter | Data Type | Description | Example |
| ---------------- | -------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `plot_2Dplots` | (bool) | Activates 2D plots | True |
| plot_axis | (str) | Coordinate axis to plot | "phi" |
| nk_model | (int) | Number of data points | 2000 |
| plot_QE_grid | (bool) | Should the model energy be compared with QE data? | True |
| path_QE | (str) | File path of the QE data | "/home/chris/nitiB2_uspp/nitiB2_model_out/punkt3_center_thz_p0007-0019-00_n21-28-64/model_path_point3_2/nitiB2_model_df.csv" |
| `plot_4Dplot` | (bool) | Activates 4D plots (3D + color axis) | True |