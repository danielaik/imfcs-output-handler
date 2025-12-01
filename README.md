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

   - `01_batch_screening.ipynb`to screen all batch processed files
   - For analysis example see `03_analyse.ipynb`

### Testing the package from other environemnt (target)

1. Clone repository
2. `cd imfcs-output-handler`
3. Activate the _target_ virtual environment, e.g. `conda activate $MY_ENVIRONMENT`
4. `pip install -e .`
5. Use library in conjuction with others

## Raw data

Raw datas are available upon request or can be downlowded here XX
