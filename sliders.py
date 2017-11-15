"""
Present an interactive spectrum explorer with slider widgets.

Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve slider.py

at your command prompt. Then navigate to the URL

    http://localhost:5006/slider

in your browser.

Built from example:
https://github.com/bokeh/bokeh/blob/master/examples/app/sliders.py
"""

import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, LabelSet, Slider, Dropdown, TextInput, RadioButtonGroup
from bokeh.plotting import figure
from astropy.io import ascii

# Set up data
wavelength, flux = np.loadtxt('data/sample_spectrum.txt', unpack=True)
flux /= flux.max()
N = len(wavelength)

# Load VALD3 line list
from whoseline.lines import vald3_path
table = ascii.read(vald3_path)

table_min_wavelength = table['wavelengths'].min()
table_max_wavelength = table['wavelengths'].max()

wl_bounds = [wavelength.min(), wavelength.max()]
rows_within_bounds = ((table['wavelengths'] > wl_bounds[0]) &
                      (table['wavelengths'] < wl_bounds[1]))
strengths_within_bounds = table[rows_within_bounds]['strengths']

# Create object spectrum data source
source = ColumnDataSource(data=dict(wavelength=wavelength, flux=flux))

# Create line list label source
lines = ColumnDataSource(data=dict(x=table['wavelengths'][rows_within_bounds].data,
                                   top=np.zeros_like(table['wavelengths'][rows_within_bounds].data),
                                   names=table['species'][rows_within_bounds].data))

# Create a set of labels for each species
labels = LabelSet(x='x', y='top', text='names', level='glyph',
                  x_offset=0, y_offset=0, source=lines, render_mode='canvas',
                  angle=np.pi/3)

# Set up plot
plot = figure(plot_height=600, plot_width=800, title="Example spectrum",
              tools="wheel_zoom,box_zoom,pan,reset,save",
              x_range=[wavelength.min(), wavelength.max()],
              y_range=[0, flux.max()])

# Add vertical bars for each line in the line list
plot.vbar(x='x', top='top', source=lines,
          color="black", width=0.01, bottom=0, alpha=0.5)

# Add the actual spectrum
plot.line('wavelength', 'flux', source=source, line_width=1, line_alpha=0.8)
# x_label='Wavelength [Angstrom]', y_label='Flux'

# Set up widgets
nlines_slider = Slider(title="more/less lines", value=10, start=0,
                       end=100, step=0.01)

# def on_text_change(attr, old, new):
#     try:
#         nlines_slider.value = new
#     except ValueError:
#         return

# nlines_text = TextInput(value=str(nlines_slider.value), title='more/less lines:')
# nlines_text.on_change('value', on_text_change)

rv_offset = Slider(title="RV offset", value=0, start=-100,
                   end=100, step=0.01)

menu = [("Cool dwarf", "item_1"), ("Cool giant", "item_2"),
        ("Quasar", "item_3"), ("Galaxy", "item_3")]
dropdown = Dropdown(label="Line list", button_type="success", menu=menu)
radio_button_group = RadioButtonGroup(labels=["Cool dwarf", "Cool giant",
                                              "Quasar", "Galaxy"], active=0)


def on_slider_change(attrname, old, new):
    n_lines_scale = nlines_slider.value
    rv_offset_val = rv_offset.value
    n_lines = int(n_lines_scale/100 * len(strengths_within_bounds))
    condition = strengths_within_bounds >= np.sort(strengths_within_bounds)[-n_lines]
    label_wavelengths = table['wavelengths'][rows_within_bounds]
    label_height = condition.astype(float) * flux.max()

    label_names = table['species'][rows_within_bounds].data.copy()
    # Blank out some labels
    label_names[~condition] = ''

    # nlines_text.value = str(nlines_slider.value) #str(new)

    lines.data = dict(x=label_wavelengths + rv_offset_val,
                      top=0.9*label_height*plot.y_range.end,
                      names=label_names)


for w in [nlines_slider, rv_offset]:
    w.on_change('value', on_slider_change)

# for w in [nlines_text]:
#     w.on_change('value', on_text_change)


# Set up layouts and add to document
inputs = widgetbox(nlines_slider, rv_offset, radio_button_group)  #nlines_text
plot.add_layout(labels)

curdoc().add_root(column(inputs, plot, height=1000))
curdoc().title = "Whose line is it anyway"
