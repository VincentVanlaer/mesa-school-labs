# Tuesday Lab-2 | Modifying `run_star_extras.f90` to calculate the Eddington-Sweet circulation velocity

Led by: Philip Mocz

* [Download the Lab](https://ssgithub.com/VincentVanlaer/mesa-school-labs/tree/main/content/tuesday/lab-2)
* [Download the ESTER 2D models](https://ssgithub.com/VincentVanlaer/mesa-school-labs/tree/main/content/tuesday/ester_models)
* [Download solution](https://ssgithub.com/VincentVanlaer/mesa-school-labs/tree/main/content/tuesday/lab-2-solution)

**Goal:** Compute the Eddington-Sweet circulation velocity, `v_ES`, for a star evolved with MESA,
and save it in the profiles output. Compare it against 2D ESTER models.

MESA is quite powerful and flexible. In addition to saving all sorts of information about your star that you can request for in your inlists, MESA lets you extend its functionality by modifying the `run_star_extras.f90` file. This allows you to compute and save additional quantities, such as `v_ES`, directly into the profiles output for further analysis. For these operations, you will need to code in Fortran and learn about MESA's data structures and subroutines. This flexibility enables you to customize your simulations and extract specific data tailored to your research needs.

## Theory

The paper [Heger et al. (2000)](https://ui.adsabs.harvard.edu/abs/2000ApJ...528..368H/abstract) defines the Eddington-Sweet velocity as follows.

From [Kippenhahn (1974)](https://ui.adsabs.harvard.edu/abs/1974IAUS...66...20K/abstract), an estimate of the circulation velocity is:

$$
v_e \equiv \frac{\nabla_{\mathrm{ad}}}{\delta\left(\nabla_{\mathrm{ad}}-\nabla\right)} \frac{\omega^2 r^3 l}{(G m)^2}\left[\frac{2\left(\varepsilon_n+\varepsilon_v\right) r^2}{l}-\frac{2 r^2}{m}-\frac{3}{4 \pi \rho r}\right]
$$

In the presence of $\mu$-gradients, meridional circulation has to work against the potential and thus might be inhibited or suppressed (Mestel 1952, 1953). Formally, this can be written as a "stabilizing" circulation velocity,


$$
v_\mu \equiv \frac{H_P}{\tau_{\mathrm{KH}}^*} \frac{\varphi \nabla_\mu}{\delta\left(\nabla-\nabla_{\mathrm{ad}}\right)}
$$

([Kippenhahn (1974)](https://ui.adsabs.harvard.edu/abs/1974IAUS...66...20K/abstract); [Pinsonneault et al. (1989)](https://ui.adsabs.harvard.edu/abs/1989ApJ...338..424P/abstract)), where

$$
\tau_{\mathrm{KH}}^* \equiv \frac{G m^2}{r\left(l-m \varepsilon_v\right)}
$$

is the local Kelvin-Helmholtz timescale, used here as an
estimate for the local thermal adjustment timescale of the
currents ([Pinsonneault et al. (1989)](https://ui.adsabs.harvard.edu/abs/1989ApJ...338..424P/abstract)).

The Eddington-Sweet velocity is then:

$$
v_{\mathrm{ES}} \equiv \max \left(\left|v_e\right|-\left|v_\mu\right|, 0\right)
$$

For our purposes, we can ignore $\varepsilon_v$ in our calculations.

## Extending MESA

The MESA Documentation at [https://docs.mesastar.org](https://docs.mesastar.org) 
is very useful for describing how to use and modify MESA.
The page [Extending MESA](https://docs.mesastar.org/en/latest/using_mesa/extending_mesa.html) describes, for example, how to compute and save an extra profile by modifying your `run_star_extras.f90` file in your project work directory.

The `run_star_extras.f90` file contains hooks to modify the output profile columns.

* ``how_many_extra_profile_columns``
* ``data_for_extra_profile_columns``

(Note: there are also hooks to add custom history columns)

The first function (`how_many_extra_profile_columns`) needs to be modified to tell MESA how many columns to add. In our case we are interested in adding one new column, so the function should look like:

```fortran
integer function how_many_extra_profile_columns(id)
   integer, intent(in) :: id
   integer :: ierr
   type (star_info), pointer :: s
   ierr = 0
   call star_ptr(id, s, ierr)
   if (ierr /= 0) return
   how_many_extra_profile_columns = 1
end function how_many_extra_profile_columns
```

For this lab, modify your function in your work directory to look like the above.

The second function (`data_for_extra_profile_columns`) will perform the calculation. In this lab, you will fill out this function.

```fortran
subroutine data_for_extra_profile_columns(id, n, nz, names, vals, ierr)
   integer, intent(in) :: id, n, nz
   character (len=maxlen_profile_column_name) :: names(n)
   real(dp) :: vals(nz,n)
   integer, intent(out) :: ierr
   type (star_info), pointer :: s
   integer :: k
   integer :: i
   ierr = 0
   call star_ptr(id, s, ierr)
   if (ierr /= 0) return

   ! IMPLEMENT EDDINTGON-SWEET VELOCITY CALCULATION HERE

   end subroutine data_for_extra_profile_columns
```

You will have to specify the name of the new profile column,
e.g. `names(1) = 'v_ES'`, and its values `vals(i,1)`, where `i` is the `i`-th zone in the star. There are `nz` zones in total. The index 1 refers to the fact that this is the 1st extra column we are filling out.

To calculate the Eddington-Sweet velocity, we will need to know the variable names in the code that correspond to the ones in the equation. I provide a reference below:

| Variable                      | in MESA                   |
|-------------------------------|---------------------------|
| $\nabla_{\mathrm{ad}}$        | s% grada(i)               |
| $\delta$                      | s% chiT(i) / s% chiRho(i) |
| $r$                           | s% r(i)                   |
| $l$                           | s% L(i)                   |
| $m$                           | s% m(i)                   |
| $\rho$                        | s% rho(i)                 |
| $\varepsilon_n$               | s% eps_nuc(i)             |
| $\nabla_{\mathrm{ad}}-\nabla$ | s% gradT_sub_grada(i)     |
| $G$                           | s% cgrav(i)               |
| $\omega$                      | s% omega(i)               |
| $H_P$                         | s% scale_height(i)        |
| $\nabla_\mu$                  | s% am_gradmu_factor       |
| $\varphi$                     | s% smoothed_brunt_B(i)    |

You can find what they do exaclty by searching around in the code with the `grep` command-line tool.
All the variables available can be found in the
`star_data/public/*.inc` include files, and their default values in found in `star/defaults/controls.defaults`.
To see where they appear in the source code, you'll need to search the Fortran `*.f90` source code files.
E.g., in the main MESA directory, try out the following:
```console
grep am_gradmu_factor star/defaults/controls.defaults
grep am_gradmu_factor star_data/private/*.inc
grep am_gradmu_factor star/private/*.f90
```
to see all appearances and uses of `am_gradmu_factor` in the code.


### Bonus


For numerical robustness, MESA sometimes internally smooths variables across cells.
For example, a smoothed $\delta$ looks like the following.

```fortran
! alpha smoothing
alfa = s% dq(i-1) / (s% dq(i-1) + s% dq(i))
delta = alfa * s% chiT(i) / s% chiRho(i) + (1.0d0 - alfa) * s% chiT(i-1) / s% chiRho(i-1)
```

Investigate the result of alpha-smoothing on your calculation of the Eddington-Sweet velocity profile.


## Compare your results against 2D ESTER models

To plot your MESA results against 2D ESTER models, we will use the Python library [mesa-reader](https://billwolf.space/py_mesa_reader/) by Bill Wolf. If you have Python installed on your system, you'll need to install `mesa-reader` (e.g., `pip install mesa-reader`), and run the plotting script provided:

```console
python plot.py
```

Otherwise you can visit the following Google Colab notebook and plot it in the cloud:

[Google Colab MESA Day 2 Minilab 2 notebook](https://colab.research.google.com/drive/1RGBrGY_oHTjxuagSuYkgR7251CPplDug?usp=sharing)

You'll need to upload the MESA output (the files inside `M10_Z0p20_fov0p015_logD3_O20/`) and the ESTER mode (`ester_models/M10_O60_X071Z200_evol_viscv1e7_visc_h1e7_delta010_2_0025.h5`) into the `/content/` folder and press `Run` to create the plot.
