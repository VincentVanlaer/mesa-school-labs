#!/usr/bin/env python3
"""
make_batch.py - Python script to create batch inlists from a CSV file of parameters.
Fixed version with improved robustness matching the behavior of make_batch.sh
"""

import os
import csv
import re
import shutil
import sys

def create_batch_inlists(csv_file):
    """Create batch inlists from parameters in CSV file"""
    # Define paths
    batch_dir = "../batch_inlists"
    template_inlist = os.path.join("../..", "inlist_project")
    
    # Create batch directory if it doesn't exist
    os.makedirs(batch_dir, exist_ok=True)
    
    # Ask user about pgstar settings
    enable_pgstar = input("Do you want to enable pgstar for batch runs? (yes/no): ").lower()
    pgstar_setting = "pgstar_flag = .true." if enable_pgstar.startswith('y') else "pgstar_flag = .false."
    
    # Read CSV file, skipping header
    with open(csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        
        for row in reader:
            # Unpack row or skip if too short
            if len(row) < 6:
                continue
                
            name = row[0].strip()
            mass = row[1].strip()
            metallicity = row[2].strip()
            scheme = row[3].strip()
            fov = row[4].strip()
            f0 = row[5].strip()
            
            # Skip rows with missing data
            if not mass or not metallicity:
                continue
            
            # Create descriptive filename encoding the parameters
            # Convert mass to integer for filename
            mass_int = int(float(mass))
            
            if scheme.lower() in ["no overshooting", "none", "no overshoot"]:
                outfile = os.path.join(batch_dir, f"inlist_M{mass_int}_Z{metallicity}_noovs.inp")
                ovs_option = "none"
            else:
                outfile = os.path.join(batch_dir, f"inlist_M{mass_int}_Z{metallicity}_{scheme}_fov{fov}_f0{f0}.inp")
                ovs_option = scheme
            
            print(f"Creating {outfile}...")
            
            # Copy template
            shutil.copy(template_inlist, outfile)
            
            # Read template content
            with open(outfile, 'r') as f:
                content = f.read()
            
            # Update initial_mass - ensure proper format including scientific notation
            if re.search(r'initial_mass\s*=', content):
                content = re.sub(r'initial_mass\s*=\s*[0-9]*(\.[0-9]*)?([dD]?[eE][-+]?[0-9]*)?', f'initial_mass = {mass}', content)
            else:
                # Add it to the starting specifications section if it exists
                if '! starting specifications' in content:
                    content = re.sub(r'! starting specifications\n', f'! starting specifications\n    initial_mass = {mass} ! in Msun units\n', content)
                else:
                    # Otherwise add it at the beginning of the &controls section
                    content = re.sub(r'&controls', f'&controls\n\n    ! starting specifications\n    initial_mass = {mass} ! in Msun units', content)
            
            # For initial_z - ensure proper format including scientific notation
            if re.search(r'initial_z\s*=', content):
                content = re.sub(r'initial_z\s*=\s*[0-9]*(\.[0-9]*)?([dD]?[eE][-+]?[0-9]*)?', f'initial_z = {metallicity}', content)
            else:
                # Add it after initial_mass if it exists
                if re.search(r'initial_mass\s*=', content):
                    content = re.sub(r'(initial_mass\s*=.+)', f'\\1\n    initial_z = {metallicity} ! initial metal mass fraction', content)
                else:
                    # Otherwise add it at the beginning of the &controls section
                    content = re.sub(r'&controls', f'&controls\n\n    ! starting specifications\n    initial_z = {metallicity} ! initial metal mass fraction', content)
            
            # For Zbase in the &kap section
            if re.search(r'Zbase\s*=', content):
                content = re.sub(r'Zbase\s*=\s*[0-9]*(\.[0-9]*)?([dD]?[eE][-+]?[0-9]*)?', f'Zbase = {metallicity}', content)
            else:
                # Add it to the &kap section if it exists
                if '&kap' in content:
                    content = re.sub(r'&kap\n', f'&kap\n    Zbase = {metallicity}\n', content)
                else:
                    # Otherwise add a new &kap section before &controls
                    content = re.sub(r'&controls', f'&kap\n    ! kap options\n    Zbase = {metallicity}\n/ ! end of kap namelist\n\n&controls', content)
            
            # For pgstar_flag
            if re.search(r'pgstar_flag\s*=\s*\.', content):
                content = re.sub(r'pgstar_flag\s*=\s*\.(true|false)\.', pgstar_setting, content)
            else:
                # Add it to the &star_job section if it exists
                if '&star_job' in content:
                    content = re.sub(r'&star_job\n', f'&star_job\n    {pgstar_setting}\n', content)
                else:
                    # Otherwise add a new &star_job section at the beginning of the file
                    content = f'&star_job\n    {pgstar_setting}\n/ ! end of star_job namelist\n\n' + content
            
            # Handle save_model_filename
            model_filename = f"M{mass_int}_Z{metallicity}"
            if ovs_option != "none":
                model_filename = f"{model_filename}_{scheme}_fov{fov}_f0{f0}"
            else:
                model_filename = f"{model_filename}_noovs"
                
            if re.search(r'save_model_filename\s*=', content):
                content = re.sub(r"save_model_filename\s*=\s*'.*'", f"save_model_filename = '{model_filename}.mod'", content)
            else:
                # Add save model options to &star_job
                if re.search(r'save_model_when_terminate\s*=', content):
                    content = re.sub(r'(save_model_when_terminate\s*=\s*\.[a-z]+\.)', f'\\1\n    save_model_filename = \'{model_filename}.mod\'', content)
                else:
                    save_model_options = f"    save_model_when_terminate = .true.\n    save_photo_when_terminate = .true.\n    save_model_filename = '{model_filename}.mod'"
                    if '&star_job' in content:
                        content = re.sub(r'(&star_job\n)', f'\\1{save_model_options}\n', content)
                    else:
                        # Otherwise add a new &star_job section at the beginning of the file
                        content = f'&star_job\n{save_model_options}\n/ ! end of star_job namelist\n\n' + content
            
            # Handle overshoot parameters
            if ovs_option == "none":
                # Comment out all overshoot lines
                content = re.sub(r'^(\s*overshoot_scheme)', r'!\1', content, flags=re.MULTILINE)
                content = re.sub(r'^(\s*overshoot_zone_type)', r'!\1', content, flags=re.MULTILINE)
                content = re.sub(r'^(\s*overshoot_zone_loc)', r'!\1', content, flags=re.MULTILINE)
                content = re.sub(r'^(\s*overshoot_bdy_loc)', r'!\1', content, flags=re.MULTILINE)
                content = re.sub(r'^(\s*overshoot_f\()', r'!\1', content, flags=re.MULTILINE)
                content = re.sub(r'^(\s*overshoot_f0\()', r'!\1', content, flags=re.MULTILINE)
            else:
                # Check if overshoot parameters already exist
                if re.search(r'overshoot_scheme\(1\)', content) or re.search(r'!\s*overshoot_scheme\(1\)', content):
                    # Uncomment and update existing parameters
                    content = re.sub(r'!\s*overshoot_scheme\(1\)\s*=\s*.*', f'     overshoot_scheme(1) = \'{scheme}\'', content)
                    content = re.sub(r'!\s*overshoot_zone_type\(1\)\s*=\s*.*', f'     overshoot_zone_type(1) = \'any\'', content)
                    content = re.sub(r'!\s*overshoot_zone_loc\(1\)\s*=\s*.*', f'     overshoot_zone_loc(1) = \'core\'', content)
                    content = re.sub(r'!\s*overshoot_bdy_loc\(1\)\s*=\s*.*', f'     overshoot_bdy_loc(1) = \'top\'', content)
                    content = re.sub(r'!\s*overshoot_f\(1\)\s*=\s*.*', f'     overshoot_f(1) = {fov}d0', content)
                    content = re.sub(r'!\s*overshoot_f0\(1\)\s*=\s*.*', f'     overshoot_f0(1) = {f0}d0', content)
                    
                    # Also handle active parameters (not commented)
                    content = re.sub(r'overshoot_scheme\(1\)\s*=\s*.*', f'     overshoot_scheme(1) = \'{scheme}\'', content)
                    content = re.sub(r'overshoot_zone_type\(1\)\s*=\s*.*', f'     overshoot_zone_type(1) = \'any\'', content)
                    content = re.sub(r'overshoot_zone_loc\(1\)\s*=\s*.*', f'     overshoot_zone_loc(1) = \'core\'', content)
                    content = re.sub(r'overshoot_bdy_loc\(1\)\s*=\s*.*', f'     overshoot_bdy_loc(1) = \'top\'', content)
                    content = re.sub(r'overshoot_f\(1\)\s*=\s*.*', f'     overshoot_f(1) = {fov}d0', content)
                    content = re.sub(r'overshoot_f0\(1\)\s*=\s*.*', f'     overshoot_f0(1) = {f0}d0', content)
                else:
                    # Add new overshoot parameters
                    overshoot_section = f"""
     overshoot_scheme(1) = '{scheme}'
     overshoot_zone_type(1) = 'any'
     overshoot_zone_loc(1) = 'core'
     overshoot_bdy_loc(1) = 'top'
     overshoot_f(1) = {fov}d0
     overshoot_f0(1) = {f0}d0
"""
                    # Check if there's a mixing section
                    if '! mixing' in content:
                        content = re.sub(r'! mixing\n', f'! mixing\n{overshoot_section}', content)
                    else:
                        # Find a good place to add it
                        if '! timesteps' in content:
                            content = re.sub(r'! timesteps', f'! mixing\n{overshoot_section}\n\n  ! timesteps', content)
                        elif '! mesh' in content:
                            content = re.sub(r'! mesh', f'! mixing\n{overshoot_section}\n\n  ! mesh', content)
                        elif '! solver' in content:
                            content = re.sub(r'! solver', f'! mixing\n{overshoot_section}\n\n  ! solver', content)
                        else:
                            # Add before end of controls
                            content = re.sub(r'/ ! end of controls namelist', f'  ! mixing\n{overshoot_section}\n\n/ ! end of controls namelist', content)
            
            # Add history and profile columns files if not present
            if not re.search(r'history_columns_file\s*=', content):
                if '&star_job' in content:
                    content = re.sub(r'(&star_job\n.*)', r'\1    history_columns_file = \'my_history_columns.list\'\n', content)
            
            if not re.search(r'profile_columns_file\s*=', content):
                if '&star_job' in content and 'history_columns_file' in content:
                    content = re.sub(r'(history_columns_file\s*=.*)', r'\1    profile_columns_file = \'my_profile_columns.list\'\n', content)
                elif '&star_job' in content:
                    content = re.sub(r'(&star_job\n.*)', r'\1    profile_columns_file = \'my_profile_columns.list\'\n', content)
            
            # Make sure Ledoux criterion is set
            if not re.search(r'use_Ledoux_criterion\s*=', content):
                if '! mixing' in content:
                    content = re.sub(r'(! mixing.*)', r'\1\n     use_Ledoux_criterion = .true.', content)
            else:
                content = re.sub(r'use_Ledoux_criterion\s*=\s*\..*\.', r'use_Ledoux_criterion = .true.', content)
            
            # Ensure stopping condition is properly set
            if not re.search(r'xa_central_lower_limit_species', content):
                if '! when to stop' in content:
                    stop_condition = """
    ! stop when the center mass fraction of h1 drops below this limit
    xa_central_lower_limit_species(1) = 'h1'
    xa_central_lower_limit(1) = 1d-3
"""
                    content = re.sub(r'! when to stop\n', f'! when to stop\n{stop_condition}', content)
                else:
                    # Add stopping condition section
                    if '&controls' in content:
                        content = re.sub(r'&controls\n', f'&controls\n\n  ! when to stop\n    xa_central_lower_limit_species(1) = \'h1\'\n    xa_central_lower_limit(1) = 1d-3\n\n', content)
            
            # Write updated content
            with open(outfile, 'w') as f:
                f.write(content)
    
    print("Batch inlist creation completed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <csv_file>")
        sys.exit(1)
        
    csv_file = sys.argv[1]
    create_batch_inlists(csv_file)
