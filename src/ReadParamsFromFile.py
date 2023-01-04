import numpy as np

def readParams(filename):

    params = []

    with open(filename) as file:

        for line in file:
            # skip comments in the file
            if line[0]=='#': continue

            # get the parameters as strings, convert to doubles
            par = list(map(np.double, line.split()))
            params.append(par)
            for p in par:
                if p<0:
                    print('WARNING: p={}<0'.format(p))

    return params
