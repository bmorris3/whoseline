from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__all__ = ['LineList', 'query']

import os
import astropy.units as u

mock_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'data', 'vald3_threshold05.txt')


class LineList(object):
    """
    LineList table object
    """
    def __init__(self, wavelength, species, priority):
        """
        Parameters
        ----------
        wavelength : `~astropy.units.Quantity`
        species : `~numpy.ndarray`
        priority : `~numpy.ndarray`
        """
        self.wavelength = wavelength
        self.species = species
        self.priority = priority

    @classmethod
    @u.quantity_input(wavelength_min=u.Angstrom, wavelength_max=u.Angstrom)
    def from_mock(cls, wavelength_min, wavelength_max):
        """

        >>> from whoseline import LineList
        >>> import astropy.units as u
        >>> l = LineList.from_mock(3000*u.Angstrom, 4000*u.Angstrom)
        """
        from astropy.io import ascii

        table = ascii.read(mock_data_path)

        in_wavelength_bounds = ((table['wavelengths']*u.Angstrom < wavelength_max) &
                                (table['wavelengths']*u.Angstrom > wavelength_min))

        return cls(wavelength=table['wavelengths'][in_wavelength_bounds].data * u.Angstrom,
                   species=table['species'][in_wavelength_bounds].data,
                   priority=table['strengths'][in_wavelength_bounds].data)


@u.quantity_input(wavelength_min=u.Angstrom, wavelength_max=u.Angstrom)
def query(source, wavelength_min, wavelength_max):
    """
    Query table for values

    Parameters
    ----------
    source : str
    wavelength_min : `~astropy.units.Quantity`
    wavelength_max : `~astropy.units.Quantity`
    """
    if source == 'NIST':
        ll = LineList.from_mock(wavelength_min=wavelength_min,
                                wavelength_max=wavelength_max)

