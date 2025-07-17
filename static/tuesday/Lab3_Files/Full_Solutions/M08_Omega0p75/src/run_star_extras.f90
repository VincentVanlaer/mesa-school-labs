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

         !!!! ADD IN OTHER_TORQUE AND OTHER_AM_MIXING!!!!
         s% other_torque => meridional_circulation
         s% other_am_mixing => additional_nu
         !!!! !!!!

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

      
      !! CUSTOM OTHER TORQUE SUBROUTINE !!
      subroutine meridional_circulation(id, ierr)
         ! Variable Declarations
         integer, intent(in) :: id
         integer, intent(out) :: ierr
         type (star_info), pointer :: s

         real(dp), allocatable :: U_r(:), mer_comp(:), dmer_comp_dr(:)
         real(dp) :: total_torque_envelope

         !!!! DECLARE THREE ADDITIONAL INTEGERS: k, k0, and nz !!!!
         integer :: k, k0, nz 
         !!!! !!!!

         
         ! Error Check and Call Star Pointer
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return

         ! Get number of zones
         nz = s% nz        ! Number of zones in the model

         ! Get index where the radiative envelope starts
         k0 = 0
         do k = s% nz, 1, -1 ! Start at the edge of the convective core.
            if (s% mixing_type(k) == minimum_mixing) then
               k0 = k
               exit
            end if
         end do

         ! Allocate arrays
         allocate(U_r(nz), mer_comp(nz), dmer_comp_dr(nz))

         ! Calculate
         !!!! ADD IN THE EQUATION FOR U_r AND mer_comp !!!!
         U_r = (s% r) / (s% r(1)) * 0.001 ! cm s-1
         mer_comp = s% rho * pow4(s% r) * (s% omega) * U_r ! g cm2 s-2
         !!!! !!!!
         dmer_comp_dr = (mer_comp(1:nz-1)-mer_comp(2:nz)) / (s% r(1:nz-1) - s% r(2:nz)) ! g cm s-2
         s% xtra2_array(1:nz-1) = dmer_comp_dr


         ! Smooth dmer_comp_dr
         call smooth_dFdr(id, 1, nz-1, s% xtra2_array, s% xtra6_array, ierr)

         ! For zones in the radiative envelope, apply torque using dmer_comp_dr
         ! Note, the indexing for zones starts at the surface with k = 1, then 
         ! continues to the core with k = nz
         do k = 1, k0 ! k0 is the index where the radiative envelope starts
            ! Note, extra_jdot is the rate at which specific angular momentum is changed, so the units are cm2 s-2
            s% extra_jdot(k) = s% extra_jdot(k) + s% xtra2_array(k) / (5d0 * pow2(s% r(k)) * s% rho(k))
            s% xtra1_array(k) = s% extra_jdot(k) ! Save to xtra array for plotting
         end do

         ! Get the total torque on the envelope
         total_torque_envelope = dot_product(s% extra_jdot(1:k0), s% dm_bar(1:k0)) ! g cm^2 s^-2, torque on the envelope

         ! Save the total torque to an extra star variable
         s% xtra(1) = total_torque_envelope

         ! For zones in the convective core, apply reverse torque to ensure AM conservation
         do k = k0+1, nz
            s% extra_jdot(k) = -total_torque_envelope / ((nz - k0) * s% dm_bar(k))
            s% xtra1_array(k) = s% extra_jdot(k) ! Save to xtra array, for plotting
         end do

      end subroutine meridional_circulation


      !! CUSTOM SMOOTHING ROUTINE !!
      subroutine smooth_dFdr(id, k0, k1, array, work, ierr)
         integer, intent(in) :: id, k0, k1
         integer, intent(out) :: ierr
         type (star_info), pointer :: s

         real(dp), pointer, dimension(:) :: array, work
         logical, parameter :: preserve_sign = .false.
         ierr =0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         call weighed_smoothing(array(k0:k1), k1-k0, 100, preserve_sign, work) !100 array for smoothing, number of cells, smooth 2*ns+1 cells, preserve sign, work array
      end subroutine smooth_dFdr


      !! WEIGHED SMOOTHING !!
      subroutine weighed_smoothing(dd, n, ns, preserve_sign, ddold)
      !     based on routine written by S.-C. Yoon, 18 Sept. 2002
      !     for smoothing  any variable (dd) with size n over 2*ns+1 cells.
         real(dp), intent(inout) :: dd(:) ! (n)
         integer, intent(in) :: n, ns
         logical, intent(in) :: preserve_sign
         real(dp), intent(inout) :: ddold(:) ! (n) work array

         integer :: nweight, mweight, i, j, k
         real(dp) :: weight(2*ns+1), sweight, v0

         include 'formats'

         do i = 1,n
           ddold(i) = dd(i)
         end do
         
         !--preparation for smoothing --------
         nweight = ns
         mweight = 2*nweight+1
         do i = 1,mweight
            weight(i) = 0d0
         end do
         weight(1) = 1d0
         do i = 1,mweight-1
            do j = i+1,2,-1
               weight(j) = weight(j) + weight(j-1)
            end do
         end do

         !--smoothing ------------------------
         do i=2,n-1
            sweight=0d0
            dd(i)=0d0
            v0 = ddold(i)
            do j = i, max(1,i-nweight), -1
               k=j-i+nweight+1
               if (preserve_sign .and. v0*ddold(j) <= 0) exit
               sweight = sweight+weight(k)
               dd(i) = dd(i)+ddold(j)*weight(k)
            end do
            do j = i+1, min(n,i+nweight)
               k=j-i+nweight+1
               if (preserve_sign .and. v0*ddold(j) <= 0) exit
               sweight = sweight+weight(k)
               dd(i) = dd(i)+ddold(j)*weight(k)
            end do
            if (sweight > 0) then
               sweight = 1d0/sweight
               dd(i) = dd(i)*sweight
            end if
         end do
      end subroutine weighed_smoothing


      !! CUSTOM VISCOSITY ROUTINE!!
      subroutine additional_nu(id, ierr)
         integer, intent(in) :: id
         integer, intent(out) :: ierr
         integer :: k, k0

         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return

         k0 = 0
         do k = s% nz, 1, -1 ! Start at the edge of the convective core.
            if (s% mixing_type(k) == minimum_mixing) then
               k0 = k
               exit
            end if
         end do

         do k = 1, k0
            s% am_nu_omega(k) = s% am_nu_omega(k) + s% uniform_am_nu_non_rot
         end do

         do k = k0+1, s% nz
            s% am_nu_omega(k) = s% am_nu_omega(k) + s% D_mix(k)
         end do

      end subroutine additional_nu


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
         how_many_extra_history_columns = 1 !!!! !!!! CHANGE NUMBER OF EXTRA HISTORY COLUMNS
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
         
         !!!! ADD TOTAL TORQUE HERE !!!!
         names(1) = "total_torque_envelope"
         vals(1) = s% xtra(1) 
         !!!! !!!!
         
      end subroutine data_for_extra_history_columns

      
      integer function how_many_extra_profile_columns(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         how_many_extra_profile_columns = 2 !!!! !!!! CHANGE NUMBER OF EXTRA PROFILE COLUMNS
      end function how_many_extra_profile_columns
      
      
      subroutine data_for_extra_profile_columns(id, n, nz, names, vals, ierr)
         integer, intent(in) :: id, n, nz
         character (len=maxlen_profile_column_name) :: names(n)
         real(dp) :: vals(nz,n)
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         integer :: k
         !!!!
         !real(dp) :: extra_torque
         !!!!
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


         !!!! ADD EXTRA_JDOT AND LOG_dJ_OVER_J HERE !!!!
         names(1) = "extra_jdot"
         names(2) = "log_dJ_over_J"
         do k = 1, nz
             vals(k, 1) = s% xtra1_array(k)
             vals(k, 2) = log10(abs(s% xtra1_array(k) * s% dt / s% j_rot(k)))
         end do  
         !!!! !!!!

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
      
