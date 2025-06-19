# Monday MaxiLab 2: Overshooting during core helium burning (CHeB)


### Preparation

Now we are interested in studying how stars with and without core 
overshooting evolve during the CHeB and which impact it has. 

As a first step, we copy the folder from Lab1 and name it Lab2.
You can do this by hand or run in your terminal::

```
	cp -r lab1 lab2
```

Before we start modifying the inlists such that we can model the 
further evolution of our 5Msun star, lets clean up the directory
and delete not needed files from our previous runs, such as the 
directories LOGS, photos, and png::

```
	./clean
	rm -r LOGS photos png
```

Alternatively, or if you want to be sure that everything is working properly,
you can download a cleaned folder [here]().

In the previous Lab1 we have calculated a 5Msun model with 
step overshooting having f=0.030 and f0=0.005 until core-hydrogen
depletion. The model should be saved as ``M5_Z0014_fov030_f0ov0005_TAMS.mod``
and should be still in your lab2 folder. To save computation time, 
and to avoid calculating the evolution to the TAMS several times,
we will load the saved model every time when we will explore 
different physical settings. 

If you did not finish lab1 or by accident overwrote your model during lab1. 
You can download the TAMS model [here](https://github.com/Daniel-Pauli/mesa-school-labs/blob/patch-1/content/monday/lab2/M5_Z0014_fov030_f0ov0005_TAMS.mod).

inlist_project: star_job
------------------------

To load a saved model, we need to modify our *inlist_project* 
in the *star_job* section. Since we do not need to start with
a pre-main-sequence model anymore, we need to delete or comment
out (by putting an "!" infront of the text) the following lines::

```
  ! begin with a pre-main sequence model
    create_pre_main_sequence_model = .true.
  ! reducing the number of relaxation steps to decrease computation time
    pre_ms_relax_num_steps = 100
```

We also do no longer need to save the model at the end of the run, 
meaning that we can also delete or comment out the following lines::

```
  ! save a model and photo at the end of the run
    save_model_when_terminate = .true.
    save_photo_when_terminate = .true.
    save_model_filename = 'M5_Z0014_fov030_f0ov0005_TAMS.mod'
```

Furthermore, since we do want to start from a previously saved
model, we do not want to fix the initial timesteps and thus 
remove or comment out the lines:: 

```
  ! Set the initial time step to 1 year
    set_initial_dt = .true.
    years_for_initial_dt = 1d0
```
    
Now, we need to add lines that tell MESA to load a saved model.
Can you go to the MESA website and search for commands that allow
us to load a saved model?

<details class="hx-border hx-border-blue-200 dark:hx-border-blue-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-blue-100 dark:hx-bg-neutral-800 hx-text-blue-900 dark:hx-text-blue-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Show hint 1</em>
</summary>

Look in the *star_job* panel under *References and Defaults* in the  
[MESA documentation](https://docs.mesastar.org/en/24.08.1/reference/star_job.html)

</details>

<details class="hx-border hx-border-blue-200 dark:hx-border-blue-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-blue-100 dark:hx-bg-neutral-800 hx-text-blue-900 dark:hx-text-blue-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Show hint 2</em>
</summary>

Can you find on the website any content that is related to **load** something?

</details>

<details class="hx-border hx-border-green-200 dark:hx-border-green-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-green-100 dark:hx-bg-neutral-800 hx-text-green-900 dark:hx-text-green-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Show answer</em>

Add to your *star_job* section in the *inlist_project* the following lines::
```
! loading the pre-saved 5Msun model
    load_saved_model = .true.
    load_model_filename = 'M5_Z0014_fov030_f0ov0005_TAMS.mod'
```

</details>
  

inlist_project: controls
------------------------

Now that we are done with modifying the *star_job* section, we 
also need to check if there are any controls that will cause 
issues when loading and running the model. 

The first controls that can be removed or commented out are, the ones defining 
the initial conditions at the beginning of the evolution::
	
```
  ! starting specifications

    initial_mass = 5 ! in Msun units

    initial_z = 0.014 ! initial metal mass fraction

```
    
Moreover, we should change our stopping condition. In Lab 1, we
were only interested in the evolution until the TAMS. But now we
want to go to the end of core helium burning (CHeB), which we 
will define as core helium mass fraction < 1d-5. Replace the 
old stopping condition by the new one.

<details>
<summary>Show hint 1</summary>

Look in the *controls* panel under *References and Defaults* in the 
[MESA documentation](https://docs.mesastar.org/en/24.08.1/reference/controls.html)

</details>

<details>
<summary>Show answer</summary>

Replace the lines::
```
! stop when the center mass fraction of h1 drops below this limit
    xa_central_lower_limit_species(1) = 'h1'
    xa_central_lower_limit(1) = 1d-6
```

with 

```
! stop when the center mass fraction of he4 drops below this limit
    xa_central_lower_limit_species(1) = 'he4'
    xa_central_lower_limit(1) = 1d-5
```

Alternatively, you can use the following shortcut::
```
! stop at the end of core helium burning 
    stop_at_phase_TACHeB = .true.
```

</details>

If you want to make sure that all the changes you have made are correct,
you can quickly compile and run your model. If the pgstar window opens up,
everything is fine and you can stop the model. 

```
	./clean && ./mk
	./rn
```
To stop your model, you can press in the terminal ctrl+c for a linux or cmd+c for a mac.
    
adding a new inlist file: inlist_extra
--------------------------------------

In the next step, we want to vary the input parameters of our
model calculations and the output files where the LOGS and png
files are saved. Because it can be quite messy, adding and
editing the various parameters in the *inlist_project* and 
*inlist_pgstar* at the same time, lets create a new inlist, 
in which we only have the controls that we want to edit for
both files. To do that, we can modify the *inlist* file. In 
the *controls* section, add the following lines::

```
  ! adding an external file where we can add additional controls
    read_extra_controls_inlist(2) = .true.
    extra_controls_inlist_name(2) = 'inlist_extra'
```

This allows MESA to read *inlist_project* first, and then *inlist_extra*. 
    
Similarly, in the *pgstar* section in *inlist*, add::

```
  ! adding an external file where we can add additional controls
    read_extra_pgstar_inlist(2) = .true.
    extra_pgstar_inlist_name(2) = 'inlist_extra'
```
    
So far the file *inlist_extra* does not exist, so 
lets create it. You can do that by typing in your 
terminal::

```
	touch inlist_extra
```
	
To tell MESA where to read the new controls, we need to add 
in *inlist_extra* a controls and a pgstar section::

```
	&controls
	  ! Here we can add our controls
	   
	/ ! end of controls namelist
	
	&pgstar
	  ! Here we can edit stuff related to pgstar
	  
	/ ! end of pgstar namelist
	
```

Note, that you need to include also the additional empty line
at the end of the block, otherwise MESA will throw an error. 
Just for safety, lets see if everything worked, the model starts and the
pgstar window opens again:

```
	./rn
```
To stop your model, you can press in the terminal ctrl+c for a linux or cmd+c for a mac.

Running different models until Terminal Age Core Helium Burning (TACHeB)
======================================

Core helium burning without core overshooting
--------------------------------------
	
As a first run, we want to calculate the 5Msun model until
core helium depletion without including core overshoot. To 
be able to compare the output between the different models,
lets create for each run a separate output folder for the 
LOGS and the png files. To change the default storage folders
we can add in the *controls* section in the *inlist_extra*::

```
  ! change the LOGS directory
    log_directory = 'output_no_overshoot/LOGS'
```

and in the *pgstar* section in the *inlist_extra*::

```
  ! change the png directory
    Grid1_file_dir = 'output_no_overshoot/png' 
```

    
Before we start running the model without core overshooting
during core helium burning. Think about what you would expect.
Should the core grow, stay at the same size, or even receed 
and why do you think so?
    
Finally it is time to run the model! Go to your terminal,
load and run MESA::

```
	./clean && ./mk
	./rn
```
	
Look at your pgstar output. Especially at the upper right
plot depicting how much the convective core grows in mass.
How does the core evolve? Was it as you expected? Can you 
figure out why the core behaves as it does?

Core helium burning with step overshooting
-----------------------------------------------

Now lets add some overshooting on top of the helium burning
core to see how it impacts the evolution. For core helium
burning, lets use a moderate step overshooting,
namely f_ov = 0.1 and f0_ov = 0.005. In lab1, we added
overshooting on the top of the hydrogen burning core by 
using the following lines::

```
  ! mixing
     overshoot_scheme(1) = 'step'
     overshoot_zone_type(1) = 'burn_H'
     overshoot_zone_loc(1) = 'core'
     overshoot_bdy_loc(1) = 'top'
     overshoot_f(1) = 0.3
     overshoot_f0(1) = 0.005
```

Let's add similar lines in the *controls* section 
in *inlist_extra*. Can you figure out how we need to modify
them to tell MESA that we want a second overshooting region
on top of the helium burning core?

<details>
<summary>Show hint 1</summary>

Since the first overshooting scheme is already used in the first set ``(1)`` we need to change them to ``(2)``
for all controls.

</details>

<details>
<summary>Show hint 2</summary>

Are the locations, types and boundaries of the overshooting zone still correct? 
Can you find on the website other options where to allow overshooting? 
Check the controls for overshooting on [here](https://docs.mesastar.org/en/24.08.1/reference/controls.html). 

</details>

<details>
<summary>Show answer</summary>

In the end you should have in the *controls* section of your *inlist_extra* lines that are similar to::
```
! mixing
     overshoot_scheme(2) = 'step'
     overshoot_zone_type(2) = 'burn_He'
     overshoot_zone_loc(2) = 'core'
     overshoot_bdy_loc(2) = 'top'
     overshoot_f(2) = 0.1
     overshoot_f0(2) = 0.005
```

</details>

Before we start the model, remember to change the output files
such that we are not overwriting the outputs from the last run.
We can do that in the *inlist_extra* by overwriting the directory
commands with::

```
  ! change the LOGS directory
    log_directory = 'output_overshoot/LOGS'
    
  ! change the png directory
    Grid1_file_dir = 'output_overshoot/png' 
```

What do you expect to happen now? Will the core grow, stay at
the same level, or receed? 

Okay we are ready to go, lets run the model::

```
	./rn
```
	
Look again at how the convective core grows in mass. Does it
fit your expectations? Compare the maximum mass of the 
convective core to the case without overshooting. To do that
you can have a look at your pgstar files saved in 
``output_no_overshoot/png``. Are the maximum masses similar
or different and why?

<details>
<summary>Show answer</summary>

Overshooting is very efficient in mixing additional fuel into the core, leading to a growth.

</details>

If you look at the upper right plot, showing the evolution 
of the growing core, you should see some pulses where the core
mass grows and receeds again. That is strange. At the model
numbers where these pulses occur, can you see something happening
in the structure of the star in the Kippenhahn diagram?

<details>
<summary>Show answer</summary>

You should see that a convective region forms directly on top of the overshooting region. 
This phenomenon is called helium breathing pulses and occurs mostly in low and intermediate
mass stars occuring during core helium burning. The reason that this happens is due to the
convective core reaching into layers with a strong chemical gradient. When this happens, a
convective region forms on top of the core that is stable against overshooting, pushing down
the overshooting and the core mass. Numerically, the modeling of the convective boundaries in these regions
is challenging and has to do with the $\nabla_\text{rad}$ profile changing during the evolution leading to
the formation of with the formation of the convective region forming when reaching a local minimum. 
It is not clear if the helium breathing pulses are of physical or numerical nature. If you want to
read more about helium breathing pulses, you can check out these papers: [Castellani et al. 1985](https://ui.adsabs.harvard.edu/abs/1985ApJ...296..204C/abstract), [Constantino et al. 2016](https://ui.adsabs.harvard.edu/abs/2016MNRAS.456.3866C/abstract), [Salaris & Cassisi 2017](https://ui.adsabs.harvard.edu/abs/2017RSOS....470192S/abstract), [Paxton et al. 2018](https://ui.adsabs.harvard.edu/abs/2018ApJS..234...34P/abstract), and [Córsico & Althaus 2024](https://ui.adsabs.harvard.edu/abs/2024ApJ...964...30C/abstract) (their figure 1 nicely illustrates the impact of the breathing pules on the core helium burning time).


One thing that we have been ignoring sofar
in our treatment of overshooting is the impact of a chemical gradient as the one between the helium 
burning core and the envelope as an additional stabilizing force, reducing the size of the overshooting region.
Resolving where the convective boundary lies is way beyond the scope of our lab, but we encourage 
you to explore other mixing options. 


</details>

Limiting core overshooting in regions with strong chemical gradients
--------------------------------------------------------------------

In MESA while modeling overshooting, one can account for a stabilizing 
composition gradient in the calculations using the Brunt-Vaisala frequency.
This is turned on in MESA by default::

```
   calculate_Brunt_B = .true.
   calculate_Brunt_N2 = .true.
```

However, the threshold is set to ``0d0``. For our calculations, let's 
set this threshold to a higher value to prevent to overshoot in regions
with a strong chemical gradient. In your *controls* section in your 
*inlist_extra* add::

```
    overshoot_brunt_B_max = 1d-1   
```
    
and change the output directories to::

```
  ! change the LOGS directory
    log_directory = 'output_overshoot_brunt/LOGS'
```
    
and::

```
  ! change the png directory
    Grid1_file_dir = 'output_overshoot_brunt/png'
```

Lets have a look, what MESA will tell us::

```
	./rn
```
	
Look again at the plot showing the growth of the convective
core mass. How does it compare to to the model with the 
strong overshooting and the model without overshooting? Do you 
have an idea why these differences appear?

<details>
<summary>Show answer</summary>

The new included physics quickly remove the growth of the core by overshooting 
due to the strong chemical gradient between the core and the H-burning shell. 
When the stabilizing gradient is hit, overshooting is suppressed. Therefore, 
the final convective mass of the helium core of this star is quite similar 
to that one of the model without overshooting.


</details>
