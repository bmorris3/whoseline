from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__all__ = ['LineList', 'query']

import sqlite3
conn = sqlite3.connect('test.db')
c = conn.cursor()


class LineList(object):
    """
    LineList table object
    """
    def __init__(self, wavelength, species, priority):
        """
        Parameters
        ----------
        wavelength : `~numpy.ndarray`
        species : `~numpy.ndarray`
        priority : `~numpy.ndarray`
        """
        self.wavelength = wavelength
        self.species = species
        self.priority = priority


def query(table, wavelength_min, wavelength_max):
    """
    Parameters
    ----------
    table : `str`
    wavelength_min : `~astropy.units.Quantity`
    wavelength_max : `~astropy.units.Quantity`
    """
    
