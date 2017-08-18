from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u
from ipywidgets import widgets 
import warnings

__all__ = ['interactive_plot']

@u.quantity_input(wavelength=u.Angstrom)
def interactive_plot(wavelength, flux):
    
    from .lines import (table, plot_lines, table_min_wavelength, table_max_wavelength, 
                        LineListWavelengthBoundWarning)
    
    wavelength = wavelength.to(u.Angstrom).value
    
    if (wavelength.min() < table_min_wavelength) or (wavelength.max() > table_max_wavelength):
        warnmessage = """Spectrum's wavelength bounds extend 
                         beyond wavelength bounds of line list"""
        
        warnings.warn(warnmessage, LineListWavelengthBoundWarning)
    
    wavelength_width = widgets.IntSlider(min=0.1, max=wavelength.ptp(), 
                                         step=0.1, value=wavelength.ptp(),
                                         description="Wavelength Width:")

    wavelength_center = widgets.IntSlider(min=wavelength.min(), 
                                          max=wavelength.max(), 
                                          step=0.1, value=wavelength.mean(),
                                          description="Wavelength Center:")

    flux_max = widgets.IntSlider(min=np.nanmin(flux), 
                                 max=np.nanmax(flux), 
                                 step=0.01, value=np.percentile(flux, 99.9), 
                                 description='Flux Max:')

    n_lines = widgets.IntSlider(min=0, max=len(table)//100, 
                                step=1, value=10, description="More/less lines:")

    interact_kwargs = dict(wavelength_width=wavelength_width, 
                           wavelength_center=wavelength_center, 
                           flux_max=flux_max, n_lines=n_lines)

    @widgets.interact(**interact_kwargs)
    def plot_instance(wavelength_width, wavelength_center, flux_max, n_lines):
        fig, ax = plt.subplots()
        ax.plot(wavelength, flux)

        line_kwargs = dict(color='gray', alpha=0.2, ls='--')

        ax.set(xlim=[wavelength_center - wavelength_width/2, 
                     wavelength_center + wavelength_width/2], 
               ylim=[0, flux_max],
               xlabel='Wavelength', ylabel='Flux')
        plot_lines(table, ax, n_lines, line_kwargs)

        plt.show()