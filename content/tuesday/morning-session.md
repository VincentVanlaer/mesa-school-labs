---
weight: 1
math: true
---

# Beyond Inlists: Extending MESA with `run_star_extras.f90`

Inlists, models and photos are the core of MESA, and you can do a lot of great science without even knowing how to write a line of Fortran code. But fairly soon in your MESA journey, you will run into limits of what you can do with inlists alone. This is where `run_star_extras.f90` comes in. It allows you to extend MESA's capabilities by writing your own Fortran code that can interact with the star model. A few examples of things you can do with `run_star_extras.f90` include:

- creating a custom stopping condition
- changing control parametrs during a run without restarting
- adding custom data to profile or history files
- implementing custom physics, like energy sources or mass loss prescriptions

The goal of these exercises is to get you up and running with `run_star_extras.f90` and provide a resource you can return to when you next need to extend MESA.

## Acknowledgements

This material is strongly influenced by similar material from past MESA schools by Josiah Schwab, a former MESA developer. Specifically, this material is drawn from his introductory materials for the 2021 MESA summer school, which can be found [here](https://jschwab.github.io/mesa-2021/).

## Fortran Basics

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