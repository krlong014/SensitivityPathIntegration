#!/usr/bin/env python

import numpy as np

class Mesh1D:
    def __init__(self, a, b, nx):
        self.X = np.linspace(a, b, nx)
        self.numElems = nx-1
        self.numNodes = nx

    def vertexPos(self, v):
        return self.X[v]

    def elemFacets(self, c):
        return (c, c+1)

    def elemWidth(self, c):
        return self.X[c+1]-self.X[c]


if __name__=='__main__':

    mesh = Mesh1D(0, 5.0, 4)

    for e in range(0, mesh.numElems):
        print('elem %d' % e)
        verts = mesh.elemFacets(e)
        print('\tnodes = ', verts)
        print('\t\tpositions= %12.5f %12.5f' % (mesh.vertexPos(verts[0]), mesh.vertexPos(verts[1])))
    

    
