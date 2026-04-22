"""
sim_hamiltonian.py
==================

Core module for QuTiP master equation simulation of the QD-photon CNOT gate.

Builds the Jaynes-Cummings Hamiltonian for a 3-level quantum dot (QD)
coupled to a single-mode photonic crystal cavity, including all dissipation
channels via Lindblad collapse operators.

System Description:
-------------------
The QD has three relevant energy levels:
  |g⟩  : ground state (no exciton)
  |+⟩  : bright exciton, σ+ transition — COUPLED to cavity
  |−⟩  : bright exciton, σ− transition — DECOUPLED from cavity

The cavity is a single mode with annihilation operator â.

Hilbert Space:
  H = H_QD ⊗ H_cav = C³ ⊗ C^N
  where N is the Fock-space truncation (typically N=5 since n̄ ≈ 0.1).

Hamiltonian (rotating frame at probe frequency ω_L):
  H = Δ_c â†â + Δ_+ |+⟩⟨+| + Δ_− |−⟩⟨−|
      + g(â† σ_+ + â σ_+†)
      + ε(â + â†)

  where:
    Δ_c = ω_cav − ω_L   (cavity detuning from probe)
    Δ_+ = ω_+  − ω_L    (σ+ transition detuning)
    Δ_− = ω_−  − ω_L    (σ− transition detuning)
    g = 12.9 GHz         (vacuum Rabi coupling, σ+ only)
    ε = drive amplitude  (weak probe, n̄ ≈ 0.1)

Collapse Operators (Lindblad master equation):
  L1 = √κ â              — cavity photon loss
  L2 = √γ_+ |g⟩⟨+|      — σ+ spontaneous emission
  L3 = √γ_− |g⟩⟨−|      — σ− spontaneous emission (Purcell-modified)
  L4 = √γ_deph |+⟩⟨+|   — pure dephasing of |+⟩ state

References:
  Kim et al., Nature Photonics (2013), arXiv:1304.0776
  Supplementary Sections 2-4
"""

import numpy as np
import qutip

# ──────────────────────────────────────────────────────────────────────────────
# Physical parameters (all in GHz, i.e., frequency / 2π)
# ──────────────────────────────────────────────────────────────────────────────

# From paper: main text p.4, Supplementary Section 3
G_GHZ = 12.9          # QD-cavity coupling g/2π (GHz)
KAPPA_GHZ = 31.9      # Cavity decay rate κ/2π (GHz)
GAMMA_PLUS_GHZ = 1.887  # σ+ spontaneous emission rate γ_spon/2π (GHz)
                         # = 1/530 ps = 1.887 GHz
                         # NOTE: In the Lindblad ME, collapse op L = √γ_spon |g⟩⟨+|
                         # gives coherence decay at γ_spon/2 = 0.943 GHz,
                         # which matches the paper's γ (HL linewidth parameter).
SIGMA_I_GHZ = 5.2     # Spectral diffusion inhomogeneous width σ_I/2π (GHz)
GAMMA_DEPH_GHZ = 0.0  # Pure dephasing rate (negligible compared to σ_I)

# Default Fock space truncation
N_FOCK_DEFAULT = 5

# ──────────────────────────────────────────────────────────────────────────────
# QD state indices (in the 3-level basis {|g⟩, |+⟩, |−⟩})
# ──────────────────────────────────────────────────────────────────────────────
# We use the convention:
#   |0⟩ = |g⟩  (ground state)
#   |1⟩ = |+⟩  (σ+ exciton, cavity-coupled)
#   |2⟩ = |−⟩  (σ− exciton, cavity-decoupled)

IDX_G = 0    # Ground state
IDX_PLUS = 1  # |+⟩ state
IDX_MINUS = 2  # |−⟩ state
N_QD = 3      # QD Hilbert space dimension


# ══════════════════════════════════════════════════════════════════════════════
# QD OPERATORS (in the 3-level QD subspace)
# ══════════════════════════════════════════════════════════════════════════════

def qd_state(idx):
    """
    Return a QD basis state |idx⟩ as a QuTiP Qobj (ket).
    
    Parameters
    ----------
    idx : int
        State index: 0 = |g⟩, 1 = |+⟩, 2 = |−⟩
    
    Returns
    -------
    ket : qutip.Qobj
        Basis ket in the 3-level QD space.
    """
    return qutip.basis(N_QD, idx)


def qd_projector(idx):
    """
    Return the projector |idx⟩⟨idx| in the QD subspace.
    
    Parameters
    ----------
    idx : int
        State index: 0 = |g⟩, 1 = |+⟩, 2 = |−⟩
    
    Returns
    -------
    proj : qutip.Qobj
        Projector operator |idx⟩⟨idx|.
    """
    s = qd_state(idx)
    return s * s.dag()


def qd_transition(idx_upper, idx_lower):
    """
    Return the transition operator |upper⟩⟨lower| (lowering operator).
    
    For example, qd_transition(IDX_PLUS, IDX_G) returns |+⟩⟨g| which
    is the RAISING operator for the σ+ transition. Its conjugate |g⟩⟨+|
    is the lowering (emission) operator.
    
    Parameters
    ----------
    idx_upper : int
        Upper state index.
    idx_lower : int
        Lower state index.
    
    Returns
    -------
    op : qutip.Qobj
        Transition operator |upper⟩⟨lower|.
    """
    return qd_state(idx_upper) * qd_state(idx_lower).dag()


# ══════════════════════════════════════════════════════════════════════════════
# FULL SYSTEM OPERATORS (QD ⊗ cavity tensor product)
# ══════════════════════════════════════════════════════════════════════════════

def build_operators(N_cav=N_FOCK_DEFAULT):
    """
    Build all system operators in the full QD ⊗ cavity Hilbert space.
    
    The tensor product convention is: QD ⊗ cavity
    So a full-system operator is constructed as:
        qutip.tensor(qd_op, cav_op)
    
    Parameters
    ----------
    N_cav : int
        Fock space truncation for the cavity mode.
    
    Returns
    -------
    ops : dict
        Dictionary containing all system operators:
        - 'a'        : cavity annihilation operator â
        - 'adag'     : cavity creation operator â†
        - 'n_cav'    : cavity number operator â†â
        - 'I_qd'     : QD identity
        - 'I_cav'    : cavity identity
        - 'proj_g'   : projector |g⟩⟨g| ⊗ I_cav
        - 'proj_plus': projector |+⟩⟨+| ⊗ I_cav
        - 'proj_minus': projector |−⟩⟨−| ⊗ I_cav
        - 'sigma_plus_raise' : |+⟩⟨g| ⊗ I_cav  (QD raising, σ+ transition)
        - 'sigma_plus_lower' : |g⟩⟨+| ⊗ I_cav  (QD lowering, σ+ transition)
        - 'sigma_minus_raise': |−⟩⟨g| ⊗ I_cav  (QD raising, σ− transition)
        - 'sigma_minus_lower': |g⟩⟨−| ⊗ I_cav  (QD lowering, σ− transition)
    """
    # Subsystem identities
    I_qd = qutip.qeye(N_QD)
    I_cav = qutip.qeye(N_cav)
    
    # Cavity operators (I_qd ⊗ cav_op)
    a_bare = qutip.destroy(N_cav)
    a = qutip.tensor(I_qd, a_bare)
    adag = a.dag()
    n_cav = adag * a
    
    # QD projectors (qd_op ⊗ I_cav)
    proj_g = qutip.tensor(qd_projector(IDX_G), I_cav)
    proj_plus = qutip.tensor(qd_projector(IDX_PLUS), I_cav)
    proj_minus = qutip.tensor(qd_projector(IDX_MINUS), I_cav)
    
    # QD transition operators (qd_op ⊗ I_cav)
    # σ+ transition: |g⟩ ↔ |+⟩
    sigma_plus_raise = qutip.tensor(qd_transition(IDX_PLUS, IDX_G), I_cav)   # |+⟩⟨g|
    sigma_plus_lower = qutip.tensor(qd_transition(IDX_G, IDX_PLUS), I_cav)   # |g⟩⟨+|
    
    # σ− transition: |g⟩ ↔ |−⟩
    sigma_minus_raise = qutip.tensor(qd_transition(IDX_MINUS, IDX_G), I_cav)  # |−⟩⟨g|
    sigma_minus_lower = qutip.tensor(qd_transition(IDX_G, IDX_MINUS), I_cav)  # |g⟩⟨−|
    
    return {
        'a': a,
        'adag': adag,
        'n_cav': n_cav,
        'I_qd': I_qd,
        'I_cav': I_cav,
        'proj_g': proj_g,
        'proj_plus': proj_plus,
        'proj_minus': proj_minus,
        'sigma_plus_raise': sigma_plus_raise,
        'sigma_plus_lower': sigma_plus_lower,
        'sigma_minus_raise': sigma_minus_raise,
        'sigma_minus_lower': sigma_minus_lower,
    }


# ══════════════════════════════════════════════════════════════════════════════
# HAMILTONIAN BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def build_hamiltonian(ops, delta_c, delta_plus, delta_minus=None,
                      g=G_GHZ, epsilon=0.01):
    """
    Build the Jaynes-Cummings Hamiltonian in the rotating frame.
    
    H = Δ_c â†â + Δ_+ |+⟩⟨+| + Δ_− |−⟩⟨−|
        + g(â† |g⟩⟨+| + â |+⟩⟨g|)
        + ε(â + â†)
    
    Note: The JC interaction couples the cavity to the σ+ transition ONLY.
    The σ− transition is decoupled (different circular polarization +
    large Zeeman detuning from cavity).
    
    The interaction term is:
        g(â† σ_+ + â σ_+†) = g(â† |g⟩⟨+| + â |+⟩⟨g|)
    
    Wait — careful with conventions! In the standard JC model:
        H_int = g(â† σ_- + â σ_+)
    where σ_- = |g⟩⟨e| (lowering) and σ_+ = |e⟩⟨g| (raising).
    
    So: â† acts with σ_- (= |g⟩⟨+|): photon absorbed, QD de-excited → WRONG
    Actually: â† σ_- means cavity gains photon when QD emits → correct.
    
    The physical process is:
        â† |g⟩⟨+|  : QD goes |+⟩→|g⟩, cavity gains photon (emission into cavity)
        â |+⟩⟨g|   : QD goes |g⟩→|+⟩, cavity loses photon (absorption from cavity)
    
    Parameters
    ----------
    ops : dict
        Operators dictionary from build_operators().
    delta_c : float
        Cavity detuning Δ_c = ω_cav − ω_L (GHz).
    delta_plus : float
        σ+ transition detuning Δ_+ = ω_+ − ω_L (GHz).
        When σ+ is resonant with cavity: Δ_+ ≈ Δ_c (+ small shift Δ_0a).
    delta_minus : float, optional
        σ− transition detuning Δ_− = ω_− − ω_L (GHz).
        If None, set to a large value (100 GHz) since it's far detuned.
    g : float
        Vacuum Rabi coupling g/2π (GHz). Default: 12.9 GHz.
    epsilon : float
        Coherent drive amplitude (GHz). Should be weak (ε ≪ κ).
        Default: 0.01 GHz (gives n̄ ≈ 4ε²/κ² ≈ 4e-7, well in linear regime).
    
    Returns
    -------
    H : qutip.Qobj
        Full system Hamiltonian.
    """
    if delta_minus is None:
        delta_minus = 100.0  # Far detuned, effectively decoupled
    
    a = ops['a']
    adag = ops['adag']
    n_cav = ops['n_cav']
    proj_plus = ops['proj_plus']
    proj_minus = ops['proj_minus']
    sigma_plus_lower = ops['sigma_plus_lower']  # |g⟩⟨+|
    sigma_plus_raise = ops['sigma_plus_raise']  # |+⟩⟨g|
    
    # Free Hamiltonian terms
    H_cav = delta_c * n_cav                     # Δ_c â†â
    H_qd_plus = delta_plus * proj_plus           # Δ_+ |+⟩⟨+|
    H_qd_minus = delta_minus * proj_minus        # Δ_− |−⟩⟨−|
    
    # Jaynes-Cummings interaction (σ+ transition only)
    # g(â† |g⟩⟨+| + â |+⟩⟨g|)
    H_int = g * (adag * sigma_plus_lower + a * sigma_plus_raise)
    
    # Coherent drive (weak probe)
    H_drive = epsilon * (a + adag)
    
    # Total Hamiltonian
    H = H_cav + H_qd_plus + H_qd_minus + H_int + H_drive
    
    return H


def build_hamiltonian_bare_cavity(ops, delta_c, epsilon=0.01):
    """
    Build Hamiltonian for the bare cavity case (QD in |−⟩, no coupling).
    
    When the QD is in state |−⟩, the σ+ transition is Pauli-blocked
    (the electron state needed for |+⟩ is occupied). The cavity sees
    no QD interaction, so g_eff = 0.
    
    H = Δ_c â†â + ε(â + â†)
    
    Parameters
    ----------
    ops : dict
        Operators dictionary.
    delta_c : float
        Cavity detuning (GHz).
    epsilon : float
        Drive amplitude (GHz).
    
    Returns
    -------
    H : qutip.Qobj
        Bare cavity Hamiltonian.
    """
    return delta_c * ops['n_cav'] + epsilon * (ops['a'] + ops['adag'])


# ══════════════════════════════════════════════════════════════════════════════
# COLLAPSE OPERATORS (LINDBLAD DISSIPATION)
# ══════════════════════════════════════════════════════════════════════════════

def build_collapse_ops(ops, kappa=KAPPA_GHZ, gamma_plus=GAMMA_PLUS_GHZ,
                       gamma_minus=None, gamma_deph=GAMMA_DEPH_GHZ):
    """
    Build the list of collapse operators for the Lindblad master equation.
    
    The master equation is:
        dρ/dt = -i[H, ρ] + Σ_k (L_k ρ L_k† − ½{L_k† L_k, ρ})
    
    Collapse operators:
    
    1. L1 = √κ â
       Cavity photon loss at rate κ. This is the dominant decay channel.
       κ/2π = 31.9 GHz → cavity photon lifetime = 1/κ ≈ 5 ps.
    
    2. L2 = √γ_spon |g⟩⟨+|
       Spontaneous emission from |+⟩ → |g⟩ (σ+ transition).
       γ_spon/2π = 1.887 GHz (= 1/530 ps).
       This represents emission into NON-cavity modes (leaky modes).
       The cavity-enhanced emission is already included in H_int.
       
       IMPORTANT: The Lindblad term D[√γ |g⟩⟨+|] gives:
         - Population decay at rate γ_spon = 1.887 GHz
         - Coherence decay at rate γ_spon/2 = 0.943 GHz
       The paper's HL equations (Eq. 14) use γ = γ_spon/2 as the
       coherence linewidth, so these are consistent.
    
    3. L3 = √γ_− |g⟩⟨−|
       Spontaneous emission from |−⟩ → |g⟩ (σ− transition).
       γ_−/2π depends on detuning via Purcell effect (see Fig S4).
       Default: same as γ_+ (off-resonance Purcell suppression is small
       for the σ− transition since it's far detuned from cavity).
    
    4. L4 = √(γ_deph/2) |+⟩⟨+|
       Pure dephasing of |+⟩ state. At 4.3 K, pure dephasing is negligible
       compared to the inhomogeneous linewidth σ_I = 5.2 GHz.
       We set γ_deph = 0 by default (spectral diffusion is handled
       classically by averaging over Gaussian P(δ)).
    
    Parameters
    ----------
    ops : dict
        Operators dictionary from build_operators().
    kappa : float
        Cavity decay rate κ/2π (GHz).
    gamma_plus : float
        σ+ spontaneous emission rate γ_+/2π (GHz).
    gamma_minus : float, optional
        σ− spontaneous emission rate γ_−/2π (GHz).
        If None, defaults to gamma_plus.
    gamma_deph : float
        Pure dephasing rate γ_deph/2π (GHz).
    
    Returns
    -------
    c_ops : list of qutip.Qobj
        List of collapse operators for mesolve.
    """
    if gamma_minus is None:
        gamma_minus = gamma_plus
    
    c_ops = []
    
    # 1. Cavity photon loss: L1 = √κ â
    c_ops.append(np.sqrt(kappa) * ops['a'])
    
    # 2. σ+ spontaneous emission: L2 = √γ_+ |g⟩⟨+|
    c_ops.append(np.sqrt(gamma_plus) * ops['sigma_plus_lower'])
    
    # 3. σ− spontaneous emission: L3 = √γ_− |g⟩⟨−|
    if gamma_minus > 1e-10:
        c_ops.append(np.sqrt(gamma_minus) * ops['sigma_minus_lower'])
    
    # 4. Pure dephasing: L4 = √(γ_deph/2) |+⟩⟨+|
    #    The factor 1/2 converts from T2 dephasing rate to Lindblad rate.
    #    The Lindblad term γ_deph/2 × D[|+⟩⟨+|] gives dephasing at rate γ_deph.
    if gamma_deph > 1e-10:
        c_ops.append(np.sqrt(gamma_deph / 2.0) * ops['proj_plus'])
    
    return c_ops


# ══════════════════════════════════════════════════════════════════════════════
# INITIAL STATES
# ══════════════════════════════════════════════════════════════════════════════

def initial_state_qd_g(N_cav=N_FOCK_DEFAULT):
    """
    Initial state: QD in |g⟩, cavity in vacuum |0⟩.
    
    Returns
    -------
    rho0 : qutip.Qobj
        Density matrix |g,0⟩⟨g,0|.
    """
    psi = qutip.tensor(qd_state(IDX_G), qutip.basis(N_cav, 0))
    return qutip.ket2dm(psi)


def initial_state_qd_minus(N_cav=N_FOCK_DEFAULT):
    """
    Initial state: QD in |−⟩, cavity in vacuum |0⟩.
    
    Returns
    -------
    rho0 : qutip.Qobj
        Density matrix |−,0⟩⟨−,0|.
    """
    psi = qutip.tensor(qd_state(IDX_MINUS), qutip.basis(N_cav, 0))
    return qutip.ket2dm(psi)


def initial_state_qd_mixed(rho_minus, N_cav=N_FOCK_DEFAULT):
    """
    Initial state: QD in mixed state ρ_QD = ρ_−|−⟩⟨−| + (1−ρ_−)|g⟩⟨g|,
    cavity in vacuum.
    
    This represents the QD after a pump pulse with imperfect π-pulse
    preparation: probability ρ_− to be in |−⟩.
    
    Parameters
    ----------
    rho_minus : float
        Probability of QD being in |−⟩ (0 to 1).
    
    Returns
    -------
    rho0 : qutip.Qobj
        Mixed density matrix.
    """
    rho_g = initial_state_qd_g(N_cav)
    rho_m = initial_state_qd_minus(N_cav)
    return (1.0 - rho_minus) * rho_g + rho_minus * rho_m


# ══════════════════════════════════════════════════════════════════════════════
# STEADY-STATE REFLECTION COEFFICIENT
# ══════════════════════════════════════════════════════════════════════════════

def compute_reflection_coefficient(delta_c, ops, c_ops, qd_state_label='g',
                                   delta_0a=0.0, g=G_GHZ, epsilon=0.01,
                                   N_cav=N_FOCK_DEFAULT):
    """
    Compute the cavity reflection coefficient r(ω) at a single probe
    detuning using QuTiP's steady-state solver.
    
    Method:
    -------
    1. Build the Hamiltonian with the given detunings and drive ε
    2. Solve for steady state: ρ_ss = steadystate(H, c_ops)
    3. Extract ⟨â⟩_ss = Tr(ρ_ss â)
    4. Use input-output relation:
       
       r = 1 − κ⟨â⟩_ss / ε
       
       This follows from the input-output relation â_out = â_in − √κ â,
       combined with H_drive = ε(â+â†) where ε = √κ × α_in.
       So α_in = ε/√κ, and:
       r = â_out/â_in = 1 − √κ ⟨â⟩_ss / (ε/√κ) = 1 − κ⟨â⟩_ss / ε
    
    Parameters
    ----------
    delta_c : float
        Cavity detuning Δ_c = ω_cav − ω_L (GHz).
    ops : dict
        System operators from build_operators().
    c_ops : list
        Collapse operators from build_collapse_ops().
    qd_state_label : str
        'g' for ground state (coupled), '-' for |−⟩ (bare cavity).
    delta_0a : float
        Mean QD-cavity detuning Δ_0a = ω_QD − ω_cav (GHz).
    g : float
        Coupling strength g/2π (GHz).
    epsilon : float
        Drive amplitude (GHz).
    N_cav : int
        Fock space truncation.
    
    Returns
    -------
    r : complex
        Reflection coefficient at this probe frequency.
    """
    kappa = KAPPA_GHZ  # Use the global value for consistency
    
    if qd_state_label == '-':
        # QD in |−⟩: bare cavity, no JC coupling
        # For bare cavity, we can use a simplified 1D model, but for
        # consistency we use the full Hilbert space with g=0.
        H = build_hamiltonian(ops, delta_c, delta_plus=delta_c + delta_0a,
                              g=0.0, epsilon=epsilon)
    else:
        # QD in |g⟩: full JC coupling
        delta_plus = delta_c + delta_0a  # σ+ detuning from probe
        H = build_hamiltonian(ops, delta_c, delta_plus=delta_plus,
                              g=g, epsilon=epsilon)
    
    # Solve for steady state
    rho_ss = qutip.steadystate(H, c_ops)
    
    # Extract ⟨â⟩_ss
    a_expect = qutip.expect(ops['a'], rho_ss)
    
    # Input-output relation derivation:
    # ─────────────────────────────────
    # The Hamiltonian drive H = ε(â + â†) gives the Heisenberg equation:
    #   dâ/dt = -(iΔ_c + κ/2)â - igσ_- - iε
    #
    # Comparing with the Heisenberg-Langevin equation:
    #   dâ/dt = -(iΔ_c + κ/2)â - igσ_- + √κ α_in
    #
    # We identify: √κ α_in = -iε  →  α_in = -iε/√κ
    #
    # The input-output relation (Gardiner convention, matches paper Eq. 20):
    #   α_out = α_in - √κ ⟨â⟩_ss
    #
    # Therefore:
    #   r = α_out/α_in = 1 - √κ ⟨â⟩_ss / α_in
    #     = 1 - √κ ⟨â⟩_ss / (-iε/√κ)
    #     = 1 - iκ ⟨â⟩_ss / ε
    #
    # Verification: bare cavity at resonance → ⟨â⟩ = -2iε/κ
    #   r = 1 - iκ(-2iε/κ)/ε = 1 - 2 = -1 ✓
    r = 1.0 - 1j * kappa * a_expect / epsilon
    
    return r


def compute_reflection_spectrum(delta_c_array, ops, c_ops,
                                qd_state_label='g', delta_0a=0.0,
                                g=G_GHZ, epsilon=0.01,
                                N_cav=N_FOCK_DEFAULT):
    """
    Compute the reflection coefficient r(ω) over an array of probe detunings.
    
    Parameters
    ----------
    delta_c_array : array-like
        Array of cavity detunings Δ_c (GHz).
    ops, c_ops, qd_state_label, delta_0a, g, epsilon, N_cav :
        Same as compute_reflection_coefficient().
    
    Returns
    -------
    r_array : complex ndarray
        Reflection coefficient at each detuning.
    """
    delta_c_array = np.asarray(delta_c_array)
    r_array = np.zeros(len(delta_c_array), dtype=complex)
    
    for i, dc in enumerate(delta_c_array):
        r_array[i] = compute_reflection_coefficient(
            dc, ops, c_ops, qd_state_label=qd_state_label,
            delta_0a=delta_0a, g=g, epsilon=epsilon, N_cav=N_cav
        )
    
    return r_array


# ══════════════════════════════════════════════════════════════════════════════
# PURCELL DECAY RATE (from paper Supplementary Section 4)
# ══════════════════════════════════════════════════════════════════════════════

def purcell_decay_rate(delta_ghz, g=G_GHZ, kappa=KAPPA_GHZ):
    """
    Compute the Purcell-modified decay rate of the |−⟩ state.
    
    From Supplementary Section 4:
        σ_− = 4g²κ / (4Δ² + κ²) + σ_0
    
    where σ_0 = 1/530 ps = 1.887 GHz is the background decay rate
    (leaky modes + nonradiative).
    
    Parameters
    ----------
    delta_ghz : float or array
        Detuning between σ− transition and cavity Δ/2π (GHz).
    g : float
        Coupling g/2π (GHz).
    kappa : float
        Cavity decay rate κ/2π (GHz).
    
    Returns
    -------
    sigma_minus : float or array
        Total decay rate σ_−/2π (GHz).
    """
    delta = np.asarray(delta_ghz, dtype=float)
    sigma_0 = 1.0 / 0.530   # 1/(530 ps) in GHz = 1.887 GHz
    purcell = 4.0 * g**2 * kappa / (4.0 * delta**2 + kappa**2)
    return purcell + sigma_0


# ══════════════════════════════════════════════════════════════════════════════
# SELF-TEST / VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("sim_hamiltonian.py — Self-Test & Validation")
    print("=" * 70)
    
    N_cav = N_FOCK_DEFAULT
    ops = build_operators(N_cav)
    c_ops = build_collapse_ops(ops)
    
    print(f"\nHilbert space dimension: {N_QD} × {N_cav} = {N_QD * N_cav}")
    print(f"Number of collapse operators: {len(c_ops)}")
    
    # ── Test 1: Bare cavity at resonance should give r = -1 ──
    print("\n--- Test 1: Bare cavity (g=0) at resonance ---")
    r_bare = compute_reflection_coefficient(
        delta_c=0.0, ops=ops, c_ops=c_ops,
        qd_state_label='-', delta_0a=0.0, g=0.0, epsilon=0.01
    )
    print(f"  r(Δ_c=0, bare) = {r_bare:.4f}")
    print(f"  Expected: -1.0000")
    print(f"  |error| = {abs(r_bare - (-1.0)):.2e}")
    
    # ── Test 2: Coupled cavity at resonance should give r ≈ (C-1)/(C+1) ──
    print("\n--- Test 2: Coupled cavity (g=12.9) at resonance ---")
    # Paper's cooperativity uses coherence linewidth γ = γ_spon/2:
    gamma_coherence = GAMMA_PLUS_GHZ / 2.0  # = 0.943 GHz
    C = 2.0 * G_GHZ**2 / (KAPPA_GHZ * gamma_coherence)
    r_expected = (C - 1.0) / (C + 1.0)
    
    r_coupled = compute_reflection_coefficient(
        delta_c=0.0, ops=ops, c_ops=c_ops,
        qd_state_label='g', delta_0a=0.0, g=G_GHZ, epsilon=0.01
    )
    print(f"  Cooperativity C = 2g²/(κγ) = {C:.2f}  (γ = γ_spon/2 = {gamma_coherence:.3f} GHz)")
    print(f"  r(Δ_c=0, coupled) = {r_coupled.real:.4f} + {r_coupled.imag:.4f}j")
    print(f"  Expected (analytical): r = (C-1)/(C+1) = {r_expected:.4f}")
    print(f"  |error| = {abs(r_coupled.real - r_expected):.2e}")
    
    # ── Test 3: Cavity photon number check ──
    print("\n--- Test 3: Mean photon number in cavity ---")
    H_test = build_hamiltonian(ops, delta_c=0.0, delta_plus=0.0,
                                g=G_GHZ, epsilon=0.01)
    rho_ss = qutip.steadystate(H_test, c_ops)
    n_mean = qutip.expect(ops['n_cav'], rho_ss)
    print(f"  ⟨n⟩ = {n_mean:.6f}")
    print(f"  Weak probe condition: ⟨n⟩ ≪ 1 ? {'YES ✓' if n_mean < 0.01 else 'NO ✗'}")
    
    # ── Test 4: QD populations in steady state ──
    print("\n--- Test 4: QD populations in steady state ---")
    pg = qutip.expect(ops['proj_g'], rho_ss)
    pp = qutip.expect(ops['proj_plus'], rho_ss)
    pm = qutip.expect(ops['proj_minus'], rho_ss)
    print(f"  P(g) = {pg:.6f}")
    print(f"  P(+) = {pp:.6f}")
    print(f"  P(−) = {pm:.6f}")
    print(f"  Sum  = {pg+pp+pm:.6f} (should be 1.0)")
    
    print("\n" + "=" * 70)
    print("Self-test complete.")
    print("=" * 70)
