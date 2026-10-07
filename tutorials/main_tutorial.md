
# Project structure and first configuration

* The Python code in the src folder is divided into the 5 main modules.
  The folder structure is shown below.
  The Python code in the `src` folder is divided into the 5 main modules.
  The module-folders contain files in which the variables required for the calculations are defined.
  The module named `model` is an exception, as the configuration files are located in subfolders.
  In the modules `model` and `thz`, there is a standard pattern for naming these configuration files:

| Configuration file with ...   | Usage         |
| ----------------------------- | --------------|
| `calc` in name                | calculation   |
| `plot` in name                | plotting      |

> Example 1\
> The file `example_conv.py` in the module-folder `conv` defines all variables for the SCF calculation and plotting.

> Example 2\
> The file `example_model_calc.py` in the sub folder `model` defines all variables for the calculation of band structures and modeling.\
> The file `example_model_plot.py` in the sub folder `model` defines all variables for plotting the results.

* The `lib` subfolder of each module contains files in which functions and code sections are defined.
  Alongside these files, there is always a `config.py` file. 
  This file must be manually configured before the first calculation.
* Additionally, the configuration file `plot_config.py` defines global plot settings of `matplotlib` for the module.
  If a plot does not display correctly, the settings here must be adjusted.
  Alternatively, the specific plot function can be modified (mostly in a `plot.py` file).

* During the calculation process, Python will access various files and folders (and also create some).
  These files and folders are defined via the functions and variables in `config.py`.
  The following variables need to be defined manually:

| Variable | Meaning |
| --- | ---
| <main_directory> | main folder path for the calculations and results |
| <prefix> | subdirectory path for the Quantum Espresso input-files |
| <num_cores> | number of cores for parallel calculations (mpirun -np {num_cores}) |
| <num_pool> | number of linked processor cores (-npool {num_pool}) |

* A folder `pseudo` containing the pseudopotentials should be located in the `main_directory` folder.
* The Quantum Espresso (QE) input-files are located inside the prefix-folder.
  Within these input-files, the QE parameters are defined as the folder-names:

```
prefix = '<prefix>'
pseudo_dir = '../pseudo'
outdir = '../tmp_<prefix>'
```

> Example\
> The band structures of the B2 phase of NiTi are to be calculated using uspp-pseudopotentials.
> The main calculation directory is located at: `"/home/chris/nitiB2_uspp"`.
> The pseudo folder, containing the pseudopotentials is also located there.
> The `conv` module for the SCF calculation is used.
> Therefore, the subdirectory is named `nitiB2_conv`.\
> Consequently, the following variables in the Python code are defined as:
>   - main_directory = "/home/chris/nitiB2_uspp"
>   - prefix = "nitiB2_conv"
>
> Inside the QE-input-files, the QE-parameteres are defined as follows:
>   - prefix = 'nitiB2_conv'
>   - pseudo_dir = '../pseudo'
>   - outdir = '../tmp_nitiB2_conv'

For clarity, the tutorials for each module are explained in different documents.
These documents contain descriptions of all variables as well as explanations using examples.

| Module | Tutorial |
| --- | --- |
| conv | tutorial_conv.md |
| fermi | tutorial_fermi.md |
| thz | tutorial_thz.md |
| model | tutorial_model.md |
| transport | tutorial_transport.md |


```
Masterarbeit-NiTi-Code/                   <main_cirectory>/
├── src/                                        ├── <prefix>/
    ├── conv/                                   |   ├── <prefix>.scf.in
    |   ├── lib/                                |   ├── <prefix>.nscf.in
    |   |   ├── config.py                       |   ├── <prefix>.scf.out
    |   |   ├── plot_config.py                  |   └── ...
    |   |   ├── qe_conv.py                      ├── <prefix_out>/
    |   |   └── run_conv.py                     |   ├── <suffix>/
    |   ├── example_conv.py                     |   |   ├── <nscf>/
    |   └── ...                                 |   |   |   └── <prefix>.xml
    ├── model/                                  |   |   ├── <scf>/
    |   ├── lib/                                |   |   |   └── <prefix>.xml
    |   |   ├── config.py                       |   |   ├── <modeltype>/
    |   |   ├── plot_config.py                  |   |   |   ├── <prefix>_df.csv
    |   |   ├── qe_model_calc.py                |   |   |   ├── <prefix>_df_original.csv
    |   |   ├── ...                             |   |   |   ├── <prefix>_errors_diff.csv
    |   |   ├── run_model_calc.py               |   |   |   ├── <prefix>_coeffs_diff.csv
    |   |   └── ...                             |   |   |   └── ...
    |   ├── sect/                               |   |   ├── log/
    |   |   ├── example_sect_calc.py            |   |   |   └── log.txt                      
    |   |   ├── example_sect_plot.py            |   |   ├── tmp/   
    |   |   └── ...                             |   |   |   ├── <prefix>.scf.in
    |   ├── model/                              |   |   |   └── ...
    |   |   ├── example_model_calc.py           |   |   ├── <prefix>.scf.in
    |   |   ├── example_model_plot.py           |   |   ├── <prefix>.nscf.in
    |   |   └── ...                             |   |   ├── <prefix>.scf.out
    |   ├── modelMME/                           |   |   └── ...
    |   |   ├── example_modelMME_calc.py        |   └── ...
    |   |   ├── example_modelMME_plot.py        ├── <prefix_out>/
    |   |   └── ...                             |   ├── <suffix>/
    |   ├── path/                               |   |   ├── <prefix>.save/
    |   |   ├── example_path_00_calc.py         |   |   ├── <prefix>.xml
    |   |   ├── example_path_01.py              |   |   └── ...
    |   |   └── ...                             |   └── ...
    |   └── ...                                 ├── pseudo/
    ├── thz/                                    |   └── ...
    |   ├── lib/                                ├── tmp_<prefix>
    |   |   ├── config.py                       |   ├── <prefix>.save/
    |   |   ├── plot_config.py                  |   ├── <prefix>.xml
    |   |   ├── qe_thz_calc.py                  |   └── ...                       
    |   |   ├── ...                             ├── tmp_<prefix>_COPY/           
    |   |   ├── run_thz_calc.py                 |   ├── <prefix>.save/                         
    |   |   └── ...                             |   ├── <prefix>.xml         
    |   ├── example_thz_calc_uspp_punkt1.py     |   └── ...
    |   ├── example_thz_plot_uspp_punkt1.py     |                                  
    |   |   └── ...                             ...               
    ...                                             
```  