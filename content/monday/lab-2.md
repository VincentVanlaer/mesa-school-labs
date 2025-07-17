# Monday MiniLab 2: Overshooting during core helium burning (CHeB)

## Overview

**A. Preparation**
* ~10 Minutes
* Adjusting the MESA inlist files to run until core helium depletion
* Creating a new file called *inlist_extra*, where we can vary our physics quickly

**B. Running different models until Terminal Age Core Helium Burning (TACHeB)**
* ~30 Minutes
* exploring how different physical assumptions change the evolution of a star and the structure of the convective core

**C. Bonus Task: Including additional plots**
* ~20 Minutes
* Getting familiar with pgstar and modifying it to show an additional plotting window
* Intestivate when convection zones in a star are formed

## A. Preparation

Now we are interested in studying how stars with and without core 
overshooting evolve during the CHeB and which impact it has. 

As a first step, we copy the folder from Lab1 and name it Lab2.
You can do this by hand or run in your terminal:

```
cp -r lab1 lab2
```

Before we start modifying the inlists such that we can model the 
further evolution of our $5\,M_\odot$ star, let us clean up the directory
and delete not needed files from our previous runs, such as the 
directories LOGS, photos, and png:

```
./clean
rm -r LOGS photos png
```

Alternatively, or if you want to be sure that everything is working properly,
you can download a cleaned folder [here](https://github.com/Daniel-Pauli/mesa-school-labs/blob/patch-1/content/monday/lab2.zip).

In lab1 we have calculated a $5\,M_\odot$ model with 
step overshooting having $f_\text{ov}=0.030$ and $f_{0\,\text{ov}}=0.005$ until core-hydrogen
depletion. The model should be saved as ``M5_Z0014_fov030_f0ov0005_TAMS.mod``
and should still be in your lab2 folder. To save computation time, 
and to avoid calculating the evolution to the TAMS several times,
we will be loading this saved model every time to explore 
different physical settings. 

If you did not finish lab1 or by accident overwrote your model during lab1. 
You can download the TAMS model [here](https://github.com/Daniel-Pauli/mesa-school-labs/blob/patch-1/content/monday/lab2/M5_Z0014_fov030_f0ov0005_TAMS.zip).

### inlist_project: star_job

To load a saved model, we need to modify our *inlist_project* 
in the *star_job* section. Since we do not need to start with
a pre-main-sequence model anymore, we need to delete or comment
out (by putting an "!" in front of the text) the following lines:

```fortran
  ! begin with a pre-main sequence model
    create_pre_main_sequence_model = .true.
  ! reducing the number of relaxation steps to decrease computation time
    pre_ms_relax_num_steps = 100
```

Note that you should not copy these code blocks. They are already in your *inlist_project*. 
Instead, you need to comment out these lines by yourself!
We also no longer need to save the model at the end of the run, 
meaning that we can also delete or comment out the following lines:

```fortran
  ! save a model and photo at the end of the run
    save_model_when_terminate = .true.
    save_photo_when_terminate = .true.
    save_model_filename = 'M5_Z0014_fov030_f0ov0005_TAMS.mod'
```

Furthermore, since we do want to start from a previously saved
model, we do not want to fix the initial timesteps and thus 
remove or comment out the lines: 

```fortran
  ! Set the initial time step to 1 year
    set_initial_dt = .true.
    years_for_initial_dt = 1d0
```
    
Now, we need to add lines that tell MESA to load a saved model.
Go to the MESA website and search for commands that allow us to load a saved model. 
In your inlist, load the model "M5_Z0014_fov030_f0ov0005_TAMS.mod".

{{< details title="Show hint 1" closed="true" >}}

Look in the *star_job* panel under *References and Defaults* in the  
[MESA documentation](https://docs.mesastar.org/en/24.08.1/reference/star_job.html)

{{< /details >}}

{{< details title="Show hint 2" closed="true" >}}

Can you find on the website any content that is related to **load** something?

{{< /details >}}


{{< details title="Show answer" closed="true" >}}

Add to your *star_job* section in the *inlist_project* the following lines:
```fortran
! loading the pre-saved 5 Msun model
    load_saved_model = .true.
    load_model_filename = 'M5_Z0014_fov030_f0ov0005_TAMS.mod'
```

{{< /details >}}
  

### inlist_project: controls

Now that we are done with modifying the *star_job* section, we 
also need to check if there are any controls that will cause 
issues when loading and running the model. 

The first controls that can be removed or commented out are, the ones defining 
the initial conditions at the beginning of the evolution:
	
```fortran
  ! starting specifications

    initial_mass = 5 ! in Msun units

    initial_z = 0.014 ! initial metal mass fraction

```
    
Moreover, we should change our stopping condition. In Lab 1, we
were only interested in the evolution until the TAMS. But now we
want to go to the end of core helium burning (CHeB), which we 
will define as core helium mass fraction < 1d-5. Replace the 
old stopping condition by the new one.

{{< details title="Show hint 1" closed="true" >}}
Look in the *controls* panel under *References and Defaults* in the 
[MESA documentation](https://docs.mesastar.org/en/24.08.1/reference/controls.html)

{{< /details >}}

{{< details title="Show answer" closed="true" >}}

Replace the lines:
```fortran
! stop when the center mass fraction of h1 drops below this limit
    xa_central_lower_limit_species(1) = 'h1'
    xa_central_lower_limit(1) = 1d-6
```

with 

```fortran
! stop when the center mass fraction of he4 drops below this limit
    xa_central_lower_limit_species(1) = 'he4'
    xa_central_lower_limit(1) = 1d-5
```

Alternatively, you can use the following shortcut:
```
! stop at the end of core helium burning 
    stop_at_phase_TACHeB = .true.
```

{{< /details >}}

If you want to make sure that all the changes you have made are correct,
you can quickly compile and run your model. If the pgstar window opens up,
everything is fine and you can stop the model. 

```
./clean && ./mk
./rn
```
To stop your model, you can press in the terminal ctrl+c. In case that does not work on your mac, try cmd+c.
    
### adding a new inlist file: inlist_extra

In the next step, we want to vary the input parameters of our
model calculations and the output files where the LOGS and png
files are saved. Because it can be quite messy, adding and
editing the various parameters in the *inlist_project* and 
*inlist_pgstar* at the same time, let us create a new inlist, 
in which we only have the controls that we want to edit for
both files. To do that, we can modify the *inlist* file. In 
the *controls* section, add the following lines:

```fortran
  ! adding an external file where we can add additional controls
    read_extra_controls_inlist(2) = .true.
    extra_controls_inlist_name(2) = 'inlist_extra'
```

This allows MESA to read *inlist_project* first, and then *inlist_extra*. Note that if the same item appears in both inlists, MESA adopts the last value it reads. 
    
Similarly, in the *pgstar* section in *inlist*, add:

```fortran
  ! adding an external file where we can add additional controls
    read_extra_pgstar_inlist(2) = .true.
    extra_pgstar_inlist_name(2) = 'inlist_extra'
```
    
So far the file *inlist_extra* does not exist, so 
let us create it. You can do that by typing in your 
terminal:

```
	touch inlist_extra
```
	
To tell MESA where to read the new controls, we need to add 
in *inlist_extra* a controls and a pgstar section:

```fortran
	&controls
	  ! Here we can add our controls
	   
	/ ! end of controls namelist
	
	&pgstar
	  ! Here we can edit stuff related to pgstar
	  
	/ ! end of pgstar namelist
	
```

Note, that you need to include also the additional empty line
at the end of the block, otherwise MESA will throw an error. 
Just for safety, let us see if everything worked, the model starts, and the
pgstar window opens again:

```
./rn
```
To stop your model, you can press in the terminal ctrl+c. In case that does not work on your mac, try cmd+c.

## B. Running different models until Terminal Age Core Helium Burning (TACHeB)

### Core helium burning without core overshooting
	
As a first run, we want to calculate the $5\,M_\odot$ model until
core helium depletion without including core overshoot. To 
be able to compare the output between the different models,
let us create for each run a separate output folder for the 
LOGS and the png files. To change the default storage folders
we can add in the *controls* section in the *inlist_extra*:

```fortran
  ! change the LOGS directory
    log_directory = 'output_no_overshoot/LOGS'
```

and in the *pgstar* section in the *inlist_extra*:

```fortran
  ! change the png directory
    Grid1_file_dir = 'output_no_overshoot/png' 
```

    
Before we start running the model without core overshooting
during core helium burning. Think about what you would expect.
Should the core grow, stay at the same size, or even recede 
and why do you think so?
    
Finally it is time to run the model! Go to your terminal,
load and run MESA:

```
./clean && ./mk
./rn
```
	
Look at your pgstar output. Especially at the upper right
plot depicting how much the convective core grows in mass.
How does the core evolve? Was it as you expected? Can you 
figure out why the core behaves as it does?

### Core helium burning with step overshooting

Now add some overshooting on top of the helium-burning
core to see how it impacts the evolution. For core helium
burning, use a moderate step overshooting,
namely $f_\text{ov} = 0.1$ and $f_{0,\,\text{ov}} = 0.005$. In lab1, we added
overshooting on top of the hydrogen burning core by 
using the following lines:

```fortran
  ! mixing
     overshoot_scheme(1) = 'step'
     overshoot_zone_type(1) = 'burn_H'
     overshoot_zone_loc(1) = 'core'
     overshoot_bdy_loc(1) = 'top'
     overshoot_f(1) = 0.3
     overshoot_f0(1) = 0.005
```

Let's add similar lines in the *controls* section 
in *inlist_extra*. 
Can you figure out how we need to modify
them to tell MESA that we also want an overshooting region
on top of the helium-burning core?

{{< details title="Show hint 1" closed="true" >}}

Since the first overshooting scheme is already used in the first set ``(1)``, we need to change it to ``(2)``
for all controls.

{{< /details >}}

{{< details title="Show hint 2" closed="true" >}}

Are the locations, types, and boundaries of the overshooting zone still correct? 
Can you find on the website other options where to allow overshooting? 
Check the controls for overshooting on [here](https://docs.mesastar.org/en/24.08.1/reference/controls.html). 

{{< /details >}}

{{< details title="Show answer" closed="true" >}}

In the end, you should have in the *controls* section of your *inlist_extra* lines that are similar to:
```fortran
! mixing
     overshoot_scheme(2) = 'step'
     overshoot_zone_type(2) = 'burn_He'
     overshoot_zone_loc(2) = 'core'
     overshoot_bdy_loc(2) = 'top'
     overshoot_f(2) = 0.1
     overshoot_f0(2) = 0.005
```

{{< /details >}}

Before we start the model, remember to change the output files
such that we are not overwriting the outputs from the last run.
We can do that in the *inlist_extra* by overwriting the directory
commands with:

```fortran
  ! change the LOGS directory
    log_directory = 'output_overshoot/LOGS'
    
  ! change the png directory
    Grid1_file_dir = 'output_overshoot/png' 
```

What do you expect to happen now? Will the core grow, stay at
the same level, or receed? 

Okay we are ready to go. Let us run the model:

```
./rn
```
	
Look again at how the convective core grows in mass. Does it
fit your expectations? Compare the maximum mass of the 
convective core to the case without overshooting. To do that
you can have a look at your pgstar files saved in 
``output_no_overshoot/png``. Are the maximum masses similar
or different and why?

{{< details title="Show answer" closed="true" >}}

Overshooting is very efficient in mixing additional fuel into the core, leading to a growth.

{{< /details >}}

If you look at the upper right plot, showing the evolution 
of the growing core, you should see some pulses where the core
mass grows and receeds again. That is strange. At the model
numbers where these pulses occur, can you see something happening
in the structure of the star in the Kippenhahn diagram?

{{< details title="Show answer" closed="true" >}}

In the Kippenhahn diagram, shown in the lower left corner of the pgstar windows, you should see 
that a convective region forms directly on top of the overshooting region. 
Alternatively, you can also in the mixing plot, shown in the lower right corner of the pgstar window,
that a convective region is forming every now and then on top of the overshooting region.
This phenomenon is called helium breathing pulses and occurs mostly in low and intermediate-mass stars
during core helium burning. The reason that this happens is due to the
convective core reaching into layers with a strong chemical gradient. When this happens, a
convective region forms on top of the core that is stable against overshooting, pushing down
the overshooting and the core mass. Numerically, the modeling of the convective boundaries in these regions
is challenging and has to do with the $\nabla_\text{rad}$ profile changing during the evolution, leading to
the formation of a convective region when reaching a local minimum. 
It is not clear if the helium breathing pulses are of physical or numerical nature. If you want to
read more about helium breathing pulses, you can check out these papers: [Castellani et al. 1985](https://ui.adsabs.harvard.edu/abs/1985ApJ...296..204C/abstract), [Constantino et al. 2016](https://ui.adsabs.harvard.edu/abs/2016MNRAS.456.3866C/abstract), [Salaris & Cassisi 2017](https://ui.adsabs.harvard.edu/abs/2017RSOS....470192S/abstract), [Paxton et al. 2018](https://ui.adsabs.harvard.edu/abs/2018ApJS..234...34P/abstract), and [Córsico & Althaus 2024](https://ui.adsabs.harvard.edu/abs/2024ApJ...964...30C/abstract) (their figure 1 nicely illustrates the impact of the breathing pules on the core helium burning time).

{{< /details >}}

### Limiting core overshooting in regions with strong chemical gradients

Now, let us consider the impact of a chemical gradient between the helium-burning core and the envelope as an additional stabilizing force.
This will reduce the size of the overshooting region and maybe help to prevent the core from growing into the unstable region.
In MESA while modeling overshooting, one can account for a stabilizing 
composition gradient in the calculations using different parameters. For instance, one could use the Ledoux criterion and semi-convective mixing or the Brunt-Väisälä  frequency (or buoyancy frequency), 
which is a measure of the stability of a fluid to vertical displacement as present in overshooting regions. For more information on different physical processes that can impact mixing regions, you can check out the MESA documentation. In this section, we will consider limiting the overshooting to regions where the Brunt-Väisälä frequency is low.

The Brunt is the frequency of buoyant oscillations. In convective regions, formally the Brunt is 0/negative (perturbations cause motion or growth rather than oscillation). One can think of this as analogous to a taut guitar string. in some sense higher Brunt means a more rigid (less convective) structure. Another way to think about this is to compare the buoyant frequency to the convective overturn frequency. The longer the buoyant frequency, the more likely that activity from the convective region can penetrate and mix with material just outside the convective boundary. The faster the buoyant frequency, the quicker the fluid can respond and stay stably stratified. 
By limiting the Brunt, one imposes that overshooting shouldn’t be present in regions where a perturbation will vibrate quickly rather than churn.

To turn on the frequency in MESA use the following lines in your *controls* section of your *inlist_extra*:

```fortran
   calculate_Brunt_B = .true.
   calculate_Brunt_N2 = .true.
```

Even when turned on, the default value for the threshold is set to ``0d0``. For our calculations, let's 
set this threshold to a higher value to prevent overshooting in regions
with a strong chemical gradient. In your *controls* section in your 
*inlist_extra* add:

```fortran
    overshoot_brunt_B_max = 1d-1   
```
    
and change the output directories to:

```fortran
  ! change the LOGS directory
    log_directory = 'output_overshoot_brunt/LOGS'
```
    
and:

```fortran
  ! change the png directory
    Grid1_file_dir = 'output_overshoot_brunt/png'
```

Let us have a look, what MESA will tell us:

```
./rn
```
	
Look again at the plot showing the growth of the convective
core mass. How does it compare to to the model with the 
strong overshooting and the model without overshooting? Do you 
have an idea why these differences appear?

{{< details title="Show answer" closed="true" >}}

The newly included physics quickly removes the growth of the core by overshooting 
due to the strong chemical gradient between the core and the H-burning shell. 
When the stabilizing gradient is hit, overshooting is suppressed. 
Therefore, the final convective mass of the helium core of this star is quite similar 
to that of the model without overshooting.

{{< /details >}}


The problem of breathing pulses is an ongoing issue with no real solution. By limiting the Brunt-Väisälä frequency (or Brunt factor), we are effectively suppressing overshooting in regions with strong chemical gradients, where even small instabilities are more likely to trigger pulsations than induce mixing. An alternative way to treat these pulses could be to use another criterion for determining convective boundaries. However, resolving the location of the convective boundary is beyond the scope of our lab, but we encourage you to explore other mixing options.

## C. Bonus Task: Including additional plots

In the previous exercises, we have encountered that if we use overshooting during 
core helium burning, the helium breathing pulses are triggered. Here, we would 
like to investigate a bit further when and why MESA turns specific regions into
 convective regions and when not. Following the Schwarzschild criterion, a zone 
 in a star becomes convective if $\nabla_\text{rad} > \nabla_\text{ad}$. 
So let's modify our *inlist_pgstar* such that we can see how the gradients evolve.

At first, we need to make more space for an additional plot. In the *inlist_pgstar* 
You can see that the grids the plots are shown on have 3 columns and 2 rows:
```fortran
	Grid1_num_cols = 3 ! divide plotting region into this many equal width cols
	Grid1_num_rows = 2 ! divide plotting region into this many equal height rows
```
For now, we do not need to add more rows or columns, the history panel shows the
growth of the convective core is quite large anyways, so let us make it smaller. Can
you identify the code block in *inlist_pgstar* that is telling the grid where to plot the history panel of convective core mass? If yes, change its column width from
2 to 1.
 
{{< details title="Show hint 1" closed="true" >}}

The quantity "Grid1_plot_name" tells pgstar which plot we want to assign a position and width.

{{< /details >}}

{{< details title="Show hint 2" closed="true" >}}

The history panel showing the growth of the convective core is not a default one 
and might have a different name than "conv_mass_core".

{{< /details >}}


{{< details title="Show hint 3" closed="true" >}}

The position of a plot is set by "Grid1_plot_row" and "Grid1_plot_col", while its 
size is determined by "Grid1_plot_rowspan" and "Grid1_plot_colspan".

{{< /details >}}

{{< details title="Show answer" closed="true" >}}

```fortran
	Grid1_plot_name(5) = 'History_Panels1'
	Grid1_plot_row(5) = 1          ! number from 1 at top
	Grid1_plot_rowspan(5) = 1       ! plot spans this number of rows
	Grid1_plot_col(5) =  2          ! Number from 1 at left
	Grid1_plot_colspan(5) = 1       ! plot spans this number of columns
```

{{< /details >}}

To test if your changes yield the correct result, start your model and see if the
 pgstar window looks as expected.

```
./rn
```

To investigate how the adiabatic and radiative temperature gradients change in the
star, we need to add a profile panel. This can be done by adding the following code
in the upper part of your *inlist_pgstar*:

```fortran
	! Profile Panel
	Profile_Panels1_win_flag = .false. ! we do not want an extra window to open up.

	Profile_Panels1_win_width = 10
	Profile_Panels1_win_aspect_ratio = 1.1

	Profile_Panels1_title = ''

	Profile_Panels1_xaxis_name = 'mass'

	Profile_Panels1_num_panels = 1
	Profile_Panels1_yaxis_name(1) = ''
	Profile_Panels1_other_yaxis_name(1) = ''
```
as you can see the "Profile_Panels1_yaxis_name" and "Profile_Panels1_yaxis_name" are left blank so far. This is where we want to add the individual gradients. Unfortunately, we do not have an output yet for them. The Profile_Panels access the parameters that are used in the profile_cloumns.list. Open *my_profile_columns.list* and search for the adiabatic and radiative temperature gradients and comment them out.

{{< details title="Show answer" closed="true" >}}

The adiabatic temperature gradient in MESA is called "grada", and the radiative temperature gradient is "gradr".  

{{< /details >}}

Now that these are saved, pgstar can access them. So let's include them using
```fortran
	Profile_Panels1_yaxis_name(1) = 'grada'
	Profile_Panels1_other_yaxis_name(1) = 'gradr'
```

And lastly, before we can investigate how these gradients evolve in our models,
we need to tell the grid, that we now want to plot a 6th plot and where to put it.
To add another plot, we need to change
```fortran
	Grid1_num_plots = 5 ! <= 10
```
to 
```fortran
	Grid1_num_plots = 6 ! <= 10
```

Given your experience in resizing the history panel. Can you add a code block telling the grid to plot the profile plot in the upper right corner?

{{< details title="Show hint 1" closed="true" >}}

The "Grid1_plot_name" of the profile plot in our case is "Profile_Panels1".

{{< /details >}}

{{< details title="Show hint 2" closed="true" >}}

This is the 6th plot we add, so make sure that you also use it as (6).

{{< /details >}}


{{< details title="Show answer" closed="true" >}}

```fortran
	Grid1_plot_name(6) = 'Profile_Panels1'
	Grid1_plot_row(6) = 1          ! number from 1 at top
	Grid1_plot_rowspan(6) = 1       ! plot spans this number of rows
	Grid1_plot_col(6) =  3          ! Number from 1 at left
	Grid1_plot_colspan(6) = 1       ! plot spans this number of columns  
```

{{< /details >}}

You can now start your model and check if the plot shows up.
```
./rn
```
As you might see, the history panels and the profile panels are overlapping. For a better representation, you can adjust their paddings at the top, left, right, and bottom via 
```fortran
	Grid1_plot_pad_top(6) = x     
	Grid1_plot_pad_bot(6) = x     
	Grid1_plot_pad_left(6) = x    
	Grid1_plot_pad_right(6) = x   
```
Play around with the values, restart your model to check what the panels look like,
until you find a good fit on your computer. 

{{< details title="Show answer" closed="true" >}}

In our case, a good plot was found using:
```fortran
	Grid1_plot_pad_top(5) = 0.03     
	Grid1_plot_pad_bot(5) = 0.03     
	Grid1_plot_pad_right(5) = 0.03     

	Grid1_plot_pad_top(6) = 0.03     
	Grid1_plot_pad_bot(6) = 0.03     
	Grid1_plot_pad_left(6) = 0.03     
```

{{< /details >}}

Maybe some of you already noted, but the gradients scale differently, which makes identifying regions where convection should occur ($\nabla_\text{rad} > \nabla_\text{ad}$) very hard. This can be quickly fixed by adding the same minima and maxima for both axes, like this:
```fortran
	Profile_Panels1_ymin(1) = 0 
	Profile_Panels1_ymax(1) = 0.5
	Profile_Panels1_other_ymin(1) = 0 
	Profile_Panels1_other_ymax(1) = 0.5
```

Now everything should be good. Modify your *inlist_extra* and investigate how the gradients evolve in the case without overshooting, with overshooting, and using the brunt factor. Can you see why the Brunt factor is more like a workaround and not a real solution to the problem?

