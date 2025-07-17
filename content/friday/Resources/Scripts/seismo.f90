      function integrate_r_(x, y, mask) result(int_y)
          ! as implemented in GYRE utils
          real(dp), intent(in) :: x(:)
          real(dp), intent(in) :: y(:)
          logical, optional, intent(in) :: mask(:)
          real(dp) :: int_y
          integer :: n

          n = size(x)

          if (present(mask)) then
              int_y = sum((y(2:) + y(:n-1)) * (x(2:) - x(:n-1)), mask=mask(2:) .and. mask(:n-1)) / 2
          else
              int_y = sum((y(2:) + y(:n-1)) * (x(2:) - x(:n-1))) / 2
          endif

          return
      end function integrate_r_

      integer function extras_check_model(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s

         real(dp) :: delta_nu, discr !γπ discriminant

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

         if (s% x_integer_ctrl(1) > 0 .and. s% phase_of_evolution >= s% x_integer_ctrl(1)) then
                 extras_check_model = terminate
                 write (*, *) 'have reached desired phase_of_evolution'
                 return
         end if

         ! if (s% x_ctrl(1) > 1 .and. s% delta_Pg > 0) then
         !         delta_nu = 1/(2*s% photosphere_acoustic_r) !Hz
         !         write(*,*) delta_nu * 1d6
         !         write(*,*) s% delta_Pg !seconds
         !         write(*,*) s% nu_max
         !         discr = s% delta_Pg * (s% nu_max / 1d6) ** 2 / delta_nu
         !         write(*,*) discr
         !         if (1/discr > s% x_ctrl(1)) then
         !                 extras_check_model = terminate
         !                 return
         !         end if
         ! end if

         if (s% x_logical_ctrl(1)) then
            ! custom stopping condition: stop when ΔΠ corresponds to a frequency spacing
            ! of f * νmax. In this case f = 2.

            discr = s% delta_Pg * s% nu_max / 1d6
            if (discr > 0 .and. discr < 2d0) then
               extras_check_model = terminate
               return
            end if 
         end if

         if ( s% x_ctrl(1) > 0 ) then
            ! stopping condition for Δν as set by x_ctrl(1) in controls namelist
            ! I think this has been superseded in newer version of MESA though
            delta_nu = 1/(2*s% photosphere_acoustic_r) * 1d6 ! μHz
            if (delta_nu < s% x_ctrl(1)) then
               extras_check_model = terminate
               return
            end if
         end if

      end function extras_check_model

      integer function how_many_extra_history_columns(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0 
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         how_many_extra_history_columns = 2
      end function how_many_extra_history_columns
    
      subroutine data_for_extra_history_columns(id, n, names, vals, ierr)
         integer, intent(in) :: id, n
         character (len=maxlen_history_column_name) :: names(n)
         real(dp) :: vals(n)
         integer, intent(out) :: ierr
         type (star_info), pointer :: s

         integer :: nz
         logical, allocatable :: mask(:)

         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return

         nz = s% nz
        
         names(1) = 'delta_omega_p'
         vals(1) = integrate_r_(s% r(1:nz), s% omega(1:nz)/(s% csound(1:nz))) / integrate_r_(s% r(1:nz), 1/(s% csound(1:nz)))

         allocate(mask(nz))

         mask = (s% brunt_N2(1:nz) > 1d-10) .and. (s% x(1:nz) < .95)

         names(2) = 'delta_omega_g'
         vals(2) = 0.5 * integrate_r_(s% r(1:nz), s% omega(1:nz) * sqrt(s% brunt_N2(1:nz))/(s% r(1:nz)), mask=mask) / integrate_r_(s% r(1:nz), sqrt(s% brunt_N2(1:nz))/(s% r(1:nz)), mask=mask)

         deallocate(mask)

      end subroutine data_for_extra_history_columns
