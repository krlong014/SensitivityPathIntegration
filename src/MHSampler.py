#!/usr/bin/env python

import numpy as np
from SettingsHandler import *
from Logger import *
from string import *



class MHSampler:
    defaultSettings = {
        'Num Samples' : 100,
        'Burn Length' : 100,
        'Decorrelation Length' : 10,
        'Output Interval' : 10,
        'Warning on Proposal Failure' : True,
        'Abort on Proposal Failure' : False,
        'Warning on Run Failure' : True,
        'Abort on Run Failure' : False,
        'Verbosity' : 2
        }

    def __init__(self,
                 modelMgr,
                 proposalGenerator,
                 sampleHandler,
                 settings):
        self.modelMgr = modelMgr
        self.proposalGenerator = proposalGenerator
        self.sampleHandler = sampleHandler
        self.settings = mergeSettings(MHSampler.defaultSettings, settings)

    def run(self):
        numSamples = self.settings['Num Samples']
        burnLength = self.settings['Burn Length']
        decorLength = self.settings['Decorrelation Length']
        outputInterval = self.settings['Output Interval']
        warnOnPropFail = self.settings['Warning on Proposal Failure']
        warnOnRunFail = self.settings['Warning on Run Failure']
        abortOnPropFail = self.settings['Abort on Proposal Failure']
        abortOnRunFail = self.settings['Abort on Run Failure']
        verb = self.settings['Verbosity']

        # Get initial value of model parameters
        fInit = self.proposalGenerator.getInit()
        fPrev = np.copy(fInit)

        # Compute likelihood function for initial parameters
        LPrev = self.modelMgr.likelihood(fPrev)

        # Do any preprocessing needed by the sample handler
        self.sampleHandler.preprocess()

        # Burn-in step: ignore an initial batch of accepted samples
        if verb > 0:
            Logger.write('Starting burn-in phase with burnLength=%d' % burnLength)
        burns = 0
        rejects = 0
        propFailures = 0
        while burns < burnLength:
            # Have the model manager generate new model parameters
            fCur = self.proposalGenerator.proposal(fPrev)

            try:
                LCur = self.modelMgr.likelihood(fCur)
            except (RuntimeError, ArithmeticError) as e:
                if abortOnPropFail:
                    raise RuntimeError('MHSampler: proposal failed with error {}'.format(e))
                if warnOnPropFail:
                    Logger.write('MHSampler warning: Likelihood calculation failed with error {}'.format(e))
                fPrev = np.copy(fCur)
                propFailures += 1
                continue

            # Decide whether this is an acceptable step
            m = LCur/LPrev
            if np.random.random() < m:
                # Sample would have been accepted had we not been in burn phase
                burns += 1
                LPrev = LCur
                fPrev = np.copy(fCur)
            else:
                # Sample rejected as burn
                rejects += 1

        if verb > 0:
            Logger.write('Burn in phase done: burns=%d, rejects=%d, failures=%d'
                  % (burns, rejects, propFailures))

        # Main sampling loop:

        samples = 0
        totRejects = 0
        curRejects = 0
        propFailures = 0
        runFailures = 0
        if verb > 0:
            Logger.write('Starting main sample loop with numSamples=%d' % numSamples)

        while samples < numSamples:

            # Skip a number of good samples to reduce correlations
            skipped = 0
            curRejects = 0
            while skipped < decorLength:
                # Have the model manager generate new model parameters
                fCur = self.proposalGenerator.proposal(fPrev)

                try:
                    LCur = self.modelMgr.likelihood(fCur)
                except (RuntimeError, ArithmeticError) as e:
                    if abortOnPropFail:
                        raise RuntimeError('MHSampler: proposal failed with error {}'.format(e))
                    if warnOnPropFail:
                        Logger.write('MHSampler Warning: Likelihood calculation failed with error {}'.format(e))
                    fPrev = np.copy(fCur)
                    propFailures += 1
                    continue

                # Decide whether this is an acceptable step
                m = LCur/LPrev
                if np.random.random() < m:
                    # Accept sample for skipping
                    skipped += 1
                    LPrev = LCur
                    fPrev = np.copy(fCur)
                else:
                    # Reject sample
                    curRejects += 1
                    totRejects += 1

            # Run the model for this sample

            try:
                results = self.modelMgr.run(fCur)
            except (RuntimeError, ArithmeticError) as e:
                if abortOnRunFail:
                    raise e
                if warnOnRunFail:
                    Logger.write('MHSampler Warning: run failed with error {}'.format(e))
                runFailures += 1
                continue


            self.sampleHandler.process(self.modelMgr, fCur, results)

            if (samples % outputInterval == 0):
                Logger.write('sample #%d, cur rejects=%d tot rejects=%d'
                      % (samples, curRejects, totRejects))
                self.sampleHandler.report()

            samples += 1


        # Done main sampling loop
        if (verb > 0):
            Logger.write('Done main sampling loop')
        self.sampleHandler.postprocess()
