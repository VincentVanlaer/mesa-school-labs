# MESA Lab Bonus Tasks

This directory contains enhanced tools to analyze your MESA models and automate running multiple models with different parameters. These tools are organized into two main categories:

1. **Python Analysis** - Tools to create plots and analyze a single MESA run
2. **Batch Runs** - Tools to automate running multiple MESA models with different parameters

## 1. Python Analysis for Single Models

After completing your first MESA model run, you can use these Python scripts to create publication-quality plots and analyze your results without needing to run multiple models.

### Quick Start

```bash
cd bonus_tasks/python_analysis
python hr_plot.py           # Creates HR diagram from your MESA run
python conv_core_plot.py    # Plots core mass evolution
python composition_plot.py  # Shows composition profiles
```

These scripts will automatically detect your MESA model in the `LOGS/` directory and create appropriate plots. All plots are saved to a `plots/` directory for easy access.

NB As these scripts run within a directory with no guaranteed paths, we use relative paths. This is not ideal but do not move these files.

### Available Analysis Scripts

| Script | Description |
|--------|-------------|
| `hr_plot.py` | Creates HR diagrams (both standard and 3D with age as z-axis) |
| `conv_core_plot.py` | Plots convective core mass evolution over time |
| `composition_plot.py` | Shows composition profiles for different elements |

These scripts work "out of the box" with any standard MESA run that includes the necessary history and profile columns (which you set up during the main lab).

---

## 2. Batch Running MESA (Sequentially)

The batch run system allows you to explore how different physical parameters (like overshooting) affect stellar evolution by automating the creation and execution of multiple MESA models, avoiding tedious manual editing of the inlist parameters. 
Bash alternatives for the python files have been provided where possible (whereever mesa reader is not required).
### Directory Structure



## MESA Batch Run Timing

### Runtime Expectations

The MESA batch run framework allows you to efficiently run multiple stellar models with different parameters. Here's what to expect in terms of timing:

- **Setup time**: ~10 minutes to configure batch runs
- **Individual model runtime**:
  - ~70-75 seconds per model (using 4 threads)
  - ~105-125 seconds per model (using 2 threads)

### Performance Considerations

- **Threading impact**: Using 4 threads instead of 2 reduces runtime by approximately 30-40%
- **Batch size options**:
  - Small batch (10 models): Completes in ~12-20 minutes
  - Full parameter space (128 models): Takes ~2.5-4 hours depending on thread count

### Recommendations

For the lab session, we'll provide a subset of ~10 representative models to ensure all students can complete the exercise within the available time. This allows for:

- Quick iteration and analysis
- Exploration of the key parameter effects
- Completion within a single lab period

If you are particularly interested in the topic, you can run larger batches outside of lab hours using the same framework.



```
batch_runs/
├── 0_dependency_check.py/.sh   # Verify your environment is correctly set up
├── 1_make_batch.py/.sh         # Generate inlists from CSV parameter file
├── 2_verify_inlists.py         # Verify inlists were generated correctly
├── 3_run_batch.py/.sh          # Run all inlists sequentially
├── 4_verify_outlists.py        # Verify runs completed successfully
└── 5_construct_output.py       # Extract results into CSV
```

### Workflow for Batch Runs

The typical workflow follows these steps:

0. **Check dependencies** to ensure your environment is properly set up
   ```bash
   python 0_dependency_check.py
   ```

1. **Generate inlists** using a CSV file of parameter combinations
   ```bash
   python 1_make_batch.py MESA_Lab.csv
   ```
   This creates a separate inlist for each parameter set in the `../batch_inlists/` directory.

2. **Verify inlists** similar to before
   ```bash
   python 2_verify_inlists.py MESA_Lab.csv
   ```
   This checks the inlist files for any weird things that may have happened. Both of the methods for constructing the these inlists are prone to error. 

    

3. **Run the models** (this may take several hours)
   ```bash
   python 3_run_batch.py
   ```
   Each model is run sequentially with results saved to `../runs/`

4. **Verify output** 
   ```bash
   python 4_verify_oulists.py MESA_Lab.csv
   ```
 This checks the output files to ensure that we have the expected features seen in our stars.  


5. **Analyze the results** collectively
   ```bash
   python 5_construct_output.py         # Creates a summary CSV
   ```

6. **Revisit python plots** 

   ```bash
   python plot_hr.py                    # Creates combined HR diagram
   python plot_ccore_mass.py            # Plots all core masses
   python plot_composition.py           # Shows composition profiles
   ```

   You can also invesitage how the inlist parameters changed the run time (this can be more apparrent with differnt parameter spaces):

   ```bash
   python plot_timing.py
   ```


### Understanding the Parameter Space

The provided `MESA_Lab.csv` file contains parameter combinations to explore:

- **Initial mass**: 2, 5, 15, 30 M☉
- **Metallicity**: Z = 0.014, 0.0014
- **Overshooting schemes**: None, Exponential, Step
- **Overshooting parameters (f_ov)**: 0.01-0.3
- **Penetration depths (f0)**: 0.001-0.01

You can select a subset of these parameters or create your own parameter combinations.

## Technical Requirements

To run these scripts, you'll need:

- **Python 3.6+** with the following packages:
  - `numpy`
  - `matplotlib`
  - `mesa_reader` (for parsing MESA output)
  - `pandas` (for data manipulation)

- **MESA environment variables** properly set:
  - `MESA_DIR`
  - `MESASDK_ROOT`

The dependency check script will verify these requirements for you.

## Troubleshooting

- If plots don't appear, check if your MESA run generated the required history and profile files
- For batch runs, examine individual log files in `../runs/[model_name]/run.log`
- Ensure your CSV file has the correct format (see `MESA_Lab.csv`)
- For Python errors, verify you have all required packages installed



### Installing MESA Reader

MESA Reader is a Python package for analyzing output from the MESA stellar evolution code.

#### Option 1: Installation with pip

The simplest method using Python's package manager:

```bash
# Standard installation
pip install mesa-reader

# User-specific installation (no admin rights needed)
pip install --user mesa-reader
```


#### Option 2: Installation from source

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/wmwolf/py_mesa_reader.git

# Navigate to the directory
cd py_mesa_reader

# Install in development mode
pip install -e .
```


## Further Customisation

These scripts are designed to be easily modified for your specific research needs:

- Edit plotting styles in the Python files
- Add new parameters to the CSV file
- Modify inlist generation in `make_batch.py`
- Create your own analysis scripts based on the provided examples

---

