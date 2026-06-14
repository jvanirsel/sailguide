import dataproc
import time
import pyvisa
from pyvisa.resources import MessageBasedResource
from typing import cast, Callable
import numpy as np
from pathlib import Path

VMAX = 50.0
SOURCEMETERS = {
    'BIGGIE': 'USB0::0x05E6::0x2450::04475936::INSTR',
    'TUPAC': 'USB0::0x05E6::0x2450::04473229::INSTR',
    'EMINEM': 'USB0::0x05E6::0x2450::04536984::INSTR'
    }


def sweep(
        cfg: dict,
        delay:float = 1.0,
        is_rpa: bool = True,
        on_step: Callable = lambda e: None
        ) -> np.ndarray:

    pfx = 'RPA_' if is_rpa else 'LP_'

    nplc = float(cfg[pfx + 'NPLC'])
    vmin = float(cfg[pfx + 'VMIN'])
    vmax = float(cfg[pfx + 'VMAX'])
    steps = int(cfg[pfx + 'STEPS'])
    irange = float(cfg[pfx + 'CURRENT_RANGE'].replace(' nA', 'e-9').replace(' uA', 'e-6').replace(' mA', 'e-3'))

    settle_time = 2.0 * nplc / 60.0
    voltages = np.linspace(vmin, vmax, steps)
    vrange = VMAX

    rm = pyvisa.ResourceManager()
    src = cast(MessageBasedResource, rm.open_resource(SOURCEMETERS[cfg[pfx + 'SOURCE']]))
    mtr = cast(MessageBasedResource, rm.open_resource(SOURCEMETERS[cfg[pfx + 'METER']]))

    for ins in (src, mtr):
        ins.timeout = 5000
        ins.write_termination = '\n'
        ins.read_termination = '\n'
        ins.write('*RST')
        ins.write('*CLS')

    src.write(':SOUR:FUNC VOLT')
    src.write(f':SOUR:VOLT:ILIM {irange:.4e}')
    src.write(f':SOUR:VOLT:RANG {vrange:.4e}')
    src.write(f':SENS:CURR:RANG {irange:.4e}')
    src.write(':OUTP ON')

    mtr.write(':SENS:FUNC "CURR"')
    mtr.write(f':SENS:CURR:NPLC {nplc:.4e}')
    mtr.write(f':SOUR:VOLT:RANG {vrange:.4e}')
    mtr.write(f':SENS:CURR:RANG {irange:.4e}')
    mtr.write(':OUTP ON')

    src.write(f':SOUR:VOLT {voltages[0]}')
    time.sleep(delay)
    src.query(':MEAS:CURR?')

    iv_curve = np.full((steps, 3), np.nan)
    try:
        for k, v in enumerate(voltages):
            on_step(k)
            src.write(f':SOUR:VOLT {v}')
            time.sleep(settle_time)
            i_source = -float(src.query(':MEAS:CURR?'))
            i_meter = -float(mtr.query(':MEAS:CURR?'))
            iv_curve[k, 0] = v
            iv_curve[k, 1] = i_meter
            iv_curve[k, 2] = i_source

    finally:
        src.write(':SOUR:VOLT 0')
        src.write(':OUTP OFF')
        mtr.write(':OUTP OFF')

    return iv_curve


def fake_sweep(
        cfg: dict,
        delay:float = 1.0,
        is_rpa: bool = True,
        on_step: Callable = lambda e: None,
        fake_noise_level: float = 0.01
        ) -> np.ndarray:

    pfx = 'RPA_' if is_rpa else 'LP_'

    nplc = float(cfg[pfx + 'NPLC'])
    filepath = Path(__file__).parent / 'data' / 'sample_sweep'
    iv_curve = dataproc.load_iv_curve(filepath)
    settle_time = 0.2

    iv_noisy = iv_curve.copy()
    noise = 1 + fake_noise_level * np.random.randn(*iv_curve[:, 1:].shape)
    iv_noisy[:, 1:] *= noise

    max_i = len(iv_noisy) - 1

    time.sleep(delay)
    for i, d in enumerate(iv_noisy):
        on_step(i, max_i)
        time.sleep(settle_time)
    
    return iv_noisy