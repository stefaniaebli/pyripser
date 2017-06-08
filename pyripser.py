import numpy as np
from scipy.spatial import distance_matrix
import subprocess
from tempfile import mktemp
from os import remove


def ripser(dm, ord_max=2, ripser_pathname='/home/stefania/ripser/ripser', ripser_format='distance'):
	matrix_filename = mktemp()
	np.savetxt(matrix_filename, dm, delimiter=' ')
	result = execute_and_parse(matrix_filename=matrix_filename, ord_max=ord_max, ripser_pathname=ripser_pathname, ripser_format=ripser_format)
	remove(matrix_filename)
	return result


def execute_and_parse(matrix_filename, ord_max=2, ripser_pathname='/home/stefania/ripser/ripser', ripser_format='distance'):
	proc = subprocess.Popen([ripser_pathname, '--dim', str(ord_max), '--format', ripser_format, matrix_filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output =''
	for line in proc.stdout:
		print(line[:-1])
		output += line

	proc.wait()
	# output = proc.stdout.read()
	
	output_list = output.split('\n')
	n_points_output = int(output_list[0].split(' ')[3])
	# assert(n_points == n_points_output)
	matrix_min, matrix_max = output_list[1].split(' ')[2].strip('[').strip(']').split(',')
	matrix_min = float(matrix_min)
	matrix_max = float(matrix_max)
	# print(matrix_min, matrix_max)
	row = 2
	# for ord in range(ord_max + 1):
	ord = -1
	result = {}
	while output_list[row] != '':
		if output_list[row].startswith('persistence intervals in dim '):
			ord = int(output_list[row].split(' ')[-1][:-1])
			row += 1
			result_ord = []
			result[ord] =result_ord
			continue

		birth, death = output_list[row].strip(' []()').split(',')
		birth = float(birth)
		try:
			death = float(death)
		except ValueError:
			death = np.nan

		result_ord.append((birth, death))

		row += 1

	return result


if __name__ == '__main__':
	n_points = 100
	dim = 5
	matrix_filename = '/home/stefania/ripser/examples/random_50.txt'
	ord_max = 2
	ripser_pathname = '/home/stefania/ripser/ripser'
	ripser_format = 'distance'

	X = np.random.uniform(size=(n_points, dim))
	dm = distance_matrix(X, X)
	result = ripser(dm, ord_max=ord_max)

