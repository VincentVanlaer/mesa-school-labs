#!/usr/bin/env python3
"""
plot_timing_analysis.py - Simple script to visualize MESA runtime vs parameters
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

# Load timing data
df_timing = pd.read_csv("../run_timings.csv")
plots_dir = "plots"

# Extract parameters from filenames
data = []
for _, row in df_timing.iterrows():
    filename = row['inlist_name']
    parts = filename.replace('inlist_M', '').split('_')
    
    mass = float(parts[0])
    metallicity = float(parts[1][1:])  # Remove 'Z'
    
    if 'noovs' in filename:
        scheme = 'none'
        fov = 0.0
        f0 = 0.0
    else:
        scheme = parts[2]
        fov = float(parts[3][3:])  # Remove 'fov'
        f0 = float(parts[4][2:])  # Remove 'f0'
    
    runtime = row['runtime_seconds']
    
    data.append({
        'mass': mass,
        'metallicity': metallicity,
        'scheme': scheme,
        'fov': fov,
        'f0': f0,
        'runtime_seconds': runtime
    })

# Create DataFrame
df = pd.DataFrame(data)

# 3D Plot
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

schemes = df['scheme'].unique()
colors = ['blue', 'red', 'green']
markers = ['o', '^', 's']

for i, scheme in enumerate(schemes):
    scheme_data = df[df['scheme'] == scheme]
    
    ax.scatter(
        scheme_data['mass'], 
        scheme_data['fov'],
        scheme_data['runtime_seconds'],
        color=colors[i % len(colors)],
        marker=markers[i % len(markers)],
        label=scheme,
        s=100
    )

ax.set_xlabel('Mass (M☉)')
ax.set_ylabel('Overshooting Parameter (fov)')
ax.set_zlabel('Runtime (seconds)')
ax.legend()
plt.show()
plt.savefig(plots_dir + "/runtime_3d_plot.png", dpi=300)

# 2D Plot with color showing runtime
plt.figure(figsize=(12, 8))

for i, scheme in enumerate(schemes):
    scheme_data = df[df['scheme'] == scheme]
    
    scatter = plt.scatter(
        scheme_data['mass'],
        scheme_data['metallicity'],
        c=scheme_data['runtime_seconds'],
        s=scheme_data['fov'] * 500 + 50,  # Size based on fov
        marker=markers[i % len(markers)],
        cmap='brg',
        edgecolors='black',
        label=scheme
    )

plt.colorbar(scatter, label='Runtime (seconds)')
plt.xlabel('Mass (M☉)')
plt.ylabel('Metallicity (Z)')
plt.legend()
plt.show()
plt.savefig(plots_dir + "/runtime_2d_plot.png", dpi=300)

