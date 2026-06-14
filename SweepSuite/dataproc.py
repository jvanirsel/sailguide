from tkobjects import CLBG, CLFG
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

CLPL = '#F00'
VMAX = 20.0


def load_iv_curve(
        filepath: Path,
        header_lines: int = 10,
        ) -> np.ndarray:
    
    filename = filepath / 'iv_curve.csv'

    if not filename.exists():
        print('IV data file not found.')
        return np.empty([0, 3])

    with open(filename, 'r') as f:
        lines = f.readlines()

    steps = 0
    for line in lines:
        if line.startswith('NUM SWEEP STEPS'):
            steps = int(line.strip('\n').split(',')[1])
            break
    assert steps > 1, 'Number of steps not found.'

    ct = 0
    iv_curve = np.full((steps, 3), np.nan)
    for i, line in enumerate(lines[header_lines:header_lines + steps]):
        data = line.strip('\n').split(',')
        iv_curve[i, :] = (float(data[0]), float(data[1]), float(data[2]))
        ct +=1
    return iv_curve


def save_iv_curve(
        filepath: Path,
        cfg: dict,
        iv_curve: np.ndarray,
        is_rpa: bool = True
        ) -> None:        

    pfx = 'RPA_' if is_rpa else 'LP_'
    filename = filepath / 'iv_curve.csv'
    irange = float(cfg[pfx + "CURRENT_RANGE"].replace(' nA', 'e-9').replace(' uA', 'e-6').replace(' mA', 'e-3'))

    with open(filename, 'w') as f:
        f.write(f'TIME,{np.datetime64("NOW")},\n')
        f.write(f'SOURCE,{cfg[pfx + "SOURCE"]},\n')
        f.write(f'METER,{cfg[pfx + "METER"]},\n')
        f.write(f'SWEEP VOLTAGE RANGE (V),{float(cfg[pfx + "VMIN"]):.4f},{float(cfg[pfx + "VMAX"]):.4f}\n')
        f.write(f'NUM SWEEP STEPS,{cfg[pfx + "STEPS"]},\n')
        f.write(f'NUM POWER LINE CYCLES,{float(cfg[pfx + "NPLC"]):.4f},\n')
        f.write(f'VRANGE,{VMAX:.4f},\n')
        f.write(f'IRANGE,{irange:.4f},\n')
        f.write(',,\n')

        f.write('Voltage (V),Meter current (A),Source current (A)\n')
        for p in iv_curve:
            f.write(f'{p[0]:.6e},{p[1]:.6e},{p[2]:.6e}\n')


def save_params(
        filepath: Path,
        fluid: dict,
        funds: dict,
        ) -> None:
    filename = filepath / 'params.csv'

    with open(filename, 'w') as f:
        f.write(f'TIME,{np.datetime64("NOW")},\n')
        f.write(',,\n')
        f.write('PARAMETER,VALUE,2SIGMA\n')
        f.write(f'BEAM SPEED (m/s),{fluid["U"][0]},{fluid["U"][1]}\n')
        f.write(f'BEAM ENERGY (eV),{fluid["E"][0]},{fluid["E"][1]}\n')
        f.write(f'BEAM DENSITY - FIT (m^-3),{fluid["N1"][0]},{fluid["N1"][1]}\n')
        f.write(f'BEAM DENSITY - SATURATION (m^-3),{fluid["N2"][0]},{fluid["N2"][1]}\n')
        f.write(f'BEAM TEMPERATURE (eV),{fluid["T"][0]},{fluid["T"][1]}\n')

        f.write(f'THERMAL SPEED (m/s),{funds["vt"][0]},{funds["vt"][1]}\n')
        f.write(f'AFLVEN SPEED (m/s),{funds["va"][0]},{funds["va"][1]}\n')
        f.write(f'PLASMA FREQUENCY (rad/s),{funds["wp"][0]},{funds["wp"][1]}\n')
        f.write(f'DEBYE LENGTH (m),{funds["ld"][0]},{funds["ld"][1]}\n')


def plot_data(
        ax: Axes,
        canvas: FigureCanvasTkAgg,
        data: np.ndarray,
        labels: tuple[str, ...],
        plot_column_2: bool = False,
        yscale: float = 1e9,
        plot_velocity: bool = False,
        mass: float = np.nan,
        imax: tuple[float, float, int] = (np.nan, np.nan, 0),
        ) -> None:

    if plot_velocity:
        assert mass > 0, 'Please provide particle mass.'
        v = data[:, 0]
        x = np.sign(v) * np.sqrt(2 * np.abs(v) / mass) / 1e3
    else:
        x = data[:, 0]

    ax.clear()
    ax.plot(x, data[:, 1] * yscale, label=labels[3], linewidth=2, color=CLPL)
    if plot_column_2:
        ax.plot(x, data[:, 2] * yscale, label=labels[4], linewidth=2, color=CLPL, linestyle='--')
        legend = ax.legend(loc='upper right', labelcolor=CLFG)
        legend.get_frame().set_facecolor(CLBG)
    ax.set_title(labels[0], color=CLFG)
    ax.set_xlabel(labels[1], color=CLFG)
    ax.set_ylabel(labels[2], color=CLFG)
    ax.grid()
    ax.xaxis.get_offset_text().set_color(CLFG)
    ax.yaxis.get_offset_text().set_color(CLFG)
    if imax[2]:
        id = imax[2]
        ax.axhline(y=(imax[0] - imax[1]) * yscale, color='red', linestyle=':')
        ax.axhline(y=(imax[0] + imax[1]) * yscale, color='red', linestyle=':')
        ax.plot(x[:id], data[:id, 1] * yscale, label='Saturation Current', linewidth=2, color='white')
        legend = ax.legend(loc='upper right', labelcolor=CLFG)
        legend.get_frame().set_facecolor(CLBG)

    canvas.draw()


def fit_linearly_modulated_gaussian(
        didv_curve: np.ndarray,
        mass: float,
        ) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:

    v = didv_curve[:, 0]
    u = np.sign(v) * np.sqrt(2 * np.abs(v) / mass)
    dvdu = mass * u
    didu_curve = didv_curve.copy()
    didu_curve[:, 0] = u
    didu_curve[:, 1] = dvdu * didv_curve[:, 1]

    x = didu_curve[:, 0]
    y = didu_curve[:, 1]

    a0 = (np.max(y) - np.min(y)) / np.max(np.abs(x))
    indices = np.where(y > a0 / 2)[0]
    if len(indices) >= 2:
        fwhm_est = x[indices[-1]] - x[indices[0]]
        sigma0 = fwhm_est / (2*np.sqrt(2*np.log(2)))
    else:
        sigma0 = (np.max(x) - np.min(x)) / 10.0
    betasq0 = (2 * sigma0)**-1.0
    mu0 = x[np.argmax(y)]
    if mu0 < 0:
        a0 *= -1
    p0 = [a0, betasq0, mu0]

    def model(x, a, betasq, mu):
        return a * x * np.exp(-betasq * (x - mu)**2)

    popt, pcov = curve_fit(model, x, y, p0=p0)
    print(f'Optimal parameters: a = {popt[0]:.4e},  betasq = {popt[1]:.4e},  mu = {popt[2]:.4e}')

    perr = 2 * np.sqrt(np.diag(pcov))
    yfit = model(x, *popt)
    residuals = y - yfit
    dof = max(1, len(y) - len(popt))
    chi2 = np.sum(residuals**2)
    reduced_chi2 = chi2 / dof
    squared_sum_residuals = np.sum(residuals**2)
    squared_sum_total = np.sum((y - np.mean(y))**2)
    r2 = 1 - squared_sum_residuals / squared_sum_total
    fit_info = {'chi2': chi2, 'red_chi2': reduced_chi2, 'r2': r2, 'cov': pcov, 'dof': dof}

    didu_curve[:, 2] = yfit
    dvdu[dvdu == 0] = 1e-10
    didv_curve[:, 2] = didu_curve[:, 2] / dvdu

    return didv_curve, popt, perr, fit_info


def saturation_current(
        iv_curve: np.ndarray,
        factor: float = 0.03
        ) -> tuple[float, float, int]:
    
    i = iv_curve[:, 1]
    di_max = np.quantile(i, 0.99) * factor
    mask = np.abs(np.diff(i)) > di_max
    if np.any(mask):
        id = np.argmax(mask)
    else:
        id = -1
    
    print(f'Saturation cutoff at {iv_curve[id, 0]} V.')

    imax = np.mean(i[:id])
    dimax = 2 * np.std(i[:id])

    return float(imax), float(dimax), int(id)