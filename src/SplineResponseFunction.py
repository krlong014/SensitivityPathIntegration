#!/usr/bin/env python


from Mesh1D import *
from math import *
import numpy as np
import matplotlib.pyplot as plt

from SplineSolver import *

class SplineResponseFunction:
    def __init__(self, xMax, nx):

        self.nx = nx
        self.xMax = xMax
        self.solver = SplineSolver(xMax, nx)
        self.mesh = Mesh1D(0.0, xMax, nx)
        self.X = np.array([i*xMax/float(nx-1) for i in range(0,nx)])


    def name(self):
        return 'Spline'

    def setParams(self, params):
        self.fParams = params
        self.solver.solve(self.fParams)

        self.responseData = np.array([self.eval(x) for x in self.X])

    def getParams(self):
        return self.fParams

    def eval(self, y):
        return self.solver.interpolate(y)

    def evalDerivs(self, y):
        return self.solver.interpolateDerivs(y)

    def isInInterval(self, a, b, x):
        if x>=a and x<=b:
            return True
        return False


    def tabulateVals(self, xVals):
        y = np.zeros(len(xVals))

        for i in range(0,len(xVals)):
            y[i]=self.interpolate(xVals[i])
        return y

    def setParamsFromResponse(self, rFunc):
        nx = self.nx
        xMax = self.xMax
        X = np.array([i*xMax/float(nx-1) for i in range(0,nx)])
        self.responseData = np.array([rFunc.eval(x) for x in X])
        self.fParams = np.zeros(nx)

        eps = (1.0e-7)*xMax

        self.fParams[0] = -(2*rFunc.eval(0) - 5*rFunc.eval(eps)
                           + 4*rFunc.eval(2*eps) - rFunc.eval(3*eps))/eps/eps

        for i in range(1,nx-1):
            self.fParams[i] = (2*rFunc.eval(X[i])
                               - rFunc.eval(X[i]-eps)
                               - rFunc.eval(X[i]+eps))/eps/eps

        self.fParams[nx-1] = -(2*rFunc.eval(xMax) - 5*rFunc.eval(xMax-eps)
                              + 4*rFunc.eval(xMax-2*eps)
                              - rFunc.eval(xMax-3*eps))/eps/eps


        self.solver.solve(self.fParams)

        return self.fParams




if __name__=='__main__':

    # Define a simple response function
    class Tanh:
        def __init__(self):
            pass
        def eval(self,x):
            return tanh(x)

    # Define a spline response
    xMax = 5.0
    nx = 64
    r = SplineResponseFunction(xMax, nx)

    nVals = 200
    x = np.linspace(0.0, xMax, nVals)
    z = np.copy(x)

    # Create spline function from second derivative of simple function
    th = Tanh()
    w = r.setParamsFromResponse(th)

    # Locations of nodes
    X = np.linspace(0.0, xMax, nx)

    t = np.array([tanh(s) for s in x])
    z = np.array([r.eval(s) for s in x])

    plt.plot(x, z, '-r', x, t, '-b', X, w, '-k')
    plt.show()
