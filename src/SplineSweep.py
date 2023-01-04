#import matplotlib
#matplotlib.use('Agg')

from mpi4py import MPI
from Boss import *
from Worker import *
from Task import *
import logging
from SplineResponseFunction import *
from ChemostatModelMgr import *
from LimitPointSampleHandler import *
from ResponseData import *
from SplineProposalGenerator import *
from MultiParamProposalGenerator import *
from MHSampler import *
from StoredParamSampler import *
from ShowResponseCurves import *
from ShowContours import *
from Logger import *
from DefaultSettings import *
from socket import gethostname
from getpass import getuser
from datetime import *
from time import strftime
import time
import numpy as np

import os




def runSampler(settings, D, Nx=32):

    name = settings['Run Name']
    dirname = settings['Output Directory']

    if not os.path.exists(dirname):
        if settings['Create Directory If Needed']:
            os.makedirs(dirname)
        else:
            raise RuntimeError('Directory %s does not exist: aborting'
                               % dirName)

    logName = '%s/%s-n-%d-D-%f.log' % (dirname, name, Nx, D)

    Logger.openLog(logName, settings)

    # Set up response function
    rfSettings = settings['Response Function']
    if rfSettings['Type']=='Spline':
        rFunc = SplineResponseFunction(
            rfSettings['Settings']['X Max'],
            Nx)
            #rfSettings['Settings']['NX Grid'])
    elif rfSettings['Type'] == 'Tanh':
        rFunc = TanhModel()
    elif rfSettings['Type'] == 'Ivlev':
        rFunc = IvlevModel()
    elif rfSettings['Type'] == 'Holling':
        rFunc = HollingModel()
    else:
        raise RuntimeError('Unimplemented Response function %s' % rfSettings['Type'])

    # Set up response function experimental data set
    rData = ResponseData(settings['Response Data'])

    # Set up chemostat model manager
    modelMgr = ChemostatModelMgr(rFunc, rData,
                                 settings['Model Manager'], D)

    # Set up sample handler
    sampleHandler = LimitPointSampleHandler(settings['Sample Handler'])

    # Set up sampler
    samplerSpec = settings['Sampler']
    if samplerSpec['Type']=='MH': # Metropolis-Hastings sampler
        # Set up proposal generator
        pgSettings = samplerSpec['Proposal Generator']
        print(('found propgen type=%s' % pgSettings['Type']))
        if pgSettings['Type']=='Spline':
            propGen = SplineProposalGenerator(rFunc, pgSettings['Settings'])
        elif pgSettings['Type']=='MultiParam':
            propGen = MultiParamProposalGenerator(rFunc, pgSettings['Sigma'])
        else:
            raise RuntimeError('Unimplemented proposal generator %s' % pgSettings['Type'])

        # Set up sampler
        sampler = MHSampler(modelMgr, propGen, sampleHandler,
                            samplerSpec['MH Control'])
    elif samplerSpec['Type']=='Stored':
        filenames = samplerSpec['Filenames']
        sampler = StoredParamSampler(modelMgr, filenames, sampleHandler)
    else:
        pass

    # Go!!!!

    print('settings=', settings)

    sampler.run()

    nlp = sampleHandler.limitPointCount
    nlc = sampleHandler.sampleCount - sampleHandler.limitPointCount

    Logger.write('-- Results ---------------------------------------------\n')
    Logger.write('\tname=%s D=%f' % (name, D))
    Logger.write('\t\tNumber of limit points: %d' % nlp)
    Logger.write('\t\tNumber of limit cycles: %d' % nlc)
    Logger.write('\n\n')

    lpp = sampleHandler.limitPointParams
    lcp = sampleHandler.limitCycleParams

    numToShow = settings['Visualization']['Num Curves to Show']
    imgFormat = settings['Visualization']['Format']
    doContours = settings['Visualization']['Show Contours']
    if True or rfSettings['Type']=='Spline':
        doContours = False

    showCurves = False
    if showCurves==True:
        imgName = '%s/response-%s.%s' % (dirname, name, imgFormat)
        showResponseCurves(name, imgName, modelMgr, lpp, lcp, numToShow)
    if doContours==True:
        imgName = '%s/contour-%s.%s' % (dirname, name, imgFormat)
        showContours(imgName, modelMgr, lpp, lcp)

    dumpParams = True
    if dumpParams==True:
        np.savetxt('%s/limitPointParams-%s-nx-%d-D-%f.csv' % (dirname, name, Nx, D),
                   np.array(lpp),
                   header=' Limit Point Parameters from run logged in %s'
                   % logName)
        np.savetxt('%s/limitCycleParams-%s-nx-%d-D-%f.csv' % (dirname, name, Nx, D),
                   np.array(lcp),
                   header=' Limit Cycle Parameters from run logged in %s'
                   % logName)

    Logger.closeLog()

    return (nlp, nlc)




class RunnerFunction(Task.Function):

    def __init__(self, rank, dirName, dryRun=False):
        self.rank = rank
        self.dirName = dirName
        self.dryRun = dryRun

    def run(self, arg):

        storedSampleDir = '../Results/Spline-Runs/Spline-N-64/'
        storedSampleTag = 'Spline-nx-64-D-0.050000'
        storedSampleFiles = (
            storedSampleDir+'limitCycleParams-%s.csv' % storedSampleTag,
            storedSampleDir+'limitPointParams-%s.csv' % storedSampleTag
            )

        samplerSettings = {
            'Type' : 'Stored',
            'Filenames' : storedSampleFiles
            }


        responseFunc = splineResp
        propGen = splinePropGen
        Nx = 64
        numSamples = 10000

        name = 'Spline'
        settings = makeRunSettings(name, self.dirName, responseFunc,
            propGen, numSamples, samplerSettings)

        D = arg

        if not self.dryRun:
            nlp, nlc = runSampler(settings, D, Nx)
            return True
        else:
            logName = '%s/%s-n-%d-D-%f.log' % (self.dirName, name, Nx, D)
            Logger.openLog(logName, 'Dummy run on proc %d' % self.rank, stdOut=False)
            Logger.write(settings)
            time.sleep(60*np.random.default_rng().random())
            return True

class EmptyAnalyzer(Task.ResultAnalyzer):
    def __init__(self):
        super().__init__()

    def acceptResult(self, result):
        pass


    def postprocess(self):
        pass



if __name__ == '__main__':


    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    logLevel = logging.INFO

    # Generate a date-based label for the output directory. Since this
    # label will depend on the clock time to the second, run on the
    # boss and broadcast to the workers so that everyone gets the same
    # label.
    labelStr = ''
    if rank==0:
        now = datetime.now()
        dateStr = now.strftime('%Y-%d-%b-%f')
        labelStr = 'Sample-%s-%s-%s' % (getuser(), gethostname(), dateStr)

    labelStr = comm.bcast(labelStr, root=0)

    dirName = '../Results/Spline-Runs/D-Sweep/Spline-' + labelStr
    os.makedirs(dirName, exist_ok = True)

    if rank==0:
        args = [D for D in np.arange(0.03, 0.1001, 0.0025)]
        analyzer = EmptyAnalyzer()
        boss = Boss(args, analyzer, comm=comm, logLevel=logLevel)
        boss.loop()
        analyzer.postprocess()
    else:
        f = RunnerFunction(rank, dirName, dryRun=False)
        worker = Worker(f, comm=comm, logLevel=logLevel)
        worker.loop()
