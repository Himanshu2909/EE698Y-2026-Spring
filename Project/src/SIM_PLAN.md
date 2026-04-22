# QuTiP Master Equation Simulation Plan

## System: QD-Photon CNOT Gate (Kim et al., 2013)

### Physical Model

**Hilbert Space**: 3-level QD {|g⟩, |+⟩, |−⟩} ⊗ N-Fock cavity (N=5)

**Hamiltonian** (rotating frame at probe ω_L):
```
H = Δ_c â†â + Δ_+ |+⟩⟨+| + Δ_− |−⟩⟨−| + g(â†|g⟩⟨+| + â|+⟩⟨g|) + ε(â + â†)
```

**Collapse Operators**:
```
L1 = √κ â                    (cavity decay, κ/2π = 31.9 GHz)
L2 = √γ_spon |g⟩⟨+|         (σ+ emission, γ_spon/2π = 1.887 GHz)
L3 = √γ_− |g⟩⟨−|            (σ− emission, Purcell-dependent)
```

**Input-Output Relation**:
```
r(ω) = 1 − iκ⟨â⟩_ss / ε
```

### Key Parameters
| Parameter | Value | Source |
|---|---|---|
| g/2π | 12.9 GHz | Supplementary Sec. 3 |
| κ/2π | 31.9 GHz | Supplementary Sec. 1 |
| γ_spon | 1/530 ps | Supplementary Sec. 4 |
| σ_I/2π | 5.2 GHz | Supplementary Sec. 3 |
| C (cooperativity) | 11.06 | 2g²/(κγ) |

### Simulation Modules
1. `sim_hamiltonian.py` — Operators, Hamiltonian, collapse operators
2. `sim_reflection.py` — Steady-state reflection spectrum (Figs 2b, 2d-f)
3. `sim_dynamics.py` — Time-domain: Rabi (Fig 3a), Purcell (S4), pump-probe (3b-e)
4. `sim_cnot.py` — CNOT gate with polarization analysis (Figs 4a-e)

### Spectral Diffusion
Classical averaging: `W(ω) = ∫ P(δ) × |1−r(ω,δ)|²/4 dδ` over Gaussian P(δ).

### Validation
- Bare cavity: r(0) = −1 ✓
- Coupled cavity: r(0) = 0.834 = (C−1)/(C+1) ✓  
- ME matches analytical formula across full spectrum ✓
