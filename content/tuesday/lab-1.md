---
weight: 1
author: Beatriz Bordadágua
---

# Minilab 1: 1D rotating stellar models
## Introduction
In the most simple case of a non-rotating single star the only forces acting on a mass element are pressure and gravity. The resulting spherical symmetry implies that the stellar structure equations depend only on one spatial coordinate (e.g., mass) and time.
However, **rotation deforms the spherical symmetry** (i.e., the equatorial radius becomes larger than the polar radius) consequently affecting stellar surface parameters, abundances and even its course of evolution (see e.g., [Palacios 2013](https://doi.org/10.1051/eas/1362007)). You can guess that to properly account for all the effects associated with rotation we need a multi-dimensional approach to solve the stellar structure equations. Today, **we will compare our 1D MESA rotating models with 2D ESTER models** ([Mombarg et al, 2023;](https://doi.org/10.1051/0004-6361/202347454)[ 2024](https://doi.org/10.1051/0004-6361/202348466)).

In the case with rotation, 1D stellar evolution codes, such as MESA, rely on the so-called shellular approximation to solve the stellar structure equations -- if the angular velocity is constant over isobars. 
MESA includes rotational effects by applying corrections to the equilibrium stellar structure equations to account for the effect of the centrifugal force and by solving two additional equations: the mixing of chemical elements and the angular momentum (AM) transport. **The latter determines the evolution of the angular velocity $(\Omega)$ with time which is what we will focus on this minilab 1.** 

The AM transport is mediated through diffusive and advective processes. In MESA, the AM transport is only included by diffusion using the following equation,
$$
\left(\frac{\partial \Omega}{\partial t} \right)_m = \frac{1}{i} \left(\frac{\partial}{\partial m} \right)_t \left[ \left(4\pi r^2 \rho \right)^2 i\; \nu_{\mathrm{AM}} \left(\frac{\partial \Omega}{\partial m}\right)_t\right]- \frac{\Omega}{r} \left(\frac{\partial r}{\partial t} \right)_m \left(\frac{\mathrm{d}\ln{i}}{\mathrm{d}\ln{r}} \right),
$$
where $i$ is a shell specific moment of inertia, and **$\nu_{\mathrm{AM}}$ is the turbulent viscosity which determines the efficiency of the AM transport**. The first term on the right-hand side accounts for the diffusion transport and the second term accounts for contraction and expansion of the shells at constant mass.


In this minilab 1 we will incorporate rotation in a 10 solar mass model using MESA. We will look at the effect of rotation in the global surface parameters and on the internal rotation profile by including different AM transport mechanisms.




## Setup

Download the working directory for minilab 1 [here](https://www.dropbox.com/scl/fi/g5mw93o2ziz3jmkkrlx6j/minilab1.zip?rlkey=g9svi1apesx5uvg8mnghh4e07&st=8sr1ky86&dl=0).
The solutions for each exercise are [here](https://www.dropbox.com/scl/fi/q9v32nw27odry6v1t0sra/minilab1_solutions.zip?rlkey=lqdbiuwnpx2cdwmuupfy4ty6r&st=i6mf0mt3&dl=0).

Unpack the zip files using `unzip minilab1.zip` and move to the working directory `cd minilab1/Exercise_0`.

## Exercise 0: Pre-main sequence model
Before we start incorporating rotation in our models, we need to compute the pre-main sequence (PMS) track that will be saved and used as a starting point in the next steps.
We will start by modify the standard inlist. Add the commands below into the `inlist_project` in the respective modules `&star_job`, `&kap` and `&controls`.

Copy the commands below to compute a PMS model and save a model at the zero-age-main-sequence (ZAMS) phase.
```
create_pre_main_sequence_model = .true.
pre_ms_T_c = 6d5 
save_model_when_terminate = .true. 
save_model_filename = 'model_ZAMS' 
```

First, change the nuclear network to include additional reactions and isotopes relevant for the CNO-cycle. A list of default nuclear networks options are listed in the `$MESA_DIR/data/net_data/nets` directory.
```
change_net = .true.
new_net_name = 'pp_cno_extras_o18_ne22.net'
```
Modify the initial composition of the model to be uniform and according to Grevesse & Noels 1993 (GN93) to match the composition of the 2D ESTER models.
```
set_uniform_initial_composition = .true.

initial_h1  = 0.71d0
initial_h2  = 0d0
initial_he3 = 0d0
initial_he4 = 0.27d0

initial_zfracs = 2
```

In the module `&kap` modify the opacities to match the GN93 abundances.
```
kap_file_prefix = 'gn93'
kap_lowT_prefix = 'lowT_fa05_gn93'
kap_CO_prefix = 'gn93_co'

! CO enhanced opacities
use_Type2_opacities = .true.
kap_Type2_full_off_X = 1d-3
kap_Type2_full_on_X = 1d-6
Zbase = 0.02
```

Now let's modify the module `&controls` to include the physics we want in our stellar model. Start by selecting an initial mass of 10 solar masses by copying

```
initial_mass = 10d0
```
Then, define the luminosity near the ZAMS and add the stopping condition at the ZAMS
```
Lnuc_div_L_zams_limit = 0.99
stop_at_phase_ZAMS = .true.
```

Set the minimum value for mixing.
```
set_min_D_mix = .true.
min_D_mix = 1d3
```
Add the atmospheric boundary conditions.
```
atm_option = 'T_tau'
atm_T_tau_relation = 'Eddington'
atm_T_tau_opacity = 'varying'
```
Include the mixing length prescription as developed by Cox & Giuli 1968 and add the solar calibrated  value for Eddington grey for the mixing length parameter.
```
mixing_length_alpha = 1.713d0  
mlt_option = 'Cox'
```

Include the following Hydrogen core overshoot (calibrated to typical g-mode pulsator).
```
overshoot_scheme(1) = 'exponential'
overshoot_zone_type(1) = 'burn_H'
overshoot_zone_loc(1) = 'core'
overshoot_bdy_loc(1) = 'top'
overshoot_f(1) = 0.015
overshoot_f0(1) = 0.005

overshoot_scheme(2) = 'exponential'
overshoot_zone_type(2) = 'any'
overshoot_zone_loc(2) = 'shell'
overshoot_bdy_loc(2) = 'any'
overshoot_f(2) = 0.005
overshoot_f0(2) = 0.005
```
> [!IMPORTANT]
> Do not forget to save all the changes you made in the `inlist_project`.

**Finally let's run MESA!** Do not forget to always clean the executable files, compile the code and, at last, run the executable generated. Let the code run until it reaches the ZAMS. The run will stop automatically after it reaches the stopping criterion (this might take some minutes < 5min).
```
./clean
```
```
./mk
```
```
./rn
```

> [!TIP]
> If you get permission denied when trying to `./mk` or `./rn`, run `chmod u+x rn` in the terminal.


if there's a permission denied when trying to run rn or mk, you just have to run `chmod u+x rn` in the terminal

> [!NOTE]
> A PGstar plot window displaying the HR diagram of the star should appear. 


Once the run is finished, you should have a model named `model_ZAMS` in your work directory. This is our starting model for the next steps.

> [!IMPORTANT]
> Copy the saved model into the directory of Exercise 1 and Exercise 2. 
>```
>cp model_ZAMS ../Exercise_1/
>```
>```
>cp model_ZAMS ../Exercise_2/
>```
>```
>cp model_ZAMS ../Exercise_Bonus/
>```



## Exercise 1: The effect of rotation on the surface parameters

First, move to the `Exercise_1` work directory and check if the file `model_ZAMS` is there. Otherwise, repeat the last step in Exercise 0.

Start the computation from the precomputed ZAMS model. To do so modify the `&star_job`in the `inlist_project` by adding
```
create_pre_main_sequence_model = .false.
load_saved_model = .true.
load_model_filename = 'model_ZAMS'
```

The degree of deformation from the spherical symmetry due to rotation depends on the ratio of the rotation rate and the critical rotation of the star ($\Omega /\Omega_{\mathrm{crit}}$). The critical rotation is reached when the centrifugal force equals the gravitational force in the equatorial plane. For this run, set the $(\Omega /\Omega_{\mathrm{crit}})_{\mathrm{initial}}$ = 0.2 by adding 
```
new_omega_div_omega_crit = 0.2
set_near_zams_omega_div_omega_crit_steps = 20
```
Next, in the `&controls` section add a stopping criterion when the central hydrogen abundance drops below $10^{-3}$, i.e., at the end of the main-sequence stage.
```
xa_central_lower_limit_species(1) = 'h1'
xa_central_lower_limit(1) = 1d-3
```

Modify the output LOGS directory name to specify the physics you included in your model for each, for example `LOGS_0.2_nuvisc_1d5`. Do not forget to change the name of the LOGS directory in each run otherwise the output files will be overwritten.

```
log_directory = 'LOGS_0.2_nuvisc_1d5'
```
As we introduced in the beginning of this minilab, the turbulent viscosity coefficient $\nu_{\mathrm{AM}}$ determines the efficiency of the transport of AM by diffusion. 
A very high value of $\nu_{\mathrm{AM}}$ induces very efficient AM transport and results in near solid body rotation rate as it is the case in convective regions. 

For the purpose of this lab we will **include an arbitrary viscosity coefficient $\nu_{\mathrm{AM}}=10^5 \;\mathrm{cm}^2\mathrm{/s}$ that is uniform throughout the star.**
Look for the parameters you need to add to the `inlist_project` in the MESA rotation `&controls` documentation [here](https://docs.mesastar.org/en/24.08.1/reference/controls.html).

{{< details title="Hint." closed="true" >}}
The MESA parameter for the viscosity $\nu_{\mathrm{AM}}$ is `am_nu`.
Look in the rotation controls tab and search for the key-word `uniform_am_nu`.
{{< /details >}}

{{< details title="Solution. Click on it to check your solution." closed="true" >}}
These are the two parameters you need to add.
```
set_uniform_am_nu_non_rot = .true. 
uniform_am_nu_non_rot = 1d5 !cm^2/s
```
{{< /details >}}

Now that we have included the rotation parameters in our inlist let's add the surface and center omega information to the `history.data` file so that we can track how those parameters change along evolution. To do so, you just need to uncomment (remove the ! ) the lines below from the file `history_columns.list` in your work directory.
- `surf_avg_omega`
- `surf_avg_omega_div_omega_crit`
- `center_omega`
- `center_omega_div_omega_crit`
- `grav_dark_L_polar`
- `grav_dark_Teff_polar`
- `grav_dark_L_equatorial`
- `grav_dark_Teff_equatorial`

Lastly, let's add the omega profile information to the `profile.data` files by uncommenting the lines below from the file `profile_columns.list` in your work directory.
- `omega`
- `omega_div_omega_crit`

> [!IMPORTANT]
> Do not forget to save all the changes you made in the `inlist_project`, `history_columns.list` and `profile_columns.list`.

**Finally let's run MESA!** The run will stop automatically after it reaches the stopping criterion (this might take some minutes < 5min).
```
./clean \;./mk
./rn
```

> [!NOTE]
> **A pgplot window should appear when you start the MESA run.** On the left-hand side you have three history panels showing the evolution of the respective quantities with time. On the right-hand side you have three profile panels which show the quantities throughout the star that are updated at each timestep. **Spend some time looking at the pgplot to understand each individual plot.** 

Don't worry if your run has finished before you grasped the content of the plots. The pgplot of the final model was saved in the `/png` folder under the name `grid1000495.png`. **Modify the name of this file in order to not be rewritten in the next runs**, for e.g., `grid1000495_0.2_nuvisc1d5.png`.


**Let's create another model with faster rotation $(\Omega /\Omega_{\mathrm{crit}})_{\mathrm{initial}}$ = 0.6.** Make the necessary modifications to the `inlist_project`. Do not forget to change the LOGS directory name, for e.g., `'LOGS_0.6_nuvisc_1d5'`.

{{< details title="Solution. Click on it to check your solution." closed="true" >}}
Modify the parameter in the `&star_job` section of the `inlist_project`.
```
new_omega_div_omega_crit = 0.6
```
Modify the parameter in the `&controls` section of the `inlist_project`.
```
log_directory = 'LOGS_0.6_nuvisc_1d5'
```
{{< /details >}}

**Run MESA again:** `./clean` `./mk` `./rn`. The run will stop automatically after it reaches the stopping criterion (this might take some minutes < 5min). 
After the run has finished do not forget to modify the `png` file name, for e.g., `grid1000495_0.6_nuvisc1d5.png`.


Look again at the pgplot panels with the HDR. Can you explain the difference?


Compare the pgplot png files of the two runs ($\Omega/\Omega_{\mathrm{crit}}$ = 0.2 and $\Omega/\Omega_{\mathrm{crit}}$ = 0.6) more specifically compare the HR diagram panels. Can you explain why they are different?


{{< details title="Discuss with your table first before clicking here." closed="true" >}}
The difference you see between the HRDs is the so-called **gravity-darkening** (von Zeipel 1924). Including rotation deforms the star from its equilibrium spherical symmetry. Due to the centrifugal force, the effective gravity is lower at the equator than at the poles. Therefore, the poles are hotter than the equator. You can also interpret it as the equator lines follows the track a non-rotating less massive star would have (the opposite for the polar lines).
{{< /details >}}


## Exercise 2: (Magneto)-hydrodynamic instabilities
In Exercise 1 we took a very simple approach by including a constant ad-hoc viscosity in MESA models. In this Exercise 2, we will take a more physically motivated approach by including (magneto)-hydrodynamic instabilities in our stellar models.

In addition to the effects of rotation on the surface parameters see in Exercise 1, **rotation also triggers several hydrodynamical instabilities that can transport AM and chemical elements in the radiative regions**. MESA includes several (magneto)-hydrodynamical processes in its AM transport prescription: 
- dynamical shear instability (DSI), 
- Solberg-Høiland instability (SH), 
- secular shear instability (SSI), 
- Eddington-Sweet circulation (ES), 
- Goldreich-Schubert-Fricke instability (GSF),
- Spruit-Taylor dynamo (ST).

See more details on these physical processes in [Heger et al. (2000)](https://iopscience.iop.org/article/10.1086/308158/pdf). The MESA viscosity coefficient $(\nu_{\mathrm{AM}})$ is calculated as a sum of the diffusion coefficients for convection, semi-convection and the instabilities described above. 



First, move to the `Exercise_2` work directory and check if the file `model_ZAMS` is there. Otherwise, repeat the last step in Exercise 0.

Next, disable the uniform viscosity in the `&controls` section of the `inlist_project` that we used in the previous exercise.
```
set_uniform_am_nu_non_rot = .false. 
uniform_am_nu_non_rot = 0d0
```

> [!IMPORTANT]
> **In this exercise you will compute models with different $(\Omega/\Omega_{\mathrm{crit}})_{\mathrm{initial}}$ and different rotational-instabilities.** 
>In this [google spreadsheet](https://docs.google.com/spreadsheets/d/1Rc_gstPrDX4eZfTN4dc20j9K_ddqjsyR0gEtQT2xd2s/edit?usp=sharing) choose the combination of parameters you want to include in your model and write your name there so no one computes the same model. 


> [!TIP]
> Choose the lower $(\Omega/\Omega_{\mathrm{crit}})_{\mathrm{initial}}$ to start with since they are easier to compute.
If by the end of the lab you still have time to spare you can run a different combination from the spreadsheet.

Modify `inlist_project` according to what you chose in the google spreadsheet. Include the selected $(\Omega/\Omega_{\mathrm{crit}})_{\mathrm{initial}}$ and do not forget to change the LOGS directory name, for e.g., `'LOGS_0.6_DSI'` (recall that we have also done this steps in Exercise 1).


{{< details title="Check here the parameters you have to modify." closed="true" >}}
Modify the parameter in the `&star_job` section of the `inlist_project`.
```
new_omega_div_omega_crit = <VALUE>
```
Modify the parameter in the `&controls` section of the `inlist_project`.
```
log_directory = 'LOGS_<VALUE>_<INSTABILITY>'
```
{{< /details >}}

Additionally, to **include the AM transport by (magneto)-hydrodynamic processes in MESA** set the parameters below equal to 1 to in the `&controls` section of the `inlist_project`.
```
D_DSI_factor = 1   ! dynamical shear instability
D_SH_factor  = 0   ! Solberg-Hoiland
D_SSI_factor = 0   ! secular shear instability
D_ES_factor  = 0   ! Eddington-Sweet circulation
D_GSF_factor = 0   ! Goldreich-Schubert-Fricke
D_ST_factor  = 0   ! Spruit-Tayler dynamo
```

Save all the changes you made in the `inlist_project`. There is **one more step before you start your computation**. 

Asteroseismic observations can only provide near core rotation rate estimates for these stars. Remember that for the mass range we are computing (10 solar masses) the star has a convective core and a radiative envelope during the main-sequence stage. MESA history parameters only include omega at the centre of the star and at the surface. **In order to compare with observations we need to compute the near core rotation rate using the `run_star_extras` module in MESA.**

Prepare in the `run_star_extras.f90` (inside the `src` folder in the work directory) three additional history columns named `omega_core_div_omega_surf`, `omega_core`, and `omega_surf`. Set the correct number of additional columns in the `how_many_extra_history_columns` function by adding 
```fortran
how_many_extra_history_columns = 3
```
and modify the `data_for_extra_history_columns` function for each additional column as follows:
```fortran
! variable names
names(1) = 'omega_core_div_omega_surf'
names(2) = 'omega_core'
names(3) = 'omega_surf'

! convert from rad/s to 1/day
factor = 60d0*60d0*24d0/(2d0*PI)

! omega at the edge of the convective core in daysprofile_columns.list
vals(2) = 
! omega at the surface in days  
vals(3) = 
! omega_core/omega_surf
vals(1) = 
```

{{< details title="Hint." closed="true" >}}
Use the MESA profile variable `s% omega(k)` and the history variable `s% omega_avg_surf` to compute the variables needed. In MESA the variable `s%nz` corresponds to the mesh point at the boundary of the convective core.
{{< /details >}}


{{< details title="Check your code with the solution. Click on it to reveal it." closed="true" >}}
```fortran
! omega at the edge of the convective core (s%nz) in days
vals(2) = s% omega(s% nz) *factor
! omega at the surface in days  
vals(3) = s% omega_avg_surf *factor
! omega_core/omega_surf (enforce lower limit of 1 to avoid weird feature in pgplot) 
vals(1) = max(1d0,vals(2)/vals(3))
```
{{< /details >}}

> [!WARNING]
> This new variables were already added in the `pgstar_inlist` in the folder `Exercise_2`. So confirm if the name of the variables in your `run_star_extras` is correct otherwise you will have warnings in the pgplot.

> [!IMPORTANT]
> Do not forget to save all the changes you made in the `inlist_project` and in the `run_star_extras.f90`.

**Finally let's run MESA!** `./clean` `./mk` `./rn`. The run will stop automatically after it reaches the stopping criterion (this should take some minutes < 5min). 

> [!NOTE]
> **A pgplot window should appear when you start the MESA run.** Look at the pgplot panels on the right-hand side to confirm that the instability you included in the `inlist_project` is activated.


Insert the values of `omega_core` `omega_surf` and `surf_avg_omega_div_omega_crit` in the [google spreadsheet](https://docs.google.com/spreadsheets/d/1Rc_gstPrDX4eZfTN4dc20j9K_ddqjsyR0gEtQT2xd2s/edit?usp=sharing). You can find these values on the `/png/grid1000495.png` saved after each run or in the last line of the output file `LOGS/history.data` of the respective run. 

Finally, let's compare the MESA track we just computed with 2D Ester models. To do so either send your tutor the `history.data` file of your runs or plot the models yourself using this [jupiter notebook](https://colab.research.google.com/drive/1HY_7Y59D4JFJG4tiY3q5TUmdJsz4wGIT#scrollTo=dIL6HmKwXFfK). The instructions to make the comparison plots are in the jupiter notebook itself. **Can you match the 2D Ester models with the (magneto)-hydrodynamic instability included in your model?** Compare your results with the rest of your table. 

## Bonus Exercise: Critical rotation
Some of the runs in Exercise 2 may have led to rotation rates above critical rotation. In order to automatically stop a computation when this takes place you need to add a customized stopping criterion to the `run_star_extras`.

{{< details title="Hint 1" closed="true" >}}
The function you need to modify is
```fortran
integer function extras_check_model
```
{{< /details >}}

{{< details title="Hint 2" closed="true" >}}
The MESA variables you can use are `s% omega_avg_surf` and `s% omega_crit_avg_surf`
{{< /details >}}

{{< details title="Check your code with the solution. Click on it to reveal it." closed="true" >}}
```fortran
if (s% omega_avg_surf/s% omega_crit_avg_surf >= 1.1d0) then
    extras_check_model = terminate
    write(*, *) 'termination code: reached critical rotation'
    return
end if
```
{{< /details >}}

Run MESA with a high value of $(\Omega /\Omega_{\mathrm{crit}})_{\mathrm{initial}}$ = 0.9. Check if the code stops once the rotation rate is above critical rotation (you can monitor the $(\Omega /\Omega_{\mathrm{crit}})$ evolution using the pgplot).
