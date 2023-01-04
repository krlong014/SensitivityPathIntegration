#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from SettingsHandler import *
from TimestepOutputManager import *
from ERK import *
from math import *





class StepDoublingDriver:
    defaults = {
        "Verbosity" : 0,      # Verbosity for diagnostic output
        "HInit" : 0.1,        # Initial stepsize as fraction of run interval
        "MaxSteps" : 100000,  # Maximum number of steps 
        "Tolerance" : 1.0e-4, # Accuracy target for run
        "Safety" : 0.9,       # Safety factor for stepsize increae
        "MinStepsizeFactor" : 0.001, # Minimum stepsize as fraction of initial
        "MaxStepsizeFactor" : 1000.0 # Maximum stepsize as fraction of initial
    }
    
    def __init__(self, stepper,
                 settings = defaults):
        self.stepper = stepper
        self.settings = mergeSettings(StepDoublingDriver.defaults, settings)

    def runStepper(self, rhsFunc, timeInterval, uInit, outMgr):
        
        t = timeInterval[0]
        tStop = timeInterval[1]
        uCur = uInit
        
        stepper = self.stepper
        p = stepper.p
        
        verb = self.settings["Verbosity"];
        dt = self.settings["HInit"];
        maxSteps = self.settings["MaxSteps"];
        tau = self.settings["Tolerance"];
        safety = self.settings["Safety"];
        minStepsizeFactor = self.settings["MinStepsizeFactor"];
        maxStepsizeFactor = self.settings["MaxStepsizeFactor"];

        step = 0
        numShrink = 0
        numGrow = 0
        numEvals = 0

        atMinStepsize = False
        atMaxStepsize = False
        minStepsize = dt * minStepsizeFactor
        maxStepsize = dt * maxStepsizeFactor

        minStepUsed = fabs(dt)
        maxStepUsed = fabs(dt)

        # Write the initial value
        outMgr.write(t, uCur)


        # Main loop
        while (t < tStop and step < maxSteps):
            if verb>=3:
                print('Step %d from t=%g to %g with h=%g', (step, t, t+dt, dt))
            if (t + dt > tStop):
                dt = tStop - t
                if verb>=3:
                    print('Timestep exceeds interval; reducing h to %g' % dt)

            if verb>=3:
                print('Doing full step and two half-steps')
            uFullStep = stepper.step(uCur, t, rhsFunc, dt)
            uMid = stepper.step(uCur, t, rhsFunc, dt/2.0)
            uTwoHalfSteps = stepper.step(uMid, t+dt/2, rhsFunc, dt/2.0)
            errEst = np.linalg.norm(uFullStep - uTwoHalfSteps, np.inf);
            numEvals += 3

            # Estimate new stepsize
            dtNew = dt
            if errEst<tau:
                if errEst==0.0: # deal with occasional division by zero
                    dtNew = dt*pow(0.5, 1.0/(p+1))
                dtNew = dt*pow(tau/errEst, 1.0/(p+1));
            else:
                dtNew = dt*pow(tau/errEst, 1.0/p);

            if (dtNew<dt and not atMinStepsize):
                if safety*dtNew <= minStepsize:
                    dt = minStepsize
                    atMinStepsize = True
                else:
                    dt = safety*dtNew
                atMaxStepsize = False
                if verb>=3:
                    print('Reducing stepsize to h=%g' % dt)
                numShrink+=1
                continue # Don't accept step; try again with smaller stepsize

            # If we've made it to this point, the step is good

            # Decide whether to write the step
            wroteStep = False
            while outMgr.needToWrite(t, dt):
                # Interpolate to the writing time
                tn0 = t
                tn1 = t+dt/2.0
                tn2 = t+dt
                tnw = outMgr.tNextWrite
                phi0 = (tnw-tn1)*(tnw-tn2)/(tn0-tn1)/(tn0-tn2)
                phi1 = (tnw-tn0)*(tnw-tn2)/(tn1-tn0)/(tn1-tn2)
                phi2 = (tnw-tn1)*(tnw-tn0)/(tn2-tn1)/(tn2-tn0)
                uWrite = uCur*phi0 + uMid*phi1 + uTwoHalfSteps*phi2
                
                outMgr.write(tnw, uWrite)
                wroteStep = True

            minStepUsed = min(minStepUsed, fabs(dt))
            maxStepUsed = max(maxStepUsed, fabs(dt))

            uCur = np.copy(uTwoHalfSteps)

            t += dt
            step += 1

            # Write final step if necessary
            if t==tStop and outMgr.needToWrite(t, dt) and not wroteStep:
                outMgr.write(t, uCur)
                

            if (t<tStop and fabs(dtNew) > fabs(dt) and not atMaxStepsize):
                if fabs(dtNew) >= maxStepsize:
                    atMaxStepsize = True
                    dt = maxStepsize
                else:
                    dt = dtNew
                atMinStepsize = False
                numGrow += 1
        # Done timestepping loop!


        if verb>=2:
            print('Done time integration')
            print('\tFinal time           %g' % t)
            print('\tNum steps            %d' % step)
            print('\tMin stepsize used    %g' % minStepUsed)
            print('\tMax stepsize used    %g' % maxStepUsed)
            print('\tNumber of func evals %d' % numEvals)
            print('\tNum step decrease    %d' % numShrinks)
            print('\tNum step increase    %d' % numGrow)

        stat = {
            'NSteps' : step,
            'NEval'  : numEvals
            }

        return stat

    
            
    
    



if __name__=='__main__':

    def fTest(u, t):
        x = u[0]
        v = u[1]
        return np.array([v, -x])

    def uExact(t):
        return np.array([cos(t), -sin(t)])

    epsVals = (1.0e-4, 1.0e-5, 1.0e-6, 1.0e-7, 1.0e-8, 1.0e-9, 1.0e-10)
    errVals = []
    nStepVals = []
    
    for eps in epsVals:
        tInit = 0.0
        tFinal = 5.0;
        nReport = 10
        uInit = [1.0, 0.0]

        stepSettings = {"Tolerance" : eps}
        driver = StepDoublingDriver(HeunStepper(), stepSettings)
        outMgr = NPStorageOutputManager([tInit, tFinal], uInit, nReport)
        
        stat = driver.runStepper(fTest, [tInit, tFinal], uInit, outMgr)

        for i in range(0, nReport+1):
            print(outMgr.tVals[i,0], outMgr.uStore[i,:]) 
        
        err = np.linalg.norm(uExact(outMgr.tVals[nReport,0])-outMgr.uStore[nReport,:], np.inf)

        nStepVals.append(stat['NSteps'])

        errVals.append(err)

    print(errVals)
    
    plt.loglog(nStepVals, errVals, 'k-o', nStepVals, epsVals, 'b-s')
    plt.show()



     
        


    

    
    
