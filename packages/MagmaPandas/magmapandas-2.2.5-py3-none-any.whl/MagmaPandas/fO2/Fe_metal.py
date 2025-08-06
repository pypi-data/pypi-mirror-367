import numpy as np
import pandas as pd
from scipy.constants import R

"""
Based on supplementary text to:

K. Armstrong et al. (2019) Deep magma ocean formation set the oxidation state of Earth’s mantle. Science. Vol 365, pp. 903-906

unless specified otherwise
"""

Fe_bulk_modulus = pd.DataFrame(
    {"k0": [45.8, 37], "k0_p": [4.7, 8]}, index=("Fe_metal", "FeO_melt")
)  # GPa

activities = pd.Series({"FeO_melt": 1.5, "Fe_metal": 1})


def Gibbs0(T_K):
    """
    Standard state free energy of the reaction

    Fe(metal) + 0.5O2 -> FeO(liq)

    Table 6 from:

    St.C. O'Neill et al. (2002) The effect of melt composition on trace element partitioning: an experimental investigation of the activity coefficients of FeO, NiO, CoO, MoO2 and MoO3 in silicate melts. Chemical Geology. Vol 186, pp. 151-181

    J/mol
    """

    return -244118 + 115.559 * T_K - 8.474 * T_K * np.log(T_K)


def V0_FeO(T_K):
    """
    Equation S10

    J/GPa
    """

    return 13650 + 2.92 * (T_K - 1673)


def V0_Feliquid(T_K):
    """
    page 10
    Why is this the same as V0(FeO)?
    THIS IS WRONG

    J/GPa
    """
    return 13650 + 2.92 * (T_K - 1673)


def _a(k0, k0_p):
    """
    S7
    """
    k0_pp = -k0_p / k0
    return (1 + k0_p) / (1 + k0_p + k0 * k0_pp)


def _b(k0, k0_p):
    """
    S8
    """
    k0_pp = -k0_p / k0
    return k0_p / k0 - k0_pp / (1 + k0_p)


def _c(k0, k0_p):
    """
    S9
    """
    k0_pp = -k0_p / k0
    return (1 + k0_p + k0 * k0_pp) / (k0_p**2 + k0_p - k0 * k0_pp)


def VdP(P_bar, T_K, phase):
    """
    S10
    """

    P_GPa = P_bar / 1e4

    k0, k0_p = Fe_bulk_modulus.loc[phase]

    V0 = {"Fe_metal": V0_Feliquid, "FeO_melt": V0_FeO}[phase](T_K=T_K)

    a = _a(k0=k0, k0_p=k0_p)
    b = _b(k0=k0, k0_p=k0_p)
    c = _c(k0=k0, k0_p=k0_p)

    part_1 = a * (1 - (1 + b + P_GPa) ** (1 - c))
    part_2 = b * (c - 1) * P_GPa

    return P_GPa * V0 * (1 - a + part_1 / part_2)


def deltaGibbs(P_bar, T_K):

    G0 = Gibbs0(T_K=T_K)
    VdP_FeO = VdP(P_bar=P_bar, T_K=T_K, phase="FeO_melt")
    VdP_Fe = VdP(P_bar=P_bar, T_K=T_K, phase="Fe_metal")
    dVdP = VdP_FeO - VdP_Fe

    return G0 + dVdP


def calculate_fO2(T_K, P_bar, XFeO_melt, XFe_metal=1):
    """
    S14

    calculate fO2 at the equilibrium

    2Fe(liquid) + O2 -> 2FeO(melt)

    based om measured melt FeO mol fractions.
    """

    dG = deltaGibbs(P_bar=P_bar, T_K=T_K)

    log10fO2 = (
        dG / (R * T_K * np.log(10))
        + 2 * np.log10(XFeO_melt * activities["FeO_melt"])
        - 2 * np.log10(XFe_metal * activities["Fe_metal"])
    )

    return 10**log10fO2
