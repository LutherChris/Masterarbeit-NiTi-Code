# Parameters of thz - calc

Main parameters for activating the code blocks are `highlighted`.
* (list) means Python lists and NumPy arrays together
  
## Definition of paths

| Parameter | Data type | Description                                                                | Example    |
| --- | --- | --- | --- |
| nks_list | (list) | List of different nks values<br>nks: (int) number of data points per path  | [100] |
| R_list | (list) | List of different R values<br>R: (float) radius for the unit vector u | np.arange(0.33, 0.3725, 0.0025) |
| u | (list) | (ux, uy, uz) - unit vector of the original line around which the rotation occurs | (1, 0, 0); u = u / np.linalg.norm(u) |
| a | (list) | (ax, ay, az) - unit vector for the initial path, which lies orthogonal to u  | (0, 1, 0); a = a / np.linalg.norm(a) |
| r | (float) | Radius for the unit vector a | 0.2 |
| v | (list) | (vx, vy, vz) - displacement vector for the initial path | (0, 0, 0) |
| phi_steps | (int) | Number of intermediate paths between 0° and 180° | 48 |
| minangle | (float) | In deg, minimum angle of calculations (for the plot) | 0 |
| maxangle | (float) | In deg, maximum angle of calculations (for the plot) | 360 |
| decimals | (int) | Determines how many decimal places the path vectors are rounded to, default: 12 | 12 |

## Plot of paths

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `plot_coords` | (bool) | Activates the plot of the paths | False, True |

## Calculation of paths

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `calc` | (bool) | Activates the calculation of the paths by QE | False |
| datlabel | (str) | Extra label in the file name to distinguish calculations | "point1" |

## Loading and analysis of data

| Parameter | Data type | Description | Example |
| ---------------- | --------- | ----------------------------------------------- | -------- |
| `analysis` | (bool) | Activates the loading and analysis of the data | False |
| bandnumbers | (list) | List of bands selected for the plot<br>- If exactly two bands are chosen, the difference is calculated.<br>- Note: counting starts at 0. | [14, 15] |

# Parameters for thz -- plot

Main parameters for activating the code blocks are `highlighted`

## Parameters from the calculation

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| a | (list) | (ax, ay, az) - unit vector for the initial path, which lies orthogonal to u | (0, 1, 0); a / np.linalg.norm(a) |
| r | (float) | Radius for the unit vector a | 0.2 |
| nks_list | (list) | List of different nks values<br>nks: (int) number of data points per path | [100] |
| R_list | (list) | List of different R values<br>R: (float) radius for the unit vector u | np.arange(0.33, 0.3725, 0.0025) |
| phi_steps | (int) | Number of intermediate paths between 0° and 180° | 48 |
| datlabel | (str) | Extra label in the file name to distinguish calculations | "point1" |

## Tricontour and trisurf plots

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `contourplot` | (bool) | Activates tricontour or trisurf plots | False |
| plottype_contourplot | (str) | To distinguish the plot type; possible choices are:<br>"tricontour_diff"<br>"tricontour_band0"<br>"tricontour_band1"<br>"tricontour_limit_diff"<br>"trisurf_diff"<br>"trisurf_band0"<br>"trisurf_band1"<br>"trisurf_all_bands" | "tricontour_limit_diff" |
| levels | (int) | Number of contour lines in the plot | 30 |
| peaks | (bool) | Should the peaks also be plotted as points? | True |
| xlim_values_contourplot | (tuple) | Restriction of the plots to a specific range of the x-axis | None |
| ylim_values_contourplot | (tuple) | Restriction of the plots to a specific range of the y-axis | None |

## Plot of bands along one of the paths

| Parameter | Data type | Description | Example  |
| --- | --- | --- | --- |
| `plotbands` | (bool) | Activates the plot along the paths | False |
| deg | (float) | Plots the path in the kx-plane that is closest to the angle deg (in °) | 45 |
| sym | (bool) | With sym=True, the opposite path rotated by 180° is also plotted | True |
| xlim_values_plotbands | (tuple) | Restriction of the plots to a specific range of the x-axis | None |
| ylim_values_plotband  | (tuple) | Restriction of the plots to a specific range of the y-axis | None |

## Plot depending on the rotation angle

| Parameter | Data type | Description | Example  |
| --- | --- | --- | --- |
| `plot_vs_phi` | (bool) | Activates the plot depending on the rotation angle | False |

## Plot depending on R

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `plot_vs_R` | (bool) | Activates the plot depending on R | False |
| philabel | (bool) | Should the global minima be plotted in color in the legend? | False |
| symmetry | (int) | Symmetry of the data (for the global minima labels) | 4 |
| thz_area_R | (bool) | Data points are filtered according to the THz condition | False |

## 3D plot depending on R and phi

| Parameter | Data type | Description | Example |
| --- | --- | --- | --- |
| `plot_vs_phi_R` | (bool) | Activates the 3D plot | False |
| plottype_phi_R | (str) | To distinguish the plot type; possible choices are:<br>"diff"<br>"bands"<br>"R" | "diff" |
| thz_area_3D | (bool) | Data points are filtered according to the THz condition | False |
