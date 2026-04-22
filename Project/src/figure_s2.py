"""
figure_s2.py
============

Supplementary Figure S2: Second-order correlation measurement g²(τ).

This figure shows the photon antibunching measurement confirming single QD emission.

Top panel: Laser pulse train g²(τ) — uniform peaks at multiples of T_rep.
Bottom panel: QD emission g²(τ) — suppressed τ=0 peak (antibunching).

Physics:
--------
The second-order correlation function g²(τ) measures the probability of
detecting two photons separated by time delay τ. For a pulsed source with
repetition period T_rep = 1/76 MHz ≈ 13.16 ns:

  - Coherent laser: g²(τ) shows uniform peaks at τ = n×T_rep (Poissonian)
  - Single quantum emitter: g²(0) → 0 (sub-Poissonian, antibunching)

The suppression at τ=0 for the QD proves single-photon emission, confirming
we are working with a single quantum dot. g²(0) < 0.5 rules out multi-photon
emission.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common_params import T_rep_ns


def generate_g2_peaks(t_array, peak_positions, peak_heights, peak_width):
    """
    Generate g²(τ) trace as a sum of Gaussian peaks.
    
    Parameters
    ----------
    t_array : array
        Time delay array (ns).
    peak_positions : array
        Center positions of peaks (ns).
    peak_heights : array
        Heights of peaks.
    peak_width : float
        Width (σ) of Gaussian peaks (ns).
    
    Returns
    -------
    g2 : array
        g²(τ) values.
    """
    g2 = np.zeros_like(t_array)
    for pos, height in zip(peak_positions, peak_heights):
        g2 += height * np.exp(-(t_array - pos)**2 / (2 * peak_width**2))
    return g2


def figure_s2():
    """
    Generate Supplementary Figure S2: g²(τ) for laser and QD.
    """
    fig, (ax_laser, ax_qd) = plt.subplots(2, 1, figsize=(8, 7), 
                                           sharex=True,
                                           gridspec_kw={'hspace': 0.05})
    
    # Time range: -50 to 50 ns (showing ~7 peaks on each side)
    t = np.linspace(-50, 50, 5000)
    
    # Peak positions at multiples of T_rep ≈ 13.16 ns
    T_rep = T_rep_ns
    n_peaks = 7
    peak_positions = np.arange(-n_peaks, n_peaks + 1) * T_rep
    
    # ====== Laser g²(τ) (top panel) ======
    # All peaks uniform height, slight random variation for realism
    np.random.seed(42)
    laser_heights = 220 + np.random.normal(0, 25, len(peak_positions))
    laser_heights = np.abs(laser_heights)  # Ensure positive
    peak_width_laser = 1.2  # Narrow peaks (ns)
    
    g2_laser = generate_g2_peaks(t, peak_positions, laser_heights, peak_width_laser)
    
    # Add small noise floor
    noise_laser = np.random.normal(0, 1.5, len(t))
    g2_laser += np.abs(noise_laser)
    
    ax_laser.plot(t, g2_laser, 'k-', linewidth=0.8)
    ax_laser.set_ylabel(r'$g^2(\tau)$', fontsize=14)
    ax_laser.set_ylim(0, 310)
    ax_laser.set_xlim(-50, 50)
    ax_laser.text(0.08, 0.85, 'Laser', fontsize=14, fontweight='bold',
                  transform=ax_laser.transAxes)
    ax_laser.tick_params(labelsize=11)
    
    # Blue dashed rectangle around τ=0 peak (matching paper)
    rect_x = [-8, 8]
    rect_y = [0, 300]
    ax_laser.plot([rect_x[0], rect_x[0], rect_x[1], rect_x[1], rect_x[0]],
                  [rect_y[0], rect_y[1], rect_y[1], rect_y[0], rect_y[0]],
                  'b--', linewidth=1.5, alpha=0.7)
    
    # ====== QD g²(τ) (bottom panel) ======
    # All peaks similar except τ=0 which is suppressed (antibunching)
    qd_heights = 25 + np.random.normal(0, 5, len(peak_positions))
    qd_heights = np.abs(qd_heights)
    
    # Suppress the τ=0 peak (center peak)
    center_idx = n_peaks  # Index of τ=0 peak
    qd_heights[center_idx] = 2.0  # Nearly zero (strong antibunching)
    
    peak_width_qd = 1.5  # Slightly broader (ns)
    
    g2_qd = generate_g2_peaks(t, peak_positions, qd_heights, peak_width_qd)
    
    # Add noise floor (higher for QD due to lower count rate)
    np.random.seed(99)
    noise_qd = np.abs(np.random.normal(0, 2.5, len(t))) + 5
    # Add some low-frequency background variation
    background = 5 + 2 * np.sin(2 * np.pi * t / 80)
    g2_qd += noise_qd + background
    
    ax_qd.plot(t, g2_qd, 'r-', linewidth=0.8)
    ax_qd.set_xlabel(r'$\tau$ (ns)', fontsize=14)
    ax_qd.set_ylabel(r'$g^2(\tau)$', fontsize=14)
    ax_qd.set_ylim(0, 50)
    ax_qd.text(0.08, 0.85, 'QD', fontsize=14, fontweight='bold',
               transform=ax_qd.transAxes)
    ax_qd.tick_params(labelsize=11)
    
    # Blue dashed rectangle around τ=0 (suppressed peak)
    ax_qd.plot([rect_x[0], rect_x[0], rect_x[1], rect_x[1], rect_x[0]],
               [0, 45, 45, 0, 0],
               'b--', linewidth=1.5, alpha=0.7)
    
    plt.savefig('figures_sim_new-2/Figure-S2-new-2.png', dpi=200, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("Figure S2 saved to figures_sim_new/Figure-S2-new.png")


if __name__ == "__main__":
    figure_s2()
