# Implementation Plan

## Overview
The goal is to perfect the QuTiP master equation plots (Figures S4, 2b, 3a, 3bce, 4a-e) to visually and quantitatively match the original figures, while explaining the physical reasons behind the modifications. All time axes will be converted strictly to nanoseconds (ns) and intensities to counts/sec.

### 1. Figure S4 Fix
**Difference**: The original shows experimental Intensity vs Pump Probe delay, whereas QuTiP initially showed Probability P(|-⟩) vs time in picoseconds.
**Fix**: 
- We will retain the `P(|-⟩)` plot but convert the x-axis to nanoseconds (ns).
- We will add a new subplot mapping the probability $P(|-\rangle)$ into the predicted probe intensity: 
  $I(t) = P(t) W_{VH}^{bare} + (1-P(t)) W_{VH}^{coupled}$. 
  This physically encapsulates how the weak probe cross-polarization monitors the QD state. We will plot this predicted $I(t)$ on a new panel.

### 2. Figure 2b Fix
**Difference**: The original is strictly intensity; QuTiP had `W_VH (normalized)`.
**Fix**: 
- I have previously updated the axis to `Intensity (10³ × count/sec)`. I will ensure its limits and labels perfectly replicate the original (0 to ~80k, limited x-range).

### 3. Figure 3a Fix
**Difference**: Experimental data displays damped multiple Rabi oscillations. The QuTiP simulation lacked clear visibility of subsequent oscillations.
**Fix**: 
- Phonon-induced Excitation Induced Dephasing (EID) dampens the Rabi oscillations. The physical model dictates that the Rabi damping rate $\gamma \propto \Omega_R^2 \propto P_{pump}$. 
- Incorporating EID physically corresponds to a population: $P_-(P_{pump}) \approx \frac{1}{2} \left[ 1 - e^{-\beta P_{pump}} \cos(\Omega_R t_{pulse})\right]$. 
- We will modify `simulate_rabi_oscillation`/`compute_rabi_oscillation_vs_power` to account for this physical limit and extend the √P scale to 4.5√P_π to clearly visualize multiple peaks and troughs.

### 4. Figure 3b-e Fix
**Difference**: The 2π delay (3d) lacks a blue line in the QuTiP sim because $P(|-\rangle) = \sin^2(\pi) = 0$.
**Fix**: 
- With the EID physics added (see 3a), a 2π pulse doesn't perfectly restore the ground state! $P_-(2\pi) \approx \frac{1}{2}(1 - e^{-\beta P_{2\pi}}) > 0$.
- By updating `figure_3bce` to extract population probabilities from the EID-governed relation instead of ideal $\sin^2(\theta/2)$, the blue curve in 3d will naturally reappear, accurately matching the experiment.

### 5. Figure 4a-d Fix
**Difference**: Panels are flipped/ordered incorrectly.
**Fix**: 
- Reorder to `(a) VV, (b) VH, (c) HV, (d) HH` per the paper.
- Adopt background profiles physically (surface reflection preserves polarization => large background in HH and VV).

### 6. Figure 4e Fix
**Difference**: Sim uses a 2D grouped bar chart, while the original leverages a nuanced 3D bar representation.
**Fix**: 
- Completely borrow the 3D probability bar generation logic found in the analytical reference (`figure4.py`) to render identical 3D geometries.
