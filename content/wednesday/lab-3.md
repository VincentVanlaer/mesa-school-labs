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
Fdrag = s% x_ctrl(5) *  4*pi*rho_r*(G * M2 / vrel)**2 * I
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
>          Ra = 2.0d0 * G * M2 / vrel**2
> 
>          ! compute the drag force
>          ! first, get Ostriker (1999) because needed for both implementations
>          if (Mach_r < 1.0d0) then
>             I = 0.5d0 * log((1.0d0 + Mach_r) / (1.d0 - Mach_r)) - Mach_r
>          else
>             I = 0.5d0 * log( 1.0d0 - 1.0d0/Mach_r**2) + log(2*a / r_min)
>          end if
>          Fdrag_Ost = 4*pi*rho_r*(G * M2 / vrel)**2 * I
> 
>          if (s% x_logical_ctrl(1)) then
>             ! use  MacLeod & Ramirez-Ruiz (2015)
>             eps_rho = H_P_r / Ra 
>             f_mod = 1.91791946 - 1.52814698 * eps_rho + 0.75992092 * eps_rho**2
>             Fdrag_Mac = pi * Ra**2 * vrel**2 * rho_r * f_mod
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