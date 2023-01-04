#!/usr/bin/env python

import numpy as np
from ResponseFunctionManager import *
import matplotlib.pyplot as plt
from Chemostat import *
from SettingsHandler import *

class ResponseData:
    defaults = {
        'File' : '../ExperimentalData/FloraEtAl2011.csv',
        'Delimiter' : ',',
        'Sigma Factor' : 1.0
        }

    def __init__(self, settings):

        self.settings = mergeSettings(ResponseData.defaults, settings)
        datafile = self.settings['File']
        delim = self.settings['Delimiter']
        sigmaFactor = self.settings['Sigma Factor']

        csv = np.genfromtxt(datafile, delimiter=delim)
        xScaleUp = 360
        rScaleDown = 1.225
        self.xDat = csv[:,0]*xScaleUp
        self.rDat = csv[:,1]/rScaleDown

        ivlev = IvlevModel()
        ri = np.array([ivlev.eval(x) for x in self.xDat])
        self.sigma = sigmaFactor*sqrt(np.var(ri - self.rDat))

    def likelihood(self, rFunc):

        f, df, df2 = rFunc.evalDerivs(0.1)
        factor = 1.0
        slopeCutoff = 0.02
        if abs(df)>slopeCutoff:
            factor = exp(-2*(df-slopeCutoff)/slopeCutoff)
        rVals = np.array([rFunc.eval(x) for x in self.xDat])
        dr = (rVals - self.rDat)/self.sigma/sqrt(2)
        return factor*exp(-np.sum(np.multiply(dr, dr)))





if __name__=='__main__':
    r = ResponseData()
