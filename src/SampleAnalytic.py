#!/usr/bin/env python

# Results from 3 July 2019:
# {
# 'Ivlev': [4804, 5196],
# 'Holling': [3070, 6930],
# 'Tanh': [6724, 3276]
# }
# Results from 5 July 2019
# {'Combination': [6617, 3383]}

from ResponseFunction import *
from ChemostatModelMgr import *
from LimitPointSampleHandler import *
from ResponseData import *
from MultiParamProposalGenerator import *
from MHSampler import *

#models = (TanhModel(), IvlevModel(), HollingModel())
models = (CombinationModel(),)


def sampleResponseCurves():

    figNum = 1
    showRCurves = False
    showContours = False;

    results = {}

    for respFunc in models:

        propGen = MultiParamProposalGenerator(respFunc, [0.2, 0.2, 0.2, 0.2, 0.2, 0.2])
        print('sigma = ', propGen.sig)

        respData = ResponseData()

        modelMgr = ChemostatModelMgr(respFunc, respData)

        sampleHandler = LimitPointSampleHandler()

        sampler = MHSampler(modelMgr, propGen, sampleHandler)

        sampler.run()

        nlp = sampleHandler.limitPointCount
        nlc = sampleHandler.sampleCount - sampleHandler.limitPointCount
        results[respFunc.name()] = [nlp, nlc]
        

        if showRCurves:
            showResponseCurves(figNum, modelMgr,
                               sampleHandler.limitPointParams,
                               sampleHandler.limitCycleParams)
            figNum += 1

        if showContours:
            showContours(figNum, modelMgr,
                               sampleHandler.limitPointParams,
                               sampleHandler.limitCycleParams)
            figNum += 1

    
    print(results)
        




def showResponseCurves(figNum, modelMgr, limPtParams, limCycleParams, imgName):

    respFunc = modelMgr.responseFunc
    plt.figure(figNum)
    
    for p in limPtParams:
        x = np.linspace(0,90,200)
        respFunc.setParams(p)
        f  =1.225
        r = f*np.array([respFunc.eval(xi) for xi in x])
        plt.plot(x/360, r, 'r-')


    for p in limCycleParams:
        x = np.linspace(0,90,200)
        respFunc.setParams(p)
        f  =1.225
        r = f*np.array([respFunc.eval(xi) for xi in x])
        plt.plot(x/360, r, 'b-')

    csv = np.genfromtxt('../ExperimentalData/FloraEtAl2011.csv', delimiter=",")
    xDat = csv[:,0]
    rDat = csv[:,1]
    plt.plot(xDat, rDat, 'ko')
    plt.axis([0, 0.1, 0, 0.1])
    plt.title(respFunc.name())
    plt.savefig('response-%s.png' % respFunc.name())
    plt.close()



    

def showContours(imgName, modelMgr, limPtParams, limCycleParams):

    na = 100
    nb = 100

    aMin = 0.001
    aMax = 0.025

    bMin = 0.001
    bMax = 0.3
    
    
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
    if LC.shape[0]>0: plt.plot(LC[:,0], LC[:,1], 'ks', markersize=2)
    plt.savefig(imgName)
    plt.close()
            
                             
if __name__ == '__main__':
    sampleResponseCurves()
