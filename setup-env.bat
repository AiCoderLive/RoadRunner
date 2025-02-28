@echo off
echo Installing Mamba environment manager...
conda install -y -c conda-forge mamba

echo Creating environment from environment.yml...
mamba env create -f environment.yml

echo Environment setup complete! Activate with: conda activate road_runner