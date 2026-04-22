"""
common_params.py
================

Shared physical parameters and constants for the QD-photon cNOT gate simulation.

All parameters are extracted from Kim et al., Nature Photonics (2013):
"A quantum logic gate between a solid-state quantum bit and a photon"

Convention:
-----------
  - All angular frequencies are in units of 2π·GHz (i.e., we store values as GHz
    and multiply by 2π where needed in the equations).
  - Energies/frequencies labelled with _ghz suffix are in GHz (frequency, not angular).
  - The reflection coefficient equations use angular frequency differences (Δ), but
    since all terms are ratios, we can work directly in GHz (the 2π cancels).

References:
-----------
  [1] Main text, p.4: g/2π = 12.9 GHz, κ/2π = 31.9 GHz
  [2] Supplementary Section 3: σ_I/2π = 5.2 GHz
  [3] Supplementary Section 4: γ_spon = 1/530 ps → γ = γ_spon/2
  [4] Main text, p.5: probe bandwidth = 4.2 GHz
  [5] Methods: laser repetition rate = 76 MHz
"""

import numpy as np

# ==============================================================================
# Fundamental Constants
# ==============================================================================
c_light = 2.998e8          # Speed of light (m/s)
hbar = 1.0546e-34          # Reduced Planck constant (J·s)

# ==============================================================================
# Cavity-QD System Parameters (in GHz, i.e., frequency / 2π)
# ==============================================================================

# QD-cavity coupling strength  [Ref: main text p.4, Supp. Sec. 3]
g_ghz = 12.9               # g / 2π in GHz

# Cavity energy decay rate  [Ref: main text p.4]
kappa_ghz = 31.9            # κ / 2π in GHz
Q_factor = 10200            # Cavity quality factor

# QD spontaneous emission rate  [Ref: Supp. Sec. 4]
# γ_spon = 1/530 ps.  γ = γ_spon / 2 (half the spontaneous emission rate
# is used as the QD linewidth parameter in the Heisenberg-Langevin equations)
tau_spon_ps = 530.0                            # Spontaneous emission lifetime (ps)
gamma_spon_ghz = 1.0 / (tau_spon_ps * 1e-3)   # γ_spon in GHz = 1/(530e-3 ns) ≈ 1.887 GHz
gamma_ghz = gamma_spon_ghz / 2.0              # γ / 2π in GHz ≈ 0.943 GHz

# Inhomogeneous linewidth (spectral diffusion)  [Ref: Supp. Sec. 3]
sigma_I_ghz = 5.2           # σ_I / 2π in GHz

# ==============================================================================
# Optical Parameters
# ==============================================================================

# Cavity resonance wavelength  [Ref: Fig. 2b, center between two peaks]
lambda_cav_nm = 920.93      # Cavity resonance wavelength (nm)

# Frequency of cavity resonance
nu_cav_ghz = c_light / (lambda_cav_nm * 1e-9) * 1e-9  # in GHz ≈ 325,700 GHz

# QD σ+ transition: on resonance with cavity at B = 1.6 T
# So Δ_0a = ω_QD - ω_cav = 0 at B = 1.6 T for Fig. 2b

# σ− transition operating wavelength for CNOT (from Fig. 4 blue line)
lambda_qd_minus_nm = 920.96  # |−⟩ transition wavelength used for probability calc

# ==============================================================================
# Experimental Parameters
# ==============================================================================

# Probe pulse bandwidth  [Ref: main text p.5]
probe_bandwidth_ghz = 4.2   # Probe laser bandwidth (GHz)

# Laser repetition rate  [Ref: Methods]
rep_rate_mhz = 76.0         # Laser repetition rate (MHz)
T_rep_ns = 1e3 / rep_rate_mhz  # Repetition period ≈ 13.16 ns

# Pump-probe delay settings  [Ref: main text p.5]
delay_short_ps = 80.0       # Short delay (QD in |−⟩ state)
delay_long_ns = 4.0         # Long delay (QD relaxed to |g⟩)

# Pump pulse duration  [Ref: Methods]
pump_pulse_ps = 10.0        # Pump pulse duration (ps)
probe_pulse_ps = 75.0       # Probe pulse duration (ps)

# π-pulse power  [Ref: main text p.5]
P_pi_uW = 0.12              # π-pulse average power (µW)

# Probability of QD excitation after π-pulse  [Ref: Supp. Sec. 5]
rho_pi = 0.93               # Probability of |−⟩ occupation after π-pulse

# ==============================================================================
# Purcell Lifetime Parameters  [Ref: Supp. Sec. 4]
# ==============================================================================

# Nonradiative + leaky mode decay rate
sigma_0_ghz = 1.0 / (tau_spon_ps * 1e-3)  # σ_0 = 1/530 ps in GHz

# Measured detunings and lifetimes for S4
# Detuning Δ/2π (GHz) → Lifetime 1/σ_− (ps)
s4_detunings_ghz = np.array([113.0, 169.0, 230.0])
s4_lifetimes_ps = np.array([230.0, 350.0, 460.0])

# ==============================================================================
# Atomic Cooperativity
# ==============================================================================

# C = 2g² / (κγ)  [Ref: main text p.3]
C = 2.0 * g_ghz**2 / (kappa_ghz * gamma_ghz)
# Expected: C = 2 * 12.9² / (31.9 * 0.943) ≈ 11.1

# ==============================================================================
# Derived: QD-cavity frequency conversion wavelength ↔ frequency
# ==============================================================================

def wavelength_to_freq_ghz(lam_nm):
    """Convert wavelength (nm) to frequency (GHz)."""
    return c_light / (lam_nm * 1e-9) * 1e-9

def freq_ghz_to_wavelength(nu_ghz):
    """Convert frequency (GHz) to wavelength (nm)."""
    return c_light / (nu_ghz * 1e9) * 1e9

def wavelength_to_detuning_ghz(lam_nm, lam_ref_nm=None):
    """
    Convert wavelength (nm) to detuning from cavity resonance (GHz).
    
    Detuning Δ = ω_ref - ω = 2π(ν_ref - ν)
    Positive detuning means the reference is at higher frequency (shorter wavelength).
    
    Parameters
    ----------
    lam_nm : array-like
        Wavelengths to convert (nm)
    lam_ref_nm : float, optional
        Reference wavelength. Defaults to cavity resonance.
    
    Returns
    -------
    detuning_ghz : array-like
        Detuning in GHz
    """
    if lam_ref_nm is None:
        lam_ref_nm = lambda_cav_nm
    nu = wavelength_to_freq_ghz(np.asarray(lam_nm))
    nu_ref = wavelength_to_freq_ghz(lam_ref_nm)
    return nu_ref - nu  # Positive when lam > lam_ref (red-detuned)

def detuning_ghz_to_wavelength(delta_ghz, lam_ref_nm=None):
    """
    Convert detuning (GHz) to wavelength (nm).
    
    Parameters
    ----------
    delta_ghz : array-like
        Detuning in GHz (positive = red-detuned from reference)
    lam_ref_nm : float, optional
        Reference wavelength. Defaults to cavity resonance.
    
    Returns
    -------
    lam_nm : array-like
        Wavelengths in nm
    """
    if lam_ref_nm is None:
        lam_ref_nm = lambda_cav_nm
    nu_ref = wavelength_to_freq_ghz(lam_ref_nm)
    nu = nu_ref - np.asarray(delta_ghz)
    return freq_ghz_to_wavelength(nu)


if __name__ == "__main__":
    print("=== QD-Photon cNOT Gate: System Parameters ===")
    print(f"  g/2π = {g_ghz} GHz")
    print(f"  κ/2π = {kappa_ghz} GHz")
    print(f"  γ/2π = {gamma_ghz:.3f} GHz")
    print(f"  σ_I/2π = {sigma_I_ghz} GHz")
    print(f"  Cooperativity C = {C:.1f}")
    print(f"  λ_cav = {lambda_cav_nm} nm")
    print(f"  ν_cav = {nu_cav_ghz:.1f} GHz")
    print(f"  Strong coupling: g > κ/4 ? {g_ghz > kappa_ghz/4}")
    print(f"  Ideal |g⟩ reflectivity: r = (C-1)/(C+1) = {(C-1)/(C+1):.3f}")
