---
weight: 1
author: Saskia Hekker, Susmita Das, Zhao Guo, Arthur Le Saux and Noi Shitrit for MESA School Leuven 2025
---

## Maxilab2: Different Reaction Rates
### Background:

During the core helium-burning (CHeB) phase, the energy production from the core is primarily driven by two nuclear reactions:

- The **triple-alpha process** ($3\alpha$): three helium nuclei (${}^4\mathrm{He}$) fuse to form carbon (${}^{12}\mathrm{C}$). It occurs in two steps: ${}^4\mathrm{He} + {}^4\mathrm{He} \rightarrow {}^8\mathrm{Be}$ and ${}^8\mathrm{Be} + {}^4\mathrm{He} \rightarrow {}^{12}\mathrm{C} + \gamma$.
- The ${}^{12}\mathrm{C}(\alpha, \gamma)^{16}\mathrm{O}$ reaction: a carbon nucleus captures an alpha particle to form oxygen (${}^{12}\mathrm{C} + {}^4\mathrm{He} \rightarrow {}^{16}\mathrm{O} + \gamma$).

As mentioned in the introduction to the Maxilab, nuclear reaction rates and their temperature dependence are a source of uncertainty in RC evolution, leading to different stellar interior structures and different period spacings to compare with observations. Helium burning in RC stars is driven primarily by two nuclear reactions. The $3\alpha$ process dominates during the early stages of the core helium-burning phase, while the ${}^{12}\mathrm{C}(\alpha, \gamma){}^{16}\mathrm{O}$ reaction becomes more important later on.

These reactions are highly temperature-sensitive and uncertain, especially the ${}^{12}\mathrm{C}(\alpha, \gamma){}^{16}\mathrm{O}$ rate. In stellar interiors, this reaction occurs at low energies (hundreds of keV), where the cross-section is extremely small because the Coulomb barrier suppresses the reaction probability. Direct measurements in the laboratory at these energies are impractical, so experiments are performed at higher energies (in the MeV range) and extrapolated to stellar conditions using theoretical models. This extrapolation introduces significant uncertainty.

Changes in these rates affect the core composition, the duration of the core helium-burning (CHeB) phase, and, indirectly, the size and structure of the convective core. This, in turn, influences the period spacing $\Delta \Pi$, making reaction rates a key variable to explore.

In this Maxilab2, we will learn how to change the reaction rates in MESA, and we will reproduce Figure 5 and Figure 6 from Noll et al. 2024 together as a class. Each table will explore a different initial stellar mass and reaction rate.

Figure 5 from Noll et al. 2024 shows the evolution of $\Delta \Pi$ during the CHeB phase for different $3\alpha$ reaction rates as a function of CHeB age (top panel) and central helium abundance (lower panel).
![Figure 5 from Noll et al. 2024](/thursday/aa48276-23-fig5.jpg)

Same as Figure 5, but for different ${}^{12}\mathrm{C}(\alpha, \gamma){}^{16}\mathrm{O}$ reaction rates:
![Figure 6 from Noll et al. 2024](/thursday/aa48276-23-fig6.jpg)

### Aims
**MESA aims**: In this Maxilab, you will learn how to find and modify the nuclear reaction network, how to read the reaction network files and where to find them in the `$MESA_DIR`. You will learn how to change reaction rates for specific profiles and how to incorporate all of that into your MESA inlist. You will also learn how to navigate the MESA documentation.

**Science aims**: You will learn how changing the reaction rate for a specific evolutionary phase in stellar evolution affects the composition and inner structure, and hence the period spacing pattern.

**Solution**: In case you get stuck at any point during the exercises, you can find the solution for this Maxilab [here](https://github.com/Noi-Shitrit/MESA_summer_school-maxilab2-Day4/blob/main/maxilab2_solution.zip). Clicking this link will download a zipped directory named: maxilab2_solution.zip.

### Setting up the MESA model
In this Maxilab, we will fix the mixing scheme to maximal overshooting to test the effect of reaction rates on the period spacing.

If you ran your MESA models in Maxilab1 using the maximal overshooting scheme, you can copy that work directory and continue this Maxilab with it. If you used another mixing scheme, or if you are not sure about your solution, please download the correct model from [here](https://github.com/Noi-Shitrit/MESA_summer_school-maxilab2-Day4/blob/main/maxilab2.zip). This link will download a work directory named **maxilab2.zip**.

If you want to unzip the folder using the terminal, you can use:
```linux
unzip maxilab2.zip
```

**Terminal commands**:

```linux
cd maxilab2
./clean && ./mk
```

Make sure that you are able to compile and start the run without any issues, and stop the run after you see the pgplot window.

{{< details title="Task 1" closed="false" >}}
Go over the `inlist_project` file. Make sure that maximal overshooting is indeed the mixing scheme that is set.
{{< /details >}}

{{< details title="Hint 1" closed="true" >}}
There are different mixing schemes inside the solution to Maxilab1 that you downloaded. There are comments explaining each one, and there is one for the maximal overshooting scheme.  
Make sure that all the other mixing schemes are commented out, leaving only the maximal overshooting one active.
{{< /details >}}

{{< details title="Task 2" closed="false" >}}
- Look for the nuclear reaction network name that is used by default if you do not specify another one in your inlist.  
- Locate the corresponding network file, open it, and find the reaction rate entries related to the He-burning processes.
{{< /details >}}

{{< details title="Hint 2" closed="true" >}}
- Look for the `&star_job` controls in the MESA documentation ([available here](https://github.com/noi26/MESA_summer_school-maxilab2-Day4/blob/main/maxilab2.zip), under `Reference and Defaults -> star_job`). Find the default nuclear reaction network name there.  
- Check your `inlist` for the `&star_job` controls that set the reaction network. If none is specified, MESA will use its default.  
- Look in `$MESA_DIR/data/net_data/nets/` to see which file corresponds to that default network.  
- Open the network file in a text editor and examine the listed reaction entries.  
- Identify the entries corresponding to the triple-alpha process and the ${}^{12}\mathrm{C}(\alpha, \gamma){}^{16}\mathrm{O}$ reaction.  
- Copy the names of these entries for Task 3.
{{< /details >}}


{{< details title="Solution 2" closed="true" >}}
- The name of the default nuclear reaction network in MESA is `basic.net`. This is also the file you need to open to find the entries corresponding to the triple-alpha process and the ${}^{12}\mathrm{C}(\alpha, \gamma){}^{16}\mathrm{O}$ reaction, located in `$MESA_DIR/data/net_data/nets/`.  
- The entries are: `r_he4_he4_he4_to_c12`, `r_c12_ag_o16`.
{{< /details >}}

The names of the reaction rate entries you found refer to files that describe the reaction rate of each process as a function of temperature. If you want to use another file for a specific process, for example one computed in a recent study that MESA does not include yet, you can add these files and direct MESA to read them. These files can be found under: `ls $MESA_DIR/data/rates_data/rate_tables`.

{{< details title="Task 3" closed="false" >}}
- Find the `inlist` variables that need to be changed in order to modify the reaction rates for the two He-burning processes (use the names of the reaction rate entries you found in Task 2) and edit your `inlist` accordingly.  
- The reaction rate values to test are the default rates multiplied by 0.25, 0.5, 1, 2, and 5 for the $3\alpha$ process while keeping the ${}^{12}\mathrm{C}(\alpha, \gamma){}^{16}\mathrm{O}$ reaction rate at 1, and vice versa. Each table will be assigned a different value to compute.
{{< /details >}}

{{< details title="Hint 3" closed="true" >}}
- Check the `&star_job` section in the MESA documentation for variables that let you specify special reaction rate factors for individual reactions. You can also look in the `$MESA_DIR/star/defaults/star_job.defaults` file.  
- Look for three `inlist` variables that let you control the number of special rate factors to assign, specify the name of the reaction, and set the scaling factor.
{{< /details >}}

{{< details title="Solution 3" closed="true" >}}
This is how the addition to the `&star_job` section in your `inlist_project` file should look:  
```fortran
num_special_rate_factors = 2
reaction_for_special_factor(1) = 'r_he4_he4_he4_to_c12'
reaction_for_special_factor(2) = 'r_c12_ag_o16'
special_rate_factor(1) = 1  ! 0.25, 0.5, 1.00, 2.00, 5.00
special_rate_factor(2) = 5   ! 0.25, 0.5, 1.00, 2.00, 5.00
```

In this example, the $3\alpha$ reaction rate (`r_he4_he4_he4_to_c12`) is set to 1, and the ${}^{12}\mathrm{C}(\alpha, \gamma){}^{16}\mathrm{O}$ reaction rate (`r_c12_ag_o16`) is scaled by a factor of 5.
{{< /details >}}

{{< details title="Task 4" closed="false" >}}
Finally, find the two `&star_job` variables that will print to the terminal during the run: one that lists the reactions in the current network, and one that provides detailed information about those reactions.
{{< /details >}}

{{< details title="Solution 4" closed="true" >}}
This is how the addition to the `&star_job` section in your `inlist_project` file should look:  
```fortran
show_net_reactions_info = .true.
list_net_reactions = .true.
```
{{< /details >}}

Before we start running our models, let’s make sure we understand what we have in our `pgstar` plot.  
We can add two plots that will give us information about the reaction rates and the temperature changes during the run.

{{< details title="Task 5" closed="false" >}}
Replace the Kippenhahn diagram and the mixing profile plot you added in Maxilab1 to make more space for our two new plots, with the following:  
- An abundance plot of all the elements in the nuclear reaction network we are using, displayed as mass fraction (in log scale) as a function of the mass profile of the star.  
- The central temperature ($\log_{10}(T_c)$) as a function of the central density ($\log_{10}(\rho_c)$) in log-log scale.
{{< /details >}}

{{< details title="Hint 5" closed="true" >}}
These plots are included in the MESA `pgstar` defaults and can be added easily.  
- Look in the MESA documentation under **Using MESA / Using PGSTAR**, where you will find **The Inventory of Plots** section with the available plot titles.  
- You can also check the `$MESA_DIR/star/defaults/pgstar.defaults` file to see the default plot settings and titles you can use.
{{< /details >}}

{{< details title="Solution 5" closed="true" >}}
- Replace this line: `Grid1_plot_name(1) = 'Kipp'` with: `Grid1_plot_name(1) = 'Abundance'`.  
- Replace this line: `Grid1_plot_name(5) = 'Mixing'` with: `Grid1_plot_name(5) = 'TRho'`.

Your complete `inlist_pgstar` should look like this:
```fortran
&pgstar

  ! Set up grid layout

  file_white_on_black_flag = .false.

  Grid1_win_flag = .true.

  Grid1_file_interval = 5
  Grid1_file_width = 25

  Grid1_num_cols = 10
  Grid1_num_rows = 10

  Grid1_win_width = 14
  Grid1_win_aspect_ratio = 0.5
  Grid1_xleft = 0.00
  Grid1_xright = 1.00
  Grid1_ybot = 0.00
  Grid1_ytop = 1.00

  Grid1_num_plots = 8

  ! Add Abundance plot

  Grid1_plot_name(1) = 'Abundance'

  Grid1_plot_row(1) = 1
  Grid1_plot_rowspan(1) = 5
  Grid1_plot_col(1) = 1
  Grid1_plot_colspan(1) = 4

  Grid1_plot_pad_left(1) = 0.05
  Grid1_plot_pad_right(1) = 0.01
  Grid1_plot_pad_top(1) = 0.04
  Grid1_plot_pad_bot(1) = 0.05
  Grid1_txt_scale_factor(1) = 0.5

  ! Add HR diagram

  Grid1_plot_name(2) = 'HR'
  Grid1_plot_row(2) = 6
  Grid1_plot_rowspan(2) = 3
  Grid1_plot_col(2) = 1
  Grid1_plot_colspan(2) = 2

  Grid1_plot_pad_left(2) = 0.05
  Grid1_plot_pad_right(2) = 0.01
  Grid1_plot_pad_top(2) = 0.02
  Grid1_plot_pad_bot(2) = 0.07
  Grid1_txt_scale_factor(2) = 0.5

  ! Add abudance profile plot

  Grid1_plot_name(3) = 'Power'

  Grid1_plot_row(3) = 6
  Grid1_plot_rowspan(3) = 3
  Grid1_plot_col(3) = 3
  Grid1_plot_colspan(3) = 2

  Grid1_plot_pad_left(3) = 0.05
  Grid1_plot_pad_right(3) = 0.01
  Grid1_plot_pad_top(3) = 0.02
  Grid1_plot_pad_bot(3) = 0.07
  Grid1_txt_scale_factor(3) = 0.5

  ! Add text panel

  Grid1_plot_name(4) = 'Text_Summary1'
  Grid1_plot_row(4) = 9
  Grid1_plot_rowspan(4) = 2
  Grid1_plot_col(4) = 1
  Grid1_plot_colspan(4) = 10

  Grid1_plot_pad_left(4) = 0.00
  Grid1_plot_pad_right(4) = 0.00
  Grid1_plot_pad_top(4) = 0.00
  Grid1_plot_pad_bot(4) = 0.00
  Grid1_txt_scale_factor(4) = 0

  Text_Summary1_name(1,1) = 'model_number'
  Text_Summary1_name(2,1) = 'star_age'
  Text_Summary1_name(3,1) = 'log_dt'
  Text_Summary1_name(4,1) = 'luminosity'
  Text_Summary1_name(5,1) = 'Teff'
  Text_Summary1_name(6,1) = 'radius'
  Text_Summary1_name(7,1) = 'log_g'
  Text_Summary1_name(8,1) = 'star_mass'

  Text_Summary1_name(1,2) = 'log_cntr_T'
  Text_Summary1_name(2,2) = 'log_cntr_Rho'
  Text_Summary1_name(3,2) = 'log_center_P'
  Text_Summary1_name(4,2) = 'center h1'
  Text_Summary1_name(5,2) = 'center he4'
  Text_Summary1_name(6,2) = ''
  Text_Summary1_name(7,2) = ''
  Text_Summary1_name(8,2) = ''

  Text_Summary1_name(1,3) = 'log_Lnuc'
  Text_Summary1_name(2,3) = 'log_Lneu'
  Text_Summary1_name(3,3) = 'log_LH'
  Text_Summary1_name(4,3) = 'log_LHe'
  Text_Summary1_name(5,3) = 'num_zones'
  Text_Summary1_name(6,3) = ''
  Text_Summary1_name(7,3) = ''
  Text_Summary1_name(8,3) = ''

  Text_Summary1_name(1,4) = 'nu_max'
  Text_Summary1_name(2,4) = 'delta_nu'
  Text_Summary1_name(3,4) = 'delta_Pg'
  Text_Summary1_name(4,4) = ''
  Text_Summary1_name(5,4) = ''
  Text_Summary1_name(6,4) = ''
  Text_Summary1_name(7,4) = ''
  Text_Summary1_name(8,4) = ''

  ! Add temperature-density plot

  Grid1_plot_name(5) = 'TRho'
  Grid1_plot_row(5) = 1
  Grid1_plot_rowspan(5) = 4
  Grid1_plot_col(5) = 6
  Grid1_plot_colspan(5) = 4

  Grid1_plot_pad_left(5) = 0.05
  Grid1_plot_pad_right(5) = 0.05
  Grid1_plot_pad_top(5) = 0.04
  Grid1_plot_pad_bot(5) = 0.07
  Grid1_txt_scale_factor(5) = 0.5

  Grid1_file_flag = .true.
  Grid1_file_dir = 'pgplot'
  Grid1_file_prefix = 'grid_'
  file_white_on_black_flag = .true.
  Grid1_file_interval = 10

  ! Add mode inertia panel

  Grid1_plot_name(6) = 'History_Panels1' !
  Grid1_plot_row(6) = 5
  Grid1_plot_rowspan(6) = 4
  Grid1_plot_col(6) = 6
  Grid1_plot_colspan(6) = 5

  History_Panels1_win_flag = .true.
  History_Panels1_num_panels = 2
  History_Panels1_xaxis_name = 'model_number'
  History_Panels1_yaxis_name(1) ='delta_Pg'
  History_Panels1_other_yaxis_name(1) = ''
  History_Panels1_yaxis_name(2) ='center_he4'
  History_Panels1_other_yaxis_name(2) = ''
  History_Panels1_automatic_star_age_units = .true.

  Grid1_plot_pad_left(6) = 0.05
  Grid1_plot_pad_right(6) = 0.05
  Grid1_plot_pad_top(6) = 0.04
  Grid1_plot_pad_bot(6) = 0.07
  Grid1_txt_scale_factor(6) = 0.5

/ ! end of pgstar namelist
```
{{< /details >}}

Now run your models. In the `pgplot` window, you will be able to observe the changing abundances of the elements involved in He-burning (mainly He4, Be7, C12, and O16) as the temperature of the star changes.

```linux
cd maxilab2
./clean && ./mk
./rn
```

This is how your `pgplot` window is supposed to look:
![pgplot](/thursday/pgplot.png)

The run should take around 10 minutes on 2 threads, since the star needs to evolve into the RC phase.

Meanwhile, make sure you’re ready to upload your history files once your run is complete so we can create a live plot using the files you upload [to this folder](https://tauex-my.sharepoint.com/:f:/g/personal/noyshitrit_tauex_tau_ac_il/Eh7ABs_UnNFAmwRLzIIZNaUBg48dgmIeCfP5RmVarcPK-A?e=FfRMbG).  
Additionally, we have prepared a Google Colab notebook. In this notebook, you'll upload your MESA `history.data` file and generate basic plots of $\Delta \Pi$ versus age and central helium abundance.

## Google Colab Instructions:
1. [Click here](https://colab.research.google.com/drive/1g9lz20FU9IVrg3CJTF9y5jZ80SYJghbE?usp=sharing) to open the notebook and connect to your Google account.  
2. You can review the Python script if you'd like. You don’t need to install anything manually—just run the notebook cells, and it will automatically install any required packages. It uses the `mesa-reader` package (more information [here](https://github.com/wmwolf/py_mesa_reader)) to read the history file easily.  
3. During the run (which will take 1–2 minutes), Colab will prompt you to upload a file. Please upload your `history.data` file when asked.  
4. You will see the generated plot displayed below in the notebook.

{{< details title="Bonus Task" closed="false" >}}
We will learn how to create a new nuclear reaction network. We will then run the same inlists, but using the new reaction network that we create.

Up until now, we have used the `basic.net` network located in the `$MESA_DIR/data/net_data/nets` directory.  
Copy the `basic.net` file to your working directory and give it a new name, like `basic_custom.net`, then open the file and review its contents.  
The file includes two functions: `add_isos()` and `add_reactions()`. For more information about how these functions work and how to create a custom network, see the [MESA documentation](https://docs.mesastar.org/en/latest/net/nets.html).

We will comment out all the helium-burning reactions except for: `r_he4_he4_he4_to_c12` and `r_c12_ag_o16`.


Edit your `inlist_project` to include the new network:  
```fortran
! new net
change_initial_net = .true.
new_net_name = 'basic_custom.net'
```

And comment out the reaction rate variables in your `inlist`:
```fortran
!num_special_rate_factors = 2
!reaction_for_special_factor(1) = 'r_he4_he4_he4_to_c12'
!reaction_for_special_factor(2) = 'r_c12_ag_o16'
!special_rate_factor(1) = 1  ! 0.25, 0.5, 1.00, 2.00, 5.00
!special_rate_factor(2) = 5   ! 0.25, 0.5, 1.00, 2.00, 5.00
```

MESA will look for `basic_custom.net` both in your working directory and in `$MESA_DIR/data/net_data/nets`.

Run and re-plot $\Delta \Pi$ versus age and central helium abundance using the Google Colab notebook again (you will need to upload your new `history.data` file).  

Not much has changed, right?  
This shows us that the helium-burning reaction processes that most influence the period spacing—and therefore the interior structure of the star—are: `r_he4_he4_he4_to_c12` and `r_c12_ag_o16`.

If you comment one of them out (just for the exercise—it doesn't come from a real physical motivation), you will already start to see a more noticeable change in the period spacing plots, and hence, also in the interior structure of the star.

You can find the complete work directory solution for the bonus exercise [here](https://github.com/Noi-Shitrit/MESA_summer_school-maxilab2-Day4/blob/main/maxilab2_bonus_solution.zip).

This bonus task took inspiration from one of last year's MESA Summer School labs. If you want to learn more about changing nuclear networks in MESA, please look [here](https://courtcraw.github.io/mesadu_wdbinaries/lab2.html).
{{< /details >}}
