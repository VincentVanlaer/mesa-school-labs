## Wednesday Mini-lab 3: Upsilon Sagittarii 
Upsilon Sagittarii is a hydrogren deficient binary that has been suggested to be in its second stage of mass transfer, after the primary has expanded to become a helium supergiant following core helium exhaustion. [Gilkis & Tomer 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract) have identified the progentitor of this system to be a 5 solar mass star with a 3.125 solar mass companion and an initial orbital period of 8.4 days.

We will modify `src/run_binary_extras.f90` to capture the simulation at the values as determined from the observations of the binary system. Because the track is rather complicated, we will slowly build up to finding the right combination of stopping criteria to match the models with the system.
The stellar parameters can be found in this table, which has been adapted from Table 1 of [Gilkis & Tomer 2022](https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.3541G/abstract).
| Parameter       | Value       |
| -----------     | ----------- |
| $T_{eff,1}[kK]$      | $10\pm1$       |
| $T_{eff,2}[kK]$      | $23\pm2$        |
| $logL_{1}[Lsun]$    | $3.67\pm0.15$       |
| $logL_{2}[Lsun]$    | $3.1\pm0.2$        |
| $R_{1}[Rsun]$       | $28\pm8$       |
| $R_{2}[Rsun]$       | $2.2\pm0.3$        |
| $logg_{1}[cm/s^{2}]$   | $1.0$            |

![landscape]()


## Task 1
To start, we will attempt to capture the simulation with only one stopping criterion, the effective temperature.
Use the following parameter in the `extras_binary_finish_step` hook in `run_binary_extras.f90`:  
`b% s1% center_h1` ! Hydrogen mass fraction at the center of the primary

The first goal is to capture when mass transfer happens, based on the mass transfer rate exceeding $10^{-10}$ Msun/yr.
## Task 2

## Task 3

```
fortran
f=4.d0
```
