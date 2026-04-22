"""
sim_reflection.py
=================

Steady-state cavity reflection spectrum simulation using QuTiP.

Computes the cavity reflection coefficient r(ω) by solving the Lindblad
master equation to steady state for each probe frequency, then extracting
⟨â⟩_ss via the input-output relation.

This module generates:
  - Figure 2b: Narrowband laser reflection spectrum (vacuum Rabi doublet)
  - Figure 2d-f: CW pump spectroscopy (effect of σ− pumping)

Cross-validation: Results are compared against the analytical model in
cavity_model.py to verify the ME simulation.

References:
  Paper Supplementary Eq. (16), (20), (36)-(42)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sim_hamiltonian import (
    build_operators, build_collapse_ops, compute_reflection_spectrum,
    G_GHZ, KAPPA_GHZ, GAMMA_PLUS_GHZ, SIGMA_I_GHZ, N_FOCK_DEFAULT
)
from cavity_model import (
    r_coupled as r_coupled_analytical,
    r_bare as r_bare_analytical,
    spectral_diffusion_pdf,
    compute_spectrum_VH as analytical_VH,
    compute_spectrum_VV as analytical_VV,
)
import os
import time


# Output directory for simulation figures
SIM_FIG_DIR = 'figures_sim_qutip'
os.makedirs(SIM_FIG_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# SPECTRAL DIFFUSION AVERAGING FOR ME SIMULATION
# ══════════════════════════════════════════════════════════════════════════════

def compute_reflection_spectrum_with_sd(delta_c_array, ops, c_ops,
                                         qd_state_label='g', delta_0a=0.0,
                                         g=G_GHZ, sigma_I=SIGMA_I_GHZ,
                                         epsilon=0.01, n_sd=30, sd_range=3.0):
    """
    Compute reflection spectrum averaged over spectral diffusion.
    
    For each spectral diffusion shift δ, the QD-cavity detuning becomes
    Δ_0a + δ. We compute r(ω, δ) for each δ, then average the INTENSITY
    |1-r|²/4 over the Gaussian distribution P(δ).
    
    This is exactly the paper's Eq. (41):
        W_VH = ∫ P(δ) × |1 - r(ω, δ)|² / 4 dδ
    
    Parameters
    ----------
    delta_c_array : array
        Cavity detuning array (GHz).
    ops, c_ops : operators
    qd_state_label : str
        'g' or '-'
    delta_0a : float
        Mean QD-cavity detuning (GHz).
    g : float  
        Coupling strength (GHz).
    sigma_I : float
        Spectral diffusion width (GHz).
    epsilon : float
        Drive amplitude (GHz).
    n_sd : int
        Number of spectral diffusion samples.
    sd_range : float
        Range in units of σ_I.
    
    Returns
    -------
    W_VH : array
        Cross-polarization intensity |1-r|²/4, spectral-diffusion averaged.
    W_VV : array
        Same-polarization intensity |1+r|²/4, spectral-diffusion averaged.
    r_avg : complex array
        Average reflection coefficient (for reference).
    """
    delta_c_array = np.asarray(delta_c_array)
    N = len(delta_c_array)
    
    if qd_state_label == '-' or sigma_I < 1e-6:
        # No spectral diffusion for bare cavity or if σ_I ≈ 0
        r_arr = compute_reflection_spectrum(
            delta_c_array, ops, c_ops,
            qd_state_label=qd_state_label, delta_0a=delta_0a,
            g=g, epsilon=epsilon
        )
        W_VH = np.abs(1.0 - r_arr)**2 / 4.0
        W_VV = np.abs(1.0 + r_arr)**2 / 4.0
        return W_VH, W_VV, r_arr
    
    # Sample spectral diffusion shifts
    sd_vals = np.linspace(-sd_range * sigma_I, sd_range * sigma_I, n_sd)
    weights = spectral_diffusion_pdf(sd_vals, sigma_I)
    d_sd = sd_vals[1] - sd_vals[0]
    
    W_VH = np.zeros(N)
    W_VV = np.zeros(N)
    r_avg = np.zeros(N, dtype=complex)
    
    print(f"  Computing spectral diffusion average ({n_sd} samples)...")
    for j, (sd, w) in enumerate(zip(sd_vals, weights)):
        if (j + 1) % 10 == 0:
            print(f"    SD sample {j+1}/{n_sd} (δ = {sd:.1f} GHz)")
        
        # Shift QD detuning by spectral diffusion
        delta_0a_shifted = delta_0a + sd
        
        r_arr = compute_reflection_spectrum(
            delta_c_array, ops, c_ops,
            qd_state_label='g', delta_0a=delta_0a_shifted,
            g=g, epsilon=epsilon
        )
        
        W_VH += w * np.abs(1.0 - r_arr)**2 / 4.0 * d_sd
        W_VV += w * np.abs(1.0 + r_arr)**2 / 4.0 * d_sd
        r_avg += w * r_arr * d_sd
    
    return W_VH, W_VV, r_avg


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2b: NARROWBAND REFLECTION SPECTRUM
# ══════════════════════════════════════════════════════════════════════════════

def figure_2b(N_cav=N_FOCK_DEFAULT, n_points=80, n_sd=25):
    """
    Generate Figure 2b: High-resolution cavity reflection spectrum.
    
    Reproduces the vacuum Rabi doublet measured with a narrowband tunable
    laser at B = 1.6 T (σ+ transition resonant with cavity, Δ_0a ≈ 0).
    
    The spectrum is measured in cross-polarization (V_in → H_out).
    """
    print("\n" + "=" * 60)
    print("Figure 2b: Narrowband Reflection Spectrum (ME simulation)")
    print("=" * 60)
    
    t_start = time.time()
    
    # Setup
    ops = build_operators(N_cav)
    c_ops = build_collapse_ops(ops)
    
    # Probe frequency range: ±40 GHz around cavity resonance
    delta_c = np.linspace(-40, 40, n_points)
    delta_0a = 0.0  # QD on resonance with cavity at B = 1.6 T
    
    # ── ME simulation: coupled cavity with spectral diffusion ──
    print("\n[ME] Computing coupled spectrum with spectral diffusion...")
    W_VH_me, W_VV_me, r_avg_me = compute_reflection_spectrum_with_sd(
        delta_c, ops, c_ops, qd_state_label='g',
        delta_0a=delta_0a, n_sd=n_sd
    )
    
    # ── ME simulation: bare cavity ──
    print("\n[ME] Computing bare cavity spectrum...")
    r_bare_me = compute_reflection_spectrum(
        delta_c, ops, c_ops, qd_state_label='-',
        delta_0a=delta_0a, g=0.0
    )
    W_VH_bare_me = np.abs(1.0 - r_bare_me)**2 / 4.0
    
    # ── Analytical comparison ──
    print("\n[Analytical] Computing reference spectra...")
    W_VH_analytical = analytical_VH(delta_c, delta_0a, qd_state='g')
    W_VH_bare_analytical = analytical_VH(delta_c, delta_0a, qd_state='-')
    
    t_elapsed = time.time() - t_start
    print(f"\nTotal computation time: {t_elapsed:.1f} s")
    
    # ── Normalize for comparison ──
    # Scale ME and analytical to same peak height
    scale_me = 1.0 / max(W_VH_bare_me.max(), 1e-10)
    scale_an = 1.0 / max(W_VH_bare_analytical.max(), 1e-10)
    
    # ── Plot ──
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Panel 1: Cross-pol intensity (V→H) — main comparison
    ax = axes[0]
    ax.plot(delta_c, W_VH_me * scale_me, 'b-', lw=2, label='ME simulation')
    ax.plot(delta_c, W_VH_analytical * scale_an, 'r--', lw=1.5, 
            label='Analytical (Eq. 41)')
    ax.plot(delta_c, W_VH_bare_me * scale_me, 'k:', lw=1, alpha=0.5,
            label='Bare cavity (ME)')
    ax.set_xlabel('Δ_c / 2π (GHz)', fontsize=12)
    ax.set_ylabel('W_VH (normalized)', fontsize=12)
    ax.set_title('Fig 2b: V→H Cross-Polarization', fontsize=13)
    ax.legend(fontsize=9)
    ax.set_xlim(-40, 40)
    
    # Panel 2: Reflection coefficient r(ω)
    ax = axes[1]
    r_coupled_an = np.array([
        r_coupled_analytical(dc, delta_0a) for dc in delta_c
    ])
    # Average over SD for analytical
    sd_vals = np.linspace(-3*SIGMA_I_GHZ, 3*SIGMA_I_GHZ, n_sd)
    wts = spectral_diffusion_pdf(sd_vals, SIGMA_I_GHZ)
    d_sd = sd_vals[1] - sd_vals[0]
    r_avg_an = np.zeros(len(delta_c), dtype=complex)
    for sd, w in zip(sd_vals, wts):
        r_tmp = np.array([r_coupled_analytical(dc, delta_0a, delta_sd=sd) 
                          for dc in delta_c])
        r_avg_an += w * r_tmp * d_sd
    
    ax.plot(delta_c, np.abs(r_avg_me)**2, 'b-', lw=2, label='|r|² (ME)')
    ax.plot(delta_c, np.abs(r_avg_an)**2, 'r--', lw=1.5, label='|r|² (Analytical)')
    ax.plot(delta_c, np.abs(r_bare_me)**2, 'k:', lw=1, alpha=0.5, 
            label='|r|² (bare)')
    ax.set_xlabel('Δ_c / 2π (GHz)', fontsize=12)
    ax.set_ylabel('|r(ω)|²', fontsize=12)
    ax.set_title('Reflection Coefficient', fontsize=13)
    ax.legend(fontsize=9)
    ax.set_xlim(-40, 40)
    
    plt.tight_layout()
    fig_path = os.path.join(SIM_FIG_DIR, 'Figure2b-ME.png')
    plt.savefig(fig_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {fig_path}")
    
    return delta_c, W_VH_me, W_VH_analytical


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2d-f: CW PUMP SPECTROSCOPY
# ══════════════════════════════════════════════════════════════════════════════

def figure_2def(N_cav=N_FOCK_DEFAULT, n_points=60, n_sd=20):
    """
    Generate Figure 2d-f: CW pump spectroscopy.
    
    Shows how the cavity spectrum changes when pumping the σ− transition:
      d) Pump detuned +10 GHz (QD mostly in |g⟩, coupled spectrum)
      e) Pump on resonance (QD in |−⟩, bare-like spectrum)
      f) Pump detuned -10 GHz (QD mostly in |g⟩, coupled spectrum)
    
    Physics: The pump excites the QD into |−⟩ with a detuning-dependent
    probability. We model this as a mixed state ρ = p|−⟩⟨−| + (1-p)|g⟩⟨g|.
    On resonance, p ≈ 0.5-0.8 (CW saturation); off-resonance, p ≈ 0.
    """
    print("\n" + "=" * 60)
    print("Figure 2d-f: CW Pump Spectroscopy (ME simulation)")
    print("=" * 60)
    
    t_start = time.time()
    
    ops = build_operators(N_cav)
    c_ops = build_collapse_ops(ops)
    
    delta_c = np.linspace(-40, 40, n_points)
    delta_0a = 0.0  # σ+ on resonance with cavity
    
    # Compute coupled and bare spectra
    print("\n[ME] Computing coupled spectrum...")
    W_VH_coupled, _, _ = compute_reflection_spectrum_with_sd(
        delta_c, ops, c_ops, qd_state_label='g',
        delta_0a=delta_0a, n_sd=n_sd
    )
    
    print("\n[ME] Computing bare cavity spectrum...")
    r_bare = compute_reflection_spectrum(
        delta_c, ops, c_ops, qd_state_label='-', delta_0a=delta_0a, g=0.0
    )
    W_VH_bare = np.abs(1.0 - r_bare)**2 / 4.0
    
    # CW pump on σ− transition: model as mixed state
    # On resonance: p_minus ≈ 0.6 (CW saturation)
    # At ±10 GHz detuning: p_minus ≈ 0.05 (Lorentzian tail)
    pump_detunings = [10.0, 0.0, -10.0]     # GHz
    p_minus_values = [0.05, 0.60, 0.05]      # Excitation probability
    panel_labels = ['d', 'e', 'f']
    
    t_elapsed = time.time() - t_start
    print(f"\nComputation time: {t_elapsed:.1f} s")
    
    # ── Plot ──
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    
    # Normalize to peak
    norm = max(W_VH_bare.max(), 1e-10)
    
    for i, (pump_det, p_m, label) in enumerate(
            zip(pump_detunings, p_minus_values, panel_labels)):
        ax = axes[i]
        
        # Mixed spectrum: p × bare + (1-p) × coupled
        W_mixed = p_m * W_VH_bare + (1.0 - p_m) * W_VH_coupled
        
        ax.plot(delta_c, W_mixed / norm, 'b-', lw=2)
        ax.fill_between(delta_c, 0, W_mixed / norm, alpha=0.15, color='blue')
        ax.set_xlabel('Δ_c / 2π (GHz)', fontsize=11)
        ax.set_ylabel('Intensity (norm.)', fontsize=11)
        ax.set_title(f'({label}) Δ_L/2π = {pump_det:+.0f} GHz, p_− = {p_m:.2f}',
                      fontsize=11)
        ax.set_xlim(-40, 40)
        ax.set_ylim(0, 1.1)
    
    plt.suptitle('Figure 2d-f: CW Pump Spectroscopy (ME Simulation)',
                 fontsize=13, y=1.02)
    plt.tight_layout()
    fig_path = os.path.join(SIM_FIG_DIR, 'Figure2def-ME.png')
    plt.savefig(fig_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved: {fig_path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  QuTiP ME Simulation: Cavity Reflection Spectrum            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # Generate Figure 2b
    delta_c, W_VH_me, W_VH_an = figure_2b(n_points=80, n_sd=25)
    
    # Generate Figure 2d-f
    figure_2def(n_points=60, n_sd=20)
    
    print("\n" + "=" * 60)
    print("All reflection spectrum simulations complete.")
    print("=" * 60)
