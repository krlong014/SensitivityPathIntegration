#!/usr/bin/env python

from math import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


class MultiParamResponseFunction:

    def __init__(self, params):
        self.params = np.array(params)

    def setParams(self, params):
        self.params = np.array(params)

    def getParams(self):
        return np.copy(self.params)



class HollingModel(MultiParamResponseFunction):
    def __init__(self, params=[0.015, 0.18]):
        MultiParamResponseFunction.__init__(self, params)

    def eval(self, y):
        a = self.params[0]
        b = self.params[1]
        return a * y / (1.0 + b*y)

    def evalDerivs(self, y):
        a = self.params[0]
        b = self.params[1]

        den = 1 + b*y
        f = a/den
        return (f*y, f/den, -2.0*b*f/den/den)


    def name(self):
        return 'Holling'



class IvlevModel(MultiParamResponseFunction):
    def __init__(self, params=[0.011, 0.15]):
        MultiParamResponseFunction.__init__(self, params)

    def eval(self, y):
        a = self.params[0]
        b = self.params[1]
        return a/b * (1.0 - exp(-b*y))


    def evalDerivs(self, y):
        a = self.params[0]
        b = self.params[1]

        ex = exp(-b*y)
        return (a/b*(1-ex), a*ex, -a*b*ex)


    def name(self):
        return 'Ivlev'



class TanhModel(MultiParamResponseFunction):
    def __init__(self, params=[0.0082, 0.11]):
        MultiParamResponseFunction.__init__(self, params)

    def eval(self, y):
        a = self.params[0]
        b = self.params[1]
        return a/b * tanh(b*y)

    def evalDerivs(self, y):
        a = self.params[0]
        b = self.params[1]

        t = tanh(b*y)
        s = 1.0/cosh(b*y)
        return (a/b*t, a*s*s, -2*a*b*t*s*s)

    def name(self):
        return 'Tanh'

class CombinationModel(MultiParamResponseFunction):
    def __init__(self, params=[0.015, 0.18, 0.011, 0.15, 0.0082, 0.11]):
        MultiParamResponseFunction.__init__(self, params)
        self.holling = HollingModel([params[0], params[1]])
        self.ivlev = IvlevModel([params[2], params[3]])
        self.tanh = TanhModel([params[4], params[5]])

    def eval(self, y):
        return 1/3.0*(self.holling.eval(y)
                      + self.ivlev.eval(y)
                      + self.tanh.eval(y))

    def setParams(self, params):
        self.params = np.array(params)
        self.holling.setParams([params[0], params[1]])
        self.ivlev.setParams([params[2], params[3]])
        self.tanh.setParams([params[4], params[5]])

    def getParams(self):
        return np.copy(self.params)

    def name(self):
        return 'Combination'



def showModels():
    x = np.linspace(0,90,200)
    mh = HollingModel()
    mi = IvlevModel()
    mt = TanhModel()
    mc = CombinationModel()
    f = 1.225
    rh = f*np.array([mh.eval(xi) for xi in x])
    ri = f*np.array([mi.eval(xi) for xi in x])
    rt = f*np.array([mt.eval(xi) for xi in x])
    rc = f*np.array([mc.eval(xi) for xi in x])

    csv = np.genfromtxt('../ExperimentalData/FloraEtAl2011.csv', delimiter=",")
    xDat = csv[:,0]
    rDat = csv[:,1]

    mpl.rcParams.update({'font.size' : 14})

    plt.plot(x/360, rh, 'r-',
             x/360, ri, 'b-',
             x/360, rt, 'g-',
             x/360, rc, 'k-',
             xDat, rDat, 'ko')
    plt.legend(['Holling', 'Ivlev', 'Tanh', 'Combination', 'Data'])
    plt.xlabel('Food density')
    plt.ylabel('Grazer response function')
    plt.axis([0, 0.25, 0, 0.25])
    plt.show()




if __name__=='__main__':

    showModels()
