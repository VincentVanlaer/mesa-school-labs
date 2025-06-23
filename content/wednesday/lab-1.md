## Introduction
Over the past decade, it has become clear that most massive stars are born in binary or multiple-star systems. Throughout their evolution, these stars undergo various interactions that can significantly alter their properties. One such interaction is **mass transfer**, where stars exchange mass and angular momentum. Mass transfer plays a crucial role in producing various stellar phenomena, such as different types of core-collapse supernovae, magnetic stars, X-ray sources, and gravitational wave sources. The nature of these phenomena depends on **when the mass transfer occurs** and whether it is **stable or unstable**. In this lab, we will explore mass transfer across the initial binary parameter space.

> [!NOTE]
> In this lab, we only evolve the primary star (the initially more massive star) in detail, assuming the secondary star (the initially less massive star) as a point mass due to timing issues. This option is done via `evolve_both_stars = .false.` in binary_job. This is the default option.  

## Task 1. Identifying different mass transfer cases
Mass transfer can be divided into three cases based on the evolutionary phase of the primary star when the transfer occurs. The primary star evolves faster, fills its Roche lobe, and begins transferring mass to the secondary star. The three cases are:
Case A: The primary is undergoing core hydrogen burning.
Case B: The primary is undergoing core helium burning.
Case C: The primary has reached the end of core helium burning (also called core helium depletion).

Now, let's download the MESA work directory. The MESA work directory for this task can be downloaded from [here](https://heibox.uni-heidelberg.de/f/e438b0ef7cb64b90a497/?dl=1).

> [!TIP]
> You can extract BinaryEvolution_Lab1.tar in the current directory through the following command:  
> `tar -xf BinaryEvolution_Lab1.tar`  
> After the extraction, enter the directory through the following command:  
> `cd BinaryEvolution_Lab1`  
> Now you are in the MESA work directory for this lab.

In the following subtasks, **we want to catch during which evolutionary phase the donor star undergoes mass transfer**. We will modify `src/run_binary_extras.f90` to capture different mass transfer cases for a given system with the following initial conditions: 20Msun (initial primary mass) + 12Msun (initial secondary mass) with an initial orbital period of 100 days. 

> [!IMPORTANT]
> In `run_binary_extras.f90`, you can use the quantities internally computed by MESA using the binary pointer `b%` and star pointers `s1%`/`s2%` to access the donor/accretor modules, respectively. In this lab, you will be using the following parameters:
>
>- `b% s1% center_h1`: Hydrogen mass fraction at the center of the primary  
>- `b% s1% center_he4`: Helium mass fraction at the center of the primary  
>- `b% mtransfer_rate`: Mass transfer rate in g/s (negative)
> 
> Use these parameters in the `extras_binary_finish_step` hook in `run_binary_extras.f90`

### Task 1-1. Is the primary undergoing mass transfer?
**As a first step, add in the " !!! TASK 1 block begins !!! " in the `run_binary_extras.f90` a if condition to check whether the primary is transferring mass or not. If it is undergoing a mass transfer, print out "Undergoing mass transfer" message in the terminal.** A good threshold to differentiate between mass-transfer and no mass-transfer is $10^{-10}$ Msun/yr. 

> [!WARNING]
> Don't forget to do `./clean` and `./mk` after modifying the `run_star_extras.f90` file.

{{< details title="Hint 1-1 (1)" closed="true" >}}
It is important to check the units of the parameters in MESA. In many cases, it is in cgs units. ```b% mtransfer_rate``` is in g/s. Use the constants secyer (seconds in a year) and Msun (solar mass in grams) to convert g/s into Msun/yr. You can use these directly in ```run_binary_extras.f90``` (thanks to this line `use const_def`).
{{< /details >}}


{{< details title="Hint 1-1 (2)" closed="true" >}}
! Convert mass transfer rate from g/s to Msun/yr  
! 1 year = 3.15576e7 s, 1 Msun = 1.989e33 g  
! Use: abs(b% mtransfer_rate)/Msun*secyer
{{< /details >}}


{{< details title="Hint 1-1 (3)" closed="true" >}}
Check how to print a string in the terminal at core carbon depletion in the "HINT" block in `run_star_extras.f90`.  
write(*,*) ' ... '
{{< /details >}}


{{< details title="Solution 1-1" closed="true" >}}
```fortran
         !!! TASK 1 block begins !!!
         if (abs(b% mtransfer_rate)/Msun*secyer > 1d-10) then
             write(*,*) '****************** Undergoing mass transfer ******************'
         end if
         !!! TASK 1 block ends !!!
```
{{< /details >}}

> [!TIP]
> When you do a MESA run via "./rn | tee out.txt", you can save the terminal output into a file.
> So, even when you miss the terminal output, you can check the out.txt file to see what was printed out during the run.
> Also, you can use "grep -ir XXX out.txt" to see if XXX is included in out.txt.

Please make sure that your implementation is working correctly by running a model and checking if it indeed gives the desired output when the mass-transfer rate exceeds the threshold. In the PGSTAR plot, you can find the mass transfer rate (blue line) in the upper right corner (`lg_mtransfer_rate` in logarithmic scale). This run should end with the following print out in the terminal:
```
 *********************************************
 **** Terminated at core carbon depletion ****
 *********************************************
```

### Task 1-2. Which evolutionary phase is the primary in?
As a next step, we now want to identify during which burning stage our model is undergoing mass transfer. Note that typically core hydrogen burning is considered to be finished when the central hydrogen abundance drops below 1e-6, and core helium burning is finished when the central helium abundance is below 1e-6. **Now think of conditions to identify which evolutionary state the primary is in, and print it out.** Please also test if your code compiles, to avoid propagating the errors.  
1. Core hydrogen burning phase  
2. Core helium burning phase  
3. Core helium depletion onwards

> [!WARNING]
> Don't forget to do `./clean` and `./mk` after modifying the `run_star_extras.f90` file.

{{< details title="Hint 1-2" closed="true" >}}
Check the mass fractions of hydrogen (```b% s1% center_h1```) and helium (```b% s1% center_he4```) to determine the current burning phase. Check how core carbon depletion is captured in the "HINT" block in `run_star_extras.f90`. In the case of hydrogen and helium, check whether the mass fractions of hydrogen and helium are above or below 1e-6.
{{< /details >}}


{{< details title="Solution 1-2" closed="true" >}}
```fortran
         !!! TASK 1 block begins !!!
         if (abs(b% mtransfer_rate)/Msun*secyer > 1d-10) then
             write(*,*) '****************** Undergoing mass transfer ******************'
         end if
         
         if (b% s1% center_h1 > 1e-6) then
             write(*,*) '****************** Core hydrogen burning ******************'
         else if ((b% s1% center_he4 > 1e-6) .and. (b% s1% center_h1 < 1e-6)) then
             write(*,*) '****************** Core helium burning ******************'
         else if (b% s1% center_he4 < 1e-6) then
             write(*,*) '****************** Past core helium burning ******************'
         end if
         !!! TASK 1 block ends !!!
```
{{< /details >}}

### Task 1-3. Print out Case A / B / C
As a last step, we want to output in the terminal which mass transfer case it is when there is a mass transfer. **Comment out the previous scripts in the "TASK 1" block and write new if-else statements that prints out Case A / B / C if the corresponding mass transfer is occuring.** Please compile your code and test your model. Can you identify which mass transfer case that your model underwent? If you missed the terminal output, you can check the out.txt file to see what was printed out during the run.

> [!WARNING]
> Don't forget to do `./clean` and `./mk` after modifying the `run_star_extras.f90` file.

If-else statements to print out Case A/B/C?
{{< details title="Hint 1-3 (1)" closed="true" >}}
```fortran
         !!! TASK 1 block begins !!!
!         if (abs(b% mtransfer_rate)/Msun*secyer > 1d-10) then
!             write(*,*) '****************** Undergoing mass transfer ******************'
!         end if
         
!         if (b% s1% center_h1 > 1e-6) then
!             write(*,*) '****************** Core hydrogen burning ******************'
!         else if ((b% s1% center_he4 > 1e-6) .and. (b% s1% center_h1 < 1e-6)) then
!             write(*,*) '****************** Core helium burning ******************'
!         else if (b% s1% center_he4 < 1e-6) then
!             write(*,*) '****************** Past core helium burning ******************'
!         end if

         if (Condition for Case A event) then
             write(*,*) '****************** Case A ******************'
         else if (Condition for Case B event) then
             write(*,*) '****************** Case B ******************'
         else if (Condition for Case C event) then
             write(*,*) '****************** Case C ******************'
         end if   
         !!! TASK 1 block ends !!!
```
{{< /details >}}

Condition for Case A event?
{{< details title="Hint 1-3 (2)" closed="true" >}}
```fortran
(b% s1% center_h1 > 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)
```
{{< /details >}}

Condition for Case B event?
{{< details title="Hint 1-3 (3)" closed="true" >}}
```fortran
(b% s1% center_h1 < 1d-6) .and. (b% s1% center_he4 > 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)
```
{{< /details >}}

Condition for Case C event?
{{< details title="Hint 1-3 (4)" closed="true" >}}
```fortran
(b% s1% center_he4 < 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)
```
{{< /details >}}


{{< details title="Solution 1-3" closed="true" >}}
```fortran
         !!! TASK 1 block begins !!!
!         if (abs(b% mtransfer_rate)/Msun*secyer > 1d-10) then
!             write(*,*) '****************** Undergoing mass transfer ******************'
!         end if
         
!         if (b% s1% center_h1 > 1e-6) then
!             write(*,*) '****************** Core hydrogen burning ******************'
!         else if ((b% s1% center_he4 > 1e-6) .and. (b% s1% center_h1 < 1e-6)) then
!             write(*,*) '****************** Core helium burning ******************'
!         else if (b% s1% center_he4 < 1e-6) then
!             write(*,*) '****************** Past core helium burning ******************'
!         end if

         if ((b% s1% center_h1 > 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)) then
             write(*,*) '****************** Case A ******************'
         else if ((b% s1% center_h1 < 1d-6) .and. (b% s1% center_he4 > 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)) then
             write(*,*) '****************** Case B ******************'
         else if ((b% s1% center_he4 < 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)) then
             write(*,*) '****************** Case C ******************'
         end if   
         !!! TASK 1 block ends !!!
```
{{< /details >}}

***
**Bonus exercise:**  
Can you print out which mass transfer cases a binary system undergoes throughout its evolution at the end of the run? Try to capture all the cases. For example, Case A mass transfer is generally followed by Case B mass transfer. In this case, we want to print out "Case A + B" at termination.
***


> [!TIP]
> **Got stuck** during the lab? Do not worry! You can always download solution from here **[⬇ Download](/mesa-school-labs-2025/wednesday/BinaryEvolution_Lab1.tar)** to catch up!


## Task 2. Determine mass transfer stability
In some cases, mass transfer becomes unstable, leading the binary to enter a common-envelope phase. 

***
**Bonus exercise:**  
If you have many cores (more than approx. 6), run a binary model with the following initial binary parameters:  
m1 = 20  
m2 = 6  
initial_period_in_days = 5  
You need to modify "inlist_extra", which contains handles for `binary_controls` for changing initial binary parameters.

```fortran
&binary_controls
   m1 = 20.0d0                     ! initial donor mass in Msun
   m2 = 12.0d0                     ! initial companion mass in Msun
   initial_period_in_days = 100d0  ! initial orbital period in days
/ ! end of binary_controls namelist
```
What do you see in the screen output? Can you identify which parameter is changing?  

> [!TIP]
> You can check the number of cores via:  
> grep -c ^processor /proc/cpuinfo       (in terminal for Linux)  
> echo %NUMBER_OF_PROCESSORS%            (in CMD for Windows)  
> sysctl hw.ncpu                         (in terminal for macOS)  
***

One way to detect this instability is to check the mass transfer rate and the timestep. If the mass transfer rate is high and the timestep becomes very small (on the order of seconds to minutes), it is an indication that unstable mass transfer has started.

Use `b% mtransfer_rate` (mass transfer rate in g/s, negative) and `b% s1% dt` (timestep in seconds) in !!! TASK 2 block begins !!! in `extras_binary_finish_step` hook in `run_binary_extras.f90`. **Make a code to terminate the run when the mass transfer rate is above $10^{-3}$ Msun/yr the timestep falls below 0.1 year, which is enough to capture the unstable mass transfer event, and print "Terminated due to unstable mass transfer" in the terminal.** If the mass transfer was stable or there was no mass transfer, the run should end with the printout "Terminated due to core carbon depletion" in the terminal. Until now, if it took a long time (more than approx. 20 mins), you can copy the solution and go to Task 3 :)

> [!WARNING]
> Don't forget to do `./clean` and `./mk` after modifying the `run_star_extras.f90` file.

{{< details title="Hint 2" closed="true" >}}
You can instruct MESA to stop computations by using `extras_binary_finish_step = terminate` at the right place. Check how to terminate the MESA run in the "HINT" block in `run_star_extras.f90`.
{{< /details >}}

{{< details title="Solution 2" closed="true" >}}
```fortran

         !!!!! TASK 2 block begins !!!
         if ((abs(b% mtransfer_rate)/Msun*secyer > 1d-3) .and. (b% s1% dt / secyer < 0.1)) then
             write(*,*) '**********************************************'
             write(*,*) '** Terminated due to unstable mass transfer **'
             write(*,*) '**********************************************'
             extras_binary_finish_step = terminate
         end if
         !!!!! TASK 2 block ends !!!

```    
{{< /details >}}

> [!TIP]
> **Got stuck** during the lab? Do not worry! You can always download solution from here **[⬇ Download](/mesa-school-labs-2025/wednesday/BinaryEvolution_Lab1.tar)** to catch up!

## Task 3. Run a model with random initial binary parameters
Now, we will explore different mass transfer cases and their stability across the initial binary parameter space. We will fix an initial primary mass to 20 Msun. Choose a random pair of initial mass ratio and an initial orbital period from the "P-q diagram" sheet in the following Google Spreadsheet, and put your name in the corresponding column:
https://docs.google.com/spreadsheets/d/1HLwsGPu6w3t2NMUcdVYvkHFvqgIOUDkigfrZruN6Uo8/edit?usp=sharing  
**And perform MESA run with the corresponding initial parameters.** You need to modify "inlist_extra", which contains handles for `binary_controls` for changing initial binary parameters.

```fortran
&binary_controls
   m1 = 20.0d0                     ! initial donor mass in Msun
   m2 = 12.0d0                     ! initial companion mass in Msun
   initial_period_in_days = 100d0  ! initial orbital period in days
/ ! end of binary_controls namelist
```

Observe the terminal output to check the case of the mass transfer when mass transfer begins (this is because Case A is always followed by Case B). If you missed it, you can do "grep -ir Case out.txt" to print out the occurrences of the string "Case" from the out.txt file. Record your results in the "P-q diagram" sheet in the Google Spreadsheet.

Parameters to Enter:  
**Initial mass ratio (M2/M1)**: A value between 0.1 and 0.9.  
**Initial orbital period**: A value between 1 and 3000 days.  
**Case**: One of A, B, or C.  
**Stable**: Enter y for stable mass transfer or n if terminated due to unstable mass transfer.  
If there was no mass transfer, leave **Case** and **Stable** blank.  


***
**Bonus exercise:**  
By default, you are asked to run one model.
If you have completed this task quickly, you can choose more pairs and run more input results.
Also, you can choose a random initial mass ratio and initial orbital period pair out of the pairs that are given in the sheet. 
If you do so, please append your values at the end of the original table.
***

As many students input values, a pattern will emerge in the initial orbital period-mass ratio (P-q) diagram. 
- Where are Case A / B / C systems located in the P-q diagram? Why? 
- How does the initial mass ratio affect the stability of mass transfer? Why?
- Do you see other interesting patterns? Why?
Discuss with your group members.


# Task 4 (optional): Visualizing the effect of binary evolution with TULIPS
![Example TULIPS visualization](https://astro-tulips.readthedocs.io/en/latest/_images/first_animation.gif "TULIPS visualization of the apparent size and color evolution of a massive star")

We can look at the outcome of binary evolution in more detail by visualizing our simulation results with [TULIPS](https://astro-tulips.readthedocs.io/), a Python package for stellar evolution visualization. We will create movies of the changes in the properties of a donor and accretor in a binary system pre-computed with MESA. For this exercise, you will need to upload the contents of the `LOGS1` and `LOGS2` output directories found [here](https://drive.google.com/drive/folders/1n_KliN8Jfmy0VXGFLE2o57U5_cy_oj0N?usp=sharing) into this [Google Collab notebook](https://colab.research.google.com/drive/1tkEXYIyOM7sWmnKZu4Ds1I235lnZHD7i?usp=sharing).

Solutions can be found [here](https://colab.research.google.com/drive/1SzbHAYd5nmnQsBCMpuESwpRVTS1o9X6j?usp=sharing).


### Acknowledgement
The MESA input files were built upon the following resource:  
https://wwwmpa.mpa-garching.mpg.de/~jklencki/html/massive_binaries.html
