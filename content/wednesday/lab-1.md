## Introduction
Over the past decade, it has become clear that most massive stars are born in binary or multiple-star systems. Throughout their evolution, these stars undergo various interactions that can significantly alter their properties. One such interaction is **mass transfer**, where stars exchange mass and angular momentum. Mass transfer plays a crucial role in producing various stellar phenomena, such as different types of core-collapse supernovae, magnetic stars, X-ray sources, and gravitational wave sources. The nature of these phenomena depends on **when the mass transfer occurs** and whether it is **stable or unstable**. In this lab, we will explore mass transfer across the initial binary parameter space.

## Task 1. Identifying different mass transfer cases
Mass transfer can be divided into three cases based on the evolutionary phase of the primary star (the initially more massive star) when the transfer occurs. The primary star evolves faster, fills its Roche lobe, and begins transferring mass to the secondary star (the initially less massive star). The three cases are:
Case A: The primary is doing core hydrogen burning.
Case B: The primary is doing core helium burning.
Case C: The primary has depleted core helium.

We will modify `src/run_binary_extras.f90` to capture different mass transfer cases for a given system with the following initial conditions: 20Msun (initial primary mass) + 12Msun (initial secondary mass) with an initial orbital period of 100 days. When you do a MESA run, do "rn | tee out.txt" to save the terminal output into a file.

Use the following parameters in the `extras_binary_finish_step` hook in `run_binary_extras.f90`:  
`b% s1% center_h1` ! Hydrogen mass fraction at the center of the primary  
`b% s1% center_he4` ! Helium mass fraction at the center of the primary  
`b% mtransfer_rate` ! Mass transfer rate in g/s

The first goal is to capture when mass transfer happens, based on the mass transfer rate exceeding $10^{-10}$ Msun/yr.

<details>
  <summary>Hint 1</summary>
  
It is important to check the units of the parameters in MESA. In many cases, it is in cgs units. ```b% mtransfer_rate``` is in g/s. Use the variables secyr (seconds in a year) and Msun (solar mass in grams) to convert g/s into Msun/yr. You can use the variables directly in ```run_binary_extras.f90```.
</details>

<details>
  <summary>Solution 1</summary>
  
  ```fortran
  b% mtransfer_rate/Msun*secyer > 1d-10
```
</details>

The second goal is to capture different burning phases:
1. Core hydrogen burning phase
2. Core helium burning phase
3. Core helium depletion onwards

<details>
  <summary>Hint 2</summary>
  
Check the mass fractions of hydrogen (```b% s1% center_h1```) and helium (```b% s1% center_he4```) to determine the current burning phase. Check how core carbon depletion is captured in the "HINT" block. In the case of hydrogen and helium, check whether the mass fractions of hydrogen and helium are above or below 1e-6.
</details>

<details>
  <summary>Solution 2</summary>
  
Core hydrogen burning phase: ```b% s1% center_h1 > 1e-6```  
Core helium burning phase: ```(b% s1% center_he4 > 1e-6) .and. (b% s1% center_h1 < 1e-6)```  
The phase after core helium depletion: ```b% s1% center_he4 < 1e-6```
</details>

Finally, think of a way to print out "Case A", "Case B", and "Case C" in the terminal, depending on the different burning phases of the primary while mass transfer is happening. 

<details>
  <summary>Hint 3</summary>
  Check how to print a string in the terminal at core carbon depletion in the "HINT" block. 
</details>

<details>
  <summary>Solution 3</summary>

  ```fortran
         !!!!! TASK 1 block begins !!!
         if ((b% s1% center_h1 > 1d-6) .and. (b% mtransfer_rate/Msun*secyer > 1d-10)) then
             write(*,*) '****************** Case A ******************'
         else if ((b% s1% center_h1 < 1d-6) .and. (b% s1% center_he4 > 1d-6) .and. (b% mtransfer_rate/Msun*secyer > 1d-10)) then
             write(*,*) '****************** Case B ******************'
         else if ((b% s1% center_he4 < 1d-6) .and. (b% mtransfer_rate/Msun*secyer > 1d-10)) then
             write(*,*) '****************** Case C ******************'
         end if   
         !!!!! TASK 1 block ends !!!
```
</details>

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

One way to detect this instability is to check the timestep. If the timestep becomes very small (on the order of seconds to minutes), it can be an indication that unstable mass transfer has started.

Use `b% s1% dt` (timestep in seconds) in `extras_binary_finish_step` hook in `run_binary_extras.f90`. Make a code to terminate the run when the timestep falls below 30 seconds, which is enough to capture the unstable mass transfer event, and print "Terminated due to unstable mass transfer" in the terminal. If the mass transfer was stable or there was no mass transfer, the run should end with the printout "Terminated due to core carbon depletion" in the terminal.

<details>
  <summary>Hint</summary>
  Check how to terminate the MESA run in the "HINT" block.
</details>

<details>
  <summary>Solution</summary>
  
  ```fortran
         !!!!! TASK 2 block begins !!!
         if (b% s1% dt < 30) then
             write(*,*) '************************************************'
             write(*,*) '*** Terminated due to unstable mass transfer ***'
             write(*,*) '************************************************'
             extras_binary_finish_step = terminate
         end if   
         !!!!! TASK 2 block ends !!!
```       
</details>

## Task 3. Run a model with random initial binary parameters
Now, we will explore different mass transfer cases and their stability across the initial binary parameter space. We will fix an initial primary mass to 20 Msun. Choose a random initial secondary mass from 1 to 19 Msun and an initial orbital period from 1 to 3000 days, and run the model.

Observe the terminal output to check the case of the mass transfer when mass transfer begins (this is because Case A is always followed by Case B). If you missed it, you can do "grep -ir Case out.txt" to print out the occurrences of the string "Case" from the out.txt file.

Record your results in the following Google Spreadsheet:
https://docs.google.com/spreadsheets/d/1HLwsGPu6w3t2NMUcdVYvkHFvqgIOUDkigfrZruN6Uo8/edit?usp=sharing

Parameters to Enter:  
**Initial mass ratio (M2/M1)**: A value between 0.05 and 0.95.  
**Initial orbital period**: A value between 1 and 3000 days.  
**Case**: One of A, B, or C.  
**Stable**: Enter y for stable mass transfer or n if terminated due to unstable mass transfer.  
If there was no mass transfer, leave **Case** and **Stable** blank.  

As many students input values, a pattern will emerge in the initial orbital period-mass ratio diagram. What kind of patterns do you see? Why do you think such patterns arise? Discuss with your group members.


<br><br><br><br>
### Acknowledgement
The MESA input files were built upon the following resource:  
https://wwwmpa.mpa-garching.mpg.de/~jklencki/html/massive_binaries.html
