from constants import M, Z
import tkinter as tk
from pathlib import Path
import numpy as np


def update(entry: tk.Entry, val: str):
    if entry.cget('state') == 'readonly':
        entry.config(state='normal')
        entry.delete(0, tk.END)
        entry.insert(0, val)
        entry.config(state='readonly')
    else:
        entry.delete(0, tk.END)
        entry.insert(0, val)


def latest(paths: list[Path]) -> list:
    return sorted(paths, key=lambda p: p.stat().st_ctime, reverse=True)


def nd(curve: np.ndarray) -> np.ndarray:
    x = curve[:, 0]
    y1 = curve[:, 1]

    d = np.full_like(curve, np.nan)
    d[:, 0] = x
    d[:, 1] = -np.gradient(y1, x)
    d[:, 2] = np.full_like(x, np.nan)

    return d


def weighted_mass(cfg: dict) -> float:
    wm = 0.0
    tw = 0.0
    for s, w in cfg.items():
        if s == 'BMAG':
            continue
        wm += float(w) * M[s]
        tw += float(w)
    return wm / tw


def weighted_charge(cfg: dict) -> float:
    wz = 0.0
    tw = 0.0
    for s, w in cfg.items():
        if s == 'BMAG':
            continue
        wz += float(w) * Z[s]
        tw += float(w)
    return wz / tw

def bar(label: str, i: int, max: int, bar_len = 50) -> str:
    pct = float(i) / float(max)
    fill = int(bar_len * pct)
    return f'{label}: ' + '\u2B24' * fill + '\u25EF' * (bar_len-fill) + f' {100 * pct:.0f} %'
