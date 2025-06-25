import os
import numpy as np
import matplotlib.pyplot as plt
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
            print(f"Loaded: {run_name}")

    return runs_data

def plot_core_mass_fraction_evolution(runs_data, run_params, plots_dir="plots"):
    os.makedirs(plots_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8))

    scheme_colors = {"none": "black", "exponential": "blue", "step": "red"}
    fov_linestyles = {0.01: "-", 0.02: "-", 0.03: "--", 0.04: "--", 0.10: ":", 0.20: ":", 0.30: "-.", 0.40: "-."}
    mass_markers = {2.0: "o", 5.0: "s", 15.0: "^", 30.0: "d"}

    for run, data in runs_data.items():
        params = run_params[run]
        if not (hasattr(data, 'star_age') and hasattr(data, 'he_core_mass') and hasattr(data, 'star_mass')):
            continue

        cmf = 100.0 * data.he_core_mass / data.star_mass
        age = data.star_age / 1e6

        valid = age >= 1.0
        age = age[valid]
        cmf = cmf[valid]

        color = scheme_colors.get(params["scheme"], "gray")
        linestyle = fov_linestyles[min(fov_linestyles, key=lambda k: abs(k - params["fov"]))] if params["scheme"] != "none" else "-"
        marker = mass_markers[min(mass_markers, key=lambda k: abs(k - params["mass"]))]
        markevery = max(1, len(age) // 8)

        ax.plot(age, cmf, color=color, linestyle=linestyle, linewidth=2, marker=marker, markevery=markevery, markersize=6)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1, None)
    ax.set_xlabel("Age (Myr)", fontsize=14)
    ax.set_ylabel("Core Mass Fraction (%)", fontsize=14)
    ax.set_title("Convective Core Mass Fraction Evolution", fontsize=16)
    ax.grid(True, which="both", ls="-", alpha=0.3)

    ax.text(0.01, 0.02, "Color: Scheme | Line: fov | Marker: Mass", transform=ax.transAxes, fontsize=9,
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))

    plt.tight_layout()
    plt.savefig(f"{plots_dir}/core_mass_fraction_vs_log_age.png", dpi=300)
    plt.show()
    print("Saved core mass fraction plot.")
    return fig

def plot_core_mass_evolution(runs_data, run_params, plots_dir="plots"):
    os.makedirs(plots_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8))

    scheme_colors = {"none": "black", "exponential": "blue", "step": "red"}
    fov_linestyles = {0.01: "-", 0.02: "-", 0.03: "--", 0.04: "--", 0.10: ":", 0.20: ":", 0.30: "-.", 0.40: "-."}
    mass_markers = {2.0: "o", 5.0: "s", 15.0: "^", 30.0: "d"}

    for run, data in runs_data.items():
        params = run_params[run]
        if not (hasattr(data, 'star_age') and hasattr(data, 'he_core_mass')):
            continue

        age = data.star_age / 1e6
        valid = age >= 1.0
        age = age[valid]
        core_mass = data.he_core_mass[valid]

        color = scheme_colors.get(params["scheme"], "gray")
        linestyle = fov_linestyles[min(fov_linestyles, key=lambda k: abs(k - params["fov"]))] if params["scheme"] != "none" else "-"
        marker = mass_markers[min(mass_markers, key=lambda k: abs(k - params["mass"]))]
        markevery = max(1, len(age) // 8)

        ax.plot(age, core_mass, color=color, linestyle=linestyle, linewidth=2, marker=marker, markevery=markevery, markersize=6)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1, None)
    ax.set_xlabel("Age (Myr)", fontsize=14)
    ax.set_ylabel("Core Mass ($M_\odot$)", fontsize=14)
    ax.set_title("Convective Core Mass Evolution", fontsize=16)
    ax.grid(True, which="both", ls="-", alpha=0.3)

    ax.text(0.01, 0.02, "Color: Scheme | Line: fov | Marker: Mass", transform=ax.transAxes, fontsize=9,
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))

    plt.tight_layout()
    plt.savefig(f"{plots_dir}/core_mass_vs_log_age.png", dpi=300)
    plt.show()
    print("Saved core mass plot.")
    return fig

def main():
    batch_runs_dir = "../runs"
    plots_dir = "plots"
    run_dirs = [d for d in glob.glob(os.path.join(batch_runs_dir, "*")) if os.path.isdir(d)]
    run_params = parse_run_parameters(run_dirs)
    runs_data = load_mesa_data(run_dirs, run_params)
    plot_core_mass_fraction_evolution(runs_data, run_params, plots_dir)
    plot_core_mass_evolution(runs_data, run_params, plots_dir)
    print("Done.")

if __name__ == "__main__":
    main()
