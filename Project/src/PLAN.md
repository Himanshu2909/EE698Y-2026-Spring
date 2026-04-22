# Simulation of QD-Photon CNOT Gate: Reproducing Figures from Kim et al. (2013)

## Background

This paper demonstrates a **controlled-NOT (cNOT) quantum logic gate** between a solid-state quantum bit (a quantum dot, QD) and a photonic qubit. The QD is strongly coupled to a photonic crystal nanocavity. The QD qubit states are |g⟩ (ground state) and |−⟩ (excited exciton state), while the photonic qubit is encoded in polarization (|H⟩ and |V⟩).

### Core Physics

1. **Three-level QD system**: Ground state |g⟩ and two bright exciton states |+⟩ and |−⟩. Under Faraday-configuration magnetic field, σ+ transition (|g⟩→|+⟩) tunes to cavity resonance, σ− remains detuned.
2. **Cavity reflection coefficient**: Derived from Heisenberg-Langevin equations:
   - When QD is in |g⟩: `r(ω) = 1 − κ / (iΔ_c + κ/2 + g²/(iΔ_a + γ))` where Δ_c = ω_c − ω, Δ_a = ω_a − ω
   - When QD is in |−⟩: `r(ω) = 1 − κ / (iΔ_c + κ/2)` (bare cavity, QD decoupled)
3. **Polarization transformation**: H/V basis rotated 45° from cavity axis. Output intensities given by Eqs. (32)-(40) in supplementary.
4. **Spectral diffusion**: Gaussian inhomogeneous broadening with P(δ) averaged over reflection coefficient.

### Key Parameters (from paper fits)
- g/2π = 12.9 GHz (QD-cavity coupling strength)
- κ/2π = 31.9 GHz (cavity decay rate, Q ≈ 10,200)
- γ = γ_spon/2 where γ_spon = 1/530 ps (from Purcell measurements)
- σ_I/2π = 5.2 GHz (inhomogeneous linewidth from spectral diffusion)
- Cavity resonance: λ_cav ≈ 920.93 nm (from Fig 2b midpoint between peaks)
- QD σ+ transition on cavity resonance at B = 1.6 T (Δ_0a = 0 for Fig 2b)

---

## Figures to Reproduce

### Figure 2: CW Characterization
| Panel | Description | Method |
|-------|-------------|--------|
| **2a** | Cavity spectrum vs magnetic field (2D color map) | Simulate QD-cavity anti-crossing: σ+ tunes through cavity with B-field. Use broadband source model |
| **2b** | High-res cavity spectrum at B=1.6T with narrowband laser | Use Eq.(41) with Gaussian spectral diffusion average |
| **2c** | Cavity spectrum vs pump laser detuning (2D color map) | Model pump-induced population of |−⟩ state modifying cavity spectrum |
| **2d-f** | Line cuts at ΔL/2π = 10, 0, −10 GHz | Extract slices from 2c model |

### Figure 3: Pulsed Pump-Probe (Bit Flip Demo)
| Panel | Description | Method |
|-------|-------------|--------|
| **3a** | Probe intensity vs √P (Rabi oscillations) | Sinusoidal modulation of QD excitation probability vs pump power |
| **3b-e** | Cavity spectra at 0, π, 2π, 3π pump conditions | Linear mixture: W = ρ·W_bare + (1−ρ)·W_coupled, where ρ is |−⟩ occupation |

### Figure 4: Complete CNOT Characterization
| Panel | Description | Method |
|-------|-------------|--------|
| **4a-d** | All 4 combinations: VV, VH, HV, HH | Use Eqs.(37)-(40) for two QD states |
| **4e** | Probability bar charts | Extract probabilities at λ = 920.96 nm |

### Supplementary Figure S2: g²(τ)
| Panel | Description | Method |
|-------|-------------|--------|
| **S2** | Second-order correlation of QD and laser | Simulate pulsed g²(τ) with suppressed τ=0 peak for QD |

### Supplementary Figure S4: Qubit Lifetime
| Panel | Description | Method |
|-------|-------------|--------|
| **S4a** | Probe intensity vs pump-probe delay (3 detunings) | Exponential decays with Purcell-modified lifetimes |
| **S4b** | Lifetime vs QD-cavity detuning | Fit σ = 4g²κ/(4Δ² + κ²) + σ₀ |

---

## Proposed Implementation

### File Structure
```
src/
├── figures/              # Original figures from paper (existing)
├── figures_sim/          # Our simulated figures (output)
├── common_params.py      # Shared physical parameters and constants
├── cavity_model.py       # Core cavity reflection calculations
├── figure2.py            # Figure 2 (a-f) simulation
├── figure3.py            # Figure 3 (a-e) simulation
├── figure4.py            # Figure 4 (a-e) simulation
├── figure_s2.py          # Supplementary Figure S2
├── figure_s4.py          # Supplementary Figure S4
├── DOCUMENTATION.md      # Physics + code documentation
└── PLAN.md               # This plan file
```

---

### [NEW] [common_params.py](file:///home/blakktyger/Documents/BlakkTyger/Acads/Sem6/EE698Y-2026-Spring/Project/src/common_params.py)

All shared physical constants and parameters:
- g, κ, γ, σ_I in angular frequency (rad/s) and GHz
- Cavity resonance wavelength/frequency
- Wavelength-to-frequency conversion utilities
- Spectral diffusion Gaussian P(δ) function

### [NEW] [cavity_model.py](file:///home/blakktyger/Documents/BlakkTyger/Acads/Sem6/EE698Y-2026-Spring/Project/src/cavity_model.py)

Core physics engine:
- `r_coupled(omega, delta_0a, delta, g, kappa, gamma)` — Reflection coefficient when QD in |g⟩ (Eq. 36)
- `r_bare(omega, kappa)` — Reflection coefficient when QD in |−⟩ (Eq. 20)
- `W_VH(omega_f, ...)`, `W_VV(...)`, `W_HH(...)`, `W_HV(...)` — Output intensities for all 4 polarization combos (Eqs. 37-40) with spectral diffusion averaging
- QuTiP master equation solver for Jaynes-Cummings Hamiltonian (for validation & potential QuTiP-based approach)

### [NEW] [figure2.py](file:///home/blakktyger/Documents/BlakkTyger/Acads/Sem6/EE698Y-2026-Spring/Project/src/figure2.py)

**Fig 2a**: Simulate anti-crossing
- Model: Zeeman splitting gives σ+ frequency shifting linearly with B through cavity resonance
- For each B value, compute broadband reflection spectrum using |1+r(ω)|²/2 averaged over spectral diffusion
- Plot as 2D color map (wavelength × B-field)

**Fig 2b**: Narrowband laser scan
- Direct implementation of Eq.(41)
- Sweep laser frequency across cavity, compute reflected intensity
- Parametric fit verification with g/2π=12.9 GHz, κ/2π=31.9 GHz, σ_I/2π=5.2 GHz

**Fig 2c**: Pump laser detuning map
- For each pump laser detuning ΔL, compute occupation of |−⟩ state (Lorentzian absorption profile)
- Modify effective spectrum: weighted mixture of coupled and bare cavity
- Plot as 2D color map

**Fig 2d-f**: Line cuts from 2c

### [NEW] [figure3.py](file:///home/blakktyger/Documents/BlakkTyger/Acads/Sem6/EE698Y-2026-Spring/Project/src/figure3.py)

**Fig 3a**: Rabi oscillations
- ρ(P) = sin²(π√(P/P_π)/2) with damping from excitation-induced dephasing
- Two curves: 80ps delay (Rabi oscillations visible) and 4ns delay (QD relaxed to |g⟩)
- At 80ps: I = ρ · I_bare + (1−ρ) · I_coupled at cavity resonance
- At 4ns: I = I_coupled (always |g⟩)

**Fig 3b-e**: Spectra at nπ pulse conditions
- Use Eqs.(37)-(40) for V→H measurement
- For each pump condition: W(ω) = ρ_n · W_bare(ω) + (1−ρ_n) · W_coupled(ω)
- ρ_0=0, ρ_π=0.93, ρ_2π≈0, ρ_3π≈0.93 (with decreasing contrast)
- Include 4.2 GHz probe bandwidth convolution

### [NEW] [figure4.py](file:///home/blakktyger/Documents/BlakkTyger/Acads/Sem6/EE698Y-2026-Spring/Project/src/figure4.py)

**Fig 4a-d**: All polarization combinations
- Use Eqs. (37)-(40) with narrowband approximation
- For same-polarization cases (VV, HH): add quadratic background I_B(ω) = a₀ + a₁(ω−ω_cav) + a₂(ω−ω_cav)²
- Two datasets per panel: QD in |−⟩ (80ps) and QD in |g⟩ (4ns)

**Fig 4e**: Probability bars
- Extract intensities at λ = 920.96 nm from fitted curves
- Calculate all P_ij using formulas from Supplementary Section 6
- 3D bar plot for both QD states

### [NEW] [figure_s2.py](file:///home/blakktyger/Documents/BlakkTyger/Acads/Sem6/EE698Y-2026-Spring/Project/src/figure_s2.py)

**Fig S2**: g²(τ) correlation
- Pulsed laser g²(τ): periodic peaks at multiples of T_rep = 1/76 MHz ≈ 13.16 ns
- QD emission g²(τ): same periodic peaks but with suppressed τ=0 peak (antibunching)
- Model each peak as Gaussian with appropriate width

### [NEW] [figure_s4.py](file:///home/blakktyger/Documents/BlakkTyger/Acads/Sem6/EE698Y-2026-Spring/Project/src/figure_s4.py)

**Fig S4a**: Lifetime decays
- Three exponential decays: I(t) = A·exp(−σ·t) + I_baseline
- Detunings: Δ/2π = 113, 169, 230 GHz → lifetimes = 230, 350, 460 ps
- Normalize and plot

**Fig S4b**: Lifetime vs detuning
- Theory curve: 1/σ_− = 1/(4g²κ/(4Δ² + κ²) + σ₀)
- Plot with σ₀ = 1/530 ps, g/2π = 12.9 GHz, κ/2π = 31.9 GHz
- Red circles at the three measured points

---

## QuTiP Integration Strategy

While the paper's theory is analytical (input-output formalism), we'll use QuTiP to:
1. **Validate the analytical model**: Set up Jaynes-Cummings Hamiltonian, compute steady-state reflection via master equation
2. **Compute cavity reflection spectra**: Use QuTiP's `steadystate()` to get ⟨a⟩ and derive r(ω)
3. **Simulate g²(τ)**: Use QuTiP's `correlation_2op_1t()` for photon statistics

The primary simulation will use the **analytical formulas** (which are exact in the weak-field limit) for efficiency and accuracy, with QuTiP validation.

---

## Verification Plan

### Automated Tests
- Compare each simulated figure against original via visual inspection
- Verify key numerical values:
  - Fig 2b: Peak splitting ≈ 2g/2π ≈ 25.8 GHz
  - Fig 3c: Contrast (I_max−I_min)/I_max ≈ 60%
  - Fig 4e: P_HV ≈ 0.93, P_VH ≈ 0.98 for |−⟩ state

### Iterative Refinement
- After generating each figure, visually compare with original
- Adjust parameters/model if needed before proceeding to next figure

## Execution Order
1. Install dependencies (numpy, scipy, matplotlib, qutip)
2. `common_params.py` → `cavity_model.py` (foundation)
3. Figure S4 (simplest, validates key parameters)
4. Figure 2b (core model validation)
5. Figure 2a, 2c-f (extensions of 2b model)
6. Figure S2 (independent, straightforward)
7. Figure 3 (builds on Fig 2 model + pump dynamics)
8. Figure 4 (complete cNOT characterization)
9. Documentation and comparison
