#!/usr/bin/env python

import numpy as np
from SettingsHandler import *
from Logger import *
from string import *



class StoredParamSampler:



    def __init__(self,
                 modelMgr,
                 filenames,
                 sampleHandler,
                 verb = 1):
        self.modelMgr = modelMgr
        self.filenames = filenames
        self.sampleHandler = sampleHandler
        self.verb = verb

    def run(self):


        samples = 0
        runFailures = 0
        outputInterval = 10;
        verb = self.verb
        if verb > 0:
            Logger.write('Starting main sample loop')

        for filename in self.filenames:

            if verb > 0:
                Logger.write('Reading parameters from file %s' % filename)

            with open(filename) as file:

                for line in file:
                    # skip comments in the file
                    if line[0]=='#': continue

                    # get the parameters as strings
                    params = list(map(np.double, line.split()))
                    L = self.modelMgr.likelihood(params)

                    # Run the model
                    try:
                        results = self.modelMgr.run(params)
                    except (RuntimeError, ArithmeticError) as e:
                        if abortOnRunFail:
                            raise e
                        if warnOnRunFail:
                            Logger.write('StoredParamSampler Warning: run failed with error {}'.format(e))
                        runFailures += 1
                        continue

                    self.sampleHandler.process(self.modelMgr, params, results)

                    if (samples % outputInterval == 0):
                        Logger.write('sample #%d' % samples)
                        self.sampleHandler.report()

                    samples += 1


                # Done main sampling loop
                if (verb > 0):
                    Logger.write('Done main sampling loop')
                self.sampleHandler.postprocess()
