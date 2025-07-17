# Modified version of plot_hr.py that works with single or batch runs

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mesa_reader as mr
import glob

def plot_single_hr_diagram(logs_path="LOGS"):
    """Create HR diagram for a single MESA run with evolutionary phase information"""
    
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
        
        # Create the plot
        plt.figure(figsize=(10, 8))
        
        # Define color mapping based on central hydrogen abundance if available
        if hasattr(data, 'center_h1'):
            # Create a color map based on central hydrogen abundance
            norm = plt.Normalize(0, max(data.center_h1))
            cmap = plt.cm.viridis
            
            # Plot with color representing evolutionary state
            sc = plt.scatter(data.log_Teff, data.log_L, 
                        c=data.center_h1, cmap=cmap, norm=norm,
                        s=30, alpha=0.8)
            
            # Add a line connecting points
            plt.plot(data.log_Teff, data.log_L, '-', color='gray', alpha=0.5, linewidth=1)
            
            # Add a colorbar
            cbar = plt.colorbar(sc)
            cbar.set_label('Central H mass fraction')
            
            # Mark evolutionary points
            # ZAMS (when H burning is well established)
            zams_h1 = 0.7  # Typical value, adjust if needed
            # TAMS (when central H is depleted to stopping criterion)
            tams_h1 = 0.001
            
            # Find indices closest to ZAMS and TAMS
            if min(data.center_h1) < 0.1 and max(data.center_h1) > 0.6:  # Make sure we have both phases
                zams_idx = np.abs(data.center_h1 - zams_h1).argmin()
                tams_idx = np.abs(data.center_h1 - tams_h1).argmin()
                
                # Mark ZAMS with a star
                plt.scatter(data.log_Teff[zams_idx], data.log_L[zams_idx], 
                          marker='x', s=20, edgecolor='black', facecolor='navy',
                          label='ZAMS')
                
                # Mark TAMS with a square
                plt.scatter(data.log_Teff[tams_idx], data.log_L[tams_idx], 
                          marker='x', s=10, edgecolor='black', facecolor='gold',
                          label='TAMS')
            else:
                # If we don't have the full evolution, just mark start and end
                plt.scatter(data.log_Teff[0], data.log_L[0], color='green', s=100, 
                          marker='o', label='Start')
                plt.scatter(data.log_Teff[-1], data.log_L[-1], color='red', s=100, 
                          marker='s', label='End')
        else:
            # Fallback to original coloring if no center_h1
            plt.plot(data.log_Teff, data.log_L, '-', color='blue', linewidth=2)
            
            # Add points for start and end of evolution
            plt.scatter(data.log_Teff[0], data.log_L[0], color='green', s=100, 
                      marker='o', label='Start')
            plt.scatter(data.log_Teff[-1], data.log_L[-1], color='red', s=100, 
                      marker='s', label='End')
        
        # Set up the plot
        plt.xlabel(r"$\log(T_{\mathrm{eff}}/\mathrm{K})$", fontsize=14)
        plt.ylabel(r"$\log(L/L_{\odot})$", fontsize=14)
        plt.gca().invert_xaxis()  # Teff decreases to the right
        plt.grid(alpha=0.3)
        plt.legend(loc='best')
        
        # Save and show
        os.makedirs("plots", exist_ok=True)
        plt.tight_layout()
        plt.savefig("plots/hr_diagram.png", dpi=300)
        print(f"Saved HR diagram to plots/hr_diagram.png")
        plt.show()
        
        # Make a 3D age plot if age info exists
        if hasattr(data, 'star_age') and hasattr(data, 'log_Teff') and hasattr(data, 'log_L'):
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            age_myr = data.star_age / 1e6  # Convert to Myr
            
            # Add color based on evolutionary phase if available
            if hasattr(data, 'center_h1'):
                points = ax.scatter(data.log_Teff, data.log_L, age_myr,
                                   c=data.center_h1, cmap=cmap, norm=norm,
                                   s=30, alpha=0.8)
                
                # Connect points
                ax.plot(data.log_Teff, data.log_L, age_myr, color='gray', alpha=0.5, linewidth=1)
                
                # Add colorbar
                cbar = fig.colorbar(points, ax=ax, pad=0.1)
                cbar.set_label('Central H mass fraction')
                
                # Mark key evolutionary points if we have the full evolution
                if min(data.center_h1) < 0.1 and max(data.center_h1) > 0.6:
                    ax.scatter(data.log_Teff[zams_idx], data.log_L[zams_idx], age_myr[zams_idx],
                              marker='x', s=200, edgecolor='black', facecolor='navy',
                              label='ZAMS')
                    ax.scatter(data.log_Teff[tams_idx], data.log_L[tams_idx], age_myr[tams_idx],
                              marker='x', s=150, edgecolor='black', facecolor='gold',
                              label='TAMS')
                else:
                    ax.scatter(data.log_Teff[0], data.log_L[0], age_myr[0], 
                             color='green', marker='o', s=100, label='Start')
                    ax.scatter(data.log_Teff[-1], data.log_L[-1], age_myr[-1], 
                             color='red', marker='s', s=100, label='End')
            else:
                ax.plot(data.log_Teff, data.log_L, age_myr, color='blue', linewidth=2)
                ax.scatter(data.log_Teff[0], data.log_L[0], age_myr[0], 
                          color='green', marker='o', s=100, label='Start')
                ax.scatter(data.log_Teff[-1], data.log_L[-1], age_myr[-1], 
                          color='red', marker='s', s=100, label='End')
            
            ax.set_xlabel(r"$\log(T_{\mathrm{eff}}/\mathrm{K})$", fontsize=14)
            ax.set_ylabel(r"$\log(L/L_{\odot})$", fontsize=14)
            ax.set_zlabel("Age (Myr)", fontsize=14)
            ax.invert_xaxis()
            ax.legend()
            
            plt.savefig("plots/hr_diagram_3d.png", dpi=300)
            print(f"Saved 3D HR diagram to plots/hr_diagram_3d.png")
            plt.show()
            
        return True
        
    except Exception as e:
        print(f"Error creating HR diagram: {e}")
        return False



def main():
    # First, check if we're in a directory with a single MESA run
    if os.path.isdir("../../LOGS"):
        print("Found LOGS directory in ../../LOGS folder. Creating HR diagram for single run.")
        plot_single_hr_diagram("../../LOGS")

    if os.path.isdir("../runs"):
        print("Using batch runs directory structure.")
        # Import and run the batch plotting code
        try:
            from batch.plot_hr import main as batch_main
            batch_main()
        except ImportError:
            print("Could not import batch plotting functions. Are you in the right directory?")

    # If not, try to use the batch runs if available
    else:
        print("Error: Could not find LOGS directory or batch_runs/runs directory.")
        print("Make sure you're running this script from the right location.")

if __name__ == "__main__":
    main()
