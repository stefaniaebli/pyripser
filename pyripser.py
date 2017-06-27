"""Pyrpser is a Python wrapper to the executable ripser:
  https://github.com/Ripser/ripser

With this wrapper, it is possible to compute the births and deaths of
homology classes of Vietoris-Rips complexes up to the desired order(s)
for a given (Numpy) distance matrix.

Copyright Emanuele Olivetti and Stefania Ebli, 2017

MIT License.

"""

import numpy as np
import subprocess
from tempfile import mktemp
from os import remove

RIPSER_PATHNAME = '/home/stefania/ripser/ripser'


def ripser(dm, ord_max=2, ripser_pathname=RIPSER_PATHNAME,
           ripser_format='distance', verbose=False):
    """Higher-level wrapper of ripser that compute the births and deaths
    of homology classes of Vietoris-Rips complexes up to the desired
    order for a given (Numpy) distance matrix (dm).

    """

    matrix_filename = mktemp()
    np.savetxt(matrix_filename, dm, delimiter=' ')
    result = execute_and_parse(matrix_filename=matrix_filename,
                               ord_max=ord_max,
                               ripser_pathname=ripser_pathname,
                               ripser_format=ripser_format,
                               verbose=verbose)
    remove(matrix_filename)
    return result


def execute_and_parse(matrix_filename, ord_max=2,
                      ripser_pathname=RIPSER_PATHNAME,
                      ripser_format='distance',
                      verbose=True):
    """Lower-level wrapper of ripser, which operates on a txt matrix saved
    on file.
    """
    command = [ripser_pathname,
               '--dim', str(ord_max),
               '--format', ripser_format,
               matrix_filename]
    print("Executing: %s" % " ".join(command))
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    # Print output on screen and keep a copy in variable 'output':
    output = ''
    for line in proc.stdout:
        if verbose:
            print(line[:-1])

        output += line

    proc.wait()

    error = False
    for line in proc.stderr:
        print(line)
        error = True

    if error:
        raise Exception

    # Parse output:
    print("")
    print("Parsing ripser output...")
    output_list = output.split('\n')
    n_points_output = int(output_list[0].split(' ')[3])
    print("Number of points: %s" % n_points_output)
    matrix_min, matrix_max = output_list[1].split(' ')[2].strip('[').strip(']').split(',')
    matrix_min = float(matrix_min)
    matrix_max = float(matrix_max)
    row = 2
    ord = None
    result = {}
    while output_list[row] != '':
        if output_list[row].startswith('persistence intervals in dim '):
            ord = int(output_list[row].split(' ')[-1][:-1])
            row += 1
            result_ord = []
            result[ord] = result_ord
            print("Parsing results of order: %s" % ord)
            continue

        birth, death = output_list[row].strip(' []()').split(',')
        birth = float(birth)
        try:
            death = float(death)
        except ValueError:  # this occurs when death is infinity
            death = np.nan

        result_ord.append((birth, death))
        row += 1

    return result


if __name__ == '__main__':
    from scipy.spatial import distance_matrix
    n_points = 10
    dim = 2
    ord_max = 1
    X = np.random.uniform(size=(n_points, dim))
    dm = distance_matrix(X, X)
    result = ripser(dm, ord_max=ord_max, verbose=True)
