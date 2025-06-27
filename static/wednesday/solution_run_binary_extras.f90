! ***********************************************************************
!
!   Copyright (C) 2012-2019  Bill Paxton & The MESA Team
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
      module run_binary_extras 

      use star_lib
      use star_def
      use const_def
      use const_def
      use chem_def
      use num_lib
      use binary_def
      use math_lib
      
      implicit none

      integer, parameter :: ilx_reached_rlo = 1
      
      contains
      
      subroutine extras_binary_controls(binary_id, ierr)
         integer :: binary_id
         integer, intent(out) :: ierr
         type (binary_info), pointer :: b
         ierr = 0

         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then
            write(*,*) 'failed in binary_ptr'
            return
         end if

         ! Set these function pointers to point to the functions you wish to use in
         ! your run_binary_extras. Any which are not set, default to a null_ version
         ! which does nothing.
         b% how_many_extra_binary_history_header_items => how_many_extra_binary_history_header_items
         b% data_for_extra_binary_history_header_items => data_for_extra_binary_history_header_items
         b% how_many_extra_binary_history_columns => how_many_extra_binary_history_columns
         b% data_for_extra_binary_history_columns => data_for_extra_binary_history_columns

         b% extras_binary_startup=> extras_binary_startup
         b% extras_binary_start_step=> extras_binary_start_step
         b% extras_binary_check_model=> extras_binary_check_model
         b% extras_binary_finish_step => extras_binary_finish_step
         b% extras_binary_after_evolve=> extras_binary_after_evolve

         ! Once you have set the function pointers you want, then uncomment this (or set it in your star_job inlist)
         ! to disable the printed warning message,
          b% warn_binary_extra =.false.
         
      end subroutine extras_binary_controls


      integer function how_many_extra_binary_history_header_items(binary_id)
         use binary_def, only: binary_info
         integer, intent(in) :: binary_id
         how_many_extra_binary_history_header_items = 0
      end function how_many_extra_binary_history_header_items


      subroutine data_for_extra_binary_history_header_items( &
           binary_id, n, names, vals, ierr)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id, n
         character (len=maxlen_binary_history_column_name) :: names(n)
         real(dp) :: vals(n)
         integer, intent(out) :: ierr
         ierr = 0
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then
            write(*,*) 'failed in binary_ptr'
            return
         end if
      end subroutine data_for_extra_binary_history_header_items


      integer function how_many_extra_binary_history_columns(binary_id)
         use binary_def, only: binary_info
         integer, intent(in) :: binary_id
         how_many_extra_binary_history_columns = 0
      end function how_many_extra_binary_history_columns


      subroutine data_for_extra_binary_history_columns(binary_id, n, names, vals, ierr)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer, intent(in) :: n
         character (len=maxlen_binary_history_column_name) :: names(n)
         real(dp) :: vals(n)
         integer, intent(out) :: ierr
         ierr = 0
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then
            write(*,*) 'failed in binary_ptr'
            return
         end if
         
      end subroutine data_for_extra_binary_history_columns
      
      
      integer function extras_binary_startup(binary_id,restart,ierr)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer, intent(out) :: ierr
         logical, intent(in) :: restart
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if
         
!          b% s1% job% warn_run_star_extras = .false.
          extras_binary_startup = keep_going
      end function  extras_binary_startup
      
      integer function extras_binary_start_step(binary_id,ierr)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer, intent(out) :: ierr

         extras_binary_start_step = keep_going
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if
      
      end function  extras_binary_start_step
      
      !Return either keep_going, retry or terminate
      integer function extras_binary_check_model(binary_id)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer :: ierr
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if  
         extras_binary_check_model = keep_going
        
      end function extras_binary_check_model
      
      
      ! returns either keep_going or terminate.
      ! note: cannot request retry; extras_check_model can do that.
      integer function extras_binary_finish_step(binary_id)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer :: ierr
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if  
         extras_binary_finish_step = keep_going

         !!! HINT block begins !!!
         if (b% s1% center_he4 < 1d-6 .and. b% s1% center_c12 < 0.01) then
             write(*,*) '*********************************************'
             write(*,*) '**** Terminated at core carbon depletion ****'
             write(*,*) '*********************************************'
             extras_binary_finish_step = terminate            
         end if
         !!! HINT block ends !!!

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

         !!!!! TASK 2 block begins !!!
         if ((abs(b% mtransfer_rate)/Msun*secyer > 1d-3) .and. (b% s1% dt/secyer < 0.1)) then
             write(*,*) '**********************************************'
             write(*,*) '** Terminated due to unstable mass transfer **'
             write(*,*) '**********************************************'
             extras_binary_finish_step = terminate
         end if
         !!!!! TASK 2 block ends !!!

         if (b% r(1) > b% rl(1) .and. .not. b% lxtra(ilx_reached_rlo)) then 
            ! things to do upon the first RLOF is reached
            b% lxtra(ilx_reached_rlo) = .true.
            b% s1% solver_itermin_until_reduce_min_corr_coeff = 25
            b% s1% solver_max_tries_before_reject = 40
            b% s1% max_tries_for_retry = 40
            b% s1% tiny_corr_coeff_limit = 1000    
            b% s1% corr_coeff_limit = 0.2d0
            b% s1% ignore_too_large_correction = .true.
            b% s1% ignore_min_corr_coeff_for_scale_max_correction = .true.
            b% s1% use_gold_tolerances = .true.
            b% s1% use_gold2_tolerances = .false.
            b% s1% gold_solver_iters_timestep_limit = 30
            b% s1% gold_iter_for_resid_tol3 = 10
            b% s1% gold_tol_residual_norm3 = 1d-6
            b% s1% gold_tol_max_residual3 = 1d-3
            b% s1% tol_max_correction = 1d-2
            b% s1% tol_correction_norm = 1d-3
            b% s1% max_corr_jump_limit = 1d99
            b% s1% max_resid_jump_limit = 1d99

            b% s1% make_gradr_sticky_in_solver_iters = .true.
         end if
         
      end function extras_binary_finish_step
      
      subroutine extras_binary_after_evolve(binary_id, ierr)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer, intent(out) :: ierr
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if      
         
 
      end subroutine extras_binary_after_evolve     
      
      end module run_binary_extras
