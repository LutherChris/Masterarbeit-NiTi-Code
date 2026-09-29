
# Tutorial for fermi

* This tutorial uses a NiTi calculation as an example.
  The Quantum Espresso input files are located in the `examples/nitiB2_uspp/nitiB2_fermi` folder.
  To begin, we define the variables in the config.py file of the fermi-module (`Masterarbeit-NiTi-Code/src/fermi/lib/config.py`).
  In my case:
```
prefix = "nitiB2_fermi"
main_directory = f"/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/nitiB2_uspp"
```

* This small module plots the band structure from a Gnuplot file from QE; it does not perform the calculations.
  The SCF calculation (`calculation = 'scf'`) and NSCF calculation (`calculation = 'bands'`) must first be performed manually using `pw.x` via the terminal.
* Open the terminal in the folder containing the QE input files.
  Then start the QE calculations via the terminal.
  I use 6 cores, 3 of which are connected.
```
mpirun -np 6 pw.x -npool 3 -in nitiB2_fermi.scf.in > nitiB2_fermi.scf.out
```
```
mpirun -np 6 pw.x -npool 3 -in nitiB2_fermi.bands.in > nitiB2_fermi.bands.out
```
```
bands.x < nitiB2_fermi.bands_x.in > nitiB2_fermi.bands_x.out
```
* After the calculation the high-symmetry points are written to the `nitiB2_fermi.bands_x.out`file:
```
     Check: negative core charge=   -0.000024
     Reading collected, re-writing distributed wavefunctions
     high-symmetry point:  0.0000 0.0000 0.0000   x coordinate   0.0000
     high-symmetry point:  0.0000 0.5000 0.0000   x coordinate   0.5000
     high-symmetry point:  0.5000 0.5000 0.0000   x coordinate   1.0000
     high-symmetry point:  0.0000 0.0000 0.0000   x coordinate   1.7071
     high-symmetry point:  0.5000 0.5000 0.5000   x coordinate   2.5731
```
* The numbers after `coordinate` are the position of the x-axis labels of the band energy diagram, defined in the configuration file of the fermi module (`Masterarbeit-NiTi-Code/src/fermi/example_fermi.py`)
```
x_coordinates = [0, 0.5000, 1.0000, 1.7071, 2.5731]
x_labels = ["$\\Gamma$", "X", "M", "$\\Gamma$", "R"]
```
* The parameter `fermi_energy` defines the Fermi energy, which can be determined using the following command in the terminal.
```
grep -e 'Fermi energy' -e estimated nitiB2_fermi.scf.out
```
* Other parameters of the module are listed below.
  When the program is executed, the band energy is plotted along the path.

## Parameters of fermi

The following explains all the parameters of the module. `(list)` means Python lists or NumPy arrays.


| Parameter | Data Type | Description | Example |
| --- | --- | --- | --- |
| gnufile                | (str)   | Filename of the gnuplot file from QE | "nitiB2_fermi.dat.gnu" |
| fermi_energy           | (float) | Fermi energy from QE                 | 16.8868 |
| plot_fermilevel        | (bool)  | Should the Fermi level be plotted?   | True |
| x_coordinates          | (list)  | Path coordinates of the high-symmetry-points | [0, 0.5000, 1.0000, 1.7071, 2.5731] |
| x_labels               | (list)  | Path coordinate labels               | ["$\\Gamma$", "X", "M", "$\\Gamma$", "R"] |
| y_lim                  | (list)  | Y-axis is only plotted within the range of y_lim[0] and y_lim[1] (in eV) | [-2.0, 2.0] |
