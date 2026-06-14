import tkobjects, utils, sweep, dataproc, plasma
from tkobjects import CLBG, CLFG, FTSZ
from sweep import VMAX
import tkinter as tk
import tkinter.font as tkfont
from screeninfo import get_monitors
from collections.abc import Callable
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading

CONFIG_PATH = Path('config')
DATA_PATH = Path('data')
PROFILE = 'default.profile'
CONFIG_ON_STARTUP = True


################ MAIN ################

class gui:
    def __init__(self) -> None:

        # configurations
        self._configure_window_geometry()
        self._configure_settings()
        plt.rcParams.update({
            'font.size': FTSZ,
            'axes.titlesize': FTSZ,
            'axes.labelsize': FTSZ,
            'xtick.labelsize': FTSZ,
            'ytick.labelsize': FTSZ,
            'legend.fontsize': FTSZ,
        })

        # create root window
        self.root = tk.Tk()
        self.root.geometry(f'{self.width}x{self.height}+{self.x}+{self.y}')
        self.root.state('zoomed')
        self.root.config(bg=CLBG, padx=10)

        self.font = tkfont.nametofont('TkDefaultFont')
        self.font.configure(size=FTSZ)
        self.root.option_add('*font', self.font)

        # key bindings
        self.root.bind('<F11>', self.on_f11)
        self.root.bind('<Escape>', self.on_esc)
        self.root.protocol('WM_DELETE_WINDOW', self.on_exit)

        self.root.bind('<F1>', self.open_configure_sweep)
        self.root.bind('<F2>', self.open_configure_rpa)
        self.root.bind('<F3>', self.open_configure_lp)
        self.root.bind('<F4>', self.open_configure_plasma)

        # toolbar & statusbar
        self._generate_toolbar()
        self._generate_statusbar()

        # load configs
        self.load_global_config()
        self.load_sweep_config()
        self.load_rpa_config()
        self.load_lp_config()
        self.load_plasma_config()

        # content frame
        self.main_frame = tk.Frame(self.root, bg=CLBG)
        self.main_frame.pack(side='top', fill='both', expand=True)

        # panel frame
        self.panel_frm = tk.Frame(self.main_frame, bg=CLBG)
        self.panel_frm.pack(side='left', fill='both')

        tk.Label(self.panel_frm, text='RPA', bg=CLBG, fg=CLFG).grid(row=1, column=1, sticky='ew')
        tk.Label(self.panel_frm, text='LP', bg=CLBG, fg=CLFG).grid(row=1, column=2, sticky='ew')
        self.panel_sweep_srcmtr, r = tkobjects.entry(self.panel_frm, 2, 'Source / Meter', double_entry=True, readonly=True)
        self.panel_sweep_vrange, r = tkobjects.entry(self.panel_frm, r, 'Voltage Ranges', double_entry=True, readonly=True)
        self.panel_sweep_nsteps, r = tkobjects.entry(self.panel_frm, r, 'Sweep steps', double_entry=True, readonly=True)
        self.panel_sweep_nplcir, r = tkobjects.entry(self.panel_frm, r, 'NPLC / IRANGE', double_entry=True, readonly=True)

        r = tkobjects.vspace(self.panel_frm, r)
        self.panel_rpa_shape, r = tkobjects.entry(self.panel_frm, r, 'Aperture Shape', readonly=True)
        self.panel_rpa_scrns, r = tkobjects.entry(self.panel_frm, r, 'Screens', readonly=True)
        self.panel_rpa_prtcl, r = tkobjects.entry(self.panel_frm, r, 'Particle Type', readonly=True)
        self.panel_rpa_effar, r = tkobjects.entry(self.panel_frm, r, 'Effecitve Area', readonly=True)

        r = tkobjects.vspace(self.panel_frm, r)
        self.panel_plasma_major, r = tkobjects.entry(self.panel_frm, r, 'Composition', readonly=True)
        self.panel_plasma_water, r = tkobjects.entry(self.panel_frm, r, 'Contaminants', readonly=True)
        self.panel_plasma_bmag, r = tkobjects.entry(self.panel_frm, r, 'Magnetic Field', readonly=True)

        r = tkobjects.vspace(self.panel_frm, r)
        self.sweep_label, r = tkobjects.entry(self.panel_frm, r, 'Sweep label', value_type='alnum')
        self.panel_sweep_folders, r= tkobjects.combo(self.panel_frm, r, 'Load Sweep', self.get_sweep_folders())

        self.panel_sweep_btns_frm = tk.Frame(self.panel_frm, bg=CLBG)
        self.panel_sweep_btns_frm.grid(row=r, column=0, columnspan=3, sticky='ew', pady=15)
        tkobjects.button(self.panel_sweep_btns_frm, 'Load Sweep', self.on_load_sweep)
        tkobjects.button(self.panel_sweep_btns_frm, 'Sweep All', self.on_sweep_all)
        tkobjects.button(self.panel_sweep_btns_frm, 'Sweep LP', self.on_sweep_lp)
        tkobjects.button(self.panel_sweep_btns_frm, 'Sweep RPA', self.on_sweep_rpa)
        tkobjects.button(self.panel_sweep_btns_frm, 'Config All', self.on_config_all)

        self.panel_beam_velocity, r = tkobjects.entry(self.panel_frm, r+1, 'Beam Speed', readonly=True, units='km/s')
        self.panel_beam_energy, r = tkobjects.entry(self.panel_frm, r+1, 'Beam Energy', readonly=True, units='eV')
        self.panel_beam_density, r = tkobjects.entry(self.panel_frm, r+1, 'Beam Dens. 10^', readonly=True, units='m\u207B\u00B3', double_entry=True)
        self.panel_beam_temperature, r = tkobjects.entry(self.panel_frm, r+1, 'Beam Temp.', readonly=True, units='eV')

        r = tkobjects.vspace(self.panel_frm, r)
        self.panel_vt, r = tkobjects.entry(self.panel_frm, r, 'Thermal Speed', readonly=True, units='km/s')
        self.panel_va, r = tkobjects.entry(self.panel_frm, r, 'Alfv\u00E9n Speed', readonly=True, units='km/s')
        self.panel_wp, r = tkobjects.entry(self.panel_frm, r, 'Plasma Freq.', readonly=True, units='rad/s')
        self.panel_ld, r = tkobjects.entry(self.panel_frm, r, 'Debye Length', readonly=True, units='mm')

        # figures frame
        self.figures_frm = tk.Frame(self.main_frame, bg=CLBG)
        self.figures_frm.pack(side='right', fill='both', expand=True)

        # plot check boxes
        self.figure_checks_frm = tk.Frame(self.figures_frm, bg=CLBG)
        self.figure_checks_frm.pack(side='bottom', fill='x', padx=80)

        self.plot_velocity = tk.BooleanVar(value=False)
        self.plot_source_current = tk.BooleanVar(value=False)
        tkobjects.check(self.figure_checks_frm, 'Plot Velocity', self.plot_velocity, self.on_load_sweep)
        tkobjects.check(self.figure_checks_frm, 'Plot Source Current', self.plot_source_current, self.on_load_sweep)

        # plot
        self.figure_plot_frm = tk.Frame(self.figures_frm, bg=CLBG)
        self.figure_plot_frm.pack(side='top', fill='both', expand=True)

        self.fig, (self.ax0, self.ax1) = plt.subplots(2, 1)
        self.fig.patch.set_color(CLBG)
        self.fig.tight_layout()
        for ax in [self.ax0, self.ax1]:
            assert isinstance(ax, Axes)
            ax.xaxis.label.set_color(CLFG)
            ax.yaxis.label.set_color(CLFG)
            ax.title.set_color(CLFG)
            ax.tick_params(axis='both', colors=CLFG)
            ax.set_facecolor(CLBG)
            ax.grid(color='#444')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.figure_plot_frm)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', expand=True, fill='both')       

        # config on startup
        if CONFIG_ON_STARTUP:
            self.on_config_all()



################ TOOLBAR ################

    def _generate_toolbar(self) -> None:
        self.toolbar = tk.Frame(self.root, bg=CLBG)
        self.toolbar.pack(side='top', fill='x', pady=(0, 5))

        self._toolbar_menu('Action', [
            ('Setup', self.open_configure_global),
            ('Set Default', self.set_global_default),
            ('Quit', self.on_exit)
            ])
        
        self._toolbar_menu('Configure', [
            ('Sweep', self.open_configure_sweep),
            ('RPA', self.open_configure_rpa),
            ('LP', self.open_configure_lp),
            ('Plasma', self.open_configure_plasma),
            ])

        self._toolbar_menu('View', [
            ('Change Fontsize', self.on_change_fontsize)
            ])

        self._toolbar_menu('Help', [
            ('Get good', self.on_exit)
            ])


    def _toolbar_menu(self, name: str, options: list[tuple[str, Callable]]) -> None:
        button = tk.Menubutton(self.toolbar, text=name, bg=CLBG, fg=CLFG)
        button.pack(side='left')
        menu = tk.Menu(button, tearoff=0, bg=CLBG, fg=CLFG, activebackground='#333')
        button['menu'] = menu
        for label, command in options:
            menu.add_command(label=label, command=command)


    def on_action_1(self, event=None) -> None:
        self.msg('Action 1')


    def on_view_1(self, event=None) -> None:
        self.msg('View 1')

################ STATUS BAR ################

    def _generate_statusbar(self) -> None:
        self.statusbar = tk.Frame(self.root, bg=CLBG)
        self.statusbar.pack(side='bottom', fill='x', pady=5)

        self.status = tk.Entry(self.statusbar, state='readonly', readonlybackground='#444', fg=CLFG)
        self.status.pack(side='left', fill='x', expand=True)

        self.plasma_config_lamp = tkobjects.Lamp(self.statusbar, label='Plasma')
        self.plasma_config_lamp.pack(side='right', padx=5)

        self.lp_config_lamp = tkobjects.Lamp(self.statusbar, label='LP')
        self.lp_config_lamp.pack(side='right', padx=5)

        self.rpa_config_lamp = tkobjects.Lamp(self.statusbar, label='RPA')
        self.rpa_config_lamp.pack(side='right', padx=5)

        self.sweep_config_lamp = tkobjects.Lamp(self.statusbar, label='Sweep')
        self.sweep_config_lamp.pack(side='right', padx=5)

        tk.Label(self.statusbar, text='Configuration status: ', bg=CLBG, fg=CLFG, font=('Courier New', FTSZ)).pack(side='right', padx=(10, 5))


################ CONFIG PANEL ################

    def fill_panel_sweep_cfg(self) -> None:
        utils.update(self.panel_sweep_srcmtr[0], f'{self.sweep_cfg["RPA_SOURCE"]} / {self.sweep_cfg["RPA_METER"]}')
        utils.update(self.panel_sweep_srcmtr[1], self.sweep_cfg["LP_SOURCE"])
        utils.update(self.panel_sweep_vrange[0], f'{float(self.sweep_cfg["RPA_VMIN"])} \u2013 {float(self.sweep_cfg["RPA_VMAX"])} V')
        utils.update(self.panel_sweep_vrange[1], f'{float(self.sweep_cfg["LP_VMIN"])} \u2013 {float(self.sweep_cfg["LP_VMAX"])} V')
        utils.update(self.panel_sweep_nsteps[0], self.sweep_cfg["RPA_STEPS"])
        utils.update(self.panel_sweep_nsteps[1], self.sweep_cfg["LP_STEPS"])
        utils.update(self.panel_sweep_nplcir[0], f'{self.sweep_cfg["RPA_NPLC"]} / {self.sweep_cfg["RPA_CURRENT_RANGE"]}')
        utils.update(self.panel_sweep_nplcir[1], f'{self.sweep_cfg["LP_NPLC"]} / {self.sweep_cfg["LP_CURRENT_RANGE"]}')

    def fill_panel_rpa_cfg(self) -> None:
        dim = 'diameter' if self.rpa_cfg['SHAPE'] == 'CIRCLE' else 'side length'
        size = float(self.rpa_cfg["SIZE"]) * 1e-3 # m
        area = np.pi * (size / 2)**2 if self.rpa_cfg['SHAPE'] == 'CIRCLE' else size**2 # m^2
        self.effarea = area * (float(self.rpa_cfg['OPACITY']) / 100)**int(self.rpa_cfg['SCREENS']) # m^2
        utils.update(self.panel_rpa_shape[0], f'{self.rpa_cfg["SHAPE"].capitalize()} with a {size * 1e3} mm {dim}')
        utils.update(self.panel_rpa_scrns[0], f'{self.rpa_cfg["SCREENS"]} screens with {self.rpa_cfg["OPACITY"]}% opacity each')
        utils.update(self.panel_rpa_prtcl[0], f'Configured for {self.rpa_cfg["PARTICLES"].lower()}')
        utils.update(self.panel_rpa_effar[0], f'{self.effarea * 1e6:.1f} mm\u00B2')

    def fill_panel_plasma_cfg(self) -> None:
        s0 = f'{self.plasma_cfg["Ar+"]}% Ar\u207A, ' if int(self.plasma_cfg["Ar+"]) > 0 else ''
        s1 = f'{self.plasma_cfg["Ar++"]}% Ar\u00B2\u207A, ' if int(self.plasma_cfg["Ar++"]) > 0 else ''
        s2 = f'{self.plasma_cfg["N2+"]}% N\u2082\u207A, ' if int(self.plasma_cfg["N2+"]) > 0 else ''
        s3 = f'{self.plasma_cfg["N+"]}% N\u207A, ' if int(self.plasma_cfg["N+"]) > 0 else ''
        s4 = f'{self.plasma_cfg["He+"]}% He\u207A, ' if int(self.plasma_cfg["He+"]) > 0 else ''
        major = f'{s0}{s1}{s2}{s3}{s4}'.strip(', ')
        utils.update(self.panel_plasma_major[0], major)

        s4 = f'{self.plasma_cfg["H2O+"]}% H\u2082O\u207A, ' if int(self.plasma_cfg["H2O+"]) > 0 else ''
        s5 = f'{self.plasma_cfg["H3O+"]}% H\u2083O\u207A, ' if int(self.plasma_cfg["H3O+"]) > 0 else ''
        s6 = f'{self.plasma_cfg["OH+"]}% OH\u207A, ' if int(self.plasma_cfg["OH+"]) > 0 else ''
        s7 = f'{self.plasma_cfg["NO+"]}% NO\u207A, ' if int(self.plasma_cfg["NO+"]) > 0 else ''
        water = f'{s4}{s5}{s6}{s7}'.strip(', ')
        utils.update(self.panel_plasma_water[0], water if water else 'None')

        b = f'{float(self.plasma_cfg["BMAG"]) * 1e6:.3f} \u03BCT'
        utils.update(self.panel_plasma_bmag[0], b)

    def fill_panel_fluid_params(self) -> None:
        u = self.fluid['U']
        e = self.fluid['E']
        n1 = self.fluid['N1']
        n2 = self.fluid['N2']
        t = self.fluid['T']
        utils.update(self.panel_beam_velocity[0], f'{u[0] / 1e3:.3f} \u00B1 {u[1] / 1e3:.3f}')
        utils.update(self.panel_beam_energy[0], f'{e[0]:.3f} \u00B1 {e[1]:.3f}')
        utils.update(self.panel_beam_density[0], f'{np.log10(n1[0]):.3f} \u00B1 {np.log10(n1[1]):.3f}')
        utils.update(self.panel_beam_density[1], f'{np.log10(n2[0]):.3f} \u00B1 {np.log10(n2[1]):.3f}')
        utils.update(self.panel_beam_temperature[0], f'{t[0]:.3f} \u00B1 {t[1]:.3f}')

        vt = self.funds['vt']
        wp = self.funds['wp']
        va = self.funds['va']
        ld = self.funds['ld']
        utils.update(self.panel_vt[0], f'{vt[0] / 1e3:.3f} \u00B1 {vt[1] / 1e3:.3f}')
        utils.update(self.panel_va[0], f'{va[0] / 1e3:.3f} \u00B1 {va[1] / 1e3:.3f}')
        utils.update(self.panel_wp[0], f'{wp[0]:.3f} \u00B1 {wp[1]:.3f}')
        utils.update(self.panel_ld[0], f'{ld[0] * 1e3:.3f} \u00B1 {ld[1] * 1e3:.3f}')


################ CONFIGURATION FUNCTIONS ################

    def close_config_windows(self, q: str = ''):
        if hasattr(self, 'window') and q == 'all':
            self.window.destroy()
        if hasattr(self, 'save_window'):
            self.save_window.destroy()
        if hasattr(self, 'load_window'):
            self.load_window.destroy()
        if hasattr(self, 'sure_window'):
            self.sure_window.destroy()


    def load_config(self, ext: str, cfg_name: None | str, try_loadfile: bool = True) -> dict[str, str]:
        if hasattr(self, 'loadfile') and try_loadfile:
            filepath = self.loadfile_var.get()
        elif cfg_name:
            filepath = CONFIG_PATH / f'{cfg_name}.{ext}'
        else:
            filepath = CONFIG_PATH / f'default.{ext}'
            print('Set config to default.')

        if hasattr(self, 'load_window'):
            self.load_window.destroy()

        with open(filepath, 'r') as f:
            lines = f.readlines()
        self.msg(f'Loaded {filepath}')

        cfg = {}
        for line in lines:
            if line.strip('\n'):
                entry = line.strip('\n').split(': ')
                cfg[entry[0]] = entry[1]
        return cfg


    def on_load_config(self, ext: str, command: Callable) -> None:
        self.close_config_windows()
        self.load_window = tk.Toplevel(self.root, bg=CLBG, padx=10, pady=10)
        self.load_window.title('')
        self.load_window.resizable(False, False)
        self.load_window.focus_set()

        configs = utils.latest(list(CONFIG_PATH.glob(f'*.{ext}')))
        self.loadfile_var = tk.StringVar()
        self.loadfile = tkobjects.load(self.load_window, 'Load', configs, command, self.loadfile_var)
        self.load_window.bind('<Return>', command)


    def on_save_config(self, command: Callable):
        self.close_config_windows()
        self.save_window = tk.Toplevel(self.root, bg=CLBG, padx=10, pady=10)
        self.save_window.title('')
        self.save_window.resizable(False, False)
        self.save_window.focus_set()

        self.filestem = tkobjects.save(self.save_window, 'Save & Confirm', command, value_type='alnum')
        self.filestem.focus_set()
        self.filestem.bind('<Return>', command)


    def on_cancel_config(self, event=None) -> None:
        self.close_config_windows('all')

################ GLOBAL CONFIGURATION ################

    def set_global_default(self, event=None) -> None:
        if self.assured():
            with open(CONFIG_PATH / 'default.profile', 'w') as f:
                f.write(f'SWEEP: {self.global_cfg["SWEEP"]}\n')
                f.write(f'RPA: {self.global_cfg["RPA"]}\n')
                f.write(f'LP: {self.global_cfg["LP"]}\n')
                f.write(f'PLASMA: {self.global_cfg["PLASMA"]}\n')


    def load_global_config(self, event=None) -> None:
        self.global_cfg = self.load_config('profile', self.global_cfg_name)
        if hasattr(self, 'window'):
            self.fill_global_config()

    def open_configure_global(self, event=None) -> None:
        self.close_config_windows('all')
        self.window = tk.Toplevel(self.root, bg=CLBG)
        self.window.title('Save Profile')
        self.window.resizable(False, False)
        self.window.focus_set()

        entries = tk.Frame(self.window, bg=CLBG)
        entries.pack(side='top', padx=(10, 10))

        self.sweep_cfgs = [p.stem for p in utils.latest(list(CONFIG_PATH.glob(f'*.sweep')))]
        self.rpa_cfgs = [p.stem for p in utils.latest(list(CONFIG_PATH.glob(f'*.rpa')))]
        self.plasma_cfgs = [p.stem for p in utils.latest(list(CONFIG_PATH.glob(f'*.plasma')))]

        r = 0
        r = tkobjects.header(entries, r, 'Select Configurations')
        self.global_sweep_cfg, r = tkobjects.combo(entries, r, 'Sweep', values=self.sweep_cfgs)
        self.global_rpa_cfg, r = tkobjects.combo(entries, r, 'RPA', values=self.rpa_cfgs)
        self.global_plasma_cfg, r = tkobjects.combo(entries, r, 'Plasma', values=self.plasma_cfgs)

        self.fill_global_config()

        options = tk.Frame(self.window, bg=CLBG)
        options.pack(side='bottom', fill='x', padx=20, pady=(40, 20))
        tkobjects.button(options, 'Configure', self.on_global_config)
        tkobjects.button(options, 'Load', self.on_load_global_config)
        tkobjects.button(options, 'Save', self.on_save_global_config)
        tkobjects.button(options, 'Cancel', self.on_cancel_config)
        self.window.bind('<Return>', self.on_global_config)


    def fill_global_config(self) -> None:
        self.global_sweep_cfg.set(self.global_cfg['SWEEP'])
        self.global_rpa_cfg.set(self.global_cfg['RPA'])
        self.global_plasma_cfg.set(self.global_cfg['PLASMA'])


    def on_global_config(self, event=None) -> None:
        self.global_cfg['SWEEP'] = self.global_sweep_cfg.get()
        self.global_cfg['RPA'] = self.global_rpa_cfg.get()
        self.global_cfg['PLASMA'] = self.global_plasma_cfg.get()

        self.sweep_cfg = self.load_config('sweep', self.global_sweep_cfg.get(), try_loadfile=False)
        self.rpa_cfg = self.load_config('rpa', self.global_rpa_cfg.get(), try_loadfile=False)
        self.plasma_cfg = self.load_config('plasma', self.global_plasma_cfg.get(), try_loadfile=False)

        self.close_config_windows('all')
        self.sweep_configured = True
        self.rpa_configured = True
        self.plasma_configured = True
        self.sweep_config_lamp.on()
        self.rpa_config_lamp.on()
        self.plasma_config_lamp.on()

        self.fill_panel_sweep_cfg()
        self.fill_panel_rpa_cfg()
        self.fill_panel_plasma_cfg()
        self.msg('Loaded profile.')


    def on_load_global_config(self, event=None) -> None:
        self.on_load_config('profile', self.load_global_config)


    def on_save_global_config(self, event=None) -> None:
        self.on_save_config(self.save_global_config)


    def save_global_config(self, event=None) -> None:
        filestem = self.filestem.get()
        if filestem:
            filepath = CONFIG_PATH / f'{filestem}.profile'
            if filepath.exists():
                self.err('Profile already exists.')
                return
            
            with open(filepath, 'w') as f:
                f.write(f'SWEEP: {self.global_sweep_cfg.get()}\n')
                f.write(f'RPA: {self.global_rpa_cfg.get()}\n')
                f.write(f'PLASMA: {self.global_plasma_cfg.get()}\n')

            self.msg(f'Saved {filepath}')

            self.save_window.destroy()
            self.on_global_config()
        else:
            self.err('Please enter a label.')


################ SWEEP CONFIGURATION ################

    def load_sweep_config(self, event=None) -> None:
        self.sweep_cfg = self.load_config('sweep', self.sweep_cfg_name)
        if hasattr(self, 'window'):
            self.fill_sweep_config()

    def open_configure_sweep(self, event=None) -> None:
        self.close_config_windows('all')
        self.window = tk.Toplevel(self.root, bg=CLBG)
        self.window.title('Configure Sweep')
        self.window.resizable(False, False)
        self.window.focus_set()

        entries = tk.Frame(self.window, bg=CLBG)
        entries.pack(side='top', padx=(10, 10))

        iranges = ['1 nA', '10 nA', '100 nA', '1 uA', '10 uA', '100 uA', '1 mA']
        sourcemeters = ['BIGGIE', 'TUPAC', 'EMINEM']

        r = 1
        r = tkobjects.header(entries, r, 'RPA Sweep Configuration')
        self.rpa_sweep_source, r = tkobjects.combo(entries, r, 'Source', values=sourcemeters)
        self.rpa_sweep_meter, r = tkobjects.combo(entries, r, 'Meter', values=sourcemeters)
        self.rpa_sweep_vrange, r = tkobjects.entry(entries, r, 'Sweep Range', units='V', double_entry=True, value_type='float')
        self.rpa_sweep_steps, r = tkobjects.entry(entries, r, 'Number of Steps', value_type='spint')
        self.rpa_sweep_nplc, r = tkobjects.entry(entries, r, 'NPLC', value_type='nnfloat')
        self.rpa_sweep_irange, r = tkobjects.combo(entries, r, 'Current Range', iranges, units='nA')

        r = tkobjects.header(entries, r + 2, 'LP Sweep Configuration')
        self.lp_sweep_source, r = tkobjects.combo(entries, r, 'Source', values=sourcemeters)
        self.lp_sweep_vrange, r = tkobjects.entry(entries, r, 'Sweep Range', units='V', double_entry=True, value_type='float')
        self.lp_sweep_steps, r = tkobjects.entry(entries, r, 'Number of Steps', value_type='spint')
        self.lp_sweep_nplc, r = tkobjects.entry(entries, r, 'NPLC', value_type='nnfloat')
        self.lp_sweep_irange, r = tkobjects.combo(entries, r, 'Current Range', iranges, units='nA')

        self.fill_sweep_config()

        options = tk.Frame(self.window, bg=CLBG)
        options.pack(side='bottom', fill='x', padx=20, pady=(40, 20))
        tkobjects.button(options, 'Configure', self.on_sweep_config)
        tkobjects.button(options, 'Load', self.on_load_sweep_config)
        tkobjects.button(options, 'Save', self.on_save_sweep_config)
        tkobjects.button(options, 'Cancel', self.on_cancel_config)
        self.window.bind('<Return>', self.on_sweep_config)


    def fill_sweep_config(self) -> None:
        self.rpa_sweep_source.set(self.sweep_cfg['RPA_SOURCE'])
        self.rpa_sweep_meter.set(self.sweep_cfg['RPA_METER'])
        utils.update(self.rpa_sweep_vrange[0], self.sweep_cfg['RPA_VMIN'])
        utils.update(self.rpa_sweep_vrange[1], self.sweep_cfg['RPA_VMAX'])
        utils.update(self.rpa_sweep_steps[0], self.sweep_cfg['RPA_STEPS'])
        utils.update(self.rpa_sweep_nplc[0], self.sweep_cfg['RPA_NPLC'])
        self.rpa_sweep_irange.set(self.sweep_cfg['RPA_CURRENT_RANGE'])

        self.lp_sweep_source.set(self.sweep_cfg['LP_SOURCE'])
        utils.update(self.lp_sweep_vrange[0], self.sweep_cfg['LP_VMIN'])
        utils.update(self.lp_sweep_vrange[1], self.sweep_cfg['LP_VMAX'])
        utils.update(self.lp_sweep_steps[0], self.sweep_cfg['LP_STEPS'])
        utils.update(self.lp_sweep_nplc[0], self.sweep_cfg['LP_NPLC'])
        self.lp_sweep_irange.set(self.sweep_cfg['LP_CURRENT_RANGE'])


    def on_sweep_config(self, event=None) -> None:
        if self._valid_sweep_config():
            self.sweep_cfg['RPA_SOURCE'] = self.rpa_sweep_source.get()
            self.sweep_cfg['RPA_METER'] = self.rpa_sweep_meter.get()
            self.sweep_cfg['RPA_VMIN'] = self.rpa_sweep_vrange[0].get()
            self.sweep_cfg['RPA_VMAX'] = self.rpa_sweep_vrange[1].get()
            self.sweep_cfg['RPA_STEPS'] = self.rpa_sweep_steps[0].get()
            self.sweep_cfg['RPA_NPLC'] = self.rpa_sweep_nplc[0].get()
            self.sweep_cfg['RPA_CURRENT_RANGE'] = self.rpa_sweep_irange.get()

            self.sweep_cfg['LP_SOURCE'] = self.lp_sweep_source.get()
            self.sweep_cfg['LP_METER'] = self.lp_sweep_source.get()
            self.sweep_cfg['LP_VMIN'] = self.lp_sweep_vrange[0].get()
            self.sweep_cfg['LP_VMAX'] = self.lp_sweep_vrange[1].get()
            self.sweep_cfg['LP_STEPS'] = self.lp_sweep_steps[0].get()
            self.sweep_cfg['LP_NPLC'] = self.lp_sweep_nplc[0].get()
            self.sweep_cfg['LP_CURRENT_RANGE'] = self.lp_sweep_irange.get()

            self.close_config_windows('all')
            self.sweep_configured = True
            self.sweep_config_lamp.on()
            self.fill_panel_sweep_cfg()
            self.msg('Configured sweep.')


    def _valid_sweep_config(self, event=None) -> bool:
        try:
            rpa_v0 = float(self.rpa_sweep_vrange[0].get())
            rpa_v1 = float(self.rpa_sweep_vrange[1].get())
            rpa_steps = int(self.rpa_sweep_steps[0].get())
            rpa_nplc = float(self.rpa_sweep_nplc[0].get())
            lp_v0 = float(self.lp_sweep_vrange[0].get())
            lp_v1 = float(self.lp_sweep_vrange[1].get())
            lp_steps = int(self.lp_sweep_steps[0].get())
            lp_nplc = float(self.lp_sweep_nplc[0].get())
        except Exception as e:
            self.err(f'Sweep configuration invalid: {e}')
            return False
        if rpa_v1 <= rpa_v0 or lp_v1 <= lp_v0 :
            self.err('Sweep range must be in ascending order.')
            return False
        if any(abs(v) > VMAX for v in (rpa_v0, rpa_v1, lp_v0, lp_v1)):
            self.err(f'Maximum absolute sweep voltage is {VMAX:.4f} V.')
            return False
        if rpa_steps < 2 or lp_steps < 2:
            self.err('Number of sweep steps should be greater than 1.')
            return False
        if self.rpa_sweep_source.get() == self.rpa_sweep_meter.get():
            self.err('RPA Source and Meter cannot be the same.')
            return False
        if rpa_nplc < 0.01 or rpa_nplc > 10.0 or lp_nplc < 0.01 or lp_nplc > 10.0:
            self.err('NPLC should be with 0.01 and 10.')
            return False
        return True


    def on_load_sweep_config(self, event=None) -> None:
        self.on_load_config('sweep', self.load_sweep_config)


    def on_save_sweep_config(self, event=None) -> None:
        if self._valid_sweep_config():
            self.on_save_config(self.save_sweep_config)


    def save_sweep_config(self, event=None) -> None:
        filestem = self.filestem.get()
        if filestem:
            filepath = CONFIG_PATH / f'{filestem}.sweep'
            if filepath.exists():
                self.err('Sweep configuration already exists.')
                return
            
            with open(filepath, 'w') as f:
                f.write(f'RPA_SOURCE: {self.rpa_sweep_source.get()}\n')
                f.write(f'RPA_METER: {self.rpa_sweep_meter.get()}\n')
                f.write(f'RPA_VMIN: {float(self.rpa_sweep_vrange[0].get()):.4f}\n')
                f.write(f'RPA_VMAX: {float(self.rpa_sweep_vrange[1].get()):.4f}\n')
                f.write(f'RPA_STEPS: {int(self.rpa_sweep_steps[0].get())}\n')
                f.write(f'RPA_NPLC: {float(self.rpa_sweep_nplc[0].get()):.2f}\n')
                f.write(f'RPA_CURRENT_RANGE: {self.rpa_sweep_irange.get()}\n\n')

                f.write(f'LP_SOURCE: {self.lp_sweep_source.get()}\n')
                f.write(f'LP_METER: {self.lp_sweep_source.get()}\n')
                f.write(f'LP_VMIN: {float(self.lp_sweep_vrange[0].get()):.4f}\n')
                f.write(f'LP_VMAX: {float(self.lp_sweep_vrange[1].get()):.4f}\n')
                f.write(f'LP_STEPS: {int(self.lp_sweep_steps[0].get())}\n')
                f.write(f'LP_NPLC: {float(self.lp_sweep_nplc[0].get()):.2f}\n')
                f.write(f'LP_CURRENT_RANGE: {self.lp_sweep_irange.get()}\n')

            self.msg(f'Saved {filepath}')

            self.save_window.destroy()
            self.on_sweep_config()
        else:
            self.err('Please enter a label.')


################ RPA CONFIGURATION ################

    def load_rpa_config(self, event=None) -> None:
        self.rpa_cfg = self.load_config('rpa', self.rpa_cfg_name)
        if hasattr(self, 'window'):
            self.fill_rpa_config()

    def open_configure_rpa(self, event=None) -> None:
        self.close_config_windows('all')
        self.window = tk.Toplevel(self.root, bg=CLBG)
        self.window.title('Configure RPA')
        self.window.resizable(False, False)
        self.window.focus_set()

        entries = tk.Frame(self.window, bg=CLBG)
        entries.pack(side='top', padx=(10, 10))

        r = 0
        r = tkobjects.header(entries, r, 'RPA Insturment Configuration')
        self.rpa_shape, r = tkobjects.combo(entries, r, 'Aperture Shape', values=['CIRCLE', 'SQUARE'])
        self.rpa_size, r = tkobjects.entry(entries, r, 'Aperture Diameter / Width', value_type='nnfloat', units='mm')
        self.rpa_screens, r = tkobjects.entry(entries, r, 'Number of Screens', value_type='spint')
        self.rpa_opacity, r = tkobjects.entry(entries, r, 'Screen Opacity', value_type='sp%', units='%')
        self.rpa_particles, r = tkobjects.combo(entries, r, 'Particle Type', values=['IONS', 'ELECTRONS'])

        self.fill_rpa_config()

        options = tk.Frame(self.window, bg=CLBG)
        options.pack(side='bottom', fill='x', padx=20, pady=(40, 20))
        tkobjects.button(options, 'Configure', self.on_rpa_config)
        tkobjects.button(options, 'Load', self.on_load_rpa_config)
        tkobjects.button(options, 'Save', self.on_save_rpa_config)
        tkobjects.button(options, 'Cancel', self.on_cancel_config)
        self.window.bind('<Return>', self.on_rpa_config)


    def fill_rpa_config(self) -> None:
        self.rpa_shape.set(self.rpa_cfg['SHAPE'])
        utils.update(self.rpa_size[0], self.rpa_cfg['SIZE'])
        utils.update(self.rpa_screens[0], self.rpa_cfg['SCREENS'])
        utils.update(self.rpa_opacity[0], self.rpa_cfg['OPACITY'])
        self.rpa_particles.set(self.rpa_cfg['PARTICLES'])


    def on_rpa_config(self, event=None) -> None:
        if self._valid_rpa_config():
            self.rpa_cfg['SHAPE'] = self.rpa_shape.get()
            self.rpa_cfg['SIZE'] = self.rpa_size[0].get()
            self.rpa_cfg['SCREENS'] = self.rpa_screens[0].get()
            self.rpa_cfg['OPACITY'] = self.rpa_opacity[0].get()
            self.rpa_cfg['PARTICLES'] = self.rpa_particles.get()

            self.close_config_windows('all')
            self.rpa_configured = True
            self.rpa_config_lamp.on()
            self.fill_panel_rpa_cfg()
            self.msg('Configured RPA.')


    def _valid_rpa_config(self, event=None) -> bool:
        try:
            s = float(self.rpa_size[0].get())
            n = int(self.rpa_screens[0].get())
            o = int(self.rpa_opacity[0].get())
        except Exception as e:
            self.err(f'RPA configuration invalid: {e}')
            return False
        if not s > 0:
            self.err('Screen size has to be positive.')
            return False
        if not n > 1:
            self.err('Need at least 2 screens.')
            return False
        if not (o > 0 and o <= 100):
            self.err('Screen opacity should be positive and 100 or less.')
            return False
        return True
    

    def on_load_rpa_config(self, event=None) -> None:
        self.on_load_config('rpa', self.load_rpa_config)


    def on_save_rpa_config(self, event=None) -> None:
        if self._valid_rpa_config():
            self.on_save_config(self.save_rpa_config)


    def save_rpa_config(self, event=None) -> None:
        filestem = self.filestem.get()
        if filestem:
            filepath = CONFIG_PATH / f'{filestem}.rpa'
            if filepath.exists():
                self.err('RPA configuration already exists.')
                return
            
            with open(filepath, 'w') as f:
                f.write(f'SHAPE: {self.rpa_shape.get()}\n')
                f.write(f'SIZE: {float(self.rpa_size[0].get()):.4f}\n')
                f.write(f'SCREENS: {int(self.rpa_screens[0].get())}\n')
                f.write(f'OPACITY: {int(self.rpa_opacity[0].get())}\n')
                f.write(f'PARTICLES: {self.rpa_particles.get()}\n')

            self.msg(f'Saved {filepath}')

            self.save_window.destroy()
            self.on_rpa_config()
        else:
            self.err('Please enter a label.')


################ LP CONFIGURATION ################

    def load_lp_config(self, event=None) -> None:
        pass

    def open_configure_lp(self, event=None) -> None:
        self.close_config_windows('all')
        self.err('Not yet implemented.')


################ PLASMA CONFIGURATION ################

    def load_plasma_config(self, event=None) -> None:
        self.plasma_cfg = self.load_config('plasma', self.plasma_cfg_name)
        if hasattr(self, 'window'):
            self.fill_plasma_config()

    def open_configure_plasma(self, event=None) -> None:
        self.close_config_windows('all')
        self.window = tk.Toplevel(self.root, bg=CLBG)
        self.window.title('Configure Plasma')
        self.window.resizable(False, False)
        self.window.focus_set()

        entries = tk.Frame(self.window, bg=CLBG)
        entries.pack(side='top', padx=(10, 10))

        r = 0
        r = tkobjects.header(entries, r, 'Plasma Configuration')
        self.plasma_ArII, r = tkobjects.entry(entries, r, 'Ar+', value_type='nn%', units='%')
        self.plasma_ArIII, r = tkobjects.entry(entries, r, 'Ar++', value_type='nn%', units='%')
        self.plasma_N2II, r = tkobjects.entry(entries, r, 'N2+', value_type='nn%', units='%')
        self.plasma_NII, r = tkobjects.entry(entries, r, 'N+', value_type='nn%', units='%')
        self.plasma_HeII, r = tkobjects.entry(entries, r, 'He+', value_type='nn%', units='%')

        r = tkobjects.header(entries, r + 1, 'Water Related Ions')
        self.plasma_H2OII, r = tkobjects.entry(entries, r, 'H2O+', value_type='nn%', units='%')
        self.plasma_H3OII, r = tkobjects.entry(entries, r, 'H3O+', value_type='nn%', units='%')
        self.plasma_OHII, r = tkobjects.entry(entries, r, 'OH+', value_type='nn%', units='%')
        self.plasma_NOII, r = tkobjects.entry(entries, r, 'NO+', value_type='nn%', units='%')

        r = tkobjects.header(entries, r + 1, 'Background B-Field')
        self.plasma_bmag, r = tkobjects.entry(entries, r, '|B|', value_type='nnefloat', units='T')

        self.fill_plasma_config()

        options = tk.Frame(self.window, bg=CLBG)
        options.pack(side='bottom', fill='x', padx=20, pady=(40, 20))
        tkobjects.button(options, 'Configure', self.on_plasma_config)
        tkobjects.button(options, 'Load', self.on_load_plasma_config)
        tkobjects.button(options, 'Save', self.on_save_plasma_config)
        tkobjects.button(options, 'Cancel', self.on_cancel_config)
        self.window.bind('<Return>', self.on_plasma_config)


    def fill_plasma_config(self) -> None:
        utils.update(self.plasma_ArII[0], self.plasma_cfg['Ar+'])
        utils.update(self.plasma_ArIII[0], self.plasma_cfg['Ar++'])
        utils.update(self.plasma_N2II[0], self.plasma_cfg['N2+'])
        utils.update(self.plasma_NII[0], self.plasma_cfg['N+'])
        utils.update(self.plasma_HeII[0], self.plasma_cfg['He+'])
        utils.update(self.plasma_H2OII[0], self.plasma_cfg['H2O+'])
        utils.update(self.plasma_H3OII[0], self.plasma_cfg['H3O+'])
        utils.update(self.plasma_OHII[0], self.plasma_cfg['OH+'])
        utils.update(self.plasma_NOII[0], self.plasma_cfg['NO+'])
        utils.update(self.plasma_bmag[0], self.plasma_cfg['BMAG'])


    def on_plasma_config(self, event=None) -> None:
        if self._valid_plasma_config():
            self.plasma_cfg['Ar+'] = self.plasma_ArII[0].get()
            self.plasma_cfg['Ar++'] = self.plasma_ArIII[0].get()
            self.plasma_cfg['N2+'] = self.plasma_N2II[0].get()
            self.plasma_cfg['N+'] = self.plasma_NII[0].get()
            self.plasma_cfg['He+'] = self.plasma_HeII[0].get()
            self.plasma_cfg['H2O+'] = self.plasma_H2OII[0].get()
            self.plasma_cfg['H3O+'] = self.plasma_H3OII[0].get()
            self.plasma_cfg['OH+'] = self.plasma_OHII[0].get()
            self.plasma_cfg['NO+'] = self.plasma_NOII[0].get()
            self.plasma_cfg['BMAG'] = self.plasma_bmag[0].get()

            self.mass = utils.weighted_mass(self.plasma_cfg)
            self.charge = utils.weighted_charge(self.plasma_cfg)
            self.bmag = float(self.plasma_cfg['BMAG'])

            self.close_config_windows('all')
            self.plasma_configured = True
            self.plasma_config_lamp.on()
            self.fill_panel_plasma_cfg()
            self.msg('Configured plasma.')


    def _valid_plasma_config(self, event=None) -> bool:
        try:
            s0 = int(self.plasma_ArII[0].get())
            s1 = int(self.plasma_ArIII[0].get())
            s2 = int(self.plasma_N2II[0].get())
            s3 = int(self.plasma_NII[0].get())
            s4 = int(self.plasma_HeII[0].get())
            s5 = int(self.plasma_H2OII[0].get())
            s6 = int(self.plasma_H3OII[0].get())
            s7 = int(self.plasma_OHII[0].get())
            s8 = int(self.plasma_NOII[0].get())
            b = float(self.plasma_bmag[0].get())
        except Exception as e:
            self.err(f'Plasma configuration invalid: {e}')
            return False
        total = sum((s0, s1, s2, s3, s4, s5, s6, s7, s8))
        if total != 100:
            self.err(f'Ionic species do not add to 100%. Total = {total}%.')
            return False
        if b > 1:
            self.err('Magnetic field strength should not exceed 1 Tesla.')
            return False
        return True
    

    def on_load_plasma_config(self, event=None) -> None:
        self.on_load_config('plasma', self.load_plasma_config)


    def on_save_plasma_config(self, event=None) -> None:
        if self._valid_plasma_config():
            self.on_save_config(self.save_plasma_config)


    def save_plasma_config(self, event=None) -> None:
        filestem = self.filestem.get()
        if filestem:
            filepath = CONFIG_PATH / f'{filestem}.plasma'
            if filepath.exists():
                self.err('RPA configuration already exists.')
                return
            
            with open(filepath, 'w') as f:
                f.write(f'Ar+: {int(self.plasma_ArII[0].get())}\n')
                f.write(f'Ar++: {int(self.plasma_ArIII[0].get())}\n')
                f.write(f'N2+: {int(self.plasma_N2II[0].get())}\n')
                f.write(f'N+: {int(self.plasma_NII[0].get())}\n')
                f.write(f'He+: {int(self.plasma_HeII[0].get())}\n')
                f.write(f'H2O+: {int(self.plasma_H2OII[0].get())}\n')
                f.write(f'H3O+: {int(self.plasma_H3OII[0].get())}\n')
                f.write(f'OH+: {int(self.plasma_OHII[0].get())}\n')
                f.write(f'NO+: {int(self.plasma_NOII[0].get())}\n')
                f.write(f'BMAG: {float(self.plasma_bmag[0].get())}\n')

            self.msg(f'Saved {filepath}')

            self.save_window.destroy()
            self.on_plasma_config()
        else:
            self.err('Please enter a label.')


################ SWEEP FUNCTIONS ################

    def _sweep_progress(self, sweep_id: int, max_id: int) -> None:
        bar = utils.bar('Sweeping', sweep_id, max_id)
        self.status.configure(fg='#0F0')
        self.root.after(0, self.msg, bar, '\r')
    

    def _run_sweep_thread(self, is_rpa: bool) -> None:
        try:
            iv_curve = sweep.fake_sweep(self.sweep_cfg, is_rpa=is_rpa, on_step=self._sweep_progress)
            self.root.after(0, self._finish_sweep, iv_curve, is_rpa)
        except Exception as e:
            self.root.after(0, self.err, f'Sweep failed: {e}')


    def _finish_sweep(self, iv_curve, is_rpa: bool) -> None:
        self.iv_curve = iv_curve
        self.status.configure(fg=CLFG)
        print()

        pfx = 'rpa_' if is_rpa else 'lp_'
        folder_stem = f'{pfx}{self.sweep_label[0].get()}'
        filepath = DATA_PATH / f'{folder_stem}_000'
        if filepath.is_dir():
            ids = [int(str(f).split('_')[-1]) for f in DATA_PATH.glob(f'{folder_stem}_*')]
            new_id = max(ids) + 1
            filepath = DATA_PATH / f'{folder_stem}_{new_id:03d}'
        filepath.mkdir()

        dataproc.save_iv_curve(filepath, self.sweep_cfg, self.iv_curve, is_rpa=is_rpa)

        self.panel_sweep_folders['values'] = self.get_sweep_folders()
        self.panel_sweep_folders.set(filepath.name)

        self.on_load_sweep()


    # def on_sweep(self, event=None, is_rpa: bool = True) -> None:
    #     if self.sweep_configured:
    #         if self.sweep_label[0].get():
    #             self.iv_curve = sweep.sweep(self.sweep_cfg, is_rpa=is_rpa, on_step=lambda sid: self.msg(f'Sweep id = {sid}'))
    #             # self.iv_curve = sweep.fake_sweep(self.sweep_cfg, is_rpa=is_rpa)

    #             pfx = 'rpa_' if is_rpa else 'lp_'
    #             folder_stem = f'{pfx}{self.sweep_label[0].get()}'
    #             filepath = DATA_PATH / f'{folder_stem}_000'
    #             if filepath.is_dir():
    #                 ids = [int(str(f).split('_')[-1]) for f in DATA_PATH.glob(f'{folder_stem}_*')]
    #                 id = max(ids) + 1
    #                 filepath = DATA_PATH / f'{folder_stem}_{id:03d}'
    #             filepath.mkdir()
    #             dataproc.save_iv_curve(filepath, self.sweep_cfg, self.iv_curve, is_rpa=is_rpa)

    #             self.panel_sweep_folders['values'] = self.get_sweep_folders()
    #             self.panel_sweep_folders.set(filepath.name)

    #             self.on_load_sweep()
    #         else:
    #             self.err('Please enter a sweep label.')
    #     else:
    #         self.err('Sweep not configured.')

    def on_sweep(self, event=None, is_rpa: bool = True) -> None:
        if not self.sweep_configured:
            self.err('Sweep not configured.')
            return

        if not self.sweep_label[0].get():
            self.err('Please enter a sweep label.')
            return

        threading.Thread(target=self._run_sweep_thread, args=(is_rpa,), daemon=True).start()


    def on_sweep_rpa(self, event=None) -> None:
        self.on_sweep(is_rpa=True)


    def on_sweep_lp(self, event=None) -> None:
        self.on_sweep(is_rpa=False)


    def on_sweep_all(self, event=None) -> None:
        self.on_sweep(is_rpa=False)
        self.on_sweep(is_rpa=True)


    def on_load_sweep(self, event=None) -> None:
        if not self.mass > 0:
            self.err('Please confifure plasma first.')
            return
        filepath = DATA_PATH / self.panel_sweep_folders.get()
        self.msg(f'Loading {filepath}...')
        self.iv_curve = dataproc.load_iv_curve(filepath)
        self.saturation_current = dataproc.saturation_current(self.iv_curve)

        if np.any(np.isnan(self.iv_curve)):
            self.err('Invalid IV curve.')
        self.didv_curve = utils.nd(self.iv_curve)
        try:
            self.didv_curve, self.popt, self.perr, _ = dataproc.fit_linearly_modulated_gaussian(self.didv_curve, self.mass)
            good_fit = True
        except Exception as e:
            good_fit = False
            self.err(f'Curve fitting failed: {e}')
        
        if good_fit:
            self.fluid = plasma.compute_plasma_fluid_params(self.popt, self.perr, self.mass, self.charge, self.effarea, self.saturation_current)
            self.funds = plasma.compute_fundemental_params(self.fluid, m=self.mass, b=self.bmag)
            self.fill_panel_fluid_params()
            dataproc.save_params(filepath, self.fluid, self.funds)

        self.plot(plot_velocity=self.plot_velocity.get())
        sfx = '_v' if self.plot_velocity.get() else ''
        self.save_plot(filepath, sfx)
            

################ PLOT FUNCTIONS ################

    def plot(self, plot_velocity: bool = False):
        if plot_velocity and not self.mass > 0:
            self.plot_velocity.set(False)
            self.err('Plotting against velocity requires the plasma to be configured.')
            return

        labelx = 'Source Voltage (km/s)' if plot_velocity else 'Source Voltage (V)'

        title = f'{self.panel_sweep_folders.get()}'
        labely = 'Meter Current (nA)'
        labelA = 'Meter Current'
        labelB = 'Source Current'
        dataproc.plot_data(self.ax0, self.canvas, self.iv_curve, (title, labelx, labely, labelA, labelB)
                           , plot_column_2=self.plot_source_current.get(), plot_velocity=plot_velocity
                           , mass=self.mass, imax=self.saturation_current)
        
        title = f'U = {self.panel_beam_velocity[0].get()} km/s  —  '
        title += f'E = {self.panel_beam_energy[0].get()} eV  —  '
        title += f'N = 10^({self.panel_beam_density[0].get()}) m\u207B\u00B3  —  '
        title += f'T = {self.panel_beam_temperature[0].get()} eV'     
        labely = 'Current Derivative (nA / V)'
        labelA = 'Derivative Data'
        labelB = 'Derivative Fit'
        dataproc.plot_data(self.ax1, self.canvas, self.didv_curve, (title, labelx, labely, labelA, labelB)
                           , plot_column_2=True, plot_velocity=plot_velocity, mass=self.mass)
    
    def save_plot(self, filepath: Path, sfx: str) -> None:
        self.fig.savefig(filepath / f'iv_curve{sfx}.png')


################ OTHER ################

    def _configure_window_geometry(self) -> None:
        monitors = get_monitors()
        monitor = monitors[0]
        max_width = 0
        for m in monitors:
            if m.width > max_width:
                monitor = m
                max_width = m.width
        self.width = round(0.7 * monitor.width)
        self.height = round(0.7 * monitor.height)
        self.x = monitor.x + (monitor.width - self.width) // 2
        self.y = monitor.y + (monitor.height - self.height) // 2


    def _toggle_fullscreen(self) -> None:
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
            self.root.state('normal')
        else:
            self.root.attributes('-fullscreen', True)


    def _configure_settings(self) -> None:
        self.sweep_configured = False
        self.rpa_configured = False
        self.plasma_configured = False
        self.global_cfg_name = 'default'
        self.mass = 0.0
        self.charge = 0.0
        self.bmag = 0.0
        self.effarea = 0.0
        self.ftsz = FTSZ
        self.old_ftsz = FTSZ
        with open(CONFIG_PATH / f'{self.global_cfg_name}.profile', 'r') as f:
            lines = f.readlines()
        for line in lines:
            entry = line.strip('\n').split(': ')
            if entry[0] == 'SWEEP':
                self.sweep_cfg_name = entry[1]
            elif entry[0] == 'RPA':
                self.rpa_cfg_name = entry[1]
            elif entry[0] == 'LP':
                self.lp_cfg_name = entry[1]
            elif entry[0] == 'PLASMA':
                self.plasma_cfg_name = entry[1]
    

    def on_config_all(self) -> None:
        self.fill_panel_sweep_cfg()
        self.fill_panel_rpa_cfg()
        self.fill_panel_plasma_cfg()

        self.mass = utils.weighted_mass(self.plasma_cfg)
        self.charge = utils.weighted_charge(self.plasma_cfg)
        self.bmag = float(self.plasma_cfg['BMAG'])

        self.sweep_configured = True
        self.rpa_configured = True
        self.plasma_configured = True
        self.sweep_config_lamp.on()
        self.rpa_config_lamp.on()
        self.plasma_config_lamp.on()

        self.msg('Configured all.')


    def assured(self, event=None) -> bool:
        self.close_config_windows()
        self.sure_window = tk.Toplevel(self.root, bg='#C00', padx=10, pady=10)
        self.sure_window.title('')
        self.sure_window.resizable(False, False)
        self.sure_window.focus_set()
        self.sure_window.grab_set()
        self.sure_result = False

        self.root.bell()
        tkobjects.button(self.sure_window, 'Yes', lambda: self._sure_response(True) )
        tkobjects.button(self.sure_window, 'No', lambda: self._sure_response(False))
        tk.Label(self.sure_window, text='Are you sure?'
                 , bg='#C00', fg=CLFG, font=('TkDefaultFont', round(1.2 * FTSZ), 'bold')
                 ).pack(side='left', padx=10)

        self.root.wait_window(self.sure_window)
        return self.sure_result


    def _sure_response(self, result):
        self.sure_result = result
        self.sure_window.destroy()


    def msg(self, text: str, end='\n', color=CLFG) -> None:
        print(text, end=end)
        utils.update(self.status, text)


    def err(self, text: str) -> None:
        self.root.bell()
        text = f' *** [ERROR] {text} *** '
        self.msg(text)


    def on_f11(self, event=None) -> None:
        self._toggle_fullscreen()


    def on_esc(self, event=None) -> None:
        self.root.attributes('-fullscreen', False)
        self.root.state('normal')


    def on_change_fontsize(self, event=None) -> None:
        self.close_config_windows()
        self.load_window = tk.Toplevel(self.root, bg=CLBG, padx=10, pady=10)
        self.load_window.title('')
        self.load_window.resizable(False, False)
        self.load_window.focus_set()

        fontsizes = [10, 11, 12, 13, 14, 15, 16]
        self.fontsize_var = tk.StringVar()
        self.load_fontsize = tkobjects.load(self.load_window, 'Set Fontsize', fontsizes, self.change_fontsize, self.fontsize_var)
        self.load_fontsize.set(self.ftsz)
        self.load_window.bind('<Return>', self.change_fontsize)


    def change_fontsize(self, event=None) -> None:
        self.old_ftsz = self.ftsz
        self.ftsz = int(self.load_fontsize.get())
        self.font.configure(size=self.ftsz)
        self.root.option_add('*font', self.font)
        self.close_config_windows()
        plt.rcParams.update({
            'font.size': self.ftsz,
            'axes.titlesize': self.ftsz,
            'axes.labelsize': self.ftsz,
            'xtick.labelsize': self.ftsz,
            'ytick.labelsize': self.ftsz,
            'legend.fontsize': self.ftsz,
        })

        f =  (self.ftsz / self.old_ftsz)**0.8
        new_sweep_lamp_width = round(float(self.sweep_config_lamp['width']) * f)
        new_rpa_lamp_width = round(float(self.rpa_config_lamp['width']) * f)
        new_lp_lamp_width = round(float(self.lp_config_lamp['width']) * f)
        new_plasma_lamp_width = round(float(self.plasma_config_lamp['width']) * f)

        print(f'Font = {self.old_ftsz} -> {self.ftsz}\t Width = {self.sweep_config_lamp["width"]} -> {new_sweep_lamp_width}')

        self.sweep_config_lamp.configure(width=new_sweep_lamp_width)
        self.rpa_config_lamp.configure(width=new_rpa_lamp_width)
        self.lp_config_lamp.configure(width=new_lp_lamp_width)
        self.plasma_config_lamp.configure(width=new_plasma_lamp_width)


    def run(self):
        self.root.mainloop()


    def on_exit(self):
        plt.close('all')
        self.root.destroy()


    @staticmethod

    def get_sweep_folders() -> list[str]:
        return [p.name for p in Path(DATA_PATH).iterdir() if p.is_dir()]


if __name__ == '__main__':
    app = gui()
    app.run()