#!/usr/bin/env python


from math import *
import numpy as np
import matplotlib.pyplot as plt


class SplineSolver:
    def __init__(self, xMax, nx):

        #
        self.xMax = xMax

        # N is the number of nodes. There are then N-1 intervals.
        self.N = nx

        # h is the interval size
        self.h = xMax/float(nx-1)

        # c is the vector of spline coefficients.
        self.c = np.zeros(4*(self.N-1))

    def solve(self, wDat):

        N = self.N
        h = self.h
        c = self.c

        # There are N nodes, numbered 0 to N-1.
        # There are N-1 intervals, numbered 0 to N-2.

        # Use BC at 0 to set c_0 in first interval
        c[0] = 0


        # First pass to compute c_2 and c_3
        for i in range(0,N-1):
            a0 = wDat[i]
            a1 = wDat[i+1]-wDat[i]
            c[4*i+2] = -(h*h/2.0)*a0
            c[4*i+3] = -(h*h/6.0)*a1


        # Use BC at N*h to compute c_1 at interval N-2
        c[4*(N-2)+1] = -2.0*c[4*(N-2)+2] - 3.0*c[4*(N-2)+3]

        # Second pass to compute c_1 at intervals (N-2) to 0
        for i in range(N-3,-1,-1):
            c[4*i+1] = c[4*(i+1)+1] - 2*c[4*i+2] - 3*c[4*i+3]


        # Final pass to compute c_0 at intervals 1 to N-2
        for i in range(0,N-2):
            c[4*(i+1)] = c[4*i] + c[4*i+1] + c[4*i+2] + c[4*i+3]

#        print c



    def isInInterval(self, a, b, x):
        if x>=a and x<=b:
            return True
        return False

    def locatePoint(self, x):

        h = self.h
        n = self.N

        if x < 0:
            return -1
        if x > n*h:
            return self.N

        low = 0
        high = self.N
        while high-low > 1:
            mid = (high+low)/2
            if x >= mid*h:
                low=mid
            else:
                high=mid
        return low

    def interpolate(self, x):

        i = int(self.locatePoint(x))
        #print (x,i)
        if i<0:
            return 0


        if i>=(self.N-1):
            C = self.c[4*(self.N-2):4*(self.N-2)+4]
#            print C
            return C[0] + C[1] + C[2] + C[3]

        t = (x-i*self.h)/self.h

        C = self.c[4*i:4*i+4]
#        print C
        return C[0] + t*(C[1] + t*(C[2] + t*C[3]))

    def interpolateDerivs(self, x):

        i = int(self.locatePoint(x))
        #print (x,i)
        if i<0:
            return (0,0,0)


        if i>=(self.N-1):
            C = self.c[4*(self.N-2):4*(self.N-2)+4]
#            print C
            return (C[0] + C[1] + C[2] + C[3], 0, 0)

        t = (x-i*self.h)/self.h

        C = self.c[4*i:4*i+4]
#        print C
        return (C[0] + t*(C[1] + t*(C[2] + t*C[3])),
                (C[1] + t*(2*C[2] + t*3*C[3]))/self.h,
                (2*C[2] + t*6*C[3])/self.h/self.h
                )

    def deriv2(self, x):

        i = self.locatePoint(x)
        if i<0:
            return 0

        if i>=(self.N-1):
            return 0

        t = (x-i*self.h)/self.h

        C = self.c[4*i:4*i+4]
        return (6.0*t*C[3] + 2.0*C[2])/self.h/self.h

    def deriv1(self, x):

        i = self.locatePoint(x)
        if i<0:
            return 0

        if i>=(self.N-1):
            return 0

        t = (x-i*self.h)/self.h

        C = self.c[4*i:4*i+4]
#        print (t, C, C[1], 3.0*t*t*C[3], C[1]+3.0*t*t*C[3])
        return (C[1] + t*(2.0*C[2] + t*3.0*C[3])) /self.h



    def linInterp(self, wDat, x):

        i = self.locatePoint(x)
        if i<0:
            return 0

        if i>=(self.N-1):
            return 0

        x0 = i*self.h
        x1 = (i+1)*self.h
        return (x-x0)/self.h*wDat[i+1] - (x-x1)/self.h*wDat[i]



    def tabulateVals(self, xVals):
        y = np.zeros(len(xVals))

        for i in range(0,len(xVals)):
            y[i]=self.interpolate(xVals[i])
        return y


if __name__=='__main__':


    xMax = pi/2

    print('{', end=' ')

    pMax = 10
    for p in range(2,pMax):
        nx = 2**p
        r = SplineSolver(xMax, nx)
        X = [i*xMax/(nx-1) for i in range(0,nx)]
        w = np.array([sin(x) for x in X])

        r.solve(w)

        nVals = 1000
        x = np.linspace(0.0, xMax, nVals)
        z = np.copy(x)
        z1 = np.copy(x)
        z2 = np.copy(x)
        zEx = [-sin(t) for t in x]
        f2 = [r.linInterp(w, t)+0.01 for t in x]

        for i in range(len(x)):
            z[i] = r.interpolate(x[i])
            z2[i] = r.deriv2(x[i])
            z1[i] = r.deriv1(x[i])


        print('{%d, %20.15f}' % (nx, np.linalg.norm(z-zEx,np.inf)), end=' ')
        if p<pMax-1:
            print(',')


        #        plt.plot(x, z, '-b',
        #        x, zEx, '-r'
        #             x, z2, '-b',
        #             x, z1, '-k',
        #             x, f2, '-r'
        #)
        #plt.show()

    print('}')
