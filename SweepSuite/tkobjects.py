import tkinter as tk
from tkinter import ttk
import re
from collections.abc import Callable
import tkinter.font as tkfont
from typing import Literal

CLBG = '#222'
CLFG = '#EEE'
FTSZ = 12

_REGEXS = {
    'all': r'^.*$',
    'float': r'^-?\d*\.?\d*$',
    'nnfloat': r'\d*\.?\d*$',
    'efloat': r'^-?\d*\.?\d*([eE][+-]?\d*)?$',
    'nnefloat': r'^\d*\.?\d*([eE][+-]?\d*)?$',
    'int': r'^-?\d*$',
    'nnint': r'^\d*$',
    'spint': r'^([1-9]\d*)?$',
    'alnum': r'^[a-zA-Z0-9_-]*$',
    'nn%': r'^(?:100|[1-9]?\d)?$',
    'sp%': r'^(?:100|[1-9]\d?)?$',
}


def _validate(value, value_type: str = 'all'):
    return bool(re.compile(_REGEXS[value_type]).fullmatch(value))


def entry(
        frame,
        row: int,
        label: str,
        units: str = '',
        double_entry: bool = False,
        value_type: str = 'all',
        readonly: bool = False,
        ) -> tuple[list[tk.Entry], int]:
    
    vcmd = (frame.register(lambda v: _validate(v, value_type=value_type)), "%P")

    tk.Label(frame, text=label, anchor='e', bg=CLBG, fg=CLFG).grid(column=0, row=row, sticky='ew', padx=10)
    tk.Label(frame, text=units, anchor='w', bg=CLBG, fg=CLFG).grid(column=3, row=row, sticky='ew', padx=10)

    state = 'readonly' if readonly else 'normal'
    fg = CLFG if readonly else CLBG
    num_entries = 2 if double_entry else 1
    values = []
    for c in range(num_entries):
        value = tk.Entry(frame, fg=fg, bg=CLFG, readonlybackground='#333', validate='key', validatecommand=vcmd, state=state)
        value.grid(column=c+1, row=row, columnspan=3-num_entries, padx=1, sticky='ew')
        values.append(value)
    return values, row + 1


def combo(
        frame,
        row: int,
        label: str,
        values: list[str],
        units: str = '',
        ) -> tuple[ttk.Combobox, int]:
    
    tk.Label(frame, text=label, anchor='e', bg=CLBG, fg=CLFG).grid(column=0, row=row, sticky='ew', padx=10)
    value = ttk.Combobox(frame, values=values, state='readonly')
    value.set(values[0])
    value.grid(column=1, row=row, columnspan=2, padx=1, sticky='ew')
    tk.Label(frame, text=units, anchor='e', bg=CLBG, fg=CLFG).grid(column=3, row=row, sticky='ew', padx=10)


    return value, row + 1


def button(
        frame,
        text: str,
        command: Callable,
        side: Literal['left', 'right', 'bottom', 'top'] = 'right',
        padx: int = 1,
        ) -> None:
    
    tk.Button(frame, text=text, command=command, bg='#111', fg=CLFG).pack(side=side, padx=padx)


def check(
        frame, 
        text: str,
        variable: tk.BooleanVar,
        command: Callable,
        side: Literal['left', 'right', 'bottom', 'top'] = 'left',
        ) -> tk.Checkbutton:
    
    check = tk.Checkbutton(frame, text=text, variable=variable, command=command, bg=CLBG, fg=CLFG, selectcolor=CLBG)
    check.pack(side=side)
    return check


def save(
        frame,
        label: str,
        command: Callable,
        value_type: str = '',
        ) -> tk.Entry:
    
    vcmd = (frame.register(lambda v: _validate(v, value_type=value_type)), "%P")
    value = tk.Entry(frame, bg=CLFG, validate='key', validatecommand=vcmd, width=30)
    value.pack(side='left', padx=10)
    tk.Button(frame, text=label, command=command).pack(side='left')

    return value


def load(
        frame,
        label: str,
        values: list,
        command: Callable,
        strvar: tk.StringVar,
        ) -> ttk.Combobox:
    
    vals = [str(f) for f in values]
    value = ttk.Combobox(frame, values=vals, textvariable=strvar, width=30)
    value.pack(side='left', padx=10)
    value.insert(0, vals[0])
    tk.Button(frame, text=label, command=command).pack(side='left')

    return value


def header(
        frame,
        row: int,
        text: str,
        cs: int = 2,
        ) -> int:
    
    label = tk.Label(frame, text=text, bg=CLBG, fg=CLFG, font=('TkDefaultFont', round(1.2 * FTSZ), 'bold'))
    label.grid(row=row, column=1, columnspan=cs, sticky='ew', pady=(20, 10))

    return row + 1


def vspace(
        frame,
        row: int,
        height: int = 10,
        cs: int = 4,
        ) -> int:
    
    tk.Frame(frame, height=height, bg=CLBG).grid(row=row, column=0, columnspan=cs, sticky='nesw')
    return row + 1


class Lamp(tk.Canvas):
    def __init__(self, master, label: str = '', size=30, fg=CLFG, **kwargs):

        self.font = tkfont.nametofont("TkDefaultFont")
        self.font.configure(size=FTSZ)
        text_width = self.font.measure(label)
        super().__init__(
            master,
            width=size + text_width + FTSZ / 2,
            height=size,
            highlightthickness=0,
            bd=0,
            bg=CLBG,
            **kwargs
        )

        self.fg = fg
        self.size = size
        self.label = label
        self.on_color = ["#0F0", "#080"]
        self.off_color = ["#F00", "#800"]
        self.idle_color = ["#FB0", "#860"]
        self._state = 'off'

        pad = size * 0.1
        edge = size * 0.1
        label_pad = size * 0.1

        self._lamp_edge = self.create_oval(
            pad, pad, size - pad, size - pad,
            fill = self.off_color[1],
            outline=''
        )

        self._lamp = self.create_oval(
            pad + edge, pad + edge, size - edge - pad, size - edge - pad,
            fill = self.off_color[0],
            outline=''
        )

        self._label = self.create_text(
            size + label_pad,
            size / 2,
            text = self.label,
            anchor='w',
            fill=self.fg
            )

    def turn(self, state: str):
        self._state = state
        if state == 'off':
            self.itemconfig(self._lamp, fill=self.off_color[0])
            self.itemconfig(self._lamp_edge, fill=self.off_color[1])
        elif state == 'idle':
            self.itemconfig(self._lamp, fill=self.idle_color[0])
            self.itemconfig(self._lamp_edge, fill=self.idle_color[1])
        elif state == 'on':
            self.itemconfig(self._lamp, fill=self.on_color[0])
            self.itemconfig(self._lamp_edge, fill=self.on_color[1])

    def off(self):
        self.turn('off')

    def idle(self):
        self.turn('idle')

    def on(self):
        self.turn('on')
