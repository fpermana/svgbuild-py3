# -*- coding: utf-8 -*-
# interpolations - routines for numerical interpolations between control values

'''

Routines for numerical interpolation between various control values.

SYNOPSIS

    >>> import interpolations ; from interpolations import *
    >>> import vectors ; from vectors import *

    Linear:

    >>> linear(0.5,  10, 20)
        15.0

    >>> linear(1.0, 2.0,  1.5,  10, 20)
        15.0

    >>> linear(1.0, 2.0,  1.5,  V(10,100,1000), V(20,200,2000))
        V(15.0, 150.0, 1500.0)

    Bezier:

    >>> bezier(0.5,  10, 20, 10)
        15.0

    >>> bezier(0.5,  10, 20, 20, 10)
        175.0

    >>> bezier(0.5,  V(10,100), V(20,200), V(20,200), V(10,100))
        V(17.5, 175.0)

AUTHOR

    Ed Halley (ed@halley.cc) 25 October 2007

REFERENCES

    Bezier code adapted and ported to python from a C++ v3 implementation:
    http://local.wasp.uwa.edu.au/~pbourke/surfaces_curves/bezier/index2.html

'''

__all__ = [ 'linear', 'bezier' ]

#----------------------------------------------------------------------------

import math

#----------------------------------------------------------------------------

def linear(*args):
    '''Find a point along a linear path of two controls.
    Controls may be scalars, or vectors if arithmetic operators defined.

    May take three arguments, linear(i, A, B).
    Interpolated values equal control A at i==0.0, and control B at i==1.0.
    
    May take five arguments, linear(x, y, i, A, B).
    Interpolated values equal control A at i==x, and control B at i==y.
    '''
    if len(args) == 3:
        (xmin, xmax) = (0., 1.)
        (x, hmin, hmax) = args
    elif len(args) == 5:
        (xmin, xmax, x, hmin, hmax) = args
    else:
        raise ValueError('linterp() takes 3 or 5 arguments')
    return ( ((x)-(xmin)) * ((hmax)-(hmin)) / ((xmax)-(xmin)) + (hmin) )

#----------------------------------------------------------------------------

# ref:
# http://local.wasp.uwa.edu.au/~pbourke/surfaces_curves/bezier/index2.html

def bezier3(i, A, B, C):
    '''Find a point along a bezier curve of three controls.
    Controls may be scalars, or vectors if arithmetic operators defined.

    Takes four arguments, bezier3(i, A, B, C).
    Interpolated values touch A at i==0.0, and C at i==1.0.
    Interpolated values may not touch B value.
    '''
    ii = 1.-i
    i2 = i*i
    ii2 = ii*ii
    j = A*ii2 + 2*B*ii*i + C*i2
    return j

def bezier4(i, A, B, C, D):
    '''Find a point along a bezier curve of four controls.
    Controls may be scalars, or vectors if arithmetic operators defined.

    Takes five arguments, bezier4(i, A, B, C, D).
    Interpolated values touch A at i==0.0, and D at i==1.0.
    Interpolated values may not touch B or C values.
    '''
    
#    print i, A, B, C, D
    
    ii = 1.-i
    i3 = i*i*i
    ii3 = ii*ii*ii
    j = A*ii3 + 3*B*i*ii*ii + 3*C*i*i*ii + D*i3
    return j

def bezier(i, *A):
    '''Find a point along a bezier curve of arbitrary number of controls.
    Controls may be scalars, or vectors if arithmetic operators defined.

    Takes at least two arguments, bezier(i, A, ...).
    Interpolated values touch A at i==0.0, and last control at i==1.0.
    Interpolated values may not touch any intervening control value.

    Uses linear interpolation for two controls (A, B),
    or constant if only given one control (A).
    '''
    n = len(A)-1
    if n < 4:
        if n < 0: raise ValueError('need at least one control value')
        if n == 0: return A[0]
        if n == 1: return linear(i, *A)
        if n == 2: return bezier3(i, *A)
        if n == 3: return bezier4(i, *A)
    ik = 1
    ii = 1-i
    ink = math.pow(ii, float(n))
    if i == 1.0:
        return A[-1]*1.0
    j = A[0]*0.0
    for k in range(n+1):
        nn = n
        kn = k
        nkn = n - k
        blend = ik*ink
        ik *= i
        ink /= ii
        while (nn >= 1):
            blend *= nn
            if (kn > 1):
                blend /= kn
                kn -= 1
            if (nkn > 1):
                blend /= nkn
                nkn -= 1
            nn -= 1
        j += A[k]*blend
    return j

#----------------------------------------------------------------------------

def __test__():
    from testing import __ok__, __report__
    import vectors ; from vectors import V,equal,zero

    print('Testing interpolations...')

    __ok__( linear(0.5, 50, 60), 55 )
    __ok__( linear(1, 2, 1.5, 50, 60), 55 )
    __ok__( linear(1, 2, 1.5, V(50,500), V(60,600)), V(55,550) )

    __ok__( bezier3(0.0,  0.0, 1.0, 0.0), 0.0 )
    __ok__( bezier3(0.5,  0.0, 1.0, 0.0), 0.5 )
    __ok__( equal( bezier3(0.2,  0.0, 1.0, 0.0),
                   bezier3(0.8,  0.0, 1.0, 0.0) ) )
    __ok__( bezier3(1.0,  0.0, 1.0, 0.0), 0.0 )

    __ok__( bezier4(0.0,  0.0, 1.0, 1.0, 0.0), 0.0 )
    __ok__( bezier4(0.5,  0.0, 1.0, 1.0, 0.0), 0.75 )
    __ok__( equal( bezier4(0.2,  0.0, 1.0, 1.0, 0.0),
                   bezier4(0.8,  0.0, 1.0, 1.0, 0.0) ) )
    __ok__( bezier4(1.0,  0.0, 1.0, 1.0, 0.0), 0.0 )

    __ok__( bezier(0.0,  0.0, 1.0, 1.0, 1.0, 0.0), 0.0 )
    __ok__( bezier(0.5,  0.0, 1.0, 1.0, 1.0, 0.0), 0.875 )
    __ok__( equal( bezier(0.2,  0.0, 1.0, 1.0, 1.0, 0.0),
                   bezier(0.8,  0.0, 1.0, 1.0, 1.0, 0.0) ) )
    __ok__( bezier(1.0,  0.0, 1.0, 1.0, 1.0, 0.0), 0.0 )
    __ok__( bezier(1.0,  0.0, 1.0, 1.0, 1.0, 0.0), 0.0 )

    __report__()

def __table__():
    from testing import __ok__, __report__

    for x in range(40+1):
        i = x/40.0
        print(i, ',', bezier(i, 1.0,2.0,0.0,2.0,1.0))

if __name__ == '__main__':
    raise Exception('This module is not a stand-alone script.  Import it in a program.')

