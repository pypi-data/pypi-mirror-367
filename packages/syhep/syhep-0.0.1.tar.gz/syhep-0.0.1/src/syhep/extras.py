# pyright: reportOperatorIssue=false
# pyright: reportArgumentType=false
# pyright: reportAssignmentType=false
# pyright: reportReturnType=false

"""
The following functions were added to calculations of DM very specific scenarios.
Proceed to use those with caution!
"""

from typing import Union, List, Dict, Any, Tuple
from sympy.combinatorics.permutations import Permutation
import sympy as sy

from syhep import *

# Type aliases for clarity
SpinorHelicity = Union[int, float]
Mediator = Any  # Mediator particle object
Momentum = Any  # Four-momentum object from syhep
SymbolicMatrix = sy.Matrix
SymbolicExpression = sy.Expr

def vbuwMB(p1: Momentum, h1: SpinorHelicity, p2: Momentum, h2: SpinorHelicity, 
           qv: Momentum, mmed: SymbolicExpression, cv: SymbolicExpression, 
           ca: SymbolicExpression) -> SymbolicMatrix:
    """
    Calculate weak current for neutrino-fermion scattering with momentum transfer.
    
    Computes the electroweak current j_μ for ν̄(p1,h1) + f(p2,h2) → mediator
    including both standard current and momentum transfer terms.
    
    Args:
        p1: Neutrino four-momentum
        h1: Neutrino helicity
        p2: Fermion four-momentum  
        h2: Fermion helicity
        qv: Momentum transfer four-vector
        mmed: Mediator mass
        cv: Vector coupling constant
        ca: Axial coupling constant
        
    Returns:
        Four-component current vector j_μ
    """
    # boson_mass = qv[1]
    qvec = qv / mmed

    # GCW theory
    cv, ca, gz, gw, thetaw, gz_theta, gw_theta, gf = sy.symbols(
        r'c_v c_a g_Z g_W theta_W g_Z_theta g_W_theta, g_f', real=True, )
    # gz = gw / sy.cos(thetaw)
    gv = cv / 2
    ga = ca / 2
    # gz_theta = (gw / sy.cos(thetaw))

    # gw_theta = gw * sy.cos(thetaw)
    EWproj = -sy.I * gf * (gv * one - ga * g5)

    j0 = -sy.I * (vbar(p1, h1) * g0 * EWproj * u(p2, h2) -
               vbar(p1, h1) * g0 * EWproj * qvec[0] * u(p2, h2))
    j1 = -sy.I * (vbar(p1, h1) * g1 * EWproj * u(p2, h2) -
               vbar(p1, h1) * g1 * EWproj * qvec[1] * u(p2, h2))
    j2 = -sy.I * (vbar(p1, h1) * g2 * EWproj * u(p2, h2) -
               vbar(p1, h1) * g2 * EWproj * qvec[2] * u(p2, h2))
    j3 = -sy.I * (vbar(p1, h1) * g3 * EWproj * u(p2, h2) -
               vbar(p1, h1) * g3 * EWproj * qvec[3] * u(p2, h2))
    result = sy.Matrix([sy.simplify(j0[0]), sy.simplify(j1[0]),
                    sy.simplify(j2[0]), sy.simplify(j3[0])])
    return result


def V3ZOutOut(k: Momentum, hk: SpinorHelicity, p: Momentum, hp: SpinorHelicity, 
              qv: Momentum, mmed: SymbolicExpression, cv: SymbolicExpression, 
              ca: SymbolicExpression) -> SymbolicMatrix:
    """
    Calculate three-point vector vertex for two outgoing gauge bosons.
    
    Computes the VVV vertex contribution for k + p → mediator with both
    standard gauge theory terms and momentum-dependent corrections.
    
    Args:
        k: First boson four-momentum
        hk: First boson helicity
        p: Second boson four-momentum
        hp: Second boson helicity
        qv: Momentum transfer four-vector
        mmed: Mediator mass
        cv: Vector coupling constant
        ca: Axial coupling constant
        
    Returns:
        Four-component vertex amplitude
    """
    cv, ca, gz, gw, thetaw, gz_theta, gw_theta, gv = sy.symbols(
        r'c_v c_a g_Z g_W theta_W g_Z_theta g_W_theta, g_v', real=True)

    eps3 = polbar(k, hk)
    eps4 = polbar(p, hp)

    p3 = fourvec(k)
    p4 = fourvec(p)

    # boson_mass = qv[1]
    qvec = qv / mmed

    s1 = dotprod4(eps3, eps4)  # 0
    s2 = dotprod4(eps3, p4)   # GeV
    s3 = dotprod4(eps4, p3)   # GeV

    elm1 = s1 * (p4[0] - p3[0]) - 2 * s2 * eps4[0] + 2 * s3 * eps3[0]  # GeV
    elm2 = s1 * (p4[1] - p3[1]) - 2 * s2 * eps4[1] + 2 * s3 * eps3[1]  # GeV
    elm3 = s1 * (p4[2] - p3[2]) - 2 * s2 * eps4[2] + 2 * s3 * eps3[2]  # GeV
    elm4 = s1 * (p4[3] - p3[3]) - 2 * s2 * eps4[3] + 2 * s3 * eps3[3]  # GeV

    w3 = dotprod4(qvec, p3)     # GeV
    w4 = dotprod4(qvec, p4)     # GeV
    we3 = dotprod4(qvec, eps3)  # 0
    we4 = dotprod4(qvec, eps4)  # 0
    print(f'w3 {w3}')
    print(f'w4 {w4}')
    wd = w3 - w4  # = dotprod4(qvec, p4 - p3)

    SSelm1 = ((s1 * (w3 - w4)) - ((2 * s2) * we3) +
              ((2 * s3) * we4))  # * qvec[0]     ## GeV
    SSelm2 = ((s1 * (w3 - w4)) - ((2 * s2) * we3) +
              ((2 * s3) * we4))  # * qvec[0]     ## GeV
    SSelm3 = ((s1 * (w3 - w4)) - ((2 * s2) * we3) +
              ((2 * s3) * we4))  # * qvec[0]     ## GeV
    SSelm4 = ((s1 * (w3 - w4)) - ((2 * s2) * we3) +
              ((2 * s3) * we4))  # * qvec[0]     ## GeV

    result = sy.Matrix([elm1 - SSelm1, elm2 - SSelm2, elm3 -
                    SSelm3, elm4 - SSelm4]) * sy.I * gv

    return result


def vbuwMB_noqq(p1: Momentum, h1: SpinorHelicity, p2: Momentum, h2: SpinorHelicity, 
                qv: Momentum, mmed: SymbolicExpression, cv: SymbolicExpression, 
                ca: SymbolicExpression) -> SymbolicMatrix:
    """
    Calculate weak current without momentum transfer terms.
    
    Simplified version of vbuwMB that excludes the qvec momentum transfer
    corrections, computing only the standard electroweak current.
    
    Args:
        p1: Neutrino four-momentum
        h1: Neutrino helicity
        p2: Fermion four-momentum
        h2: Fermion helicity
        qv: Momentum transfer four-vector (unused in calculation)
        mmed: Mediator mass (unused in calculation)
        cv: Vector coupling constant
        ca: Axial coupling constant
        
    Returns:
        Four-component current vector j_μ
    """
    # boson_mass = qv[1]
    qvec = qv / mmed

    # GCW theory
    cv, ca, gz, gw, thetaw, gz_theta, gw_theta, gf = sy.symbols(
        r'c_v c_a g_Z g_W theta_W g_Z_theta g_W_theta, g_f', real=True, )
    # gz = gw / sy.cos(thetaw)
    gv = cv / 2
    ga = ca / 2
    # gz_theta = (gw / sy.cos(thetaw))
    # gw_theta = gw * sy.cos(thetaw)
    EWproj = -sy.I * gf * (gv * one - ga * g5)

    # - vbar(p1, h1) * g0 * EWproj * qvec[0]  * u(p2, h2) )
    j0 = -sy.I * (vbar(p1, h1) * g0 * EWproj * u(p2, h2))
    # - vbar(p1, h1) * g1 * EWproj * qvec[1]  * u(p2, h2) )
    j1 = -sy.I * (vbar(p1, h1) * g1 * EWproj * u(p2, h2))
    # - vbar(p1, h1) * g2 * EWproj * qvec[2]  * u(p2, h2) )
    j2 = -sy.I * (vbar(p1, h1) * g2 * EWproj * u(p2, h2))
    # - vbar(p1, h1) * g3 * EWproj * qvec[3]  * u(p2, h2) )
    j3 = -sy.I * (vbar(p1, h1) * g3 * EWproj * u(p2, h2))
    result = sy.Matrix([sy.simplify(j0[0]), sy.simplify(j1[0]),
                    sy.simplify(j2[0]), sy.simplify(j3[0])])
    return result


def V3ZOutOut_noqq(k: Momentum, hk: SpinorHelicity, p: Momentum, hp: SpinorHelicity, 
                   qv: Momentum, mmed: SymbolicExpression, cv: SymbolicExpression, 
                   ca: SymbolicExpression) -> SymbolicMatrix:
    """
    Calculate three-point vector vertex without momentum transfer corrections.
    
    Simplified version of V3ZOutOut that excludes momentum-dependent terms,
    computing only the standard gauge theory VVV vertex.
    
    Args:
        k: First boson four-momentum
        hk: First boson helicity
        p: Second boson four-momentum
        hp: Second boson helicity
        qv: Momentum transfer four-vector (used for setup only)
        mmed: Mediator mass (used for setup only)
        cv: Vector coupling constant
        ca: Axial coupling constant
        
    Returns:
        Four-component vertex amplitude
    """
    cv, ca, gz, gw, thetaw, gz_theta, gw_theta, gv = sy.symbols(
        r'c_v c_a g_Z g_W theta_W g_Z_theta g_W_theta, g_v', real=True)

    eps3 = polbar(k, hk)
    eps4 = polbar(p, hp)

    p3 = fourvec(k)
    p4 = fourvec(p)

    qvec = qv / mmed

    s1 = dotprod4(eps3, eps4)  # 0
    s2 = dotprod4(eps3, p4)   # GeV
    s3 = dotprod4(eps4, p3)   # GeV

    elm1 = s1 * (p4[0] - p3[0]) - 2 * s2 * eps4[0] + 2 * s3 * eps3[0]  # GeV  # type: ignore
    elm2 = s1 * (p4[1] - p3[1]) - 2 * s2 * eps4[1] + 2 * s3 * eps3[1]  # GeV  # type: ignore
    elm3 = s1 * (p4[2] - p3[2]) - 2 * s2 * eps4[2] + 2 * s3 * eps3[2]  # GeV  # type: ignore
    elm4 = s1 * (p4[3] - p3[3]) - 2 * s2 * eps4[3] + 2 * s3 * eps3[3]  # GeV  # type: ignore

    w3 = dotprod4(qvec, p3)     # GeV
    w4 = dotprod4(qvec, p4)     # GeV
    we3 = dotprod4(qvec, eps3)  # 0
    we4 = dotprod4(qvec, eps4)  # 0

    wd = w3 - w4  # = dotprod4(qvec, p4 - p3)

    # SSelm1 = ((s1 * (w3 - w4))  - ((2 * s2) * we3)  +  ((2 * s3)  * we4) ) #* qvec[0]     ## GeV
    # SSelm2 = ((s1 * (w3 - w4))  - ((2 * s2) * we3)  +  ((2 * s3)  * we4) ) #* qvec[0]     ## GeV
    # SSelm3 = ((s1 * (w3 - w4))  - ((2 * s2) * we3)  +  ((2 * s3)  * we4) ) #* qvec[0]     ## GeV
    # SSelm4 = ((s1 * (w3 - w4))  - ((2 * s2) * we3)  +  ((2 * s3)  * we4) ) #* qvec[0]     ## GeV

    result = sy.Matrix([elm1, elm2, elm3, elm4]) * sy.I * gv
    # result = sy.Matrix([elm1 - SSelm1, elm2 - SSelm2, elm3 - SSelm3, elm4 - SSelm4]) * sy.I * gv

    return result


# !!!
# Dark matter scenarios

def vbu_VDM(p1: Momentum, h1: SpinorHelicity, p2: Momentum, h2: SpinorHelicity, 
            qv: Momentum, mmed: SymbolicExpression, cv: SymbolicExpression, 
            ca: SymbolicExpression, secterm: bool = True) -> SymbolicMatrix:
    """
    Calculate vector dark matter current with left/right handed couplings.
    
    Computes fermion current for vector dark matter models with separate
    left and right-handed coupling constants and optional momentum transfer terms.
    
    Args:
        p1: First fermion four-momentum
        h1: First fermion helicity
        p2: Second fermion four-momentum
        h2: Second fermion helicity
        qv: Momentum transfer four-vector
        mmed: Mediator mass
        cv: Vector coupling constant
        ca: Axial coupling constant
        secterm: Include momentum transfer terms if True
        
    Returns:
        Four-component current vector j_μ
    """
    st = 1 if secterm else 0

    # boson_mass = qv[1]
    qvec = qv / mmed

    gf, gl, gr, grv, gra, glv, gla = sy.symbols(
        r'g_f g_l g_r g_{rv} g_{ra} g_{lv} g_{la}', real=True, )

    # GCW theory

    # gz = gw / sy.cos(thetaw)
    # glv = cv / 2
    # gla = ca / 2
    # gz_theta = (gw / sy.cos(thetaw))

    # gw_theta = gw * sy.cos(thetaw)
    EWproj = -sy.I * gf * (glv * one - gla * g5)
    Glr = - sy.I * (gl * (glv * one - gla * g5) + gr * (grv * one + gra * g5)) / 2

    # EXPLANATION:
    # gr = 0 -> usual matter, no right handed stuff
    # gl = 0 -> exotic matter, only right handed stuff
    # gl = gr -> mixing, two things coexist
    # gl = - gr -> ???
    # glv, gla, gra, grv vector or axial vector stuff, given a right or left handed scenario, in a right handded scenario replaced by ca and cv, should give EW theory

    j0 = -sy.I * (vbar(p1, h1) * g0 * Glr * u(p2, h2) - st *
               vbar(p1, h1) * g0 * Glr * qvec[0] * u(p2, h2))
    j1 = -sy.I * (vbar(p1, h1) * g1 * Glr * u(p2, h2) - st *
               vbar(p1, h1) * g1 * Glr * qvec[1] * u(p2, h2))
    j2 = -sy.I * (vbar(p1, h1) * g2 * Glr * u(p2, h2) - st *
               vbar(p1, h1) * g2 * Glr * qvec[2] * u(p2, h2))
    j3 = -sy.I * (vbar(p1, h1) * g3 * Glr * u(p2, h2) - st *
               vbar(p1, h1) * g3 * Glr * qvec[3] * u(p2, h2))
    result = sy.Matrix([sy.simplify(j0[0]), sy.simplify(j1[0]),
                    sy.simplify(j2[0]), sy.simplify(j3[0])])
    return result


def V3ZOutOut_VDM(k: Momentum, hk: SpinorHelicity, p: Momentum, hp: SpinorHelicity, 
                  qv: Momentum, mmed: SymbolicExpression, cv: SymbolicExpression, 
                  ca: SymbolicExpression, secterm: bool = True) -> SymbolicMatrix:
    """
    Calculate three-point vertex for vector dark matter models.
    
    Vector dark matter version of V3ZOutOut with optional momentum transfer
    corrections controlled by secterm parameter.
    
    Args:
        k: First boson four-momentum
        hk: First boson helicity
        p: Second boson four-momentum
        hp: Second boson helicity
        qv: Momentum transfer four-vector
        mmed: Mediator mass
        cv: Vector coupling constant
        ca: Axial coupling constant
        secterm: Include momentum transfer terms if True
        
    Returns:
        Four-component vertex amplitude
    """
    cv, ca, gz, gw, thetaw, gz_theta, gw_theta, gv = sy.symbols(
        r'c_v c_a g_Z g_W theta_W g_Z_theta g_W_theta, g_v', real=True)

    st = 1 if secterm else 0

    eps3 = polbar(k, hk)
    eps4 = polbar(p, hp)

    p3 = fourvec(k)
    p4 = fourvec(p)

    # boson_mass = qv[1]
    qvec = qv / mmed

    s1 = dotprod4(eps3, eps4)  # 0
    s2 = dotprod4(eps3, p4)   # GeV
    s3 = dotprod4(eps4, p3)   # GeV

    elm1 = s1 * (p4[0] - p3[0]) - 2 * s2 * eps4[0] + 2 * s3 * eps3[0]  # GeV
    elm2 = s1 * (p4[1] - p3[1]) - 2 * s2 * eps4[1] + 2 * s3 * eps3[1]  # GeV
    elm3 = s1 * (p4[2] - p3[2]) - 2 * s2 * eps4[2] + 2 * s3 * eps3[2]  # GeV
    elm4 = s1 * (p4[3] - p3[3]) - 2 * s2 * eps4[3] + 2 * s3 * eps3[3]  # GeV

    w3 = dotprod4(qvec, p3)     # GeV
    w4 = dotprod4(qvec, p4)     # GeV
    we3 = dotprod4(qvec, eps3)  # 0
    we4 = dotprod4(qvec, eps4)  # 0
    print(f'w3 {w3}')
    print(f'w4 {w4}')
    wd = w3 - w4  # = dotprod4(qvec, p4 - p3)

    SSelm1 = st * ((s1 * (w3 - w4)) - ((2 * s2) * we3) +
                   ((2 * s3) * we4))  # * qvec[0]     ## GeV
    SSelm2 = st * ((s1 * (w3 - w4)) - ((2 * s2) * we3) +
                   ((2 * s3) * we4))  # * qvec[0]     ## GeV
    SSelm3 = st * ((s1 * (w3 - w4)) - ((2 * s2) * we3) +
                   ((2 * s3) * we4))  # * qvec[0]     ## GeV
    SSelm4 = st * ((s1 * (w3 - w4)) - ((2 * s2) * we3) +
                   ((2 * s3) * we4))  # * qvec[0]     ## GeV

    result = sy.Matrix([elm1 - SSelm1, elm2 - SSelm2, elm3 -
                    SSelm3, elm4 - SSelm4]) * sy.I * gv

    return result


def ff_SDM_(p1: Momentum, h1: SpinorHelicity, p2: Momentum, h2: SpinorHelicity, 
            qv: Momentum, mmed: SymbolicExpression) -> SymbolicMatrix:
    """
    Calculate fermion current for scalar dark matter interaction.
    
    Computes the scalar coupling current for F + F → S processes in
    scalar dark matter models with pure scalar interaction.
    
    Args:
        p1: First fermion four-momentum
        h1: First fermion helicity
        p2: Second fermion four-momentum
        h2: Second fermion helicity
        qv: Momentum transfer four-vector (used for setup)
        mmed: Mediator mass (used for setup)
        
    Returns:
        Four-component current vector (scalar coupling)
    """
    # st = 1 if secterm else 0

    # mediator mass = qv[1]
    qvec = qv / mmed

    gf, gs = sy.symbols(r'g_f g_s', real=True)

    # GCW theory

    # gz = gw / sy.cos(thetaw)
    # glv = cv / 2
    # gla = ca / 2
    # gz_theta = (gw / sy.cos(thetaw))

    # gw_theta = gw * sy.cos(thetaw)
    # EWproj = -sy.I * gf * (glv * one - gla * g5)
    # * (glv * one - gla * g5)  + grx * (grv * one + gra * g5)) / 2
    GS = - sy.I * (gs)

    # EXPLANATION:
    # gr = 0 -> usual matter, no right handed stuff
    # gl = 0 -> exotic matter, only right handed stuff
    # gl = gr -> mixing, two things coexist
    # gl = - gr -> ???
    # glv, gla, gra, grv vector or axial vector stuff, given a right or left handed scenario, in a right handded scenario replaced by ca and cv, should give EW theory

    # * sy.I #- st * vbar(p1, h1) * g0 * Glr * qvec[0]  * u(p2, h2) )
    j0 = (vbar(p1, h1) * GS * u(p2, h2))
    # * sy.I #- st * vbar(p1, h1) * g1 * Glr * qvec[1]  * u(p2, h2) )
    j1 = (vbar(p1, h1) * GS * u(p2, h2))
    # * sy.I #- st * vbar(p1, h1) * g2 * Glr * qvec[2]  * u(p2, h2) )
    j2 = (vbar(p1, h1) * GS * u(p2, h2))
    # * sy.I #- st * vbar(p1, h1) * g3 * Glr * qvec[3]  * u(p2, h2) )
    j3 = (vbar(p1, h1) * GS * u(p2, h2))
    result = sy.Matrix([sy.simplify(j0[0]), sy.simplify(j1[0]),
                    sy.simplify(j2[0]), sy.simplify(j3[0])])
    return result


def _SDM_ff(p1: Momentum, h1: SpinorHelicity, p2: Momentum, h2: SpinorHelicity, 
            qv: Momentum, mmed: SymbolicExpression) -> SymbolicMatrix:
    """
    Calculate fermion current for scalar dark matter decay.
    
    Computes the scalar coupling current for S → F + F̄ decay processes
    in scalar dark matter models.
    
    Args:
        p1: First fermion four-momentum
        h1: First fermion helicity
        p2: Second fermion four-momentum
        h2: Second fermion helicity
        qv: Momentum transfer four-vector (used for setup)
        mmed: Mediator mass (used for setup)
        
    Returns:
        Four-component current vector (scalar coupling)
    """
    # st = 1 if secterm else 0

    # mediator mass = qv[1]
    qvec = qv / mmed

    gf, gsx = sy.symbols(r'g_f g_sx', real=True)

    # * (glv * one - gla * g5)  + grx * (grv * one + gra * g5)) / 2
    GS = - sy.I * (gsx)

    # EXPLANATION:
    # gr = 0 -> usual matter, no right handed stuff
    # gl = 0 -> exotic matter, only right handed stuff
    # gl = gr -> mixing, two things coexist
    # gl = - gr -> ???
    # glv, gla, gra, grv vector or axial vector stuff, given a right or left handed scenario, in a right handded scenario replaced by ca and cv, should give EW theory

    j0 = (vbar(p1, h1) * GS * u(p2, h2))
    j1 = (vbar(p1, h1) * GS * u(p2, h2))
    j2 = (vbar(p1, h1) * GS * u(p2, h2))
    j3 = (vbar(p1, h1) * GS * u(p2, h2))
    result = sy.Matrix([sy.simplify(j0[0]), sy.simplify(j1[0]),
                    sy.simplify(j2[0]), sy.simplify(j3[0])])
    return result


def phi(pp: Momentum, ha: SpinorHelicity) -> SymbolicMatrix:
    """
    Scalar field wavefunction.
    
    Returns a trivial scalar field representation as a 4x1 matrix of ones.
    
    Args:
        pp: Scalar particle momentum (unused)
        ha: Scalar particle helicity (unused)
        
    Returns:
        4x1 matrix representing scalar field
    """
    res = sy.Matrix([[1], [1], [1], [1]])
    return res


def phibar(pp: Momentum, ha: SpinorHelicity) -> SymbolicMatrix:
    """
    Conjugate scalar field wavefunction.
    
    Returns a trivial conjugate scalar field representation as a 1x4 matrix of ones.
    
    Args:
        pp: Scalar particle momentum (unused)
        ha: Scalar particle helicity (unused)
        
    Returns:
        1x4 matrix representing conjugate scalar field
    """
    res = sy.Matrix([[1, 1, 1, 1]])
    return res





def Amplitude_schannel(u1: str, p1: Momentum, u2: str, p2: Momentum, prp: str, 
                       u3: str, p3: Momentum, u4: str, p4: Momentum) -> List[SymbolicExpression]:
    """
    Calculate s-channel scattering amplitude with mediator propagator.
    
    Computes the full amplitude for 2→2 scattering via s-channel mediator exchange,
    including all helicity combinations and Breit-Wigner propagator.
    
    Args:
        u1: Initial particle type ('u', 'v', 'ubar', 'vbar', 'pol', 'polbar', 'phi', 'phibar')
        p1: Initial particle 1 momentum
        u2: Initial particle 2 type
        p2: Initial particle 2 momentum
        prp: Mediator type ('scalar', 'vector', 'fermion')
        u3: Final particle 1 type
        p3: Final particle 1 momentum
        u4: Final particle 2 type
        p4: Final particle 2 momentum
        
    Returns:
        List of amplitude terms for all helicity combinations
    """
    # Breit-Wigner denominator, to be added in the end of the calculation for simplicity.
    spinor: Dict[str, Dict[str, Any]] = {
        'u': {'type': 'F', 'fn': u},
        'v': {'type': 'F', 'fn': v},
        'vbar': {'type': 'F', 'fn': vbar},
        'ubar': {'type': 'F', 'fn': ubar},
        'pol': {'type': 'V', 'fn': pol},
        'polbar': {'type': 'V', 'fn': polbar},
        'phi': {'type': 'S', 'fn': phi},
        'phibar': {'type': 'S', 'fn': phibar}
    }

    def get_propagator(prop: str, type1: str, dm: bool = False) -> Tuple[SymbolicExpression, SymbolicExpression]:
        """Get vertex and propagator for given mediator and particle types."""
        # pick the correct indice for SM or DM mechanics
        dmsm = r"\chi" if dm else r"\psi"

        s, Mmed, Gamma = sy.symbols(r's M_{med} Gamma', real=True)
        gs, gps = sy.symbols(f'g_s{dmsm} g_ps{dmsm}', real=True)
        gv, gav = sy.symbols(f'g_v{dmsm} g_av{dmsm}', real=True)

        denom = (s - Mmed**2 + sy.I * (Mmed * Gamma))

        if prop == 'scalar':
            vertex = {
                "F": -sy.I * (gs * one + sy.I * gps * g5),  # scalar and pseudoscalar couplings
                "V": -sy.I * gs * one,  # Scalar vector coupling
                "S": -sy.I * gs * one,  # Triple scalar simple coupling
            }
            propagator = -1 / denom

        elif prop == 'vector':
            # Placeholder for vector propagator
            vertex = {"F": -sy.I * gv * one, "V": -sy.I * gv * one, "S": -sy.I * gv * one}
            propagator = -1 / denom

        elif prop == 'fermion':
            print('Fermion propagator not yet implemented')
            vertex = {"F": -sy.I * gv * one, "V": -sy.I * gv * one, "S": -sy.I * gv * one}
            propagator = -1 / denom

        else:
            raise ValueError(f"Unknown propagator type: {prop}")

        return vertex[type1], propagator

    def init_J() -> List[SymbolicMatrix]:
        """Calculate initial state current with all helicity combinations."""
        hel_fermion = [-1, 1]
        vertex, propagator = get_propagator(prp, spinor[u1]['type'])
        Jc_init: List[SymbolicMatrix] = []
        
        for hl in hel_fermion:
            for hr in hel_fermion:
                jc = []
                for i in range(4):
                    # Initial current - propagator only here
                    ji = spinor[u1]['fn'](p1, hl) * vertex * propagator * spinor[u2]['fn'](p2, hr)
                    jc.append(sy.simplify(ji[0]))
                Jc_init.append(sy.Matrix(jc))

        return Jc_init

    def final_J(types: str) -> List[SymbolicMatrix]:
        """Calculate final state current with all helicity combinations."""
        hel_fermion = [-1, 1] if types != 'V' else [-1, 0, 1]
        vertex, propagator = get_propagator(prp, types, dm=True)
        Jc_final: List[SymbolicMatrix] = []
        
        for hl in hel_fermion:
            for hr in hel_fermion:
                jc = []
                for i in range(4):
                    # Second current
                    jf = spinor[u3]['fn'](p3, hl) * vertex * spinor[u4]['fn'](p4, hr)
                    jc.append(sy.simplify(jf[0]))
                Jc_final.append(sy.Matrix(jc))

        return Jc_final

    # Trace final result
    Ji = init_J()
    Jf = final_J(spinor[u4]['type'])
    Terms: List[SymbolicExpression] = []
    
    for j_init in Ji:
        for j_final in Jf:
            Terms.append(sy.simplify(dotprod4(j_init, j_final)))

    return Terms


def decay_Gamma(prp: str, u3: str, p3: Momentum, u4: str, p4: Momentum) -> List[SymbolicExpression]:
    """
    Calculate decay width amplitude for mediator → particle + antiparticle.
    
    Computes amplitude terms for mediator decay processes, summing over
    all helicity combinations of the decay products.
    
    Args:
        prp: Mediator type ('scalar', 'vector', 'fermion') 
        u3: Decay product 1 type
        p3: Decay product 1 momentum
        u4: Decay product 2 type  
        p4: Decay product 2 momentum
        
    Returns:
        List of amplitude terms for all helicity combinations
    """
    # Breit-Wigner denominator, to be added in the end of the calculation for simplicity.
    spinor: Dict[str, Dict[str, Any]] = {
        'u': {'type': 'F', 'fn': u},
        'v': {'type': 'F', 'fn': v},
        'vbar': {'type': 'F', 'fn': vbar},
        'ubar': {'type': 'F', 'fn': ubar},
        'pol': {'type': 'V', 'fn': pol},
        'polbar': {'type': 'V', 'fn': polbar},
        'phi': {'type': 'S', 'fn': phi},
        'phibar': {'type': 'S', 'fn': phibar}
    }

    def get_propagator(prop: str, types: str, dm: bool = False) -> Tuple[SymbolicExpression, SymbolicExpression]:
        """Get vertex and propagator for given mediator and particle types."""
        # pick the correct indice for SM or DM mechanics
        dmsm = r"\chi" if dm else r"\psi"

        s, Mmed, Gamma = sy.symbols(r's M_{med} Gamma', real=True)
        gs, gps = sy.symbols(f'g_s{dmsm} g_ps{dmsm}', real=True)
        gv, gav = sy.symbols(f'g_v{dmsm} g_av{dmsm}', real=True)

        denom = (s - Mmed**2 + sy.I * (Mmed * Gamma))

        if prop == 'scalar':
            vertex = {
                "F": sy.I * -sy.I * (gs * one),  # scalar couplings
                "V": sy.I * gs * one,  # Scalar vector coupling
                "S": -sy.I * gs * one,  # Triple scalar simple coupling
            }
            propagator = -1 / denom

        elif prop == 'vector':
            # Placeholder for vector propagator
            vertex = {"F": -sy.I * gv * one, "V": -sy.I * gv * one, "S": -sy.I * gv * one}
            propagator = -1 / denom

        elif prop == 'fermion':
            print('Fermion propagator not yet implemented')
            vertex = {"F": -sy.I * gv * one, "V": -sy.I * gv * one, "S": -sy.I * gv * one}
            propagator = -1 / denom

        else:
            raise ValueError(f"Unknown propagator type: {prop}")

        return vertex[types], propagator

    def init_J(types: str) -> List[SymbolicMatrix]:
        """Calculate initial state current for decay process."""
        hel_fermion = [-1, 1] if types != 'V' else [-1, 0, 1]
        vertex, propagator = get_propagator(prp, types)
        Jc_init: List[SymbolicMatrix] = []
        
        for hl in hel_fermion:
            jc = []
            for i in range(4):
                ji = spinor[u3]['fn'](p3, hl) * vertex
                jc.append(sy.simplify(ji[0]))
            Jc_init.append(sy.Matrix(jc))

        return Jc_init

    def final_J(types: str) -> List[SymbolicMatrix]:
        """Calculate final state current for decay process."""
        hel_fermion = [-1, 1] if types != 'V' else [-1, 0, 1]
        vertex, propagator = get_propagator(prp, types, dm=True)
        Jc_final: List[SymbolicMatrix] = []

        for hl in hel_fermion:
            jc = []
            for i in range(4):
                jf = one * spinor[u4]['fn'](p4, hl)
                jc.append(sy.simplify(jf[0]))
            Jc_final.append(sy.Matrix(jc))

        return Jc_final

    # Trace final result
    Ji = init_J(spinor[u3]['type'])
    Jf = final_J(spinor[u4]['type'])
    Terms: List[SymbolicExpression] = []
    
    for j_init in Ji:
        for j_final in Jf:
            Terms.append(sy.simplify(dotprod4(j_init, j_final)))

    return Terms


# OLD Version

# def Amplitude_schannel(u1: str, p1: Momentum, u2: str, p2: Momentum, prp: str, 
#                        u3: str, p3: Momentum, u4: str, p4: Momentum) -> List[SymbolicExpression]:
#     """
#     Calculate s-channel scattering amplitude with mediator propagator.
    
#     Computes the full amplitude for 2→2 scattering via s-channel mediator exchange,
#     including all helicity combinations and Breit-Wigner propagator.
    
#     Args:
#         u1: Initial particle type ('u', 'v', 'ubar', 'vbar', 'pol', 'polbar', 'phi', 'phibar')
#         p1: Initial particle 1 momentum
#         u2: Initial particle 2 type
#         p2: Initial particle 2 momentum
#         prp: Mediator type ('scalar', 'vector', 'fermion')
#         u3: Final particle 1 type
#         p3: Final particle 1 momentum
#         u4: Final particle 2 type
#         p4: Final particle 2 momentum
        
#     Returns:
#         List of amplitude terms for all helicity combinations
#     """
#     # Breit-Wigner denominator, to be added in the end of the calculation for simplicity.
#     spinor = {
#         'u': {'type': 'F', 'fn': u},
#         'v': {'type': 'F', 'fn': v},
#         'vbar': {'type': 'F', 'fn': vbar},
#         'ubar': {'type': 'F', 'fn': ubar},
#         'pol': {'type': 'V', 'fn': pol},
#         'polbar': {'type': 'V', 'fn': polbar},
#         'phi': {'type': 'S', 'fn': phi},
#         'phibar': {'type': 'S', 'fn': phibar}
#     }

#     # prop = {
#     #         'scalar'    : 'S',
#     #         'vector'    : 'V',
#     #         'axial'     : 'A',
#     #         'pseudoscalar' : 'P',
#     #         'fermion' : 'F',
#     # }

#     # Breit-Wigner denominator, to be added in the end of the calculation for simplicity.
#     def get_propagator(prop, type1, dm=False):

#         # pick the correct indice for SM or DM mechanics
#         dmsm = r"\chi" if dm else r"\psi"

#         s, Mmed, Gamma = sy.symbols(r's M_{med} Gamma', real=True)
#         gs, gps = sy.symbols(f'g_s{dmsm} g_ps{dmsm}', real=True)
#         gv, gav = sy.symbols(f'g_v{dmsm} g_av{dmsm}', real=True)
#         # gs, gps, gsx =  symbols(r'g_{v} g_{ps} g_{sx}', real=True )

#         denom = (s - Mmed**2 + sy.I * (Mmed * Gamma))

#         if prop == 'scalar':
#             vertex = {
#                 # scalar and pseudoscalar couplings
#                 f"F": -sy.I * (gs * one + sy.I * gps * g5),
#                 f"V": -sy.I * gs * one,  # Scalar vector coupling
#                 f"S": -sy.I * gs * one,  # Triple scalar simple coupling
#             }

#             propagator = -1 / denom

#         elif prop == 'vector':
#             # vertex = {
#             #             f"{type1}{type2}": -sy.I * ( gs * one + sy.I * gps * g5 ), ## scalar and pseudoscalar couplings
#             #             f"{type1}{type2}": -sy.I *  gsx * one,
#             #             f"{type1}{type2}": -sy.I *  gsx * one,
#             #          }                  ## Triple scalar simple coupling
#             pass

#         elif prop == 'fermion':
#             print('Not yet')
#             pass

#         return vertex[type1], propagator

#     def init_J():
#         hel_fermion = [-1, 1]
#         vertex, propagator = get_propagator(
#             prp, spinor[u1]['type'])  # Get initial propagator
#         Jc_init = []  # define initial current
#         for hl in hel_fermion:
#             for hr in hel_fermion:
#                 jc = []
#                 for i in range(4):
#                     # print(spinor[u1](p1, hl))
#                     # print('newspinor')
#                     # IMPORTANT!!! intial current - propagator only here
#                     ji = spinor[u1]['fn'](
#                         p1, hl) * vertex * propagator * spinor[u2]['fn'](p2, hr)
#                     jc.append(sy.simplify(ji[0]))

#                 Jc_init.append(sy.Matrix(jc))

#         return Jc_init

#     def final_J(types):
#         hel_fermion = [-1, 1] if types != 'V' else [-1, 0, 1]
#         vertex, propagator = get_propagator(
#             prp, types, dm=True)  # Get initial propagator
#         Jc_final = []  # define initial current
#         for hl in hel_fermion:
#             for hr in hel_fermion:
#                 jc = []
#                 for i in range(4):
#                     # print(spinor[u3](p3, hl))
#                     # IMPORTANT!!! # second current
#                     jf = spinor[u3]['fn'](p3, hl) * \
#                         vertex * spinor[u4]['fn'](p4, hr)
#                     # print(jf)
#                     jc.append(sy.simplify(jf[0]))

#                 Jc_final.append(sy.Matrix(jc))

#         return Jc_final

#     # Trace final result
#     Ji = init_J()
#     Jf = final_J(spinor[u4]['type'])
#     Terms = []
#     for j_init in Ji:
#         for j_final in Jf:
#             # print('append term')

#             Terms.append(sy.simplify(dotprod4(j_init, j_final)))

#     return Terms


# def decay_Gamma(prp, u3, p3, u4, p4):

#     # Breit-Wigner denominator, to be added in the end of the calculation for simplicity.
#     spinor = {
#         'u': {'type': 'F', 'fn': u},
#         'v': {'type': 'F', 'fn': v},
#         'vbar': {'type': 'F', 'fn': vbar},
#         'ubar': {'type': 'F', 'fn': ubar},
#         'pol': {'type': 'V', 'fn': pol},
#         'polbar': {'type': 'V', 'fn': polbar},
#         'phi': {'type': 'S', 'fn': phi},
#         'phibar': {'type': 'S', 'fn': phibar}
#     }

#     # prop = {
#     #         'scalar'    : 'S',
#     #         'vector'    : 'V',
#     #         'axial'     : 'A',
#     #         'pseudoscalar' : 'P',
#     #         'fermion' : 'F',
#     # }

#     # Breit-Wigner denominator, to be added in the end of the calculation for simplicity.
#     def get_propagator(prop, types, dm=False):

#         # pick the correct indice for SM or DM mechanics
#         dmsm = r"\chi" if dm else r"\psi"

#         s, Mmed, Gamma = sy.symbols(r's M_{med} Gamma', real=True)
#         gs, gps = sy.symbols(f'g_s{dmsm} g_ps{dmsm}', real=True)
#         gv, gav = sy.symbols(f'g_v{dmsm} g_av{dmsm}', real=True)
#         # gs, gps, gsx =  symbols(r'g_{v} g_{ps} g_{sx}', real=True )

#         denom = (s - Mmed**2 + sy.I * (Mmed * Gamma))

#         if prop == 'scalar':
#             vertex = {
#                 # + sy.I * gps * g5 ), ## scalar and pseudoscalar couplings
#                 f"F": sy.I * -sy.I * (gs * one),
#                 f"V": sy.I * gs * one,  # Scalar vector coupling
#                 f"S": -sy.I * gs * one,  # Triple scalar simple coupling
#             }

#             propagator = -1 / denom

#         elif prop == 'vector':
#             # vertex = {
#             #             f"{type1}{type2}": -sy.I * ( gs * one + sy.I * gps * g5 ), ## scalar and pseudoscalar couplings
#             #             f"{type1}{type2}": -sy.I *  gsx * one,
#             #             f"{type1}{type2}": -sy.I *  gsx * one,
#             #          }                  ## Triple scalar simple coupling
#             pass

#         elif prop == 'fermion':
#             print('Not yet')
#             pass

#         return vertex[types], propagator

#     def init_J(types):
#         # print(types)
#         hel_fermion = [-1, 1] if types != 'V' else [-1, 0, 1]
#         vertex, propagator = get_propagator(
#             prp, types)  # Get initial propagator
#         Jc_init = []  # define initial current
#         for hl in hel_fermion:
#             jc = []
#             for i in range(4):
#                 # print(hl)
#                 # print(spinor[u1](p1, hl))
#                 # print('newspinor')
#                 ji = spinor[u3]['fn'](p3, hl) * vertex
#                 jc.append(sy.simplify(ji[0]))

#             Jc_init.append(sy.Matrix(jc))

#         return Jc_init

#     def final_J(types):
#         # print(types)
#         hel_fermion = [-1, 1] if types != 'V' else [-1, 0, 1]
#         vertex, propagator = get_propagator(
#             prp, types, dm=True)  # Get initial propagator
#         Jc_final = []  # define initial current

#         for hl in hel_fermion:
#             jc = []

#             for i in range(4):
#                 # print(hl)
#                 # print(spinor[u3](p3, hl))
#                 jf = one * spinor[u4]['fn'](p4, hl)
#                 # print(jf)
#                 jc.append(sy.simplify(jf[0]))

#             Jc_final.append(sy.Matrix(jc))

#         return Jc_final

#     # Trace final result
#     Ji = init_J(spinor[u3]['type'])
#     Jf = final_J(spinor[u4]['type'])
#     Terms = []
#     for j_init in Ji:
#         for j_final in Jf:
#             # print('append term')

#             Terms.append(sy.simplify(dotprod4(j_init, j_final)))

#     return Terms




