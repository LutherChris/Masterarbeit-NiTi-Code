
# Tutorial for thz

* This tutorial uses a NiTi calculation as an example.
  The Quantum Espresso input files are located in the `examples/B2_uspp/B2_thz` folder.
  To begin, we define the variables in the config.py file (`Masterarbeit-NiTi-Code/src/thz/lib`).
  In my case:
```
prefix = "B2_thz"
main_directory = "/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/B2_uspp"
num_cores = 6
num_pool = 3
```

* In this module, calculations (`calc`) and plots (`plot`) are separated.
  The calculations are configured using the configuration file `example_thz_calc.py`.
  The plots are configured via `example_thz_plot.py`.

## Calculations (`example_thz_calc.py`)

* The band energies are calculated along various paths using Quantum Espresso.
  The start and end points of these paths are defined based on the following considerations:
  * start:  $R\vec{u}+\vec{v}$
  * end:    $R\vec{u}+\vec{v}+r(\hat{M}(\vec{u},\phi)\cdot\vec{a}$
  * The vector $\vec{u}$ serves as a normalized origin vector along a line in the Brillouin zone. 
    The displacement vector v serves a generalizing function, forming the connecting line between $R\vec{u}$ and the starting point of the paths.
  * The value $r$ determines the length of the paths.
    The matrix-vector product $\hat{M}\cdot\vec{a}$ defines the unit vector pointing toward the path's end point. 
    The 3x3 matrix $\vec{M}$ is a rotation matrix that rotates the vector $\vec{a}$ around the normalized origin vector $\vec{u}$ by an angle of $\phi$. 
    This rotation is performed using the matrix representation of Rodrigues' rotation formula.
  * For each $R$, a plane of paths is formed that is orthogonal to the vector $\vec{u}$. 
    Varying $R$ ​​creates a cylindrical arrangement of various paths.

First, these ideas are defined in the code:
```
u = (1, 0, 0)
u = u / np.linalg.norm(u) # Normierung
a = (0,1,0)
a = a / np.linalg.norm(a) # Normierung
v = (0, 0, 0)
r = 0.2

R_list = np.arange(0.33, 0.371, 0.00125)
nks_list= [100]
phi_steps = 48
minangle = 0
maxangle = 360
```

* The parameter `nks_list` defines the number of data points along one of the paths. 
  The parameter `phi_steps` defines the angular resolution of the rotation, while `minangle` and `maxangle` allow the paths to be restricted to a specific angular range. 
  The parameter `R_list` defines various R-values ​​for the calculations; for each value in this list, all paths within the plane are subsequently calculated.

### Calculation phase
```
plot_coords = False
calc = False
datlabel = "point1"
```
* To plot all paths prior to calculation, the main parameter `plot_coords=True` must be set.
  The calculation is initiated by setting the parameter `calc=True`.
  Various subfolders are created (see below) within the `prefix` folder during the calculation process.
  The parameter `datlabel` serves as a `suffix` for subfolders to distinguish between different calculation runs.

The calculation proceeds in the following steps:
* First, the SCF calculation is performed if the QE `outdir` folder named `tmp_{prefix}` does not exist.
* Then, the contents of this folder are copied to a new folder named `tmp_{prefix}_COPY`.
* Next, the k-points in the QE input file are modified for the subsequent path.
* The band structure calculation is then performed using the `pw.x` program of QE.
* Subsequently, the `outdir` folder `tmp_{prefix}` is copied to a new folder `{prefix}_tmp`, where all band structure calculations for various paths are organized into subfolders.
* The folder containing the QE input files is also copied to a new folder named `{prefix}_out`. The results are also organized into subfolders.
* Upon completion of the calculation, the QE `outdir` folder `tmp_{prefix}` is cleared, and the SCF data is copied back to it from `tmp_{prefix}_COPY`. This ensures that the next band structure calculation starts from the same clean SCF calculation.

```
/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/B2_uspp <---- <main_cirectory> folder
├── B2_thz/                                                 <---- <prefix> folder
|   ├── B2_thz.scf.in
|   ├── B2_thz.bands.in
|   ├── B2_thz.scf.out
|   └── ...
├── B2_thz_out/                                             <-----{prefix}_out folder
|   ├── point1_nks100_phisteps48_R0.33_r0.2/                <---- <suffix> folder
|   |   ├── 0/
|   |   |   ├── B2_thz_df.csv
|   |   |   └── ...
|   |   ├── 1/
|   |   |   ├── B2_thz_df.csv
|   |   |   └── ...
|   | ...
├── B2_thz_tmp/                                             <---- <{prefix}_tmp> folder   
|   └── ...
├── tmp_B2_thz/                                             <---- <tmp_{prefix}> folder   
|   └── ...
├── tmp_B2_thz_COPY/                                        <---- <tmp_{prefix}_COPY> folder   
|   └── ...
...
```

### Analysis phase
```
analysis = False
bandnumbers = [14,15] # Attention: Counting starts at 0
```
* After the calculation, `calc=False` can be set and the analysis block is activated by setting `analysis=True`.
  This block loads the data from the QE XML file and saves the results as a CSV file in the `<suffix>` folders. 
  The parameter `bandnumbers` defines the bands near the Fermi energy.
  If exactly two bands are specified, the band difference between them is calculated.
  * NOTE: Counting starts at 0. For example, bandnumbers = [14, 15] selects the 15th and 16th bands.
* In addition to the raw data, CSV files containing the local minima of the individual paths are saved.
  Local and global minima across all paths within a plane are also saved as a separate CSV file.
  The table below describes the contents of all CSV files in the subfolders `<suffix>` of `<prefix>_out`:


| CSV file per path in `<suffix>\<number>`| Content |
| ----------------------- | ----------------------------------------------------------------- |
| <prefix>_df.csv           | Original data from the XML file, extended by the entries "phi", "R", "r", and "fermi_energy"; Energies in Hartree, angles in rad          |
| <prefix>_df_for_plots.csv | Data for plots: selected bands, band difference, projection onto the plane, and radius within the plane; Energies in eV, angles in deg |
| <prefix>_peaks.csv        | Data of the local |

| CSV file per entire plane in `<suffix>` | Content |
| --------------------------- | --------------------------------------------- |
| <prefix>_all_df_for_plots.csv | Data for plots of all paths                   |
| <prefix>_all_peaks.csv        | All local minima of all paths                 |
| <prefix>x_phi_peaks.csv        | Local minima of the data from <prefix>_all_peaks.csv  |
| <prefix>_phi_global_peaks.csv | Global minima of the data from <prefix>_all_peaks.csv |

## Plots (`example_thz_plot.py`)

* Once the calculations are complete, the data can be plotted.
  The plots are configured in the configuration file using `example_thz_plot.py`.
  There, the calculation parameters are defined first so that the program can locate the paths to the CSV files.

```
a = (0,1,0)
a = a / np.linalg.norm(a) # Normierung
r = 0.2

R_list = np.arange(0.33, 0.371, 0.00125)
#R_list = [0.34625]

nks_list= [100]
phi_steps = 48
datlabel = "point1"
```
The following sections enable the generation of various plots:
- 2D tricontour plots and 3D trisurf plots of the bands and the band difference
- Plot of the energy bands and their difference along the path of a specific angle
- Plot of the band difference and bands as a function of the rotation angle; all local minima are plotted for each rotation angle (i.e., for each path)
- Plot of the minima of all paths as a function of R; all local minima in the plane are plotted for each R
- Plot of the band difference or the bands as a function of R and phi, displayed as 3D surfaces

Some plots have configuration options that, along with all other variables, are listed and described in the tabular overview below.



# Parameters of thz - calc

Main parameters for activating the code blocks are `highlighted`.
* (list) means Python lists and NumPy arrays together
  
### Definition of paths

| Parameter | Data type | Description                                                                | Example    |
| --------- | --------- | -------------------------------------------------------------------------- | ---------- |
| nks_list  | (list)    | List of different nks values<br>nks: (int) number of data points per path  | [100]      |
| R_list    | (list)    | List of different R values<br>R: (float) radius for the unit vector u      | np.arange(0.33, 0.3725, 0.0025)      |
| u         | (list)    | (ux, uy, uz) - unit vector of the original line around which the rotation occurs | (1, 0, 0); u = u / np.linalg.norm(u) |
| a         | (list)    | (ax, ay, az) - unit vector for the initial path, which lies orthogonal to u  | (0, 1, 0); a = a / np.linalg.norm(a)   |
| r         | (float)   | Radius for the unit vector a                                               | 0.2        |
| v         | (list)    | (vx, vy, vz) - displacement vector for the initial path                    | (0, 0, 0)  |
| phi_steps | (int)     | Number of intermediate paths between 0° and 180°                           | 48         |
| minangle  | (float)   | In deg, minimum angle of calculations (for the plot)                       | 0          |
| maxangle  | (float)   | In deg, maximum angle of calculations (for the plot)                       | 360        |
| decimals  | (int)     | Determines how many decimal places the path vectors are rounded to, default: 12 | 12    |

### Plot of paths

| Parameter     | Data type | Description                     | Example     |
| ------------- | --------- | ------------------------------- | ----------- |
| `plot_coords` | (bool)    | Activates the plot of the paths | False, True |

### Calculation of paths

| Parameter    | Data type | Description                                                | Example  |
| ------------ | --------- | ---------------------------------------------------------- | -------- |
| `calc`       | (bool)    | Activates the calculation of the paths by QE               | False    |
| datlabel     | (str)     | Extra label in the file name to distinguish calculations   | "point1" |

### Loading and analysis of data

| Parameter        | Data type | Description                                     | Example  |
| ---------------- | --------- | ----------------------------------------------- | -------- |
| `analysis`       | (bool)    | Activates the loading and analysis of the data  | False    |
| bandnumbers      | (list)    | List of bands selected for the plot<br>- If exactly two bands are chosen, the difference is calculated.<br>- Note: counting starts at 0. | [14, 15]  |

# Parameters for thz -- plot

Main parameters for activating the code blocks are `highlighted`

### Parameters from the calculation

| Parameter | Data type | Description                                                                  | Example                           |
| --------- | --------- | ---------------------------------------------------------------------------- | --------------------------------- |
| a         | (list)    | (ax, ay, az) - unit vector for the initial path, which lies orthogonal to u  | (0, 1, 0); a / np.linalg.norm(a)  |
| r         | (float)   | Radius for the unit vector a                                                 | 0.2                               |
| nks_list  | (list)    | List of different nks values<br>nks: (int) number of data points per path    | [100]                             |
| R_list    | (list)    | List of different R values<br>R: (float) radius for the unit vector u        | np.arange(0.33, 0.3725, 0.0025)   |
| phi_steps | (int)     | Number of intermediate paths between 0° and 180°                             | 48                                |
| datlabel  | (str)     | Extra label in the file name to distinguish calculations                     | "point1"                          |

### Tricontour and trisurf plots

| Parameter               | Data type | Description                                                  | Example |
| ----------------------- | --------- | ------------------------------------------------------------ | ------- |
| `contourplot`           | (bool)    | Activates tricontour or trisurf plots                        | False   |
| plottype_contourplot    | (str)     | To distinguish the plot type; possible choices are:<br>"tricontour_diff"<br>"tricontour_band0"<br>"tricontour_band1"<br>"tricontour_limit_diff"<br>"trisurf_diff"<br>"trisurf_band0"<br>"trisurf_band1"<br>"trisurf_all_bands" | "tricontour_limit_diff" |
| levels                  | (int)     | Number of contour lines in the plot                          | 30      |
| peaks                   | (bool)    | Should the peaks also be plotted as points?                  | True    |
| xlim_values_contourplot | (tuple)   | Restriction of the plots to a specific range of the x-axis   | None    |
| ylim_values_contourplot | (tuple)   | Restriction of the plots to a specific range of the y-axis   | None    |

### Plot of bands along one of the paths

| Parameter             | Data type | Description                                                            | Example  |
| --------------------- | --------- | -----------------------------------------------------------------------| -------- |
| `plotbands`           | (bool)    | Activates the plot along the paths                                     | False    |
| deg                   | (float)   | Plots the path in the kx-plane that is closest to the angle deg (in °) | 45       |
| sym                   | (bool)    | With sym=True, the opposite path rotated by 180° is also plotted       | True     |
| xlim_values_plotbands | (tuple)   | Restriction of the plots to a specific range of the x-axis             | None     |
| ylim_values_plotband  | (tuple)   | Restriction of the plots to a specific range of the y-axis             | None     |

### Plot depending on the rotation angle

| Parameter           | Data type | Description                                        | Example  |
| ------------------- | --------- | -------------------------------------------------- | -------- |
| `plot_vs_phi`       | (bool)    | Activates the plot depending on the rotation angle | False    |

### Plot depending on R

| Parameter     | Data type | Description                                                     | Example  |
| ------------- | --------- | --------------------------------------------------------------- | -------- |
| `plot_vs_R`   | (bool)    | Activates the plot depending on R                               | False    |
| philabel      | (bool)    | Should the global minima be plotted in color in the legend?     | False    |
| symmetry      | (int)     | Symmetry of the data (for the global minima labels)             | 4        |
| thz_area_R    | (bool)    | Data points are filtered according to the THz condition         | False    |

### 3D plot depending on R and phi

| Parameter         | Data type | Description                                                                     | Example  |
| ----------------- | --------- | ------------------------------------------------------------------------------- | -------- |
| `plot_vs_phi_R`   | (bool)    | Activates the 3D plot                                                           | False    |
| plottype_phi_R    | (str)     | To distinguish the plot type; possible choices are:<br>"diff"<br>"bands"<br>"R" | "diff"   |
| thz_area_3D       | (bool)    | Data points are filtered according to the THz condition                         | False    |
