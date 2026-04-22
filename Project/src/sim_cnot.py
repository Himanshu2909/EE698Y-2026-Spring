"""
sim_cnot.py
===========

CNOT gate simulation: full pump-probe protocol with polarization analysis.

Simulates the QD-photon CNOT gate for all 4 input-output polarization
combinations (HH, HV, VH, VV) using the ME-derived reflection coefficient.

Generates:
  - Figure 4a-d: Cavity spectra for all polarization combinations
  - Figure 4e: Probability truth table (bar charts)

Physics:
  The photonic crystal cavity has polarization axis ŷ.
  Input in H/V basis decomposes into cavity basis:
    |H⟩ = (|x⟩ + |y⟩)/√2
    |V⟩ = (|y⟩ - |x⟩)/√2
  
  x-component interacts with cavity: reflected with r(ω)
  y-component reflects from surface: reflected with r_y = -1
  
  Output fields:
    b_H = [(1+r)/2] a_H + [(1-r)/2] a_V        (Eq. 23 from supp.)
    b_V = [(1-r)/2] a_H + [(1+r)/2] a_V        (Eq. 24 from supp.)
  
  Wait — the paper uses: b̂_x = -â_x + √κ â (Eq. 3)
  and b̂_y = -â_y (Eq. 4) → r_y = -1
  
  In H/V basis:
    b_H = [(r+r_y)/2] a_H + [(r-r_y)/2] a_V
    b_V = [(r-r_y)/2] a_H + [(r+r_y)/2] a_V
  
  With r_y = -1:
    b_H = [(r-1)/2] a_H + [(r+1)/2] a_V
    b_V = [(r+1)/2] a_H + [(r-1)/2] a_V
  
  Wait, that doesn't match the paper's Eq (23-24). Let me re-derive:
  
  Paper Eq (1-2):  â_H = (â_x + â_y)/√2,  â_V = (â_y - â_x)/√2
  Paper Eq (3-4):  b̂_x = -â_x + √κ â = r_x â_x,  b̂_y = -â_y = r_y â_y
  
  Actually r_y = -1 (direct reflection preserves phase for y-pol).
  
  Paper Eq (21-22):
    b̂_H = (b̂_x + b̂_y)/√2 = (r_x â_x - â_y)/√2
    b̂_V = (b̂_y - b̂_x)/√2 = (-â_y - r_x â_x)/√2
  
  Substituting â_x = (â_H - â_V)/√2*(-1) ... actually this is getting messy.
  Let me just use the paper's final equations:
  
  From Eq (23): b̂_H = [(1+r)/2] â_H + [(1-r)/2] â_V
  From Eq (24): b̂_V = [(1-r)/2] â_H + [(1+r)/2] â_V
  
  Wait... that can't be right because with the sign conventions used.
  Let me verify: from Eq 1, â_x = (â_H - â_V)/√2 ... no wait:
  â_H = (â_x + â_y)/√2 → â_x = (â_H - â_V) ... no.
  
  From Eq (1): â_H = (â_x + â_y)/√2
  From Eq (2): â_V = (â_y - â_x)/√2
  Solving: â_x = (â_H - â_V)/√2, â_y = (â_H + â_V)/√2
  
  Wait: â_H + â_V = (â_x + â_y + â_y - â_x)/√2 = 2â_y/√2 = √2 â_y
  â_H - â_V = (â_x + â_y - â_y + â_x)/√2 = 2â_x/√2 = √2 â_x
  So: â_x = (â_H - â_V)/√2, â_y = (â_H + â_V)/√2  
  
  Then: b̂_x = r â_x, b̂_y = -â_y (r_y = -1)
  
  b̂_H = (b̂_x + b̂_y)/√2 = (r â_x - â_y)/√2
       = (r(â_H - â_V)/√2 - (â_H + â_V)/√2) / √2
       = [r(â_H - â_V) - (â_H + â_V)] / 2
       = [(r-1)â_H + (-r-1)â_V] / 2
       = [(r-1)/2] â_H - [(r+1)/2] â_V
  
  b̂_V = (b̂_y - b̂_x)/√2 = (-â_y - r â_x)/√2
       = (-(â_H + â_V)/√2 - r(â_H - â_V)/√2) / √2
       = [-(â_H + â_V) - r(â_H - â_V)] / 2
       = [(-1-r)â_H + (-1+r)â_V] / 2
       = [-(r+1)/2] â_H + [(r-1)/2] â_V
  
  Hmm, this has signs. Let me think about what r means more carefully.
  
  From paper Eq (20): for bare cavity at resonance, r = -1.
  So the total reflection for x-pol is r_x = r (includes the sign).
  
  Let's check: if QD in |−⟩ and at resonance, r = -1.
  Then:
    b̂_H = [(-1-1)/2] â_H - [(-1+1)/2] â_V = -â_H
    b̂_V = [-(-1+1)/2] â_H + [(-1-1)/2] â_V = -â_V
  So b_H = -a_H, b_V = -a_V: polarization preserved. ✓
  
  If QD in |g⟩ and strong coupling: r ≈ +0.83.
  Then:
    b̂_H = [(0.83-1)/2] â_H - [(0.83+1)/2] â_V 
         = -0.085 â_H - 0.915 â_V
    b̂_V = [-(0.83+1)/2] â_H + [(0.83-1)/2] â_V
         = -0.915 â_H - 0.085 â_V
  
  For V input (â_H=0, â_V=1):
    b_H = -0.915,  b_V = -0.085
    P_VH = |b_H|² = 0.837,  P_VV = |b_V|² = 0.007
  
  That means V→H intensity is LARGE when QD coupled. This is the 
  cross-polarization rotation (polarization flip) = CNOT bit-flip ✓
  
  For V input, QD in |−⟩ (r=-1):
    b_H = 0,  b_V = -1
    P_VH = 0,  P_VV = 1
  No rotation = identity. Wait, but the paper says the opposite convention...
  
  Actually this IS correct:
    QD |g⟩ + V → mostly H (bit flip) ✓
    QD |−⟩ + V → stays V (identity) ✓
    This IS CNOT behavior!

  So the output intensities are:
    W_ab(ω) = |⟨b̂_b⟩|² when input is |a⟩ polarized
  
  Now, with spectral diffusion we average the intensities as in Eq (37)-(40).

References:
  Paper Supplementary Eq. (23)-(24), (37)-(40)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import time

from sim_hamiltonian import (
    build_operators, build_collapse_ops, compute_reflection_spectrum,
    G_GHZ, KAPPA_GHZ, GAMMA_PLUS_GHZ, SIGMA_I_GHZ, N_FOCK_DEFAULT,
)
from sim_reflection import compute_reflection_spectrum_with_sd
from cavity_model import spectral_diffusion_pdf

SIM_FIG_DIR = 'figures_sim_qutip'
os.makedirs(SIM_FIG_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# POLARIZATION TRANSFER MATRIX
# ══════════════════════════════════════════════════════════════════════════════

def polarization_intensities(r_array):
    """
    Compute output polarization intensities for all 4 input-output combos.
    
    Given the cavity reflection coefficient r(ω), compute the output
    intensities W_ab where a = input pol, b = output pol.
    
    From the derivation (see module docstring):
      b_H = [(r-1)/2] a_H - [(r+1)/2] a_V
      b_V = [-(r+1)/2] a_H + [(r-1)/2] a_V
    
    For input |H⟩ (a_H=1, a_V=0):
      W_HH = |b_H|² = |(r-1)/2|² 
      W_HV = |b_V|² = |(r+1)/2|²
    
    For input |V⟩ (a_H=0, a_V=1):
      W_VH = |b_H|² = |(r+1)/2|² 
      W_VV = |b_V|² = |(r-1)/2|²
    
    Note: W_HH = W_VV = |r-1|²/4 and W_HV = W_VH = |r+1|²/4.
    Cross-pol and same-pol are symmetric in this ideal model.
    
    Wait, that can't be right. Let me recheck...
    
    For V input:
      b_H = -[(r+1)/2] × 1 = -(r+1)/2
      |b_H|² = |r+1|²/4  ← W_VH
      
      b_V = [(r-1)/2] × 1 = (r-1)/2
      |b_V|² = |r-1|²/4  ← W_VV
    
    For H input:
      b_H = [(r-1)/2] × 1 = (r-1)/2
      |b_H|² = |r-1|²/4  ← W_HH
      
      b_V = [-(r+1)/2] × 1 = -(r+1)/2
      |b_V|² = |r+1|²/4  ← W_HV
    
    So: W_HH = W_VV = |r-1|²/4 (same-pol → SAME as each other)
        W_HV = W_VH = |r+1|²/4 (cross-pol → SAME as each other)
    
    Parameters
    ----------
    r_array : complex array
        Reflection coefficient r(ω).
    
    Returns
    -------
    W_HH, W_HV, W_VH, W_VV : arrays
        Output intensities for each polarization combination.
    """
    r = np.asarray(r_array)
    
    W_HH = np.abs(r - 1.0)**2 / 4.0   # Same-pol (H→H)
    W_HV = np.abs(r + 1.0)**2 / 4.0   # Cross-pol (H→V)
    W_VH = np.abs(r + 1.0)**2 / 4.0   # Cross-pol (V→H)
    W_VV = np.abs(r - 1.0)**2 / 4.0   # Same-pol (V→V)
    
    return W_HH, W_HV, W_VH, W_VV


def compute_cnot_spectra(delta_c_array, ops, c_ops, qd_state_label='g',
                          delta_0a=0.0, g=G_GHZ, sigma_I=SIGMA_I_GHZ,
                          epsilon=0.01, n_sd=20, sd_range=3.0,
                          bg_HH=0.0, bg_VV=0.0):
    """
    Compute CNOT output spectra for all 4 polarization combinations.
    
    Includes spectral diffusion averaging and optional background for
    same-pol channels (due to imperfect mode matching).
    
    Parameters
    ----------
    delta_c_array : array
        Cavity detuning array (GHz).
    ops, c_ops : system operators
    qd_state_label : str
        'g' or '-'
    delta_0a, g, sigma_I, epsilon : physical parameters
    n_sd : int
        Number of spectral diffusion samples.
    bg_HH, bg_VV : float
        Additive background for same-pol channels (fraction of peak).
    
    Returns
    -------
    W_dict : dict
        Dictionary with keys 'HH', 'HV', 'VH', 'VV' containing intensity arrays.
    """
    delta_c_array = np.asarray(delta_c_array)
    N = len(delta_c_array)
    
    if qd_state_label == '-' or sigma_I < 1e-6:
        r_arr = compute_reflection_spectrum(
            delta_c_array, ops, c_ops,
            qd_state_label=qd_state_label, delta_0a=delta_0a,
            g=g, epsilon=epsilon
        )
        W_HH, W_HV, W_VH, W_VV = polarization_intensities(r_arr)
        
    else:
        # Spectral diffusion averaging
        sd_vals = np.linspace(-sd_range * sigma_I, sd_range * sigma_I, n_sd)
        weights = spectral_diffusion_pdf(sd_vals, sigma_I)
        d_sd = sd_vals[1] - sd_vals[0]
        
        W_HH = np.zeros(N)
        W_HV = np.zeros(N)
        W_VH = np.zeros(N)
        W_VV = np.zeros(N)
        
        for sd, w in zip(sd_vals, weights):
            delta_0a_shifted = delta_0a + sd
            r_arr = compute_reflection_spectrum(
                delta_c_array, ops, c_ops,
                qd_state_label='g', delta_0a=delta_0a_shifted,
                g=g, epsilon=epsilon
            )
            hh, hv, vh, vv = polarization_intensities(r_arr)
            W_HH += w * hh * d_sd
            W_HV += w * hv * d_sd
            W_VH += w * vh * d_sd
            W_VV += w * vv * d_sd
    
    # Add background for same-pol channels
    W_HH += bg_HH
    W_VV += bg_VV
    
    return {'HH': W_HH, 'HV': W_HV, 'VH': W_VH, 'VV': W_VV}


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4a-d: ALL POLARIZATION COMBINATIONS
# ══════════════════════════════════════════════════════════════════════════════

def figure_4(N_cav=N_FOCK_DEFAULT, n_freq=60, n_sd=20):
    """
    Generate Figure 4a-d: CNOT spectra for all polarization combinations,
    and Figure 4e: probability truth table.
    
    Panel layout:
      (a) H_in → V_out
      (b) V_in → H_out
      (c) V_in → V_out
      (d) H_in → H_out
    
    Blue: 80 ps delay (π-pulse, p_− ≈ 0.80)
    Red: 4 ns delay (QD relaxed, p_− = 0)
    """
    print("\n" + "=" * 60)
    print("Figure 4: CNOT Gate — All Polarization Combinations")
    print("=" * 60)
    
    t_start = time.time()
    
    ops = build_operators(N_cav)
    c_ops = build_collapse_ops(ops)
    
    delta_c = np.linspace(-40, 40, n_freq)
    delta_0a = 0.0
    
    # ── Compute spectra for both QD states ──
    print("\n  [ME] Computing coupled spectra (QD in |g⟩)...")
    W_coupled = compute_cnot_spectra(
        delta_c, ops, c_ops, qd_state_label='g',
        delta_0a=delta_0a, n_sd=n_sd,
        bg_HH=0.01, bg_VV=0.01  # 1% background for same-pol
    )
    
    print("  [ME] Computing bare spectra (QD in |−⟩)...")
    W_bare = compute_cnot_spectra(
        delta_c, ops, c_ops, qd_state_label='-',
        delta_0a=delta_0a, g=0.0, n_sd=1,
        bg_HH=0.01, bg_VV=0.01
    )
    
    # 80 ps delay: p_− ≈ 0.80 (after π-pulse and partial decay)
    p_minus_80ps = 0.80
    # 4 ns delay: p_− = 0 (fully relaxed)
    p_minus_4ns = 0.0
    
    # Mixed spectra
    W_pi = {}
    W_g = {}
    for key in ['HH', 'HV', 'VH', 'VV']:
        W_pi[key] = p_minus_80ps * W_bare[key] + (1 - p_minus_80ps) * W_coupled[key]
        W_g[key] = p_minus_4ns * W_bare[key] + (1 - p_minus_4ns) * W_coupled[key]
    
    # Scaling to experimental counts
    scale = 25000 / max(W_bare['VH'].max(), 1e-10)
    bg = 3000
    
    t_elapsed = time.time() - t_start
    print(f"\n  Computation time: {t_elapsed:.1f} s")
    
    # ── Panel arrangement: (a) HV, (b) VH, (c) VV, (d) HH ──
    panels = [
        ('a', 'HV', 'H_in → V_out'),
        ('b', 'VH', 'V_in → H_out'),
        ('c', 'VV', 'V_in → V_out'),
        ('d', 'HH', 'H_in → H_out'),
    ]
    
    fig, axes = plt.subplots(1, 4, figsize=(20, 4.5))
    
    for i, (label, key, title) in enumerate(panels):
        ax = axes[i]
        
        I_pi = W_pi[key] * scale + bg
        I_g = W_g[key] * scale + bg
        
        ax.plot(delta_c, I_pi / 1000, 'bo-', ms=3, lw=1.5, label='80 ps (π-pulse)')
        ax.plot(delta_c, I_g / 1000, 'rs-', ms=3, lw=1.5, label='4 ns (relaxed)')
        
        ax.set_xlabel('Δ_c / 2π (GHz)', fontsize=11)
        if i == 0:
            ax.set_ylabel('Intensity (×10³ counts/sec)', fontsize=11)
        ax.set_title(f'({label}) {title}', fontsize=12)
        ax.set_xlim(-40, 40)
        ax.legend(fontsize=8)
    
    plt.suptitle('Figure 4a-d: CNOT Gate Spectra (ME Simulation)', 
                 fontsize=14, y=1.02)
    plt.tight_layout()
    fig_path = os.path.join(SIM_FIG_DIR, 'Figure4abcd-ME.png')
    plt.savefig(fig_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {fig_path}")
    
    # ══════════════════════════════════════════════════════════════════════
    # FIGURE 4e: PROBABILITY TRUTH TABLE
    # ══════════════════════════════════════════════════════════════════════
    
    # Extract probabilities at cavity resonance (Δ_c = 0)
    idx_0 = np.argmin(np.abs(delta_c))
    
    # Probabilities when QD is in |−⟩ (π-pulse at 80ps)
    # Cross-pol intensities serve as the "ideal" reference
    # P_ab^π = I_ab^π / I_ideal
    # For cross-pol: I_ideal = I_bare at max (no QD interaction)
    
    # At resonance for bare cavity: r = -1
    # W_VH_bare = |r+1|²/4 = 0 (V→H vanishes for bare cavity at resonance)
    
    # Wait, that's wrong. For QD in |−⟩ at resonance: r = -1
    # W_VH = |(-1)+1|²/4 = 0  ← V→H is zero! 
    # W_VV = |(-1)-1|²/4 = 1  ← V→V is maximum!
    
    # For QD in |g⟩ (coupled): r ≈ +0.83
    # W_VH = |0.83+1|²/4 = 0.84  ← V→H large (polarization rotation)
    # W_VV = |0.83-1|²/4 = 0.007 ← V→V small
    
    # CNOT truth: 
    #   |g⟩ + V → H (bit flip):  W_VH large, W_VV small ✓
    #   |−⟩ + V → V (identity):  W_VH zero, W_VV large ✓
    
    # Probability: P_VH = W_VH / (W_VH + W_VV)
    print("\n  Computing probability truth table at resonance...")
    
    # For QD in |g⟩ (4 ns delay)
    P_g = {}
    total_g_H = W_g['HH'][idx_0] + W_g['HV'][idx_0]  # H input total
    total_g_V = W_g['VH'][idx_0] + W_g['VV'][idx_0]  # V input total
    P_g['HH'] = W_g['HH'][idx_0] / total_g_H if total_g_H > 0 else 0
    P_g['HV'] = W_g['HV'][idx_0] / total_g_H if total_g_H > 0 else 0
    P_g['VH'] = W_g['VH'][idx_0] / total_g_V if total_g_V > 0 else 0
    P_g['VV'] = W_g['VV'][idx_0] / total_g_V if total_g_V > 0 else 0
    
    # For QD in |−⟩ (π-pulse at 80 ps)
    P_pi = {}
    total_pi_H = W_pi['HH'][idx_0] + W_pi['HV'][idx_0]
    total_pi_V = W_pi['VH'][idx_0] + W_pi['VV'][idx_0]
    P_pi['HH'] = W_pi['HH'][idx_0] / total_pi_H if total_pi_H > 0 else 0
    P_pi['HV'] = W_pi['HV'][idx_0] / total_pi_H if total_pi_H > 0 else 0
    P_pi['VH'] = W_pi['VH'][idx_0] / total_pi_V if total_pi_V > 0 else 0
    P_pi['VV'] = W_pi['VV'][idx_0] / total_pi_V if total_pi_V > 0 else 0
    
    print(f"\n  QD |g⟩: P_HH={P_g['HH']:.3f}, P_HV={P_g['HV']:.3f}, "
          f"P_VH={P_g['VH']:.3f}, P_VV={P_g['VV']:.3f}")
    print(f"  QD |−⟩: P_HH={P_pi['HH']:.3f}, P_HV={P_pi['HV']:.3f}, "
          f"P_VH={P_pi['VH']:.3f}, P_VV={P_pi['VV']:.3f}")
    
    # Experimental values (from paper Table 1)
    P_exp_g = {'HH': 0.61, 'HV': 0.35, 'VH': 0.38, 'VV': 0.58}
    P_exp_pi = {'HH': 0.07, 'HV': 0.93, 'VH': 0.98, 'VV': 0.10}
    
    # ── Plot probability table ──
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    x = np.arange(4)
    width = 0.35
    keys_order = ['VV', 'VH', 'HV', 'HH']
    xlabels = ['P_VV', 'P_VH', 'P_HV', 'P_HH']
    
    # Panel 1: QD in |−⟩ (π-pulse)
    ax = axes[0]
    vals_sim = [P_pi[k] for k in keys_order]
    vals_exp = [P_exp_pi[k] for k in keys_order]
    
    bars1 = ax.bar(x - width/2, vals_sim, width, label='ME Simulation',
                   color='steelblue', edgecolor='navy', alpha=0.85)
    bars2 = ax.bar(x + width/2, vals_exp, width, label='Experiment',
                   color='coral', edgecolor='darkred', alpha=0.85)
    
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=11)
    ax.set_ylabel('Probability', fontsize=12)
    ax.set_title('QD in |−⟩ (π-pulse)', fontsize=13)
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=10)
    ax.axhline(0.5, color='gray', ls='--', alpha=0.3)
    
    # Add value labels
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.02,
                f'{h:.2f}', ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.02,
                f'{h:.2f}', ha='center', va='bottom', fontsize=9)
    
    # Panel 2: QD in |g⟩ (no pump)
    ax = axes[1]
    vals_sim = [P_g[k] for k in keys_order]
    vals_exp = [P_exp_g[k] for k in keys_order]
    
    bars1 = ax.bar(x - width/2, vals_sim, width, label='ME Simulation',
                   color='steelblue', edgecolor='navy', alpha=0.85)
    bars2 = ax.bar(x + width/2, vals_exp, width, label='Experiment',
                   color='coral', edgecolor='darkred', alpha=0.85)
    
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=11)
    ax.set_ylabel('Probability', fontsize=12)
    ax.set_title('QD in |g⟩ (no pump)', fontsize=13)
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=10)
    ax.axhline(0.5, color='gray', ls='--', alpha=0.3)
    
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.02,
                f'{h:.2f}', ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.02,
                f'{h:.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.suptitle('Figure 4e: CNOT Truth Table (ME Simulation)', 
                 fontsize=14, y=1.02)
    plt.tight_layout()
    fig_path = os.path.join(SIM_FIG_DIR, 'Figure4e-ME.png')
    plt.savefig(fig_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {fig_path}")
    
    return W_coupled, W_bare, P_g, P_pi


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  QuTiP ME Simulation: CNOT Gate                             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    W_coupled, W_bare, P_g, P_pi = figure_4(n_freq=60, n_sd=20)
    
    print("\n" + "=" * 60)
    print("CNOT gate simulation complete.")
    print("=" * 60)
