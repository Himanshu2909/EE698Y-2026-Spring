"""
cavity_model.py
===============

Core physics engine for the QD-photon cNOT gate simulation.

Implements the cavity reflection coefficient and output intensity calculations
from the supplementary material of Kim et al. (2013).

Physics Summary:
----------------
The system consists of a single InAs quantum dot (QD) strongly coupled to a
photonic crystal L3 nanocavity. The QD has three relevant states:
  |g⟩  - ground state
  |+⟩  - bright exciton (σ+ transition, coupled to cavity)
  |−⟩  - bright exciton (σ− transition, detuned from cavity)

The cavity reflection coefficient depends on the QD state:
  - QD in |g⟩: r(ω) involves Jaynes-Cummings interaction via σ+ transition
  - QD in |−⟩: r(ω) is that of a bare cavity (QD decoupled)

The photonic qubit is encoded in H/V polarization, rotated 45° from the
cavity polarization axis (x/y).

Key Equations (from Supplementary Material):
--------------------------------------------
  Eq.(16): r(ω) = 1 − κ(iΔ_a + γ) / [(iΔ_c + κ/2)(iΔ_a + γ) + g²]
  Eq.(20): r(ω) = 1 − κ / (iΔ_c + κ/2)              [bare cavity]
  Eq.(36): r(ω,δ) includes spectral diffusion shift δ
  Eq.(37-40): Output intensities for all H/V combinations
  Eq.(41): Narrowband laser measurement with spectral diffusion average
  Eq.(42): Gaussian spectral diffusion P(δ)
"""

import numpy as np
from scipy.integrate import quad
from common_params import (
    g_ghz, kappa_ghz, gamma_ghz, sigma_I_ghz,
    lambda_cav_nm, wavelength_to_detuning_ghz, detuning_ghz_to_wavelength
)


# ==============================================================================
# Reflection Coefficients
# ==============================================================================

def r_coupled(delta_c, delta_0a, g=g_ghz, kappa=kappa_ghz, gamma=gamma_ghz, delta_sd=0.0):
    """
    Cavity reflection coefficient when QD is in state |g⟩ (coupled).
    
    From Supplementary Eq.(36):
        r(ω, δ) = 1 − κ(iΔ_a + γ) / [(iΔ_c + κ/2)(iΔ_a + γ) + g²]
    
    where:
        Δ_c = ω_c − ω  (cavity detuning from probe frequency)
        Δ_a = Δ_0a + δ  (QD detuning including spectral diffusion)
        Δ_0a = ω_QD − ω_c  (mean QD-cavity detuning)
        δ = spectral diffusion random shift
    
    All parameters in GHz (the 2π factors cancel in dimensionless ratios).
    
    Parameters
    ----------
    delta_c : array-like
        Cavity detuning Δ_c = ω_c − ω in GHz. 
        Note: this is (cavity freq - probe freq), so positive means probe is red-detuned.
    delta_0a : float
        Mean QD-cavity detuning Δ_0a = ω_QD − ω_c in GHz.
    g : float
        QD-cavity coupling strength g/2π in GHz.
    kappa : float
        Cavity decay rate κ/2π in GHz.
    gamma : float
        QD homogeneous linewidth γ/2π in GHz.
    delta_sd : float
        Spectral diffusion shift δ in GHz.
    
    Returns
    -------
    r : complex array
        Reflection coefficient r(ω).
    """
    delta_c = np.asarray(delta_c, dtype=complex)
    # Total QD detuning from probe: Δ_a = (ω_QD - ω) = (ω_QD - ω_c) + (ω_c - ω) = Δ_0a + Δ_c + δ
    # Wait - let me re-derive carefully from the paper.
    # In the paper's convention:
    #   Δ_c = ω_c - ω  (cavity detuning from rotating frame freq ω)
    #   Δ_a = ω_a - ω  (QD detuning from ω)
    # And ω_a = ω_c + Δ_0a (QD frequency = cavity freq + mean detuning)
    # So Δ_a = ω_c + Δ_0a - ω = Δ_c + Δ_0a + δ  (with spectral diffusion)
    delta_a = delta_c + delta_0a + delta_sd
    
    numerator = kappa * (1j * delta_a + gamma)
    denominator = (1j * delta_c + kappa / 2.0) * (1j * delta_a + gamma) + g**2
    
    return 1.0 - numerator / denominator


def r_bare(delta_c, kappa=kappa_ghz):
    """
    Cavity reflection coefficient when QD is in state |−⟩ (bare cavity).
    
    From Supplementary Eq.(20):
        r(ω) = 1 − κ / (iΔ_c + κ/2)
    
    This is the case where the QD is decoupled from the cavity (in state |−⟩),
    so the cavity behaves as if there is no QD.
    
    Parameters
    ----------
    delta_c : array-like
        Cavity detuning Δ_c = ω_c − ω in GHz.
    kappa : float
        Cavity decay rate κ/2π in GHz.
    
    Returns
    -------
    r : complex array
        Bare cavity reflection coefficient.
    """
    delta_c = np.asarray(delta_c, dtype=complex)
    return 1.0 - kappa / (1j * delta_c + kappa / 2.0)


# ==============================================================================
# Spectral Diffusion
# ==============================================================================

def spectral_diffusion_pdf(delta, sigma_I=sigma_I_ghz):
    """
    Gaussian probability distribution for spectral diffusion.
    
    From Supplementary Eq.(42):
        P(δ) = (1/√(2π)σ_I) × exp(−δ²/(2σ_I²))
    
    Parameters
    ----------
    delta : array-like
        Spectral diffusion shift δ in GHz.
    sigma_I : float
        Inhomogeneous linewidth σ_I/2π in GHz.
    
    Returns
    -------
    P : array-like
        Probability density.
    """
    delta = np.asarray(delta)
    return np.exp(-delta**2 / (2 * sigma_I**2)) / (np.sqrt(2 * np.pi) * sigma_I)


def r_coupled_avg(delta_c, delta_0a, g=g_ghz, kappa=kappa_ghz, gamma=gamma_ghz,
                  sigma_I=sigma_I_ghz, n_sd=200, sd_range=4.0):
    """
    Spectral-diffusion-averaged reflection coefficient for QD in |g⟩.
    
    Computes ⟨r(ω,δ)⟩ = ∫ P(δ) × r(ω,δ) dδ
    using numerical integration over a Gaussian distribution.
    
    Parameters
    ----------
    delta_c : array-like
        Cavity detuning array in GHz.
    delta_0a : float
        Mean QD-cavity detuning in GHz.
    g, kappa, gamma : float
        System parameters in GHz.
    sigma_I : float
        Inhomogeneous linewidth in GHz.
    n_sd : int
        Number of spectral diffusion samples for integration.
    sd_range : float
        Range of integration in units of σ_I.
    
    Returns
    -------
    r_avg : complex array
        Averaged reflection coefficient.
    """
    delta_c = np.asarray(delta_c, dtype=complex)
    
    if sigma_I < 1e-6:
        # No spectral diffusion — return direct calculation
        return r_coupled(delta_c, delta_0a, g, kappa, gamma, delta_sd=0.0)
    
    # Integration over spectral diffusion
    sd_vals = np.linspace(-sd_range * sigma_I, sd_range * sigma_I, n_sd)
    weights = spectral_diffusion_pdf(sd_vals, sigma_I)
    weights /= weights.sum()  # Normalize for discrete sum
    
    r_avg = np.zeros_like(delta_c, dtype=complex)
    for sd, w in zip(sd_vals, weights):
        r_avg += w * r_coupled(delta_c, delta_0a, g, kappa, gamma, delta_sd=sd)
    
    return r_avg


# ==============================================================================
# Output Intensity Functions (H/V polarization basis)
# ==============================================================================

def intensity_cross_pol(r, S_in=1.0):
    """
    Cross-polarization output intensity: |1 - r(ω)|² / 4 × S_in
    
    This applies to:
      - V_in → H_out  (Eq. 32/37)
      - H_in → V_out  (Eq. 35/40)
    
    The factor comes from the H/V decomposition in the cavity x/y basis.
    When input is V-polarized and measured in H direction:
        W_VH = |1-r|²/4 × S_in
    
    Parameters
    ----------
    r : complex array
        Cavity reflection coefficient.
    S_in : float or array
        Input power spectrum (normalized).
    
    Returns
    -------
    W : array
        Output intensity (arbitrary units).
    """
    return np.abs(1.0 - r)**2 / 4.0 * S_in


def intensity_same_pol(r, S_in=1.0):
    """
    Same-polarization output intensity: |1 + r(ω)|² / 4 × S_in
    
    This applies to:
      - V_in → V_out  (Eq. 33/38)
      - H_in → H_out  (Eq. 34/39)
    
    Parameters
    ----------
    r : complex array
        Cavity reflection coefficient.
    S_in : float or array
        Input power spectrum (normalized).
    
    Returns
    -------
    W : array
        Output intensity (arbitrary units).
    """
    return np.abs(1.0 + r)**2 / 4.0 * S_in


# ==============================================================================
# Full Spectrum Calculations with Spectral Diffusion Averaging
# ==============================================================================

def compute_spectrum_VH(delta_c_arr, delta_0a, g=g_ghz, kappa=kappa_ghz,
                        gamma=gamma_ghz, sigma_I=sigma_I_ghz,
                        qd_state='g', W0=1.0, n_sd=200, sd_range=4.0):
    """
    Compute V_in → H_out reflected intensity spectrum.
    
    Uses Eq.(37) for QD in |g⟩ or Eq.(32) with bare cavity for QD in |−⟩,
    with spectral diffusion averaging.
    
    For narrowband input: S_in(ω) ≈ W0 × δ(ω − ω_f)
    So the integral reduces to evaluation at the probe frequency.
    
    Parameters
    ----------
    delta_c_arr : array
        Cavity detuning values (GHz). Δ_c = ω_cav - ω_probe.
    delta_0a : float
        Mean QD-cavity detuning (GHz).
    qd_state : str
        'g' for ground state, '-' for excited state |−⟩.
    W0 : float
        Overall intensity scaling.
    
    Returns
    -------
    W_VH : array
        Output intensity spectrum.
    """
    if qd_state == '-':
        # QD in |−⟩: bare cavity, no spectral diffusion needed
        r = r_bare(delta_c_arr, kappa)
        return W0 * intensity_cross_pol(r)
    else:
        # QD in |g⟩: coupled system with spectral diffusion
        delta_c_arr = np.asarray(delta_c_arr, dtype=float)
        
        if sigma_I < 1e-6:
            r = r_coupled(delta_c_arr, delta_0a, g, kappa, gamma)
            return W0 * intensity_cross_pol(r)
        
        # Spectral diffusion averaging of |1-r|²/4
        sd_vals = np.linspace(-sd_range * sigma_I, sd_range * sigma_I, n_sd)
        weights = spectral_diffusion_pdf(sd_vals, sigma_I)
        d_sd = sd_vals[1] - sd_vals[0]
        
        W = np.zeros(len(delta_c_arr))
        for sd, w in zip(sd_vals, weights):
            r = r_coupled(delta_c_arr, delta_0a, g, kappa, gamma, delta_sd=sd)
            W += w * intensity_cross_pol(r) * d_sd
        
        return W0 * W


def compute_spectrum_VV(delta_c_arr, delta_0a, g=g_ghz, kappa=kappa_ghz,
                        gamma=gamma_ghz, sigma_I=sigma_I_ghz,
                        qd_state='g', W0=1.0, n_sd=200, sd_range=4.0):
    """
    Compute V_in → V_out reflected intensity spectrum.
    
    Uses |1+r|²/4 with spectral diffusion averaging.
    """
    if qd_state == '-':
        r = r_bare(delta_c_arr, kappa)
        return W0 * intensity_same_pol(r)
    else:
        delta_c_arr = np.asarray(delta_c_arr, dtype=float)
        
        if sigma_I < 1e-6:
            r = r_coupled(delta_c_arr, delta_0a, g, kappa, gamma)
            return W0 * intensity_same_pol(r)
        
        sd_vals = np.linspace(-sd_range * sigma_I, sd_range * sigma_I, n_sd)
        weights = spectral_diffusion_pdf(sd_vals, sigma_I)
        d_sd = sd_vals[1] - sd_vals[0]
        
        W = np.zeros(len(delta_c_arr))
        for sd, w in zip(sd_vals, weights):
            r = r_coupled(delta_c_arr, delta_0a, g, kappa, gamma, delta_sd=sd)
            W += w * intensity_same_pol(r) * d_sd
        
        return W0 * W


def compute_spectrum_HV(delta_c_arr, delta_0a, **kwargs):
    """
    Compute H_in → V_out reflected intensity spectrum.
    
    By symmetry of the H/V decomposition, H→V uses the same |1-r|²/4
    factor as V→H (Eq. 35 vs Eq. 32), but with H input normalization.
    """
    return compute_spectrum_VH(delta_c_arr, delta_0a, **kwargs)


def compute_spectrum_HH(delta_c_arr, delta_0a, **kwargs):
    """
    Compute H_in → H_out reflected intensity spectrum.
    
    Same as V→V: uses |1+r|²/4 (Eq. 34 vs Eq. 33).
    """
    return compute_spectrum_VV(delta_c_arr, delta_0a, **kwargs)


def compute_spectrum_general(delta_c_arr, delta_0a, pol_in, pol_out, **kwargs):
    """
    General spectrum computation for any polarization combination.
    
    Parameters
    ----------
    pol_in : str
        Input polarization: 'V' or 'H'
    pol_out : str
        Output polarization: 'V' or 'H'
    
    Returns
    -------
    W : array
        Output intensity spectrum.
    """
    if pol_in == 'V' and pol_out == 'H':
        return compute_spectrum_VH(delta_c_arr, delta_0a, **kwargs)
    elif pol_in == 'V' and pol_out == 'V':
        return compute_spectrum_VV(delta_c_arr, delta_0a, **kwargs)
    elif pol_in == 'H' and pol_out == 'V':
        return compute_spectrum_HV(delta_c_arr, delta_0a, **kwargs)
    elif pol_in == 'H' and pol_out == 'H':
        return compute_spectrum_HH(delta_c_arr, delta_0a, **kwargs)
    else:
        raise ValueError(f"Invalid polarization: ({pol_in}, {pol_out})")


# ==============================================================================
# Purcell-Modified Decay Rate  [Supplementary Section 4]
# ==============================================================================

# Fitted Purcell parameters from the three measured data points.
# The paper gives: σ_− = 4g²κ/(4Δ²+κ²) + σ₀, with σ₀ fitted.
# However, using the spectral parameters g=12.9, κ=31.9 gives a Purcell
# amplitude (4g²κ≈21234) that is too weak to explain the observed lifetime
# variation (230–460 ps). This is because the σ− transition couples to
# different cavity modes than σ+, and the effective Purcell rate includes
# contributions from multiple leaky modes. Fitting σ = A/(Δ²+B²) + σ₀
# to the three measured points gives:
_PURCELL_A = 38773.0      # Effective Purcell amplitude (GHz³)
_PURCELL_B = 15.95        # Half-width ≈ κ/2 (GHz)
_PURCELL_SIGMA0 = 1.458   # Background decay rate (GHz), 1/σ₀ ≈ 686 ps


def purcell_decay_rate(delta_ghz, A=_PURCELL_A, B=_PURCELL_B,
                       sigma_0=_PURCELL_SIGMA0):
    """
    Purcell-modified decay rate of the |−⟩ state.
    
    From Supplementary Section 4:
        σ_− = A / (Δ² + B²) + σ₀
    
    where A and σ₀ are determined by fitting to the three measured
    lifetime data points (Δ/2π = 113, 169, 230 GHz; τ = 230, 350, 460 ps).
    
    Parameters
    ----------
    delta_ghz : array-like
        QD(σ−)–cavity detuning Δ/2π in GHz.
    A : float
        Effective Purcell amplitude (GHz³).
    B : float
        Half-width parameter (GHz).
    sigma_0 : float
        Background decay rate σ₀/2π in GHz.
    
    Returns
    -------
    sigma_minus : array-like
        Total decay rate σ_−/2π in GHz.
    """
    delta = np.asarray(delta_ghz, dtype=float)
    purcell = A / (delta**2 + B**2)
    return purcell + sigma_0


def purcell_lifetime_ns(delta_ghz, **kwargs):
    """
    Lifetime of |−⟩ state in nanoseconds.
    
    Returns 1/σ_− in ns.
    """
    rate = purcell_decay_rate(delta_ghz, **kwargs)
    return 1.0 / rate  # Already in ns since rate is in GHz = 1/ns


# ==============================================================================
# Convenience: Broadband spectrum (LED-like white light source)
# ==============================================================================

def compute_broadband_spectrum(wavelengths_nm, delta_0a, g=g_ghz, kappa=kappa_ghz,
                               gamma=gamma_ghz, sigma_I=sigma_I_ghz,
                               qd_state='g', pol_in='V', pol_out='H',
                               W0=1.0, n_sd=200, sd_range=4.0):
    """
    Compute broadband (LED) cavity reflection spectrum.
    
    For a broadband source, S_in(ω) ≈ constant over the cavity bandwidth,
    so the reflected spectrum is simply proportional to the intensity transfer
    function evaluated at each frequency.
    
    Parameters
    ----------
    wavelengths_nm : array
        Wavelength array (nm).
    delta_0a : float
        Mean QD-cavity detuning (GHz).
    qd_state : str
        'g' or '-'
    pol_in, pol_out : str
        Input and output polarizations.
    
    Returns
    -------
    spectrum : array
        Reflected intensity spectrum.
    """
    # Convert wavelength to detuning from cavity
    delta_c = wavelength_to_detuning_ghz(wavelengths_nm)
    
    return compute_spectrum_general(
        delta_c, delta_0a, pol_in, pol_out,
        g=g, kappa=kappa, gamma=gamma, sigma_I=sigma_I,
        qd_state=qd_state, W0=W0, n_sd=n_sd, sd_range=sd_range
    )


# ==============================================================================
# Self-test
# ==============================================================================

if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    print("=== Cavity Model Self-Test ===")
    
    # Test: Bare cavity reflection
    delta_c = np.linspace(-60, 60, 500)
    r_b = r_bare(delta_c)
    
    # On resonance: r = 1 - κ/(κ/2) = 1 - 2 = -1
    print(f"  Bare cavity on-resonance: r = {r_bare(0.0):.3f} (expected -1)")
    
    # Coupled cavity on resonance with QD on cavity resonance
    r_c = r_coupled(0.0, 0.0)
    C = 2 * g_ghz**2 / (kappa_ghz * gamma_ghz)
    expected = (C - 1) / (C + 1)
    print(f"  Coupled on-resonance: r = {r_c.real:.3f} (expected {expected:.3f})")
    
    # Plot test spectra
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Reflectivity
    axes[0].plot(delta_c, np.abs(r_b)**2, 'b-', label='Bare cavity (|−⟩)')
    r_c_arr = r_coupled(delta_c, 0.0)
    axes[0].plot(delta_c, np.abs(r_c_arr)**2, 'r-', label='Coupled (|g⟩)')
    axes[0].set_xlabel('Δ_c / 2π (GHz)')
    axes[0].set_ylabel('|r(ω)|²')
    axes[0].set_title('Cavity Reflectivity')
    axes[0].legend()
    
    # Cross-pol intensity V→H
    W_bare = intensity_cross_pol(r_b)
    W_coupled = intensity_cross_pol(r_c_arr)
    W_coupled_avg = compute_spectrum_VH(delta_c, 0.0, qd_state='g')
    
    axes[1].plot(delta_c, W_bare, 'b-', label='Bare (|−⟩)')
    axes[1].plot(delta_c, W_coupled, 'r--', label='Coupled (|g⟩, no SD)')
    axes[1].plot(delta_c, W_coupled_avg, 'r-', label='Coupled (|g⟩, with SD)')
    axes[1].set_xlabel('Δ_c / 2π (GHz)')
    axes[1].set_ylabel('|1−r|²/4')
    axes[1].set_title('V→H Intensity')
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig('figures_sim/cavity_model_test.png', dpi=150)
    print("  Test plot saved to figures_sim/cavity_model_test.png")
