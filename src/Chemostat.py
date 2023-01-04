#!/usr/bin/env python

from StepDoublingDriver import *
from TimestepOutputManager import *
from math import *
from ResponseFunction import *
import numpy as np
import matplotlib.pyplot as plt




class Chemostat:
    def __init__(self, response, D=0.05):
        self.g = response
        self.D = D # 0.05
        self.Xin = 130.0
        self.e1 = 0.3
        self.e2 = 1.2
        self.vMax = 1.6
        self.k = 16.0

    def f(self, x):
        return self.vMax*x/(self.k + x)

    def RHS(self, u):
        x = u[0]
        y = u[1]
        z = u[2]
        D = self.D
        e1 = self.e1
        e2 = self.e2
        Xin = self.Xin

        fOfX = self.f(x)
        gOfY = self.g.eval(y)

        fx = D*(Xin - x) - fOfX*y
        fy = e1*fOfX*y - gOfY*z - D*y
        fz = e2*gOfY*z - D*z

        return np.array([fx,fy,fz])


    def run(self, driver, nReport, tInit, tFinal, u0):

        outMgr = NPStorageOutputManager([tInit, tFinal], u0, nReport)

        def f(y, t):
            return self.RHS(y)

        stat = driver.runStepper(f, [tInit, tFinal], u0,  outMgr)

        return outMgr.uStore

def goingToLimitPoint(U, nCheck, tol):

    N = len(U)
    mins = np.amin(U[N-nCheck:N,:],0)
    maxes = np.amax(U[N-nCheck:N,:],0)
    diff = np.linalg.norm(maxes - mins, np.inf)

    return diff <= tol




if __name__=='__main__':

    # Initial conditions for chemostat
    u0 = np.array([40.0, 10.0, 40.0])

    tInit = 0.0
    tFinal = 1600.0
    nReport = 1600

    driver = StepDoublingDriver(HeunStepper())

    T = np.linspace(0, tFinal, nReport+1)
    Ut = Chemostat(TanhModel()).run(driver, nReport, tInit, tFinal, u0)
    Uh = Chemostat(HollingModel()).run(driver, nReport, tInit, tFinal, u0)
    Ui = Chemostat(IvlevModel()).run(driver, nReport, tInit, tFinal, u0)

    print('Ut size=', Ut.shape)


    if goingToLimitPoint(Ut, 100, 0.5):
        print('Tanh model approaches limit point')
    else:
        print('Tanh model does not approach limit point')

    if goingToLimitPoint(Uh, 100, 0.5):
        print('Holling model approaches limit point')
    else:
        print('Holling model does not approach limit point')

    if goingToLimitPoint(Ui, 100, 0.5):
        print('Ivlev model approaches limit point')
    else:
        print('Ivlev model does not approach limit point')


    # plt.figure(1)
    # plt.plot(Ut[:,1],Ut[:,2],'g', Uh[:,1],Uh[:,2], 'r', Ui[:,1], Ui[:,2],'b')
    # plt.legend(['tanh', 'Holling', 'Ivlev'])
    # plt.xlabel('y')
    # plt.ylabel('z')
    # plt.savefig('baselineModelPhase.png')
    #
    # plt.figure(2)
    # plt.plot(T, Ut[:,2],'g', T, Uh[:,2], 'r', T, Ui[:,2],'b')
    # plt.legend(['tanh', 'Holling', 'Ivlev'])
    # plt.xlabel('time (hour)')
    # plt.ylabel('z')
    # plt.savefig('baselineModelTime.png')



    x = np.linspace(0,90,200)
    mh = HollingModel()
    mi = IvlevModel()
    mt = TanhModel()
    f = 1.225
    rh = f*np.array([mh.eval(xi) for xi in x])
    ri = f*np.array([mi.eval(xi) for xi in x])
    rt = f*np.array([mt.eval(xi) for xi in x])

    csv = np.genfromtxt('../ExperimentalData/FloraEtAl2011.csv', delimiter=",")
    xDat = csv[:,0]
    rDat = csv[:,1]

    plt.plot(x/360, rt, 'g-', x/360, rh, 'r-', x/360, ri, 'b-', xDat, rDat, 'ko')
    plt.axis([0, 0.25, 0, 0.25])
    plt.legend(['tanh', 'Holling', 'Ivlev'])
    plt.ylabel('predator response $g(y)$')
    plt.xlabel('prey density $y$')
    plt.savefig('baselineModelResponse.png')


    # ax=plt.figure().add_subplot(projection='3d')
    # ax.view_init(20,30)
    # ax.plot(Ut[:,0],Ut[:,1],Ut[:,2], 'g', linewidth=0.5)
    # ax.plot(Uh[:,0],Uh[:,1],Uh[:,2], 'r', linewidth=0.5)
    # ax.plot(Ui[:,0],Ui[:,1],Ui[:,2], 'b', linewidth=0.5)
    # ax.legend(['tanh', 'Holling', 'Ivlev'])
    # plt.savefig('baselineModel3D.pdf')

    plt.close('all')

    fig, ax = plt.subplots(1,3)

    ax[0].plot(Ut[:,1],Ut[:,2], 'g', linewidth=1)
    ax[0].axis([0, 30, 10, 50])
    ax[0].legend(['tanh'])
    ax[0].set_aspect('equal')
    ax[0].set_xlabel('y')
    ax[0].set_ylabel('z')
    #ax[0,1].savefig('baselineTanh.pdf')


    ax[1].plot(Uh[:,1],Uh[:,2], 'r', linewidth=1)
    ax[1].axis([0, 30, 10, 50])
    ax[1].legend(['Holling'])
    ax[1].set_aspect('equal')
    ax[1].set_xlabel('y')
    #ax[1,0].xlabel('y')
    #ax[1,0].ylabel('z')
    #ax[1,0].savefig('baselineHolling.pdf')

    ax[2].plot(Ui[:,1],Ui[:,2], 'b', linewidth=1)
    ax[2].axis([0, 30, 10, 50])
    ax[2].legend(['Ivlev'])
    ax[2].set_aspect('equal')
    ax[2].set_xlabel('y')
    #ax[1,1].xlabel('y')
    #ax[1,1].ylabel('z')
    #ax[1,1].savefig('baselineIvlev.pdf')

    plt.savefig('baselineModels.pdf')
