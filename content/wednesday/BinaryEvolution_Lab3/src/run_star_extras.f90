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
      use chem_def
            
      implicit none

      real(dp), parameter :: ZFeSolar = 1.6d-3
               
      integer, parameter :: ix_comp_wind = 16
                 
      ! declarations for other_winds
         character (len=strlen) :: OB_wind_scheme
         character (len=strlen) :: CSG_wind_scheme
         real(dp) :: Grafener_scaling_factor
         real(dp) :: OB_scaling_factor
         real(dp) :: hot_wind_min_T
         real(dp) :: cool_wind_max_T
         real(dp) :: WNL_wind_min_dg
         real(dp) :: OB_wind_max_dg
         real(dp) :: h_wind_min_h
         real(dp) :: he_wind_max_h
         real(dp) :: he_wind_max_Mdot
         real(dp) :: he_wind_max_Gamm               
         integer :: he_wind_qion_option
         real(dp) :: CSG_wind_min_L
         real(dp) :: AGB_wind_max_L
         real(dp) :: Reimers_scaling_factor
         real(dp) :: Blocker_scaling_factor
         real(dp) :: AGB_wind_scaling_factor         
         real(dp) :: CSG_wind_scaling_factor
         
         namelist /other_winds/ &
            OB_wind_scheme, &
            CSG_wind_scheme, &
           Grafener_scaling_factor, &
            OB_scaling_factor, &
            hot_wind_min_T, &
            cool_wind_max_T, &
            WNL_wind_min_dg, &
            OB_wind_max_dg, &
            h_wind_min_h, &
            he_wind_max_h, &
            he_wind_max_Mdot, &
            he_wind_max_Gamm, &
            he_wind_qion_option, &
            CSG_wind_min_L, &
            AGB_wind_max_L, &
            Reimers_scaling_factor, &
            Blocker_scaling_factor, &
            AGB_wind_scaling_factor, &            
            CSG_wind_scaling_factor
            
      ! end of declarations for other_winds      
            
      ! these routines are called by the standard run_star check_model
      contains
      
      subroutine read_inlist_other_winds(ierr)
         integer, intent(out) :: ierr
         character (len=256) :: filename, message
         integer :: unit         
         filename = 'inlist_other_winds'
         write(*,*) 'read_inlist_other_winds'
         ! set defaults
         OB_wind_scheme = 'VS21'
         CSG_wind_scheme = 'de Jager'
         OB_scaling_factor = 1.0d0
         Grafener_scaling_factor = 1.0d0
         hot_wind_min_T = 10000
         cool_wind_max_T = 11000
         WNL_wind_min_dg = 0.08
         OB_wind_max_dg = 0.12
         h_wind_min_h = 0.35
         he_wind_max_h = 0.45
         he_wind_max_Mdot = 0.01
         he_wind_max_Gamm = 0.9
         he_wind_qion_option = 2
         CSG_wind_min_L = 4000
         AGB_wind_max_L = 55000
         Reimers_scaling_factor = 0.477
         Blocker_scaling_factor = 0.1
         AGB_wind_scaling_factor = 1.0d0           
         CSG_wind_scaling_factor = 1.0d0
         
         open(newunit=unit, file=trim(filename), action='read', delim='quote', iostat=ierr)
         if (ierr /= 0) then
            write(*, *) 'Failed to open control namelist file ', trim(filename)
         else
            read(unit, nml=other_winds, iostat=ierr)  
            close(unit)
            if (ierr /= 0) then
               write(*, *) 'Failed while trying to read control namelist file ', trim(filename)
               write(*, '(a)') &
                  'The following runtime error message might help you find the problem'
               write(*, *) 
               open(newunit=unit, file=trim(filename), action='read', delim='quote', status='old', iostat=ierr)
               read(unit, nml=other_winds)
               close(unit)
            end if  
         end if

      end subroutine read_inlist_other_winds

      subroutine other_wind(id, L, M, R, Tsurf, X, Y, Z, w, ierr)
         use star_def
         use chem_def, only: chem_isos
         integer, intent(in) :: id
         real(dp), intent(in) :: L, M, R, Tsurf, X, Y, Z ! surface values (cgs)
         ! NOTE: surface is outermost cell. not necessarily at photosphere.
         ! NOTE: don't assume that vars are set at this point.
         ! so if you want values other than those given as args,
         ! you should use values from s% xh(:,:) and s% xa(:,:) only.
         ! rather than things like s% Teff or s% lnT(:) which have not been set yet.
         real(dp), intent(out) :: w ! wind in units of Msun/year (value is >= 0)
         real(dp) :: wOB, wcool, wCSG, wAGB, wRGB, p0, vw, wAGBmax, wBlocker, wVW
         real(dp) :: wWNL, logMdot, gamma_edd, xsurf, beta, gammazero, lgZ, deltagamma         
         real(dp) :: fWNL, fh, fhot, whot, whoth, whothe
         real(dp) :: Xc, Yc, ZFe, Zi, wWR
         real(dp) :: mdotthermal
         integer :: i
         integer, intent(out) :: ierr
         type(star_info), pointer :: s

         w = 0
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         
         Xc = 0
         Yc = 0
         ZFe = 0
         do i=1,s% species
            Zi = chem_isos% Z(s% chem_id(i))
            if (Zi .eq. 1) then
               Xc = Xc + s% xa(s%net_iso(s% chem_id(i)),s% nz)
            else if (Zi .eq. 2) then
               Yc = Yc + s% xa(s%net_iso(s% chem_id(i)),s% nz)
            elseif (Zi .eq. 26) then
               ZFe = ZFe + s% xa(s%net_iso(s% chem_id(i)),1)
            end if
         end do  
                     
         if (X > h_wind_min_h .and. Tsurf > hot_wind_min_T) then
            xsurf = X
            gamma_edd = exp10(-4.813d0)*(1+xsurf)*(L/Lsun)*(Msun/M)
            lgZ = log10(ZFe/ZFeSolar)
            gammazero = 0.326d0 - 0.301d0*lgZ - 0.045d0*lgZ*lgZ
            deltagamma = gamma_edd - gammazero
         
            if (WNL_wind_min_dg > deltagamma) then
               wWNL = 0
            else
               beta = 1.727d0 + 0.250d0*lgZ
               logMdot = &
                  + 10.046d0 &
                  - 3.5d0*log10(Tsurf) &
                  + beta*log10(deltagamma) &
                  + 0.42d0*log10(L/Lsun) &
                  - 0.45d0*xsurf
               wWNL = exp10(logMdot)
               wWNL = wWNL * Grafener_scaling_factor
            end if
         
            if (deltagamma > OB_wind_max_dg) then
               wOB = 0
            else      
               if (OB_wind_scheme == 'VS21') then
                  call eval_Vink_wind(L, M, R, Tsurf, X, Y, ZFe, .false., wOB)
               elseif (OB_wind_scheme == 'V01') then
                  call eval_Vink_wind(L, M, R, Tsurf, X, Y, ZFe, .true., wOB)
               elseif (OB_wind_scheme == 'Bjorklund21') then
                  logMdot = -5.55 + 0.79*log10(ZFe/ZFeSolar) + (2.16 - 0.32*log10(ZFe/ZFeSolar))*log10(L/(1d6*Lsun))
                  wOB = exp10(logMdot)
               else
                  ierr = -1
               end if
               wOB = wOB * OB_scaling_factor
            end if
         
            if (deltagamma > OB_wind_max_dg) then
               whoth = wWNL
            elseif (WNL_wind_min_dg > deltagamma) then
               whoth = wOB
            else
               fWNL = (deltagamma - WNL_wind_min_dg) / (OB_wind_max_dg - WNL_wind_min_dg)
               whoth = (1.0 - fWNL) * wOB + fWNL * wWNL
            end if
         else
            whoth = 0
         end if
         
         if (he_wind_max_h > X .and. Tsurf > hot_wind_min_T) then       
         
            logMdot = -13.3d0 + 1.36d0 * log10(L/Lsun) + 0.61d0 * log10(ZFe/ZFeSolar)
            whothe = exp10(logMdot)
            
            call eval_Sander_wind(L, M, X, Y, ZFe, wWR)
            
            if (whothe < wWR .and. log10(L/Lsun) .gt. 4.5 .and. Tsurf .gt. 3d4) then
               whothe = wWR
               logMdot = log10(wWR)
            end if
         end if
         
         if (Tsurf > hot_wind_min_T) then
            if (X > he_wind_max_h) then
               whot = whoth
            elseif (h_wind_min_h > X) then
               whot = whothe
            else
               fh = (X - h_wind_min_h) / (he_wind_max_h - h_wind_min_h)
               whot = (1.0 - fh) * whothe + fh * whoth
            end if
         else
            whot = 0
         end if
         
         if (cool_wind_max_T > Tsurf) then
            wRGB = 4d-13*Reimers_scaling_factor*(L*R/M)/(Lsun*Rsun/Msun)
                     
            if (Xc < 0.01d0 .and. Yc < s% RGB_to_AGB_wind_switch .and. L < AGB_wind_max_L*Lsun) then
               p0 = -2.07 - 0.9*log10(M/Msun) + 1.940*log10(R/Rsun)
               p0 = exp10(p0)
               if (p0>2000) p0 = 2000
               wVW = -11.4 + 0.0125*p0
               wVW = exp10(wVW)
               vw = 1d5 * (-13.5 + 0.056*p0)
               if (vw > 15d5) vw = 15d5
               if (vw > 0) then
                  wAGBmax = (secyer/clight) * L / (vw*Msun)
                  if (wVW > wAGBmax) wVW = wAGBmax
               end if
               
               wBlocker = (4d-13*(L*R/M)/(Lsun*Rsun/Msun)) * Blocker_scaling_factor * &
                  4.83d-9 * pow(M/Msun,-2.1d0) * pow(L/Lsun,2.7d0)
                  
               if (wBlocker > wVW) then
                  wAGB = wBlocker
               else
                  wAGB = wVW
               end if               
            else
               wAGB = 0.0
            end if

            if (L > CSG_wind_min_L*Lsun) then                                
              if (CSG_wind_scheme == 'de Jager') then
                  logMdot = 1.769d0*log10(L/Lsun) - 1.676d0*log10(Tsurf) - 8.158d0
               else if (CSG_wind_scheme == 'Nieuwenhuijzen') then
                  logMdot = -14.02d0 + 1.24d0*log10(L/Lsun) + 0.16d0*log10(M/Msun) + 0.81d0*log10(R/Rsun)
               else if (CSG_wind_scheme == 'van Loon') then
                 logMdot = -5.65d0 + 1.05d0*log10(L/(1d4*Lsun)) - 6.3d0*log10(Tsurf/35d2)
               end if               
               wCSG = exp10(logMdot)
               wCSG = wCSG * CSG_wind_scaling_factor               
            else
               wCSG = 0            
            end if

            if (wRGB > wAGB .and. wRGB > wCSG) then
               wcool = wRGB
               logMdot = log10(wcool)
            elseif (wAGB > wCSG) then
               wcool = wAGB
               logMdot = log10(wcool)
            else
               wcool = wCSG
               logMdot = log10(wcool)
            end if
         else
            wcool = 0
         end if
         
         if (hot_wind_min_T > Tsurf) then
            w = wcool
         elseif (Tsurf > cool_wind_max_T) then
            w = whot
         else
            fhot = (Tsurf - hot_wind_min_T) / (cool_wind_max_T - hot_wind_min_T)
            w = (1.0 - fhot) * wcool + fhot * whot
         end if

         mdotthermal = (R*L/(0.75d0*standard_cgrav*M))*secyer/msun
         if (w > mdotthermal) then
            logMdot = log10(w)
            logMdot = log10(mdotthermal)
            w = mdotthermal
         end if
         
         s% xtra(ix_comp_wind) = w
                  
      end subroutine other_wind

      subroutine eval_Vink_wind(L, M, R, Tsurf, X, Y, ZFe, use2001, w)
         real(dp), intent(in) :: L, M, R, Tsurf, X, Y, ZFe
         logical, intent(in) :: use2001
         real(dp), intent(inout) :: w
         real(dp) :: vinf, Gamma_e, dZ, Z_rel, charrho, vesc 
         real(dp) :: ratio, Tjump1, Tjump2, logMdot, offset
        real(dp) :: logL5, logM30, lograt, logT40, logT20
         character (len=strlen) :: zone
         real(dp), parameter :: GGRAV = 6.67d-8 
         
         vinf = -1
         
         Gamma_e = 7.66d-5 * 0.325 * (L/Lsun) / (M/Msun)
         
         if (use2001) then
            dZ = 0.85
         else
            dZ = 0.42
         end if
         
         Z_rel = ZFe/ZFeSolar
         
         charrho = -14.94 + (3.1857 * Gamma_e) + (dZ * log10(Z_rel))
         ! Jump temperatures via Eqs. (15) from Vink et al. (2001) and (6) from Vink et al. (2000)
         Tjump1 = ( 61.2 + (2.59 * charrho) ) * 1000.
         Tjump2 = ( 100. + (6.0 * charrho) ) * 1000.
         
         if (Tjump1 < Tjump2) then
            w = 0
            return
         end if
         
         vesc = sqrt(2.0*GGRAV*M*(1-Gamma_e)/R)*1d-5
         ratio = vinf/vesc
         
         if (Tsurf < Tjump1) then
            if (Tsurf < Tjump2) then
               zone = 'cold'
               ratio = 0.7
            else
               zone = 'inter'
               ratio = 1.3
            end if
         else
            zone = 'hot'
            ratio = 2.6
         end if

         logL5  = log10(L/Lsun) - 5.
         logM30 = log10((M/Msun)/30.)
         lograt = log10(ratio/2.)
         logT40 = log10(Tsurf/40000)
         logT20 = log10(Tsurf/20000)
         
         if (zone == 'cold') then
            offset = -5.99
         elseif (zone == 'inter') then
            offset = -6.688
         else
            offset = -6.697
         end if
         
         if (zone == 'hot') then
            logMdot = offset + 2.194 * logL5 - 1.313 * logM30 &
               - 1.226 * lograt + 0.933 * logT40 - 10.92 * (logT40**2) + dZ * log10(Z_rel)
         else
            logMdot = offset + 2.210 * logL5 - 1.339 * logM30 &
               - 1.601 * lograt + 1.07 * logT20 + 0.85 * log10(Z_rel)            
         end if

         w = exp10(logMdot)
      
      end subroutine eval_Vink_wind
      
      subroutine eval_Sander_wind(L, M, X, Y, Zfe, w)
         real(dp), intent(in) :: L, M, X, Y, Zfe
         real(dp), intent(inout) :: w
         real(dp), parameter :: a = 2.932
         real(dp) :: lgZ, qion, Gamma_e, Gamma_eb, Gamma_r, c, logMdot_off, logw
         
         lgZ = log10(ZFe/ZFeSolar)
         if (he_wind_qion_option .eq. 1) then
            qion = (2-X)/(4-3*X)
         elseif (he_wind_qion_option .eq. 2) then
            qion = (4-3*X-2*Y)/(12-11*X-8*Y)
         else
            qion = 0.5            
         end if
         
         Gamma_e = (10**(-4.51))*qion*(L/Lsun)/(M/Msun)
         Gamma_eb = 0.244 - 0.324 * lgZ
         c = 9.15 - 0.44 * lgZ
         logMdot_off = -2.61 + 0.23 * lgZ
         
         if (Gamma_e > he_wind_max_Gamm) then         
            Gamma_e = he_wind_max_Gamm
         end if
         
         Gamma_r = Gamma_eb / Gamma_e
         
         logw = a * log10(-log10(1-Gamma_e)) - log10(2.0) * (Gamma_r**c) + logMdot_off
         
         w = exp10(logw)
         
         if (w > he_wind_max_Mdot) then
            w = he_wind_max_Mdot
         end if
         
      end subroutine eval_Sander_wind
      
      subroutine large_outer_D(id, ierr)
         integer, intent(in) :: id
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         real(dp) :: mdot, mmix, Dmix
         integer :: nz, k

         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return

         mdot = s% mstar_dot

         if (mdot .le. 0d0) return

         mmix = s% x_ctrl(1)*s% m(1)
         Dmix = s% x_ctrl(2)
         nz = s% nz

         do k=1,nz
            if (s% m(k) .lt. mmix) then
               exit
            end if
            if (s% D_mix(k) .lt. Dmix) then
               s% D_mix(k) = Dmix
               if (s% mixing_type(k) .eq. no_mixing) then
                  s% mixing_type(k) = anonymous_mixing
               end if
            end if
         end do

      end subroutine large_outer_D     
      
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

         s% other_wind => other_wind
         ! setup for other_winds
         call read_inlist_other_winds(ierr)
         s% other_D_mix => large_outer_D
                           
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
      
