#!/usr/bin/env python3
"""
run_batch.py - Python script to run MESA with each inlist in the batch directory
Cross-platform replacement for run_batch.sh
"""

import os
import sys
import glob
import shutil
import subprocess
import re
import time
import csv

def run_batch():
    """Run MESA with each inlist in the batch directory"""
    # Change to main MESA work directory
    os.chdir("../..")
    
    # Check if we're in the right directory
    if not os.path.isfile("inlist") or not os.path.isfile("star"):
        print("Error: This script must be run from the main MESA work directory.")
        sys.exit(1)
    
    batch_dir = os.path.join("bonus_tasks", "batch_inlists")
    output_dir = os.path.join("bonus_tasks", "runs")
    timing_file = os.path.join("bonus_tasks", "run_timings.csv")
    
    # Check if batch inlists exist
    inlist_files = glob.glob(os.path.join(batch_dir, "*.inp"))
    if not os.path.isdir(batch_dir) or not inlist_files:
        print(f"Error: No batch inlists found in {batch_dir}.")
        print("Please run make_batch.py first to create the inlists.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Count total number of inlists to process
    total = len(inlist_files)
    print(f"Found {total} inlist files in {batch_dir}")
    
    # Confirm with user before proceeding
    if "--force" not in sys.argv:
        print(f"\nYou are about to run {total} MESA simulations.")
        response = input("Do you want to continue? (yes/no): ")
        if not response.lower().startswith('y'):
            print("Batch run cancelled.")
            sys.exit(0)
    
    # Initialize timing file with header if it doesn't exist
    if not os.path.exists(timing_file):
        with open(timing_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["inlist_name", "runtime_seconds", "completion_status"])
    
    # Process each inlist
    current = 0
    for inlist_file in inlist_files:
        current += 1
        inlist_name = os.path.basename(inlist_file).rsplit('.', 1)[0]
        run_dir = os.path.join(output_dir, inlist_name)
        
        print(f"[{current}/{total}] Processing {inlist_name}...")
        
        # Create run directory and subdirectories
        os.makedirs(run_dir, exist_ok=True)
        os.makedirs(os.path.join(run_dir, "LOGS"), exist_ok=True)
        os.makedirs(os.path.join(run_dir, "photos"), exist_ok=True)
        
        # Copy necessary files
        shutil.copy(inlist_file, "inlist_project")
        
        # Run MESA
        print(f"Running MESA with {inlist_name} parameters...")
        start_time = time.time()
        
        with open(os.path.join(run_dir, "run.log"), 'w') as log_file:
            result = subprocess.run(["./star"], stdout=log_file, stderr=log_file)
        
        end_time = time.time()
        elapsed = int(end_time - start_time)
        
        # Determine completion status
        if result.returncode == 0:
            completion_status = "completed"
        else:
            completion_status = "failed"
            print(f"Warning: MESA run for {inlist_name} may have encountered an error.")
        
        # Record timing in the CSV file
        with open(timing_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([inlist_name, elapsed, completion_status])
        
        print(f"Run completed in {elapsed} seconds (Status: {completion_status}).")
        
        # Copy results
        if os.path.isdir("LOGS"):
            for item in os.listdir("LOGS"):
                s = os.path.join("LOGS", item)
                d = os.path.join(run_dir, "LOGS", item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)
        
        if os.path.isdir("photos"):
            for item in os.listdir("photos"):
                s = os.path.join("photos", item)
                d = os.path.join(run_dir, "photos", item)
                if os.path.isfile(s):
                    shutil.copy2(s, d)
        
        shutil.copy("inlist_project", run_dir)
        if os.path.isfile("inlist"):
            shutil.copy("inlist", run_dir)
        if os.path.isfile("inlist_pgstar"):
            shutil.copy("inlist_pgstar", run_dir)
        
        # Copy model file if it exists
        # Extract model filename from inlist
        with open(inlist_file, 'r') as f:
            content = f.read()
            model_file_match = re.search(r"save_model_filename\s*=\s*'([^']*)'", content)
            if model_file_match:
                model_file = model_file_match.group(1)
                if os.path.isfile(model_file):
                    shutil.copy2(model_file, run_dir)
        
        print(f"Completed run for {inlist_name}")
        print("------------------------------------------")
    
    print("\nAll batch runs completed!")
    print(f"Timing information saved to {timing_file}")

if __name__ == "__main__":
    run_batch()
