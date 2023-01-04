
import copy


def mergeSettings(defaultSettings, inputSettings):

    rtn = copy.deepcopy(defaultSettings)
    
    for k in list(inputSettings.keys()):
        if k not in defaultSettings:
            raise ValueError(
                'Unknown key={badKey} in parameter dictionary {d}.\n'
                'Allowed keys are {goodKeys}'.format(
                    badKey=k,
                    d=inputSettings,
                    goodKeys=list(defaultSettings.keys())
                )
            )
        rtn[k] = inputSettings[k]
        
    return rtn
    

if __name__=='__main__':
    defaults = {"A" : 1, "B" : 2}
    inputs = {"A" : 3}
    badInputs = {"C" : 3}

    print(mergeSettings(defaults, inputs))
    print(mergeSettings(defaults, badInputs))
