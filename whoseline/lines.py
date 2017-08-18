import os
from astropy.io import ascii
import matplotlib.pyplot as plt
import numpy as np

__all__ = ['table', 'plot_lines']

vald3_path = os.path.join(os.path.dirname(__file__), os.path.pardir, 
                          'data', 'vald3_threshold05.txt')

table = ascii.read(vald3_path)

def plot_lines(line_table, axis, n_lines, line_kwargs, upper_xaxis=True):
    wl_bounds = axis.get_xlim()

    rows_within_bounds = ((line_table['wavelengths'] > wl_bounds[0]) & 
                           (line_table['wavelengths'] < wl_bounds[1]))
    
    strengths_within_bounds = line_table[rows_within_bounds]['strengths']
    
    if len(strengths_within_bounds) < n_lines:
        n_lines = len(strengths_within_bounds)
    
    condition = strengths_within_bounds >= np.sort(strengths_within_bounds)[-n_lines]

    for wavelength, strength, species in zip(line_table['wavelengths'][rows_within_bounds][condition],
                                             line_table['strengths'][rows_within_bounds][condition], 
                                             line_table['species'][rows_within_bounds][condition]):
        axis.axvline(wavelength, **line_kwargs)
        if not upper_xaxis:
            axis.annotate(species, xy=(wavelength, 1.0), rotation=30)
        
    new_ticks = line_table['wavelengths'][rows_within_bounds][condition]
    new_tick_labels = line_table['species'][rows_within_bounds][condition]
    
    if upper_xaxis:
        axis_upper = axis.twiny()

        def tick_function(x):
            return (x-wl_bounds[0])/(wl_bounds[1] - wl_bounds[0])

        axis_upper.set_xticks(tick_function(new_ticks))
        axis_upper.set_xticklabels(new_tick_labels, rotation=45, ha='left')