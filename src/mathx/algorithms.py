'''
Created on 25.12.2015

@author: michi
'''
import math

def findRootSecant(func,y,xleft,xright,tol = 1.0e-12, abstol = 1.0e-16, maxiter = 60):
    '''
    Solve the equation y = func(x) by teh secant method.
    
    :param func: The function to evaluate.
    :param y: The ordinate value to search.
    :param xleft: The left point of the search interval
    :param xright: The right point of the search interval
    '''
    
    x1 = xleft
    dy1 = func(x1)-y
    x2 = xright
    dy2 = func(x2)-y
    
    if dy1*dy2 > 0:
        raise ValueError("Initial interval does not have values with opposite signs w.r.t. y.")
    
    if math.fabs(y) < abstol:
        realtol = abstol
    else:
        realtol = math.fabs(y) * tol
    
    for niter in range(maxiter):
        
        # y2         +
        #           /
        #          /
        # y ------/-------
        #        /
        #       /
        #      /
        # y1  +
        #
        #     x1  xm x2
        #
        #
        # (xm - x1) / (y-y1) = (x2-xm)/(y2-y)
        # (x1 -xm) / dy1 = (x2-xm)/dy2
        # dy2 * (x1-xm) = dy1 * (x2-xm)
        # xm*(dy1-dy2) = dy1 * x2 - dy2 * x1
        # xm = (dy1 * x2 - dy2 * x1) / (dy1-dy2)
    
        xm = (dy1 * x2 - dy2 * x1) / (dy1-dy2)
        dym = func(xm)-y
        
        print ("niter,dym=%d,%lg"%(niter,dym))
        
        if math.fabs(dym)<realtol:
            return xm
        
        
        #if dy1*dym > 0:
        x2 = xm
        dy2 = dym
        #else:
        #    x1 = xm
        #    dy1 = dym
    
    raise ValueError("Root finding diverged after %d iterations."%maxiter)
def findRoot(func,y,xleft,xright,tol = 1.0e-12, abstol = 1.0e-16, maxiter = 60):
    es = []
    while xleft<=xright:
        try:
            root = findRootSecant(func, y, xleft, xright, tol, abstol, maxiter)
        except BaseException as e:
            es.append(e)
        xleft = root+1
        yield root
    print(es)
        
    
    