#!/usr/bin/env python

from math import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from ResponseFunction import *
from ChemostatModelMgr import *

def showResponseCurves(name, imgName, modelMgr, limPtParams, limCycleParams,
                       numToShow=100,
                       axis = [0.0, 0.25, 0.0, 0.25]):
    #fig = plt.figure()

    nlp = len(limPtParams)
    nlc = len(limCycleParams)
    nTot = nlp + nlc
    nlpToShow = int(ceil(numToShow*float(nlp)/nTot))
    nlcToShow = int(ceil(numToShow*float(nlc)/nTot))

    if nlpToShow>0:
        samp = np.random.choice(nlp, min(nlpToShow, nlp), False)
        for i in samp:
            p = limPtParams[i]
            x = np.linspace(0,90,200)
            modelMgr.responseFunc.setParams(p)
            f  =1.225
            r = f*np.array([modelMgr.responseFunc.eval(xi) for xi in x])
            plt.plot(x/360, r, 'r-', linewidth=1.0)


    if nlcToShow>0:
        samp = np.random.choice(nlc, min(nlcToShow, nlc), False)
        for i in samp:
            p = limCycleParams[i]
            x = np.linspace(0,90,200)
            modelMgr.responseFunc.setParams(p)
            f  =1.225
            r = f*np.array([modelMgr.responseFunc.eval(xi) for xi in x])
            plt.plot(x/360, r, 'b-', linewidth=1.0)


    csv = np.genfromtxt('../ExperimentalData/FloraEtAl2011.csv', delimiter=",")
    xDat = csv[:,0]
    rDat = csv[:,1]
    plt.plot(xDat, rDat, 'ko')
    plt.axis(axis)
    plt.title(modelMgr.name())
    plt.savefig(imgName)
    plt.close()


def showSampledResponseCurves(title, imgName, responseFunc,
    limPtParams, limCycleParams, sampleIndices,
    axis = [0.0, 0.25, 0.0, 0.25]):

    #fig = plt.figure()

    nlp = len(limPtParams)
    nlc = len(limCycleParams)

    for i in sampleIndices:
        if i < nlp:
            k = i
            params = limPtParams[k]
            lineSpec = 'r-'
        else:
            k = i - nlp
            params = limCycleParams[k]
            lineSpec = 'b-'

        x = np.linspace(0,90,200)
        responseFunc.setParams(params)
        f  =1.225
        r = f*np.array([responseFunc.eval(xi) for xi in x])

        plt.plot(x/360, r, lineSpec, linewidth=0.5)

    csv = np.genfromtxt('../ExperimentalData/FloraEtAl2011.csv', delimiter=",")
    xDat = csv[:,0]
    rDat = csv[:,1]
    plt.plot(xDat, rDat, 'ko')
    plt.axis(axis)
    plt.title(title)
    lcLine = mlines.Line2D([], [], color='blue')
    lpLine = mlines.Line2D([], [], color='red')
    plt.legend([lpLine, lcLine],['Limit Point', 'Limit Cycle'])
    plt.savefig(imgName)
    plt.close()

def showSampledResponseDerivs(title, imgName, responseFunc,
    limPtParams, limCycleParams, sampleIndices,
    axis = [0.0, 0.25, 0.00, 0.05]):

    #fig = plt.figure()

    nlp = len(limPtParams)
    nlc = len(limCycleParams)

    for i in sampleIndices:
        if i < nlp:
            k = i
            params = limPtParams[k]
            lineSpec = 'r-'
        else:
            k = i - nlp
            params = limCycleParams[k]
            lineSpec = 'b-'

        x = np.linspace(0,90,600)
        responseFunc.setParams(params)
        f  =1.225
        r1 = f*np.array([responseFunc.evalDerivs(xi)[1] for xi in x])
        r2 = f*np.array([responseFunc.evalDerivs(xi)[2] for xi in x])
        plt.plot(x/360, r2, lineSpec, linewidth=0.5)
        #plt.plot(x/360, r2, lineSpec, linewidth=0.5)

    csv = np.genfromtxt('../ExperimentalData/FloraEtAl2011.csv', delimiter=",")
    xDat = csv[:,0]
    rDat = csv[:,1]
    #plt.plot(xDat, rDat, 'ko')
    #plt.axis(axis)
    plt.title(title)
    plt.savefig(imgName)
    plt.close()


def showSampleCurves(name, modelMgr, limPtParams, limCycleParams):

    fig = plt.figure()
    for p in limPtParams:
        plt.semilogy(p, 'r-')


    for p in limCycleParams:
        plt.semilogy(p, 'b-')

    plt.title(modelMgr.name())
    plt.savefig('params-%s.png' % name)
    plt.close(fig)
