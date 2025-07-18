# Modified version of plot_composition.py that works with single MESA run

import os
import numpy as np
import matplotlib.pyplot as plt
import mesa_reader as mr
import glob

def plot_single_composition_profiles(logs_path="LOGS"):
    """Create composition profile plots for a single MESA run"""
    
    # Check if the LOGS directory exists
    if not os.path.isdir(logs_path):
        print(f"Error: Could not find {logs_path} directory")
        return
        
    # Try to find the latest profile file
    profile_files = sorted(glob.glob(os.path.join(logs_path, "profile*.data")))
    
    if not profile_files:
        print(f"Error: Could not find any profile files in {logs_path}")
        return
        
    try:
        # Load the last profile
        latest_profile = mr.MesaData(profile_files[-1])
        
        # Create the hydrogen profile plot
        plt.figure(figsize=(10, 8))
        if hasattr(latest_profile, 'mass') and hasattr(latest_profile, 'x_mass_fraction_H'):
            # Plot mass fraction vs mass coordinate
            plt.plot(latest_profile.mass / latest_profile.star_mass, 
                     latest_profile.x_mass_fraction_H, '-', 
                     color='blue', linewidth=2, label='Hydrogen')
            
            # Add helium if available
            if hasattr(latest_profile, 'y_mass_fraction_He'):
                plt.plot(latest_profile.mass / latest_profile.star_mass, 
                         latest_profile.y_mass_fraction_He, '-', 
                         color='red', linewidth=2, label='Helium')
            
            # Add metals if available
            if hasattr(latest_profile, 'z_mass_fraction_metals'):
                plt.plot(latest_profile.mass / latest_profile.star_mass, 
                         latest_profile.z_mass_fraction_metals, '-', 
                         color='green', linewidth=2, label='Metals')
            
            plt.xlabel("Mass Coordinate (m/M$_{\\rm star}$)", fontsize=14)
            plt.ylabel("Mass Fraction", fontsize=14)
            plt.title("Composition Profile at Final Model", fontsize=16)
            plt.legend(loc='best')
            plt.grid(alpha=0.3)
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            
            # Save and show
            os.makedirs("plots", exist_ok=True)
            plt.tight_layout()
            plt.savefig("plots/composition_profile.png", dpi=300)
            print(f"Saved composition profile to plots/composition_profile.png")
            plt.show()
        
        # Create the mixing plot
        plt.figure(figsize=(10, 8))
        if hasattr(latest_profile, 'mass') and hasattr(latest_profile, 'log_D_mix'):
            plt.plot(latest_profile.mass / latest_profile.star_mass, 
                     latest_profile.log_D_mix, '-', 
                     color='blue', linewidth=2)
            
            plt.xlabel("Mass Coordinate (m/M$_{\\rm star}$)", fontsize=14)
            plt.ylabel("log D$_{\\rm mix}$ (cm$^2$/s)", fontsize=14)
            plt.title("Mixing Profile at Final Model", fontsize=16)
            plt.grid(alpha=0.3)
            plt.xlim(0, 1)
            
            plt.tight_layout()
            plt.savefig("plots/mixing_profile.png", dpi=300)
            print(f"Saved mixing profile to plots/mixing_profile.png")
            plt.show()
            
        return True
        
    except Exception as e:
        print(f"Error creating composition profile plots: {e}")
        return False

def main():
    # First, check if we're in a directory with a single MESA run
        # If not, try to use the batch runs if available
    if os.path.isdir("../../LOGS"):
        print("Found LOGS directory in current folder. Creating composition plots for single run.")
        plot_single_composition_profiles("../../LOGS")

    if os.path.isdir("../runs"):
        print("Using batch runs directory structure.")
        # Import and run the batch plotting code

        try:
            from batch.plot_composition import main as batch_main
            batch_main()
        except ImportError:
            print("Could not import batch plotting functions. Are you in the right directory?")

    else:
        print("Error: Could not find LOGS directory or batch_runs/runs directory.")
        print("Make sure you're running this script from the right location.")

if __name__ == "__main__":
    main()
