import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import solara
from ipywidgets import Output
import numpy as np

import astropy.units as u
from astroquery.nist import Nist

from expecto import get_spectrum
from expecto.core import (
    phoenix_model_temps, phoenix_model_logg, phoenix_model_z, phoenix_model_alpha
)

import pandas as pd


df_elements = pd.read_csv(os.path.join(os.path.dirname(__file__), 'elements.csv'))
abundance_sort = np.argsort(np.nan_to_num(df_elements['Solar Abundance'], -1))
elements_by_abundance = list(
    df_elements['Element'][abundance_sort[::-1]]
)

sorted_elements = solara.reactive(elements_by_abundance)

fig_output = Output()


def g_string_to_float(s):
    if not isinstance(s, np.ma.core.MaskedConstant):
        return list(map(float, s.split(' - ')))
    else:
        return [np.nan, np.nan]


def ritz_string_to_float(s):
    if isinstance(s, np.ma.core.MaskedConstant):
        return np.nan
    elif isinstance(s, float):
        return s
    elif '+' in s:
        return float(s[:-1])
    else:
        return float(s)


n_species = solara.reactive(5)
species_list = solara.reactive(sorted_elements.value[:int(n_species.value)])
minimum_wavelength = solara.reactive(0.38)
maximum_wavelength = solara.reactive(0.41)
spectrum_line_alpha = solara.reactive(1)
spectrum_line_width = solara.reactive(0.7)
meta = solara.reactive({})
T_eff = solara.reactive(5800)
log_g = solara.reactive(4.5)
metallicity = solara.reactive(0.0)
alpha = solara.reactive(0.0)
log_scale = solara.reactive(True)

style = {
    'text-transform': 'capitalize'
}


@solara.component
def Page():
    solara.Title("whose line is it anyway?")

    def clear_species_selections():
        species_list.set([])

    def select_all_species():
        species_list.set(sorted_elements)

    def next_n_species():
        if len(species_list.value):
            last_idx = sorted_elements.value.index(species_list.value[-1])
        else:
            last_idx = 0
        species_list.set(sorted_elements.value[last_idx:last_idx + int(n_species.value)])

    def first_n_species():
        species_list.set(sorted_elements.value[:int(n_species.value)])

    with solara.Column():
        with solara.Columns([0.5, 1, 1, 1, 0.5]):
            with solara.Column():
                pass

            with solara.Column():
                solara.Markdown('## PHOENIX Spectrum')
                solara.Select("Effective temperature [K]", list(phoenix_model_temps), T_eff)
                solara.Select("log g [cgs]", list(phoenix_model_logg), log_g)
                solara.Select("Metallicity, Z = [M/H]", list(phoenix_model_z), metallicity)
                solara.Select("[alpha/H]", list(phoenix_model_alpha), alpha)

                if len(meta.value):
                    children = [
                        solara.HTML(tag='p', unsafe_innerHTML=str(meta.value.tostring(sep=r'<br />')))
                    ]
                    solara.Details("PHOENIX model header", children=children, expand=False)

            with solara.Column():
                solara.Markdown('## Elements')
                solara.SelectMultiple("Elements", species_list, sorted_elements.value)
                solara.Button("Clear selected elements", on_click=clear_species_selections, style=style)

                def order_by_atomic_number(by_atomic_number):
                    if by_atomic_number:
                        elements = list(
                            df_elements['Element']
                        )
                    else:
                        elements = elements_by_abundance

                    sorted_elements.set(elements)
                    species_list.set(sorted_elements.value[:int(n_species.value)])

                solara.Switch(label="Order by atomic number", value=False, on_value=order_by_atomic_number)

                solara.InputInt("Number of species per query", n_species)
                solara.Button(f"Select first {n_species} elements", on_click=first_n_species, style=style)
                solara.Button(f"Select next {n_species} elements", on_click=next_n_species, style=style)
                solara.Button("Select all elements (slow)", on_click=select_all_species, style=style)

            with solara.Column():
                solara.Markdown('## Wavelength range')
                solara.InputFloat("Minimum wavelength [µm]", minimum_wavelength)
                solara.InputFloat("Maximum wavelength [µm]", maximum_wavelength)

                solara.Markdown('<br /><br />\n## Plot')
                solara.SliderFloat("Spectrum opacity", spectrum_line_alpha, min=0, max=1)
                solara.SliderFloat("Spectrum line width", spectrum_line_width, min=0.1, max=10)
                solara.Switch(label='Log scale', value=log_scale)

            with solara.Column():
                pass

    with solara.Column(align='center'):
        with fig_output:
            plt.close()
            fig_output.clear_output()
            fig = plt.figure(figsize=(20, 5))

            wl_min, wl_max = [minimum_wavelength.value, maximum_wavelength.value] * u.um
            spectrum = get_spectrum(
                T_eff=T_eff.value,
                log_g=log_g.value,
                Z=metallicity.value,
                alpha=alpha.value,
                cache=True
            )
            meta.set(spectrum.meta)

            spectrum_mask = (
                (spectrum.wavelength >= wl_min) &
                (spectrum.wavelength <= wl_max)
            )

            plt.plot(
                spectrum.wavelength[spectrum_mask].to(u.um),
                spectrum.flux[spectrum_mask],
                color='k',
                lw=spectrum_line_width.value,
                alpha=spectrum_line_alpha.value
            )
            query_results = {}
            for i, species in enumerate(species_list.value):
                try:
                    table = Nist.query(wl_min, wl_max, linename=species)
                    query_results[species] = table
                except (Exception, KeyError):
                    # skip elements not supported in NIST query
                    continue

                if 'gi   gk' not in table.colnames:
                    continue

                g_1, g_2 = np.array([g_string_to_float(s) for s in table['gi   gk']]).T / u.cm
                f_ik = table['fik']

                # https://phys.libretexts.org/Bookshelves/Astronomy__Cosmology/Stellar_Atmospheres_(Tatum)/09%3A_Oscillator_Strengths_and_Related_Topics/9.09%3A_Summary_of_Relations_Between_f%2C_A_and_S
                # proportional to
                wavelength_ritz = np.array([ritz_string_to_float(ritz) for ritz in table['Ritz']])
                S = (g_1 * f_ik * wavelength_ritz).value
                for j, (wl, strength) in enumerate(zip(wavelength_ritz, S)):
                    plot_alpha = (strength - np.nanmin(S)) / np.ptp(S[~np.isnan(S)])
                    if not np.isnan(plot_alpha):
                        plt.axvline(wl, alpha=plot_alpha, color=f'C{i}', zorder=-10)


            plt.legend([Line2D([], [], color=f'C{i}') for i in range(len(species_list.value))], species_list.value)
            plt.gca().set(
                xlabel='Wavelength [µm]',
                ylabel=f'Flux [{spectrum.flux.unit.to_string("latex")}]',
                yscale='log' if log_scale.value else 'linear'
            )
            solara.FigureMatplotlib(fig)

    with solara.Columns([0.1, 1, 0.1]):
        with solara.Column():
            pass

        with solara.Column():
            solara.Markdown("## NIST Results")
            solara.Markdown(
                'Query results from the [NIST Atomic Spectra Database (Standard Reference Database 78)]'
                '(https://www.nist.gov/pml/atomic-spectra-database) via '
                '[astroquery.nist](https://astroquery.readthedocs.io/en/latest/nist/nist.html).'
            )
            if len(species_list.value):
                with solara.lab.Tabs(background_color="#bbeefe", color='#000000'):
                    for species in species_list.value:
                        with solara.lab.Tab(species, style=style):
                            if species in query_results:
                                df = query_results[species].to_pandas()
                                solara.DataFrame(df.sort_values('Ritz'), items_per_page=10)

        with solara.Column():
            pass
