
# Tutorial for model

* This tutorial uses a NiTi calculation as an example.
  The Quantum Espresso input files are located in the `examples/B2_uspp/B2_model` folder.
  To begin, we define the variables in the config.py file (`Masterarbeit-NiTi-Code/src/model/lib`).
  In my case:
```
prefix = "B2_model"
main_directory = "/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/B2_uspp"
num_cores = 6
num_pool = 3
```

* This module is the most complex one. The configuration files are located in subfolders (see table). 
  There is almost always a consistent pattern for naming the configuration files.

| Configuration file with ... | Usage | Example |
| --- | --- | --- |
| "calc" in the name | Calculation | example_model_calc.py |
| "plot" in the name | Plot | example_model_plot.py |
| "path" in the name | Path calculation | example_path_01.py |
| "use" in the name | Application/Comparison | example_use.py |

| Subfolder | Description | Uses ... |
| --- | --- | --- |
| sect | Calculation of the intersection points at Fermi energy | calc, plot |
| path | Calculation of the paths | calc, path |
| model | Calculation of the model | calc, plot |
| modelMME | Calculation of the momentum matrix elements | calc, plot |
| use | Application and Plotting of the model | use |

* This tutorial explains how to use the module using the examples in the subfolders path, model, and use.
* Descriptions of all parameters can be found in the following documents.
  I recommend reading through the tutorial first.

| Configuration file with ... | Overview of all Parameters |
| --- | ---- |
| "calc" in the name | parameters/parameters_of_model/parameters_calc.md |
| "plot" in the name | parameters/parameters_of_model/parameters_plot.md |
| "path" in the name | parameters/parameters_of_model/parameters_path.md |
| "use" in the name | parameters/parameters_of_model/parameters_use.md |

# General information about configuration diles with "calc"

With this type of file, the following sections can be configured:
* Definition of a grid in the Brillouin zone
* Plotting of this grid
* Calculation of band energies via Quantum Espresso on this grid
* Calculation of momentum matrix elements (MME) via Quantum Espresso on this grid
* Reading the QE XML file, analyzing it, and saving it as CSV files
* Loading the CSV file
* Modeling the band energies and the bands

## Definition of fixed parameters

```
# from Intersection calculation (sect)
u = (1, 0, 0)
u = u / np.linalg.norm(u)
a = (0,1,0)
a = a / np.linalg.norm(a)
v = (0, 0, 0)
R = 0.34547436
r = 0.2
phi_steps = 48
bandnumbers = (14, 15) # Attention: Counting starts at 0
zero = (0.34547436, 0.11871832, 0.11871832) # Punkt 1

# from path_calculations (path)
coord_basis="xyz"
a_coeffs=[-0.7332429642612501, 1.7826111869586354, -8.391775184580466, 99.06024644165981]
b_coeffs=[-0.7332557473726407, 1.7698517082611422, -8.400680635383303, 222.30588634644334]
modeltype_path="path_point1"
```

* First, some fixed parameters must be assigned. 
  These include the parameters `u`, `a`, `v`, `r`, `phi_steps`, and `bandnumbers` from the (`thz`) module and a calculation of the intersection point (`sect`).
* Important: The parameter `bandnumbers` contains exactly 2 entries to calculate the band difference.
* The coordinate center of the grid is defined via `zero`.
  After calculating the intersection point near the Fermi energy, the coordinates are set accordingly.
* The next parameters originate from the calculation of the crossing paths of the bands (`path`).
  If the path calculation has not yet been performed, the following parameters can be omitted.
  The parameter `coord_basis` defines which coordinate system was used in the path calculation.
  The model of the path is defined via `modeltype_path`, along with the coefficients defined by `a_coeffs` and `b_coeffs`.

## Main parameters 

```
plot_grid = False                       # BLOCK 2
calc_dft = False                        # BLOCK 3
calc_mme = False; merge_decimals=10     # BLOCK 4
analysis = False                        # BLOCK 5
load_csv = False                        # BLOCK 6
calc_model = False                      # BLOCK 7
```

* The next part of the configuration file contains the main parameters to activate sections with `True` or deactivate them with `False`. 
  Everything should be configured before the main parameters are activated.

| Block | Activation of |
| --- | --- |
| 1 | Definition of the grid (Permanently active) |
| 2 | Plotting of the grid |
| 3 | Calculation of band energies via Quantum Espresso |
| 4 | Calculation of matrix elements via Quantum Espresso |
| 5 | Calculation, analysis, and alignment of DataFrames |
| 6 | Loading the DataFrames |
| 7 | Modeling of the band energies |

* Note: The MME calculation supports the unofficial Quantum Espresso patch `dft2kp`, which can be found at: https://gitlab.com/dft2kp/dft2kp.

## Configuration of some parameters for blocks 5 and 7

```
energy="diff"
coord_system="path"
```

Next, the configuration is done via various parameters, starting with fundamental definitions for Blocks 5 and 7.

* The parameter `energy` specifies which energies the analysis block and model block are based on. Examples are:
  * "diff": band difference
  * "band0": lower band
  * "band1": upper band

* The parameter `coord_system` determines whether a coordinate transformation takes place. The logic works as follows:
  * If the grid is **not** defined via path coordinates {$t, \rho, \phi$} and `coord_system="path"` is set, then the coordinate transformation {$x,y,z$} -> {$t,\rho,\phi$} is calculated numerically (if the coefficients are available).
  * If `coord_system == "xyz_scaled"`, the coordinate system {$x,y,z$} is scaled to the interval [-1,1].
    This is only possible in regular grids. 
    The coord systems of the code are explained in `parameters/parameters_of_model/parameters_of_calc.md`

## Configuration of the grid (Block 1)

```
k0=zero
p=(0.009, 0.04, 0)
n=(19,34,60)
datlabel="punkt1"
grid_type="path"
rotation=False
path_phi_sym=1; path_no_rho0=False; path_rho_dense=0; path_rho_sigma=0.006; path_base_weight=0.2
```

The grid configuration block is active during every execution of the code.
Many grids have been tested over time. All grids use the parameters `k0`, `p`, `n`, `grid_type`, and `datlabel`.
These parameters are also used as a "suffix" later in the calculation to save the results in subfolders.
* The parameter `grid_type` defines the type of grid. In this example, "path" selects a polar grid along the path.
* The center of the grid is defined by the parameter `k0`, set here via `zero` to the intersection point of the bands near the Fermi energy. 
* `p` defines the size of the grid and `n` specifies the number of data points. 
* The parameter `datlabel` is used to distinguish between different calculations. It is used in folder and file names. 

```
/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/B2_uspp   <---- <main_cirectory> folder
├── B2_model/                                                 <---- <prefix> folder
|   ├── B2_model.scf.in
|   └── ...
├── B2_model_out/                                             <-----<prefix>_out folder
|   ├── punkt1_p0009-004-00_n19-34-60/                        <---- <suffix> folder
|   |   └── ...
... ...
```

Attention: The parameters `p` and `n` are defined differently for different grid types - can be read in the parameter overview table `parameters/parameters_of_model/parameters_calc.md`.

* The grid can be rotated via the parameter `rotation`, which is not done in this example. 
  Grid rotation only works for regular grids, because the grid is rotated using a matrix multiplication. 

The remaining parameters are grid-specific:
* The parameter `path_phi_sym=1` defines that no specific grid symmetry is enforced with respect to the angle $\phi$.
* `path_no_rho0=False` defines that the data point $\rho=0$ is included in the grid. 
  (This point can also be removed later via the option `no_000=True`)
* `path_rho_dense=0` defines that there is an increased density of radial data points at the center of the grid.
  The density decreases in a Gaussian manner towards the outside.
  The parameter `path_rho_sigma=0.006`  defines the intensity of this radial Gaussian density, and `path_base_weight=0.2` influences the base value of the radial data point density outside of this Gaussian distribution.


## Configuration of the analysis block (Block 5)

```
pca=False
# ------------------------------------------------------------
no_000=True
# ------------------------------------------------------------
cut_df_for_fit=False
cut_value_diff=0.0124; cut_value_bands=0.05; complete_cut=True
# ------------------------------------------------------------
mme_statistics=False
df_key = "px_abs2_14-15"
# ------------------------------------------------------------
find_intersection=False
intersect_point="point_1"
```

* The parameter `pca` enables a Principal Component Analysis at the energy specified by the `energy` parameter.
  However, this is only possible in Cartesian grids, as the Python functions require a regular grid (`grid_type == "regular"`).
  For this example `grid_type="path"`is set.
  Therefore, `pca` is set to `False`. 

* The parameter `no_000` removes 0-values from the data. 
  This can be useful if the model function is singular at the origin.
  * In the case of `coord_system="xyz"` or `coord_system="xyz_scaled"`, the value x=y=z=0 is removed from the data.
  * In the case of `coord_system="path"`, the value $\rho=0$ is removed from the data.

* The parameter `cut_df_for_fit` crops the data to the THz-active region.
  The THz condition is defined in eV using `cut_value_diff` and `cut_value_bands`. 
  In this case, with the selected values, the following applies:
  *  $\Delta E < 0.0124~eV$;  $E0 > -0.05~eV$;  $E1 < 0.05~eV$ 
  * Here, E0 is the lower band, E1 is the upper band, and $\Delta E$ is the band difference.

* The parameter `complete_cut` determines whether the data should be cropped exactly to the definition of the THz-active region:
  * If `complete_cut=True`, the data is simply filtered according to the above criteria. 
  * If `complete_cut=False`, cropping also takes place, but the original grid shape is preserved. 
    For example, a cylindrical grid that is larger than the THz-active area is adjusted so that the THz-active area just fits within the surface of its cylinder.
	The fundamental shape of the grid is retained. 

* The parameter `mme_statistics` activates the calculation of statistical quantities for the momentum matrix elements.
  The parameter `df_key` defines the set in which the statistical calculation is performed.

* The calculation of the nearest intersection point is activated by the parameter `find_intersection`.
  It triggers the function `model_find_intersect` in `qe_model_calc.py`.
  The function minimizes the absolute value of the sum of the energies and the band difference.
  * The parameter `intersect_point` defines which intersection point is under consideration. 
    The program enforces the alignment of the coordinate axes to avoid numerical errors and was specifically designed for different points.
	For example, for `point_1`, ky=kz is set equal, because it is known that the intersection point at the Fermi energy lies in the 45° direction.

## Configuration of the model calculations (Block 7)

```
no_a0=True
max_coeffs=3000
# ------------------------------------------------------------
modeltype="model_path_abs_4"; coord_system="path"; symmetry=1; no_000=True; energy="diff"

p_order_list = [5]
f_order_list = [27]
l_order_list = [29]
k_order_list = [5]
p1_order_list = [0]
p2_order_list = [0]
p3_order_list = [0]
```

The last section configures the modeling of the energies.
The calculation is performed for different combinations of maximum orders via loops.

* The parameter `no_a0` is used optionally only for certain models and is not important in this example.
  It removes the constant order in some polynomial models.
* The maximum number of coefficients is defined via `max_coeffs`.

* Next, the model type is configured. It is recommended to define all parameters for the model definition in a single line, even if it overwrites parameters like `energy` or `coord_system` from above. This allows you to activate or deactivate different models by commenting them out with `#`. 
  * In this section, the parameter `energy` indicates which energy the model is fitted to!
  * The parameter `modeltype` selects the type of model. 
    A large number of models have been tested.
	A list of all models can be found in file `parameters/parameters_of_model/list_of_models.md`.
	* The parameter `symmetry` is used in some models to exploit data symmetry.
    This is usually a factor inside trigonometric functions.
  * The parameters with `order_list` define the model orders whose combinations are calculated with the model. 
    In this example, only one combination (5,27,29,5) is calculated.
    Different model types require different orders.
    In this example, the orders p1, p2, and p3 are not required.

```
a0_correction = False
# ------------------------------------------------------------
ridgeCV = False 
ridge_alphas = np.logspace(-6, 2, 9) 
# ------------------------------------------------------------
col_weighting = True
# ------------------------------------------------------------
save_errors = False
```
The final configuration parameters do the following:
* The parameter `a0_correction` allows shifting the model curve by adjusting the first coefficient. 
  This is not useful for all models, but only when the first coefficient is the only constant term (e.g., in polynomial models). 
  The adjustment shifts the model so that at the center of the grid, the energy of the data matches the energy of the model. 
  This option is not always a good choice if it introduces larger errors outside the center.
* The parameter `ridgeCV` activates the Ridge regression method instead of linear regression. 
  `ridge_alphas` defines a list of alphas to be tested in the Ridge process.
* The parameter `col_weighting` activates column scaling of the data matrix according to GOLUB & VAN LOAN. 
  This improves the condition number of the linear system of equations and is usually recommended.
* The code calculates the model for different orders in the lists. 
  For each combination, the maximum error at the grid points is calculated from the difference between the model and the data.
  These maximum errors are saved as a csv file if `save_errors=True`.
  If this option is deactivated, the errors are still calculated and printed in the terminal, but they are not saved.
  Deactivating the save function is useful, if you do not want to overwrite a previously long calculation.

## Code execution

### Plotting of the grid (plot_grid=True)
* Using the main parameter `plot_grid=True`, the defined grid can be plotted within the Brillouin zone before the calculation.
  Two figures are plotted. The first figure shows at which data points Quantum Espresso will perform the calculations.
  The second figure shows the shift to the coordinate origin (defined as ${x,y,z}$). 
  Model calculations are usually not performed in the {$k_{x}, k_{y}, k_{z}$} coordinate system.
* Is everything ok, you can deactive the plot for further steps: `plot_grid=False`

### Calculation of band energies (calc_dft=True)
* Once the grid fits properly, the calculation via Quantum Espresso can be activated by setting `calc_dft=True`
  The calculation starts the function `model_calc` from the file `qe_model_calc.py`, which performs the following steps:
  * If the SCF calculation has not yet been performed, it is executed using the Quantum Espresso input file located in the `<prefix>` folder.
    The location of this folder is defined in the `config.py` file.
  * Then, the SCF calculation data is copied from the `tmp_<prefix>` output directory to the `tmp_<prefix>_COPY` folder.
  * Subsequently, the XML file from the SCF calculation is copied from the `tmp_<prefix>_COPY` folder to the `<prefix>_out/<suffix>/scf` folder. 
    The name of the `<suffix>` subfolder is determined by the lattice definition specified earlier.
  * Next, the $\vec{k0}$-points from the lattice definition are written into the QE input file for the NSCF calculation (located in the `<prefix>` folder).
  * Then, the NSCF calculation is executed. 
    This may take some time.
  * Afterward, the NSCF calculation data is copied from the `tmp_<prefix>` output directory to the `<prefix>_tmp/<suffix>` folder.
    Additionally, all files from the configuration folder `<prefix>` are copied to `<prefix>_out/<suffix>`.
  * Finally, the XML file from the NSCF calculation is copied from the `<prefix>_tmp/<suffix>` folder to `<prefix>_out/<suffix>/nscf`.
  * Subsequently, all files in the `tmp_<prefix>` folder are deleted, and the SCF calculation from the `tmp_<prefix>_COPY` folder is copied into it.
    This ensures that the clean SCF calculation is used for a re-run or for a calculation involving a different grid, without the need to recalculate it.
* After the calculation the Parameter can be set to False: `calc_dft=False`.

### Calculation of momentum matrix elements (calc_mme=True)
* Analogous to the calculation of the band energies, the calculation of the momentum matrix elements can now be activated: `calc_mme=True`.
  It uses the input file prefix_bands_x.in in the folder prefix to calculate the matrix elements using the QE subprogram `bands.x`.
* IMPORTANT: The code in this section assumes that `calc_dft` was performed before, as `bands.x` requires the correct SCF and NSCF calculation.
  This is verified by a check.
* The Python code performs the following steps:
  * First, it checks if the XML files of the SCF and NSCF calculations are present in the corresponding folders to ensure that the code block `calc_dft` has already been executed.
  * Then, it checks if the SCF and NSCF files in the folders `<prefix>` and `<prefix>_out/<suffix>` are identical.
  * Next, the namelist parameters "outdir" and "filp" in `<prefix>_bands_x.in` are adjusted so that QE finds the data in the corresponding subfolders and saves the result as `<prefix>_p_avg.dat`.
  * Afterwards, the `bands.x` calculation is performed, and the files of the configuration folder `<prefix>` are copied to `<prefix>_out/<suffix>`.
* After the calculation the Parameter can be set to False: `calc_mme=False`.

## Reading QE XML files, analyzing, and saving as CSV Files (analysis=True)

* After the DFT calculation, the analysis block (`analysis=True`) reads the Quantum Espresso XML files and saves the relevant information as a CSV file.
  Calculations like PCA-Analysis or coordinte transformations are written as new columns into the csv file.
  If a calculation of the momentum matrix elements was performed, the information from the QE `<prefix>_p_avg.dat` file is also read and relevant information is saved as `df_mme.csv`
* After the momentum matrix elements are saved as `df_mme.csv`, the momentum matrix elements are added to the energy data frame as new columns.
* The parameter `merge_decimals` specifies the number of decimal places used to map the coordinates of the MME calculation to the coordinates of the energy calculation.

## Loading the csv file (load_csv=True)
* With `load_csv=True`, the previously calculated csv file can now be loaded.
  This is useful if you want to test different models afterwards without having to run the analysis again.

## Modeling of the band difference and the bands (calc_model=False)

* With `calc_model=False` the model block is activated.
* The csv files for this module are saved in the subfolder named after the `modeltype` parameter.
  If the parameter `modeltype` was not set, the data is saved to the subfolder `out-Dateien`
  The model coefficients for the energy are also saved there using the energy parameter.
* IMPORTANT: Only the model coefficients and energy data of the last combination of orders (i.e., the last loop) are saved! 

The files contain the following:

| File | Contnt |
| --- | --- |
| prefix_df_originl.csv | Original QE data from the xml file, all bands, energies in Hartree |
| prefix_df.csv | Data on which the calculations and modeling were performed. Selected bands only, energies in eV |
| prefix_df_mme.csv | Data on momentum matrix elements |
| prefix_errors_energy.csv | Maximum errors at the data points of the entire grid for different combinations of orders. |
| prefix_errors_thz_energy.csv | Maximum errors at the data points in the THz-active region for different combinations of orders.|
| prefix_coeffs_energy.txt | Coefficients of the model calculation |


# General information about configuration files with "plot"

This section loads the required files from the `"calc"` calculation and enables various plots:
* 2D slider plots
* 3D slider plots
* 4D plots
* 4D plots_mme_in_thz
* Plotting of gradients and curvature
* 2D error plots
* 3D wireframe error plots

## Basic configuration

```
zero=(0.34547436, 0.11871832, 0.11871832)
a_coeffs=[-0.7332429642612501, 1.7826111869586354, -8.391775184580466, 99.06024644165981]
b_coeffs=[-0.7332557473726407, 1.7698517082611422, -8.400680635383303, 222.30588634644334]
modeltype_path="path_point1"
# ------------------------------------------------------------
k0=zero
p=(0.009, 0.04, 0)
n=(19,34,60)
grid_type="path"
datlabel="punkt1"
rotation=False
path_phi_sym=1; path_no_rho0=False; path_rho_dense=0; path_rho_sigma=0.006; path_base_weight=0.2
# ------------------------------------------------------------
modeltype="model_path_abs_4"; coord_system="path"; symmetry=1; no_000=True; energy="diff"

p_order = 5
f_order = 27
l_order = 29
k_order = 5
p1_order = 0
p2_order = 0
p3_order = 0
```

* To activate the plots, some basic configurations from `calc` must be set so that Python can load the CSV files and model coefficients (copy and paste). 
  These include the parameters that define the subfolder `suffix`, as well as the parameters from the last model calculation.
  The orders are not defined as lists in this part of the module.

```
thz_cut_diff=False; thz_cut_band0=False; thz_cut_band1=False
cut_value_diff=0.0124; cut_value_bands=0.05
# ------------------------------------------------------------
coord_system = "path"
# ------------------------------------------------------------
plot_energy_axis = "diff"
plot_titel = ""
```

* Next, it is defined whether the data is filtered before plotting.
  Analogous to the calculation, the filtering criterion is defined by the parameters `cut_value_diff` and `cut_value_bands`. 
  Unlike in the calculation, the three filter criteria can be activated individually.
	* `thz_cut_diff=True` activates $\Delta E < 0.0124~eV$
	* `thz_cut_band0=True` activates $E_0 > -0.05~eV$
	* `thz_cut_band1=True` activates $E_1 < 0.05~eV$
	* If all three parameters are set to `True`, the data is filtered to the THz-active region.

* Then, the $\vec{k}$ axes in the plot are defined via the parameter `coord_system`.
  Not all plotting functions can handle all coordinate systems.
  Maybe check the code (`qe_model_plot.py`) or just try it out. In the worst case, an error message will appear.
  The options are:
  * "kxyz": Original coordinate system: {$k_{x}, k_{y}, k_{z}$}
  * "xyz": Coordinate system centered: {$x,y,z$}
  * "xyz_scaled": Coordinate system centered and scaled to [-1,1]: {$x_{scaled},y_{scaled},z_{scaled}$}
  * "path": Coordinate system along the path r(t): {$t, \rho, \phi$}
  * "tNB": Coordinate system of shifted paths r(t): {$t, v_{N}, v_{B}$}
* The energy axis (or MME-axis) of the plots is determined by the parameter `plot_energy_axis`.
  Again, not all plotting functions work with every setting. 
  Functions that simply plot the QE data can basically plot any column of the CSV file.
  There are functions that evaluate the model at values between the grid points.
  These functions require that the model coefficients were also calculated for this axis.
  The options are:
	* "band0", "band1", "diff", "band0_model", "error_band0", "diff_model", "error_diff", "px", "py", "pz"
* The parameter `plot_title` sets the title for some plots.

Subsequently, individual plots are activated or deactivated using main parameters.
Some plots have individual options, which are listed together with other üarameters in the tabular list for model_plot:
`parameters/parameters_of_model/parameters_plot.md`

# Calculation of the path along band crossings with "path"

In the `calc` part of this tutorial we have defined some parameters like `a_coeffs` or `b_coeffs`.
These coefficients define a path for the models through the Bruilloin zone where the bands cross.
This section shows an example of calculating these coefficients.

* Before calculating the path, an initial grid is calculated via "calc".
  This grid should be larger than the THz-active area to increase accuracy within the THz-active zone itself.
  The file used for this is labeled with `example_path_00_calc.py` in the `src\model\path`folder.
* The other file in this folder containing only "path" in their name (without calc) configures the calculation of the path along the band crossings(`example_path_01.py`).
  Please open this file.

The first path is calculated on the data of the initial grid and then iteratively refined.
The iteration proceeds in the following steps:
* Along a selected axis, the energy values ​​of the perpendicular plane are filtered to find the minimum.
  Then, the path is fitted along these filtered points.
  Afterwards, the data is saved and optionally plotted.
* In the next step, a new grid along the path is defined based on the first fit.
* In this new grid, DFT calculations are performed by QE and saved.
* Then, the data is loaded and fitted again along a chosen axis.
  These steps are repeated until the path has been modeled very precisely.

## Basic configuration

```
bandnumbers = (14, 15)
R=0.34547436
k0=(R, 0.11871832, 0.11871832)
p=0.012
n=11
datlabel="punkt1_000"
modeltype="out-data"
coord_system="xyz"
# ------------------------------------------------------------
point="punkt1"
model_energy="diff"
model_axis="x"
```

First, the basic parameters are set, mostly originating from the DFT calculation.
Additional parameters are:
* The parameter `point` determines which functions are loaded for filtering and fitting.
* `model_energy` defines the energy axis used to filter the data for a minimum search.
  Since the difference between the bands should be minimized, "diff" is used here.
* The parameter `model_axis` defines the coordinate axis along which the data is filtered, in this example "x". 
  For this example, this is the x-axis, as the path model is parameterized by x.

## Fits

### Step 1
```
x_order_0=None; y_order_0=4; z_order_0=4; no_a0_0=True
plot_nk_model_0=1000; plot_path_0=True; calc_path_0=True
# ------------------------------------------------------------
# delta=0.003; n_grid=(50, 10, 10); path_step=0     #->path1-folder (deactivated)
# delta=0.0005; n_grid=(50, 10, 10); path_step=1    #->path2-Ordner (deactivated)
```

Next, the steps of the iteration are defined.
* The maximum polynomial orders of the path model in x, y, and z directions are defined with `x_order_0`, `y_order_0`, and `z_order_0`.
* If the parameter `no_a0_0=True`, constant terms (the 0th-order) are omitted.
* The first path calculation is activated with the parameter `calc_path_0`.
* The parameter `plot_path_0` activates the plot of the result after the fit.
  Here, `plot_nk_model_0` defines the number of data points for plotting the path.
  Two figures are plotted. The first figure shows the minima where the path is fitted. The second figure plots the path itself.

### Step 2
```
plot_nk_model_0=1000; plot_path_0=False; calc_path_0=True
# ------------------------------------------------------------
delta=0.003; n_grid=(50, 10, 10); path_step=0      #->path1-folder (activated)
# delta=0.0005; n_grid=(50, 10, 10); path_step=1   #->path2-Ordner (deactivated)

alpha=0.3; plot_grid = True; path_grid = True 
calc_dft = False
load_new_csv = False
```
The parameter `plot_path_0` from the first step is set to `False`.
Now, the next grid is defined:
* The parameter `delta` symmetrically determines the grid boundaries of the new grid along the path.
  In this example (`point="punkt1"`), these are the grid boundaries along the y and z directions.
  * $y_{\text{path}} \pm \text{delta}$, $z_{\text{path}} \pm \text{delta}$
* The parameter `n_grid` defines the number of data points in the x, y, and z directions.
* The parameter `path_step` determines folder names to save the results.
  Since this is the first iteration, "0" applies here.
  A new folder is created in `<prefix>_out/<datlabel>_path1_p.../` to save the results there.
* The parameter `path_grid=True` activates the new grid, which is plotted using the parameter `plot_grid=True`.
* `alphas` defines the opacity of the grid points in the plot.
* After running the code the figure shows the new grid in blue.
  The old grid is displayed as gray data points.

### Step 3
```
alpha=0.3; plot_grid = False; path_grid = True 
calc_dft = True
```
* If the plot looks satisfactory, it can be deactivated (`plot_grid=False`) and the calculation of the new grid is started via the parameter `calc_dft=True`.

### Step 4
```
plot_nk_model_0=1000; plot_path_0=False; calc_path_0=False
# ------------------------------------------------------------
delta=0.003; n_grid=(50, 10, 10); path_step=0      #->path1-folder (activated)
# delta=0.0005; n_grid=(50, 10, 10); path_step=1   #->path2-Ordner (deactivated)

alpha=0.3; plot_grid = False; path_grid = False 
calc_dft = False
load_new_csv = True
# ------------------------------------------------------------
x_order_1=None; y_order_1=4; z_order_1=4; no_a0_1=True
plot_nk_model_1=1000; plot_path_1 = True; calc_path_1=True
```

* Once the calculation is complete, the parameters `calc_path_0`, `path_grid`, and `calc_dft` are set to `False`.
* The new DFT data is loaded with `load_new_csv=True`.
* A new fit to this data will now be performed.
  This is activated with the parameter `calc_path_1=True`. The new fit can be plotted with `plot_path_1=True`.

### Step 5 and more
```
plot_nk_model_0=1000; plot_path_0=False; calc_path_0=True
# ------------------------------------------------------------
# delta=0.003; n_grid=(50, 10, 10); path_step=0     #->path1-folder (deactivated)
delta=0.0005; n_grid=(50, 10, 10); path_step=1      #->path2-Ordner (activated)

alpha=0.3; plot_grid = True; path_grid = True 
calc_dft = False
load_new_csv = True
# ------------------------------------------------------------
x_order_1=None; y_order_1=4; z_order_1=4; no_a0_1=True
plot_nk_model_1=1000; plot_path_1 = False; calc_path_1=False
```

* Now it continues iteratively.
* The parameters `plot_path_1` and `calc_path_1` are set back to `False`.
* The next smaller grid is activated (line with `path_step=1`) and plotted.
* If the new grid looks satisfactory it can be calculated with `calc_dft = False`
* ...

In this iterative manner, increasingly accurate grids can be defined and more precise fits can be executed step by step.
* The results of the individual steps are saved in subfolders of `<prefix>_out`.
* The subfolders are labeled with "path1", "path2" in the name, etc.
* The model coefficients are then located in the folder `out-data`, because we defined the folder using the parameter `modeltype="out-data"`.
  * The CSV file `<prefix>_coeffs_0.csv` contains the coefficients of the first fit of the iteration step.
  * The csv file `<prefix>_coeffs_1.csv` contains the coefficients of the second (more precise) fit of the iteration.
  * The files `<prefix>_mins_0.csv` and `<prefix>_mins_1.csv` are the data containing the minima where the fits were performed.

The code further down in the configuration file is used to specially plot the most recently active data. For instance, paths within an iteration can be plotted simultaneously.
In addition, a final analysis can be started.
The parameters are explained in the tabular overview:
`parameters/parameters_of_model/parameters_path.md`

# General information about configuration files with "use"

In the subfolder `src/model/use` there is an example for the configuration of this submodule.
First, the band crossing near the Fermi energy is specified:

## Basic configuration
```
k0 = (0.34547436, 0.11871832, 0.11871832) # Punkt 1
# ------------------------------------------------------------
axis_1 = np.linspace(-0.009, 0.009, 20)
axis_2 = np.linspace(0, 0.033, 20)
axis_3 = np.linspace(0, 2*np.pi, 300, endpoint=False)
```

* The application of the model functions is carried out on regular grids.
  This means, that there is no Gaussian compression of the grid.
  The grids along the coordinate axes are determined using the parameters `axis_1`, `axis_2`, and `axis_3`.
  These parameters must be NumPy arrays.
  (Individual data points can also be defined as NumPy arrays.)


> Example 1:\
> axis_1 = np.linspace(-0.009, 0.009, 20)\
> axis_2 = np.linspace(0, 0.033, 20)\
> axis_3 = np.linspace(0, 2*np.pi, 300, endpoint=False)
> * Data points along coordinate axis 1: 20 data points between -0.009 and 0.009
> * Data points along coordinate axis 2: 20 data points between 0 and 0.033
> * Data points along coordinate axis 3: 300 data points between 0 and $2\pi$

> Example 2:\
> axis_1 = an.array([0])\
> axis_2 = an.array([0])\
> axis_3 = an.array([0])
> Only one point is calculated, at the coordinate origin (0,0,0)

```
grid_type="path"
a_coeffs=[-0.7332429642612501, 1.7826111869586354, -8.391775184580466, 99.06024644165981]
b_coeffs=[-0.7332557473726407, 1.7698517082611422, -8.400680635383303, 222.30588634644334]
modeltype_path="path_point1"
```
* Subsequently, the grid type is defined via the parameter `grid_type`.
  In this example, a regular `"path"` grid is used.
  For this, it is necessary to specify the coefficients of the paths and the parameter `modeltype_path`.
  Since no coefficients are needed for the path of Point 3, a_coeffs and b_coeffs are set to None in this example.
  The following types are available:
  * Regular Cartesian grid: `grid_type="regular"`
  * Regular cylindrical grid: `grid_type="cylindrical"`
  * Regular path grid: `grid_type="path"`
  * (Regular path grid for point 2A and 2B: `grid_type="path_grid_2B"`)

```
modeltype= "model_path_abs_4"
p_order = 5
f_order = 27
l_order = 29
k_order = 5
p1_order = 0
p2_order = 0
p3_order = 0
# ------------------------------------------------------------
symmetry=1
```
* Then, the model type and the orders of the model must be defined. This is done via the parameter `modeltype` and `order` parameters.
* Next, additional model properties like `symmetry` are selected.
  We already know these parameters from the model calculation.

```
# OPTION 1:
p=(0.009, 0.04, 0); n=(19,34,60); datlabel="punkt1"; energy="diff" 

# OPTION 2:
load_coeffs_from_path = False
path_coeffs = "..."
```
* Afterwards, the coefficients of the model calculation are loaded. This can be done via two possible options:
  * Option A:
    The model coefficients are loaded from the folder structure of the modeling (`"calc"`).
    The following parameters defined there are required for this: `p`, `n`, `datlabel` and `energy`
  * Option B:
	  Alternatively, the model coefficients can be integrated directly via the file path by setting the parameter `load_coeffs_from_path` to `True`.
		The file path can be defined via `path_coeffs` as a string.

```
save_dataframe = True
path_save = "/home/chris/Schreibtisch/save.csv"
```
* When executing the program, the model energies are calculated at the data points defined in the grid.
  The results can optionally be saved as a csv file.
  To do this, the parameter `save_dataframe` must be set to `True`.
  The CSV file path is defined via the parameter `path_save`.
  If no file path is specified (`path_save=None`), a file named "df_model" is created in the folder previously defined via `p`, `n`, `datlabel` and `energy`.
  
## Plots

In addition to calculating the model energies, they can be plotted directly in the previously defined grid.
2D slider plots and 4D plots (3D + color axis) are available:
* 2D slider plots
	* The parameter `plot_2Dplots` activates the plots with `True`.
    The coordinate axis is specified via `plot_axis`.
	* The parameter `nk_model` determines how many data points are plotted along the coordinate axis.
	* A comparison to QE data can be activated via the parameter `plot_QE_grid`.
    The QE data must be specified via a path using the `parameter path_QE`.
	* Note: In the configuration file `plot_config.py`, the global setting for the parameter `figure.constrained_layout.use` should be set to `False` for slider plots (line 81). Additionally, `PLOT3D = False` should be set.
* 4D plots are activated via the parameter `plot_4Dplots`.

An overview of all parameters can be found here in:
`parameters/parameters_of_model/parameters_use.md`

