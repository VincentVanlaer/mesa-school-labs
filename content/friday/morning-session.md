
# MESA@Leuven Best Practices Lab — Convergence Testing

In this brief morning lab session, we will go over best practices for solving partial differential equations numerically, specifically in the context of the MESA Stellar Evolution Code.

The lecture slides can be found at [this repository, to be updated soon](https://broken-url.com). 

Solutions can be found at [this repository, to be updated soon](https://broken-url.com). 

## Lab Overview: 
When solving a (partial) differential equation numerically, you are essentially approximating a _derivative_ as a _difference_. 
For a quantity $y$ which varies with some coordinate $x$, this resembles the following:

$$ \frac{\partial y}{\partial x} \approx \frac{\Delta y}{\Delta x} = \frac{y[i+1] - y[i]}{x[i+1] - x[i]}$$

This is a "forward-difference," since it evaluates the difference between y at a step forward, $i+1$, and $y$ at a given step, $i$, and using that to approximate the derivative at step $i$. In practice, modern numerical techniques are just _slightly_ fancier ways of approximating a derivative as a difference between zones or between times, and then solving the set of equations corresponding to the values at each point. 

How do we know this is a good approximation? Without diving deep into the formal theory of numerical errors, let's note that a derivative is defined by taking the limit of the slope, $\left(f(x + h) - f(x)\right)/h$, as $h$ approaches 0: 

$$
f'(x) =\lim _{h \rightarrow 0} \frac{f(a+h)-f(a)}{(a+h) - (a)}
$$

So, the essential question is: "Are we in the limit of small $h$ ?"

When we solve the same equations on a finer and finer grid, and find that the answers do not change for the quantities we care about, we call this "converged" or "numerically converged." 

We now turn to exploring this in the context of the MESA stellar evolution code. This will be broken up in 3 mini-mini-labs: 

In **Mini-mini lab 1**, we will explore changing resolution in space and time. In **Mini-mini lab 2**, we will briefly discuss what to do when a resolution test _fails_. 
In **Mini-mini lab 3**, we will explore changing physical approximations within reasonable model uncertainties. Though not explicitly about numerical resolution testing, the third task is likewise **testing the numerical assumptions we are making in modeling the star as a sphere with finite shells**, so it is still a relevant aspect of convergence testing for astrophysical simulations. 

## MESA-specific background

### Lagrangian Mesh 
In the equations MESA solves, the fundamental spatial coordinate is made up of concentric shells each with a given mass. This is often referred to as the "mesh", which is broken up into "zones" (sometimes referred to as "cells" or "shells" or "mesh points"). The mass per zone $dm$ can vary, under the constraint that $\sum_i(dm_i)=M_* - m_\mathrm{IB}$ where $M_*$ is the star mass and $m_\mathrm{IB}$ is the mass inside the model inner boundary, which is 0 for most uses of MESA. The indexing is such that zone `1` corresponds to the surface of the star, and zone `nz` corresponds to the center of the star (or inner boundary). 

To help enforce that the zones are small enough that we are in fact "in the limit of small $h$", at each timestep, MESA can "adaptively" split and merge zones in order to achieve some tolerances in how various quantities vary from zone to zone. However, in choosing a mesh, MESA is guessing at what consitutes "small $h$". 

We can make MESA make better guesses, and we must always check it for errors. To change how MESA discretizes its mesh, we can do 3 things: 

S1) We can tell MESA to increase or decrease the number of zones, e.g. take whatever it thinks the mesh should be and (double? triple? 10x? halve?) the number of zones. This is controlled by setting `mesh_delta_coeff` (`=1` by default). A smaller value means more grid points, with less delta (difference) between them. A larger value means fewer grid points, with larger allowed "delta" between them. 
   
S2) We can also tell MESA to increase or decrease the tolerance for various physical targets directly. For example, perhaps MESA wants to have at most a relative change of 50% in density from zone `i` to zone `i+1`, and perhaps we think that's not good enough; we can specify that we want only 10% variations (Though, note that in this specific example you may end up with a TON of mesh points, because the density varies by tens of orders of magnitude between the core and the surface). There are _many_ controls for this; see `$MESA_DIR/star/defaults/controls.defaults` under the header
   ```fortran
   ! mesh adjustment   
   ! ===============
   ```
   Or the equivalent [on the MESA documentation website](https://docs.mesastar.org/en/latest/reference/controls.html#mesh-adjustment)

S3) We can create our own custom mesh scheme in `src/run_star_extras.f90`. We may turn to this as a bonus task, time permitting.

### Adaptive Timesteps

MESA is an implicit code, meaning it chooses its timestep adaptively and iterates until it achieves a solution within specified tolerances (i.e. specified differences between the right-hand-side and left-hand-side of the equations it's solving, as other controls on how much one model can deviate from one timestep to another). If the errors are too large in a given timestep, then MESA will cut the timestep in an attempt to get closer to "the limit of small $h$" (where now $h$ represents an increment in time $dt$). 

However, like choosing a mesh, MESA is guessing at what consitutes "small $h$". To change how MESA selects its timestep, we can likewise have a few options: 

T1) We can tell MESA to multiply the timestep it originally selects by a `time_delta_coeff`, analogous to `mesh_delta_coeff` (`=1` by default). Like with mesh, a smaller value means finer sampling in time, with less delta (difference) between them. A larger value means coarser sampling in time, with larger allowed "delta" between them. 
   
T2) We can tell MESA to increase or decrease the tolerance for various physical targets directly, in the `&controls` section of the inlist. Note that at different evolutionary phases, different tolerances may be setting the timestep. 
```fortran
   ! timestep controls
   ! =================
```
A broad control that's often used is `varcontrol_target` which specifies how much the model should deviate (defined with a broad metric encompassing a handful of physical quantities) from timestep to timestep. 
A summary of these may also be found [on the MESA documentation website](https://docs.mesastar.org/en/latest/reference/controls.html#timestep-controls)

T3) We can also tell MESA to cut or increase the timestep in `src/run_star_extras.f90` via user-defined criteria, especially in the `extras_check_model` routine, by directly manipulating the `s% dt` in the star info structure. 

# Mini-mini Lab 1: Spatial and Temporal Resolution testing

Let's set up an example that illustrates (1) the importance of testing resolution and (2) how _bad_ the default resolution in MESA is for certain regimes. 
In general, we cannot emphasize enough that these labs, the `test_suite`, and the basic `$MESA_DIR/star/work` directory are NOT converged numerically. 

Let's start as close to MESA defaults as possible. Copy a clean work directory and enter it:

```bash
cp -r $MESA_DIR/star/work ./work_res
cd work_res
```

The default work directory takes a $15M_\odot$ star and evolves it until ZAMS. In the massive star community, a lot of attention recently has been given to stellar winds, binarity, and other physics which may impact the properties of the H-rich envelope (much of which we've discussed this week). Let's evolve that model until it's later along its core He burning phase. 

First, so that everyone can easily share their last HR diagram with eachother at the table, add the following to the `&star_job` section of `inlist_project`: 

```fortran
pause_before_terminate = .true.
```

Let's also start on the main sequence, to save us a minute or two of runtime. Add the following to the `&star_job` section of `inlist_project`: 
```fortran
create_pre_main_sequence_model = .false. ! previously .true. 
```

To stop during core He burning, change the following in the  `&controls` section of `inlist_project`: 
```fortran
stop_near_zams = .false. ! previously .true.
```
and 
```fortran
xa_central_lower_limit_species(1) = 'he4' ! previously 'h1'
xa_central_lower_limit(1) = 2d-1          ! previously 1d-3
```

Though not strictly necessary, let's have the history be output every timestep. Add the following to the `&controls` section of your `inlist_project`: 
```fortran 
history_interval = 1 
```

Now we are ready for the resolution test. It is often good practice to change your time and mesh resoltion together, though in principle these can be varied independently. Today we will use methods S1/T1. We mention the other methods above in order to remind the user that there are lots of good ways to do things in MESA depending on your problem. 

Have each member of your table select a unique `*_delta_coeff` from the set `[0.3, 0.5, 1, 2]`. Make sure everyone at your table chooses a different value. 

**NOTE: For those with slower computers, you should choose larger values of `*_delta_coeff`. ** If you have a very fast computer, feel free to try other values, but it's recommended not to go below 0.2 for the sake of time in this lab block (or, if you do, be prepared to kill the run). 

To change your resolution, add the following controls to your inlist, replacing `VALUE` with the appropriate value: 

```fortran
! timesteps
time_delta_coeff = YOUR VALUE ! 1 by default
max_model_number = 2000 ! off by default -- putting a cap here in case things get too crazy

! mesh
mesh_delta_coeff = YOUR VALUE ! 1 by default
max_allowed_nz = 16000 ! default 8000
```

Finally, it will be helpful to see what's actually going on in the model as timesteps are taken. 
In inlist_pgstar, add the following line to produce a Kippenhahn Diagram: 

```fortran 
kipp_win_flag = .true.
```

With that, you're ready to run! In the terminal, from your working directory, clean make and run! 

```bash
./clean && ./mk && ./rn 
```

Watch the run evolve, and watch the runs of others at your table. Compare the HR diagram that pops up with those produced by people at your table with a different mesh_delta_coeff / time_delta_coeff. Do your diagrams agree? Disagree? Which agree better? 

For comparison to others at the table and to other runs you do in subsequent Mini-mini-labs, record the final **Mass**, **Radus**, **$T_\mathrm{eff}$**, **Luminosity**, and **star age**.  If you want to do other runs yourself, or if you are doing this lab asynchronously outside of the MESA@Leuven school, you can also save your LOGS folder to a safe location where it won't be overwritten. 

If something looks funky, maybe inspect the Kippenhahn diagram...

==KEY TAKEAWAY: DO NOT USE DEFAULTS AS A STARTING POINT FOR SCIENCE RUNS UNLESS YOU HAVE DONE ROBUST RESOLUTION TESTING!==

# Mini-mini lab 2: Resolution test failed! What do we do?  

There is no generalized procedure for a failed resolution test, but it is a sign that you need to change your setup. In the most extreme cases, you may need an entirely new set of inlist parameters that modify the MESA defaults quite heavily. It may be a good idea to post to the MESA users list, in case someone else has dealt with this before.  

In this case, inspecting the Kippenhahn diagram has shown that in some runs, especially at high resolution there are convective zones popping in and out of existence near the edge of the core which are a numerical artifact of the mixing length theory prescription. You can try to get rid of these by pruning the convective gaps, setting overshooting / core boundary mixing, or other techniques. The one we will try here is turning on `convective_pre_mixing`, which was introduced in MESA V  (Paxton et al 2019) in order to resolve discrepancies between gradients near convective boundaries especially in massive stars. (See also the `predictive_mixing` option introduced in MESA IV, Paxton et al 2018). 

Using the same inlists as the end of your previous run, turn on convective pre-mixing by adding the following to the `&controls` section of `inlist project`: 

```fortran
  ! mixing
  do_conv_premix = .true.
  use_Ledoux_criterion = .true.
```
 
Make sure to keep your unique `*_delta_coeff` from the set `[0.3, 0.5, 1, 2]` as well as the stopping condition during core He burning.
Run the model again, and watch the HR diagram and Kippenhahn diagram evolve this time.  


```bash
./clean && ./mk && ./rn 
```

Again, record the final **Mass**, **Radus**, **$T_\mathrm{eff}$**, **Luminosity**, and **star age**. Likewise, you can also save your LOGS folder to a safe location where it won't be overwritten. What has changed? Do the results look better? Discuss briefly at your table why this might be. 

# Mini-mini lab 3: Varying 1D 'physics' prescriptions

It is also important to remember that discretizing differential equations onto a finite grid in space and time is not the only approximation or engineering technique that we employ in 1D stellar evolution modeling (e.g. with MESA). If you have a science result, you want to be sure that it's robust to your inputs, numerical choices, _and_ modeling assumptions within physical reason. 

A very central part of stellar evolution modeling is the treatment of energy transport, and specifically the balance between radiative diffusion versus convection. In fact the failed resolution test was in part mediated by changing how we handle the convective (in)stability criterion. 

MESA and most stellar evolution software instruments treat convection via the Mixing Length Theory (MLT) prescription (Bohm-Vitense 1958; see recent review by Joyce & Tayar 2023). There have been discussions of the Mixing Length Theory already this week. I'll also point the interested lab-scholar to extensive content on MLT in the context of supergiant envelopes in the last year's [MESA Down Under 2024 Tuesday Lab](https://sites.google.com/view/massive-stars-mesa-down-under/welcome?authuser=0), especially the slides and background text surrounding Minilab 2. 

At heart, the assumption of mixing length theory is that the characteristic length scale for convective transport (called the mixing length, $\ell$ ) is a multiple of the Pressure Scale Height $H$: 

$$
\ell = \alpha_\mathrm{MLT} H, 
$$ 

where $\alpha_\mathrm{MLT}$ is the mixing length coefficient. Higher values of $\alpha_\mathrm{MLT}$ mean that your prescription for convection is more efficient at carrying flux, lower values correspond to lower efficiencies. 

This is often calibrated to the sun, which depending on the stellar evolution code, atmosphere tables, and many many other factors often gives a values somewhere around $\alpha_\mathrm{MLT}=1.8$. However, this is a choice, and has systematic consequences which impact the stellar radius and other quantities of interest especially when the outer stellar envelope is convective. Evolved massive stars often show evidence of higher values of $\alpha_\mathrm{MLT}$ (really, the evidence is hotter $T_\mathrm{eff}$/smaller radii than most models with lower $\alpha_\mathrm{MLT}$ predict). 

Let's leave the resolution testing directory, but copy your setup from minilab 2 to a new directory to play with the mixing length (and remove old logs files, photos, executables, etc):  
```bash
cd .. 
cp -r work_res work_alpha
cd work_alpha
rm -r LOGS
rm -r png
rm -r photos/*
```

Let's revert to the default resolution here, having decided that with CPM on it's "okay enough for our lab":  

```fortran
! timesteps
time_delta_coeff = 1 ! 1 by default
mesh_delta_coeff = 1 ! 1 by default
```

To vary $\alpha_\mathrm{MLT}$, have each member of your table select a unique `mixing_length_alpha` from the set `[1.5, 1.8, 2, 3]`. Note that all of these values have been chosen in various works in the literature for RSG modeling. Make sure everyone at your table chooses a different value. In the `&controls` section of your `inlist_project`, set: 

```fortran
! mlt
  mixing_length_alpha = YOUR ALPHA VALUE
```

Run the model, and watch the HR diagram and Kippenhahn diagram evolve, comparing to others in your group.  

```bash
./clean && ./mk && ./rn 
```

Again record the final **Mass**, **Radus**, **$T_\mathrm{eff}$**, **Luminosity**, and **star age**. Compare to the others at your table. What has changed? Discuss briefly at your table what differences you see and why they might appear. 

You should notice that higher values of $\alpha$ correspond to (in this limited application) smaller radii and hotter effective temperatures. 

Does this matter? It depends on what you care about! Just be sure to explain why it does or doesn't matter. Just as an example, if you fit supernova lightcurves using stellar models with systematically large radii (systematically low values of $\alpha_\mathrm{MLT}$), you will recover systematically low masses and explosion energies, because the supernova luminosity depends in part on the radius of the progenitor star. However, if you only care whether or not the star explodes, or the chemical evolution of stars, the core undergoing fusion and collapse is more or less _insensitive_ to changes in $\alpha_\mathrm{MLT}$ except insofar as a hotter $T_\mathrm{eff}$ changes the stellar wind mass loss rate (which we neglect entirely in our setup here). 

Though we primarily explored resolution testing from the standpoint of convergence regarding the star's position on the H-R diagram, it's likewise important to note that other key results may converge differently. If for example you care about the growth of the stellar core or about the star's chemical abundances, you should compare how _those plots_ (e.g. core mass vs. time, surface lithium versus time, etc.) change with changing resolution and engineering assumptions. 
