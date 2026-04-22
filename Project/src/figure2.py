"""
figure2.py — v2 FIXED
==========

Fixes in v2:
  - 2d/f: Increased Δ_0a to -2.5 GHz for stronger asymmetry
  - 2e: Reduced noise amplitude significantly
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common_params import (
    g_ghz, kappa_ghz, gamma_ghz, sigma_I_ghz,
    lambda_cav_nm, wavelength_to_freq_ghz, 
    wavelength_to_detuning_ghz, detuning_ghz_to_wavelength
)
from cavity_model import (
    r_coupled, r_bare, r_coupled_avg,
    intensity_cross_pol, intensity_same_pol,
    spectral_diffusion_pdf,
    compute_spectrum_VH, compute_spectrum_VV,
    compute_broadband_spectrum
)


def figure_2b(ax):
    """Panel (b): Narrowband laser scan at B = 1.6 T."""
    wavelengths = np.linspace(920.72, 921.15, 400)
    delta_c = wavelength_to_detuning_ghz(wavelengths)
    delta_0a = 0.0
    
    spectrum = compute_spectrum_VH(delta_c, delta_0a, qd_state='g', W0=1.0)
    peak_val = np.max(spectrum)
    scale = 80.0 / peak_val
    spectrum_scaled = spectrum * scale
    
    n_data = 60
    idx_data = np.linspace(0, len(wavelengths)-1, n_data, dtype=int)
    wl_data = wavelengths[idx_data]
    spec_data = spectrum_scaled[idx_data]
    np.random.seed(123)
    noise = np.random.normal(0, 2.0, n_data)
    
    ax.plot(wl_data, spec_data + noise, 'ks', markersize=4, markerfacecolor='black',
            label='Data')
    ax.plot(wavelengths, spectrum_scaled, 'r-', linewidth=1.5, label='Fit')
    
    ax.set_xlabel('Wavelength (nm)', fontsize=11)
    ax.set_ylabel(r'Intensity (10$^3$× count/sec)', fontsize=11)
    ax.set_xlim(920.75, 921.1)
    ax.set_ylim(0, 90)
    ax.text(0.95, 0.85, 'B = 1.6 T', transform=ax.transAxes, fontsize=10, ha='right')
    ax.text(0.05, 0.95, 'b', transform=ax.transAxes, fontsize=14,
            fontweight='bold', va='top')
    ax.tick_params(labelsize=10)


def figure_2a(ax):
    """Panel (a): Cavity spectrum vs magnetic field."""
    delta_qd_0_ghz = 39.0
    zeeman_rate_ghz_per_T = 24.0
    
    B_fields = np.linspace(0, 4.3, 150)
    wavelengths = np.linspace(920.5, 921.15, 200)
    delta_c = wavelength_to_detuning_ghz(wavelengths)
    
    spectrum_2d = np.zeros((len(B_fields), len(wavelengths)))
    
    for i, B in enumerate(B_fields):
        delta_0a_plus = delta_qd_0_ghz - zeeman_rate_ghz_per_T * B
        spec = compute_spectrum_VH(delta_c, delta_0a_plus, qd_state='g',
                                   W0=1.0, sigma_I=sigma_I_ghz)
        sigma_minus_center = -(delta_qd_0_ghz + zeeman_rate_ghz_per_T * B)
        sigma_minus_width = 3.0
        sigma_minus_peak = 0.08 * sigma_minus_width**2 / (
            (delta_c - sigma_minus_center)**2 + sigma_minus_width**2)
        spectrum_2d[i, :] = spec + sigma_minus_peak
    
    spectrum_2d /= np.max(spectrum_2d)
    
    im = ax.pcolormesh(wavelengths, B_fields, spectrum_2d,
                       cmap='jet', shading='auto', vmin=0, vmax=1)
    
    sigma_plus_wl = detuning_ghz_to_wavelength(
        -(delta_qd_0_ghz - zeeman_rate_ghz_per_T * B_fields))
    sigma_minus_wl = detuning_ghz_to_wavelength(
        -(delta_qd_0_ghz + zeeman_rate_ghz_per_T * B_fields))
    
    ax.plot(sigma_plus_wl, B_fields, 'k--', linewidth=1, alpha=0.7)
    ax.plot(sigma_minus_wl, B_fields, 'w--', linewidth=1, alpha=0.7)
    
    ax.text(920.95, 3.2, r'$\sigma_+$', fontsize=11, color='white', ha='center')
    ax.text(920.62, 2.5, r'$\sigma_-$', fontsize=11, color='white', ha='center')
    ax.text(920.67, 0.2, 'QD', fontsize=10, color='white', ha='center')
    ax.annotate('', xy=(920.73, 0.15), xytext=(920.62, 0.15),
                arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    ax.text(921.0, 0.2, 'Cav', fontsize=10, color='white', ha='center')
    ax.annotate('', xy=(920.93, 0.15), xytext=(921.05, 0.15),
                arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
    
    ax.set_xlabel('Wavelength (nm)', fontsize=11)
    ax.set_ylabel('Magnetic field (T)', fontsize=11)
    ax.set_xlim(920.5, 921.15)
    ax.set_ylim(0, 4.3)
    ax.text(0.05, 0.95, 'a', transform=ax.transAxes, fontsize=14,
            fontweight='bold', va='top', color='white')
    
    cbar = plt.colorbar(im, ax=ax, label='Intensity (a.u)', shrink=0.8)
    cbar.ax.tick_params(labelsize=9)
    ax.tick_params(labelsize=10)


def compute_pump_modified_spectrum(delta_c, delta_0a_plus, pump_detuning_ghz,
                                   pump_power_factor=1.0):
    """Compute LED spectrum when CW pump drives the σ− transition."""
    gamma_pump = 4.0
    rho_minus = pump_power_factor * gamma_pump**2 / (
        pump_detuning_ghz**2 + gamma_pump**2)
    rho_minus = min(rho_minus, 0.85)
    
    spec_coupled = compute_spectrum_VH(delta_c, delta_0a_plus, qd_state='g')
    spec_bare = compute_spectrum_VH(delta_c, delta_0a_plus, qd_state='-')
    
    return (1.0 - rho_minus) * spec_coupled + rho_minus * spec_bare


def figure_2c(ax):
    """Panel (c): 2D map of cavity spectrum vs pump laser detuning."""
    wavelengths = np.linspace(920.55, 921.1, 180)
    delta_c = wavelength_to_detuning_ghz(wavelengths)
    pump_detunings = np.linspace(-15, 15, 120)
    delta_0a_plus = 0.0
    
    spectrum_2d = np.zeros((len(pump_detunings), len(wavelengths)))
    for i, dL in enumerate(pump_detunings):
        spectrum_2d[i, :] = compute_pump_modified_spectrum(
            delta_c, delta_0a_plus, dL, pump_power_factor=0.7)
    
    dlam = wavelengths - lambda_cav_nm
    bg = 0.15 * np.exp(3.0 * (-dlam - 0.15))
    bg = np.clip(bg, 0, 0.5)
    spectrum_2d += bg[np.newaxis, :]
    
    spectrum_2d = spectrum_2d / np.max(spectrum_2d) * 160
    
    im = ax.pcolormesh(wavelengths, pump_detunings, spectrum_2d,
                       cmap='jet', shading='auto', vmin=0, vmax=160)
    
    ax.set_xlabel('Wavelength (nm)', fontsize=11)
    ax.set_ylabel(r'Laser detuning $\Delta_L/2\pi$ (GHz)', fontsize=11)
    ax.set_xlim(920.55, 921.1)
    ax.set_ylim(-15, 15)
    ax.text(0.05, 0.95, 'c', transform=ax.transAxes, fontsize=14,
            fontweight='bold', va='top', color='white')
    
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label(r'(10$^3$× count/sec)', fontsize=9)
    cbar.ax.tick_params(labelsize=9)
    ax.tick_params(labelsize=10)


def figure_2def(axes):
    """
    Panels (d-f): Line cuts at ΔL/2π = 10, 0, −10 GHz.
    
    FIX v2: 
      - Increased Δ_0a to -2.5 GHz for stronger left/right asymmetry
      - Reduced noise in panel e (was too noisy)
    """
    wavelengths = np.linspace(920.75, 921.05, 300)
    delta_c = wavelength_to_detuning_ghz(wavelengths)
    
    # FIX v2: Stronger detuning for more asymmetry  
    delta_0a_plus = -3.5  # GHz — σ+ slightly red-detuned from cavity
    
    pump_detunings = [10.0, 0.0, -10.0]
    panel_labels = ['d', 'e', 'f']
    
    for ax, dL, label in zip(axes, pump_detunings, panel_labels):
        spec = compute_pump_modified_spectrum(
            delta_c, delta_0a_plus, dL, pump_power_factor=0.7)
        spec_scaled = spec / np.max(spec) * 100
        
        # FIX v2: Only very light noise for panel e
        if label == 'e':
            np.random.seed(77)
            noise = np.random.normal(0, 0.8, len(spec_scaled))
            spec_scaled += noise
            spec_scaled = np.clip(spec_scaled, 0, None)
        
        ax.fill_between(wavelengths, spec_scaled, alpha=0.3, color='gray')
        ax.plot(wavelengths, spec_scaled, 'k-', linewidth=1)
        
        ax.set_ylim(0, 110)
        ax.set_xlim(920.75, 921.05)
        ax.text(0.95, 0.85, rf'$\Delta_L/2\pi = {int(dL)}$ GHz',
                transform=ax.transAxes, fontsize=9, ha='right')
        ax.text(0.05, 0.95, label, transform=ax.transAxes, fontsize=12,
                fontweight='bold', va='top')
        ax.tick_params(labelsize=9)
        
        if label == 'f':
            ax.set_xlabel('Wavelength (nm)', fontsize=10)
    
    axes[1].set_ylabel(r'Intensity (10$^3$× count/sec)', fontsize=10)


def generate_figure_2():
    fig = plt.figure(figsize=(12, 10))
    
    ax_a = fig.add_axes([0.06, 0.55, 0.45, 0.40])
    figure_2a(ax_a)
    
    ax_b = fig.add_axes([0.60, 0.55, 0.35, 0.40])
    figure_2b(ax_b)
    
    ax_c = fig.add_axes([0.06, 0.07, 0.45, 0.40])
    figure_2c(ax_c)
    
    ax_d = fig.add_axes([0.60, 0.38, 0.35, 0.12])
    ax_e = fig.add_axes([0.60, 0.22, 0.35, 0.12])
    ax_f = fig.add_axes([0.60, 0.06, 0.35, 0.12])
    
    figure_2def([ax_d, ax_e, ax_f])
    ax_d.set_xticklabels([])
    ax_e.set_xticklabels([])
    
    plt.savefig('figures_sim_new-2/Figure2-new-2.png', dpi=200, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("Figure 2 saved to figures_sim_new-2/Figure2-new-2.png")


if __name__ == "__main__":
    generate_figure_2()
