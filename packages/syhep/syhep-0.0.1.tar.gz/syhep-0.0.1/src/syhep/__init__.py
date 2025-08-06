# pyright: reportOperatorIssue=false
# pyright: reportArgumentType=false
# pyright: reportAssignmentType=false
# pyright: reportReturnType=false

"""
Symbolic calculations for High Energy Particle physics using Python and Sympy

This module provides symbolic computations for particle physics calculations
including gamma matrices, spinors, polarization vectors, and scattering amplitudes.

References to Professor Christoph Berger's book:
"Particle Physics: From the Basics to Modern Experiments", ISBN-13: 9783662717059
"""

from sympy.combinatorics.permutations import Permutation
import sympy as sy
from typing import List, Union, Literal



# Type aliases for clarity
Matrix4x4 = sy.Matrix  # 4x4 matrix
Matrix2x2 = sy.Matrix  # 2x2 matrix
FourVector = Union[sy.Matrix, List[sy.Expr]]  # Four-momentum vector
SpinorIndex = Union[int, Literal[-1, 0, 1]]  # Helicity index
Expr = sy.Expr  # Symbolic expression

# Dirac gamma matrices and identity matrix
Eins: Matrix4x4 = sy.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
"""4x4 identity matrix"""

g0: Matrix4x4 = sy.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]])
"""Gamma^0 matrix (timelike component)"""

g1: Matrix4x4 = sy.Matrix([[0, 0, 0, 1], [0, 0, 1, 0], [0, -1, 0, 0], [-1, 0, 0, 0]])
"""Gamma^1 matrix (x-component)"""

g2: Matrix4x4 = sy.Matrix([[0, 0, 0, -sy.I], [0, 0, sy.I, 0],
             [0, sy.I, 0, 0], [-sy.I, 0, 0, 0]])
"""Gamma^2 matrix (y-component)"""

g3: Matrix4x4 = sy.Matrix([[0, 0, 1, 0], [0, 0, 0, -1], [-1, 0, 0, 0], [0, 1, 0, 0]])
"""Gamma^3 matrix (z-component)"""

g5: Matrix4x4 = sy.Matrix([[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]])
"""Gamma^5 matrix (chirality matrix)"""

one: Matrix4x4 = sy.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
"""4x4 identity matrix (alias)"""

# Chiral projection operators
proj_r: Matrix4x4 = (one + g5) / 2
"""Right-handed chiral projection operator (1+γ5)/2"""

proj_l: Matrix4x4 = (one - g5) / 2
"""Left-handed chiral projection operator (1-γ5)/2"""

# Pauli matrices (chapter 2.2 or 2.8)
sig1: Matrix2x2 = sy.Matrix([[0, 1], [1, 0]])
"""Pauli matrix σ₁ (x-component)"""

sig2: Matrix2x2 = sy.Matrix([[0, -sy.I], [sy.I, 0]])
"""Pauli matrix σ₂ (y-component)"""

sig3: Matrix2x2 = sy.Matrix([[1, 0], [0, -1]])
"""Pauli matrix σ₃ (z-component)"""


def chi1(theta: Expr, phi: Expr) -> sy.Matrix:
    """
    First component of 2-spinor in spherical coordinates.
    
    Args:
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        2x1 spinor matrix
    """
    elm1 = sy.cos(theta / 2)
    elm2 = sy.exp(sy.I * phi) * sy.sin(theta / 2)
    result = sy.Matrix([[elm1], [elm2]])
    return result


def chi2(theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Second component of 2-spinor in spherical coordinates.
    
    Args:
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        2x1 spinor matrix
    """
    elm1: Expr = -sy.exp(-sy.I * phi) * sy.sin(theta / 2)
    elm2: Expr = sy.cos(theta / 2)
    result = sy.Matrix([[elm1], [elm2]])
    return result


# Helicity spinors (chapter 3.1)
def u_min(Ef: Expr, mf: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Negative helicity particle spinor u(p,-1/2).
    
    Args:
        Ef: Energy of particle
        mf: Mass of particle
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4x1 Dirac spinor
    """
    elm1 = -sy.exp(-sy.I * phi) * sy.sin(theta / 2)
    elm2 = sy.cos(theta / 2)
    fac1 = sy.sqrt(Ef - mf) / sy.sqrt(Ef + mf)
    fac2 = sy.sqrt(Ef + mf)
    elm3 = -fac1 * elm1
    elm4 = -fac1 * elm2
    result = fac2 * sy.Matrix([[elm1], [elm2], [elm3], [elm4]])
    return result


def u_plus(Ef: Expr, mf: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Positive helicity particle spinor u(p,+1/2).
    
    Args:
        Ef: Energy of particle
        mf: Mass of particle
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4x1 Dirac spinor
    """
    elm2 = sy.exp(sy.I * phi) * sy.sin(theta / 2)
    elm1 = sy.cos(theta / 2)
    fac1 = sy.sqrt(Ef - mf) / sy.sqrt(Ef + mf)
    fac2 = sy.sqrt(Ef + mf)
    elm3 = fac1 * elm1
    elm4 = fac1 * elm2
    result = fac2 * sy.Matrix([[elm1], [elm2], [elm3], [elm4]])
    return result


def v_min(Ef: Expr, mf: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Negative helicity antiparticle spinor v(p,-1/2).
    
    Args:
        Ef: Energy of antiparticle
        mf: Mass of antiparticle
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4x1 Dirac spinor
    """
    elm4 = sy.exp(sy.I * phi) * sy.sin(theta / 2)
    elm3 = sy.cos(theta / 2)
    fac1 = sy.sqrt(Ef - mf) / sy.sqrt(Ef + mf)
    fac2 = sy.sqrt(Ef + mf)
    elm1 = fac1 * elm3
    elm2 = fac1 * elm4
    result = fac2 * sy.Matrix([[elm1], [elm2], [elm3], [elm4]])
    return result


def v_plus(Ef: Expr, mf: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Positive helicity antiparticle spinor v(p,+1/2).
    
    Args:
        Ef: Energy of antiparticle
        mf: Mass of antiparticle
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4x1 Dirac spinor
    """
    elm3 = -sy.exp(-sy.I * phi) * sy.sin(theta / 2)
    elm4 = sy.cos(theta / 2)
    fac1 = sy.sqrt(Ef - mf) / sy.sqrt(Ef + mf)
    fac2 = sy.sqrt(Ef + mf)
    elm1 = -fac1 * elm3
    elm2 = -fac1 * elm4
    result = fac2 * sy.Matrix([[elm1], [elm2], [elm3], [elm4]])
    return result


def u_minbar(Ef: Expr, mf: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Adjoint of negative helicity particle spinor ū(p,-1/2).
    
    Args:
        Ef: Energy of particle
        mf: Mass of particle
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        1x4 adjoint spinor
    """
    h1 = u_min(Ef, mf, theta, phi).T * g0
    elm1 = h1[0] * sy.exp(2 * sy.I * phi)
    elm2 = h1[1]
    elm3 = h1[2] * sy.exp(2 * sy.I * phi)
    elm4 = h1[3]
    result = sy.Matrix([[elm1, elm2, elm3, elm4]])
    return result


def u_plusbar(Ef: Expr, mf: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Adjoint of positive helicity particle spinor ū(p,+1/2).
    
    Args:
        Ef: Energy of particle
        mf: Mass of particle
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        1x4 adjoint spinor
    """
    h1 = u_plus(Ef, mf, theta, phi).T * g0
    elm2 = h1[1] * sy.exp(-2 * sy.I * phi)
    elm1 = h1[0]
    elm4 = h1[3] * sy.exp(-2 * sy.I * phi)
    elm3 = h1[2]
    result = sy.Matrix([[elm1, elm2, elm3, elm4]])
    return result


def v_minbar(Ef: Expr, mf: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Adjoint of negative helicity antiparticle spinor v̄(p,-1/2).
    
    Args:
        Ef: Energy of antiparticle
        mf: Mass of antiparticle  
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        1x4 adjoint spinor
    """
    h1 = v_min(Ef, mf, theta, phi).T * g0
    elm2 = h1[1] * sy.exp(-2 * sy.I * phi)
    elm1 = h1[0]
    elm4 = h1[3] * sy.exp(-2 * sy.I * phi)
    elm3 = h1[2]
    result = sy.Matrix([[elm1, elm2, elm3, elm4]])
    return result


def v_plusbar(Ef: Expr, mf: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Adjoint of positive helicity antiparticle spinor v̄(p,+1/2).
    
    Args:
        Ef: Energy of antiparticle
        mf: Mass of antiparticle
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        1x4 adjoint spinor
    """
    h1 = v_plus(Ef, mf, theta, phi).T * g0
    elm1 = h1[0] * sy.exp(2 * sy.I * phi)
    elm2 = h1[1]
    elm3 = h1[2] * sy.exp(2 * sy.I * phi)
    elm4 = h1[3]
    result = sy.Matrix([[elm1, elm2, elm3, elm4]])
    return result


def u(pp: FourVector, ha: SpinorIndex) -> sy.Matrix:
    """
    Particle spinor u(p,λ) with specified helicity.
    
    Args:
        pp: Four-momentum [E, m, θ, φ]
        ha: Helicity (1: positive, 0: null, -1: negative)
        
    Returns:
        4x1 Dirac spinor
    """
    if ha >= 0:
        result = u_plus(pp[0], pp[1], pp[2], pp[3])
    elif ha < 0:
        result = u_min(pp[0], pp[1], pp[2], pp[3])
    return result


def v(pp: FourVector, ha: SpinorIndex) -> sy.Matrix:
    """
    Antiparticle spinor v(p,λ) with specified helicity.
    
    Args:
        pp: Four-momentum [E, m, θ, φ]
        ha: Helicity (1: positive, 0: null, -1: negative)
        
    Returns:
        4x1 Dirac spinor
    """
    if ha >= 0:
        result = v_plus(pp[0], pp[1], pp[2], pp[3])
    elif ha < 0:
        result = v_min(pp[0], pp[1], pp[2], pp[3])
    return result


def ubar(pp: FourVector, ha: SpinorIndex) -> sy.Matrix:
    """
    Adjoint particle spinor ū(p,λ) with specified helicity.
    
    Args:
        pp: Four-momentum [E, m, θ, φ]
        ha: Helicity (1: positive, 0: null, -1: negative)
        
    Returns:
        1x4 adjoint spinor
    """
    if ha >= 0:
        result = u_plusbar(pp[0], pp[1], pp[2], pp[3])
    elif ha < 0:
        result = u_minbar(pp[0], pp[1], pp[2], pp[3])
    return result


def vbar(pp: FourVector, ha: SpinorIndex) -> sy.Matrix:
    """
    Adjoint antiparticle spinor v̄(p,λ) with specified helicity.
    
    Args:
        pp: Four-momentum [E, m, θ, φ]
        ha: Helicity (1: positive, 0: null, -1: negative)
        
    Returns:
        1x4 adjoint spinor
    """
    if ha >= 0:
        result = v_plusbar(pp[0], pp[1], pp[2], pp[3])
    elif ha < 0:
        result = v_minbar(pp[0], pp[1], pp[2], pp[3])
    return result


# Polarization vectors for photons and W bosons (chapters 2.4 and 3.2)
def pol_plus(theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Positive helicity polarization vector ε⁺(θ,φ).
    
    Args:
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4-component polarization vector
    """
    elm1 = 0
    h1 = sy.cos(theta / 2) ** 2 - sy.sin(theta / 2) ** 2
    h2 = 2 * sy.sin(theta / 2) * sy.cos(theta / 2)
    elm2 = sy.sqrt(2) * sy.cos(phi) * h1 / 2 - sy.I * sy.sqrt(2) * sy.sin(phi) / 2
    elm3 = sy.sqrt(2) * sy.sin(phi) * h1 / 2 + sy.I * sy.sqrt(2) * sy.cos(phi) / 2
    elm4 = -sy.sqrt(2) * h2 / 2
    result = [elm1, elm2, elm3, elm4]
    return sy.Matrix(result)


def pol_min(theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Negative helicity polarization vector ε⁻(θ,φ).
    
    Args:
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4-component polarization vector
    """
    elm1 = 0
    h1 = sy.cos(theta / 2) ** 2 - sy.sin(theta / 2) ** 2
    h2 = 2 * sy.sin(theta / 2) * sy.cos(theta / 2)
    elm2 = sy.sqrt(2) * sy.cos(phi) * h1 / 2 + sy.I * sy.sqrt(2) * sy.sin(phi) / 2
    elm3 = sy.sqrt(2) * sy.sin(phi) * h1 / 2 - sy.I * sy.sqrt(2) * sy.cos(phi) / 2
    elm4 = -sy.sqrt(2) * h2 / 2
    result = [elm1, elm2, elm3, elm4]
    return sy.Matrix(result)


def pol_0(e0: Expr, m0: Expr, theta: Expr, phi: Expr) -> sy.Matrix:
    """
    Longitudinal polarization vector ε⁰(E,m,θ,φ) for massive bosons.
    
    Args:
        e0: Energy
        m0: Mass
        theta: Polar angle
        phi: Azimuthal angle
        
    Returns:
        4-component polarization vector
    """
    elm1 = sy.sqrt(e0**2 - m0**2) / m0
    elm2 = e0 * sy.sin(theta) * sy.cos(phi) / m0
    elm3 = e0 * sy.sin(theta) * sy.sin(phi) / m0
    elm4 = e0 * sy.cos(theta) / m0
    result = [elm1, elm2, elm3, elm4]
    return sy.Matrix(result)


def pol(pp: FourVector, ha: SpinorIndex) -> sy.Matrix:
    """
    Polarization vector ε(p,λ) with specified helicity.
    
    Args:
        pp: Four-momentum [E, m, θ, φ]
        ha: Helicity (1: positive, 0: longitudinal, -1: negative)
        
    Returns:
        4-component polarization vector
    """
    e0 = pp[0]
    m0 = pp[1]
    theta = pp[2]
    phi = pp[3]
    if ha > 0:
        result = pol_plus(theta, phi)
    elif ha < 0:
        result = pol_min(theta, phi)
    else:
        result = pol_0(e0, m0, theta, phi)
    return result


def polbar(pp: FourVector, ha: SpinorIndex) -> sy.Matrix:
    """
    Complex conjugate polarization vector ε*(p,λ).
    
    Args:
        pp: Four-momentum [E, m, θ, φ]
        ha: Helicity (1: positive, 0: longitudinal, -1: negative)
        
    Returns:
        Transposed complex conjugate polarization vector
    """
    e0 = pp[0]
    m0 = pp[1]
    theta = pp[2]
    phi = pp[3]
    if ha > 0:
        result = pol_min(theta, phi)
    elif ha < 0:
        result = pol_plus(theta, phi)
    else:
        result = pol_0(e0, m0, theta, phi)
    return sy.transpose(result)


# Utility functions for calculations
def fourvec(pp: FourVector) -> sy.Matrix:
    """
    Convert (E, m, θ, φ) to Cartesian four-momentum (E, px, py, pz).
    
    Args:
        pp: Four-momentum in spherical form [E, m, θ, φ]
        
    Returns:
        Cartesian four-momentum [E, px, py, pz]
    """
    elm1 = pp[0]  # Energy
    elm2 = pp[1]  # Mass
    elm3 = pp[2]  # Theta
    elm4 = pp[3]  # Phi

    h0 = elm3 / 2
    h1 = 2 * sy.sin(h0) * sy.cos(h0)  # sin(θ)
    h2 = (sy.cos(h0) ** 2) - (sy.sin(h0) ** 2)  # cos(θ)
    p = sy.sqrt(elm1**2 - elm2**2)  # |p|
    
    result = sy.Matrix([elm1, p * h1 * sy.cos(elm4), p * h1 * sy.sin(elm4), p * h2])
    return result


def dotprod4(jj1: FourVector, jj2: FourVector) -> Expr:
    """
    Calculate Minkowski dot product of two four-vectors.
    
    Args:
        jj1: First four-vector
        jj2: Second four-vector
        
    Returns:
        Scalar product with metric (+,-,-,-)
    """
    h1 = jj1[0] * jj2[0] - jj1[1] * jj2[1] - jj1[2] * jj2[2] - jj1[3] * jj2[3]
    result = sy.simplify(h1)
    return result


def dag(pp: FourVector) -> Matrix4x4:
    """
    Construct Feynman slash notation: p̸ = γᵘpᵤ.
    
    Args:
        pp: Four-momentum vector
        
    Returns:
        4x4 Dirac matrix representing p̸
    """
    elm1 = pp[0]
    elm2 = pp[1]
    elm3 = pp[2]
    elm4 = pp[3]
    result = elm1 * g0 - elm2 * g1 - elm3 * g2 - elm4 * g3
    return result


# QED current calculations (chapter 3.2)
def ubv(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate QED current ū(p1,h1)γᵘv(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle  
        h2: Helicity of second particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    j0 = ubar(p1, h1) * g0 * v(p2, h2)
    j1 = ubar(p1, h1) * g1 * v(p2, h2)
    j2 = ubar(p1, h1) * g2 * v(p2, h2)
    j3 = ubar(p1, h1) * g3 * v(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def ubu(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate QED current ū(p1,h1)γᵘu(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    j0 = ubar(p1, h1) * g0 * u(p2, h2)
    j1 = ubar(p1, h1) * g1 * u(p2, h2)
    j2 = ubar(p1, h1) * g2 * u(p2, h2)
    j3 = ubar(p1, h1) * g3 * u(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def vbu(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate QED current v̄(p1,h1)γᵘu(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    j0 = vbar(p1, h1) * g0 * u(p2, h2)
    j1 = vbar(p1, h1) * g1 * u(p2, h2)
    j2 = vbar(p1, h1) * g2 * u(p2, h2)
    j3 = vbar(p1, h1) * g3 * u(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def vbv(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate QED current v̄(p1,h1)γᵘv(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    j0 = vbar(p1, h1) * g0 * v(p2, h2)
    j1 = vbar(p1, h1) * g1 * v(p2, h2)
    j2 = vbar(p1, h1) * g2 * v(p2, h2)
    j3 = vbar(p1, h1) * g3 * v(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


# Weak interaction currents with (1-γ₅) coupling (chapter 6.1)
def ubvw(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate weak current ū(p1,h1)γᵘ(1-γ₅)v(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    j0 = ubar(p1, h1) * g0 * proj_l * v(p2, h2)
    j1 = ubar(p1, h1) * g1 * proj_l * v(p2, h2)
    j2 = ubar(p1, h1) * g2 * proj_l * v(p2, h2)
    j3 = ubar(p1, h1) * g3 * proj_l * v(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def ubuw(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate weak current ū(p1,h1)γᵘ(1-γ₅)u(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    j0 = ubar(p1, h1) * g0 * proj_l * u(p2, h2)
    j1 = ubar(p1, h1) * g1 * proj_l * u(p2, h2)
    j2 = ubar(p1, h1) * g2 * proj_l * u(p2, h2)
    j3 = ubar(p1, h1) * g3 * proj_l * u(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def vbuw(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate weak current v̄(p1,h1)γᵘ(1-γ₅)u(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    j0 = vbar(p1, h1) * g0 * proj_l * u(p2, h2)
    j1 = vbar(p1, h1) * g1 * proj_l * u(p2, h2)
    j2 = vbar(p1, h1) * g2 * proj_l * u(p2, h2)
    j3 = vbar(p1, h1) * g3 * proj_l * u(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def vbvw(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate weak current v̄(p1,h1)γᵘ(1-γ₅)v(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    j0 = vbar(p1, h1) * g0 * proj_l * v(p2, h2)
    j1 = vbar(p1, h1) * g1 * proj_l * v(p2, h2)
    j2 = vbar(p1, h1) * g2 * proj_l * v(p2, h2)
    j3 = vbar(p1, h1) * g3 * proj_l * v(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


# Vector-axial currents with cv-ca*γ₅ coupling (chapter 6.4)
def ubvva(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex, cv: Expr, ca: Expr) -> List[Expr]:
    """
    Calculate vector-axial current ū(p1,h1)γᵘ(cv-ca*γ₅)v(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        cv: Vector coupling constant
        ca: Axial coupling constant
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    gv = cv / 2
    ga = ca / 2
    j0 = ubar(p1, h1) * g0 * (gv * one - ga * g5) * v(p2, h2)
    j1 = ubar(p1, h1) * g1 * (gv * one - ga * g5) * v(p2, h2)
    j2 = ubar(p1, h1) * g2 * (gv * one - ga * g5) * v(p2, h2)
    j3 = ubar(p1, h1) * g3 * (gv * one - ga * g5) * v(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def ubuva(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex, cv: Expr, ca: Expr) -> List[Expr]:
    """
    Calculate vector-axial current ū(p1,h1)γᵘ(cv-ca*γ₅)u(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        cv: Vector coupling constant
        ca: Axial coupling constant
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    gv = cv / 2
    ga = ca / 2
    j0 = ubar(p1, h1) * g0 * (gv * one - ga * g5) * u(p2, h2)
    j1 = ubar(p1, h1) * g1 * (gv * one - ga * g5) * u(p2, h2)
    j2 = ubar(p1, h1) * g2 * (gv * one - ga * g5) * u(p2, h2)
    j3 = ubar(p1, h1) * g3 * (gv * one - ga * g5) * u(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def vbuva(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex, cv: Expr, ca: Expr) -> List[Expr]:
    """
    Calculate vector-axial current v̄(p1,h1)γᵘ(cv-ca*γ₅)u(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        cv: Vector coupling constant
        ca: Axial coupling constant
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    gv = cv / 2
    ga = ca / 2
    j0 = vbar(p1, h1) * g0 * (gv * one - ga * g5) * u(p2, h2)
    j1 = vbar(p1, h1) * g1 * (gv * one - ga * g5) * u(p2, h2)
    j2 = vbar(p1, h1) * g2 * (gv * one - ga * g5) * u(p2, h2)
    j3 = vbar(p1, h1) * g3 * (gv * one - ga * g5) * u(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


def vbvva(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex, cv: Expr, ca: Expr) -> List[Expr]:
    """
    Calculate vector-axial current v̄(p1,h1)γᵘ(cv-ca*γ₅)v(p2,h2).
    
    Args:
        p1: Four-momentum of first particle
        h1: Helicity of first particle
        p2: Four-momentum of second particle
        h2: Helicity of second particle
        cv: Vector coupling constant
        ca: Axial coupling constant
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    gv = cv / 2
    ga = ca / 2
    j0 = vbar(p1, h1) * g0 * (gv * one - ga * g5) * v(p2, h2)
    j1 = vbar(p1, h1) * g1 * (gv * one - ga * g5) * v(p2, h2)
    j2 = vbar(p1, h1) * g2 * (gv * one - ga * g5) * v(p2, h2)
    j3 = vbar(p1, h1) * g3 * (gv * one - ga * g5) * v(p2, h2)
    result = [sy.simplify(j0[0]), sy.simplify(j1[0]), sy.simplify(j2[0]), sy.simplify(j3[0])]
    return result


# Pauli form factor currents (chapter 5.2)
def ubuP(p1: FourVector, h1: SpinorIndex, p2: FourVector, h2: SpinorIndex) -> List[Expr]:
    """
    Calculate Pauli current ū(p1,h1)[σᵘᵛqᵥ/(4M)]u(p2,h2) for form factors.
    
    Args:
        p1: Four-momentum of initial particle
        h1: Helicity of initial particle
        p2: Four-momentum of final particle
        h2: Helicity of final particle
        
    Returns:
        List of four current components [J⁰, J¹, J², J³]
    """
    M = p1[1]  # Mass
    p14 = fourvec(p1) 
    p24 = fourvec(p2)
    
    # Four-momentum transfer qμ with lower index
    q0 = p14[0] - p24[0]
    q1 = -p14[1] + p24[1]
    q2 = -p14[2] + p24[2]
    q3 = -p14[3] + p24[3]
    
    # σᵘᵛ tensors (without factor i/2)
    jF0 = (g0 * g1 - g1 * g0) * q1 + (g0 * g2 - g2 * g0) * q2 + (g0 * g3 - g3 * g0) * q3
    jF1 = (g1 * g0 - g0 * g1) * q0 + (g1 * g2 - g2 * g1) * q2 + (g1 * g3 - g3 * g1) * q3
    jF2 = (g2 * g0 - g0 * g2) * q0 + (g2 * g1 - g1 * g2) * q1 + (g2 * g3 - g3 * g2) * q3
    jF3 = (g3 * g0 - g0 * g3) * q0 + (g3 * g1 - g1 * g3) * q1 + (g3 * g2 - g2 * g3) * q2
    
    j0 = ubar(p1, h1) * jF0 / 4 / M * u(p2, h2)
    j1 = ubar(p1, h1) * jF1 / 4 / M * u(p2, h2)
    j2 = ubar(p1, h1) * jF2 / 4 / M * u(p2, h2)
    j3 = ubar(p1, h1) * jF3 / 4 / M * u(p2, h2)
    
    # Include factor i/2
    result = [-j0[0], -j1[0], -j2[0], -j3[0]]
    return result


# Compton scattering amplitudes
def compts(k1: FourVector, hk1: SpinorIndex, p1: FourVector, hp1: SpinorIndex, 
           k2: FourVector, hk2: SpinorIndex, p2: FourVector, hp2: SpinorIndex) -> Expr:
    """
    Calculate s-channel amplitude for Compton scattering γ(k1) + e(p1) → γ(k2) + e(p2).
    
    Args:
        k1: Initial photon four-momentum
        hk1: Initial photon helicity
        p1: Initial electron four-momentum
        hp1: Initial electron helicity
        k2: Final photon four-momentum
        hk2: Final photon helicity
        p2: Final electron four-momentum
        hp2: Final electron helicity
        
    Returns:
        s-channel scattering amplitude
    """
    ke = fourvec(k1)
    pe = fourvec(p1)
    mm = p1[1]
    mk = k1[1]
    nenner = 2 * dotprod4(ke, pe) + mk**2
    
    epsbar = polbar(k2, hk2)
    eps = pol(k1, hk1)
    kern = dag(epsbar) * (dag(ke) + dag(pe) + mm * one) * dag(eps)
    h1 = sy.simplify(ubar(p2, hp2) * kern * u(p1, hp1))
    result = sy.simplify(h1[0, 0] / nenner)
    return result


def comptu(k1: FourVector, hk1: SpinorIndex, p1: FourVector, hp1: SpinorIndex,
           k2: FourVector, hk2: SpinorIndex, p2: FourVector, hp2: SpinorIndex) -> Expr:
    """
    Calculate u-channel amplitude for Compton scattering γ(k1) + e(p1) → γ(k2) + e(p2).
    
    Args:
        k1: Initial photon four-momentum
        hk1: Initial photon helicity
        p1: Initial electron four-momentum
        hp1: Initial electron helicity
        k2: Final photon four-momentum
        hk2: Final photon helicity
        p2: Final electron four-momentum
        hp2: Final electron helicity
        
    Returns:
        u-channel scattering amplitude
    """
    ka = fourvec(k2)
    pe = fourvec(p1)
    mm = p1[1]
    mk = k2[1]
    nenner = -2 * dotprod4(ka, pe) + mk**2
    
    epsbar = polbar(k2, hk2)
    eps = pol(k1, hk1)
    kern = dag(eps) * (dag(pe) - dag(ka) + mm * one) * dag(epsbar)
    h1 = sy.simplify(ubar(p2, hp2) * kern * u(p1, hp1))
    result = sy.simplify(h1[0, 0] / nenner)
    return result


def compt(k1: FourVector, hk1: SpinorIndex, p1: FourVector, hp1: SpinorIndex,
          k2: FourVector, hk2: SpinorIndex, p2: FourVector, hp2: SpinorIndex) -> Expr:
    """
    Calculate total Compton scattering amplitude (s + u channels).
    
    Args:
        k1: Initial photon four-momentum
        hk1: Initial photon helicity
        p1: Initial electron four-momentum
        hp1: Initial electron helicity
        k2: Final photon four-momentum
        hk2: Final photon helicity
        p2: Final electron four-momentum
        hp2: Final electron helicity
        
    Returns:
        Total scattering amplitude
    """
    t1 = compts(k1, hk1, p1, hp1, k2, hk2, p2, hp2)
    t2 = comptu(k1, hk1, p1, hp1, k2, hk2, p2, hp2)
    result = sy.simplify(t1 + t2)
    return result


# Numerator-only versions (without propagators)
def Ncompts(k1: FourVector, hk1: SpinorIndex, p1: FourVector, hp1: SpinorIndex,
            k2: FourVector, hk2: SpinorIndex, p2: FourVector, hp2: SpinorIndex) -> Expr:
    """
    Calculate s-channel Compton amplitude numerator (without propagator).
    
    Args:
        k1: Initial photon four-momentum
        hk1: Initial photon helicity
        p1: Initial electron four-momentum
        hp1: Initial electron helicity
        k2: Final photon four-momentum
        hk2: Final photon helicity
        p2: Final electron four-momentum
        hp2: Final electron helicity
        
    Returns:
        s-channel amplitude numerator
    """
    ke = fourvec(k1)
    pe = fourvec(p1)
    mm = p1[1]
    mk = k1[1]
    
    epsbar = polbar(k2, hk2)
    eps = pol(k1, hk1)
    kern = dag(epsbar) * (dag(ke) + dag(pe) + mm * one) * dag(eps)
    h1 = sy.simplify(ubar(p2, hp2) * kern * u(p1, hp1))
    result = sy.simplify(h1[0, 0])
    return result


def Ncomptu(k1: FourVector, hk1: SpinorIndex, p1: FourVector, hp1: SpinorIndex,
            k2: FourVector, hk2: SpinorIndex, p2: FourVector, hp2: SpinorIndex) -> Expr:
    """
    Calculate u-channel Compton amplitude numerator (without propagator).
    
    Args:
        k1: Initial photon four-momentum
        hk1: Initial photon helicity
        p1: Initial electron four-momentum
        hp1: Initial electron helicity
        k2: Final photon four-momentum
        hk2: Final photon helicity
        p2: Final electron four-momentum
        hp2: Final electron helicity
        
    Returns:
        u-channel amplitude numerator
    """
    ka = fourvec(k2)
    pe = fourvec(p1)
    mm = p1[1]
    mk = k1[1]
    
    epsbar = polbar(k2, hk2)
    eps = pol(k1, hk1)
    kern = dag(eps) * (dag(pe) - dag(ka) + mm * one) * dag(epsbar)
    h1 = sy.simplify(ubar(p2, hp2) * kern * u(p1, hp1))
    result = sy.simplify(h1[0, 0])
    return result


# Pair annihilation to two photons: f + f̄ → γγ
def gamgamt(p1: FourVector, hp1: SpinorIndex, p2: FourVector, hp2: SpinorIndex,
            k1: FourVector, hk1: SpinorIndex, k2: FourVector, hk2: SpinorIndex) -> Expr:
    """
    Calculate t-channel amplitude for e⁺e⁻ → γγ annihilation.
    
    Args:
        p1: Electron four-momentum
        hp1: Electron helicity
        p2: Positron four-momentum
        hp2: Positron helicity
        k1: First photon four-momentum
        hk1: First photon helicity
        k2: Second photon four-momentum
        hk2: Second photon helicity
        
    Returns:
        t-channel annihilation amplitude
    """
    ka = fourvec(k1)
    pe = fourvec(p1)
    mm = p1[1]
    M = k1[1]
    nenner = -2 * dotprod4(ka, pe) + M**2
    
    epsbar2 = polbar(k2, hk2)
    epsbar1 = polbar(k1, hk1)
    kern = dag(epsbar2) * (dag(ka) - dag(pe) + mm * one) * dag(epsbar1)
    h1 = sy.simplify(vbar(p2, hp2) * kern * u(p1, hp1))
    result = sy.simplify(h1[0, 0] / nenner)
    return result


def gamgamu(p1: FourVector, hp1: SpinorIndex, p2: FourVector, hp2: SpinorIndex,
            k1: FourVector, hk1: SpinorIndex, k2: FourVector, hk2: SpinorIndex) -> Expr:
    """
    Calculate u-channel amplitude for e⁺e⁻ → γγ annihilation.
    
    Args:
        p1: Electron four-momentum
        hp1: Electron helicity
        p2: Positron four-momentum
        hp2: Positron helicity
        k1: First photon four-momentum
        hk1: First photon helicity
        k2: Second photon four-momentum
        hk2: Second photon helicity
        
    Returns:
        u-channel annihilation amplitude
    """
    ka = fourvec(k2)
    pe = fourvec(p1)
    mm = p1[1]
    M = k2[1]
    nenner = -2 * dotprod4(ka, pe) + M**2
    
    epsbar2 = polbar(k2, hk2)
    epsbar1 = polbar(k1, hk1)
    kern = dag(epsbar1) * (dag(ka) - dag(pe) + mm * one) * dag(epsbar2)
    h1 = sy.simplify(vbar(p2, hp2) * kern * u(p1, hp1))
    result = sy.simplify(h1[0, 0] / nenner)
    return result


def gamgam(p1: FourVector, hp1: SpinorIndex, p2: FourVector, hp2: SpinorIndex,
           k1: FourVector, hk1: SpinorIndex, k2: FourVector, hk2: SpinorIndex) -> Expr:
    """
    Calculate total e⁺e⁻ → γγ annihilation amplitude (t + u channels).
    
    Args:
        p1: Electron four-momentum
        hp1: Electron helicity
        p2: Positron four-momentum
        hp2: Positron helicity
        k1: First photon four-momentum
        hk1: First photon helicity
        k2: Second photon four-momentum
        hk2: Second photon helicity
        
    Returns:
        Total annihilation amplitude
    """
    t1 = gamgamt(p1, hp1, p2, hp2, k1, hk1, k2, hk2)
    t2 = gamgamu(p1, hp1, p2, hp2, k1, hk1, k2, hk2)
    result = sy.simplify(t1 + t2)
    return result


# Numerator-only versions for pair annihilation
def Ngamgamt(p1: FourVector, hp1: SpinorIndex, p2: FourVector, hp2: SpinorIndex,
             k1: FourVector, hk1: SpinorIndex, k2: FourVector, hk2: SpinorIndex) -> Expr:
    """
    Calculate t-channel e⁺e⁻ → γγ amplitude numerator (without propagator).
    
    Args:
        p1: Electron four-momentum
        hp1: Electron helicity
        p2: Positron four-momentum
        hp2: Positron helicity
        k1: First photon four-momentum
        hk1: First photon helicity
        k2: Second photon four-momentum
        hk2: Second photon helicity
        
    Returns:
        t-channel amplitude numerator
    """
    ka = fourvec(k1)
    pe = fourvec(p1)
    mm = p1[1]
    
    epsbar2 = polbar(k2, hk2)
    epsbar1 = polbar(k1, hk1)
    kern = dag(epsbar2) * (dag(ka) - dag(pe) + mm * one) * dag(epsbar1)
    h1 = sy.simplify(vbar(p2, hp2) * kern * u(p1, hp1))
    result = sy.simplify(h1[0, 0])
    return result


def Ngamgamu(p1: FourVector, hp1: SpinorIndex, p2: FourVector, hp2: SpinorIndex,
             k1: FourVector, hk1: SpinorIndex, k2: FourVector, hk2: SpinorIndex) -> Expr:
    """
    Calculate u-channel e⁺e⁻ → γγ amplitude numerator (without propagator).
    
    Args:
        p1: Electron four-momentum
        hp1: Electron helicity
        p2: Positron four-momentum
        hp2: Positron helicity
        k1: First photon four-momentum
        hk1: First photon helicity
        k2: Second photon four-momentum
        hk2: Second photon helicity
        
    Returns:
        u-channel amplitude numerator
    """
    ka = fourvec(k2)
    pe = fourvec(p1)
    mm = p1[1]
    
    epsbar2 = polbar(k2, hk2)
    epsbar1 = polbar(k1, hk1)
    kern = dag(epsbar1) * (dag(ka) - dag(pe) + mm * one) * dag(epsbar2)
    h1 = sy.simplify(vbar(p2, hp2) * kern * u(p1, hp1))
    result = sy.simplify(h1[0, 0])
    return result

