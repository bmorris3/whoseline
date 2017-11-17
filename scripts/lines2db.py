#!/usr/bin/env python

import sys
import argparse
import sqlite3
import gzip

parser = argparse.ArgumentParser(description='Import a CSV data file into '
											 'the sqlite database.')
parser.add_argument('-d', '--database',
					help='The full path to the sqlite database',
					required=True)
parser.add_argument('-s', '--source',
					help='A short, unique name that identifies the source (that is already in db).',
					required=True)
parser.add_argument('-l', '--list',
					help='Path to file containing line list.',
					required=True)
parser.add_argument('--header-lines',
					help='Number of header lines to skip.',
					required=False,
					type=int,
					default=0)
parser.add_argument('--species-col',
					help='Column of file that contains the species name.',
					required=True,
					type=int)
parser.add_argument('--wavelength-col',
					help='Column of file that contains the wavelength data.',
					required=True,
					type=int)
parser.add_argument('--priority-col',
					help='Column of file that contains the priority data.',
					required=True,
					type=int)

# Print help if no parameters were provided.
#
if len(sys.argv)==1:
	print()
	parser.print_help()
	print()
	sys.exit(1)

args = parser.parse_args()

# open database connection
#
connection = sqlite3.connect(args.database)
#c = connection.cursor()

# Get the specified source id.
#
with connection:
	cursor = connection.cursor()
	cursor.execute("SELECT id FROM source WHERE short_name = ?", [args.source])
	rows = cursor.fetchall()
	if len(rows) == 0:
		print("The source name '{0}' was not found.".format(args.source))
		sys.exit(1)
	source_id  = rows[0][0]

# Read input file
#
with connection:
	cursor = connection.cursor()		
	
	query = "INSERT INTO line (species, wavelength, priority, source_id) VALUES (?,?,?,?)"
	
	if (args.list.endswith(".gz")):
		f = gzip.open(args.file)
	else:
		f = open(args.list)
	
	#
	# skip n header lines
	#
	for i in range(args.header_lines):
		f.readline()

	for line in f:
		is_csv = ',' in line # not efficient to check every time, don't care
		if is_csv:
			values = line.split(",")
		else:
			values = line.split()
		
		# strip leading/trailing spaces, quotes
		#
		for i, value in enumerate(values):
			values[i] = value.strip()		   
			values[i] = value.strip("\"'")
		
		cursor.execute(query, [values[args.species_col-1], values[args.wavelength_col-1],
							   values[args.priority_col-1], source_id])
			
	connection.commit()
