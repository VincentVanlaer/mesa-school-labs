# Rotation and centrifugal-force kernels, K_rot(r) and K_cent(r).
# These are to be integrated with respect to r, multiplied against
# 4πr²ρ and the rotational profile Ω(r), to yield the rotational
# splitting δω, under the normalisation convention that
# \int (ξr² + l(l+1) ξh²)4πr²ρ dr = 1.
# Integrating K_rot against a unit rotational profile gives
# the solid-body rotational sensitivity constant mβ = m(1-C).
# C ~ 1 for a p-mode and ~ 1/l(l+1) for a g-mode.

import numpy as np
import pygyre
from scipy.integrate import trapezoid

def rot_kernel(ξr1, ξh1, ξr2, ξh2, l, m):
    Λ2 = l * (l + 1)
    return 2*m * (ξr1.conj() * ξr2 + (Λ2 - 1) * (ξh1.conj() * ξh2) - ξr1.conj() * ξh2 - ξh1.conj() * ξr2)

def inertia(ρ, r, ξr, ξh, l):
    Λ2 = l * (l + 1)
    return trapezoid(ρ * r**2 * (np.abs(ξr)**2 + Λ2 * np.abs(ξh)**2), r)

def read_model(model_file):
    return pygyre.read_model(model_file)

def read_summary(summary_file):
    return pygyre.read_output(summary_file)

def read_details(model, detail_files):
    '''this is expected to be a list of filenames'''

    R = model.meta['R_star'] # in CGS units
    details = [pygyre.read_output(d) for d in detail_files]

    ξrs = [d['xi_r'] for d in details]
    ξhs = [d['xi_h'] for d in details]
    ρ = d[0]['ρ']
    r = d[0]['x'] * R
    Ω = np.interp(r, model['r'], model['Omega_rot'])
    return ρ, r, Ω, ξrs, ξhs

def compute_splitting(Ω, ρ, r, ξr, ξh, l):
    K = ρ * r**2 * rot_kernel(ξ_r, ξ_h, ξ_r, ξ_h, l, 1)
    inertia(ρ, r, ξ_r, ξ_h, l)
    β = trapezoid(K, r) / I / 2
    δω = trapezoid(Ω * K, r) / I / 2
    return β, δω