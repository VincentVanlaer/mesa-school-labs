# Modified version of plot_core_mass.py that works with single or batch runs

import os
import numpy as np
import matplotlib.pyplot as plt
import mesa_reader as mr
import glob

def plot_single_core_mass_evolution(logs_path="LOGS"):
    """Create core mass evolution plots for a single MESA run"""
    
    # Check if the LOGS directory exists
    if not os.path.isdir(logs_path):
        print(f"Error: Could not find {logs_path} directory")
        return
        
    # Try to load the history file
    history_path = os.path.join(logs_path, "history.data")
    if not os.path.exists(history_path):
        print(f"Error: Could not find history.data in {logs_path}")
        return
        
    try:
        # Load the data
        data = mr.MesaData(history_path)
        
        # Check if we have core mass information
        has_core_mass = False
        for core_mass_attr in ['he_core_mass', 'mass_conv_core', 'conv_mx1_top']:
            if hasattr(data, core_mass_attr):
                core_mass_attr_name = core_mass_attr
                has_core_mass = True
                break
                
        if not has_core_mass:
            print("Could not find core mass information in history data")
            return False
            
        # Create the plot
        plt.figure(figsize=(10, 8))
        
        # Get age in Myr
        if hasattr(data, 'star_age'):
            age = data.star_age / 1e6  # Convert to Myr
            plt.plot(age, getattr(data, core_mass_attr_name), '-', 
                    color='blue', linewidth=2)
            plt.xlabel("Age (Myr)", fontsize=14)
        else:
            # Fall back to model number
            plt.plot(data.model_number, getattr(data, core_mass_attr_name), '-', 
                    color='blue', linewidth=2)
            plt.xlabel("Model Number", fontsize=14)
        
        plt.ylabel(f"{core_mass_attr_name.replace('_', ' ').title()} ($M_\\odot$)", fontsize=14)
        plt.title(f"Core Mass Evolution", fontsize=16)
        plt.grid(alpha=0.3)
        
        # Save and show
        os.makedirs("plots", exist_ok=True)
        plt.tight_layout()
        plt.savefig("plots/core_mass_evolution.png", dpi=300)
        print(f"Saved core mass evolution plot to plots/core_mass_evolution.png")
        plt.show()
        
        # Also make a fractional core mass plot if we have star mass info
        if hasattr(data, 'star_mass'):
            plt.figure(figsize=(10, 8))
            
            core_mass_fraction = getattr(data, core_mass_attr_name) / data.star_mass
            
            if hasattr(data, 'star_age'):
                plt.plot(age, core_mass_fraction, '-', color='blue', linewidth=2)
                plt.xlabel("Age (Myr)", fontsize=14)
            else:
                plt.plot(data.model_number, core_mass_fraction, '-', color='blue', linewidth=2)
                plt.xlabel("Model Number", fontsize=14)
                
            plt.ylabel("Core Mass Fraction", fontsize=14)
            plt.title("Core Mass Fraction Evolution", fontsize=16)
            plt.grid(alpha=0.3)
            
            plt.tight_layout()
            plt.savefig("plots/core_mass_fraction.png", dpi=300)
            print(f"Saved core mass fraction plot to plots/core_mass_fraction.png")
            plt.show()
            
        return True
        
    except Exception as e:
        print(f"Error creating core mass evolution plots: {e}")
        return False

def main():
    # First, check if we're in a directory with a single MESA run
    if os.path.isdir("../../LOGS"):
        print("Found LOGS directory in current folder. Creating core mass plots for single run.")
        plot_single_core_mass_evolution("../../LOGS")
    
    # If not, try to use the batch runs if available
    if os.path.isdir("../runs"):
        print("Using batch runs directory structure.")
        # Import and run the batch plotting code
        try:
            from batch.plot_ccore_mass import main as batch_main
            batch_main()
        except ImportError:
            print("Could not import batch plotting functions. Are you in the right directory?")
    else:
        print("Error: Could not find LOGS directory or batch_runs/runs directory.")
        print("Make sure you're running this script from the right location.")

if __name__ == "__main__":
    main()
