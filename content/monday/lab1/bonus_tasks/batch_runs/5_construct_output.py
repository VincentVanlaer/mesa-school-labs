import os
import csv
import glob
import re
import numpy as np
from mesa_reader import MesaData

def parse_run_name(run_name):
    parts = run_name[7:].split("_")
    mass = float(parts[0][1:])
    z = float(parts[1][1:])
    if "noovs" in run_name:
        scheme = "none"
        fov = 0.0
        f0 = 0.0
    else:
        scheme = parts[2]
        fov = float(parts[3][3:]) if len(parts) > 3 and parts[3].startswith("fov") else 0.0
        f0 = float(parts[4][2:]) if len(parts) > 4 and parts[4].startswith("f0") else 0.0
    return mass, z, scheme, fov, f0

def find_tams_index(history, h1_limit=0.001):
    """Find the model index closest to TAMS based on central H depletion."""
    if not hasattr(history, 'center_h1'):
        return -1  # Return last index if center_h1 not available
    
    # Find where center_h1 drops below the limit (TAMS definition)
    tams_indices = np.where(history.center_h1 <= h1_limit)[0]
    if len(tams_indices) > 0:
        return tams_indices[0]  # Return first index where condition is met
    return -1  # Return last index if condition never met

def extract_tams_values(history):
    """Return values at TAMS."""
    tams_idx = find_tams_index(history)
    
    # If TAMS not found, use the last point -- this is what it should be anyway if your stopping conditions are correct
    if tams_idx == -1:
        tams_idx = -1
    
    age_myr = history.star_age[tams_idx] / 1e6
    log_Teff = history.log_Teff[tams_idx]
    log_L = history.log_L[tams_idx]
    
    # Get core mass if available
    he_core_mass = 0.0
    if hasattr(history, 'he_core_mass'):
        he_core_mass = history.he_core_mass[tams_idx]
    
    return age_myr, log_Teff, log_L, he_core_mass, tams_idx

def extract_core_radius(history, tams_idx):
    """Return convective core radius at TAMS if available."""
    if hasattr(history, 'conv_mx1_top_r'):
        return history.conv_mx1_top_r[tams_idx]
    return "NA"

def load_runtime_data(timings_file="run_timings.csv"):
    """Load runtime data from the CSV file created by batch runners."""
    runtimes = {}
    if not os.path.exists(timings_file):
        print(f"Warning: Timing file {timings_file} not found. Runtime data will not be included.")
        return runtimes
    
    try:
        with open(timings_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                inlist_name = row.get('inlist_name', '')
                runtime_seconds = row.get('runtime_seconds', '')
                completion_status = row.get('completion_status', '')
                
                if inlist_name and runtime_seconds:
                    try:
                        runtime_minutes = float(runtime_seconds) / 60.0
                        runtimes[inlist_name] = {
                            'runtime_minutes': round(runtime_minutes, 2),
                            'runtime_seconds': runtime_seconds,
                            'status': completion_status
                        }
                    except (ValueError, TypeError):
                        print('aaa')
        
        print(f"Loaded runtime data for {len(runtimes)} models.")
    except Exception as e:
        print(f"Error loading runtime data: {e}")
    
    return runtimes

def write_summary_csv(output_csv="../filled_Lab1.csv", base_dir="../runs", timings_file="../run_timings.csv"):
    # Load runtime data
    runtimes = load_runtime_data(timings_file)
    
    # Use the exact column headers from the spreadsheet plus the new runtime column
    fieldnames = [
        "YOUR NAME", "initial mass  [Msol]", "initial metallicity", 
        "overshoot scheme", "overshoot parameter (f_ov)", "overshoot f0", 
        "", "log_Teff [K]", "log_L [Lsol]", "Core mass [Msol]", 
        "Core radius [Rsol]", "Age [Myr]", "Runtime [s]", "Status"
    ]
    
    run_dirs = [d for d in glob.glob(os.path.join(base_dir, "*")) if os.path.isdir(d)]
    
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for run_dir in run_dirs:
            run_name = os.path.basename(run_dir)
            if not run_name.startswith("inlist_M"):
                continue
                
            logs_dir = os.path.join(run_dir, "LOGS")
            hist_file = os.path.join(logs_dir, "history.data")
            
            if not os.path.exists(hist_file):
                continue
                
            try:
                # Load history data
                history = MesaData(hist_file)
                
                # Parse parameters from run name
                mass, z, scheme, fov, f0 = parse_run_name(run_name)
                
                # Extract values at TAMS
                age, log_Teff, log_L, he_core_mass, tams_idx = extract_tams_values(history)
                core_radius = extract_core_radius(history, tams_idx)
                
                # Get runtime data if available
                runtime_seconds = ""
                status = ""
                if run_name in runtimes:
                    runtime_seconds = runtimes[run_name]['runtime_seconds']
                    status = runtimes[run_name]['status']
                else:
                    runtime_seconds = ''
                    status = 'not_completed'


                # Format values for output
                writer.writerow({
                    "YOUR NAME": "",  # Leave blank for manual entry
                    "initial mass  [Msol]": mass,
                    "initial metallicity": z,
                    "overshoot scheme": "no overshooting" if scheme == "none" else scheme,
                    "overshoot parameter (f_ov)": fov,
                    "overshoot f0": f0,
                    "": "",  # Empty column
                    "log_Teff [K]": round(log_Teff, 3) if isinstance(log_Teff, float) else "",
                    "log_L [Lsol]": round(log_L, 3) if isinstance(log_L, float) else "",
                    "Core mass [Msol]": round(he_core_mass, 5) if isinstance(he_core_mass, float) else "",
                    "Core radius [Rsol]": round(core_radius, 5) if isinstance(core_radius, (float, int)) and core_radius != "NA" else "",
                    "Age [Myr]": round(age, 2) if isinstance(age, float) else "",
                    "Runtime [s]": runtime_seconds,
                    "Status": status
                })
                
                print(f"Processed: {run_name}")
                
            except Exception as e:
                print(f"Error processing {run_name}: {e}")

    print(f"CSV summary saved to: {output_csv}")

if __name__ == "__main__":
    write_summary_csv()