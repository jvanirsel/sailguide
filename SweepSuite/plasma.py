import numpy as np
from constants import _Q_ELEM, _EPS0, _MU0


def compute_plasma_fluid_params(
        popt: np.ndarray,
        perr: np.ndarray,
        mass: float,
        charge: float,
        Aeff: float,
        imax: tuple[float, float, int],
        ) -> dict[str, tuple[float, float]]:

    u = popt[2] # m s^-1
    beta = popt[1]**0.5 # s m^-1
    e = mass * u**2 / 2 # eV
    q = charge * _Q_ELEM # C

    if Aeff == 0 or q == 0 or beta == 0:
        n1 = 0.0
    else:
        n1 = popt[0] * np.sqrt(np.pi) / (Aeff * q * beta) # m^-3
    if beta == 0:
        t = 0.0
    else:
        t = mass / (beta**2) # eV

    du = perr[2]
    de = mass * np.abs(u) * du
    dbeta = perr[1] / (2 * beta)
    dn1 = n1 * np.sqrt((dbeta / beta)**2 + (perr[0] / popt[0])**2)
    dt = 2 * t * dbeta / beta
    n2 = imax[0] / (Aeff * q * u)
    dn2 = n2 * np.sqrt((du / u)**2 + (imax[1] / imax[0])**2)

    return {'U': (u, du), 'E': (e, de), 'N1': (n1, dn1), 'N2': (n2, dn2), 'T': (t, dt)}


def compute_fundemental_params(
        fluid: dict,
        m: float, # eV s^2 m^-2
        b: float, # T
        ) -> dict[str, tuple[float, float]]:
    
    t = fluid['T'][0] # eV
    dt = fluid['T'][1]
    n = fluid['N1'][0] # m^-3
    dn = fluid['N1'][1]

    vt = np.sqrt(t / m) # m/s
    dvt = vt * (dt / t) / 2
    va = b / np.sqrt(_MU0 * n * m) # m/s
    dva = va * (dn / n) / 2
    
    wp = np.sqrt(n / (m * _EPS0)) # rad/s
    dwp = wp * (dn / n) / 2

    ld = vt / wp if wp > 0 else np.nan # m
    dld = ld * np.sqrt((dvt / vt)**2 + (dwp / wp)**2)

    return {'wp': (wp, dwp), 'vt': (vt, dvt), 'va': (va, dva), 'ld': (ld, dld)}