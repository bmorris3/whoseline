from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__all__ = ['LineList', 'query', 'linelist_paths']

import os
import astropy.units as u
import numpy as np

mock_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'data', 'vald3_threshold05.txt')

mock_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data',
                             'linelists')

linelist_paths = {'hitran': 'hitran_simplified.csv',
                  'iraf_sky_lines': 'iraf_sky_lines.csv',
                  'VALD3': 'vald3.csv',
                  'chianti': 'chianti.csv',
                  'arcturus': 'arcturus_optical.csv'}


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

    # @classmethod
    # @u.quantity_input(wavelength_min=u.Angstrom, wavelength_max=u.Angstrom)
    # def from_mock(cls, wavelength_min, wavelength_max):
    #     """
    #
    #     >>> from whoseline import LineList
    #     >>> import astropy.units as u
    #     >>> l = LineList.from_mock(3000*u.Angstrom, 4000*u.Angstrom)
    #     """
    #     from astropy.io import ascii
    #
    #     table = ascii.read(mock_data_path)
    #
    #     in_wavelength_bounds = ((table['wavelengths']*u.Angstrom < wavelength_max) &
    #                             (table['wavelengths']*u.Angstrom > wavelength_min))
    #
    #     return cls(wavelength=table['wavelengths'][in_wavelength_bounds].data * u.Angstrom,
    #                species=table['species'][in_wavelength_bounds].data,
    #                priority=table['strengths'][in_wavelength_bounds].data)

    @classmethod
    @u.quantity_input(wavelength_min=u.Angstrom, wavelength_max=u.Angstrom)
    def from_csv(cls, source, wavelength_min, wavelength_max):
        """

        >>> from whoseline import LineList
        >>> import astropy.units as u
        >>> l = LineList.from_csv(3000*u.Angstrom, 4000*u.Angstrom)
        """
        from astropy.io import ascii

        table = ascii.read(os.path.join(mock_data_dir, linelist_paths[source]))

        print(table.colnames, type(table.colnames))
        colnames = np.array(table.colnames)
        wavelength_column = colnames[np.array(['wave' in cn.lower() for cn in table.colnames])][0]
        species_column = colnames[np.array(['species' in cn.lower() for cn in table.colnames])][0]
        priorities_column = colnames[np.array(['priorit' in cn.lower() for cn in table.colnames])][0]

        print(wavelength_column, species_column, priorities_column)

        in_wavelength_bounds = ((table[wavelength_column]*u.Angstrom < wavelength_max) &
                                (table[wavelength_column]*u.Angstrom > wavelength_min))

        return cls(wavelength=table[wavelength_column][in_wavelength_bounds].data * u.Angstrom,
                   species=table[species_column][in_wavelength_bounds].data,
                   priority=table[priorities_column][in_wavelength_bounds].data)


@u.quantity_input(wavelength_min=u.Angstrom, wavelength_max=u.Angstrom)
def query(source, wavelength_min, wavelength_max):
    """
    Query table for values

    Parameters
    ----------
    source : str
    wavelength_min : `~astropy.units.Quantity`
    wavelength_max : `~astropy.units.Quantity`

    Returns
    -------
    linelist : `~whoseline.LineList` object

    Example
    -------
    >>> from whoseline import query
    >>> query('example', 3000*u.Angstrom, 4000*u.Angstrom) # doctest: +SKIP
    <whoseline.linelist_mock.LineList at 0x106030828>
    """
    #if not source == 'example':
    #    raise NotImplementedError()

    ll = LineList.from_csv(source, wavelength_min=wavelength_min,
                            wavelength_max=wavelength_max)
    
    return ll
