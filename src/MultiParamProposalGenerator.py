#!/usr/bin/env python

import numpy as np
from ResponseFunction import *
from math import *


class MultiParamProposalGenerator:
    def __init__(self, resp, delta):

        params = resp.getParams();
        d = np.array(delta)
        self.sig = np.log(np.abs(1.0+d)/np.abs(1.0-d));
        self.initParams = np.array(params)

    def proposal(self, fParams):
        logf = np.log(fParams) + np.random.normal(0, self.sig)
        return np.exp(logf)

    def getInit(self):
        return self.initParams

