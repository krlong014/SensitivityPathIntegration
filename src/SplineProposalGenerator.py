#!/usr/bin/env python

import numpy as np
from ResponseFunction import *
from SplineResponseFunction import *
from Chemostat import *
import matplotlib.pyplot as plt
from ResponseData import *
from scipy.interpolate import interp1d
import numpy.random
import scipy.ndimage



class SplineProposalGenerator:
    def __init__(self, splineResp, settings):
        self.nx = splineResp.nx
        self.xMax = splineResp.xMax
        self.X = splineResp.X
        self.fInit = self.getInit()
        self.filterWidth = settings['Filter width (# grid points)']
        self.sigVals = scipy.ndimage.gaussian_filter1d(self.getSigLogF(),
            self.filterWidth)
        self.nSig = settings['Limiter (# sigmas)']
        self.wOld = settings['Weight for previous sample (in [0:1])']

        self.a = np.log(self.getInit()) - self.nSig * self.sigVals
        self.b = np.log(self.getInit()) + self.nSig * self.sigVals
        self.h = self.b - self.a

        self.alpha = ((self.h/self.sigVals)**2 - 4)/8
        self.beta = ((self.h/self.sigVals)**2 - 4)/8

        #print('alpha={}\nbeta={}\n'.format(self.alpha,self.beta))

    def proposal(self, fParams):
        a = self.a
        b = self.b
        wOld = self.wOld

        xi = np.random.default_rng().beta(self.alpha, self.beta)
        logf = (wOld*np.log(fParams) + (1-wOld)*(a + (b-a)*xi))
        logf = scipy.ndimage.gaussian_filter1d(logf, self.filterWidth)

        return np.exp(logf)

    def getInit(self):
        logf = np.array([self.logInitFitFunc(x) for x in self.X])
        return np.exp(logf)


    def logInitFitFunc(self, x):
        return -6.37288 + x*(-0.17217 + 0.000925601*x)

    def sigLogFitFunc(self, x):
        return 3.273 + 0.0297*x + 4.7269/(1. + x)

    def getSigLogF(self):

         return np.array([self.sigLogFitFunc(x) for x in self.X])


    # def plotModels(self, plotNum):
    #
    #     plt.figure(plotNum)
    #     xFine = np.linspace(0,90,200)
    #
    #     rVecs = [np.array([mod.eval(x) for x in xFine]) for mod in self.models]
    #     plt.figure(2)
    #     for r in rVecs:
    #         plt.plot(xFine/360, 1.225*r)
    #     csv = np.genfromtxt('../ExperimentalData/FloraEtAl2011.csv', delimiter=",")
    #     xDat = csv[:,0]
    #     rDat = csv[:,1]
    #     plt.plot(xDat, rDat, 'ko')
    #     plt.axis([0, 0.25, 0.0, 0.25])


if __name__=='__main__':

    xMax = 90.0
    nx = 64
    resp = SplineResponseFunction(xMax, nx)


    splinePropGen = {
        'Type' : 'Spline',
        'Settings' : {
            'Limiter (# sigmas)' : 5.0,
            'Filter width (# grid points)' : 4,
            'Weight for previous sample (in [0:1])' : 0.5
        }
    }
    gen = SplineProposalGenerator(resp, splinePropGen['Settings'])


    plt.figure(3)
    X = gen.X
    f = gen.getInit()
    for i in range(30):
        resp.setParams(f)
        r = np.array([resp.eval(x) for x in X])
        plt.plot(X/360, r)
        for skip in range(100):
            f = gen.proposal(f)
    csv = np.genfromtxt('../ExperimentalData/FloraEtAl2011.csv', delimiter=",")
    xDat = csv[:,0]
    rDat = csv[:,1]
    plt.plot(xDat, rDat, 'ko')
    plt.axis([0, 0.25, 0.0, 0.25])

    plt.show()
