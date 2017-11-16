from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__all__ = ['LineList', 'query', 'linelist_paths']

import os
import astropy.units as u
import numpy as np
import pandas as pd

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
        # TODO: don't read with pandas and convert to astropy table.
        # just use pandas?
        path = os.path.join(mock_data_dir, linelist_paths[source])
        table = pd.read_csv(path)
        # TODO: More sophisticated table column name finder
        wavelength_column = _col_name_containing('wave', table)
        species_column = _col_name_containing('species', table)
        priorities_column = _col_name_containing('priorit', table)

        in_wavelength_bounds = ((table[wavelength_column].values*u.Angstrom < wavelength_max) &
                                (table[wavelength_column].values*u.Angstrom > wavelength_min))

        return cls(wavelength=table[wavelength_column].values[in_wavelength_bounds] * u.Angstrom,
                   species=table[species_column].values[in_wavelength_bounds],
                   priority=table[priorities_column].values[in_wavelength_bounds])


def _col_name_containing(search_str, table):
    """
    Find column header containing ``search_str``, return the exact string of that
    column header.
    """
    colnames = table.columns.values
    return colnames[np.array([search_str in cn.lower() for cn in colnames])][0]


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
