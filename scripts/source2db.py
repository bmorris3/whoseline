#!/usr/bin/env python

import sys
import sqlite3
import argparse

parser = argparse.ArgumentParser(description='Script to add a line list source to the database.')

parser.add_argument('-d', '--database',
					help='The full path to the sqlite database.',
					required=True)
parser.add_argument('--short-name',
					help='A short, unique name that identifies the source.',
					required=True)
parser.add_argument('--display-name',
					help='The full name of the list, designed for display.',
					required=True)
parser.add_argument('--url',
					help='A URL reference to the list.',
					default=None,
					required=False)
parser.add_argument('--description',
					help='A description of the source.',
					default=None,
					required=False)

# Print help if no parameters were provided.
#
if len(sys.argv)==1:
	print()
	parser.print_help()
	print()
	sys.exit(1)

args = parser.parse_args()

conn = sqlite3.connect(args.database)
c = conn.cursor()

query = '''INSERT INTO source
(short_name, display_name, url, description) VALUES (?, ?, ?, ?)'''

c.execute(query, (args.short_name, args.display_name, args.url, args.description))

conn.commit()
conn.close()

