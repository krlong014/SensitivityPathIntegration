#!/usr/bin/env python

import abc
import numpy as np
import matplotlib.pyplot as plt
from math import *

class ERKStepper(metaclass=abc.ABCMeta):
    def __init__(self, p, name):
        self.p = p
        self.name = name

    @abc.abstractmethod
    def step(self, u, t, f, dt):
        pass
                 

class EulerStepper(ERKStepper):
    def __init__(self):
        ERKStepper.__init__(self, 1, 'Euler')

    def step(self, u, t, f, dt):
        uNew = u + dt*f(u, t)
        return uNew
    
class ExplicitMidpointStepper(ERKStepper):
    def __init__(self):
        ERKStepper.__init__(self, 2, 'Explicit midpoint')
        
    def step(self, u, t, f, dt):
        uMid = u + 0.5*dt*f(u, t)
        uNew = u + dt*f(uMid, t+0.5*dt)
        return uNew

class HeunStepper(ERKStepper):
    def __init__(self):
        ERKStepper.__init__(self, 2, 'Heun')
        
    def step(self, u, t, f, dt):
        K1 = f(u, t);
        uTmp = u + dt*K1
        K2 = f(uTmp, t+dt);
        uNew = u + (0.5*dt)*(K1+K2)
        return uNew

class RK4Stepper(ERKStepper):
    def __init__(self):
        ERKStepper.__init__(self, 4, 'Classic RK4')
        
    def step(self, u, t, f, dt):
        K1 = f(u, t)
        K2 = f(u+(0.5*dt)*K1, t+dt/2.0)
        K3 = f(u+(0.5*dt)*K2, t+dt/2.0)
        K4 = f(u+dt*K3, t+dt)
        return u + (dt/6.0)*(K1 + 2.0*K2 + 2.0*K3 + K4)


if __name__=='__main__':

    def fTest(u, t):
        x = u[0]
        v = u[1]
        return np.array([v, -x])

    def uExact(t):
        return np.array([cos(t), -sin(t)])

    tFinal = 6.0

    data = {
        EulerStepper() : [],
        HeunStepper() : [],
        ExplicitMidpointStepper() : [],
        RK4Stepper() : []
        }

    n = []
    steppers = [k for k,v in list(data.items())]

    for q in range(0,10):
        nSteps = 2**(q+2)
        n.append(nSteps)
        for stepper, results in list(data.items()):
            u = np.array([1,0])
            dt = tFinal/float(nSteps)
            t = 0.0
            for i in range(1,nSteps+1):
                u = stepper.step(u, t, fTest, dt)
                t = t + dt
            uEx = uExact(t)
            err = np.linalg.norm(uEx-u, np.inf)
            results.append(err)

    plt.loglog(n, data[steppers[0]], 'b-o',
               n, data[steppers[1]], 'g-s',
               n, data[steppers[2]], 'k-s',
               n, data[steppers[3]], 'r-*')
    plt.legend([steppers[0].name, steppers[1].name, steppers[2].name,
                steppers[3].name]) 

    plt.show()
    
        
