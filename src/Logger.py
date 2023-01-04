from socket import gethostname
from getpass import getuser
from datetime import *
from time import strftime
import string
import pprint

class Logger:
    file = None
    stdOut = True

    @classmethod
    def openLog(cls, name='run', inputs=None, stdOut=True):
        cls.file = open('%s' % name, 'w')
        cls.stdOut = stdOut
        cls.ppf = pprint.PrettyPrinter(indent=2, stream=cls.file)
        cls.pps = pprint.PrettyPrinter(indent=2)
        t = datetime.utcnow().strftime('%d-%m-%Y-%H:%M:%S.%f')
        cls.write('# Run at UTC %s' % t)
        cls.write('# By user %s' % getuser())
        cls.write('# On host %s' % gethostname())
        if inputs != None:
            cls.ppf.pprint(inputs)
            if stdOut:
                cls.pps.pprint(inputs)
        cls.file.flush()

    @classmethod
    def write(cls, x):
        if isinstance(x, str):
            cls.file.write(x + '\n')
            if cls.stdOut:
                print(x)
        else:
            cls.ppf.pprint(x)
            if cls.stdOut:
                cls.pps.pprint(x)
        cls.file.flush()


    @classmethod
    def closeLog(cls):
        cls.file.close()

if __name__=='__main__':
    Logger.openLog('testLog', {'A' : 5.0})
    Logger.write('logging a step')
    Logger.write([0,1,2,3])
    d = {
        'A':1, 'B':2, 'C':3
        }
    Logger.write(d)
    Logger.closeLog()
