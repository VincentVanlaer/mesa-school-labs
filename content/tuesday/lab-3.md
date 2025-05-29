---
weight: 1
author: Beatriz Bordadágua, Joey Mombarg, Philip Mocz, Tryston Raecke
math: true
---

## Introduction 

So far in our exploration of rotating stellar models, we have seen how instabilities can be modeled in MESA to approximate particular behavior present in 2D-ESTER models. We have also gone further to calculate the Eddington-Sweet circulation velocity in the 1D case and seen some differences against analogous 2D references. 

So what does this mean? Of course a 1D model and a 2D model are going to be different, right?

The good news is that we are not consigned to spend hours on HPC clusters for every test case. Instead, given a selective set of more expensive 2D models, we can *tune* our MESA model. Luckily, we have various levers we can turn to accomplish this. If we can establish an idea of what the velocity field *should* be, then we can implement it into MESA with hooks in `run_star_extras.f90`. In this lab, we will be doing just that. Beginning from a scaffolded starting point, you will implement a custom torque and angular momentum mixing routine in MESA, outputing data that can be compared against the tracks in [Mombarg et al., 2023](https://www.aanda.org/articles/aa/pdf/2023/09/aa47454-23.pdf)[^1] and [Mombarg et al., 2024](https://www.aanda.org/articles/aa/pdf/2024/03/aa48466-23.pdf)[^2].

### An aside about Meridional circulation

Starting from its name, meridional circulation is a convective flow that operates along the meridian (North-South). These flows are not unique to stars and are a fundamental method that energy is redistributed across large fluid bodies. To trigger these flows, there need to be two differentials, one along r and one along phi (in polar coordinates). As an example, on Earth, Hadley cells are a form of meridional circulation that is driven by thermal gradients along r and pressure gradients along phi. As a result, heat is exchanged between the equator and higher latitudes, driving towards equilibrium. For a deeper discussion on Hadley cells, see [this](https://groups.seas.harvard.edu/climate/eli/research/equable/hadley.html) site from Harvard's School of Engineering and Applied Sciences after the school. Included below is an image from that link, showing the general form of Hadley cells (specifically the possible height of the Hadley Cells during the Cretaceous)

![landscape](/tuesday/hadley_cell_cretaceous.png)

Another brief example is the Atlantic Meridional Overturning Circulation (AMOC), a key factor in global climate that transfers heat and nutrients between the equator and poles. In this case, the AMOC is driven by thermohaline gradients within the ocean (roughly, salinity along r and temperature along phi). For reference, you can check out these two links from NOAA: ["What is the AMOC?"](https://oceanservice.noaa.gov/facts/amoc.html#:~:text=AMOC%20stands%20for%20Atlantic%20Meridional,necessary%20to%20sustain%20ocean%20life.) & ["What is thermohaline circulation?"](https://oceanservice.noaa.gov/education/tutorial_currents/05conveyor1.html). Included below is a AMOC schematic from [Zimmerman et al., 2025](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024GL112415):

![landscape](/tuesday/amoc_schematic.jpg)

Of course, there is additional physics in both of these prior examples that I haven't discussed and will leave for experts. In the realm of stars, these same complications are present. There are a number of physical forces that could be used to drive and brake these circulating cells in our model and even more papers discussing which forces are needed and which are not. At a high level, there are temperature & pressure gradients along r and differential rotation rates along phi. This drives material and energy in large cells across the star as it evolves. A 2014 discussion of meridional circulation in the Sun by Dr. Mausami Dikpati at the High Altitude Observatory can be found [here](http://hmi.stanford.edu/hminuggets/?p=467). 


### Helpful Links

The general Lab 3 github repo can be found [here](https://github.com/pmocz/mesa-summer-school-2025-day2/tree/main/minilab3).  This repo contains the solutions, separated by step, the starting point for the lab, and pre-made ZAMS models. 

The Lab 3 Google Sheet can be found [here](https://docs.google.com/spreadsheets/d/1DSz7hmZfaAVm9XfVc-28lxwujzKFRZx4jOxRFkxqoPk/edit?usp=sharing).
  
The Google Colab script to make your plots can be found [here](https://colab.research.google.com/drive/1fB8YwH5e_XjZFDh-UGDrcjZefHOBE4Rq?usp=sharing).  
  
  &ensp;   
  
## Instructions


### Step 0: Getting Started

> [!NOTE]
> For clarity, specific tasks are marked by **bold** text

First, **claim a mass and initial rotation from the Google Sheet by entering your initials in Column A**. Then, **copy the starting point from the github repo to a local working directory**. 

This starting point should be a fairly familiar set of files. There are the standard MESA executables (`clean`, `mk`, `rn`, `re`), a file to tell MESA where to look at startup (`inlist`), a file with the particular run parameters we wish to use (`inlist_project`), a file that tells pgstar what to do (`inlist_pgstar`), a list of columns we want in our history file (`history_columns.list`), a list of columns we want in our profile file (`profile_columns.list`), and the mysterious `src` subdirectory. Each of these files has been -mostly- pre-prepared with the structure we will need to get going. Additionally, throughout each of these starting point files, variables that need to be changes are explicitly marked with "`!!!! !!!!`". This is also true if there is some particular section that needs your input. If you have trouble finding a value, feel free to ctrl+f your way around. 

Next, given the star value you selected, **copy the relevant ZAMS model into your working directory from the Github Repo**. The working directory should now be:


{{< filetree/container >}}
  {{< filetree/folder name="Starting Point" >}}
    {{< filetree/file name="clean" >}}
    {{< filetree/file name="history_columns.list" >}}
    {{< filetree/file name="inlist" >}}
    {{< filetree/file name="inlist_project" >}}
    {{< filetree/file name="inlist_pgstar" >}}
    {{< filetree/file name="mk" >}}
    {{< filetree/file name="profile_columns.list" >}}
    {{< filetree/file name="re" >}}
    {{< filetree/file name="rn" >}}
    {{< filetree/file name="ZAMS_Z02_M\<mass\>" >}}
    {{< filetree/folder name="src" state="open" >}}
      {{< filetree/file name="run.f90" >}}
      {{< filetree/file name="run_star_extras.f90" >}}
    {{< /filetree/folder >}}
  {{< /filetree/folder >}}
{{< /filetree/container >}} 


> [!NOTE]
> There are hints throughout this site that can be used at your discretion. To see the hint, simply click the labeled button. Feel free to use hints and solutions whenever you need. 

{{< details title="Hint! Click on it to reveal it." closed="true" >}}

This is an example hint!

{{< /details >}}

At this stage, we are now ready to dive into some inlists!


### Step 1: Inlist Project

Let's start by looking over `inlist_project`. 

This file should be generally quite familiar from Minilabs 1 & 2. Starting from the top of the file in `&star_jobs`, you will need to **turn on pgstar, load from the saved ZAMS model, and set the initial rotation rate**. It is also *recommended* that you turn on the `pause_before_terminate` flag to ensure that you can view the pgstar plots before the script exits. 

{{< details title="Hint: What parameters need to be changed?" closed="true" >}}

The parameters that should be updated/added are:
- `pgstar_flag`
- `load_saved_model`
- `load_model_filename`
- `new_omega_div_omega_crit`
- `set_initial_omega_div_omega_crit`
- `pause_before_terminate` <= Recommended

{{< /details >}}

Next, in `&controls`, **set the output directory for the logs, set the initial mass, turn on other angular momentum, and turn on other torque**. For the log directory, use a standard naming convention. It is recommended that this be something like `M<mass>_Z<metallicity>_Omega<initial rotation>` (ie. `M05_Z0p20_Omega0p60`), but generally this is up to you. You can explore all the available `use_other_<hook>` in the MESA docs [here](https://docs.mesastar.org/en/latest/reference/controls.html#use-other-hook).

{{< details title="Hint: What parameters need to be changed?" closed="true" >}}

The parameters that should be updated are:
- `log_directory`
- `initial_mass`
- `use_other_torque`
- `use_other_am_mixing`

{{< /details >}}

We have now set the general starting conditions for the MESA model (from ZAMS). Included in these changes is a directive for MESA to look beyond its regular routines for the torque and angular momentum calculations, which we will deal with later.

> [!WARNING]
> Don't forget to save your changes to the inlist!

### Step 2: Inlist Pgstar

> “If a MESA model runs to TAMS, and no one sees the pgstar plot, did it even happen?”  
> — <cite>Me</cite>, circa 2025

There is nothing better than a good plot to provide some insight into how the star is doing and to check for problems on our grand journey to TAMS. 

First, let's update our directions to pgstar. To begin, open `inlist_pgstar`. 

Again, this file should be familiar from Minilabs 1 & 2. The goal here is to modify the plots to show two new values: the log of the total angular momentum (henceforth `log_total_angular_momentum`) and a new variable we will call `log_dJ_over_J`. Here, `log_dJ_over_J` can be thought of as the contribution of our planned additional torque on the rotation profile of the star. Importantly, `log_total_angular_momentum` is a scalar that varies as the star ages, while `log_dJ_over_J` will hold values for each zone throughout the radius of the star. 

Now, as a test, which of these values should be a history plot and which should be a profile plot? 

{{< details title="Hint: Which value should go with which plot?" closed="true" >}}

`log_total_angular_momentum` should be plotted in `History_Panels2`.  
`log_dJ_over_J` should be plotted in `Profile_Panels1`.

{{< /details >}}

**Update `History_Panels2` and `Profile_Panels1` to plot these values**. 


{{< details title="Hint: What are the relevant X & Y axes?" closed="true" >}}

The final `History_Panels2` should plot `star_age` on the X-axis and `log_total_angular_momentum` on the Y-axis.  
The final `Profile_Panels1` should plot `radius` on the X-axis and `log_dJ_over_J` on the Y-axis.

{{< /details >}}

> [!WARNING]
> Don't forget to save your changes to the inlist!

### Step 3: History/Profile Columns List

Now, we need to add some more information to the history and profile outputs of our model. **Open `history_columns.list` and uncomment the following five values**:
* `surf_avg_omega`
* `surf_avg_omega_div_omega_crit`
* `surf_avg_v_rot`
* `center_omega`
* `log_total_angular_momentum`

Next, **open `profile_columns.list` and uncomment the following five values**:
* `radius`
* `omega`
* `r_polar`
* `omega_crit`
* `omega_div_omega_crit`  

> [!WARNING]
> Don't forget to save your changes to the inlists!

### Step 4: Run Star Extras


As a final step before we can run the model, we need to modify `src/run_star_extras.f90` to include an additional torque from meridional circulation and increase the viscosity to match the sample 2-D ESTER models. Much of this work has already been done for you, so, if you are not a Fortran wizard, do not fear! The next three 'sub-'steps will walk through a few additions we need to get things up and running.

> [!TIP]
> Do not forget to use hints liberally if you are stuck!

#### Step 4.1: Subroutines, A New Hope

Start by looking over the `run_star_extras` file. Take note of the general form of the code. You will notice that this file is really a collection of labelled subroutines and functions (particularly labelled 'integer functions'). On a high level, these are just the basic execution steps that MESA uses to solve the model. You can see when they get called in the flowchart below. This same flowchart can be found in the MESA docs [here](https://docs.mesastar.org/en/latest/using_mesa/extending_mesa.html#control-flow). 

![landscape](/tuesday/MESA_flowchart.png)

{{< details title="Super duper fun fact 🚨" closed="true" >}}

The difference between a subroutine and a function in Fortran is that a function **MUST** return data. Subroutines, on the other hand, do not need to return anything. [This](https://www.meteor.iastate.edu/classes/mt227/lectures/Subprograms.pdf) short lecture by Dave Flory at Iowa State University covers some of the similarities, differences, and syntax of these structures.

These same structures exist across languages, but are not always explicitly distinguished by defining keywords. For example, in Python and Ruby, there is no real distinction between a function and a subroutine. Both structures are defined with the `def` keyword. Technically, a function would then include a return statement, while a subroutine would not (again, there is no real distinction here). Meanwhile, subroutines are referenced differently in Java or C by using the `void` keyword. This just signifies that there is not a return value.  

{{< /details >}}

In [`Step 1`](#step-1-inlist-project), we turned on two flags to use `other_torque` and `other_am_mixing`. Our goal here is to provide MESA with a custom subroutine that steps into the execution process (seen in the flowchart) and changes key behavior about how the torque and angular momentum mixing are calculated. Since we have not reached an AI Singularity (yet), MESA cannot intuit what these custom subroutines are or where they will be. Hence, we need to provide a pointer that says "*This* new procedure is defined by *this* other piece of code". This is done in the subroutine `extras_controls`. **Add in a pointer to our new custom subroutines, `meridional_circulation` and `additional_nu`**. Follow the form seen elsewhere in `extras_controls`, or reference the MESA docs [here](https://docs.mesastar.org/en/latest/using_mesa/extending_mesa.html#instruct-mesa-to-use-your-routine). Do not worry about what these custom subroutines *are* yet, we will cover that in the next step. 

{{< details title="Hint: Pointer format" closed="true" >}}

The general form of the pointer is:
```fortran
s% <star procedure> => <local subroutine>
```
{{< /details >}}

{{< details title="Hint: What points to what?" closed="true" >}}

`s% other_torque` should be pointing to `meridional_circulaton`.
`s% other_am_mixing` should be pointing to `additional_nu`.
{{< /details >}}


#### Step 4.2: Fortran Strikes Back

Now that MESA knows where to look, what exactly is going on in these new subroutines? Scroll down to our custom other torque subroutine, `meridional_circulation`.  

`meridional_circulation` is declared with the `subroutine` keyword, meaning we do not expact any output. Instead, this routine will grab the object containing all the star's information, identified with the pointer `s%`, and modify values directly. You will also see that this subroutine takes in two values, `id` and `ierr`. `id` is the unique identifier that is tied to each instance of `star_info`, the object which holds everything about the star. `ierr` is an integer passed across MESA to keep tabs on the status of each operation. If this value becomes non-zero, it means means that an error has occured. 

Next, we have variable declarations. In Fortran, ALL variables must be declared before they are used. The types of these variables should be explicitly provided as well. In fact, because `run_star_extras.f90` contains the `implicit none` statement at the beginning of the file, this explicit declaration is not optional. **Declare three additional integers: `k`, `k0`, and `nz`**.


{{< details title="Hint: What is the general form of a variable declaration?" closed="true" >}}

```fortran
<type> :: <variable name>
```

Multiple variables of the same type can be declared in the same line as follows:
```fortran
<type> :: <variable name0>, <variable name1>, <variable nameN>
```
{{< /details >}}


{{< details title="Hint: How do we declare an integer?" closed="true" >}}

```fortran
integer :: <variable name>
```
{{< /details >}}

{{< details title="Solution:" closed="true" >}}

```fortran
integer :: k, k0, nz
```
{{< /details >}}



> [!NOTE]
> For a deep dive into the various types available in Fortran and more, see [these notes from Ching-Kuang Shene at Michigan Technological University](https://pages.mtu.edu/~shene/COURSES/cs201/NOTES/F90-Basics.pdf) after the school.

Following this section, we reset the ierr integer to 0 (meaning success), grab the relevant pointer to our star object, then check if anything went wrong. This portion of the routine is functionally boilerplate. You  will find the same three lines across all the routines that access an instance of the star.  

The next two sections set up some important constants for subsequent calculation steps. The first, `nz`, is the integer number of zones in the model (ie. how many little star sections we have). This value can be accessed directly from the star pointer. The second value, `k0`, is the index of the zone where the radiative envelope starts. This value is not simply stored in the star pointer. Instead, we have to use a DO loop which can be thought of in the same way as a FOR loop in Python, C, or Java. This loop starts at the center and works it way to the surface, setting `k0` to the first index where the `mixing_type == minimum_mixing`, meaning we have entered the envelope. 

> [!IMPORTANT]
> When accessing a model array indexed by a `k` zone, note that `k = nz` represents the center of the star and `k = 1` represents the surface. So, when conducting a standard incrementing loop from `k = 1` to `k = nz`, you are sweeping from the surface into the core, **NOT** from the core to the surface. 

> [!NOTE]
> The criteria for what defines minimum mixing is driven by our use of `set_min_D_mix` and `min_D_mix` in `inlist_project`. This will not be explored further in this lab, but if you are interested in the backend operation, take a look at `set_mixing_info` in `$MESA_DIR/star/private/mix_info.f90`. Beware, the code can look a little intimidating. The relevant piece here is contained by lines 239 -> 247.  

Next, we allocate and calculate three arrays: `Ur`, `mer_comp`, and `dmer_comp_dr`. `Ur` will be a simple velocity field that should improve the comparison to the 2D model. The equation for this field in is: 

$$Ur = C \frac{r}{R}\;\;\; cm.s^{-1}$$  

`mer_comp` is then the meridional torque produced by that velocity field given by:

$$mer _\ comp = \rho \Omega r^4 * Ur = \frac{\rho \Omega r^5 C}{R}\;\;\;cm^2.g.s^{-2}$$  

`dmer_comp_dr` is then differential meridional torque per unit radius, 

$$\frac{\partial mer _\ comp}{\partial r} = \frac{5C\rho \Omega r^4}{R}\;\;\;cm.g.s^{-2}$$

,which is solved numerically in the subroutine with the equivalent statement:

$$\frac{\partial mer _\ comp}{\partial r}(k) = \frac{mer _\ comp(k) - mer _\ comp(k+1)}{r(k) - r(k+1)} \;\;\;cm.g.s^{-2}$$  

**Given these equations, add the equation for `Ur` and `mer_comp`, assuming `C = 1e-3`**. You can use the same variable description table from [Lab2](/tutorials/tuesday/lab-2/).

> [!NOTE]
> When taking the power of a value in MESA, it is recommended that you use a power function (ie. `pow2(X)`, `pow3(X)`, `pow4(X)`) as opposed to the power operator (`**`)

{{< details title="Hint: How do we get R?" closed="true" >}}

Remember that these variable arrays are indexed by zone. So, the value of `s% r(k)` where k is the surface index, will be the total radius, R. Given that `k = 1` at the surface, `R = s% r(1)`
{{< /details >}}

{{< details title="Solution:" closed="true" >}}

```fortran
Ur = (s% r) / (s% r(1)) * 0.001 ! cm/s
mer_comp = s% rho * pow4(s% r) * (s% omega) * Ur
```
{{< /details >}}

We also want to store a copy of `dmer_comp_dr` with the star object in memory. This can be done by passing this value over to an `xtraN_array`. Six of these arrays are declared within `star_info` to hold double precision values and are guaranteed to have a length equal to `s% nz`. With this array, we then call a weighted smoothing subroutine to decrease the amount of noise and increase how pretty our end plots are. We will not be exploring how the weighted smoothing subroutine works in this lab, but feel free to explore it at a later time after the school, if interested. 

{{< details title="Fun fact" closed="true" >}}

There are other temporary alternative arrays that hold integers (like `ixtraN_array`) or booleans

{{< /details >}}
 
 So far, we have been doing a lot of prep work collecting variables. The next sections of the subroutine are all directed at finally applying these new torques to the model. We start at the surface and work our way down to the radiative envelope boundary `k0` that we calculated previously. At each zone k we encounter, using our stored copy of `dmer_comp_dr(k)`, we get the rate at which the specific angular momentum is changed as a result of our velocity field at t=0 and add it to whatever the value of extra_jdot was at t=-1.
 
 Once we reach the convective core, we calculate the total torque that we applied to the envelope (saving it to a temporary value, `s% xtra(1)`). Then, for each zone in the core, we apply an opposing torque to ensure angular momentum is conserved. 
 
Pay attention to the places that we saved data in the star pointer, `s%`. Specifically, `s% xtra(1)` is holding onto the total torque applied to the envelope, a scalar. Meanwhile, `s% xtra1_array` and `s% xtra2_array` are storing the values of `extra_jdot` and `dmer_comp_dr` as arrays. You will need some of these values later. 

You may remember that we also pointed to another subroutine, `additional_nu`. We will not be exploring how that subroutine works, but feel free to explore it at your own pace after the school. In practice, it is just a few DO loops to increase the viscosity and help bring the 1D model into agreement. 


#### Step 4.3: Return of the Profile Columns (from Lab 2)

So, we have made the necessary calculations and saved off some variables into the star pointer. Now, we need to make those values presentable in the history and profile columns. **To start, add one extra history column and two extra profile columns **.

{{< details title="Hint: What values control how many extra columns there are in the history and profile outputs?" closed="true" >}}

To increase the number of extra history columns, modify the variable `how_many_extra_history_columns` in the function `how_many_extra_history_columns`.

To increase the number of extra profile columns, modify the variable `how_many_extra_profile_columns` in the function `how_many_extra_profile_columns`.

{{< /details >}}

Now that MESA expects some additional values, lets add the history data first. **Add our `total_torque_envelope` value from [Step 4.2](#step-42-fortran-strikes-back) to a column named `total_torque_envelope`**.

{{< details title="Hint: What is the general form of a new history column?" closed="true" >}}

```fortran
names(<column number>) = <your column name>
vals(<column number>) = <your value>
```

{{< /details >}}

{{< details title="Hint: What is the variable containing the information we need?" closed="true" >}}

We saved the total torque on the envelope into the star pointer at `s% xtra(1)`

{{< /details >}}

{{< details title="Soluton" closed="true" >}}

```fortran
names(1) = "total_torque_envelope"
vals(1) = s% xtra(1)
```

{{< /details >}}

Now, we will need to do some calculations to get the data for the profile columns. Remember, since these are profiles, they are arrays with entries at each zone k. We will be adding two columns called `extra_jdot` and `log_dJ_over_J`. `extra_jdot` is the same value we encountered in `meridional_circulation`.  `log_dJ_over_J` is an account of how much of the specific angular momentum was due to our additional velocity field. value can be calculated as, 

$$\log(\left|\frac{\Delta J_{extra} * dt}{J}  \right|)$$

where $\Delta J_{extra}$ is `extra_jdot`.

To put these values into columns, we need to make a DO loop across all the zones in the model, saving data in each one. An example of how to do this with a variable named `beta` is already given in the subroutine. **Add our two new profile columns, `extra_jdot` and `log_dJ_over_J`**. 

{{< details title="Hint: What is the general form of a new profile column?" closed="true" >}}
```fortran
names(<column number>) = <your column name>
do k = 1, nz
    vals(k, <column number>) = <your value at k>
end do
```
{{< /details >}}  

{{< details title="Hint: Where is `extra_jdot` from?" closed="true" >}}
Recall that we saved `extra_jdot` in the array `s% xtra1_array(k)`.
{{< /details >}}

{{< details title="Hint: How do I write a log or absolute value in Fortran?" closed="true" >}}
Use the functions below:
```fortran
log10()
abs()
```
{{< /details >}}

{{< details title="Hint: What other values do I need for `log_dJ_over_J`?" closed="true" >}}
Use the functions below:
```fortran
s% xtra1_array(k)
s% dt
s% j_rot(k)
```
{{< /details >}}

{{< details title="Solution" closed="true" >}}
```fortran
names(1) = "extra_jdot"
names(2) = "log_dJ_over_J"
do k = 1, nz
    vals(k, 1) = s% xtra1_array(k)
    vals(k, 2) = log10(abs(s% xtra1_array(k) * s% dt / s% j_rot(k)))
end do   
```
{{< /details >}}

Voilà! You have finished implementing all the MESA changes we need for this lab and are officially recognized as a Fortran genius. 

> [!WARNING]
> Don't forget to save your changes to run_star_extras!

### Step 5: Running the model

Let's see MESA in action. **Run the model**.

> [!IMPORTANT]
> Do not forget to `./clean`, then `./mk`, then `./rn`

You should see the rotation begin at your set initial value. Further along, the plot for `log_dJ_over_J` will display the additional torque being forced along the radius of the star. How does this value relate to the convective zone boundary? How noisy is the plot? Do you see any information about how energy is being transported?

Once the model completes, take note of the following values as printed in the pgstar plot:
* `center_omega`
* `surf_avg_omega`
* `star_age`

**Enter these values into the Google sheet for your star**. If your model reached critical rotation, enter its final age in Myr as $t_{crit}$ else leave it blank.

### Step 6: Running -another- model

You're a pro at this by now, so let's back track and try running another case without the `extra_jdot`.

**Change the log_directory and turn off `use_other_torque` in `inlist_project`**. 

> [!CAUTION]
> Check that the log directory name is new and unique, otherwise this new run will override your previous information. 

> [!IMPORTANT]
> Do not forget to save! 

**Try runnning this new model**. Is there any strange behavior in the pgstar plots? Why would that be?

> [!IMPORTANT]
> Do not forget to `./clean`, then `./mk`, then `./rn`

You should expect some artifacts in pgstar, since we have completely obliterated the values we saved out in `meridional_circulation`. Despite this, MESA should chug along, unhappily, to TAMS. We *could* have avoided this by explicitly setting `s% extra_jdot(k)` to 0 (or some other miniscule value) for every `k` in `run_star_extras.f90`. 

Once the model completes, look at the final `center_omega`, `surf_avg_omega`, `star_age` values from the pgstar plot. How do these compare to the case *with* the additional velocity field?

### Step 7: Recreate 2024 paper results

Now that we have all our data assembled, **open the Google Colab script**. For those unfamiliar with Google Colab :  
> Google Colab (short for Colaboratory) is a free, cloud-based platform provided by Google that lets you write and execute Python code in a web browser — especially useful for data science, machine learning, and education.  
> — <cite>ChatGPT.v4o</cite>

**Upload the two log directories for your runs into the provided Google Colab notebook**. Follow the steps listed there to create plots similar to those in [Mombarg et al., 2024](https://www.aanda.org/articles/aa/pdf/2024/03/aa48466-23.pdf)[^2]. 

How do the plots compare? Share the plots with others at your table. Do you notice any trends?


## Bonus

Feel free to pursue this bonus exercise if you have additional time.

So far we have been working through the models with a key assumption that `C = 1e-3` in $Ur$. Try exploring other ranges for this value, how does this modify the output in pgstar? 
  

## Primary References

[^1]: [Mombarg, Joey SG, Michel Rieutord, and F. Espinosa Lara. "The first two-dimensional stellar structure and evolution models of rotating stars-Calibration to β Cephei pulsator HD 192575." *Astronomy & Astrophysics 677* (2023): L5.](https://www.aanda.org/articles/aa/pdf/2023/09/aa47454-23.pdf)  


[^2]: [Mombarg, Joey SG, Michel Rieutord, and F. Espinosa Lara. "A two-dimensional perspective of the rotational evolution of rapidly rotating intermediate-mass stars-Implications for the formation of single Be stars." *Astronomy & Astrophysics 683* (2024): A94.](https://www.aanda.org/articles/aa/pdf/2024/03/aa48466-23.pdf)
