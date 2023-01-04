splineResp = {
    'Type' : 'Spline',
    'Settings' : {
        'X Max' : 90.0,
        'NX Grid' : 64
    }
}

splinePropGen = {
    'Type' : 'Spline',
    'Settings' : {
        'Limiter (# sigmas)' : 5.0,
        'Filter width (# grid points)' : 4,
        'Weight for previous sample (in [0:1])' : 0.1
    }
}

tanhResp = {
    'Type' : 'Tanh'
}

ivlevResp = {
    'Type' : 'Ivlev'
}

hollingResp = {
    'Type' : 'Holling'
}

mpPropGen = {
    'Type' : 'MultiParam',
    'Sigma' : (0.1, 0.1)
}

def makeRunSettings(runName, dirName, rf, propGen, numSamples,
                    samplerParams=None):

  if samplerParams==None:
    sampler = {
        'Type' : 'MH',
        'MH Control' : {
            'Num Samples' : numSamples,
            'Burn Length' : 1000,
            'Decorrelation Length' : 5, # 200
            'Output Interval' : 50,
            'Verbosity'   : 3
        },
        'Proposal Generator' : propGen
    }
  else:
    sampler = samplerParams

  print('\n\nSampler is {}\n\n'.format(sampler))

  return {
      'Run Name' : runName,
      'Output Directory' : dirName,
      'Create Directory If Needed' : True,


      'Response Function' : rf,

      'Sampler' : sampler,

      'Response Data' : {
          'File' : '../ExperimentalData/FloraEtAl2011.csv',
          'Sigma Factor' : 2.0
      },


      'Model Manager' : {
          'Integration Time' : 1000,
          'Initial Value' : [40.0, 10.0, 40.0],
          'Num to Store' : 1000,
          'Stepper Control' : {
              'Verbosity' : 0,
              'HInit' : 0.1,
              'MaxSteps' : 100000,
              'Tolerance' : 1.0e-4,
              'Safety' : 0.9,
              'MinStepsizeFactor' : 0.001,
              'MaxStepsizeFactor' : 1000.0
          }
      },

      'Sample Handler' : {
          'Num Steps To Check' : 100,
          'Limit Point Tolerance' : 0.01,
          'Verbosity' : 0
      },

      'Visualization' : {
          'Num Curves to Show' : 100,
          'Format' : 'pdf',
          'Show Contours' : True
      }
  }
