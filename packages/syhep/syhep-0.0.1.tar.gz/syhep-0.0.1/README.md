# SyHEP
**Sy**mbolic calculations for **H**igh **E**nergy **P**article physics using python and [SymPy](https://www.sympy.org/en/index.html)

A comprehensive Python module for symbolic calculations in particle physics, built on top of [SymPy](https://www.sympy.org/en/index.html). This module provides tools for computing cross sections, scattering amplitudes, spinor algebra, polarization vectors from first principles.

Chapters references are related to Professor Christoph Berger's book:
**"Particle Physics: From the Basics to Modern Experiments"** (ISBN-13: 9783662717059)

# How to install

To use the SyHEP package with all its main functions, you can install it with pip:

```bash
pip install syhep
```

## Core Features

### 🔢 Fundamental Mathematical Objects

- **Dirac Gamma Matrices**: Complete set of γ^μ matrices in 4×4 representation
- **Pauli Matrices**: Standard 2×2 Pauli matrices for spin-1/2 calculations
- **Chiral Projectors**: Left and right-handed projection operators (1±γ₅)/2
- **SU(3) Generators**: Gell-Mann matrices for QCD color algebra

### 🌀 Spinor Algebra

- **Helicity Spinors**: u(p,λ) and v(p,λ) spinors for particles and antiparticles
- **Adjoint Spinors**: ū(p,λ) and v̄(p,λ) with proper γ⁰ conjugation
- **Automatic Helicity Handling**: Support for positive (+1/2), negative (-1/2), and longitudinal (0) helicities
- **Spherical Coordinates**: Natural integration with (E, m, θ, φ) momentum parametrization

### 📡 Polarization Vectors

- **Photon Polarizations**: Circular polarizations ε±(θ,φ) for massless gauge bosons
- **Massive Boson Polarizations**: Longitudinal polarization ε⁰(E,m,θ,φ) for W/Z bosons
- **Complex Conjugation**: Automatic handling of polarization vector adjoints

### ⚡ Current Calculations

#### QED Currents 
- **Electromagnetic**: ū(p₁,h₁)γᵘu(p₂,h₂) and related combinations
- **All Fermion Types**: Support for particle-particle, particle-antiparticle, and antiparticle-antiparticle currents

#### Weak Interaction Currents 
- **Charged Current**: ū(p₁,h₁)γᵘ(1-γ₅)u(p₂,h₂) with left-handed projection
- **Vector-Axial**: ū(p₁,h₁)γᵘ(cᵥ-cₐγ₅)u(p₂,h₂) with customizable coupling constants

#### Pauli Form Factors
- **Magnetic Moments**: ū(p₁,h₁)[σᵘᵛqᵥ/(4M)]u(p₂,h₂) for anomalous magnetic interactions


### 🛠 Utility Functions

- **Four-Vector Operations**: Minkowski dot products, momentum conversions
- **Feynman Slash Notation**: Automatic construction of p̸ = γᵘpᵤ
- **Coordinate Transformations**: (E,m,θ,φ) ↔ (E,pₓ,pᵧ,pᵤ) conversions

## Quick Start

```python
import sympy as sy
import syhep as hep

# Define particle momenta in spherical coordinates
# Format: [Energy, Mass, Theta, Phi]
electron_in = [sy.Symbol('E1'), sy.Symbol('m_e'), sy.Symbol('theta1'), sy.Symbol('phi1')]
photon_in = [sy.Symbol('k1'), 0, sy.Symbol('theta_k1'), sy.Symbol('phi_k1')]

# Calculate QED current for electron-photon vertex
current = hep.ubu(electron_in, 1, electron_in, 1)  # ū(p,+1/2)γᵘu(p,+1/2)

# Compute Compton scattering amplitude
amplitude = hep.compt(photon_in, 1, electron_in, 1, photon_out, -1, electron_out, -1)

# Simplify the result
result = sy.simplify(amplitude)
```

## Applications

- **Cross Section Calculations**: Foundation for differential and total cross sections
- **Decay Rate Computations**: Matrix elements for particle decay processes  
- **Anomalous Moment Calculations**: Magnetic and electric dipole moments
- **QCD Phenomenology**: Gluon scattering and color factor computations
- **Electroweak Theory**: W/Z boson interactions and mixing angles
- **Educational Tools**: Step-by-step amplitude calculations for learning

## Key Advantages

- **Symbolic Computation**: Exact analytical results without numerical approximation
- **Helicity Formalism**: Efficient calculations using helicity eigenstates
- **Modular Design**: Individual functions for each type of interaction
- **Physics Validation**: Built on established textbook formulations
- **Extensible Framework**: Easy to add new processes and interactions

## Requirements

- Python 3.9+
- SymPy
- NumPy (for numerical evaluation)

## Physical Conventions

- **Metric**: Minkowski signature (+,-,-,-)
- **Units**: Natural units (ℏ = c = 1)
- **Helicity**: λ = ±1/2 for fermions, λ = ±1,0 for bosons
- **Momentum**: Four-vectors as [E, pₓ, pᵧ, pᵤ] in Cartesian or [E, m, θ, φ] in spherical coordinates

## Contributing

This module follows the conventions and notation of modern particle physics textbooks. When adding new features, please ensure consistency with the existing helicity formalism and maintain proper documentation with physics context.

---


# Examples

The `examples` folder has a collection of Jupyter notebooks, written by Professor Christoph Berger in its majority. Part of it is outdated, so if you find a bug, feel free to submit an issue or a PR.


# TODO

- [ ] Refactor some part of the code
- [ ] Write a better documentation



# Acknowledgments

This package was based on the work published by [Professor Christoph Berger](https://profchristophberger.com/lehrbuch-elementarteilchenphysik/python/).