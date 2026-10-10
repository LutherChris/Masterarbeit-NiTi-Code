# Installation Instructions for Quantum Espresso

* The Quantum Espresso program is required to calculate the band energies. Version 7.6 was tested.
  During the installation parallel processing with multiple processors is activated.
  For the installation I used the following commands/steps in Linux Mint Cinnamon:

```
sudo apt update && sudo apt upgrade
```
* initial required programs:
```
sudo apt install --no-install-recommends \
    autoconf \
    build-essential \
    ca-certificates \
    gfortran \
    libblas3 \
    libc6 \
    libfftw3-dev \
    libgcc-s1 \
    liblapack-dev \
    wget \
    libopenmpi-dev \
    libscalapack-openmpi-dev \
    libelpa19
```
* nvfortran-Compiler from the NVIDIA HPC SDK, v.21.7 or later:
  * https://developer.nvidia.com/hpc-sdk
* cmake:
```
sudo apt-get install cmake cmake-qt-gui
```
* gnuplot:
```
sudo apt-get install gnuplot gnuplot-x11 gnuplot-doc
```
* git:
```
sudo apt-get install git
```
* Download Quantum ESPRESSO (Version 7.6 tested): 
  * https://gitlab.com/QEF/q-e/-/releases
* move the downloaded file to a desired folder
* unpacking the source files

## Configuration

* go to QE folder:
```
cd q-e-qe-7.6/
```
* configuration:
```
./configure
```
* compiling with <n> cores on my pc
  * you can find the number of cores <n> with `nproc`
```
 make pwall -j<n>
```
* navigate to the bin folder and get the path using `pwd`
* go back to the home folder using cd, then: (replace <path> with your path)
```
echo 'export PATH="<path>:$PATH"' >> ~/.bashrc
```
* restart the terminal
* the .x files of Quantum Espresso can now be accessed quickly:
```
which pw.x
```

## Installation of Python

* My development environment consists of Anaconda and Visual Studio Code, though standard Python with pip is also an option.
  This tutorial guides through the Anaconda installation process.
* download Miniconda: https://www.anaconda.com/download/success
* change file permissions:
```
chmod +x Miniconda3-latest-Linux-x86_64.sh
```
* execute files
```
bash Miniconda3-latest-Linux-x86_64.sh
```
* if conda is automatically activated, this setting will now be configured so that conda does not always start when the terminal is opened:
```
conda config --set auto_activate_base False
```
* restart the terminal and start the Anaconda environment:
```
conda activate
```
* create a new Anaconda environment:
```
conda create --name myenv
```
* activate the new Anaconda environment:
```
conda activate myenv
```
* Install all required Python libraries:
```
conda install conda-forge::vtk
conda install conda-forge::pyfftw
conda install conda-forge::boltztrap2
conda install anaconda::numpy
conda install anaconda::pandas
conda install anaconda::matplotlib
conda install conda-forge::scikit-learn
conda install anaconda::scipy
```
If I've forgotten anything here, an error message will appear when running the code. Then simply load the required module in the same way.
* I use Visual Studio Code, but another editor can also be used.
* download Visual Studio Code and install it: https://code.visualstudio.com/
* in Visual Studio Code, activate Anaconda as the Python environment:
```
strg+shift+P -> Python: Select Interpreter -> conda-Umgebung (myenv)
```

## Fix for BoltzTraP2

* When plotting the Fermi surface using terminal commands with BoltzTraP2, an error message appears when varying the chemical potential. This can be fixed with a small modification to the file <fermisurface.py>:
* change the following in line 433:
```
a.SetVisibility(visible) -> a.SetVisibility(int(visible))
```

## Installing the dft2kp patch (https://gitlab.com/dft2kp/dft2kp):

* Download the patch for your QE version:
  https://gitlab.com/dft2kp/dft2kp/-/tree/main/patch
* Copy the patch from dft2kp to the QE folder:
  `q-e-qe-7.6/patch/qe2kp-7.6.patch`
* Open the terminal in the QE folder
* Create a virtual Python environment in the QE folder:
```
python3 -m venv venv
```
* Start the Python environment
```
source venv/bin/activate
```
* Install dft2kp with pip
```
pip install git+https://gitlab.com/dft2kp/dft2kp.git
```
* Then, in the Python environment within the QE folder, execute the following commands:
```
git init
git add
git commit -m "Initial QE commit
git apply patch/qe2kp-7.6.patch
```
* Restart the Terminal
* Recompile QE, where 12 is the number of cores
```
make pwall -j12
```

## Changes after the dft2ko patch:
* The QE XML files uses scientific notation (e.g., 3.383630720470000E-001).
  With this change, the k-Points for the momentum matrix elements (`p_avg.dat`) is specified in the same format and with maximum precision.
  This allows the MME to be assigned to the calculated energies.

* Open the QE file:
  `/home/chris/q-e-qe-7.6/PP/src/write_p_avg.f90`
* Change line 160 to:
```
        WRITE (iunout, '(10x,3es25.16,i7)') xk(1,ik),xk(2,ik),xk(3,ik), &
```
* The old line was:
```
        WRITE (iunout, '(10x,3f10.8,i7)') xk(1,ik),xk(2,ik),xk(3,ik), &
```
* Recompile QE, where 12 is the number of cores
```
make pwall -j12
```