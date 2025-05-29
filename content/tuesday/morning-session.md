---
weight: 1
math: true
---

<!--
TEMPLATES FOR COPY-PASTE:

ANSWER:
<details class="hx-border hx-border-green-200 dark:hx-border-green-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-green-100 dark:hx-bg-neutral-800 hx-text-green-900 dark:hx-text-green-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Answer</em>
</summary>
<div class="hx-p-2">

[CONTENT HERE]

</div>
</details>

HINT:
<details class="hx-border hx-border-blue-200 dark:hx-border-blue-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-blue-100 dark:hx-bg-neutral-800 hx-text-blue-900 dark:hx-text-blue-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Hint: Troubleshooting</em>
</summary>
<div class="hx-p-2">

[CONTENT HERE]

</div>
</details>
-->

# Beyond Inlists: Extending MESA with `run_star_extras.f90`

Inlists, models and photos are the core of MESA, and you can do a lot of great science without even knowing how to write a line of Fortran code. But fairly soon in your MESA journey, you will run into limits of what you can do with inlists alone. This is where `run_star_extras.f90` comes in. It allows you to extend MESA's capabilities by writing your own Fortran code that can interact with the star model. A few examples of things you can do with `run_star_extras.f90` include:

- creating a custom stopping condition
- changing control parametrs during a run without restarting
- adding custom data to profile or history files
- implementing custom physics, like energy sources or mass loss prescriptions

The goal of these exercises is to get you up and running with `run_star_extras.f90` and provide a resource you can return to when you next need to extend MESA.

## Acknowledgements

This material is strongly influenced by similar material from past MESA schools by Josiah Schwab, a former MESA developer. Specifically, this material is drawn from his introductory materials for the 2021 MESA summer school, which can be found [here](https://jschwab.github.io/mesa-2021/).

## Part 0: Fortran Basics

Fortran is a powerful language for scientific computing offering modern features with strong performance. However, one rarely writes in Fortran for their everyday tasks. With MESA, you'll rarely need to write much Fortran from scratch, but you will need to edit functions (which cannot change their inputs and must have a return value) subroutines (which *can* change their inputs and have no return value) This section provides some basic Fortran syntax to get you started. If you are already familiar with Fortran, feel free to skip this section. If you are new, skim it and come back to it as needed.

### Variables

#### Declaring Variables

Fortran is a statically-typed language, meaning you must declare the type of each variable before using it. The type of a variable determines what kind of data it can hold and how much memory it uses. Variable declarations *must* come at the beginning of function and subroutine implementations. Here are some common types:

```fortran
! declare a boolean variable
logical :: flag

! declare an integer variable
integer :: i

! declare a double precision variable
real(dp) :: foo

! declare a 1d array with 10 elements
real(dp), dimension(10) :: bar
```

Note: to make a variable double precision, you must declare it with `real(dp)` rather than just `real`.

#### Assigning Variables

When dealing with numerical literals, Fortran uses the `d` suffix to indicate double precision. For example, `3.14` is single precision, while `3.14d0` is double precision. Here are some examples of assigning values to variables:

```fortran
! booleans have two special values
flag = .true.
flag = .false.

! arrays are 1-indexed (using parentheses)
bar(1) = 3.14d0
bar(2:9) = 0
bar(10) = 2.72d0
```

### Logic and Control Flow

#### Comparison Operators

There are two (equivalent) forms of comparison operators in Fortran

| text form | symbol form | description |
|------------|-------------|-------------|
| `.gt.` | `>` | greater than |
| `.lt.` | `<` | less than |
| `.ge.` | `>=` | greater than or equal to |
| `.le.` | `<=` | less than or equal to |
| `.eq.` | `==` | equal to |
| `.ne.` | `!=` | not equal to |

```fortran
! these are the same
(i .ne. 0)
(i /= 0)
```

#### Logical Operators

There are three logical operators: .and., .or., and .not..

```fortran
! true when 0 < i < 10
((i > 0) .and. (i < 10))

! true when i /= 0,1
(.not. ((i .eq. 0) .or. (i .eq. 1)))
```

#### If, Then, and Else

```fortran
! here is an example of how to do some logic
if (x .gt. 0) then
   heavyside = 1.0
else if (x .lt. 0) then
   heavyside = 0.0
else
   heavyside = 0.5
end if
```

#### Loops

```fortran
! here is an example of a do loop
array(1) = 1
array(2) = 1
do i = 3, 10
   array(i) = array(i-1) + array(i-2)
enddo
```

## Part 1: Setting Up Your Project

When starting a new MESA project, you will often start with the default work directory:

```bash
cp -r $MESA_DIR/star/work my_new_project
cd my_new_project
```
This will create a new directory called `my_new_project` with the default MESA work directory structure. You can then edit the inlist files to set up your star model.

In other cases, you might start with an existing test case that is close to the science you are interested in. For instance, I study novae, so I might start with the `wd_nova_burst` test case:

```bash
cp -r $MESA_DIR/star/test_suite/wd_nova_burst my_new_project
cd my_new_project
```

For this exercise, we are providing a work directory that is already set up for you. It's pretty simple; it evolves a 1.0 solar mass from near the zero-age main sequence to core hydrogen exhaustion, and then pauses before exiting.

**Task 1.1:** Download the work directory, move it somewhere sensible, unzip it, and change into the directory.

[Download the work directory](#)


<details class="hx-border hx-border-green-200 dark:hx-border-green-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-green-100 dark:hx-bg-neutral-800 hx-text-green-900 dark:hx-text-green-200 hx-p-2 hx-m-0 hx-cursor-pointer">
    <em>Click here for hints or answers</em>
</summary>

<div class="hx-p-2">

After downloading the work directory, you can do everything else from the command line:

Move the directory to your desktop (or wherever you want to work on it):

```bash
mv ~/Downloads/mesa-day2-dev.zip ~/Desktop/
```
Unzip the directory:

```bash
unzip ~/Desktop/mesa-day2-dev.zip
```
Change into the directory:

```bash
cd ~/Desktop/mesa-day2-dev
```

If you're computer is too smart, it may have automatically unzipped the directory for you. In that case, you can just move the directory and change into it:

```bash
mv ~/Downloads/mesa-day2-dev ~/Desktop/
cd ~/Desktop/mesa-day2-dev
```
</div>
</details>

Now let's make sure everything is working correctly.

**Task 1.2:** Compile and run the project.

If things are set up properly, you should see a pgstar window open up, and the project should run for about 94 timesteps and pause before closing. If not, consult the hints and answer below, and reach out to tablemates or a TA for help if you can't get it working.

<details class="hx-border hx-border-green-200 dark:hx-border-green-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-green-100 dark:hx-bg-neutral-800 hx-text-green-900 dark:hx-text-green-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Answer</em>
</summary>
<div class="hx-p-2">

To compile and run the project, you can use the following commands:

```bash
./mk && ./rn
```

Note that putting `&&` between two commands means that the second command will only run if the first command succeeds. If you want to run the commands separately, you can use `./mk` to compile and `./rn` to run the project.

</div>
</details>

<details class="hx-border hx-border-blue-200 dark:hx-border-blue-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-blue-100 dark:hx-bg-neutral-800 hx-text-blue-900 dark:hx-text-blue-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Hint: Troubleshooting</em>
</summary>
<div class="hx-p-2">

Are you in the correct directory? Execute `ls` to make sure you see the normal contents of a MESA work directory, including `inlist`, `mk`, and `rn`.

Is your MESA environment set up correctly? Ensure that executing `mesasdk_version` prints out the version of the MESA SDK you have installed, and similarly ensure that `echo $MESA_DIR` prints out the path to your MESA installation.

</div>
</details>

## Part 2: Setting Up Your `run_star_extras.f90`
The file `run_star_extras.f90` lives in the `src` directory of your work directory. It is a Fortran file you can edit to add your own custom code that will run during the evolution of your stellar model. The file is already set up, but isn't very useful yet.

### Creating a boilerplate `run_star_extras.f90`

**Task 2.1:** Open the file `run_star_extras.f90` in your favorite text editor. You should see a file that looks like this:

```fortran
! ***********************************************************************
!
!   Copyright (C) 2010-2019  Bill Paxton & The MESA Team
!
!   this file is part of mesa.
!
!   REMAINING COMMENTS OMITTED FOR BREVITY
!
! ***********************************************************************
 
      module run_star_extras

      use star_lib
      use star_def
      use const_def
      use math_lib
      
      implicit none
      
      ! these routines are called by the standard run_star check_model
      contains
      
      include 'standard_run_star_extras.inc'

      end module run_star_extras
      
```

This file defines a module called `run_star_extras`, which itself loads four other modules (`star_lib`, `star_def`, `const_def`, and `math_lib`), which refer to different parts of MESA's other modules that might be useful to you. The `implicit none` statement is a good practice in Fortran that prevents you from accidentally using variables that haven't been declared.

The actual "body" of the module is then punted to the file `standard_run_star_extras.inc`, which is included at the end of the module. This file has the main boilerplate of most of the code you might want to edit, and it is by default set up to do nothing. To edit this text, though, we need to copy it into our `run_star_extras.f90`.

**Task 2.2:** Copy the entire contents of `$MESA_DIR/include/standard_run_star_extras.inc` and paste it into your `run_star_extras.f90` file, replacing the `include 'standard_run_star_extras.inc'` line. Maintain the lines above and below the `include` line, as they are necessary for the module to work correctly.

<details class="hx-border hx-border-blue-200 dark:hx-border-blue-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-blue-100 dark:hx-bg-neutral-800 hx-text-blue-900 dark:hx-text-blue-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Hint</em>
</summary>
<div class="hx-p-2">

There are fancy command line ways to do this, but for me, I prefer to actually do the copy and paste in a text editor. Open up the file with your favorite text editor. Perhaps with VS Code:

```bash
code $MESA_DIR/include/standard_run_star_extras.inc
```

Then select **all** the text in the file, copy it, and paste it into your `run_star_extras.f90` file. You can open that file in the same way:

```bash
code src/run_star_extras.f90
```

The newly-pasted content should start with the subroutine `extras_controls` and end with the subroutine `extras_after_evolve`, though the line `end module run_star_extras` should still be at the end of the file.
</div>
</details>

<details class="hx-border hx-border-green-200 dark:hx-border-green-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-green-100 dark:hx-bg-neutral-800 hx-text-green-900 dark:hx-text-green-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Answer</em>
</summary>
<div class="hx-p-2">

Below is the complete contents of what your edited `run_star_extras.f90` file should look like. If you ran into issues getting things copied properly, just copy the code below and paste it into your `run_star_extras.f90` file, replacing *everything* in that file.

```fortran
! ***********************************************************************
!
!   Copyright (C) 2010-2019  Bill Paxton & The MESA Team
!
!   this file is part of mesa.
!
!   mesa is free software; you can redistribute it and/or modify
!   it under the terms of the gnu general library public license as published
!   by the free software foundation; either version 2 of the license, or
!   (at your option) any later version.
!
!   mesa is distributed in the hope that it will be useful, 
!   but without any warranty; without even the implied warranty of
!   merchantability or fitness for a particular purpose.  see the
!   gnu library general public license for more details.
!
!   you should have received a copy of the gnu library general public license
!   along with this software; if not, write to the free software
!   foundation, inc., 59 temple place, suite 330, boston, ma 02111-1307 usa
!
! ***********************************************************************
 
      module run_star_extras

      use star_lib
      use star_def
      use const_def
      use math_lib
      
      implicit none
      
      ! these routines are called by the standard run_star check_model
      contains
      
      subroutine extras_controls(id, ierr)
         integer, intent(in) :: id
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         
         ! this is the place to set any procedure pointers you want to change
         ! e.g., other_wind, other_mixing, other_energy  (see star_data.inc)


         ! the extras functions in this file will not be called
         ! unless you set their function pointers as done below.
         ! otherwise we use a null_ version which does nothing (except warn).

         s% extras_startup => extras_startup
         s% extras_start_step => extras_start_step
         s% extras_check_model => extras_check_model
         s% extras_finish_step => extras_finish_step
         s% extras_after_evolve => extras_after_evolve
         s% how_many_extra_history_columns => how_many_extra_history_columns
         s% data_for_extra_history_columns => data_for_extra_history_columns
         s% how_many_extra_profile_columns => how_many_extra_profile_columns
         s% data_for_extra_profile_columns => data_for_extra_profile_columns  

         s% how_many_extra_history_header_items => how_many_extra_history_header_items
         s% data_for_extra_history_header_items => data_for_extra_history_header_items
         s% how_many_extra_profile_header_items => how_many_extra_profile_header_items
         s% data_for_extra_profile_header_items => data_for_extra_profile_header_items

      end subroutine extras_controls
      
      
      subroutine extras_startup(id, restart, ierr)
         integer, intent(in) :: id
         logical, intent(in) :: restart
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
      end subroutine extras_startup
      

      integer function extras_start_step(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         extras_start_step = 0
      end function extras_start_step


      ! returns either keep_going, retry, or terminate.
      integer function extras_check_model(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         extras_check_model = keep_going         
         if (.false. .and. s% star_mass_h1 < 0.35d0) then
            ! stop when star hydrogen mass drops to specified level
            extras_check_model = terminate
            write(*, *) 'have reached desired hydrogen mass'
            return
         end if


         ! if you want to check multiple conditions, it can be useful
         ! to set a different termination code depending on which
         ! condition was triggered.  MESA provides 9 customizeable
         ! termination codes, named t_xtra1 .. t_xtra9.  You can
         ! customize the messages that will be printed upon exit by
         ! setting the corresponding termination_code_str value.
         ! termination_code_str(t_xtra1) = 'my termination condition'

         ! by default, indicate where (in the code) MESA terminated
         if (extras_check_model == terminate) s% termination_code = t_extras_check_model
      end function extras_check_model


      integer function how_many_extra_history_columns(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         how_many_extra_history_columns = 0
      end function how_many_extra_history_columns
      
      
      subroutine data_for_extra_history_columns(id, n, names, vals, ierr)
         integer, intent(in) :: id, n
         character (len=maxlen_history_column_name) :: names(n)
         real(dp) :: vals(n)
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         
         ! note: do NOT add the extras names to history_columns.list
         ! the history_columns.list is only for the built-in history column options.
         ! it must not include the new column names you are adding here.
         

      end subroutine data_for_extra_history_columns

      
      integer function how_many_extra_profile_columns(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         how_many_extra_profile_columns = 0
      end function how_many_extra_profile_columns
      
      
      subroutine data_for_extra_profile_columns(id, n, nz, names, vals, ierr)
         integer, intent(in) :: id, n, nz
         character (len=maxlen_profile_column_name) :: names(n)
         real(dp) :: vals(nz,n)
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         integer :: k
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         
         ! note: do NOT add the extra names to profile_columns.list
         ! the profile_columns.list is only for the built-in profile column options.
         ! it must not include the new column names you are adding here.

         ! here is an example for adding a profile column
         !if (n /= 1) stop 'data_for_extra_profile_columns'
         !names(1) = 'beta'
         !do k = 1, nz
         !   vals(k,1) = s% Pgas(k)/s% P(k)
         !end do
         
      end subroutine data_for_extra_profile_columns


      integer function how_many_extra_history_header_items(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         how_many_extra_history_header_items = 0
      end function how_many_extra_history_header_items


      subroutine data_for_extra_history_header_items(id, n, names, vals, ierr)
         integer, intent(in) :: id, n
         character (len=maxlen_history_column_name) :: names(n)
         real(dp) :: vals(n)
         type(star_info), pointer :: s
         integer, intent(out) :: ierr
         ierr = 0
         call star_ptr(id,s,ierr)
         if(ierr/=0) return

         ! here is an example for adding an extra history header item
         ! also set how_many_extra_history_header_items
         ! names(1) = 'mixing_length_alpha'
         ! vals(1) = s% mixing_length_alpha

      end subroutine data_for_extra_history_header_items


      integer function how_many_extra_profile_header_items(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         how_many_extra_profile_header_items = 0
      end function how_many_extra_profile_header_items


      subroutine data_for_extra_profile_header_items(id, n, names, vals, ierr)
         integer, intent(in) :: id, n
         character (len=maxlen_profile_column_name) :: names(n)
         real(dp) :: vals(n)
         type(star_info), pointer :: s
         integer, intent(out) :: ierr
         ierr = 0
         call star_ptr(id,s,ierr)
         if(ierr/=0) return

         ! here is an example for adding an extra profile header item
         ! also set how_many_extra_profile_header_items
         ! names(1) = 'mixing_length_alpha'
         ! vals(1) = s% mixing_length_alpha

      end subroutine data_for_extra_profile_header_items


      ! returns either keep_going or terminate.
      ! note: cannot request retry; extras_check_model can do that.
      integer function extras_finish_step(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         extras_finish_step = keep_going

         ! to save a profile, 
            ! s% need_to_save_profiles_now = .true.
         ! to update the star log,
            ! s% need_to_update_history_now = .true.

         ! see extras_check_model for information about custom termination codes
         ! by default, indicate where (in the code) MESA terminated
         if (extras_finish_step == terminate) s% termination_code = t_extras_finish_step
      end function extras_finish_step
      
      
      subroutine extras_after_evolve(id, ierr)
         integer, intent(in) :: id
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
      end subroutine extras_after_evolve

      end module run_star_extras   
```
</div>
</details>

**NEVER** edit the `standard_run_star_extras.inc` file directly, as it is part of the MESA source code and is read by any MESA project that uses the stock `run_star_extras.f90`. Instead, you should always copy the contents of this file into your own `run_star_extras.f90` and edit that file.

Whenever you change the `run_star_extras.f90` file, you will need to recompile your project for the changes to take effect. You do *not* need to recompile your project if you only change the inlists or other files that are not part of the `src` directory. Usually a simple `./mk` will suffice, but if things are wonky, you can try `./clean && ./mk` to clean the project and recompile from scratch. 

**Task 2.3:** Compile and run the project again.

<details class="hx-border hx-border-green-200 dark:hx-border-green-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-green-100 dark:hx-bg-neutral-800 hx-text-green-900 dark:hx-text-green-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Answer</em>
</summary>
<div class="hx-p-2">

In your main work directory, run

```bash
./mk && ./rn
```

</div>
</details>

Everything should run just as before. If you see errors, read them carefully, and if you can't figure out what went wrong, ask a TA or tablemate for help.

### Baby's first Fortran and Fortran Errors

Now that we have a boilerplate `run_star_extras.f90` file, we can start modifying MESA's behavior with our own code. We should briefly review what all these functions and subroutines do, and then we can write our first Fortran code.

Perhaps you've seen the flowchart below (courtesy of Josiah Schwab) before. It shows the flow of control in MESA's evolution code, and how `run_star_extras.f90` fits into it. You might want to download this flowchart and use it to prototype where your own code will go.

<div class="hx-bg-white p-4 rounded">
  <embed src="../flowchart.pdf" type="application/pdf" width="100%" height="600px" />
</div>

Each of the `extras_*` functions and subroutines in `run_star_extras.f90` is called at a different point in the evolution process. Need to set a variable at the beginning of a run? Use `extras_startup`. Need to check a condition at the end of each step? Use `extras_check_model`. We won't see examples of all of these today, but I encourage you to look at the `run_star_extras.f90` files in many of the MESA test cases to learn more about how they can be used.

`extras_check_model` is one of the more commonly used functions, as it is called at the end of each timestep. Let's use it to do the simplest thing we can: print a message to the terminal. This is a good first step to make sure we can compile and run our code without errors.

**Task 2.4:** 

- Add the following code to the `extras_check_model` function in your `run_star_extras.f90` file:
```fortran
write(*,*) 'Hello, MESA!'
```
- Compile and run the project again, confirming that you get a bunch of annoying messages printed to the terminal.


<details class="hx-border hx-border-blue-200 dark:hx-border-blue-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-blue-100 dark:hx-bg-neutral-800 hx-text-blue-900 dark:hx-text-blue-200 hx-p-2 hx-m-0 hx-cursor-pointer">
<em>Hint: Wait, this thing isn't empty!</em>
</summary>
<div class="hx-p-4">

Yes, the "boilerplate" function is certainly not empty. It should look like this:

```fortran
integer function extras_check_model(id)
    integer, intent(in) :: id
    integer :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    extras_check_model = keep_going
    if (.false. .and. s% star_mass_h1 < 0.35d0) then
        ! stop when star hydrogen mass drops to specified level
        extras_check_model = terminate
        write(*, *) 'have reached desired hydrogen mass'
        return
    end if


    ! if you want to check multiple conditions, it can be useful
    ! to set a different termination code depending on which
    ! condition was triggered.  MESA provides 9 customizeable
    ! termination codes, named t_xtra1 .. t_xtra9.  You can
    ! customize the messages that will be printed upon exit by
    ! setting the corresponding termination_code_str value.
    ! termination_code_str(t_xtra1) = 'my termination condition'

    ! by default, indicate where (in the code) MESA terminated
    if (extras_check_model == terminate) s% termination_code = t_extras_check_model
end function extras_check_model
```

That's quite a mouthful! Everything down to and including `extras_check_model = keep_going` is boilerplate code that you should not change. It defines the type of the single input (an integer associated with the stellar model in question, called `id`), an error-tracking integer `ierr`, and the star info structure `s`, which is an enormous structure that contains all data about the stellar model.

Below that, and up until the `if (extras_check_model == terminate)` line is an example stopping condition and explanation comments that you may delete if you wish. I'll explain what's going on there, though, as custom stopping conditions are a common use of `extras_check_model`.

The `if (.false. .and. s% star_mass_h1 < 0.35d0)` line is a placeholder for a condition that will never be true. If the `.false.` were instead `.true.`, this sets a custom stopping condition based on the star's hydrogen mass, which is a member of the `s` structure with a key of `star_mass_h1`. Assuming the stopping condition has been met, you can see a message being printed out, and the crucial line `extras_check_model = terminate`, which tells MESA to stop the evolution and exit. The line `s% termination_code = t_extras_check_model` sets a custom termination code that can be used to identify where the star model stopped; this is useful particularly in test cases to ensure that a model stopped for the reason we expect it to stop.

So where does your code go? I recommend putting it right after the `extras_check_model = keep_going` line, as this is where you can add your own custom code that will run at the end of each timestep.
</div>
</details>

<details class="hx-border hx-border-green-200 dark:hx-border-green-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-green-100 dark:hx-bg-neutral-800 hx-text-green-900 dark:hx-text-green-200 hx-px-4 hx-py-2 hx-m-0 hx-cursor-pointer">
<em>Answer</em>
</summary>
<div class="hx-p-4">

Your final `extras_check_model` function should look like this (I've removed the bogus stopping condition and extra comments; see hint above for context):

```fortran
integer function extras_check_model(id)
    integer, intent(in) :: id
    integer :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    extras_check_model = keep_going
    write(*,*) 'Hello, MESA!'
    
    if (extras_check_model == terminate) s% termination_code = t_extras_check_model
end function extras_check_model
```

Ensure that your function looks just like this, with the `write(*,*) 'Hello, MESA!'` line added after the `extras_check_model = keep_going` line. Then in the terminal, run the following commands to compile and run the project:

```bash
./mk && ./rn
```
You should see a bunch of messages printed to the terminal, including `Hello, MESA!` printed at the end of each timestep. If you see any errors, read them carefully, and if you can't figure out what went wrong, ask a TA or tablemate for help.
</div>
</details>

Now that you've got some working code, let's break it! We're goint to intentionally introduce a syntax error and see what happens.

**Task 2.5:** Change the `write(*,*) 'Hello, MESA!'` line to `write(*,*) 'Hello, MESA!`. Notice the missing closing quote at the end of the string. Compile the project again and read the error message carefully. Could you figure out what went wrong without the benefit of knowing what the error was going to be?

<details class="hx-border hx-border-green-200 dark:hx-border-green-200 hx-rounded-md hx-my-2">
<summary class="hx-bg-green-100 dark:hx-bg-neutral-800 hx-text-green-900 dark:hx-text-green-200 hx-py-2 hx-px-4 hx-m-0 hx-cursor-pointer">
<em>Answer</em>
</summary>
<div class="hx-p-4">

Your [broken] code should now look like this:

```fortran
integer function extras_check_model(id)
    integer, intent(in) :: id
    integer :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    extras_check_model = keep_going
    write(*,*) 'Hello, MESA!
    
    if (extras_check_model == terminate) s% termination_code = t_extras_check_model
end function extras_check_model
```

When you run `./mk`, you should see an error message like this:

```
../src/run_star_extras.f90:100:22:

  100 |          write(*,*) 'Hello, MESA!
      |                      1
Error: Unterminated character constant beginning at (1)
make: *** [run_star_extras.o] Error 1

FAILED
```
This indicates that the string beginning at the position marked by "1" (below the letter H) on line 100 (for me, at least) is unterminated, meaning that the compiler expected a closing quote but didn't find one. The compiler is pretty good at pointing out where the error is, but sometimes it can be a bit more cryptic than this helpful error. But don't ignore compiler errors! They are your friend, and they will help you find and fix bugs in your code.
</div>
</details>

**Task 2.6:** "Fix" the error by deleting the entire `write(*,*) 'Hello, MESA!` line. Compile and run the project again. You should see no output from the `extras_check_model` function, as it is now empty.

You've now made some edits to the `run_star_extras.f90` file, compiled it, and run it successfully. You've even seen what an error looks like. Now let's get to doing something more interesting.

## Part 3: Adding a Custom Stopping Condition
If you assume the Earth is a perfect blackbody, its equilibrium temperature is given by

$$T_\oplus = T_\odot \left(\frac{R_\odot}{2\,\mathrm{AU}}\right)^{1/2}$$