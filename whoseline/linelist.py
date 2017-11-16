from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

__all__ = ['LineList', 'query']

import os
import astropy.units as u
import numpy as np

sqlite_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'data', 'linelist.db')

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
    def from_db(cls, source, wavelength_min, wavelength_max):
        """

        >>> from whoseline import LineList
        >>> import astropy.units as u
        >>> l = LineList.from_db('NIST', 3000*u.Angstrom, 4000*u.Angstrom)
        """
        
        import sqlite3

        conn = sqlite3.connect(sqlite_data_path)
        c = conn.cursor()
        
        results = c.execute('''SELECT wavelength, species, priority
            FROM data 
            INNER JOIN sources
            ON data.source_id = sources.source_id
            WHERE short_name = ?
            AND wavelength >= ?
            AND wavelength <= ?
            ''',
            (source, wavelength_min.value, wavelength_max.value)
        ).fetchall()
        
        if results:
            wavelength, species, priority = zip(*results)
        else:
            wavelength, species, priority = [], [], []
        
        return cls(
            np.array(wavelength) * u.Angstrom,
            np.array(species),
            np.array(priority)
        )


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

    ll = LineList.from_db(source, wavelength_min=wavelength_min,
                                wavelength_max=wavelength_max)
    
    return ll


if __name__ == '__main__':

    if not os.path.exists(sqlite_data_path):
        import sqlite3
        import csv
        
        conn = sqlite3.connect(sqlite_data_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE sources (
            source_id integer PRIMARY KEY,
            display_name text,
            short_name text,
            url text,
            description text
        )''')
        
        c.execute('''CREATE TABLE data (
            source_id integer, 
            wavelength real, 
            species text, 
            priority real,
            FOREIGN KEY (source_id) REFERENCES sources(source_id)
        )''')
        
        mock_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'data', 'vald3_threshold05.txt')
        
        c.execute('''INSERT INTO sources (display_name, short_name, url, description) VALUES ('NIST', 'NIST', '', '')''')
        
        conn.commit()
        
        c.execute('''SELECT * FROM sources WHERE short_name = 'NIST' ''')
        source_id, _, _, _, _ = c.fetchone()
        
        with open(mock_data_path) as f:
            reader = csv.DictReader(f, delimiter=str(u" "))
            for row in reader:
                c.execute('''INSERT INTO data (source_id, wavelength, species, priority) VALUES (?, ?, ?, ?)''', (source_id, float(row['wavelengths']), row['species'], float(row['strengths'])))
        
        conn.commit()
        conn.close()
                
    # test query
    linelist = query('NIST', 3000*u.Angstrom, 4000*u.Angstrom)
    print(linelist.wavelength, linelist.species, linelist.priority)
    
