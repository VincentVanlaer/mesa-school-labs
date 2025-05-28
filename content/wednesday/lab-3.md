## Wednesday Mini-lab 3: Upsilon Sagittarii 
Upsilon Sagittarii is a hydrogren deficient binary that has been suggested to be in its second stage of mass transfer, after the primary has expanded to become a helium supergiant following core helium exhaustion. [Gilkis & Tomer 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract) have identified the progentitor of this system to be a $5 M_{\odot}$ star with a $3.125 M_{\odot}$ companion and an initial orbital period of 8.4 days.

You will modify `src/run_binary_extras.f90` to capture the simulation at the values as determined from the observations of the binary system. Because the track is rather complicated, as can be seen in the figure below, we will slowly build up to finding the right combination of stopping criteria to match the models with the system.

![image](HRDUpsSag.png)

*The HRD of the best fitting model from the paper along with the data points from the observations.*

The stellar parameters can be found in this table, which has been adapted from Table 1 of [Gilkis & Tomer 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract).
| Parameter       | Value       |
| -----------     | ----------- |
| $T_{eff,1}[kK]$      | $10\pm1$       |
| $T_{eff,2}[kK]$      | $23\pm2$        |
| $logL_{1}[L_{\odot}]$    | $3.67\pm0.15$       |
| $logL_{2}[L_{\odot}]$    | $3.1\pm0.2$        |

## Task 1
To start, you will try to capture the simulation with only one stopping criterion, the effective temperature. Use the following parameter in the `extras_binary_finish_step` hook in `run_binary_extras.f90`: 

`b% s1% teff` ! Effective temperature of the primary star of the binary system in Kelvin

Then, to compare with the observational data, add a write statement to your stopping criterion to print the effective temperature and the luminosity of the stopping point.

Because the Roche-lobe overflow phase is computationally heavy for this particular system, the run will start shortly after. The saved model files are in 'Load', and you will need to adjust the path to the files in `inlist1` and `inlist2`.

<details>
  <summary>Hint 1</summary>

It is important to check the units of the parameters in MESA as compared to the units given in the literature. The effective temperature is given in kK in the table, while MESA uses Kelvin in the output.

</details>
<details>
  <summary>Hint 2</summary>
  
  `write(*,*) "(your text)", (values) `
  
 is used to print text to the terminal by calling the appropriate values.
</details>


<details>
  <summary>Solution 1</summary>
  
  ```fortran
         if ((b% s1% teff) .gt. 9000) then
               extras_binary_finish_step = terminate
               write(*,*) "terminating at requested effective temperature and luminosity:", b% s1% teff, log10(b% s1% l_surf)
               return
         end if
```
</details>

## Task 2
In Task 1 we have determined that working with just the effective temperature will not lead to a match between the simulation and the observations, as the luminosity is too low compared to the observations. In this next task, we will combine the luminosity and the effective temperature of the primary star to match the observations.
Use the following additional parameter in the `extras_binary_finish_step` hook in `run_binary_extras.f90`: 

`b% s1% l_surf` ! The luminosity of the primary star of the binary system in solar luminosities


<details>
  <summary>Hint 1</summary>

As can be seen in the figure, the stellar evolution track does not go through center of the data points. You will need to experiment with the error-margins to match the stellar track with the observations.

</details>

<details>
  <summary>Solution 1</summary>
  
  ```fortran
         if (((b% s1% teff) .lt. 9000) .and. (log10(b% s1% l_surf) .gt. 3.57))   then
               extras_binary_finish_step = terminate
               write(*,*) "terminating at requested effective temperature and luminosity:", b% s1% teff, log10(b% s1% l_surf)
               return
         end if  
```
</details>

## Task 3
Because we are working with a binary system, it is not only important to match the primary star, but also the secondary. In the previous task, you have matched the simulations and the observations for the primary star. In this task, you will add a stopping criterion for the secondary star and try to match both stars with the models. Before you start your new run, enable the evolution of the secondary by setting the `evolve_both_stars` in `inlist_project` command to `.true.`
Use the following additional parameter in the `extras_binary_finish_step` hook in `run_binary_extras.f90`: 

`b% s2% teff` ! Effective temperature of the primary star of the binary system in Kelvin

`b% s2% l_surf` ! The luminosity of the primary star of the binary system in solar luminosities


<br><br><br><br>
### Acknowledgement
The MESA input files were built upon the following resource:  
[Gilkis & Tomer 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract)
