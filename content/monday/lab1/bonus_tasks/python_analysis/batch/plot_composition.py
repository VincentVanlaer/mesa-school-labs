import os
import numpy as np
import matplotlib.pyplot as plt
import mesa_reader as mr
import glob
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

def create_minimal_plots(batch_runs_dir = "../runs", plots_dir = "../plots"):
    """
    Create minimal number of comprehensive plots showing all models together.
    Only creates two plots: core evolution and final hydrogen profiles.
    """

    os.makedirs(plots_dir, exist_ok=True)
    
    # Find all run directories
    run_dirs = [d for d in glob.glob(os.path.join(batch_runs_dir, "*")) if os.path.isdir(d)]
    
    # Parse run parameters
    run_params = {}
    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        if not run_name.startswith("inlist_M"):
            continue

        parts = run_name[7:].split("_")
        if len(parts) < 2:
            continue
            
        mass = float(parts[0][1:])  # Remove 'M' prefix
        z = float(parts[1][1:])     # Remove 'Z' prefix
        
        # Determine overshooting scheme
        if "noovs" in run_name:
            scheme = "none"
            fov = 0.0
            f0 = 0.0
        else:
            scheme = parts[2] if len(parts) > 2 else "unknown"
            fov = float(parts[3][3:]) if len(parts) > 3 and parts[3].startswith("fov") else 0.0
            f0 = float(parts[4][2:]) if len(parts) > 4 and parts[4].startswith("f0") else 0.0
        
        run_params[run_name] = {
            "mass": mass,
            "metallicity": z,
            "scheme": scheme,
            "fov": fov,
            "f0": f0,
            "path": run_dir
        }
    
    # Load data for all models
    print("Loading data from all models...")
    model_data = {}
    for run_name, params in run_params.items():
        logs_dir = os.path.join(params["path"], "LOGS")
        history_path = os.path.join(logs_dir, "history.data")
        
        if not os.path.exists(history_path):
            continue
            
        try:
            history = mr.MesaData(history_path)
            model_data[run_name] = {
                "history": history,
                "params": params,
                "profiles": {}
            }
            
            # Load final profile
            profile_files = sorted(glob.glob(os.path.join(logs_dir, "profile*.data")), 
                                  key=lambda x: int(os.path.basename(x)[7:-5]))
            
            if profile_files:
                try:
                    profile = mr.MesaData(profile_files[-1])
                    model_data[run_name]["profiles"]["final"] = profile
                except Exception as e:
                    print(f"Error loading final profile for {run_name}: {e}")
                        
        except Exception as e:
            print(f"Error loading data for {run_name}: {e}")
    
    print(f"Loaded data for {len(model_data)} models")
    
    # Create the two main plots
    create_unified_core_evolution_plot(model_data, plots_dir)
    create_unified_hydrogen_profile_plot(model_data, plots_dir)
    
    print("All plots complete!")

def create_unified_core_evolution_plot(model_data, plots_dir):
    """Create a single plot showing core evolution for all models."""
    print("Creating unified core evolution plot...")
    
    # Set up figure
    plt.figure(figsize=(14, 10))
    
    # Define color map for mass
    masses = sorted(set(data["params"]["mass"] for data in model_data.values()))
    colors = plt.cm.viridis(np.linspace(0, 1, len(masses)))
    mass_colors = {mass: colors[i] for i, mass in enumerate(masses)}
    
    # Define line styles for schemes
    scheme_styles = {"none": ":", "exponential": "-", "step": "--"}
    
    # Define opacity for overshooting parameter
    def get_opacity(scheme, fov):
        if scheme == "none":
            return 1.0
        # More overshooting = more opaque
        return 0.4 + 0.6 * min(1.0, fov / 0.2)
    
    # Track legend entries to avoid duplicates
    legend_entries = set()
    
    # Plot each model
    for run_name, data in model_data.items():
        params = data["params"]
        history = data["history"]
        
        if not (hasattr(history, 'star_age') and hasattr(history, 'he_core_mass') and hasattr(history, 'star_mass')):
            continue
            
        # Extract parameters
        mass = params["mass"]
        z = params["metallicity"]
        scheme = params["scheme"]
        fov = params["fov"]
        
        # Calculate core mass fraction
        core_mass_fraction = history.he_core_mass / history.star_mass
        
        # Set line properties
        color = mass_colors[mass]
        linestyle = scheme_styles.get(scheme, "-")
        alpha = get_opacity(scheme, fov)
        
        # Create label
        mass_label = f"M = {mass}M$_\\odot$"
        if scheme == "none":
            label = f"{mass_label}, Z = {z}, No overshooting"
        else:
            label = f"{mass_label}, Z = {z}, {scheme}, f$_{{ov}}$ = {fov}"
        
        # Only add to legend if we haven't seen this combination before
        if label not in legend_entries:
            legend_entries.add(label)
        else:
            label = None  # Don't add to legend
        
        # Convert age to Myr
        age_myr = history.star_age / 1e6
        
        # Plot core mass fraction vs age
        plt.plot(age_myr, core_mass_fraction, linestyle=linestyle, 
                color=color, alpha=alpha, linewidth=2)#, label=label)
    
    # Add reference lines for mass
    for mass, color in mass_colors.items():
        plt.plot([], [], '-', color=color, linewidth=3, label=f"M = {mass}M$_\\odot$")
    
    # Add reference lines for scheme
    for scheme, style in scheme_styles.items():
        plt.plot([], [], style, color='gray', linewidth=2, 
                label=f"{scheme.capitalize() if scheme != 'none' else 'No overshooting'}")
    
    # Set up axes
    plt.xscale('log')
    plt.grid(alpha=0.3)
    
    # Set labels
    plt.xlabel('Age (Myr)', fontsize=14)
    plt.ylabel('Core Mass Fraction (M$_{\\rm core}$/M$_{\\rm star}$)', fontsize=14)
    plt.title('Core Mass Fraction Evolution for All Models', fontsize=16)
    
    # Add legend in two columns
    plt.legend(loc='upper left', fontsize=10, ncol=2)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "core_evolution_all_models.png"), dpi=300)
    plt.show()
    plt.close()
    
    print("Core evolution plot saved.")

def create_unified_hydrogen_profile_plot(model_data, plots_dir):
    """Create a single plot showing hydrogen profiles at TAMS for all models."""
    print("Creating unified hydrogen profile plot...")
    
    # Set up figure
    plt.figure(figsize=(14, 10))
    
    # Define color map for mass
    masses = sorted(set(data["params"]["mass"] for data in model_data.values()))
    colors = plt.cm.viridis(np.linspace(0, 1, len(masses)))
    mass_colors = {mass: colors[i] for i, mass in enumerate(masses)}
    
    # Define line styles for schemes
    scheme_styles = {"none": ":", "exponential": "-", "step": "--"}
    
    # Define opacity for overshooting parameter
    def get_opacity(scheme, fov):
        if scheme == "none":
            return 1.0
        # More overshooting = more opaque
        return 0.4 + 0.6 * min(1.0, fov / 0.2)
    
    # Track legend entries to avoid duplicates
    legend_entries = set()
    
    # Plot each model
    for run_name, data in model_data.items():
        params = data["params"]
        
        if "final" not in data["profiles"]:
            continue
            
        profile = data["profiles"]["final"]
        
        if not (hasattr(profile, 'mass') and hasattr(profile, 'x_mass_fraction_H')):
            continue
            
        # Extract parameters
        mass = params["mass"]
        z = params["metallicity"]
        scheme = params["scheme"]
        fov = params["fov"]
        
        # Set line properties
        color = mass_colors[mass]
        linestyle = scheme_styles.get(scheme, "-")
        alpha = get_opacity(scheme, fov)
        
        # Create label
        mass_label = f"M = {mass}M$_\\odot$"
        if scheme == "none":
            label = f"{mass_label}, Z = {z}, No overshooting"
        else:
            label = f"{mass_label}, Z = {z}, {scheme}, f$_{{ov}}$ = {fov}"
        
        # Only add to legend if we haven't seen this combination before
        if label not in legend_entries:
            legend_entries.add(label)
        else:
            label = None  # Don't add to legend
        
        # Plot hydrogen profile
        plt.plot(profile.mass / profile.star_mass, profile.x_mass_fraction_H, 
                linestyle=linestyle, color=color, alpha=alpha, linewidth=2)#, label=label)
    
    # Add reference lines for mass
    for mass, color in mass_colors.items():
        plt.plot([], [], '-', color=color, linewidth=3, label=f"M = {mass}M$_\\odot$")
    
    # Add reference lines for scheme
    for scheme, style in scheme_styles.items():
        plt.plot([], [], style, color='gray', linewidth=2, 
                label=f"{scheme.capitalize() if scheme != 'none' else 'No overshooting'}")
    
    # Set up axes
    plt.grid(alpha=0.3)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    
    # Set labels
    plt.xlabel('Mass Coordinate (m/M$_{\\rm star}$)', fontsize=14)
    plt.ylabel('Hydrogen Mass Fraction', fontsize=14)
    plt.title('Hydrogen Profiles at TAMS for All Models', fontsize=16)
    
    # Add legend in two columns
    plt.legend(loc='upper left', fontsize=10, ncol=2)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "hydrogen_profiles_all_models.png"), dpi=300)
    plt.show()
    plt.close()
    
    print("Hydrogen profile plot saved.")

def main():
    batch_runs_dir = "../runs"
    plots_dir = "plots"
    create_minimal_plots(batch_runs_dir = batch_runs_dir, plots_dir = plots_dir)

if __name__ == "__main__":
    main()
