#!/usr/bin/env python2
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import os
import sys
import sqlite3
import csv

def create_database(args):
    print("Creating database %s..." % args.database)
    conn = sqlite3.connect(args.database)
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
    
    conn.commit()
    conn.close()

def import_file(csv_file, args):
    print("Processing file %s..." % csv_file)
    
    conn = sqlite3.connect(args.database)
    c = conn.cursor()
    
    c.execute('''SELECT * FROM sources WHERE short_name = ? ''', (args.source,))
    result = c.fetchone()
    
    if not result:
        print("Adding source %s..." % args.source)
        c.execute('''INSERT INTO sources (display_name, short_name, url, description) VALUES (?, ?, ?, ?)''',
                  (args.display_name, args.source, args.url, args.description))
        conn.commit()
        
        c.execute('''SELECT * FROM sources WHERE short_name = ? ''',
                  (args.source,))
        result = c.fetchone()
    
    source_id, _, _, _, _ = result
    
    headers = args.headers.split(',')
    
    if len(headers) != 3:
        sys.exit("Incorrect number of headers or columns specified. "
                 "Three are required.")
    
    with open(csv_file) as f:
        try:
            wavelength, species, priority = [int(h) for h in headers]
            print("Using columns %r" % (wavelength, species, priority))
            reader = csv.reader(f, delimiter=args.separator)
            
        except ValueError:
            print("Could not convert %r to integer column indices; assuming "
                  "text headers" % headers)
            wavelength, species, priority = headers
            reader = csv.DictReader(f, delimiter=args.separator)
            
        added = 0
        
        for row in reader:
            c.execute('''INSERT INTO data (source_id, wavelength, species, priority) VALUES (?, ?, ?, ?)''',
                      (source_id, float(row[wavelength]), row[species],
                       float(row[priority])))
            added += 1
    
    conn.commit()
    conn.close()
    
    print("Added %d rows." % added)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import a CSV data file into '
                                                 'the sqlite database.')
    parser.add_argument('database', help='The full path to the sqlite database')
    parser.add_argument('source', help='The short name of the source')
    
    parser.add_argument('files', nargs='+',
                        help='Files to be imported, Multiple files can be '
                             'imported at once if they share the same delimiter'
                             ' and metadata.')
    
    parser.add_argument('--separator', '-s',
                        help='The field separator used by the file(s)',
                        default=str(u","))
    parser.add_argument('--headers', '-H',
                        help='comma-separated list of the wavelength, species '
                             'and priority header names, in that order. If '
                             'there are no headers in the file, the '
                             'corresponding column numbers should be given '
                             'instead (starting from 0).', default='0,1,2')

    parser.add_argument('--display-name', '-n',
                        help='The display name of the source')
    parser.add_argument('--url', '-u', help='The url of the source')
    parser.add_argument('--description', '-d',
                        help='The description of the source')
    args = parser.parse_args()
    
    if not os.path.exists(args.database):
        create_database(args)
        
    for csv_file in args.files:
        import_file(csv_file, args)
