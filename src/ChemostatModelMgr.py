
import numpy as np
from MHModelManagerBase import *
from Chemostat import *

class ChemostatModelMgr(MHModelManagerBase):

    # Constructor
    def __init__(self, responseFunc, responseData, runSettings, D):
        MHModelManagerBase.__init__(self),
        self.responseFunc = responseFunc
        self.responseData = responseData
        self.runSettings = runSettings
        self.chemostat = Chemostat(self.responseFunc, D)

    # Return name of model
    def name(self):
        return self.responseFunc.name()

    # Compute likelihood of model for a given parameter set
    def likelihood(self, params):
        self.responseFunc.setParams(params)
        return self.responseData.likelihood(self.responseFunc)


    # Run a model with the specified parameters. This should return
    # whatever information is needed to compute this run's
    # contribution to the integral
    def run(self, params):

        tInit = 0.0
        tFinal = self.runSettings["Integration Time"]
        nReport = self.runSettings["Num to Store"]
        uInit = self.runSettings["Initial Value"]

        stepperControl = self.runSettings['Stepper Control']

        driver = StepDoublingDriver(HeunStepper(), stepperControl)

        return self.chemostat.run(driver, nReport, tInit, tFinal, uInit)
