"""
figure_s4.py — v2 FIXED
============

Fixes in v2:
  - S4b: Added 4th data point at Δ/2π=150 GHz, τ=300 ps (from original figure)  
  - S4b: Re-fitted Purcell parameters with 4 data points
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common_params import g_ghz, kappa_ghz
from cavity_model import purcell_decay_rate, purcell_lifetime_ns


# 4 data points from original figure (paper text mentions 3, but figure shows 4)
S4_DETUNINGS = np.array([113.0, 150.0, 169.0, 230.0])
S4_LIFETIMES_NS = np.array([0.230, 0.300, 0.350, 0.460])
S4_ERRORS_NS = np.array([0.015, 0.025, 0.020, 0.030])


def figure_s4a(ax):
    """Panel (a): Exponential decay curves for three detunings (113, 169, 230 GHz)."""
    detunings = np.array([113.0, 169.0, 230.0])
    lifetimes_ps = np.array([230.0, 350.0, 460.0])
    
    colors = ['green', 'red', 'black']
    markers = ['^', 'o', 's']
    markerfcs = ['green', 'red', 'none']
    labels = [
        r'$\Delta/2\pi=113$ GHz',
        r'$\Delta/2\pi=169$ GHz', 
        r'$\Delta/2\pi=230$ GHz'
    ]
    
    I_base = 0.68
    I_peak = 1.0
    
    for i, (det, tau, color, marker, mfc, label) in enumerate(
            zip(detunings, lifetimes_ps, colors, markers, markerfcs, labels)):
        tau_ns = tau * 1e-3
        
        np.random.seed(42 + i)
        t_data = np.linspace(-0.05, 1.25, 80)
        I_data = np.where(t_data >= 0,
            I_base + (I_peak - I_base) * np.exp(-t_data / tau_ns), I_base)
        noise_data = np.random.normal(0, 0.02, len(t_data))
        
        ax.plot(t_data, I_data + noise_data, marker=marker, color=color,
                markerfacecolor=mfc, markeredgecolor=color,
                linestyle='none', markersize=4, label=label, alpha=0.7)
        
        t_fit = np.linspace(0, 1.3, 300)
        I_fit = I_base + (I_peak - I_base) * np.exp(-t_fit / tau_ns)
        ax.plot(t_fit, I_fit, '-', color=color, linewidth=1.5, alpha=0.8)
    
    ax.set_xlabel('Pump probe delay (ns)', fontsize=12)
    ax.set_ylabel('Intensity (a.u)', fontsize=12)
    ax.set_xlim(-0.1, 1.3)
    ax.set_ylim(0.63, 1.02)
    ax.legend(fontsize=9, loc='upper right')
    ax.text(0.05, 0.95, 'a', transform=ax.transAxes, fontsize=16, 
            fontweight='bold', va='top')
    ax.tick_params(labelsize=10)


def figure_s4b(ax):
    """
    Panel (b): Lifetime vs detuning with 4 data points.
    
    FIX v2: Uses 4 data points and refitted Purcell parameters.
    """
    # Re-fitted Purcell model with 4 points
    from scipy.optimize import curve_fit
    
    def lt_model(delta, A, sigma0):
        B = 15.95
        rate = A / (delta**2 + B**2) + sigma0
        return 1.0 / rate
    
    popt, _ = curve_fit(lt_model, S4_DETUNINGS, S4_LIFETIMES_NS, p0=[40000, 1.4])
    A_fit, s0_fit = popt
    
    delta_range = np.linspace(80, 280, 300)
    lifetime_theory = lt_model(delta_range, A_fit, s0_fit)
    
    ax.plot(delta_range, lifetime_theory, 'k-', linewidth=1.5, label='Fit')
    ax.errorbar(S4_DETUNINGS, S4_LIFETIMES_NS, yerr=S4_ERRORS_NS, fmt='ro',
                markersize=7, capsize=4, label='Measurement', 
                markerfacecolor='red', markeredgecolor='red')
    
    ax.set_xlabel(r'$\Delta/2\pi$ (GHz)', fontsize=12)
    ax.set_ylabel('Lifetime (ns)', fontsize=12)
    ax.set_xlim(80, 270)
    ax.set_ylim(0.15, 0.55)
    ax.legend(fontsize=10, loc='lower right')
    ax.text(0.05, 0.95, 'b', transform=ax.transAxes, fontsize=16,
            fontweight='bold', va='top')
    ax.tick_params(labelsize=10)


def generate_figure_s4():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    figure_s4a(ax1)
    figure_s4b(ax2)
    plt.tight_layout()
    plt.savefig('figures_sim_new-2/Figure-S4-new-2.png', dpi=200, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("Figure S4 saved to figures_sim_new-2/Figure-S4-new-2.png")


if __name__ == "__main__":
    generate_figure_s4()
