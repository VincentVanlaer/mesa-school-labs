import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mesa_reader as mr
import glob

def parse_run_parameters(run_dirs):
    run_params = {}

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        if not run_name.startswith("inlist_M"):
            continue

        name_parts = run_name[7:]
        parts = name_parts.split("_")

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

        run_params[run_name] = {
            "mass": mass,
            "metallicity": z,
            "scheme": scheme,
            "fov": fov,
            "f0": f0
        }

    return run_params

def load_mesa_data(run_dirs, run_params):
    runs_data = {}

    for run_dir in run_dirs:
        run_name = os.path.basename(run_dir)
        if run_name not in run_params:
            continue

        history_path = os.path.join(run_dir, "LOGS", "history.data")
        if os.path.exists(history_path):
            h = mr.MesaData(history_path)
            runs_data[run_name] = h

    return runs_data

def plot_all_hr_diagrams(runs_data, run_params, plots_dir="plots"):
    os.makedirs(plots_dir, exist_ok=True)
    plt.figure(figsize=(16, 12))

    masses = sorted(set(param["mass"] for param in run_params.values()))
    mass_colors = plt.cm.brg(np.linspace(0, 1, len(masses)))
    mass_color_map = {mass: mass_colors[i] for i, mass in enumerate(masses)}
    scheme_markers = {'none': 'o', 'exponential': '^', 'step': 's'}

    for run, data in runs_data.items():
        params = run_params[run]
        if not (hasattr(data, 'log_Teff') and hasattr(data, 'log_L')):
            continue

        base_color = mass_color_map[params["mass"]]
        fov_alpha = 0.3 + 0.7 * params["fov"] if params["scheme"] != "none" else 1.0

        if params["scheme"] == "none":
            linestyle = '--'
        elif params["scheme"] == "exponential":
            linestyle = '-'
        else:
            linestyle = ':'

        label = f"M={params['mass']}M☉, Z={params['metallicity']}, "
        label += "No Overshooting" if params["scheme"] == "none" else f"{params['scheme']}, fov={params['fov']:.3f}"

        plt.plot(data.log_Teff, data.log_L,
                 linestyle=linestyle,
                 color=base_color,
                 alpha=fov_alpha,
                 linewidth=2,
                 #label=label
                 )

    plt.xlabel(r"$\log(T_{\mathrm{eff}}/\mathrm{K})$", fontsize=14)
    plt.ylabel(r"$\log(L/L_{\odot})$", fontsize=14)
    plt.title(f"HR Diagram for All Stellar Models", fontsize=16)
    plt.grid(alpha=0.3)
    plt.gca().invert_xaxis()

    for mass in masses:
        plt.plot([], [], '-', color=mass_color_map[mass], linewidth=3, label=f"{mass}M☉")

    for scheme, marker in scheme_markers.items():
        plt.plot([], [], linestyle='-' if scheme == 'exponential' else '--' if scheme == 'none' else ':',
                 color='gray', label=f"{scheme} scheme")

    if len(runs_data) > 15:
        plt.legend(fontsize=9, loc='upper left', bbox_to_anchor=(1.01, 1.0))
    else:
        plt.legend(fontsize=10, loc='best')

    plt.tight_layout()
    plt.savefig(f"{plots_dir}/all_hr_diagrams.png", dpi=300, bbox_inches='tight')
    plt.show()

    fig = plt.figure(figsize=(18, 14))
    ax = fig.add_subplot(111, projection='3d')

    for run, data in runs_data.items():
        params = run_params[run]
        if not (hasattr(data, 'log_Teff') and hasattr(data, 'log_L') and hasattr(data, 'star_age')):
            continue

        base_color = mass_color_map[params["mass"]]
        age_myr = data.star_age / 1e6

        label = f"M={params['mass']}M☉, "
        label += "No Overshooting" if params["scheme"] == "none" else f"{params['scheme']}, fov={params['fov']:.3f}"

        ax.plot(data.log_Teff, data.log_L, age_myr,
                color=base_color,
                linewidth=2,
                alpha=0.8,
                #label=label
                )

        ax.scatter(data.log_Teff[0], data.log_L[0], age_myr[0],
                  color=base_color, marker='o', s=50, alpha=0.8)
        ax.scatter(data.log_Teff[-1], data.log_L[-1], age_myr[-1],
                  color=base_color, marker='s', s=50, alpha=0.8)

    ax.set_xlabel(r"$\log(T_{\mathrm{eff}}/\mathrm{K})$", fontsize=14)
    ax.set_ylabel(r"$\log(L/L_{\odot})$", fontsize=14)
    ax.set_zlabel("Age (Myr)", fontsize=14)
    ax.set_title(f"HR Diagram with Age for All Stellar Models", fontsize=16)
    ax.invert_xaxis()
    ax.view_init(elev=30, azim=-60)

    if len(runs_data) <= 10:
        ax.legend(fontsize=9, loc='best')

    plt.tight_layout()
    plt.savefig(f"{plots_dir}/all_hr_diagrams_3d.png", dpi=300, bbox_inches='tight')
    plt.show()



    try:
        print("Trying to make GIF...")
        from matplotlib import animation

        # Animate the 3D plot (full rotation + bobbing)
        def update_view(frame):
            azim = (frame % 360)
            elev = 30 + 30 * np.sin(np.radians(frame)*2)  # bob up and down
            ax.view_init(elev=elev, azim=azim)
            return fig,

        # Save animation as GIF
        frames = 360  # 1 degree per frame = smooth full rotation
        anim = animation.FuncAnimation(fig, update_view, frames=frames, interval=50, blit=False)
        gif_path = os.path.join(plots_dir, "hr_diagram_3d_rotation.gif")
        anim.save(gif_path, writer='pillow', fps=20)
        print("... GIF made!")
    except:
        print("\033[1;31m" + "="*60)
        print("   \033[91mFAILED TO MAKE GIF\033[0m".center(60))
        print("   \033[90mMaybe you don't have\033[0m \033[1;36m'pillow'\033[0m \033[90minstalled...\033[0m".center(60))
        print("\033[1;31m" + "="*60 + "\033[0m")




def main():
    batch_runs_dir = "../runs"
    plots_dir = "plots"
    run_dirs = [d for d in glob.glob(os.path.join(batch_runs_dir, "*")) if os.path.isdir(d)]
    print(run_dirs)
    run_params = parse_run_parameters(run_dirs)
    runs_data = load_mesa_data(run_dirs, run_params)
    plot_all_hr_diagrams(runs_data, run_params, plots_dir)

if __name__ == "__main__":
    main()
