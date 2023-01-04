#!/usr/bin/env python

import abc

###################################################################
# Base class for model management objects to be used in
# Metropolis-Hastings sampling
###################################################################

class MHModelManagerBase(metaclass=abc.ABCMeta):
    def __init__(self):
        pass
        
    # Compute likelihood of model for a given parameter set
    @abc.abstractmethod
    def likelihood(self, params):
        pass

    # Run a model with the specified parameters. This should return
    # whatever information is needed to compute this run's
    # contribution to the integral
    @abc.abstractmethod
    def run(self, params):
        pass

    
