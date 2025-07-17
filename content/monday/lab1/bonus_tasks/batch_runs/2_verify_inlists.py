#!/usr/bin/env python3
"""
verify_inlists.py - Thoroughly verifies that all inlist files are correctly formatted
and contain all required parameters with expected values
"""

import os
import csv
import sys
import glob
import re
from collections import defaultdict

def extract_parameters(inlist_file):
    """Extract all key parameters from an inlist file with improved detection"""
    params = {}
    
    # Read the inlist file
    try:
        with open(inlist_file, 'r') as f:
            content = f.read()
            
            # Check for essential sections
            sections = {
                'star_job': re.search(r'&star_job.*?/', content, re.DOTALL) is not None,
                'controls': re.search(r'&controls.*?/', content, re.DOTALL) is not None,
                'kap': re.search(r'&kap.*?/', content, re.DOTALL) is not None,
            }
            params['sections'] = sections
            
            # Extract key parameters
            # Initial mass
            mass_match = re.search(r'initial_mass\s*=\s*([0-9.eEdD+-]+)', content)
            params['initial_mass'] = mass_match.group(1) if mass_match else None
            
            # Initial metallicity
            z_match = re.search(r'initial_z\s*=\s*([0-9.eEdD+-]+)', content)
            params['initial_z'] = z_match.group(1) if z_match else None
            
            # Zbase
            zbase_match = re.search(r'Zbase\s*=\s*([0-9.eEdD+-]+)', content)
            params['Zbase'] = zbase_match.group(1) if zbase_match else None
            
            # pgstar flag
            pgstar_match = re.search(r'pgstar_flag\s*=\s*\.([a-z]+)\.', content)
            params['pgstar_flag'] = pgstar_match.group(1) if pgstar_match else None
            
            # save model options
            save_model_match = re.search(r'save_model_when_terminate\s*=\s*\.([a-z]+)\.', content)
            params['save_model_when_terminate'] = save_model_match.group(1) if save_model_match else None
            
            save_model_filename_match = re.search(r"save_model_filename\s*=\s*'([^']*)'", content)
            params['save_model_filename'] = save_model_filename_match.group(1) if save_model_filename_match else None
            
            # Overshooting parameters
            # First check if they are commented out
            commented_overshoot = re.search(r'^\s*!+\s*overshoot_scheme', content, re.MULTILINE)
            params['overshoot_commented'] = commented_overshoot is not None
            
            # Check for active overshoot parameters
            scheme_match = re.search(r'^\s*overshoot_scheme\s*\(\s*1\s*\)\s*=\s*\'([^\']+)\'', content, re.MULTILINE)
            params['overshoot_scheme'] = scheme_match.group(1) if scheme_match else None
            
            zone_type_match = re.search(r'^\s*overshoot_zone_type\s*\(\s*1\s*\)\s*=\s*\'([^\']+)\'', content, re.MULTILINE)
            params['overshoot_zone_type'] = zone_type_match.group(1) if zone_type_match else None
            
            zone_loc_match = re.search(r'^\s*overshoot_zone_loc\s*\(\s*1\s*\)\s*=\s*\'([^\']+)\'', content, re.MULTILINE)
            params['overshoot_zone_loc'] = zone_loc_match.group(1) if zone_loc_match else None
            
            bdy_loc_match = re.search(r'^\s*overshoot_bdy_loc\s*\(\s*1\s*\)\s*=\s*\'([^\']+)\'', content, re.MULTILINE)
            params['overshoot_bdy_loc'] = bdy_loc_match.group(1) if bdy_loc_match else None
            
            f_match = re.search(r'^\s*overshoot_f\s*\(\s*1\s*\)\s*=\s*([0-9.eEdD+-]+)', content, re.MULTILINE)
            params['overshoot_f'] = f_match.group(1) if f_match else None
            
            f0_match = re.search(r'^\s*overshoot_f0\s*\(\s*1\s*\)\s*=\s*([0-9.eEdD+-]+)', content, re.MULTILINE)
            params['overshoot_f0'] = f0_match.group(1) if f0_match else None
            
            # Check for Ledoux criterion setting
            ledoux_match = re.search(r'use_Ledoux_criterion\s*=\s*\.([a-z]+)\.', content)
            params['use_Ledoux_criterion'] = ledoux_match.group(1) if ledoux_match else None
            
            # Check for stop condition
            stop_central_h1_match = re.search(r'xa_central_lower_limit_species\s*\(\s*1\s*\)\s*=\s*\'([^\']+)\'', content, re.MULTILINE)
            params['stop_condition_species'] = stop_central_h1_match.group(1) if stop_central_h1_match else None
            
            h1_limit_match = re.search(r'xa_central_lower_limit\s*\(\s*1\s*\)\s*=\s*([0-9.eEdD+-]+)', content)
            params['h1_limit'] = h1_limit_match.group(1) if h1_limit_match else None
            
            # Check for history & profile columns files
            history_columns_match = re.search(r'history_columns_file\s*=\s*\'([^\']+)\'', content)
            params['history_columns_file'] = history_columns_match.group(1) if history_columns_match else None
            
            profile_columns_match = re.search(r'profile_columns_file\s*=\s*\'([^\']+)\'', content)
            params['profile_columns_file'] = profile_columns_match.group(1) if profile_columns_match else None
            
    except Exception as e:
        print(f"Error reading inlist file {inlist_file}: {e}")
        return {}
    
    return params

def verify_inlists(csv_file, inlist_dir="batch_inlists"):
    """
    Verify that all entries in the CSV file have corresponding inlist files
    and that inlists contain all required parameters with correct values
    
    Parameters:
    csv_file (str): Path to the CSV file with parameter combinations
    inlist_dir (str): Path to the directory containing inlist files
    """
    # Get list of all inlist files
    inlist_files = glob.glob(os.path.join(inlist_dir, "*.inp"))
    inlist_basenames = [os.path.basename(f) for f in inlist_files]
    
    print(f"Found {len(inlist_files)} inlist files in {inlist_dir}")
    
    # Dictionary to track which CSV entries have matching inlist files
    csv_entries = []
    matched_entries = []
    missing_entries = []
    
    # Dictionary to track verification status for each inlist
    verification_results = {}
    
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
            scheme = row[3].strip().lower()
            fov = row[4].strip()
            f0 = row[5].strip()
            
            # Skip rows with missing data
            if not mass or not metallicity:
                print(f"Warning: Row {row_num} is missing mass or metallicity, skipping")
                continue
            
            # Determine expected filename
            if scheme in ["no overshooting", "none", "no overshoot"]:
                expected_file = f"inlist_M{mass}_Z{metallicity}_noovs.inp"
                expected_scheme = "none"
            else:
                expected_file = f"inlist_M{mass}_Z{metallicity}_{scheme}_fov{fov}_f0{f0}.inp"
                expected_scheme = scheme
            
            expected_params = {
                'initial_mass': mass,
                'initial_z': metallicity,
                'Zbase': metallicity,
                'overshoot_scheme': None if expected_scheme == "none" else expected_scheme,
                'overshoot_commented': expected_scheme == "none",
                'overshoot_f': "0" if expected_scheme == "none" else fov,
                'overshoot_f0': "0" if expected_scheme == "none" else f0,
            }
            
            csv_entries.append((row_num, expected_file, expected_params))
            
            # Check if file exists
            if expected_file in inlist_basenames:
                matched_entries.append((row_num, expected_file))
                inlist_path = os.path.join(inlist_dir, expected_file)
                # Verify the inlist parameters
                actual_params = extract_parameters(inlist_path)
                verification_results[expected_file] = {
                    'expected': expected_params,
                    'actual': actual_params,
                    'status': 'verifying',
                    'issues': []
                }
            else:
                missing_entries.append((row_num, expected_file))
    
    # Report file existence results
    print(f"\nFile Existence Summary:")
    print(f"  - Total CSV entries: {len(csv_entries)}")
    print(f"  - Matched inlist files: {len(matched_entries)}")
    print(f"  - Missing inlist files: {len(missing_entries)}")
    
    if missing_entries:
        print("\nMissing inlist files:")
        for row_num, filename in missing_entries:
            print(f"  - Row {row_num}: {filename}")
    
    # Check for extra inlist files not in the CSV
    expected_files = [entry[1] for entry in csv_entries]
    extra_files = [f for f in inlist_basenames if f not in expected_files]
    
    if extra_files:
        print(f"\nFound {len(extra_files)} extra inlist files not in the CSV:")
        for filename in extra_files:
            print(f"  - {filename}")
    
    # Verify parameters for each matched inlist
    print("\nVerifying inlist parameters...")
    
    verified_count = 0
    issue_count = 0
    
    for expected_file, result in verification_results.items():
        expected = result['expected']
        actual = result['actual']
        issues = []
        
        # Check for required sections
        if 'sections' in actual:
            if not actual['sections'].get('star_job', False):
                issues.append("Missing &star_job section")
            if not actual['sections'].get('controls', False):
                issues.append("Missing &controls section")
            if not actual['sections'].get('kap', False):
                issues.append("Missing &kap section")
        
        # Check for essential parameters
        if actual.get('initial_mass') is None:
            issues.append("Missing initial_mass parameter")
        elif not compare_numeric_values(actual['initial_mass'], expected['initial_mass']):
            issues.append(f"initial_mass mismatch: expected {expected['initial_mass']}, got {actual['initial_mass']}")
        
        if actual.get('initial_z') is None:
            issues.append("Missing initial_z parameter")
        elif not compare_numeric_values(actual['initial_z'], expected['initial_z']):
            issues.append(f"initial_z mismatch: expected {expected['initial_z']}, got {actual['initial_z']}")
        
        if actual.get('Zbase') is None:
            issues.append("Missing Zbase parameter")
        elif not compare_numeric_values(actual['Zbase'], expected['initial_z']):
            issues.append(f"Zbase mismatch: expected {expected['initial_z']}, got {actual['Zbase']}")
        
        # Check for model saving parameters
        if actual.get('save_model_when_terminate') is None:
            issues.append("Missing save_model_when_terminate parameter")
        elif actual['save_model_when_terminate'].lower() != 'true':
            issues.append(f"save_model_when_terminate should be '.true.', got '.{actual['save_model_when_terminate']}.'")
        
        if actual.get('save_model_filename') is None:
            issues.append("Missing save_model_filename parameter")
        elif not actual['save_model_filename'].endswith('.mod'):
            issues.append(f"save_model_filename should end with '.mod', got '{actual['save_model_filename']}'")
        
        # Check stopping condition
        if actual.get('stop_condition_species') is None:
            issues.append("Missing xa_central_lower_limit_species parameter")
        elif actual['stop_condition_species'] != 'h1':
            issues.append(f"stop_condition_species should be 'h1', got '{actual['stop_condition_species']}'")
        
        if actual.get('h1_limit') is None:
            issues.append("Missing xa_central_lower_limit parameter")
        
        # Check for history and profile column files
        if actual.get('history_columns_file') is None:
            issues.append("Missing history_columns_file parameter")
        
        if actual.get('profile_columns_file') is None:
            issues.append("Missing profile_columns_file parameter")
        
        # Check overshooting parameters
        if expected['overshoot_scheme'] is None:
            # Should have commented out overshoot
            if not actual.get('overshoot_commented', False) and actual.get('overshoot_scheme') is not None:
                issues.append("Overshoot should be disabled/commented out but isn't")
        else:
            # Should have active overshoot
            if actual.get('overshoot_scheme') is None:
                issues.append(f"Missing or commented out overshoot_scheme parameter")
            elif actual['overshoot_scheme'].lower() != expected['overshoot_scheme'].lower():
                issues.append(f"overshoot_scheme mismatch: expected '{expected['overshoot_scheme']}', got '{actual['overshoot_scheme']}'")
            
            if actual.get('overshoot_zone_type') is None:
                issues.append("Missing overshoot_zone_type parameter")
            elif actual['overshoot_zone_type'] not in ['any', 'burn_H', 'nonburn']:
                issues.append(f"Invalid overshoot_zone_type: '{actual['overshoot_zone_type']}'")
            
            if actual.get('overshoot_zone_loc') is None:
                issues.append("Missing overshoot_zone_loc parameter")
            elif actual['overshoot_zone_loc'] != 'core':
                issues.append(f"overshoot_zone_loc should be 'core', got '{actual['overshoot_zone_loc']}'")
            
            if actual.get('overshoot_bdy_loc') is None:
                issues.append("Missing overshoot_bdy_loc parameter")
            elif actual['overshoot_bdy_loc'] != 'top':
                issues.append(f"overshoot_bdy_loc should be 'top', got '{actual['overshoot_bdy_loc']}'")
            
            if actual.get('overshoot_f') is None:
                issues.append("Missing overshoot_f parameter")
            elif not compare_numeric_values(actual['overshoot_f'], expected['overshoot_f']):
                issues.append(f"overshoot_f mismatch: expected {expected['overshoot_f']}, got {actual['overshoot_f']}")
            
            if actual.get('overshoot_f0') is None:
                issues.append("Missing overshoot_f0 parameter")
            elif not compare_numeric_values(actual['overshoot_f0'], expected['overshoot_f0']):
                issues.append(f"overshoot_f0 mismatch: expected {expected['overshoot_f0']}, got {actual['overshoot_f0']}")
        
        # Store issues and update status
        result['issues'] = issues
        if issues:
            result['status'] = 'issues'
            issue_count += 1
        else:
            result['status'] = 'verified'
            verified_count += 1
    
    # Print verification results
    print(f"\nParameter Verification Summary:")
    print(f"  - Total inlists verified: {len(verification_results)}")
    print(f"  - Inlists without issues: {verified_count}")
    print(f"  - Inlists with issues: {issue_count}")
    
    if issue_count > 0:
        print("\nInlists with issues:")
        for filename, result in verification_results.items():
            if result['status'] == 'issues':
                print(f"\n  {filename}:")
                for issue in result['issues']:
                    print(f"    - {issue}")
    
    return issue_count == 0

def compare_numeric_values(val1, val2, tolerance=1e-6):
    """Compare numeric values with tolerance for scientific notation and formatting differences"""
    try:
        # Handle scientific notation and convert to float
        if isinstance(val1, str):
            # Replace 'd' or 'D' with 'e' for scientific notation in Fortran
            val1 = val1.lower().replace('d', 'e')
        if isinstance(val2, str):
            val2 = val2.lower().replace('d', 'e')
        
        float1 = float(val1)
        float2 = float(val2)
        
        # Check if values are close enough
        if abs(float1 - float2) <= tolerance * max(abs(float1), abs(float2)):
            return True
        
        # Special case for very small values
        if abs(float1) < tolerance and abs(float2) < tolerance:
            return True
        
        return False
    except:
        # If conversion fails, fall back to string comparison
        return str(val1).strip() == str(val2).strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <csv_file> [inlist_dir]")
        sys.exit(1)
        
    csv_file = sys.argv[1]
    inlist_dir = sys.argv[2] if len(sys.argv) > 2 else "../batch_inlists"
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        sys.exit(1)
        
    if not os.path.exists(inlist_dir):
        print(f"Error: Inlist directory '{inlist_dir}' not found")
        sys.exit(1)
    
    success = verify_inlists(csv_file, inlist_dir)
    sys.exit(0 if success else 1)