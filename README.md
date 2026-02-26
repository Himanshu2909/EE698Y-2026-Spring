# EE698Y: Introduction to Quantum Optics (Spring 2026) 
Instructor : Shilpi Gupta

## Pre Midsems

### Syllabus
| Topic | Key Concept | Notes Pages | Fox Section | Gerry & Knight Section |
|--------|------------|------------|-------------|-------------------------|
| **1. Time-Dependent Perturbation Theory (TDPT)** | TDSE and expansion in eigenstates | 1–4, 10–11, Ass. 1, Ass. 2 | 3.1, 4.2 | 4.1, 4.2 |
|  | First-order transition amplitudes for constant perturbations |  |  |  |
|  | First-order transition amplitudes for Gaussian perturbations |  |  |  |
|  | Transition probabilities, detuning (Δ), and resonance |  |  |  |
|  | Fermi's Golden Rule and Density of States (DOS) |  |  |  |
|  | *Missing/Prereq:* Basic postulates of quantum mechanics |  |  |  |
|  | *Missing/Prereq:* Hydrogenic wavefunctions (Assignment 2) |  |  |  |
| **2. Two-Level Atoms & Rabi Oscillations** | Interaction Hamiltonian and dipole operator | 5–11, 27–28, Ass. 1, Ass. 2 | 9.1, 9.2, 9.4, 9.5 | 4.3, 4.4 |
|  | Rotating Wave Approximation (RWA) |  |  |  |
|  | Coupled differential equations for state amplitudes |  |  |  |
|  | Resonant Rabi oscillations |  |  |  |
|  | Off-resonant Rabi oscillations & generalized Rabi frequency |  |  |  |
|  | Pulse area and Gaussian pulses |  |  |  |
|  | *Missing/Prereq:* Unitary evolution operators |  |  |  |
|  | *Missing/Prereq:* Heisenberg picture for spin-1/2 systems |  |  |  |
| **3. Density Matrix Formalism & Optical Bloch Equations** | Pure vs. mixed states, decoherence, populations | 12–22, Ass. 2 | 3.1.3, 9.2.3, 9.5.2, 9.6 | 4.7, 8.1, 8.5 |
|  | Time evolution without damping |  |  |  |
|  | Time evolution with damping (γ) |  |  |  |
|  | Steady-state solutions |  |  |  |
|  | Population inversion (w) and saturation |  |  |  |
|  | Bloch vector (u,v,w) and Pauli matrices |  |  |  |
|  | *Missing/Prereq:* Lindblad master equation framework |  |  |  |
| **4. Beam Splitters & Interferometry** | Classical beam splitter transformation matrices | 29–31 | 2.2 | 6.2, 6.3, 6.5 |
|  | 50:50 symmetric beam splitters and phase shifts |  |  |  |
|  | Mach-Zehnder interferometer |  |  |  |
|  | Ramsey interferometer |  |  |  |
|  | *Missing/Prereq:* Quantum treatment via creation/annihilation operators |  |  |  |
| **5. Field Quantization** | SHO formalism (a, a†) | 32–36 | 7.1, 7.3, 8.1 | 2.1, 2.4, 2.6 |
|  | Maxwell’s equations and Coulomb gauge |  |  |  |
|  | Wave equations |  |  |  |
|  | Quantization of vector potential |  |  |  |
|  | Single-mode fields |  |  |  |
|  | Fock (number) states |  |  |  |
|  | *Missing/Prereq:* Zero-point energy |  |  |  |
|  | *Missing/Prereq:* Vacuum fluctuations from non-commuting operators |  |  |  |


---

### Instructive Study Guide

**Phase 1: Semi-Classical Foundations (Fox)**
* Read **Fox Chapter 9 (9.1 - 9.5)**. This perfectly maps to your notes on TDPT, the Rotating Wave Approximation, and Rabi oscillations. Fox provides excellent visual diagrams of how the state amplitudes slosh back and forth.
* Work through the pulse area integrations (Assignment 2, Q2) alongside Fox's description of $\pi$ and $\pi/2$ pulses.

**Phase 2: Open Quantum Systems (Gerry & Knight + Simulation)**
Your notes dive heavily into the Optical Bloch Equations and damping.
* Use **Fox 9.6** to visualize the Bloch vector tracking on the Bloch sphere.
* Transition to **Gerry & Knight 4.7 and 8.1** to understand the density matrix formalism mathematically. G&K provides a more robust treatment of how environmental coupling leads to the decay rates ($\gamma$) you see in your equations.
* When tackling the Optical Bloch Equations and damping, writing a numerical simulation using Python and QuTiP is incredibly effective for visualizing the steady-state solutions and population inversion dynamics required for Assignment 2, Question 5.

**Phase 3: Moving to Fully Quantized Fields (Gerry & Knight)**
Once the semi-classical picture is solid, shift to treating the electromagnetic field as a quantum object.
* Read **Gerry & Knight Chapter 2 (2.1 - 2.4)**. Your notes on Maxwell's equations and the vector potential map exactly to G&K's derivation. This chapter will rigorously explain how to map the modes of the radiation field to the quantum harmonic oscillator operators ($\hat{a}$ and $\hat{a}^\dagger$).
* Read **Gerry & Knight Chapter 6 (6.2 - 6.3)** to bridge the gap between the classical Mach-Zehnder interferometer in your notes and its quantum mechanical equivalent.
