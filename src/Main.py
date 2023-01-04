#import matplotlib
#matplotlib.use('Agg')

from SplineResponseFunction import *
#from FEMResponseFunction import *
from ChemostatModelMgr import *
from LimitPointSampleHandler import *
from ResponseData import *
#from FEMProposalGenerator import *
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
        filenameTemplates = samplerSpec['Filenames']
        filenames = []
        rfName = rfSettings['Type']
        for t in filenameTemplates:
            filenames.append(t % (rfName, rfName))
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









if __name__ == '__main__':

  import argparse

  parser = argparse.ArgumentParser(description='sampling')
  parser.add_argument('--stored', action='store', default=None)
  parser.add_argument('--nx', action='store', type=int, default=64)
  parser.add_argument('--dir', action='store', default='../Results/Spline-Runs')
  parser.add_argument('--dryrun', action='store_true', default=False)

  args = parser.parse_args()
  storedSampleTag = args.stored
  storedSampleDir = args.dir
  isDryRun = args.dryrun
  Nx = args.nx


  now = datetime.now()
  dateStr = now.strftime('%Y-%d-%b-%f')
  labelStr = 'Sample-%s-%s-%s' % (getuser(), gethostname(), dateStr)
  outfileTemplate = '../Results/Spline-Runs/%%s-%s' % labelStr
  print(outfileTemplate)
  numSamples = 10000

  for r in (('Spline', splineResp, splinePropGen),):
      print('r=', r)
      modelName = r[0]
      outfile = outfileTemplate % modelName
      resp = r[1]
      propGen = r[2]
      print('propGen=', propGen)
      settings = makeRunSettings(modelName, outfile, resp, propGen,
                                numSamples)



      for D in (0.05,): #np.arange(0.03, 0.1001, 0.0025):
          print('D=%g' % D)
          if not isDryRun:
              runSampler(settings, D, Nx)
