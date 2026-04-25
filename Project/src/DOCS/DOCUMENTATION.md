# QD-Photon CNOT Gate Simulation: Comprehensive Documentation

## Table of Contents
1. [The Big Picture — What Is This Paper About?](#1-the-big-picture)
2. [Background Physics (From Scratch)](#2-background-physics)
3. [The Device: How It Actually Works](#3-the-device)
4. [The Theory: Mathematical Framework](#4-the-theory)
5. [Figure 3: Deep Dive Into Implementation](#5-figure-3-deep-dive)
6. [Code Architecture](#6-code-architecture)
7. [Assumptions & Simplifications](#7-assumptions)

---

## 1. The Big Picture — What Is This Paper About? <a name="1-the-big-picture"></a>

### The One-Sentence Summary

> This paper demonstrates a **CNOT logic gate** between a **solid-state quantum bit** (a quantum dot) and a **photon** (a particle of light), where the quantum dot's internal state controls whether the photon's polarization gets flipped or not.

### Why Does This Matter?

In quantum computing and quantum networking, we need to connect different quantum systems together. Photons (light particles) are ideal for carrying quantum information over long distances (through fiber optics), while solid-state qubits (like quantum dots) are good for storing and processing quantum information locally. A **quantum logic gate** between the two is the bridge — it lets the solid-state qubit "talk to" the photon, and vice versa.

### What Is a CNOT Gate?

A **CNOT (Controlled-NOT) gate** is a two-bit logic operation with a **control bit** and a **target bit**:

| Control | Target (in) | Target (out) |
|---------|-------------|--------------|
| 0       | 0           | 0 (unchanged) |
| 0       | 1           | 1 (unchanged) |
| 1       | 0           | 1 (**flipped**) |
| 1       | 1           | 0 (**flipped**) |

**Rule:** If the control = 1, the target gets flipped. If the control = 0, the target stays the same.

In this paper:
- **Control bit** = Quantum Dot (QD) state: either `|g⟩` (ground) or `|−⟩` (excited)
- **Target bit** = Photon polarization: either `|H⟩` (horizontal) or `|V⟩` (vertical)

The QD tells the photon: *"If I'm excited, flip your polarization. If I'm in the ground state, don't change."*

---

## 2. Background Physics (From Scratch) <a name="2-background-physics"></a>

### 2.1 What Is a Quantum Dot (QD)?

A **quantum dot** is a nanometer-scale semiconductor crystal (here, made of Indium Arsenide, InAs) embedded in a different semiconductor (GaAs). It's so small (~10 nm) that electrons and holes (positive charge carriers) inside it are trapped in all three dimensions, like a particle in a 3D box.

Because of this confinement, the QD has **discrete energy levels** (like an atom), earning it the nickname "artificial atom." The key levels are:

```
Energy ↑
         |+⟩  ← excited state (exciton with σ+ polarization)
         |−⟩  ← excited state (exciton with σ− polarization)
         
         |g⟩  ← ground state (no excitation)
```

- **|g⟩**: Ground state — no electron-hole pair exists
- **|+⟩** and **|−⟩**: "Bright exciton" states — an electron-hole pair with specific spin configurations
- The transition |g⟩ → |+⟩ emits/absorbs **right-circularly polarized** light (σ+)
- The transition |g⟩ → |−⟩ emits/absorbs **left-circularly polarized** light (σ−)

### 2.2 What Is a Photonic Crystal Cavity?

A **photonic crystal** is a material with a periodic pattern of holes etched into it. This creates a "photonic bandgap" — a range of wavelengths that cannot propagate through the crystal (analogous to electronic bandgaps in semiconductors).

A **defect** (missing holes) in the crystal creates a **cavity** — a tiny region where light *can* exist, trapped by the surrounding bandgap. This is an optical resonator at the nanoscale.

Key cavity parameters:
- **Resonance wavelength** (λ_cav = 920.93 nm): The specific color of light the cavity "likes"
- **Quality factor** (Q = 10,200): How long light bounces around before leaking out. Higher Q = longer trapping = sharper resonance
- **Decay rate** (κ/2π = 31.9 GHz): How fast light leaks out. Related to Q by: κ = ω_cav / Q

### 2.3 What Is Strong Coupling?

When a QD is placed inside a cavity, they can exchange energy. The **coupling strength** `g` measures how fast this exchange happens.

Three regimes exist:

| Regime | Condition | Physical Meaning |
|--------|-----------|------------------|
| **Weak coupling** | g < κ/4 | QD emits into cavity, but cavity leaks too fast. Irreversible. |
| **Strong coupling** | g > κ/4 | Energy sloshes back and forth between QD and cavity (Rabi oscillation). Two distinct peaks (vacuum Rabi splitting) appear in the spectrum. |
| **Ultra-strong** | g ~ ω_cav | New physics (not relevant here). |

In this paper: **g/2π = 12.9 GHz** and **κ/2π = 31.9 GHz**, so g > κ/4 = 8.0 GHz. ✅ **Strong coupling achieved.**

The **cooperativity** C quantifies the strength of QD-cavity interaction:

```
C = 2g² / (κ × γ)  =  2 × 12.9² / (31.9 × 0.94)  ≈  11.1
```

C >> 1 means the QD significantly modifies the cavity's optical response. This is crucial for the gate.

### 2.4 Cavity Reflection and the Gate Mechanism

When light hits the cavity from outside, it gets reflected. The **reflection coefficient** `r(ω)` tells us the amplitude and phase of the reflected light.

**Scenario 1: QD in |−⟩ state (excited, decoupled from cavity)**

The σ− transition is far detuned from the cavity. The cavity behaves as if the QD isn't there — it's a **bare cavity**:

```
r_bare(ω) = 1 − κ / (iΔ_c + κ/2)
```

At cavity resonance (Δ_c = 0): r = 1 − κ/(κ/2) = 1 − 2 = **−1**

**Scenario 2: QD in |g⟩ state (ground, coupled to cavity)**

The σ+ transition is resonant with the cavity. The QD strongly modifies the reflection:

```
r_coupled(ω) = 1 − κ(iΔ_a + γ) / [(iΔ_c + κ/2)(iΔ_a + γ) + g²]
```

At cavity resonance with QD on resonance: r = (C−1)/(C+1) ≈ **+0.83**

### 2.5 How This Makes a Gate: Polarization Rotation

The **photonic qubit** is encoded in H/V polarization, which is rotated 45° from the cavity axis (x/y):

```
|H⟩ = (|x⟩ + |y⟩) / √2
|V⟩ = (|y⟩ − |x⟩) / √2
```

The cavity only interacts with the x-polarized component (reflection coefficient r). The y-component reflects unchanged (coefficient = −1, since there's no cavity mode along y in this design).

After reflection:

```
|H⟩_out = (r|x⟩ − |y⟩) / √2
|V⟩_out = (−|y⟩ − r|x⟩) / √2
```

- **If r = −1** (QD in |−⟩, bare cavity): |H⟩ → (−|x⟩ − |y⟩)/√2 = −|V⟩. **Polarization FLIPPED!** ✅
- **If r = +1** (QD in |g⟩, ideal C→∞): |H⟩ → (+|x⟩ − |y⟩)/√2 = |H⟩. **Polarization PRESERVED!** ✅

This is exactly the CNOT truth table.

### 2.6 Measuring Cross-Polarization Intensity

In the experiment, you send in V-polarized light and measure the reflected H-polarized component (or vice versa). The **cross-polarization intensity** is:

```
W_VH(ω) = |1 − r(ω)|² / 4 × S_in(ω)
```

The **same-polarization intensity** is:

```
W_VV(ω) = |1 + r(ω)|² / 4 × S_in(ω)
```

When r = −1 (bare cavity): W_VH = |1−(−1)|²/4 = 1 (maximum cross-pol → bit flip)
When r = +1 (coupled, C→∞): W_VH = |1−1|²/4 = 0 (no cross-pol → no bit flip)

---

## 3. The Device: How It Actually Works <a name="3-the-device"></a>

### 3.1 Experimental Setup (Simplified)

```
                      ┌──────────────┐
  Pump laser ────────►│              │
  (10 ps pulse)       │   Photonic   │
                      │   Crystal    │──────► Detector
  Probe laser ────────►│   Cavity     │        (counts photons)
  (75 ps pulse)       │   + QD       │
                      └──────────────┘
                           ▲
                      Magnetic field
                      (tunes QD energy)
```

- **Pump laser**: Short (10 ps) pulse that excites the QD from |g⟩ to |−⟩ via Rabi oscillation
- **Probe laser**: Slightly longer (75 ps) pulse that serves as the photonic qubit
- **Delay**: The probe arrives a controlled time after the pump (80 ps or 4 ns)
- **Polarization optics**: Select input (V) and output (H or V) polarization
- **Detector**: Single-photon counter that measures reflected probe intensity

### 3.2 The Pump-Probe Protocol

The timing sequence for Figure 3:

```
Time ──────────────────────────────────────►

     ┌──┐                    ┌──┐
     │  │ Pump               │  │ Pump        (repeats at 76 MHz)
─────┘  └────────────────────┘  └────────────
              ┌────┐                  ┌────┐
              │    │ Probe            │    │ Probe
──────────────┘    └──────────────────┘    └──
         ◄──►
        80 ps delay
         (or 4 ns)
```

**Two measurement modes:**
1. **80 ps delay**: Probe arrives 80 ps after pump → QD is still in |−⟩ (hasn't decayed yet, since lifetime = 230–460 ps)
2. **4 ns delay**: Probe arrives 4 ns after pump → QD has fully relaxed back to |g⟩ (lifetime << 4 ns)

This lets them compare the cavity response in both QD states.

---

## 4. The Theory: Mathematical Framework <a name="4-the-theory"></a>

### 4.1 The Reflection Coefficient

The central equation (from the Heisenberg-Langevin treatment):

```
r(ω, δ) = 1 − κ(iΔ_a + γ) / [(iΔ_c + κ/2)(iΔ_a + γ) + g²]
```

Where:
- **Δ_c = ω_cav − ω**: Detuning of probe from cavity resonance
- **Δ_a = Δ_0a + Δ_c + δ**: Total QD detuning (mean QD-cavity detuning + probe detuning + spectral diffusion)
- **γ/2π ≈ 0.94 GHz**: QD homogeneous linewidth (half the spontaneous emission rate)
- **δ**: Random spectral diffusion shift

For the **bare cavity** (QD decoupled, e.g., in state |−⟩):
```
r_bare(ω) = 1 − κ / (iΔ_c + κ/2)
```

### 4.2 Spectral Diffusion

The QD's resonance frequency **wanders randomly** on timescales of microseconds (due to fluctuating charges near the QD). This is modeled as a Gaussian random variable:

```
P(δ) = (1/√(2π)σ_I) × exp(−δ²/(2σ_I²))
```

with σ_I/2π = 5.2 GHz.

Every measured spectrum is actually an **average** over many realizations of δ:

```
⟨W_VH(ω)⟩ = ∫ P(δ) × |1 − r(ω,δ)|² / 4 × dδ
```

This broadens the sharp spectral features.

### 4.3 Probe Bandwidth Convolution

The probe laser isn't perfectly monochromatic — it has a **bandwidth of 4.2 GHz** (corresponding to its 75 ps pulse duration). The measured intensity is a convolution of the ideal spectrum with the probe's spectral profile:

```
I_measured(ω) = ∫ I_ideal(ω') × G(ω − ω') dω'
```

where G is a Gaussian with width 4.2 GHz. This smears out the double-peak structure and reduces the contrast.

### 4.4 The Rabi Oscillation Model

When the pump pulse hits the QD, it drives a **Rabi oscillation** between |g⟩ and |−⟩:

```
ρ_−(P) = sin²(Θ/2)
```

where Θ = π × √(P/P_π) is the **Rabi angle** (P_π = 0.12 µW is the π-pulse power).

| Pump Power | Θ | QD State |
|------------|---|----------|
| 0 | 0 | |g⟩ (ground) |
| P_π | π | |−⟩ (fully excited) |
| 4 × P_π | 2π | |g⟩ (back to ground) |
| 9 × P_π | 3π | |−⟩ (excited again) |

**Damping:** At high power, the oscillation gets damped by **excitation-induced dephasing (EID)** — phonons in the crystal lattice destroy quantum coherence:

```
ρ_−(P) = sin²(Θ/2) × exp(−α×P) + β×P
```

- `exp(−α×P)`: Exponential damping of coherent oscillation amplitude
- `β×P`: Power-dependent incoherent background excitation (multi-phonon processes pump the QD into |−⟩ even off-resonance)

---

## 5. Figure 3: Deep Dive Into Implementation <a name="5-figure-3-deep-dive"></a>

### 5.1 What Figure 3 Shows

Figure 3 demonstrates the **controlled bit flip** — the key operation of the CNOT gate. It has five panels:

| Panel | What's plotted | X-axis | Y-axis |
|-------|---------------|--------|--------|
| **(a)** | Rabi oscillation — probe intensity vs pump power | √P (√µW) | Intensity at cavity resonance (10³ count/sec) |
| **(b)** | Spectrum with NO pump | Wavelength (nm) | Cross-pol intensity |
| **(c)** | Spectrum with **π-pulse** | Wavelength (nm) | Cross-pol intensity |
| **(d)** | Spectrum with **2π-pulse** | Wavelength (nm) | Cross-pol intensity |
| **(e)** | Spectrum with **3π-pulse** | Wavelength (nm) | Cross-pol intensity |

Each panel (b–e) shows **two traces**:
- **Blue dots** (80 ps delay): QD in |−⟩ → bare cavity → strong cross-pol signal
- **Red squares** (4 ns delay): QD relaxed to |g⟩ → coupled cavity → weak cross-pol signal

### 5.2 Function-by-Function Breakdown

#### File: `figure3.py`

---

#### `convolve_with_probe(wavelengths, spectrum, bandwidth_ghz)`

**Purpose:** Simulates the finite bandwidth of the probe laser.

**What it does:**
1. Converts the probe's spectral bandwidth from GHz to wavelength units (nm)
2. Creates a Gaussian convolution kernel with the appropriate width
3. Convolves the ideal spectrum with this kernel
4. Returns the broadened spectrum

**Why it matters:** Without this, the simulated spectrum would show perfectly sharp double peaks. In reality, the 75 ps probe pulse has a 4.2 GHz bandwidth that smears these peaks together, reducing contrast — just like in the experiment.

**Key math:**
```
σ_λ = λ²_cav / c × bandwidth_GHz    (bandwidth in wavelength units)
kernel(x) = exp(−x²/(2σ_λ²))        (Gaussian kernel)
I_out(λ) = I_ideal(λ) ⊛ kernel(λ)   (convolution)
```

---

#### `rabi_population(sqrt_P, sqrt_P_pi, damping_rate, bg_rate)`

**Purpose:** Computes the probability that the QD is in state |−⟩ for a given pump power.

**What it does:**
1. Computes the Rabi angle: Θ = π × √P / √P_π
2. Computes the coherent population: sin²(Θ/2) × exp(−α×P)
3. Adds the incoherent background: β × P
4. Returns the total ρ_− value

**Parameters:**
- `sqrt_P`: Array of √(pump power) values
- `sqrt_P_pi = √0.12 ≈ 0.346`: The √P corresponding to a π-pulse
- `damping_rate = 0.20`: EID damping coefficient α (per µW)
- `bg_rate = 0.012`: Background excitation rate β (per µW)

**Key physics insight:** The damping term makes the oscillation "die down" at high power. But the background term adds a slowly growing floor. Combined, this produces the experimental signature: **maxima stay roughly constant** (damping reduces peaks, but background lifts the floor), while **minima steadily rise** (pure background effect).

**Example values:**

| √P (√µW) | P (µW) | Θ | sin²(Θ/2) | × exp(−αP) | + βP | Total ρ_− |
|-----------|--------|---|-----------|------------|------|-----------|
| 0.00 | 0.00 | 0 | 0.00 | 0.00 | 0.00 | 0.00 |
| 0.35 | 0.12 | π | 1.00 | 0.98 | 0.001 | 0.98 |
| 0.69 | 0.48 | 2π | 0.00 | 0.00 | 0.006 | 0.006 |
| 1.04 | 1.08 | 3π | 1.00 | 0.81 | 0.013 | 0.82 |

---

#### `figure_3a(ax)`

**Purpose:** Generates panel (a) — the Rabi oscillation plot.

**Step-by-step process:**

1. **Set up power axis:** `sqrt_P` from 0 to 3.0 √µW (200 points)

2. **Compute QD occupation at each power:** Calls `rabi_population()` to get ρ_−(P)

3. **Compute probe-bandwidth-corrected intensities:**
   - Generates the full cross-pol spectrum (V→H) over a wavelength range
   - For coupled system: `compute_spectrum_VH(Δ_c, 0, qd_state='g')`
   - For bare cavity: `compute_spectrum_VH(Δ_c, 0, qd_state='-')`
   - **Convolves** each spectrum with the probe bandwidth
   - Evaluates the convolved spectra at cavity resonance wavelength
   - This gives `I_c_eff` (effective coupled intensity at probe center) and `I_b_eff` (effective bare intensity at probe center)

4. **Mix the two spectra** according to QD occupation:
   ```
   I(P) = ρ_−(P) × I_bare_eff + (1 − ρ_−(P)) × I_coupled_eff
   ```
   This is the measured intensity at cavity resonance for 80 ps delay.

5. **Scale to physical units:** Sets I_coupled (P=0 baseline) = 10,000 count/sec

6. **Plot 4 ns delay data:** Flat line at coupled intensity (QD always in |g⟩, no oscillation), with a slight upward drift modeling experimental cavity heating:
   ```
   I_4ns(P) = I_coupled + 0.4 × P    (linear in power)
   ```

7. **Add noise** for realistic appearance (Gaussian, σ ≈ 1.2k count/sec)

8. **Mark π, 2π, 3π positions** with vertical dashed lines

**Key assumption:** The probe bandwidth convolution is CRITICAL. Without it, the bare/coupled contrast ratio would be ~36:1 (since |1−r_bare|²/|1−r_coupled|² is very large at exact resonance). But the probe bandwidth "averages" over a spectral range, reducing the effective contrast to ~2.2:1 (matching the paper's observed 10k → 22k oscillation).

---

#### `figure_3_panel(ax, pump_condition, rho_80ps, panel_label, title, ...)`

**Purpose:** Generates one of panels b–e, showing the full wavelength-resolved spectrum.

**Step-by-step process:**

1. **Generate wavelength array:** 920.82 to 921.12 nm, 300 points

2. **Convert wavelength to cavity detuning:** Uses `wavelength_to_detuning_ghz()` to get Δ_c values

3. **Compute coupled and bare spectra:**
   - `spec_coupled`: Cross-pol intensity when QD is in |g⟩ (coupled)
   - `spec_bare`: Cross-pol intensity when QD is in |−⟩ (bare cavity)
   - Both call `compute_spectrum_VH()` which includes spectral diffusion averaging

4. **Convolve with probe bandwidth:** Both spectra get smoothed by the 4.2 GHz probe

5. **Mix according to QD occupation:**
   - For **no pump** (panel b): ρ = 0, so only the coupled spectrum is shown
   - For **π-pulse** (panel c): ρ = 0.93, so 93% bare + 7% coupled
   - For **2π-pulse** (panel d): ρ ≈ 0.05, so almost all coupled
   - For **3π-pulse** (panel e): ρ ≈ 0.65, so 65% bare + 35% coupled

6. **Scale to physical units:** Peak of coupled spectrum → 30,000 count/sec

7. **Plot both traces:**
   - `spec_80ps`: Blue line + blue circles (mixed spectrum at 80 ps delay)
   - `spec_4ns`: Red line + red squares (always coupled spectrum at 4 ns delay)

**Key insight about panels b–e:** The 4 ns (red) trace is **always identical** (always coupled, QD in |g⟩). Only the 80 ps (blue) trace changes with pump power. At π-pulse (panel c), blue and red are maximally different. At 2π-pulse (panel d), blue and red nearly overlap (QD back in |g⟩).

---

#### `figure_3bce(axes)`

**Purpose:** Wrapper that calls `figure_3_panel()` four times with the correct parameters.

The QD occupation values (ρ) at each pump condition come from the Rabi model:

| Condition | ρ_− value | Source |
|-----------|-----------|--------|
| No pump | 0.00 | No excitation |
| π pulse | 0.93 | From paper's fit (Supp. Sec. 5: ρ = 0.93 ± 0.04) |
| 2π pulse | 0.05 | ≈ 0 but finite due to EID (incomplete return) |
| 3π pulse | 0.65 | Reduced from 1.0 by EID damping at higher power |

---

#### `generate_figure_3()`

**Purpose:** Creates the complete 5-panel figure with proper layout.

Uses `fig.add_axes([left, bottom, width, height])` to manually position each panel — panel (a) spans the full width at the top, panels (b–e) are arranged in a 2×2 grid below.

---

### 5.3 The Underlying Physics Engine (cavity_model.py)

#### `r_coupled(delta_c, delta_0a, g, kappa, gamma, delta_sd)`

**Implements:** Equation (36) from the supplementary material.

```python
delta_a = delta_c + delta_0a + delta_sd   # Total QD detuning
numerator = kappa * (1j * delta_a + gamma)
denominator = (1j * delta_c + kappa/2) * (1j * delta_a + gamma) + g**2
return 1.0 - numerator / denominator
```

**Derivation note:** This comes from solving the Heisenberg-Langevin equations for the cavity field operator and the QD lowering operator in steady state. The key steps are:
1. Write equations of motion for cavity field (â) and QD operator (σ̂_−)
2. Set time derivatives to zero (steady state)
3. Relate output field to input field via input-output relation: b̂_out = â − b̂_in
4. The ratio b̂_out/b̂_in gives the reflection coefficient r(ω)

#### `r_bare(delta_c, kappa)`

**Implements:** Equation (20) — same as r_coupled but with g = 0.

```python
return 1.0 - kappa / (1j * delta_c + kappa/2)
```

#### `compute_spectrum_VH(delta_c_arr, delta_0a, qd_state, ...)`

**Purpose:** Computes the spectral-diffusion-averaged cross-polarization intensity.

**Process:**
1. If QD state is `'-'` (bare): Just compute `|1 − r_bare|²/4`
2. If QD state is `'g'` (coupled):
   - Create 200 sample points of spectral diffusion δ from −4σ_I to +4σ_I
   - For each δ: compute r(ω, δ), then |1−r|²/4
   - Weight by Gaussian P(δ) and sum → gives the averaged spectrum

**This is Equation (37) from the paper:**
```
W_VH = ∫ P(δ) × |1 − r(ω,δ)|² / 4 × S_in(ω) dδ dω
```

For a narrowband laser (S_in ≈ δ-function), this reduces to just the spectral diffusion integral.

---

### 5.4 Data Flow Diagram for Figure 3(c): π-Pulse Panel

```
┌─────────────────────────────────────────────────────────┐
│                     INPUT PARAMETERS                     │
│  g = 12.9 GHz, κ = 31.9 GHz, γ = 0.94 GHz             │
│  σ_I = 5.2 GHz, probe BW = 4.2 GHz                     │
│  ρ_π = 0.93 (π-pulse QD occupation)                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ For each wavelength λ in [920.82, 921.12] nm:           │
│   Δ_c = ν_cav − ν(λ)     ← convert to GHz detuning    │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     ┌────────────────┐    ┌────────────────┐
     │  COUPLED (|g⟩)  │    │   BARE (|−⟩)   │
     │                │    │                │
     │ For each δ in  │    │ r = r_bare(Δ_c)│
     │ Gaussian dist: │    │ = 1 − κ/(iΔ_c  │
     │   r(Δ_c, δ)    │    │    + κ/2)      │
     │   |1−r|²/4     │    │ |1−r|²/4       │
     │   × P(δ) × dδ  │    │                │
     │   Sum ─────────►│    │                │
     └───────┬────────┘    └───────┬────────┘
             │                     │
             ▼                     ▼
     spec_coupled(λ)      spec_bare(λ)
             │                     │
             │    ┌────────────────┘
             │    │
             ▼    ▼
     ┌────────────────────────────┐
     │  PROBE BANDWIDTH           │
     │  Convolve each with        │
     │  Gaussian (σ = 4.2 GHz)    │
     └──────────┬─────────────────┘
                │
                ▼
     ┌────────────────────────────┐
     │  MIX ACCORDING TO ρ        │
     │                            │
     │ 80 ps: ρ×bare + (1−ρ)×coupled │
     │ 4 ns:  coupled only        │
     └──────────┬─────────────────┘
                │
                ▼
     ┌────────────────────────────┐
     │  SCALE TO COUNT RATE        │
     │  peak → 30,000 count/sec    │
     └──────────┬─────────────────┘
                │
                ▼
          PLOT ON AXES
```

---

## 6. Code Architecture <a name="6-code-architecture"></a>

### File Dependency Tree

```
common_params.py          ← Physical constants, unit conversions
       │
       ▼
cavity_model.py           ← Core physics: r(ω), spectral diffusion, intensities
       │
       ├──► figure_s4.py  ← Purcell lifetime
       ├──► figure_s2.py  ← g²(τ) antibunching
       ├──► figure2.py    ← CW characterization
       ├──► figure3.py    ← Pulsed pump-probe (this doc's focus)
       └──► figure4.py    ← Full CNOT gate
```

### Key Parameters (common_params.py)

| Parameter | Value | Units | Physical Meaning |
|-----------|-------|-------|------------------|
| g/2π | 12.9 | GHz | QD-cavity coupling |
| κ/2π | 31.9 | GHz | Cavity decay rate |
| γ/2π | 0.94 | GHz | QD homogeneous linewidth |
| σ_I/2π | 5.2 | GHz | Spectral diffusion width |
| λ_cav | 920.93 | nm | Cavity resonance |
| probe BW | 4.2 | GHz | Probe laser bandwidth |
| P_π | 0.12 | µW | π-pulse power |
| ρ_π | 0.93 | — | QD excitation probability after π-pulse |

---

## 7. Assumptions & Simplifications <a name="7-assumptions"></a>

### 7.1 Assumptions in the Simulation

1. **Analytical Input-Output Formalism (not full master equation)**
   - We solve for the cavity reflection coefficient r(ω) from the Heisenberg-Langevin equations in steady state
   - This assumes the system reaches steady state within the probe pulse duration
   - Valid because the cavity lifetime (1/κ ≈ 5 ps) is much shorter than the probe pulse (75 ps)

2. **Spectral diffusion modeled as Gaussian**
   - The QD's frequency jitter is averaged as a static Gaussian over many measurement shots
   - This assumes the diffusion timescale is fast compared to total integration time but slow compared to individual pulses

3. **Narrowband probe approximation**
   - For spectral plots: the probe is treated as near-monochromatic (Eq. 41: S_in ≈ δ(ω − ω_f))
   - Then separately convolved with probe bandwidth
   - Valid because probe BW (4.2 GHz) << cavity linewidth (31.9 GHz)

4. **Rabi oscillation model is phenomenological**
   - The sin²(Θ/2) comes from solving the two-level Schrödinger equation for a pulsed drive
   - EID damping (exp(−αP)) and background (βP) are fitted parameters, not derived from microscopic theory
   - This is the same approach used in the paper

5. **No multi-photon effects**
   - The probe is weak enough that we can ignore photon-photon interactions
   - Each probe photon interacts independently with the cavity-QD system

6. **No pure dephasing**
   - Paper states: "pure dephasing rate is negligibly small compared to inhomogeneous linewidth"
   - We use γ = γ_spon/2 as the linewidth (only spontaneous emission contributes)

### 7.2 What We Do NOT Simulate

- Actual quantum state evolution (density matrix, master equation with Lindblad operators)
- Photon statistics (g²(τ) from quantum trajectories) — only approximate analytical model for Figure S2
- Dynamic Purcell decay during the probe pulse
- Detailed phonon bath coupling for EID
- Detector response, jitter, dark counts
