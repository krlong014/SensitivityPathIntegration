#!/usr/bin/env python

import abc

###################################################################
# Base class for sample handling objects to be used in 
# Metropolis-Hastings sampling. 
###################################################################

class MHSampleHandlerBase(metaclass=abc.ABCMeta):
    def __init__(self):
        pass
        
    # Callback for optional pre-processing step. Default
    # implementation is a no-op
    def preprocess(self, modelMgr):
        pass

    # Process the results of a sample run
    @abc.abstractmethod
    def process(self, modelMgr, params, results):
        pass

    # Callback for optional post-processing step. Default
    # implementation is a no-op
    def postprocess(self):
        pass

    
