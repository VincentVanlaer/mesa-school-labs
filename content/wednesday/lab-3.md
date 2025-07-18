---
author: Vincent Bronner (lead TA), Hannah Brinkman, Harim Jin, Eva Laplace, Amadeusz Miszuda
---

# Common Envelope evolution with MESA

## Introduction

In this part of the lab, we explore how we can model the common envelope (CE) phase of binary stars using MESA. We use MESA's single star module `star` to evolve the donor star. The effect of the companion star is modeled on top of that in the `run_star_extras.f90` file.

![CE cartoon](/wednesday/CE_cartoon.png)

**Fig. 1**: Cartoon illustrating the 1D CE method. The companion (black dot) is spiraling inside the giant star. The black and blue arrows indicate the relative velocity of the companion and the drag force respectively. The heating zone is highlighted by the purple ring (taken from [Bronner et al. (2024)](https://doi.org/10.25518/0037-9565.12322))

We initiate the CE run by placing the companion star of mass $M_2$ at an orbital separation $a_\mathrm{ini}= 0.99R_1$ where $R_1$ is the radius of the donor star. At this point, the companion star is subject to dynamical friction, which leads to loss of angular momentum and orbital energy, leading to a decrease in the orbital separation. We can model the strength of the drag force by using the formulation from [Ostriker (1998)](https://ui.adsabs.harvard.edu/link_gateway/1999ApJ...513..252O/doi:10.1086/306858)
$$
F_\mathrm{drag} = \frac{4\pi (G M_2)^2\rho}{v_\mathrm{rel}^2} I,
$$
where $G$ is the gravitational constant, $v_\mathrm{rel}$ is the relative velocity between the donor star and the companion star, $\rho$ is the density of the donor star at the location of the companion star, and $I$ is the Coulomb logarithm. 
{{< details title="The Coulomb logarithm" closed="true" >}}
For subsonic motion, the Coulomb logarithm is given by
$$
I_\mathrm{subsonic} = \frac{1}{2} \ln \left( \frac{1 + \mathcal{M}}{1 - \mathcal{M}} \right) - \mathcal{M},
$$
where $\mathcal{M} = v_\mathrm{rel}/c_s$ is the Mach number and $c_s$ is the sound speed. For supersonic motion, the Coulomb logarithm can be approximated as
$$
I_\mathrm{supersonic} = \frac{1}{2} \ln \left( \frac{1}{1 - \mathcal{M}^2} \right) + \ln \left( \frac{2 a}{r_\mathrm{min}} \right),
$$
where $a$ is the orbital separation and $r_\mathrm{min}$ relates to the size of the companion star. 
{{< /details>}}

Now that we know the strength of the drag force, we can calculate the change in orbital energy $E_\mathrm{orb}$ caused by the drag force. The change in orbital energy over one timestep $\Delta t$ is given by
$$
\Delta E_\mathrm{orb} = F_\mathrm{drag} v_\mathrm{rel} \Delta t.
$$
The change in orbital energy can be related to the change in orbital separation by
$$
\Delta E_\mathrm{orb} = -\frac{G M_{1,a} M_2}{2 a} + \frac{G M_{1,a^\prime} M_2}{2 a^\prime} = -\frac{G M_1 M_2}{2} \left( \frac{1}{a} - \frac{1}{a^\prime} \right),
$$
where $a^\prime$ is the new orbital separation, assuming that $M_{1,a}$ is roughly constant and that the orbit stays circular. Thus, we can model the evolution of the orbital separation.

The back reaction of the drag force on the donor star is modeled by using the `other_energy`-hook that allows us to modify the internal energy (heating/cooling). Because we know how much orbital energy is dissipated by the drag force (see above), we can add exactly the same amount of energy as heat in the envelope of the donor star. We heat all the layers within one accretion radius $R_\mathrm{a}$ of the companion star, with
$$
R_\mathrm{a} = \frac{2 G M_2}{v_\mathrm{rel}^2}.
$$
Additionally, we use a Gaussian weighting kernel $\propto \exp[-(\Delta r/R_\mathrm{a})]$ to have a smooth heating profile, where $\Delta r = |r - a|$.

# Tasks to complete

## Task 1. Check out the `run_star_extras.f90` file
Please download the provided MESA directory from **[⬇ here](/mesa-school-labs-2025/wednesday/lab3_base_dir.zip)**. This includes many files, most of which you can ignore for now. Have a close look at the `src/run_star_extras.f90` file, especially the `other_energy` hook and the `extras_finish_step` function. Try to understand how the drag force is calculated and how it is used to update the orbital separation.

{{< details title="Solution" closed="true" >}}
The drag force is calculated in line 352 and the orbital separation is updated in line 358. We are making use of the `xtra(i)` variables in the `star_info` structure. These are particularly handy as we do not have to worry about things going wrong, if MESA decides to do a `retry`.

All the heating is done in the `CE_heating` function at the end of the file.
{{< /details >}}


## Task 2. Run the CE model
Run the CE model with the provided `inlist*` files. You are provided with a $12\,\mathrm{M}_\odot$ red supergiant model (taken after core helium exhaustion from the `12M_pre_ms_to_core_collapse` test suite) and a $1.4\,\mathrm{M}_\odot$ companion star (could be a neutron star). Everything is already implemented as described above. You only need to focus on `inlist_CE`. The other inlists are taken from the test suite and not modified. So you really just have to do `./mk && ./rn`. Have a look at how the orbital separation changes over time and try to identify the different phases of CE evolution. The orbital separation is directly printed to the terminal but also saved to the `history.log` as `separation`. You can use the [MESA explorer](https://billwolf.space/mesa-explorer/) to visualize `separation` vs `star_age` (you need to upload your `history.log`file).

{{< details title="Solution" closed="true" >}}
The orbital separation is $\sim 41.1 \, {\rm R}_\odot$ after 2 years of CE evolution.
![CE separation annotated](/wednesday/CE_separation_annotated.png)
{{< /details >}}


## Task 3. Change the companion mass
Run the same setup but vary the mass of the companion star. What happens if you increase the mass of the companion star? What happens if you decrease it? How does this affect the orbital separation? **What could be the physical reson for this behavior?** We have tested the cases for $ 0.5\,\mathrm{M}_\odot \leq M_2 \leq 2.0\,\mathrm{M}_\odot$. Depending on the companion mass, you might need to adjust the stopping criterion in the `inlist_CE` file.

{{< details title="Hint (companion mass)" closed="true" >}}
Have a close look at the `inlist_CE` file. Try to spot the `x_ctrl` variable that corresponds to the companion mass.
{{< /details >}}

{{< details title="Hint (stopping criterion I)" closed="true" >}}
At the moment, the run is stopped after two years. This way, we can see all three phases of the CE evolution (loss of corotation, plunge in, and the slow spiral-in phase. For different companion masses, the duration of these phases can be shorter/longer. Adjust the stopping criterion such that all three phases are covered.)
{{< /details >}}

{{< details title="Hint (stopping criterion II)" closed="true" >}}
There are two topping criterions in the `inlist_CE` file. They are `max_model_number` and `max_age`. Use the `max_age` to define the total simulated time.
> [!NOTE]
> The `max_model_numer` stopping criterion is often used to avoid "infinite" MESA runs, in cases were numerical issues lead to small timesteps. In such cases, the `max_age` stopping condition by itself can take many steps to reach.
{{< /details >}}

{{< details title="Solution" closed="true" >}}
The variable `x_ctrl(1)` in `inlist_CE` determines the mass of the companion. For more massive companions, the orbital separation after the plunge-in phase is larger. When visualizing the orbital evolution over time, the more massive companion plunges in faster compared to less massive companion. 
![CE separation for different companion masses](/wednesday/CE_separation_masses.png)
{{< /details >}}

## Task 4. Modify the drag force
The current implementation of the drag force is based on the assumption that the companion star is moving on a straight path through a uniform density background. This is not the case during the CE phase. In a more realistic scenario, the drag force may be weaker. Implement a free parameter in the drag force calculation that allows you to scale the drag force by a global factor $C_\mathrm{drag}$. Implement it such that you can control this factor from the `inlist_CE` file. What happens if you set $C_\mathrm{drag} = 0.5$? Is this what you expected? 

> [!CAUTION]
> Don't forget for run `./clean` and `./mk` after modifying the `run_star_extras.f90` file.

{{< details title="Hint" closed="true" >}}
You might want to define a `x_ctrl` variable in the `inlist_CE` file that you can use as a global pre-factor for the drag force. Try to locate the line where the drag force in computed in the `run_star_extras.f90`. 
> [!CAUTION]
> And don't forget for run `./clean` and `./mk` after modifying the `run_star_extras.f90` file.
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
Fdrag = s% x_ctrl(5) *  4*pi*rho_r*(G * M2 / vrel)**2 * I
```
You can find a full implementation **[⬇ here](/mesa-school-labs-2025/wednesday/lab3_task4_solution.zip)**.

For $C_\mathrm{d}<1$ the plunge-in takes longer and the separation afterwards is a little larger. This is expected as the drag force is generally weaker. For $C_\mathrm{d} = 0.5$, the orbital separation after two years of CE evolution is $\sim 57.2\,\mathrm{R}_\odot$.
{{< /details >}}

## Task 5. Modify the drag force prescription
Let's extend the drag force prescription to include the density gradient of the envelope. Implement the drag force prescription from [MacLeod & Ramirez-Ruiz (2015)](https://doi.org/10.1088/0004-637X/803/1/41) in the `run_star_extras.f90` file. The drag force is given by
$$
 F_\mathrm{drag} = \pi R_\mathrm{a}^2 v_\mathrm{rel}^2\rho(c_1 + c_2 \epsilon_\rho + c_3 \epsilon_\rho^2)
$$
with $\epsilon_\rho = H_P/R_\mathrm{a}$ the ratio of the local pressure scale height and the accretion radius. The pre-factors are $(c_1, c_2, c_3) = (1.91791946, −1.52814698, 0.75992092)$. This prescription is only valid for supersonic motion. For subsonic motion, we will continue using to the current implementation. Try to implement it such that there is a smooth transition for $0.9 < \mathcal{M} < 1.1$ between the two prescriptions.

{{< details title="Hint 1 (Where to start)" closed="true" >}}
You can take the current implementation of the drag force as a starting point for this task. Try to locate in the `run_star_extras.f90` where the drag force is computed. Take this as the starting point and modify the old calculation of the drag force to the new prescription. 
{{< /details >}}

{{< details title="Hint 2" closed="true" >}}
You need to get the local pressure scale height. This is stored in the `star_info` structure. Have a look at `$MESA_DIR/star_data/public/star_data_step_work.inc` and try to find the correct name for it. If you cannot find it, have a look at hint 2.
{{< /details >}}

{{< details title="Hint 3" closed="true" >}}
The pressure scale height is called `scale_height` and can be accessed via `s% scale_height(k)` for zone `k`.
{{< /details >}}

{{< details title="Hint 4" closed="true" >}}
For a smooth transition for $0.9 < \mathcal{M} < 1.1$ you can define an auxiliary variable $\alpha = \frac{\mathcal{M} - 0.9}{1.1-0.9}$. Then the drag force in the transition region is given by
$$
F_\mathrm{drag} = \alpha F_\mathrm{drag}^\mathrm{MacLeod} + (1 - \alpha)F_\mathrm{drag}^\mathrm{Ostriker}
$$
{{< /details >}}


{{< details title="Hint 5" closed="true" >}}
Make sure that you use the pressure scale height at the correct radius coordinate. This could be done, for example, by defining a new variable `Hp_r` at the beginning of the `extras_finish_step` function. Then, in the first `DO`-loop, you can assign this variable the pressure scale height of the desired zone (`Hp_r = s% scale_height(k)`).
{{< /details >}}

{{< details title="Solution" closed="true" >}}
Now, the drag force in the supersonic regime is a bit weaker. Therefore, the plunge-in takes longer. The orbital separation after 2 years of CE is $\sim 74.1~\mathrm{R}_\odot$.
For the full implementation, see **[⬇ here](/mesa-school-labs-2025/wednesday/lab3_task5_solution.zip)**.
{{< /details >}}


## Task 6. (Bonus) Compute the gravitational-wave merger time
Now, we want to explore the effect of CE evolution on the gravitational wave (GW) inpiral time. The formula for the GW merger time was already introduced in the previous lab:
$$t_{\mathrm{merge}} = \frac{5}{256} \cdot \frac{c^5 a^4}{G^3 M_1 M_2 (M_1 + M_2)}.$$

Write a `subroutine` in `run_star_extras.f90` that computes the merger time (in Gyr) and prints this to the terminal. Reuse as much code as possible from the previous lab. Call this subroutine at the beginning and at the end of the simulation and compare the difference. What are the implications for observed GW mergers and a possible CE history of the system? How do the results differ from the GW merger times in Lab 2? What consequences does this have on binary star evolution leading to GW mergers?

> [!TIP]
> Use this structure for the new subroutine. Add it to the end of the `run_star_extras.f90` file (in between `end subroutine extras_after_evolve` and `end module run_star_extras`).
> ```fortran
>      subroutine GW_merger_time(id)
>         integer, intent(in) :: id
>         integer :: ierr
>         type (star_info), pointer :: s
>         ierr = 0
>         call star_ptr(id, s, ierr)
>         if (ierr /= 0) return
>
>         ! ADD YOUR CODE HERE:
>         ! don't forget to declare any variables before use 
>         ! at the beginning of this subrouinte
>         ! ...
>         ! write(*,*) "GW merger time", <the GW merger time you computed above>
>
>      end subroutine GW_merger_time
> ```
>
> Later, you can call this subroutine with the following syntax:
> ```fortran
> call GW_merger_time
> ```
> This executes the subroutine and prints the merger timescale to the terminal.

> [!IMPORTANT]
> For this task, it is fine to assume that $M_1$ is constant. For a real CE event, $M_1$ can reduce over time because of envelope ejection.


> [!CAUTION]
> And don't forget for run `./clean` and `./mk` after modifying the `run_star_extras.f90` file.


{{< details title="Hint (when to call the subroutine I)" closed="true" >}}
We want to know the GW merger time at the beginning and at the end of the simulation. Use the flowchart to figure out in which `extras_*` function you have to place the `call GW_merger_time` statement.
![MESA flow](/wednesday/flowchart.png)
{{< /details >}}

{{< details title="Hint (when to call the subroutine II)" closed="true" >}}
The function `extras_startup` is called directly before the first time step. This is the ideal place to calculate the initial GW merger time, because at this point of time, the model is already loaded into MESA. The final GW merger time is best computed in `extras_after_evolve`, because this function is only called once at the very end of the MESA run.
{{< /details >}}

{{< details title="Hint (constants and units)" closed="true" >}}
You can access various physical constants directly in the `run_start_extras.f90`. They are loaded in by default at the very beginning with `use const_def` (you can see the full list of constants here `$MESA_DIR/const/public/const_def.f90`). We only need the gravitational constant $G$ and the speed of light $c$. It is best to do all the calculations in cgs units (all the constants are also in cgs units). Finally we need to convert the merger time to Gyr. The following lines should help you with all the constants and unit conversions:

```fortran
         G = standard_cgrav  ! gravitational constant (cgs)
         c = clight  ! speed of light (cgs)
         s_in_Gyr = 3600d0 * 24d0 * 365.25d0 * 1d9  ! seconds in a Gyr
```
{{< /details >}}

{{< details title="Solution" closed="true" >}}
This is the full subroutine for calculating the GW merger time:
```fortran
      subroutine GW_merger_time(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s

         real(dp) :: M1, M2, a, G, c, t_merge, s_in_Gyr

         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return

         M1 = s% star_mass * Msun  ! mass of the primary star (cgs)
         M2 = s% x_ctrl(1) * Msun ! mass of the companion (cgs)
         a = s% xtra(2)  ! separation (cgs)
         G = standard_cgrav  ! gravitational constant (cgs)
         c = clight  ! speed of light (cgs)
         s_in_Gyr = 3600d0 * 24d0 * 365.25d0 * 1d9  ! seconds in a Gyr

         ! compute the merger time using Peters (1964)
         t_merge = 5d0/256d0 * (pow5(c) * pow4(a)) / (pow3(G) * M1 * M2 * (M1 + M2)) 
         write(*,*) "Merger time [Gyr]", t_merge / s_in_Gyr

      end subroutine GW_merger_time
```
The modified `extras_startup` and `extras_after_evolve` could look like this:

```fortran
      subroutine extras_startup(id, restart, ierr)
         integer, intent(in) :: id
         logical, intent(in) :: restart
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return

         ! ... (other stuff)

         ! get the merger time
         call GW_merger_time(id)

      end subroutine extras_startup
```

```fortran
      subroutine extras_after_evolve(id, ierr)
         integer, intent(in) :: id
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return

         ! get the merger time
         call GW_merger_time(id)

      end subroutine extras_after_evolve
```

For the fiducial model ($M_2=1.4\,\mathrm{M}_\odot$ and $C_\mathrm{drag} = 1.0$), the initial merger time is $2\times 10^8$ Gyr, and the final merger time is $2\times 10^{3}$ Gyr. The merger time is reduced by a factor of $10^5$ during CE, increasing the strength of GWs and speeding up the merger. However, even the final merger time is much longer than the age of the Universe ($~14$ Gyr). But further mass transfer episodes may bring the binary even closer and reduce the GW merger time. Compared to lab 2, we see hat CE is much more efficient in reducing the merger time compared to mass transfer, making CE evolution a likely formation channel for the observed GW mergers.
For the full implementation, see **[⬇ here](/mesa-school-labs-2025/wednesday/lab3_bonus_solution.zip)**.

{{< /details >}}


## Assumptions, limitations, and points to improve

> [!NOTE]
> - CE is not point-symmetric (not 1D) $\rightarrow$ our models only valid for low mass ratios, i.e., $M_2/M_1 \ll 1$
> - drag force only valid of straight line motion
> - there exist other drag force prescriptions that take the circular motion into account (e.g. [Kim & Kim 2007](https://doi.org/10.1086/519302))
> - no mass loss in this CE simulation, therefore no mass CE ejection possibility
> - no angular momentum transfer from companion to envelope
