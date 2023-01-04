#!/usr/bin/env python


from math import *
import numpy as np
import numpy.linalg as la
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt


class SplineSolverQuartic:
    def __init__(self, xMax, nx):

        #
        self.xMax = xMax

        # N is the number of nodes. There are then N-1 intervals.
        self.N = nx

        # h is the interval size
        self.h = xMax/float(nx-1)

        # c is the vector of spline coefficients.
        self.c = np.zeros(5*(self.N-1))

    def solve(self, wDat):

        N = self.N
        h = self.h
        h3 = h**3

        # There are N nodes, numbered 0 to N-1.
        # There are N-1 intervals, numbered 0 to N-2.

        B = np.zeros((5*(N-1), N))
        for nu in range(N-1):
            row0 = 1 + 5*nu
            print('row=', row0)
            B[row0, nu] = h3/6
            B[row0+1, nu] = -h3/24
            B[row0+1, nu+1] = h3/24

        print('\nMatrix B=\n', B)

        b = np.dot(B, wDat)

        A = np.zeros((5*(N-1), 5*(N-1)))

        # BC f(0)=0
        A[0,0]=1.0

        # Jump conditions at nodes
        for nu in range(1,N-1):
            row0 = 3+5*(nu-1)
            # Continuity of f at x_nu
            for k in range(5):
                A[row0, 5*(nu-1)+k] = 1
            A[row0, 5*nu] = -1
            # Continuity of f' at x_nu
            for k in range(1,5):
                A[row0+1, 5*(nu-1)+k] = k
            A[row0+1, 5*nu+1] = -1
            # Continuity of f'' at x_nu
            for k in range(2,5):
                A[row0+2, 5*(nu-1)+k] = k*(k-1)
            A[row0+2, 5*nu+2] = -2

        # Integration conditions in elements
        for e in range(N-1):
            row0 = 1 + 5*e
            A[row0,row0+2] = 1
            A[row0+1,row0+3] = 1

        # BC f'(x_max)=0
        row0 = 5*(N-1)-2
        col0 = 5*(N-2)
        for k in range(1,5):
            A[row0, col0+k] = k


        # BC f''(x_max)=0
        row0 = 5*(N-1)-1
        col0 = 5*(N-2)
        for k in range(2,5):
            A[row0, col0+k] = k*(k-1)


        print('\nMatrix A=\n', A)
        print('\nRHS b=\n', b)

        self.c = la.solve(A,b)
        print('\nc=\n', self.c)



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
            mid = (high+low)//2
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
            C = self.c[5*(self.N-2):5*(self.N-2)+5]
            return C[0] + C[1] + C[2] + C[3] + C[4]

        t = (x-i*self.h)/self.h

        C = self.c[5*i:5*i+5]
        return C[0] + t*(C[1] + t*(C[2] + t*(C[3] + t*C[4])))

    def interpolateDerivs(self, x):

        i = int(self.locatePoint(x))

        if i<0:
            return (0,0,0)


        if i>=(self.N-1):
            C = self.c[5*(self.N-2):5*(self.N-2)+5]
            return (C[0] + C[1] + C[2] + C[3] + C[4], 0, 0)

        t = (x-i*self.h)/self.h

        C = self.c[5*i:5*i+5]
        return (
            C[0] + t*(C[1] + t*(C[2] + t*(C[3]+ t*C[4]))),
            (C[1] + t*(2*C[2] + t*(3*C[3] + t*4*C[4])))/self.h,
            (2*C[2] + t*(6*C[3] + t*12*C[4]))/self.h/self.h
            )



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

    def rhs(x):
        return x-1/3

    def uSoln(x):
        return (12*x - 6*x**2 - 4*x**3 + 3*x**4)/72.


    def uSoln1(x):
        return (12 - 12*x - 12*x**2 + 12*x**3)/72.



    def uSoln2(x):
        return (-12 - 24*x + 36*x**2)/72.



    xMax = 1
    nx = 3

    s = SplineSolverQuartic(xMax, nx)
    X = np.linspace(0, xMax, nx)

    w = np.array([rhs(x) for x in X])

    s.solve(w)

    Xfine = np.linspace(0, xMax, 24)

    uEx = np.array([uSoln(x) for x in Xfine])
    u1Ex = np.array([uSoln1(x) for x in Xfine])
    u2Ex = np.array([uSoln2(x) for x in Xfine])

    uNum = np.array([s.interpolateDerivs(x)[0] for x in Xfine])
    u1Num = np.array([s.interpolateDerivs(x)[1] for x in Xfine])
    u2Num = np.array([s.interpolateDerivs(x)[2] for x in Xfine])

    plt.plot(Xfine, uEx, '-b', Xfine, uNum, 'bo')
    plt.plot(Xfine, u1Ex, '-r', Xfine, u1Num, 'ro')
    plt.plot(Xfine, u2Ex, '-k', Xfine, u2Num, 'ko')
    plt.show()
