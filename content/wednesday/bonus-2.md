## Wednesday Extra Bonus Task Lab 2: Upsilon Sagittarii

Upsilon Sagittarii is a binary system with a hydrogen depleted primary star. It has has been suggested that this system is in its second stage of mass transfer after the primary has expanded to become a helium supergiant following core helium exhaustion. [Gilkis & Shenar 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract) have identified the progenitor of this system to be a $5 M_{\odot}$ star with a $3.125 M_{\odot}$ companion and an initial orbital period of 8.4 days. The evolutionary track based on these parameters as well as the observations are shown in Figure 1. The observational parameters are given in Table 1, which has been adapted from [Gilkis & Shenar 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract).

![image](/wednesday/UpsSagHRD1.png)

**Fig. 1**: The HR diagram of the best fitting model from the paper along with the data points from the observations.

| Parameter       | Value       |
| -----------     | ----------- |
| $T_{eff,1}[kK]$      | $9\pm1$       |
| $T_{eff,2}[kK]$      | $23\pm2$        |
| $logL_{1}[L_{\odot}]$    | $3.67\pm0.15$       |
| $logL_{2}[L_{\odot}]$    | $3.1\pm0.2$        |

**Table 1**: The HR diagram of the best fitting model from the paper along with the data points from the observations.

Like in Task 1.1 of Lab 2, the aim of this mini-lab is to capture the simulations as determined from the observations of the binary system by using the `src/run_binary_extras.f90`. Because the track is rather complicated, as can be seen in the figure below, we will slowly build up to finding the right combination of stopping criteria to match the models with the system. Remember to recompile the code every time you change something in the `src/run_binary_extras.f90` with (`./clean && ./mk`) and run your new model! (`./rn`).

Unlike in the previous task, we are not starting from the standard work-directory, but rather from a cleaned-up version of the published set of inlists connected to the paper mentioned earlier. You can download them here (fill in a link!).

When working with many different settings within MESA, it is often beneficial to separate out the inlists into separate files. Lets have a look at the inlists in the work-directory. There are nine different files; `inlist`, `inlist1`, `inlist2`, `inlist_extra`, `inlist_other_winds`, `inlist_pgstar`, `inlist_project`, and `inlist_star`. 
Open the first file, `inlist`, with your favourite text editor. Like in most cases, this file only refers to other inlists which contain the parameters of the run.
Next, open the file `inlist` refers to, the `inlist_project`. In previous labs, the `inlist_project` contained all paramters. In this case, it refers to two other inlists for the settings of the primary star (`inlist1`) and the settings of the secondary star (`inlist2`). The other information in `inlist_project` is related to the binary physics, and it refers to the file `inlist_extra`.
The file `inlist_extra` contains basic settings for the binary run; the masses of the two stars and the initial period. Because these are the parameters changed in a grid-search as performed in the paper, it is easier to have them in a separate file.
`inlist1` and `inlist2` are as good as identical. The only difference between the two files is that different models are loaded and a few timestep controls. Both these inlists refer to `inlist_star` for star_job and control-settings and to `inlist_pgstar`.
`inlist_star` contains all the settings that are the same for the primary and the secondary, rather than putting them all in `inlist1` and `inlist2`. 
 `inlist_pgstar` is not used.
 The last inlist, `inlist_other_wind` is called via the `run_star_extras.f90`, and contains the values used for the alternative wind-scheme that is used for this model.
 

#### Extra Bonus Task 1
In this task, the aim is to capture the point where the simulation agrees with the observational data with only one stopping criterion, the effective temperature. Because the Roche-lobe overflow phase is computationally heavy for this particular system, the run will start shortly after the mass-transfer phase, which is indicated by the red dot in Figure 1 on the track of the primary star. The saved model files are available in 'Load'.

To make sure the models do not run too long, there is a maximum amount of models implemented in the `inlist_star`. To see if all runs well, compile (`./clean && ./mk`) and run your new model (`./rn`)! This is only to check if we set all the controls correctly, so kill the run after a few timesteps using `Ctrl C`.

To find the stopping point, use the following parameter in the `extras_binary_finish_step` hook in `run_binary_extras.f90`: 

`b% s1% teff` ! Effective temperature of the primary star of the binary system in Kelvin

Then, to compare with the observational data, add a write statement to your stopping criterion to print the effective temperature and the luminosity of the stopping point.

{{< details title="Hint 1" closed="true" >}}

It is important to check the units of the parameters in MESA as compared to the units given in the literature. The effective temperature is given in kK in the table, while MESA uses Kelvin in the output.

{{< /details >}}
       
{{< details title="Hint 2" closed="true" >}}

`write(*,*) "(your text)", (values)`
    
is used to print text to the terminal by calling the appropriate values.
{{< /details >}}

{{< details title="Solution" closed="true" >}}

There are multiple possible solutions. This is one example so you can continue to the next task.  

```fortran
if ((b% s1% teff) .gt. 9000) then
   extras_binary_finish_step = terminate
   write(*,*) "terminating at requested effective temperature and luminosity:", b% s1% teff, log10(b% s1% l_surf)
   return
end if
```
    
{{< /details >}}

#### Extra Bonus Task 2
In Extra Bonus Task 1 we have determined that working with just the effective temperature will not lead to a match between the simulation and the observations, as the luminosity is too low compared to the observations. In this next task, we will combine the luminosity and the effective temperature of the primary star to match the observations.
Use the following additional parameter in the `extras_binary_finish_step` hook in `run_binary_extras.f90`: 

`b% s1% l_surf` ! The luminosity of the primary star of the binary system in solar luminosities

{{< details title="Hint 1" closed="true" >}}
    
As can be seen in the figure above, the stellar evolution track does not go through center of the data points. You will need to experiment with the error-margins to match the stellar track with the observations.
   
{{< /details >}}

{{< details title="Solution" closed="true" >}}
  
There are multiple possible solutions, depending on how you combine the two parameters. This is one example so you can continue to the next task.
    
```fortran
if (((b% s1% teff) .lt. 9000) .and. (log10(b% s1% l_surf) .gt. 3.57))   then
    extras_binary_finish_step = terminate
    write(*,*) "terminating at requested effective temperature and luminosity:", b% s1% teff, log10(b% s1% l_surf)
    return
end if  
```

{{< /details >}}

#### Extra Bonus Task 3
Because we are working with a binary system, it is not only important to match the primary star, but also the secondary. However, matching two stars simultaneously is not a trivial task, and rather than fitting by eye like we are doing here, it is done with statistical methods. The best fit model presented in [Gilkis & Shenar 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract) thus does not match the exact observational values. So, instead of working with the observational values for the secondary, the model values will be used with the error-bars as presented in the literature, which is represented by the cyan cross in the HRD. The new values for the effective temperature and the luminosity are in the table below and were taken from Table 3 of the previously mentioned paper.

![image](/wednesday/UpsSagHRD2.png)

*The HRD of the best fitting model from the paper along with the data points from the observations and the location of the best fits.*

| Parameter       | Value       |
| -----------     | ----------- |
| $T_{eff,1}[kK]$      | $10\pm1$       |
| $T_{eff,2}[kK]$      | $21.2\pm2$        |
| $logL_{1}[L_{\odot}]$    | $3.67\pm0.15$       |
| $logL_{2}[L_{\odot}]$    | $3.5\pm0.2$        |

In the previous task, you have matched the simulations and the observations for the primary star. In this task, you will add a stopping criterion for the secondary star and try to match both stars with the models. Before you start your new run, enable the evolution of the secondary by setting the `evolve_both_stars` in `inlist_project` command to `.true.`
Use the following additional parameter in the `extras_binary_finish_step` hook in `run_binary_extras.f90`:

`b% s2% teff` ! Effective temperature of the primary star of the binary system in Kelvin

`b% s2% l_surf` ! The luminosity of the primary star of the binary system in solar luminosities

As in the previous tasks, write out the final luminosity and surface temperature of the simulation to the terminal.

{{< details title="Solution" closed="true" >}}

```fortran
if (((b% s1% teff) .lt. 9000) .and. (log10(b% s1% l_surf) .gt. 3.57) .and. ((b% s2% teff) .lt. 21200))   then
   extras_binary_finish_step = terminate
   write(*,*) "terminating at requested effective temperature and luminosity:", b% s1% teff, log10(b% s1% l_surf)
   write(*,*) "terminating at requested effective temperature and luminosity:", b% s2% teff, log10(b% s2% l_surf)
   return
end if  
```
    
{{< /details >}}


#### Extra Bonus Task 4
If you have managed to get the double stopping criterion to work, you can experiment with other observables as can be found in Table 1 and 3 of the paper, and see which combinations work. For this you can use the following commands:

`b% s1% surface_()` ! The surface abundance of the following isotopes: h1, he4, c12, n14, o16.

`b% s1% photosphere_r` ! The radius of the star in solar radii

`b% s1% photosphere_logg` !The surface gravity 

As in the previous parts, there are multiple combinations possible to reach the observed values for the stellar parameters or the modelled parameters. Not all combinations might work.


<br><br><br>
### Acknowledgement
The MESA input files were built upon the following resource:  
[Gilkis & Shenar 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract)
