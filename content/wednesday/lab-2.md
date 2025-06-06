# Part 1: X-ray binaries - exploring Cyg X-1

Cygnus X-1 is a well-known high-mass X-ray binary consisting of a black hole and an O-type supergiant companion. Recent observations (<https://arxiv.org/pdf/2504.05885>) have updated its parameters:

- Donor mass: $29^{+6}_{-3} \rm\ M_\odot$
- Black hole mass: $17.5^{+2}_{-1} \rm\ M_\odot$
- Orbital period: $5.6$ days

## 1. Simulating the Evolution of Cygnus X-1

To simulate the evolution of Cygnus X-1, we start off with creating a fresh copy of the `work/` directory (`cp -r $MESA_DIR/binary/work .`) and with running a system with initial masses $M_\mathrm{1} = 34 \rm\ M_\odot,\ M_\mathrm{2} = 17.4 \rm\ M_\odot$ and orbital period $P = 5.5 \rm\ d$. As the secondary component is a black hole, we assume it to be a point mass and focus only on the detailed evolution of the donor. Additionally, we need to set a few additional controls to the system:

<!-- - -----------????? limit accretion using the Eddington limit, ?????----------- -->
- the `Kolb` mass transfer type,
- do the wind mass accretion from the donor to the BH,
- enable rotation by assuming tidal synchronisation,
- assume conservation of the total angular momentum of the system, include loss of angular momentum via mass loss and via gravitational wave radiation,

In the case of the donor, we need to modify the `&star_job` section :

```fortran
&star_job

    mesa_dir = ''
    show_log_description_at_start = .true.

    pause_before_terminate = .true.

    pgstar_flag = .true.

    ! initial metal abundances
    relax_initial_Z = .true.
    new_Z = 0.0142d0
    initial_zfracs = 3 ! GS98

    ! rotation
    new_rotation_flag = .true.
    change_rotation_flag = .true.
    change_initial_rotation_flag = .true.

/ ! end of star_job namelist
```

and the `&controls` section:

```fortran
&controls

    extra_terminal_output_file = 'log1' 
    log_directory = 'LOGS1'
    write_profiles_flag = .false.

    profile_interval = 50
    history_interval = 1
    terminal_interval = 1
    write_header_frequency = 10

    ! convection
    use_ledoux_criterion = .true.
    MLT_option = 'ML1' ! Bohm-Vitense 1958 scheme
    mixing_length_alpha = 1.5d0
    semiconvection_option = 'Langer_85'
    alpha_semiconvection = 1.0d0


    ! step overshoot 
    overshoot_scheme(1) = 'step'
    overshoot_zone_type(1) = 'any'     
    overshoot_zone_loc(1) = 'core'      
    overshoot_bdy_loc(1) = 'top'       
    overshoot_f(1) = 0.345d0
    overshoot_f0(1) = 1.0d-4

    ! rotation
    D_DSI_factor = 1.0d0         ! Dynamical shear instability
    D_SSI_factor = 1.0d0         ! Secular shear instability
    D_GSF_factor = 1.0d0         ! Goldreich-Schubert-Fricke instability
    D_ES_factor = 1.0d0          ! Eddington-Sweet circulation
    D_SH_factor = 0.0d0          ! Solberg-Høiland (disabled unless needed)


    ! angular momentum
    ! Enable specific angular momentum and composition transport mechanisms
    am_D_mix_factor = 0.033d0 ! 1/30d0

    am_nu_DSI_factor = 1.0d0         ! Dynamical shear instability
    am_nu_SSI_factor = 1.0d0         ! Secular shear instability
    am_nu_GSF_factor = 1.0d0         ! Goldreich-Schubert-Fricke instability
    am_nu_ES_factor = 1.0d0          ! Eddington-Sweet circulation
    am_nu_SH_factor = 0.0d0          ! Solberg-Høiland (disabled unless needed)

    ! winds
    hot_wind_scheme = 'Vink'
    Vink_scaling_factor = 1.0d0 
    Dutch_wind_lowT_scheme = 'Nieuwenhuijzen'
    Dutch_scaling_factor = 1.0d0

/ ! end of controls namelist
```

To see if all runs well, run your new model! (`./rn`).

{{< details title="Solution" closed="true" >}}

```fortran
&binary_job

   inlist_names(1) = 'inlist1' 
   inlist_names(2) = 'inlist2'

   evolve_both_stars = .false.

/ ! end of binary_job namelist

&binary_controls
         
   m1 = 34d0  ! donor mass in Msun
   m2 = 17.4d0 ! companion mass in Msun
   initial_period_in_days = 5.5d0
   mdot_scheme = "Kolb"

   ! do wind accretion
   do_wind_mass_transfer_1 = .true.

   !rotation controls
   do_tidal_sync = .true.

   do_jdot_ls = .true.
   do_jdot_gr = .true.
   do_jdot_ml = .true.

   accretor_overflow_terminate = 0.2d0 ! add some space

   !control accretion using the Eddington limit
   limit_retention_by_mdot_edd = .false.

   max_tries_to_achieve = 20
         
/ ! end of binary_controls namelist

```
{{< /details >}}

<!-- ### Solution `inlist_project` -->

<!-- >```fortran
>&binary_job
>
>   inlist_names(1) = 'inlist1' 
>   inlist_names(2) = 'inlist2'
>
>   evolve_both_stars = .false.
>
>/ ! end of binary_job namelist
>
>&binary_controls
>         
>   m1 = 34d0  ! donor mass in Msun
>   m2 = 17.4d0 ! companion mass in Msun
>   initial_period_in_days = 5.5d0
>   mdot_scheme = "Kolb"
>
>   ! initial orbit synchronisation
>   ! do_initial_orbit_sync_1 = .false.
>   ! do_initial_orbit_sync_2 = .false.
>
>   ! do wind accretion
>   do_wind_mass_transfer_1 = .true.
>
>   !rotation controls
>   do_tidal_sync = .true.
>
>   do_jdot_ls = .true.
>   do_jdot_gr = .true.
>   do_jdot_ml = .true.
>
>   accretor_overflow_terminate = 0.2d0 ! add some space
>
>   !control accretion using the Eddington limit
>   limit_retention_by_mdot_edd = .true./.false.
>
>   max_tries_to_achieve = 20
>         
>/ ! end of binary_controls namelist
>
>``` -->

### 1.1. Finding the model that fits the observations

Cyg X-1 has accurate determinations of orbital and physical parameters (<https://arxiv.org/pdf/2504.05885>):

#### Orbital parameters

- $M_\mathrm{donor} = 29 ^{+6} _{-3}\ \mathrm{M_\odot}$
- $M_\mathrm{BH} = 17.5 ^{+2} _{-1}\ \mathrm{M_\odot}$
- $P_\mathrm{orb} = 5.559\ \mathrm{d}$
- $\log \dot{M} = -6.5 \pm 0.2\ \mathrm{M_\odot\, yr^{-1}}$

#### Physical parameters of the donor

- $T_\mathrm{eff} = 28\,500 \pm 1000\ \mathrm{K}$
- $\log L/\mathrm{L_\odot} = 5.5 \pm 0.1$
- $\log g = 3.2 \pm 0.1$
- $R = 22.3 ^{+1.5} _{-2.5}\ \mathrm{R_\odot}$

Let's try and find the model that fits within the measured spectroscopic parameters, like $T_{\rm eff}$, $\log L$ and $\log g$, and terminate the computations after doing so.

To force MESA to stop after finding a fitting model to the observations we need to modify the `run_binary_extras.f90` file. You can find it in the `src/` in your directory. You can use the internally computed by MESA quantities using the binary pointer `b%` and star pointers `s1%`/`s2%` to acccess the donor/accretor modules, respectively. Some examples of useful values are:

- `b% s1% Teff`: The stellar effective temperature.
- `b% s1% photosphere_L`: The stellar luminosity.
- `b% s1% photosphere_logg`: Logarythm of the stellar gravitational acceleration.

Go ahead and add a stopping criterion `extras_binary_finish_step = terminate` in the `extras_binary_finish_step` function once a model reached a desired surface properties:

```fortran
    ! returns either keep_going or terminate.
    ! note: cannot request retry; extras_check_model can do that.
    integer function extras_binary_finish_step(binary_id)
        type (binary_info), pointer :: b
        integer, intent(in) :: binary_id
        integer :: ierr
        call binary_ptr(binary_id, b, ierr)
        if (ierr /= 0) then ! failure in  binary_ptr
        return
        end if  
        extras_binary_finish_step = keep_going
        
        !!! Add a stopping criterion 

    end function extras_binary_finish_step
```

<!-- To store a model at the end of the run, add the save controls in the `&star_job` section in your inlist:

```fortran
    save_model_when_terminate = .true.
    save_model_filename = 'final_CygX1.mod'
```

We will need that model in the subsequent runs! -->

### Gravitational waves radiation and merge time

Once we are all set to run our model, we can add one extra tweak to our computations. As we assumed the loss of angular momentum via gravitational waves radiation in our model (the `do_jdot_gr` control), we can compute the approximate time our binary will take to merge.

For two point masses $m_1$ and $m_2$ on a circular orbit with separation $a$, the GW inspiral time (Peters 1964) is given by

$$t_{\mathrm{merge}} = \frac{5}{256} \cdot \frac{c^5 a^4}{G^3 m_1 m_2 (m_1 + m_2)}.$$

Alternatively, using orbital period $P$ instead of orbital separation:

$$t_{\mathrm{merge}} = \frac{5}{256} \cdot \frac{(G M_{\mathrm{chirp}})^{-5/3}}{c^5} \cdot \left( \frac{P}{2\pi} \right)^{8/3},$$

where $M_{\mathrm{chirp}}$ is the chirp mass:

$$M_{\mathrm{chirp}} = \frac{(m_1 m_2)^{3/5}}{(m_1 + m_2)^{1/5}}$$

> **Note**  
> MESA computes all we need under-the-hood. All we need to do is to capture these values and compute $t_{\mathrm{merge}}$. 
>
> **Remember** that MESA lib gives b% m(1) and b% m(2) in grams and b% period in seconds. Constants, such as $G \equiv $ `standard_cgrav` are in cgs. If you want to use the MESA-computed constants, remember to import the `const_def` module at the beginning of the `run_binary_extras.f90`.

{{< details title="Solution" closed="true" >}}

```fortran
    ! Chirp mass
    mchirp = ((b% m(1) * b% m(2))**(3.0d0 / 5.0d0)) / ((b% m(1) + b% m(2))**(1.0d0 / 5.0d0))

    ! t_merge in seconds
    t_merge = (5.0d0 / 256.0d0) * (clight**5 / standard_cgrav**(5.0d0 / 3.0d0)) * &
                ((b% period / (2.0d0 * pi))**(8.0d0 / 3.0d0)) * mchirp**(-5.0d0 / 3.0d0)

    ! seconds to Gyr
    t_merge_gyr = t_merge / (3600.0d0 * 24.0d0 * 365.25d0 * 1.0d9)

    ! write(*,*) 'Chirp mass [g]     = ', mchirp
    write(*,*) 'Merger time [Gyr]  = ', t_merge_gyr
```

{{< /details >}}

To apply all the changes you have made in your `run_binary_extras.f90` you need to compile and run your model (`./mk && ./rn`)!

{{< details title="Solution" closed="true" >}}

```fortran
      integer function extras_binary_finish_step(binary_id)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer :: ierr

         double precision :: mchirp, t_merge, t_merge_gyr

         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if  
         extras_binary_finish_step = keep_going
         
         write(*,*) 'Teff = ', b% s1% Teff, 'logL = ', log10(b% s1% photosphere_L), 'logg = ', b% s1% photosphere_logg
         write(*,*) 'f_RL = ', b% r(1)/b% rl(1)


         chi2_value = chi2(b% s1% Teff, log10(b% s1% photosphere_L), b% s1% photosphere_logg, &
                         Teff_obs, logL_obs, logg_obs, &
                         dTeff_obs, dlogL_obs, dlogg_obs)
         
         write(*,*) 'Chi2 from the previous step:',chi2_value_old
         write(*,*) 'Chi2:', chi2_value
      
      
         ! Spectroscopic observations:
         !     Teff  = 28500 +/- 1000 K
         !     log_L = 5.5 +/- 0.1 Lsun
         !     log_g = 3.2 +/- 0.1
         if ( abs(b% s1% Teff - Teff_obs) < dTeff_obs .and. &
              abs(log10(b% s1% photosphere_L) - logL_obs) < dlogL_obs .and. &
              abs(b% s1% photosphere_logg - logg_obs) < dlogg_obs .and. &
              chi2_value > chi2_value_old) then


            ! Now that we have the quasi-best fitting model, let's compute merger time due to GW emission, based on Peters 1964
            !     From MESA lib: b% m(1) and b% m(2) are in grams, b% period is in seconds,
            !     const_def gives Msun, clight and standard_cgrav in cgs

            ! Chirp mass
            mchirp = ((b% m(1) * b% m(2))**(3.0d0 / 5.0d0)) / ((b% m(1) + b% m(2))**(1.0d0 / 5.0d0))

            ! t_merge in seconds
            t_merge = (5.0d0 / 256.0d0) * (clight**5 / standard_cgrav**(5.0d0 / 3.0d0)) * &
                      ((b% period / (2.0d0 * pi))**(8.0d0 / 3.0d0)) * mchirp**(-5.0d0 / 3.0d0)

            ! seconds to Gyr
            t_merge_gyr = t_merge / (3600.0d0 * 24.0d0 * 365.25d0 * 1.0d9)

            ! write(*,*) 'Chirp mass [g]     = ', mchirp
            write(*,*) 'Merger time [Gyr]  = ', t_merge_gyr

            write(*,*) "Found a model maching the observations. Terminating"
            extras_binary_finish_step = terminate

         end if

      end function extras_binary_finish_step
```

{{< /details >}}

<!-- ### Solution `run_binary_extras.f90`

```fortran
      ! returns either keep_going or terminate.
      ! note: cannot request retry; extras_check_model can do that.
      integer function extras_binary_finish_step(binary_id)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer :: ierr

         ! Spectroscopic observations:
         !     Teff  = 28500 +/- 1000 K
         !     log_L = 5.5 +/- 0.1 Lsun
         !     log_g = 3.2 +/- 0.1
         real(dp), parameter ::  Teff_obs = 28500.0d0,  logL_obs = 5.5d0,  logg_obs = 3.2d0
         real(dp), parameter :: dTeff_obs =  1000.0d0, dlogL_obs = 0.1d0, dlogg_obs = 0.1d0

         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if  
         extras_binary_finish_step = keep_going
         
         ! optional value printing
         write(*,*) 'Teff = ', b% s1% Teff, 'logL = ', log10(b% s1% photosphere_L), 'logg = ', b% s1% photosphere_logg
         write(*,*) 'f_RL = ', b% r(1)/b% rl(1)

      
      
         ! Apply stopping condition
         if ( abs(b% s1% Teff - Teff_obs) < dTeff_obs .and. &
              abs(log10(b% s1% photosphere_L) - logL_obs) < dlogL_obs .and. &
              abs(b% s1% photosphere_logg - logg_obs) < dlogg_obs) then

            write(*,*) "Found a model maching the observations. Terminating"
            extras_binary_finish_step = terminate

         end if

      end function extras_binary_finish_step

``` -->

> **Bonus task!:**  
> The above example was coded to terminate after finding the model that fits within the observations. As you may susspect, this model is not necessarily the only one, nor the best one to fit the observations. If you finished your assignments early, try to find the best model by applying some kind of a statistics, like $\chi^2$. You will need to define the `chi2` function outside of the run_binary_extras.f90 main body, and call it before and after MESA calculates another step. **Good luck!**

## 2. The efficiency of mass transfer and it's impact on the evolution of Cyg X-1

Mass transfer in close binary systems is a highly complex, multidimensional process shaped by hydrodynamic interactions, angular momentum exchange, and geometry-dependent flow patterns. Rather than a smooth and complete handover of mass from one star to the other, the gas is channeled through the inner Lagrangian point, forming a stream that enters the Roche lobe of the companion. Depending on the relative size and position of the stars, this stream may directly impact the accretor or settle into an accretion disk before any material is finally incorporated. A significant portion of the transferred matter might never reach the companion at all, being expelled from the system via outflows, disk winds, or loss through the outer Lagrangian points.

Capturing the full physics of this process requires 3D hydrodynamical simulations, which remain computationally expensive and inaccessible for 1D routine stellar evolution modeling. In the context of 1D codes like MESA, we therefore adopt simplified prescriptions that approximate the outcome of these processes through parameterized treatments.

A central parameter in such models is the accretion efficiency, which describes the fraction of the donor’s mass loss that is successfully accreted by the companion. MESA implements this through a set of `&binary_controls` parameters:

```fortran
    mass_transfer_alpha  = 0d0 ! fraction of mass lost from the vicinity of donor as fast wind 
                               ! (e.g., isotropic re-emission)
    mass_transfer_beta   = 0d0 ! fraction of mass lost from the vicinity of accretor as fast wind
    mass_transfer_delta  = 0d0 ! fraction of mass lost from circumbinary coplanar toroid
    mass_transfer_gamma  = 0d0 ! radius of the circumbinary coplanar toroid is 
                               ! "gamma**2 * orbital_separation"
```

The effective accretion efficiency is given by:

$$
\eta = (1 - \alpha - \beta - \delta)
$$

In this minilab, we will investigate how the choice of these parameters — particularly beta, which reflects wind loss near the black hole — influences the binary’s orbital and stellar evolution. We will adopt the default values of `mass_transfer_alpha = 0d0`, `mass_transfer_delta = 0d0` and `mass_transfer_gamma = 0d0` throughout, and explore a range of values for `mass_transfer_beta` to assess the impact of inefficient accretion in systems like Cygnus X-1. This will allow us to test how different mass loss scenarios shape the long-term configuration of the system.

### Varying the Mass Transfer Efficiency

To explore the effect of mass trasnfer efficiency on future evolution of Cyg X-1, we will vary the efficiency of mass transfer by changing the `mass_transfer_beta` parameter while keeping the initial primary masses and orbital period fixed, as were before. As each run may take a while, we will crowd-source this!

The participants should split into gropus that will be assigned a value of `mass_transfer_beta`. To do so, please write your name in the following **Google Spreadsheet: https://docs.google.com/spreadsheets/d/1HLwsGPu6w3t2NMUcdVYvkHFvqgIOUDkigfrZruN6Uo8/edit?usp=sharing** to select a $\beta$ value, from **0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9**, corresponding to accretion efficiencies from 100% up to 10%, respectively. These values come either without Eddington limit (by default) or with Eddington limited mass-accretion rate. If you choose the latter, remember to include `limit_retention_by_mdot_edd` in your `binary_controls` section!

> **Note:**  
>Do not change the initial masses or period. Focus only on the effect of beta. If you have a slower machine (with lower number of cores), choose lower $\beta$ as these runs tend to be faster. Faster machines can attempt higher beta values, which lead to more computationally demanding models. The $\beta=0.0$ run should take approximately 5 minutes on 2-core machines, while the $\beta~=~0.9$ run needs around 10 minutes.

As the model fitting within Cyg X-1 determined parameters is right on the onset of mass transfer, let us comment out the previously applied stopping criterion from the `run_binary_extras.f90` to let the system evolve a bit further. This time, let us choose the stopping criterion based on the minimum mass of the donor set to $23\,\mathrm{M_\odot}$.

{{< details title="Solution" closed="true" >}}
  
```fortran
      ! stop when mass drops below this limit
      star_mass_min_limit = 23.0d0
```

{{< /details >}}

To make the runs a bit faster, reduce the resolution to

```fortran
      ! resolution
      mesh_delta_coeff = 2.0d0
      time_delta_coeff = 2.0d0
```

As the last thing we would like to do is to compare the merge time with the one we got in the previous step. Modify slightly the `run_binary_extras` file, as we no longer need to calculate the merge time only fot the specific model - let it be calculated for every model to see whether this value changes. 

Next, compile and run the models (`./mk && ./rn`) with a fixed set of initial parameters (donor and black hole masses, and orbital period), while exploring different values of mass_transfer_beta. This isolates the role of accretion efficiency in shaping the orbital evolution, mass growth, and observable properties of the system.

> **As a group effort:**  
>What can we say about the future evolution of Cyg X-1 system from shuffling the `mass_transfer_beta` alone? How does the orbit react and why? 
>
>Should the merge time differ from the previous step, try to anwer why is that so? 

> **To think about:**  
> Is `mass_transfer_beta` the only way to control the accretor mass outcome? Can we substitute this parameter with other quantity that MESA provides, e.g. lowering the initial mass of the donor component? Why?

# Part 2: Common Envelope evolution with MESA

## 1. General ideas

In this part of the lab, we explore how we can model the common envelope (CE) phase of binary stars using MESA. We use MESA's single star module `star` to evolve the donor star. The effect of the companion star is modeled ontop of that in the `run-star-extras.f90` file.

![CE cartoon](/wednesday/CE_cartoon.png)

**Fig. 1**: Cartoon illustrating the 1D CE method. The companion (black dot) is spiraling inside the giant star. The black and blue arrows indicate the relative velocity of the companion and the drag force respectively. The heating zone is highlighted by the purple ring (taken from [Bronner et al. (2024)](https://doi.org/10.25518/0037-9565.12322))

We initiate the CE run by placing the companion star of mass $M_2$ at an orbital separation $a_\mathrm{ini}= 0.99R_1$ where $R_1$ is the radius of the donor star. At this point, the companion star is subject to dynamical friction, which leads to loss of angular momentum and orbital energy, leading to a decrease in the orbital separation. We can model the strength of the drag force by using the formulation from [Ostriker (1998)](https://ui.adsabs.harvard.edu/link_gateway/1999ApJ...513..252O/doi:10.1086/306858)
$$
F_\mathrm{drag} = \frac{4\pi (G M_2)^2\rho}{v_\mathrm{rel}^2} I,
$$
where $G$ is the gravitational constant, $v_\mathrm{rel}$ is the relative velocity between the donor star and the companion star, $\rho$ is the density of the donor star at the location of the companion star, and $I$ is the Coulomb logarithm. For subsonic motion, the Coulomb logarithm is given by
$$
I_\mathrm{subsonic} = \frac{1}{2} \ln \left( \frac{1 + \mathcal{M}}{1 - \mathcal{M}} \right) - \mathcal{M},
$$
where $\mathcal{M} = v_\mathrm{rel}/c_s$ is the Mach number and $c_s$ is the sound speed. For supersonic motion, the Coulomb logarithm can be approximated as
$$
I_\mathrm{supersonic} = \frac{1}{2} \ln \left( \frac{1}{1 - \mathcal{M}^2} \right) + \ln \left( \frac{2 a}{r_\mathrm{min}} \right),
$$
where $a$ is the orbital separation and $r_\mathrm{min}$ relates to the size of the companion star. 

Now that we know the strength of the drag force, we can calculate the change in orbital energy $E_\mathrm{orb}$ caused by the drag force. The change in orbital energy over one timestep $\Delta t$ is given by
$$
\Delta E_\mathrm{orb} = F_\mathrm{drag} v_\mathrm{rel} \Delta t.
$$
The change in orbital energy can be related to the change in orbital separation by
$$
\Delta E_\mathrm{orb} = -\frac{G M_{1,a} M_2}{2 a} + \frac{G M_{1,a} M_2}{2 a^\prime} = -\frac{G M_1 M_2}{2} \left( \frac{1}{a} - \frac{1}{a^\prime} \right),
$$
where $a^\prime$ is the new orbital separation, assuming that $M_{1,a}$ is roughly constant and that the orbit stays circular. Thus, we can model the evolution of the orbital separation.

The back reaction of the drag force on the donor star is modeled by using the `other_energy`-hook that allows us to modify the internal energy (heating/cooling). Because we know how much orbital energy is dissipated by the drag force (see above), we can add exactly the same amount of energy as heat in the envelope of the donor star. We heat all the layers within one accretion radius $R_\mathrm{a}$ of the companion star, with
$$
R_\mathrm{a} = \frac{2 G M_2}{v_\mathrm{rel}^2}.
$$
Additionally, we use a Gaussian weighting kernel $\propto \exp[-(\Delta r/R_\mathrm{a})]$ to have a smooth heating profile, where $\Delta r = |r - a|$.


## 2. Tasks

1. **Check out the `run-star-extras.f90` file**: Please download the provided MESA directory from [here](https://heibox.uni-heidelberg.de/f/7ca116519fe14d5fa929/?dl=1). This includes many files, most of which you can ignore for now. Have a close look at the `src/run-star-extras.f90` file, especially the `other_energy` hook and the `extras_finish_step` function. Try to understand how the drag force is calculated and how it is used to update the orbital separation.

{{< details title="Solution" closed="true" >}}
The drag force is calculated in line 352 and the orbital separation is updated in line 358. We are making use of the `xtra(i)` variables in the `star_info` structure. These are particularly handy as we do not have to worry about things going wrong, if MESA decides to do a `retry`.

All of the heating is done in the `CE_heating` function at the end of the file.
{{< /details >}}


1. **Run the CE model**: Run the CE model with the provided `inlist*` files. You are provided with a $12\,\mathrm{M}_\odot$ red supergiant model (take after core helium exhaustino from the `12M_pre_ms_to_core_collapse` test suite) and a $1.4\,\mathrm{M}_\odot$ companion star (could be a neutron star). Everything is already implemented as described above. You only need to focus on `inlist_CE`. The other inlists are taken from the test suite and not modified. So you really just have to do `./mk && ./rn`. Have a look at how the orbital separation changes over time and try to identify the different phases of CE evolution. The orbital separation is directly printed to the terminal but also saved to the `history.log` as `separation`. You can use the [MESA explorer](https://billwolf.space/mesa-explorer/) to visualize `separation` vs `star_age` (you need to upload your `history.log`file).

{{< details title="Solution" closed="true" >}}
The orbital separation is $\sim 41.1 \, {\rm R}_\odot$ after 2 years of CE evolution.
![CE separation annotated](/wednesday/CE_separation_annotated.png)
{{< /details >}}

3. **Change the companion mass**: Run the same setup but vary the mass of the companion star. What happens if you increase the mass of the companion star? What happens if you decrease it? How does this affect the orbital separation? We have tested the cases for $ 0.5\,\mathrm{M}_\odot \leq M_2 \leq 2.0\,\mathrm{M}_\odot$. Depending on the companion mass, you might need to adjust the stopping criterion in the `inlist_CE` file.

{{< details title="Hint" closed="true" >}}
Have a close look at the `inlist_CE` file. Try to spot the `x_ctrl` variable that corresponds to the companion mass.
{{< /details >}}

{{< details title="Solution" closed="true" >}}
The variable `x_ctrl(1)` in `inlist_CE` determines the mass of the companion. For more massive companions, the orbital separation after the plunge-in phase is larger. When visualizing the orbital evolution over time, the more massive companion plunges in faster compared to less massive companion. 
![CE separation for different companion masses](/wednesday/CE_separation_masses.png)
{{< /details >}}

4. **Modify the drag force**: The current implementation of the drag force is based on the assumption that the companion star is moving on a straight path through a uniform density background. This is not the case during the CE phase. In a more realistic scenario, the drag force may be weaker. Implement a free parameter in the drag force calculation that allows you to scale the drag force by a global factor $C_\mathrm{drag}$. Implement it such that you can control this factor from the `inlist_CE` file. What happens if you set $C_\mathrm{drag} = 0.5$? Is this what you expected? 

{{< details title="Hint" closed="true" >}}
You might want to define a `x_ctrl` variable in the `inlist_CE` file that you can use as a global pre-factor for the drag force. Try to locate the line where the drag force in computed in the `run_star_extras.f90`. And don't forget to run `./mk` after modifying the `run_star_extras.f90` file.
{{< /details >}}

{{< details title="Solution" closed="true" >}}
Update the `inlist_CE` file like this:
```fortran
&controls
    ...
      x_ctrl(5) = 1.0d0  ! drag force parameter
    ...
/ ! end of controls namelist
```

Then update the `run_star_extras.f90` as follows:
```fortran
Fdrag = s% x_ctrl(5) * 4*pi*rho_r*pow2(G * M2 / vrel) * I
```
You can find a full implementation [here](https://heibox.uni-heidelberg.de/f/e47fa6a418cb4129a11b/?dl=1).

For $C_\mathrm{d}<1$ the plunge-in takes longer and the separation afterwards is a little larger. This is expected as the drag force is generally weaker. For $C_\mathrm{d} = 0.5$, the orbital separation after two years of CE evolution is $\sim 57.2\,\mathrm{R}_\odot$.
{{< /details >}}

> **(Bonus task) Modify the drag force prescription**: Let's extend the drag force prescription to include the density gradient of the envelope. Implement the drag force prescription from [MacLeod & Ramirez-Ruiz (2015)](https://doi.org/10.1088/0004-637X/803/1/41) in the `run-star-extras.f90` file. The drag force is given by
$$
 F_\mathrm{drag} = \pi R_\mathrm{a}^2 v_\mathrm{rel}^2\rho(c_1 + c_2 \epsilon_\rho + c_3 \epsilon_\rho^2)
$$
> with $\epsilon_\rho = H_P/R_\mathrm{a}$ the ratio of the local pressure scale hight and the accretion radius. The pre-factors are $c_i = (1.91791946, −1.52814698, 0.75992092)$. This prescription is only valid for supersonic motion. For subsonic motion, we will continue using to the current implementation. Try to implement it such that there is a smooth transition for $0.9 < \mathcal{M} < 1.1$ between the two prescritions.
> 
> {{< details title="Hint 1" closed="true" >}}
> You need to get the local pressure scale height. This is stored in the `star-info` structure. Have a look at `$MESA_DIR/star_data/public/star_data_step_work.inc` and try to find the correct name for it. If you cannot find it, have a look at hint 2.
> {{< /details >}}
> 
> {{< details title="Hint 2" closed="true" >}}
> The pressure scale height is called `scale_height` and can be acessed via `s% scale_height(k)` for zone `k`.
> {{< /details >}}
> 
> {{< details title="Hint 3" closed="true" >}}
> For a smooth transition for $0.9 < \mathcal{M} < 1.1$ you can define an auxiliary variable $\alpha = \frac{\mathcal{M} - 0.9}{1.1-0.9}$. Then the drag force in the transition region is given by
$$
F_\mathrm{drag} = \alpha F_\mathrm{drag}^\mathrm{MacLeod} + (1 - \alpha)F_\mathrm{drag}^\mathrm{Ostriker}
$$
> {{< /details >}}
> 
> 
> {{< details title="Solution" closed="true" >}}
> One possible implementation could look like this
> ```fortran
>          G = standard_cgrav
>          M2 = s% xtra(1)  
>          a = s% xtra(2)
>          r_min = s% xtra(3)
>          do k=1, s% nz
>             if (s% r(k) < a) then
>                M_r = s% m(k)
>                rho_r = s% rho(k)
>                cs_r = s% csound(k)
>                omega_r = s% omega(k)
>                H_P_r = s% scale_height(k)
>                exit
>             end if
>          end do
>          vorb = sqrt(G*(M_r + M2)/a)
>          vrel = vorb - omega_r * a
>          Eorb = -G*M_r*M2/(2*a)
>          Mach_r = vrel / cs_r
>          Ra = 2.0d0 * G * M2 / pow2(vrel)
> 
>          ! compute the drag force
>          ! first, get Ostriker (1999) because needed for both implementations
>          if (Mach_r < 1.0d0) then
>             I = 0.5d0 * log((1.0d0 + Mach_r) / (1.d0 - Mach_r)) - Mach_r
>          else
>             I = 0.5d0 * log( 1.0d0 - 1.0d0/pow2(Mach_r)) + log(2*a / r_min)
>          end if
>          Fdrag_Ost = 4*pi*rho_r*pow2(G * M2 / vrel) * I
> 
>          if (s% x_logical_ctrl(1)) then
>             ! use  MacLeod & Ramirez-Ruiz (2015)
>             eps_rho = H_P_r / Ra 
>             f_mod = 1.91791946 - 1.52814698 * eps_rho + 0.75992092 * pow2(eps_rho)
>             Fdrag_Mac = pi * pow2(Ra) * pow2(vrel) * rho_r * f_mod
> 
>             ! do smooth transition between the two
>             if (Mach_r < 0.9d0) then
>                Fdrag = Fdrag_Ost
>             else if (Mach_r > 1.1d0) then
>                Fdrag = Fdrag_Mac
>             else
>                alpha = (Mach_r - 0.9d0) / (1.1d0 - 0.9d0)
>                Fdrag = (1.0d0 - alpha) * Fdrag_Ost + alpha * Fdrag_Mac
>             end if
>          else
>             ! use Ostriker (1999) only
>             Fdrag = Fdrag_Ost
>          end if
> 
>          Fdrag = Fdrag * s% x_ctrl(5)  ! scale by the user-defined factor
> ```
> For the full implementation, see [here](https://heibox.uni-heidelberg.de/f/d79187f0f7494dfa91e4/?dl=1).
>
> Now, the drag force in the supersonic regime is a bit weaker. Therefore, the plunge-in takes longer. The orbital separation after 2 years of CE is $\sim 74.1~\mathrm{R}_\odot$.
> {{< /details >}}



 **Note on assumptions, limitations and points to improve**
- CE is not point-symmetric (not 1D) $\rightarrow$ our models only valid for low mass ratios, i.e., $M_2/M_1 \ll 1$
- drag force only valid of straight line motion
- there exist other drag force prescriptions that take the circular motion into account (e.g. [Kim & Kim 2007](https://doi.org/10.1086/519302))
- no mass loss in this CE simulation, therefore no mass CE ejection possibility
- no angular momentum transfer from companion to envelope