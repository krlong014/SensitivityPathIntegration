import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ResponseFunction import *
from ChemostatModelMgr import *
from LimitPointSampleHandler import *
from ResponseData import *
from MultiParamProposalGenerator import *
from MHSampler import *
from math import *
import numpy as np


def showContours(imgName, modelMgr, limPtParams, limCycleParams):

    na = 100
    nb = 100

    aMin = 0.001
    aMax = 0.05

    bMin = 0.001
    bMax = 0.6


    A = np.linspace(aMin, aMax, na)
    B = np.linspace(bMin, bMax, nb)
    Z = np.zeros((len(A), len(B)))

    ia = 0
    for a in A:
        ib = 0
        for b in B:
            p = [a, b]
            logL = log10(modelMgr.likelihood(p)+1.0e-20)
            Z[ib,ia] = logL
            ib += 1

        ia += 1

    LP = np.array(limPtParams)
    LC = np.array(limCycleParams)


    cs = plt.contourf(A, B, Z)
    plt.title(modelMgr.name())
    plt.colorbar(cs)
    plt.axis([aMin, aMax, bMin, bMax])
    if LP.shape[0]>0: plt.plot(LP[:,0], LP[:,1], 'ko', markersize=2)
    if LC.shape[0]>0: plt.plot(LC[:,0], LC[:,1], 'wo', markersize=2)
    plt.savefig(imgName)
    plt.close()
