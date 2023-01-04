import numpy as np
from Logger import *
from MHSampleHandlerBase import *

class LimitPointSampleHandler(MHSampleHandlerBase):

    def __init__(self, settings) :
        MHSampleHandlerBase.__init__(self)

        self.limitPointCount = 0
        self.sampleCount = 0
        self.numLimPtCheck = settings['Num Steps To Check']
        self.limPtTol = settings['Limit Point Tolerance']
        self.verb = settings['Verbosity']
        self.limitPointParams = []
        self.limitCycleParams = []

    def preprocess(self):
        pass

    def process(self, modelMgr, params, results):

        self.sampleCount += 1

        if (self.sampleCount%100==0 and self.verb>0):
            Logger.write('limit points = %d of %d' % (self.limitPointCount, self.sampleCount))

        if True:
            if self.goingToLimitPoint(results):
                self.limitPointCount += 1
                self.limitPointParams.append(params)
            else:
                self.limitCycleParams.append(params)

        if False:
            self.limitPointParams.append(params)

    def report(self):
        Logger.write('num LP: %d, num LC: %d' %
              (len(self.limitPointParams), len(self.limitCycleParams)))



    def goingToLimitPoint(self, U):

        N = len(U)
        nCheck = min(N, self.numLimPtCheck)
        mins = np.amin(U[N-nCheck:N,:],0)
        maxes = np.amax(U[N-nCheck:N,:],0)
        diff = np.linalg.norm(maxes - mins, np.inf)

        return diff <= self.limPtTol
