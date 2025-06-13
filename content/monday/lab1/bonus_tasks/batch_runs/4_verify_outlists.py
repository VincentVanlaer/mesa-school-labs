#!/usr/bin/env python3
"""
verify_mesa_runs.py - Fixed version for verifying MESA runs against a CSV configuration file
"""

import os
import csv
import sys
import re
import glob
import argparse

def extract_parameters_from_inlist(inlist_file):
    """
    Extract key parameters from an inlist file with improved detection of commented parameters
    """
    params = {}
    
    # Read the inlist file
    try:
        with open(inlist_file, 'r') as f:
            content = f.read()
            
            # Extract initial mass
            mass_match = re.search(r'initial_mass\s*=\s*([0-9.]+)', content)
            if mass_match:
                params['initial_mass'] = mass_match.group(1)
            
            # Extract metallicity
            z_match = re.search(r'initial_z\s*=\s*([0-9.]+)', content)
            if z_match:
                params['initial_z'] = z_match.group(1)
            
            # Check for active (uncommented) overshoot parameters
            active_scheme = re.search(r'^\s*overshoot_scheme\s*\(\s*1\s*\)\s*=\s*\'([^\']+)\'', content, re.MULTILINE)
            active_f = re.search(r'^\s*overshoot_f\s*\(\s*1\s*\)\s*=\s*([0-9.]+)', content, re.MULTILINE)
            active_f0 = re.search(r'^\s*overshoot_f0\s*\(\s*1\s*\)\s*=\s*([0-9.]+)', content, re.MULTILINE)
            
            # Check for commented out overshoot parameters
            commented_scheme = re.search(r'^\s*!+\s*overshoot_scheme', content, re.MULTILINE)
            
            # Determine overshoot scheme
            if active_scheme:
                params['overshoot_scheme'] = active_scheme.group(1)
                if active_f:
                    params['overshoot_f'] = active_f.group(1)
                if active_f0:
                    params['overshoot_f0'] = active_f0.group(1)
            elif commented_scheme:
                params['overshoot_scheme'] = 'none'
            else:
                # If no overshoot parameters are found at all, assume none
                params['overshoot_scheme'] = 'none'
            
            # Extract save model filename
            save_model_match = re.search(r"save_model_filename\s*=\s*'([^']*)'", content)
            if save_model_match:
                params['save_model_filename'] = save_model_match.group(1)
    
    except Exception as e:
        print(f"Error reading inlist file {inlist_file}: {e}")
        return {}
    
    return params

def verify_runs(csv_file, runs_dir="batch_runs/runs"):
    """
    Verify that all runs in the runs directory match the expected configurations from the CSV file
    
    Parameters:
    csv_file (str): Path to the CSV file with parameter combinations
    runs_dir (str): Path to the directory containing run folders
    """
    # Get list of all run directories
    run_folders = [f for f in glob.glob(os.path.join(runs_dir, "*")) if os.path.isdir(f)]
    run_folder_names = [os.path.basename(f) for f in run_folders]
    
    print(f"Found {len(run_folders)} run folders in {runs_dir}")
    
    # Dictionaries to track verification status
    csv_entries = []
    matched_runs = []
    missing_runs = []
    mismatched_runs = []
    
    # Read CSV file
    with open(csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header row
        
        for row_num, row in enumerate(reader, 2):  # Start counting from 2 to account for header
            if len(row) < 6:
                print(f"Warning: Row {row_num} is missing data, skipping")
                continue
                
            name = row[0].strip()
            mass = row[1].strip()
            metallicity = row[2].strip()
            scheme = row[3].strip()
            fov = row[4].strip()
            f0 = row[5].strip()
            
            # Skip rows with missing data
            if not mass or not metallicity:
                print(f"Warning: Row {row_num} is missing mass or metallicity, skipping")
                continue
            
            # Normalize the scheme value to match folder naming
            scheme_lower = scheme.lower()
            
            # Determine expected run folder name (same as inlist name without .inp extension)
            if scheme_lower in ["no overshooting", "none", "no overshoot"]:
                expected_folder = f"inlist_M{mass}_Z{metallicity}_noovs"
                expected_scheme = "none"
            else:
                expected_folder = f"inlist_M{mass}_Z{metallicity}_{scheme}_fov{fov}_f0{f0}"
                expected_scheme = scheme_lower
            
            # Track the expected configuration
            expected_config = {
                'initial_mass': mass,
                'initial_z': metallicity,
                'overshoot_scheme': expected_scheme
            }
            
            if expected_scheme != "none":
                expected_config['overshoot_f'] = fov
                expected_config['overshoot_f0'] = f0
            
            csv_entries.append((row_num, expected_folder, expected_config))
            
            # Check if run folder exists
            if expected_folder in run_folder_names:
                # Verify the inlist file has the correct parameters
                inlist_file = os.path.join(runs_dir, expected_folder, "inlist_project")
                
                if os.path.exists(inlist_file):
                    # Extract parameters from the inlist file
                    actual_params = extract_parameters_from_inlist(inlist_file)
                    
                    # Compare with expected configuration
                    mismatch = False
                    mismatch_details = []
                    
                    # Special handling for overshoot scheme
                    if expected_scheme == "none":
                        # For "none", just check if the overshoot_scheme is indeed "none"
                        if actual_params.get('overshoot_scheme') != "none":
                            mismatch = True
                            mismatch_details.append(f"overshoot_scheme expected none, got {actual_params.get('overshoot_scheme')}")
                    else:
                        # For other schemes, check all overshoot parameters
                        for param, expected_value in expected_config.items():
                            if param not in actual_params:
                                mismatch = True
                                mismatch_details.append(f"{param} is missing")
                            elif actual_params[param].lower() != expected_value.lower():
                                mismatch = True
                                mismatch_details.append(f"{param} expected {expected_value}, got {actual_params[param]}")
                    
                    # Check mass and metallicity for all runs
                    for basic_param in ['initial_mass', 'initial_z']:
                        if basic_param not in actual_params:
                            mismatch = True
                            mismatch_details.append(f"{basic_param} is missing")
                        elif actual_params[basic_param] != expected_config[basic_param]:
                            mismatch = True
                            mismatch_details.append(f"{basic_param} expected {expected_config[basic_param]}, got {actual_params[basic_param]}")
                    
                    if mismatch:
                        mismatched_runs.append((row_num, expected_folder, mismatch_details))
                    else:
                        matched_runs.append((row_num, expected_folder))
                else:
                    mismatched_runs.append((row_num, expected_folder, ["inlist_project file is missing"]))
            else:
                missing_runs.append((row_num, expected_folder))
    
    # Report results
    print(f"\nVerification Summary:")
    print(f"  - Total CSV entries: {len(csv_entries)}")
    print(f"  - Matched runs: {len(matched_runs)}")
    print(f"  - Missing runs: {len(missing_runs)}")
    print(f"  - Mismatched runs: {len(mismatched_runs)}")
    
    if missing_runs:
        print("\nMissing runs (no corresponding run folder):")
        for row_num, folder in missing_runs:
            print(f"  - Row {row_num}: {folder}")
    
    if mismatched_runs:
        print("\nMismatched runs (parameters do not match CSV):")
        for row_num, folder, details in mismatched_runs:
            print(f"  - Row {row_num}: {folder}")
            for detail in details:
                print(f"    * {detail}")
    
    # Check for extra run folders not in the CSV
    expected_folders = [entry[1] for entry in csv_entries]
    extra_folders = [f for f in run_folder_names if f not in expected_folders]
    
    if extra_folders:
        print(f"\nFound {len(extra_folders)} extra run folders not specified in the CSV:")
        for folder in extra_folders:
            inlist_file = os.path.join(runs_dir, folder, "inlist_project")
            if os.path.exists(inlist_file):
                params = extract_parameters_from_inlist(inlist_file)
                param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
                print(f"  - {folder}: {param_str}")
            else:
                print(f"  - {folder}: No inlist_project file found")
    
    # Check for log files and model completion
    print("\nChecking run completion status...")
    completed_runs = 0
    incomplete_runs = 0
    failed_runs = 0
    
    for folder in run_folder_names:
        if folder in [entry[1] for entry in matched_runs]:
            log_file = os.path.join(runs_dir, folder, "run.log")
            if os.path.exists(log_file):
                # Check if the run completed successfully
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    if "termination code: xa_central_lower_limit" in log_content:
                        completed_runs += 1
                    elif "failed" in log_content.lower() or "error" in log_content.lower():
                        failed_runs += 1
                        print(f"  - {folder}: Run failed (check run.log for details)")
                    else:
                        incomplete_runs += 1
                        print(f"  - {folder}: Run may be incomplete (no termination code found)")
            else:
                print(f"  - {folder}: No run.log file found")
    
    print(f"\nRun Status Summary:")
    print(f"  - Completed runs: {completed_runs}")
    print(f"  - Incomplete runs: {incomplete_runs}")
    print(f"  - Failed runs: {failed_runs}")
    
    # Final assessment
    success = len(missing_runs) == 0 and len(mismatched_runs) == 0
    
    if success:
        print("\nAll MESA runs match the CSV configurations and have completed.")
    else:
        print("\nSome issues were found with the MESA runs. Please review the details above.")
        
        # If only missing runs but no mismatches, this is likely expected
        if len(mismatched_runs) == 0 and len(missing_runs) > 0:
            print("Note: The missing runs may be expected if not all models have been run yet.")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify MESA runs against a CSV configuration file")
    parser.add_argument("csv_file", help="Path to the CSV file with parameter combinations")
    parser.add_argument("--runs-dir", "-d", default="../runs", 
                        help="Path to the directory containing run folders (default: runs)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file '{args.csv_file}' not found")
        sys.exit(1)
        
    if not os.path.exists(args.runs_dir):
        print(f"Error: Runs directory '{args.runs_dir}' not found")
        sys.exit(1)
    
    success = verify_runs(args.csv_file, args.runs_dir)
    sys.exit(0 if success else 1)