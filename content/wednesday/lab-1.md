## Introduction
Over the past decade, it has become clear that most massive stars are born in binary or multiple-star systems. Throughout their evolution, these stars undergo various interactions that can significantly alter their properties. One such interaction is **mass transfer**, where stars exchange mass and angular momentum. Mass transfer plays a crucial role in producing various stellar phenomena, such as different types of core-collapse supernovae, magnetic stars, X-ray sources, and gravitational wave sources. The nature of these phenomena depends on **when the mass transfer occurs** and whether it is **stable or unstable**. In this lab, we will explore mass transfer across the initial binary parameter space.

## Task 1. Identifying different mass transfer cases
*The MESA work directory for this task can be downloaded from [here](https://heibox.uni-heidelberg.de/f/e438b0ef7cb64b90a497/?dl=1).*

Mass transfer can be divided into three cases based on the evolutionary phase of the primary star (the initially more massive star) when the transfer occurs. The primary star evolves faster, fills its Roche lobe, and begins transferring mass to the secondary star (the initially less massive star). The three cases are:
Case A: The primary is undergoing core hydrogen burning.
Case B: The primary is undergoing core helium burning.
Case C: The primary has reached the end of core helium burning (also called core helium depletion).

We will modify `src/run_binary_extras.f90` to capture different mass transfer cases for a given system with the following initial conditions: 20Msun (initial primary mass) + 12Msun (initial secondary mass) with an initial orbital period of 100 days. When you do a MESA run, do "rn | tee out.txt" to save the terminal output into a file.

Use the following parameters in the `extras_binary_finish_step` hook in `run_binary_extras.f90`:  
`b% s1% center_h1` ! Hydrogen mass fraction at the center of the primary  
`b% s1% center_he4` ! Helium mass fraction at the center of the primary  
`b% mtransfer_rate` ! Mass transfer rate in g/s (negative)

The first goal is to capture when mass transfer happens, based on the mass transfer rate exceeding $10^{-10}$ Msun/yr.

{{< details title="Hint 1" closed="true" >}}
It is important to check the units of the parameters in MESA. In many cases, it is in cgs units. ```b% mtransfer_rate``` is in g/s. Use the variables secyr (seconds in a year) and Msun (solar mass in grams) to convert g/s into Msun/yr. You can use the variables directly in ```run_binary_extras.f90```.
{{< /details >}}

{{< details title="Solution 1" closed="true" >}}
```fortran
  abs(b% mtransfer_rate)/Msun*secyer > 1d-10
```
{{< /details >}}

The second goal is to capture different burning phases:
1. Core hydrogen burning phase
2. Core helium burning phase
3. Core helium depletion onwards


{{< details title="Hint 2" closed="true" >}}
Check the mass fractions of hydrogen (```b% s1% center_h1```) and helium (```b% s1% center_he4```) to determine the current burning phase. Check how core carbon depletion is captured in the "HINT" block. In the case of hydrogen and helium, check whether the mass fractions of hydrogen and helium are above or below 1e-6.
{{< /details >}}


{{< details title="Solution 2" closed="true" >}}
Core hydrogen burning phase: ```b% s1% center_h1 > 1e-6```  
Core helium burning phase: ```(b% s1% center_he4 > 1e-6) .and. (b% s1% center_h1 < 1e-6)```  
The phase after core helium depletion: ```b% s1% center_he4 < 1e-6```
{{< /details >}}

Finally, think of a way to print out "Case A", "Case B", and "Case C" in the terminal, depending on the different burning phases of the primary while mass transfer is happening. 

{{< details title="Hint 3" closed="true" >}}
Check how to print a string in the terminal at core carbon depletion in the "HINT" block.
{{< /details >}}


{{< details title="Solution 3" closed="true" >}}
```fortran
   !!!!! TASK 1 block begins !!!
   if ((b% s1% center_h1 > 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)) then
       write(*,*) '****************** Case A ******************'
   else if ((b% s1% center_h1 < 1d-6) .and. (b% s1% center_he4 > 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)) then
       write(*,*) '****************** Case B ******************'
   else if ((b% s1% center_he4 < 1d-6) .and. (abs(b% mtransfer_rate)/Msun*secyer > 1d-10)) then
       write(*,*) '****************** Case C ******************'
   end if   
   !!!!! TASK 1 block ends !!!
```
{{< /details >}}


## Task 2. Determine mass transfer stability
In some cases, mass transfer becomes unstable, leading the binary to enter a common-envelope phase. 

***
**Bonus exercise:**  
If you have many cores, run a binary model with the following initial binary parameters:  
m1 = 20  
m2 = 6  
initial_period_in_days = 5  
What do you see in the screen output? Can you identify which parameter is changing?  
***

One way to detect this instability is to check the mass transfer rate and the timestep. If the mass transfer rate is high and the timestep becomes very small (on the order of seconds to minutes), it is an indication that unstable mass transfer has started.

Use `b% mtransfer_rate` (mass transfer rate in g/s, negative) and `b% s1% dt` (timestep in seconds) in `extras_binary_finish_step` hook in `run_binary_extras.f90`. Make a code to terminate the run when the mass transfer rate is above $10^{-3}$ Msun/yr the timestep falls below 0.1 year, which is enough to capture the unstable mass transfer event, and print "Terminated due to unstable mass transfer" in the terminal. If the mass transfer was stable or there was no mass transfer, the run should end with the printout "Terminated due to core carbon depletion" in the terminal.


{{< details title="Hint" closed="true" >}}
Check how to terminate the MESA run in the "HINT" block.
{{< /details >}}

{{< details title="Solution" closed="true" >}}
```fortran

         !!!!! TASK 2 block begins !!!
         if ((abs(b% mtransfer_rate)/Msun*secyer > 1d-3) .and. (b% s1% dt < 3d6)) then
             write(*,*) '**********************************************'
             write(*,*) '** Terminated due to unstable mass transfer **'
             write(*,*) '**********************************************'
             extras_binary_finish_step = terminate
         end if
         !!!!! TASK 2 block ends !!!

```    
{{< /details >}}

## Task 3. Run a model with random initial binary parameters
Now, we will explore different mass transfer cases and their stability across the initial binary parameter space. We will fix an initial primary mass to 20 Msun. Choose a random initial mass ratio and an initial orbital period from the "Initial binary parameters" sheet in the following Google Spreadsheet:
https://docs.google.com/spreadsheets/d/1HLwsGPu6w3t2NMUcdVYvkHFvqgIOUDkigfrZruN6Uo8/edit?usp=sharing  
And perform MESA run with the corresponding initial parameters.

Observe the terminal output to check the case of the mass transfer when mass transfer begins (this is because Case A is always followed by Case B). If you missed it, you can do "grep -ir Case out.txt" to print out the occurrences of the string "Case" from the out.txt file. Record your results in the "P-q diagram" sheet in the Google Spreadsheet.

Parameters to Enter:  
**Initial mass ratio (M2/M1)**: A value between 0.1 and 0.9.  
**Initial orbital period**: A value between 1 and 3000 days.  
**Case**: One of A, B, or C.  
**Stable**: Enter y for stable mass transfer or n if terminated due to unstable mass transfer.  
If there was no mass transfer, leave **Case** and **Stable** blank.  

As many students input values, a pattern will emerge in the initial orbital period-mass ratio diagram. What kind of patterns do you see? Why do you think such patterns arise? Discuss with your group members.

***
**Bonus exercise:**  
Can you print out which mass transfer cases a binary system undergoes throughout its evolution at the end of the run? Try to capture all the cases. For example, Case A mass transfer is generally followed by Case B mass transfer. In this case, we want to print out "Case A + B" at termination.
***

# Task 4 (optional): Visualizing the effect of binary evolution with TULIPS
We can look at the outcome of binary evolution in more detail by visualizing our simulation results with TULIPS, a Python package for stellar evolution visualization. We will create movies of the changes in the properties of the donor and accretor in the binary system you simulated. For this exercise, you will need to upload the contents of your `LOGS1` and `LOGS2` output directories into this [Google Collab notebook](https://colab.research.google.com/drive/1tkEXYIyOM7sWmnKZu4Ds1I235lnZHD7i?usp=sharing).

Solutions can be found [here](https://drive.google.com/file/d/16T7aNaNFX93XDUfASpI-iFezYln4fTsv/view?usp=sharing).


### Acknowledgement
The MESA input files were built upon the following resource:  
https://wwwmpa.mpa-garching.mpg.de/~jklencki/html/massive_binaries.html
