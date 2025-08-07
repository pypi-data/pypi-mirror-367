#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plotting utilities and data visualization functions.

Provides functions for creating plots with matplotlib, managing plot defaults,
and handling data visualization with customizable parameters.
"""

import re
import copy
from typing import Any, Callable, Optional

import numpy as np
from matplotlib import pyplot as plt

from ..function_evaluation import process_args
from ..utils import repeating

global_plot_values: dict[str, Any] = {}


def setup_plotting(plot_defaults: dict[str, Any]) -> None:
    """
    Initialize plotting with the specified default parameters.

    Args:
        plot_defaults: Dictionary of default plotting parameters that will be used
                       as defaults for all subsequent data_plot calls
    """
    global global_plot_values

    global_plot_values.clear()
    global_plot_values.update(plot_defaults)


def data_plot(**kw_in: Any) -> '_PlotChainer':
    """
    Automatic data plotting.

    Args:
        **kw_in: Keyword arguments for plotting configuration

    Returns:
        PlotChainer object for chaining additional plots
    """
    kw = process_args(_data_plot_arg_declaration, [kw_in, global_plot_values])
    kw['style_list'] = repeating(kw['style_list'])
    chain_list = []

    kw['fig'] = _make_figure(kw)
    nr = 0
    for i, arr_slice in enumerate(
        kw['data'].slice_iterator(
            kw['slice_its'], fixed_axes=kw['fixed_axes'], synced_axes={}
        )
    ):
        for y_nr, y_data in enumerate(kw['y_data_list']):
            it_kw = {'arr_slice': arr_slice, 'y_nr': y_nr, 'nr': nr}
            x_arr = kw['x_data'][arr_slice]
            y_arr = y_data[arr_slice]
            legend = _get_legend(kw, it_kw)
            plt_kw_args = _get_plt_kw_args(kw, it_kw)

            if kw['style_list'][nr] is not None:
                handles = kw['plt_func'](
                    x_arr, y_arr, kw['style_list'][nr], **plt_kw_args
                )
            else:
                handles = kw['plt_func'](x_arr, y_arr, **plt_kw_args)

            if legend is not None:
                kw['handle_list'].append(handles[0])
                kw['legend_list'].append(legend)
            nr += 1

    plt.xlim(kw['xlim'])
    plt.ylim(kw['ylim'])
    plt.xlabel(kw['xlabel'])
    plt.ylabel(kw['ylabel'])
    plt.title(kw['title'])

    kw_out = kw_in
    if kw['chain']:
        plt.ioff()
        kw_out['handle_list'] = kw['handle_list']
        kw_out['legend_list'] = kw['legend_list']
        del kw_out['chain']
        kw_out['fig'] = kw['fig']
    else:
        legend_list = autoalign_legends(kw['legend_list'])
        plt.legend(kw['handle_list'], legend_list)
        kw['callback'](kw)

    chain_list.append(kw_out)
    return _PlotChainer(chain_list)


def data_multiplot(**kw_in: Any) -> '_PlotChainer':
    """
    Automatic plotting with one figure per array slice.

    Args:
        **kw_in: Keyword arguments for plotting configuration

    Returns:
        PlotChainer object for chaining additional plots
    """
    kw = process_args(_data_multiplot_arg_declaration, [kw_in, global_plot_values])
    chain_list = []

    for i, arr_slice in enumerate(
        kw['data'].slice_iterator(
            kw['slice_its'], fixed_axes=kw['fixed_axes'], synced_axes={}
        )
    ):
        slice_kw = {'arr_slice': arr_slice}
        full_title = _get_title(kw, slice_kw)
        title = re.sub(r' for .*', '', full_title)
        kw = process_args(
            _data_multiplot_arg_declaration,
            [{'title': title}, kw_in, global_plot_values],
        )
        kw['style_list'] = repeating(kw['style_list'])

        kw['fig'] = _make_figure(kw)
        nr = 0
        for y_nr, y_data in enumerate(kw['y_data_list']):
            it_kw = {'arr_slice': arr_slice, 'y_nr': y_nr, 'nr': nr}
            x_arr = kw['x_data'][arr_slice]
            y_arr = y_data[arr_slice]
            legend = _get_legend(kw, it_kw)
            plt_kw_args = _get_plt_kw_args(kw, it_kw)

            if kw['style_list'][nr] is not None:
                handles = kw['plt_func'](
                    x_arr, y_arr, kw['style_list'][nr], **plt_kw_args
                )
            else:
                handles = kw['plt_func'](x_arr, y_arr, **plt_kw_args)

            if legend is not None:
                kw['handle_list'].append(handles[0])
                kw['legend_list'].append(legend)
            nr += 1

        kw['title'] = full_title
        plt.xlim(kw['xlim'])
        plt.ylim(kw['ylim'])
        plt.xlabel(kw['xlabel'])
        plt.ylabel(kw['ylabel'])
        plt.title(kw['title'])

        kw_out = kw_in
        if kw['chain']:
            plt.ioff()
            kw_out['handle_list'] = kw['handle_list']
            kw_out['legend_list'] = kw['legend_list']
            kw_out['fig'] = kw['fig']
            del kw_out['chain']
        else:
            legend_list = autoalign_legends(kw['legend_list'])
            plt.legend(kw['handle_list'], legend_list)
            kw['callback'](kw)

        chain_list.append(kw_out)
    return _PlotChainer(chain_list)


def latex_mb(string: str, length: float) -> str:
    """
    Get latex makebox string of certain length.

    Args:
        string: String content for the makebox
        length: Length in cm for the makebox

    Returns:
        LaTeX makebox command string
    """
    return rf'\makebox[{length}cm][l]{{{string}}}'


def autoalign_legends(legends: list[Optional[str]]) -> list[Optional[str]]:
    """
    Autoalign legends at &.

    Args:
        legends: List of legend strings that may contain & alignment markers

    Returns:
        List of aligned legend strings using LaTeX makebox commands
    """
    has_at = False
    for legend in legends:
        if legend is not None and re.search(r'(?<!\\)&', legend):
            has_at = True
    if not has_at:
        return legends

    aligned_legends = [''] * len(legends)
    legend_grid = [
        [s.strip() for s in re.split(r'(?<!\\)&', legend)]
        if legend is not None
        else None
        for legend in legends
    ]
    max_nr_slots = max([len(legend_line) for legend_line in legend_grid])
    slot_lengths = [None] * max_nr_slots

    for slot_nr in range(max_nr_slots):
        max_legend_cm = 0
        for legend_line in legend_grid:
            if legend_line is not None and slot_nr <= len(legend_line) - 1:
                slot_cm = _get_legend_cm(legend_line[slot_nr])
                max_legend_cm = max(max_legend_cm, slot_cm)
        slot_lengths[slot_nr] = max_legend_cm

    for line_nr, legend_line in enumerate(legend_grid):
        if legend_line is None:
            aligned_legends[line_nr] = None
        else:
            for slot_nr, legend_entry in enumerate(legend_line):
                aligned_legends[line_nr] += (
                    latex_mb(legend_entry, slot_lengths[slot_nr]) + ' '
                )
            aligned_legends[line_nr] = aligned_legends[line_nr][:-1]
    return aligned_legends


def _default_xlabel(kw: dict[str, Any]) -> Optional[str]:
    """
    Data plot xlabel default value.

    Args:
        kw: Keyword arguments dictionary

    Returns:
        Default xlabel extracted from title, or None
    """
    xlabel = None
    if kw['title'] is not None:
        title_list = kw['title'].split('vs.')
        if len(title_list) >= 2:
            xlabel = title_list[1].strip()
    return xlabel


def _default_y_data_label_list(kw: dict[str, Any]) -> list[str]:
    """
    Data plot y_data_label_list default value.

    Args:
        kw: Keyword arguments dictionary

    Returns:
        Default y-data labels extracted from title
    """
    y_data_label_list = repeating([''])
    if kw['title'] is not None:
        title_list = kw['title'].split('vs.')
        if len(title_list) >= 2:
            try_y_data_label_list = [s.strip() for s in title_list[0].split(r'\&')]
        else:
            try_y_data_label_list = [s.strip() for s in kw['title'].split(r'\&')]
        if len(try_y_data_label_list) > 1:
            y_data_label_list = try_y_data_label_list
    return y_data_label_list


def _default_legend_f(kw: dict[str, Any]) -> Callable[[], str]:
    """
    Data plot legend_f default value.

    Args:
        kw: Keyword arguments dictionary

    Returns:
        Default legend function that returns empty string
    """
    kw['legend_data_list'] = []
    legend_f = lambda: ''
    return legend_f


def _make_figure(kw: dict[str, Any]) -> plt.Figure:
    """
    Make figure object for data plot.

    Args:
        kw: Keyword arguments dictionary

    Returns:
        Matplotlib figure object
    """
    if kw['fig'] is None:
        fig = plt.figure()
    else:
        fig = plt.figure(kw['fig'].number)
    return fig


def _get_legend_cm(string: str) -> float:
    """
    Get length of legend string in cm.

    Args:
        string: Legend string to measure

    Returns:
        Length of the string in centimeters when rendered
    """
    if string == '':
        return 0

    dpi_chars_from_pixel_width = lambda pixel_width: 0.15 * pixel_width - 7.48
    dpi_cm_from_dpi_chars = lambda chars: chars / 5.92
    cm_from_dpi_cm = lambda dpi_cm: dpi_cm - 0.02951724 * (
        plt.rcParams['figure.dpi'] - 100
    )
    plt.figure()
    plt.plot([0], [0], label=string)
    leg = plt.legend()
    points = leg.get_tightbbox().get_points()
    pixel_width = points[1, 0] - points[0, 0]
    plt.close()
    return cm_from_dpi_cm(
        dpi_cm_from_dpi_chars(dpi_chars_from_pixel_width(pixel_width))
    )


def _get_legend(kw: dict[str, Any], it_kw: dict[str, Any]) -> Optional[str]:
    """
    Data plot get legend.

    Args:
        kw: Keyword arguments dictionary
        it_kw: Iteration-specific keyword arguments

    Returns:
        Legend string or None if no legend should be shown
    """
    legend_p1 = kw['y_data_label_list'][it_kw['y_nr']]
    legend_arg_list = [
        np.mean(legend_data[it_kw['arr_slice']])
        for legend_data in kw['legend_data_list']
    ]
    legend_p2 = kw['legend_f'](*legend_arg_list)

    if legend_p1 is None or legend_p2 is None:
        legend = None
    elif legend_p1 == '':
        legend = legend_p2
    elif legend_p2 == '':
        legend = legend_p1
    else:
        legend = legend_p1 + '& for ' + legend_p2
    return legend


def _get_plt_kw_args(kw: dict[str, Any], it_kw: dict[str, Any]) -> dict[str, Any]:
    """
    Data plot get keyword args for plot function.

    Args:
        kw: Keyword arguments dictionary
        it_kw: Iteration-specific keyword arguments

    Returns:
        Dictionary of keyword arguments for matplotlib plot function
    """
    plt_kw_args = {}
    for arg_name in ['zorder_list', 'linewidth_list']:
        if kw[arg_name][it_kw['y_nr']] is not None:
            plt_kw_args[re.sub('_list', '', arg_name)] = kw[arg_name][it_kw['nr']]
    return plt_kw_args


# Data plot arg declaration.
_data_plot_arg_declaration: dict[str, tuple[bool, Callable[[dict[str, Any]], Any]]] = {
    'data': (True, lambda kw: None),
    'x_data': (True, lambda kw: None),
    'slice_its': (True, lambda kw: None),
    'plt_func': (False, lambda kw: plt.plot),
    'title': (False, lambda kw: None),
    'y_data_list': (False, lambda kw: []),
    'fixed_axes': (False, lambda kw: {}),
    'style_list': (False, lambda kw: repeating([None])),
    'legend_data_list': (False, lambda kw: []),
    'legend_f': (False, _default_legend_f),
    'y_data_label_list': (False, _default_y_data_label_list),
    'xlim': (False, lambda kw: None),
    'ylim': (False, lambda kw: None),
    'xlabel': (False, _default_xlabel),
    'ylabel': (False, lambda kw: None),
    'zorder_list': (False, lambda kw: repeating([None])),
    'linewidth_list': (False, lambda kw: repeating([None])),
    'callback': (False, lambda kw: lambda kw: None),
    'fig': (False, lambda kw: None),
    'chain': (False, lambda kw: False),
    'handle_list': (False, lambda kw: []),
    'legend_list': (False, lambda kw: []),
}


def _default_title_f(kw: dict[str, Any]) -> Callable[[], Optional[str]]:
    """
    Data multiplot default title_f.

    Args:
        kw: Keyword arguments dictionary

    Returns:
        Default title function that returns None
    """
    kw['title_data_list'] = []
    title_f = lambda: None
    return title_f


def _get_title(kw: dict[str, Any], slice_kw: dict[str, Any]) -> Optional[str]:
    """
    Data multiplot get title.

    Args:
        kw: Keyword arguments dictionary
        slice_kw: Slice-specific keyword arguments

    Returns:
        Title string for the current slice
    """
    title_arg_list = [
        np.mean(title_data[slice_kw['arr_slice']])
        for title_data in kw['title_data_list']
    ]
    title = kw['title_f'](*title_arg_list)
    return title


# Data multiplot arg declaration.
_data_multiplot_arg_declaration: dict[
    str, tuple[bool, Callable[[dict[str, Any]], Any]]
] = copy.deepcopy(_data_plot_arg_declaration)
_data_multiplot_arg_declaration = {
    **_data_multiplot_arg_declaration,
    **{
        'title_data_list': (False, lambda kw: []),
        'title_f': (False, _default_title_f),
    },
}


class _PlotChainer:
    """
    Class for chaining plots.

    Allows multiple plots to be chained together and executed with shared parameters.
    """

    def __init__(self, kw_prev_list: list[dict[str, Any]]) -> None:
        """
        Initialize plot chainer.

        Args:
            kw_prev_list: List of previous keyword argument dictionaries
        """
        self.kw_prev_list = kw_prev_list
        self.callback_f_queue: list[Callable] = []
        self.callback_arg_queue: list[dict[str, Any]] = []

    def data_plot(self, **kw_new: Any) -> None:
        """
        Add a data plot to the chain.

        Args:
            **kw_new: New keyword arguments for the plot
        """
        for kw_prev in self.kw_prev_list:
            kw_new_t = process_args(
                _data_plot_arg_declaration, [kw_new, kw_prev, global_plot_values]
            )
            self.callback_f_queue.append(kw_new_t['callback'])
            kw_new_t['callback'] = self.delayed_callback
            data_plot(**kw_new_t)
        self.callback()

    def delayed_callback(self, kw: dict[str, Any]) -> None:
        """
        Store callback arguments for later execution.

        Args:
            kw: Keyword arguments to store
        """
        self.callback_arg_queue.append(kw)

    def callback(self) -> None:
        """
        Execute all stored callbacks.
        """
        for nr, func in enumerate(self.callback_f_queue):
            func(self.callback_arg_queue[nr])
