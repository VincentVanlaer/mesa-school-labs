# MESA Lab Bonus Tasks


<p align="center">
  <img src="python_analysis/plots/hr_diagram_3d_rotation.gif" alt="Animated HRD" height="300">
</p>


**This is advanced bonus content** - only attempt after completing the main lab successfully.

You are required to have completed main MESA lab1 with successful overshooting parameter modifications


## Python Analysis and Visualization

### Overview

After completing your first MESA model run, you can use these Python scripts to create publication-quality plots and analyze your results. These scripts work as either **Single Model Analysis** or **Batch Analysis**.


### Location and Usage

```bash
cd bonus_tasks/python_analysis

# These scripts work for both single and batch analysis
python hr_plot.py           # HR diagrams (single track or multiple tracks)
python conv_core_plot.py    # Core evolution (one star or parameter study)
python composition_plot.py  # Chemical profiles (final model or comparative)
```

**All plots and animations are saved to `plots/` directory.**

---


### `hr_plot.py` - Hertzsprung-Russell Diagram Generator

Creates the fundamental diagram of stellar astrophysics showing how stars move through temperature-luminosity space during evolution.

#### Output:

- **`hr_diagram.png`**: Evolutionary track with color-coded evolutionary phases
- **`hr_diagram_3d.png`**: 3D version with stellar age as the third dimension

- **`all_hr_diagrams.png`**: Multiple evolutionary tracks color-coded by mass, line-coded by overshooting scheme
- **`all_hr_diagrams_3d.png`**: 3D comparative view showing age evolution for all models
- **`hr_diagram_3d_rotation.gif`**: Animated 3D plot rotating to show all viewing angles


#### What the Script Does

**Data Processing:**
1. Loads `log_Teff` (effective temperature) and `log_L` (luminosity) from history files
2. For single models: Creates color mapping based on central hydrogen abundance
3. For batch models: Assigns colors by stellar mass, line styles by overshooting scheme
4. Identifies key evolutionary points (ZAMS, TAMS) when hydrogen abundance data available


#### Interpretation

**Key Features:**
- **Main Sequence**: Nearly horizontal tracks where stars spend most of their lives
- **Turn-off Points**: Where tracks bend upward, marking hydrogen exhaustion
- **Mass Effects**: More massive stars (brighter, hotter) have shorter main sequence lifetimes
- **Overshooting Effects**: Stronger overshooting extends main sequence evolution -- do we see this?

**Physical Insights:**
- Track length shows main sequence lifetime
- Turn-off luminosity indicates stellar mass
- Comparison between models reveals overshooting effects on evolutionary timescales


---

### `conv_core_plot.py` - Convective Core Mass Evolution

Tracks how the convective core (the star's energy-producing region) changes throughout stellar evolution. This is a good way of directly revealing overshooting effects.


#### Output

- **`core_mass_evolution.png`**: Absolute core mass vs. stellar age
- **`core_mass_fraction.png`**: Core mass as percentage of total stellar mass vs. age

- **`core_mass_vs_log_age.png`**: All models overlaid showing core mass evolution
- **`core_mass_fraction_vs_log_age.png`**: Fractional core masses for comparison

#### What the Script Does

**Data Processing:**
1. Searches for core mass data (`he_core_mass`, `mass_conv_core`, or `conv_mx1_top`)  
2. Converts stellar age to Myr (millions of years) for readable timescales
3. For batch analysis: Color-codes by overshooting scheme


#### Interpretation

**Core Mass Growth Patterns:**
- **Rising trends**: Core grows as hydrogen burns and convective boundary moves outward
- **Plateaus**: Periods of stable core size
- **Sharp increases**: Convective boundary jumps due to composition changes
- **Final values**: Determine post-main sequence evolution path

**Overshooting Effects:**
- **No overshooting**: Sharp core boundaries, smaller final core masses
- **Exponential overshooting**: Gradual core growth, larger final masses
- **Step overshooting**: Intermediate behavior with discrete boundary extensions

**Mass Dependencies:**
- Higher mass stars: Larger cores, faster evolution
- Lower mass stars: Smaller cores, longer main sequence lifetimes
- Metallicity effects: Lower Z stars may show different core evolution patterns

**Why This Matters:**
Core mass directly determines:
- Main sequence lifetime (larger cores burn longer)
- Post-main sequence evolution (helium flash vs. non-degenerate helium burning)
- Final stellar remnant type (white dwarf, neutron star, black hole)


---

### `composition_plot.py` - Chemical Composition Analysis

#### Purpose
Reveals the star's internal chemical structure, showing how nuclear burning and mixing processes distribute elements throughout the stellar interior.

#### Single Model Output
- **`composition_profile.png`**: Hydrogen, helium, and metal abundances vs. mass coordinate at the final evolutionary model

#### Batch Model Output  
- **`core_evolution_all_models.png`**: Core mass fraction evolution for all models (comparative timeline)
- **`hydrogen_profiles_all_models.png`**: Final hydrogen profiles overlaid for all models

#### What the Script Does

**Data Processing:**
1. Loads final profile files containing internal stellar structure
2. Extracts mass fractions for hydrogen (X), helium (Y), and metals (Z)
3. For single models: Plots all three species vs. mass coordinate
4. For batch models: Focuses on hydrogen profiles and core evolution comparison

**Mass Coordinate System:**
- X-axis: Mass coordinate (m/M_total) from 0 (center) to 1 (surface)
- Y-axis: Mass fraction (0 to 1) for each chemical species

As a star evolves, its radius changes dramatically - a star can expand by factors of 10-100 during evolution. But the mass distribution within the star changes much more slowly.
Mass coordinate m/M_total = 0.2 always refers to 20% of the star's material and so it is much more age agnostic than actual radius. 
This allows for a much more universal and physically meaningful comparison of such features between stars. 

#### Interpretation

**Profile Features:**
- **Hydrogen (blue)**: Primary fuel, depleted in core, preserved in envelope
- **Helium (red)**: Nuclear burning product, concentrated where hydrogen was processed  
- **Metals (green)**: Heavy elements, largely unchanged by hydrogen burning

**Mixing Signatures:**
- **Sharp gradients**: Indicate composition discontinuities at mixing boundaries
- **Smooth transitions**: Show regions affected by convective mixing or overshooting
- **Plateau regions**: Chemically homogeneous zones due to efficient mixing

**Overshooting Effects:**
- **No overshooting**: Sharp composition boundaries, steep gradients
- **Strong overshooting**: Extended smooth composition profiles, larger chemically mixed regions
- **Intermediate overshooting**: Gradual transitions between core and envelope compositions

**Stellar Structure Information:**
- **Core boundary**: Where hydrogen drops to ~0 and helium peaks
- **Envelope composition**: Relatively unchanged from initial values
- **Transition zones**: Regions where burning and mixing compete

**Astrophysical Implications:**
- **Surface abundances**: What we observe spectroscopically
- **Core composition**: Determines next evolutionary phase
- **Mixing efficiency**: Affects stellar lifetimes and nucleosynthesis
- **Chemical evolution**: How stars contribute to galactic chemical enrichment




---




### `plot_timing.py` - Runtime Performance Analysis

#### Purpose
Plot runtime versus different features to see what makes MESA slow. 

#### Output
- **`runtime_3d_plot.png`**: 3D scatter plot showing runtime vs. mass, overshooting parameter, and scheme
- **`runtime_2d_plot.png`**: 2D plot with mass vs. metallicity, colored by runtime, sized by overshooting strength


#### What the Script Does

**Data Processing:**
1. Loads runtime data from `../run_timings.csv` (created during batch runs)
2. Extracts stellar parameters from model filenames:
   - Mass, metallicity, overshooting scheme, f_ov, f0 parameters
3. Creates visualization showing performance patterns


#### Interpretation

**Runtime Dependencies:**
- **Mass effects**: Higher mass stars typically run faster (fewer timesteps to main sequence termination)
- **Overshooting effects**: More complex overshooting schemes may increase computational cost
- **Metallicity effects**: Lower metallicity can affect convergence and timestep size
- **Numerical stability**: Some parameter combinations are computationally more challenging



---



## Reflection and Analysis Questions

After completing the batch runs and visualization exercises, consider these questions:

- How does overshooting efficiency affect stellar evolution differently for 2 solar mass versus 15 solar mass stars? When could it be considered '_more important_'?
- Which parameter combinations required the longest computational time, and what physical processes might explain this?
- How would you design an optimal parameter study to answer a specific research question while minimizing computational cost?
- What trade-offs exist between parameter space coverage and computational feasibility?
- What aspects of the batch processing workflow could be improved for larger-scale research applications?
- How could you validate your batch results against observational data?
- What uncertainties might affect conclusions drawn from parameter studies like these?



---



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
- Ensure your CSV file has the correct format (see `Lab1.csv`)
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

You are free to use these scripts however you like in the future. Some ideas:

- Edit plotting styles in the Python files
- Add new parameters to the CSV file and plot those
- Modify inlist generation in `make_batch.py` -- grids need not be linear, continious or square
- Create your own analysis scripts based on the provided examples

---
