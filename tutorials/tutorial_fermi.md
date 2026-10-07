
# Tutorial for fermi

* This tutorial uses a NiTi calculation as an example.
  The Quantum Espresso input files are located in the `examples/B2_uspp/B2_fermi` folder.
  To begin, we define the variables in the config.py file of the fermi-module (`Masterarbeit-NiTi-Code/src/fermi/lib/config.py`).
  In my case:
```
prefix = "B2_fermi"
main_directory = f"/home/chris/VS_code/Masterarbeit-NiTi-Code/examples/B2_uspp"
```

* This small module plots the band structure from a Gnuplot file from QE; it does not perform the calculations.
  The SCF calculation (QE: `calculation = 'scf'`) and NSCF calculation (QE: `calculation = 'bands'`) must first be performed manually using `pw.x` via the terminal.
* Open the terminal in the folder containing the QE input files.
  Then start the QE calculations via the terminal.
  I use 6 cores, 3 of which are connected.
```
mpirun -np 6 pw.x -npool 3 -in B2_fermi.scf.in > B2_fermi.scf.out
```
```
mpirun -np 6 pw.x -npool 3 -in B2_fermi.bands.in > B2_fermi.bands.out
```
```
bands.x < B2_fermi.bands_x.in > B2_fermi.bands_x.out
```
* After the calculation the high-symmetry points are written to the `B2_fermi.bands_x.out`file:
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
gnufile = "B2_fermi.dat.gnu"
fermi_energy = 16.5866
plot_fermilevel = True
y_lim = [-2, 2]
x_coordinates = [0, 0.5000, 1.0000, 1.7071, 2.5731]
x_labels = ["$\\Gamma$", "X", "M", "$\\Gamma$", "R"]
```
* The parameter `fermi_energy` defines the Fermi energy, which can be determined using the following command in the terminal.
```
grep -e 'Fermi energy' -e estimated B2_fermi.scf.out
```
* The other parameters of the module are listed in `parameters/parameteters_of_fermi/parameters_fermi.md`.
* When the program is executed, the band energy is plotted along the path.
