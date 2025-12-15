# imfcs-output-handler

Handle output of ImagingFCS (FIJI plugin)

## Usage

### Project setup

1. Clone repository
2. `cd imfcs-output-handler`
3. `pip install hatch`
4. `hatch env create dev` to install project in development mode, `hatch env remove dev` to remove environemnt
5. `hatch shell dev` to enter the environment, `exit`to exit
6. Run notebooks

   - `BatchScreening.ipynb`to screen all batch processed files
   - For analysis example see `AnalyseBatch.ipynb`

### Testing the package from other environemnt (target)

1. Clone repository
2. `cd imfcs-output-handler`
3. Activate the _target_ virtual environment, e.g. `conda activate $MY_ENVIRONMENT`
4. `pip install -e .`
5. Use library in conjuction with others

## Raw data

The membrane fluidity analysis performed using this repository is reported in the following article. Raw datas are available upon request.

[Ocket, E. et al. _Lipid-induced Caveolin1-Lipid droplet trafficking is associated with lipid droplet growth._ bioRxiv 2025.12.10.693432 doi:10.64898/2025.12.10.693432.](https://www.biorxiv.org/content/10.64898/2025.12.10.693432v1)
