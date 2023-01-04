#!/usr/bin/env python

import abc
import numpy as np
import matplotlib.pyplot as plt
from ERK import *
from math import *


class TimestepOutputManager(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def needToWrite(self, t, dt):
        pass
        
    
class StdOutOutputManager(TimestepOutputManager):

    def __init__(self, timeInterval, uInit, nReport):
        TimestepOutputManager.__init__(self)
        
        self.nReport = nReport
        self.writeInterval = (timeInterval[1]-timeInterval[0])/nReport
        self.writeIndex = 0
        self.tNextWrite = timeInterval[0]

    def needToWrite(self, t, dt):
        return self.tNextWrite >= t and self.tNextWrite <= t+dt
        
    def write(self, t, u):
        print(('{time} {vals}'.format(time=t, vals=u)))
        self.writeIndex += 1
        self.tNextWrite += self.writeInterval

class NPStorageOutputManager(TimestepOutputManager):
    def __init__(self, timeInterval, uInit, nReport):
        TimestepOutputManager.__init__(self)
        self.nReport = nReport
        self.writeInterval = (timeInterval[1]-timeInterval[0])/nReport
        self.writeIndex = 0
        self.tNextWrite = timeInterval[0]
        self.uStore = np.zeros((nReport+1, len(uInit)))
        self.tVals = np.zeros((nReport+1, 1))

    def needToWrite(self, t, dt):
        return self.tNextWrite >= t and self.tNextWrite <= t+dt
        
    def write(self, t, u):
        self.uStore[self.writeIndex,:]=u
        self.tVals[self.writeIndex]=t
        self.writeIndex += 1
        self.tNextWrite += self.writeInterval

     
        


    

    
    
