from __future__ import print_function
import multiprocessing 
from multiprocessing import Pool
import numpy as np
import glob
import os
import re
import sys
import time
from pathlib import Path
from write_lammps_data import lammps_inputs
from write_GULP_inputs import GULP_inputs

from UFF4MOF_construction import UFF4MOF
from UFF_construction import UFF
from Dreiding_construction import Dreiding
# add more force field classes here as they are made

force_fields = ['UFF4MOF']

def serial_conversion(directory, force_field=UFF4MOF, ff_string='UFF4MOF', outdir='unopt_lammps_data', charges=False, parallel=False, replication='cutoff'):

	try:
		os.mkdir(outdir)
	except OSError:
		pass

	print('conversion running serial on a single core')

	cifs = sorted(glob.glob(directory + os.sep + '*.cif'))
	for cif in cifs:
		print('converting ', cif, '...')
		lammps_inputs([cif, force_field, ff_string, outdir, charges, replication])

	print('--- cifs in', directory, 'converted and placed in', outdir, '---')

# =============================================================================
# def Kunhuan_serial_conversion(directory, force_field=UFF4MOF, ff_string='UFF4MOF', outdir='unopt_lammps_data', charges=False, parallel=False, replication='cutoff'):
# 
# 	try:
# 		os.mkdir(outdir)
# 	except OSError:
# 		pass
# 
# 	print('conversion running serial on a single core')
# 
# 	cifs = sorted(glob.glob(Path(directory + '/*.cif')))
# 	for cif in cifs:
# 		print('converting ', cif, '...')
# 		lammps_inputs([cif, force_field, ff_string, outdir, charges, replication])
# 
# 	print('--- cifs in', directory, 'converted and placed in', outdir, '---')
# =============================================================================



def parallel_conversion(directory, force_field=UFF4MOF, ff_string='UFF4MOF', outdir='unopt_lammps_data', charges=False, parallel=True, replication='1x1x1'):

	try:
		os.mkdir(outdir)
	except OSError:
		pass

	print('conversion running on ' + str(multiprocessing.cpu_count()) + ' cores')

	cifs = sorted(glob.glob(directory + os.sep + '*.cif'))
	args = [[cif, force_field, ff_string, outdir, charges, replication] for cif in cifs]
	pool = Pool(multiprocessing.cpu_count())
	results_par = pool.map_async(lammps_inputs, args) 
	pool.close()
	pool.join()

	print('--- cifs in', directory, 'converted and placed in', outdir, '---')

def parallel_GULP_conversion(directory, force_field=UFF4MOF, outdir='GULP_inputs', charges=False, parallel=True, replication='1x1x1', GULP=True, noautobond=True):

	try:
		os.mkdir(outdir)
	except OSError:
		pass

	print('conversion running on ' + str(multiprocessing.cpu_count()) + ' cores')

	cifs = sorted(glob.glob(directory + os.sep + '*.cif'))
	args = [[cif, force_field, outdir, charges, replication, noautobond] for cif in cifs]
	pool = Pool(multiprocessing.cpu_count())
	results_par = pool.map_async(GULP_inputs, args) 
	pool.close()
	pool.join()

	print('--- cifs in', directory, 'converted and placed in', outdir, '---')

def run_conversion(replication):

	arguments = sys.argv[1:]
	directory = arguments[0]

	optional_arguments = {'replication':replication}
	for arg in arguments[1:]:
		if '--' in arg and 'parallel':
			parse_arg = re.sub('[--]', '', arg).split('=')
			if parse_arg[0] == 'force_field':
				if parse_arg[1] == 'UFF4MOF':
					value = UFF4MOF
					optional_arguments['ff_string'] = 'UFF4MOF'
				elif parse_arg[1] == 'UFF':
					value = UFF
					optional_arguments['ff_string'] = 'UFF'
				elif parse_arg[1] == 'Dreiding':
					value = Dreiding
					optional_arguments['ff_string'] = 'Dreiding'
				# other options go here as more forcefields are made
			else:
				if parse_arg[1] == 'True':
					value = True
				elif parse_arg[1] == 'False':
					value = False
				else:
					value = parse_arg[1]

			optional_arguments[parse_arg[0]] = value

	try:
		
		if optional_arguments['GULP']:
			print('converting to GULP format...')
			parallel_GULP_conversion(directory, **optional_arguments)

	except KeyError:

		try:
			if optional_arguments['parallel']:
				parallel_conversion(directory, **optional_arguments)
			else:
				serial_conversion(directory, **optional_arguments)
				
		except KeyError:
			serial_conversion(directory, **optional_arguments)

start_time = time.time()
if __name__ == '__main__': 
	replication='1x1x1'
	#replication='cutoff'
	run_conversion(replication)
print("conversion took %s seconds " % np.round((time.time() - start_time), 3))
