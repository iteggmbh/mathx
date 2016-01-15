'''
    This is a python port of HNW's Tegral program.
   I first used a C port, then a C++ port, now I made it live in Python.
'''

import logging

log = logging.getLogger("mathx.tegral")

# Gauss-Quadrature with order 30 */

''' Support Points - because of the symmetry we only store 7 values for 15
		 support points.
		 The values represent the distance from the center of
                 the integration interval [a,b].

		 hence, the support point are given by:
                        0<=i<=6 :  c_i = (a+b)/2 -
					 gauss_15_base[i] * (b-a)/2
			i=7 :      c_7 = (a+b)/2
			8<=i<=14   c_i = (a+b)/2 +
					 gauss_15_base[14-i] * (b-a)/2
'''
gauss_15_base = [  0.98799251802048542848,
		   0.93727339240070590431,
		   0.84820658341042721620,
		   0.72441773136017004742,
		   0.57097217260853884754,
		   0.39415134707756336989,
		   0.20119409399743452230 ]

''' Gewichte : Storage schem accoring to the support points,
               but amended with an eigths value for the weight of the
               center point.
'''
gauss_15_weight = [  0.30753241996117268355e-1,
                     0.70366047488108124709e-1,
                     0.10715922046717193501,
                     0.13957067792615431445,
                     0.16626920581699393355,
                     0.18616100001556221103,
                     0.19843148532711157645,
                     0.20257824192556127288 ]

'''
  Weigths of the embedded quadrature formula of order 14
'''

gauss_15_14_weight = [ 0.429480564346795643e-1,
                       0.287463102008375231e-1,
                       0.185198436210474195,
                       0.236554834186314248e-1,
                       0.316940072793589170,
                       0.768583788397500479e-2,
                       0.394825803057813184    ]

'''
  weights of the embedded quadrature formula with order 6
'''

gauss_15_6_flag = [ -1,0,-1,1,-1,-1,2 ]

gauss_15_6_weight = [ 0.110736894967772885,
                      0.413082121428665960,
                      0.476180983603561155 ]

'''
 a self-dividing tree.
  we don't provide this type publically, so define it as structure.
'''
class TegralPartition: 

    ERROR_WEIGHT_UNDIVIDED = 0 
    ERROR_WEIGHT_LEFT      = 1 
    ERROR_WEIGHT_RIGHT     = 2 
    
    def __init__(self,func,a,b):
        
        self.error_weight = TegralPartition.ERROR_WEIGHT_UNDIVIDED
        self.a = a
        self.b = b
        self.left = None
        self.right = None
        
        length_2 = (b-a)*0.5
        abs_length_2 = abs(length_2)
        center       = (b+a)*0.5
        res_6  = 0.0
        res_14 = 0.0
        
        self.res = func(center) * gauss_15_weight[7]
  
        self.resabs = abs(self.res)
  
        for i in range(7):
        
            d = length_2*gauss_15_base[i]
      
            fval1 = func(center-d)
            fval2 = func(center+d)
      
            hold = fval1+fval2
      
            self.res    += gauss_15_weight[i] *  hold
            self.resabs += gauss_15_weight[i] * (abs(fval1)+abs(fval2))
      
            res_14 += gauss_15_14_weight[i] * hold
      
            j = gauss_15_6_flag[i]
            if j >= 0:
                res_6 += gauss_15_6_weight[j] * hold

        # error estimaton
        self.err = abs(self.res - res_14)
  
        hold = max(abs(self.res-res_6),self.err*0.1)
  
        if hold != 0.0:
            self.err *= abs_length_2*(self.err/hold)*(self.err/hold)
  
        self.res    *= length_2
        self.resabs *= abs_length_2
  
        self.err = max(1.0e-16*self.resabs,self.err)
        self.max_err = self.err
        
        if log.isEnabledFor(logging.DEBUG):
            log.debug("tegral: a,b,err,max_err=%g,%g,%g,%g"%(self.a,self.b,self.err,self.max_err))
        
    def divide(self,func):

        if self.error_weight == TegralPartition.ERROR_WEIGHT_RIGHT:
            self.right.divide(func)
        elif self.error_weight == TegralPartition.ERROR_WEIGHT_LEFT:
            self.left.divide(func)
        else: # TegralPartition.ERROR_WEIGHT_UNDIVIDED
            center = (self.a+self.b)*0.5
            self.left  = TegralPartition(func,self.a,center)
            self.right = TegralPartition(func,center,self.b)

        self.err    = self.right.err    + self.left.err
        self.res    = self.right.res    + self.left.res
        self.resabs = self.right.resabs + self.left.resabs

        if self.right.max_err > self.left.max_err:
            self.error_weight = TegralPartition.ERROR_WEIGHT_RIGHT
            self.max_err      = self.right.max_err
            
        else:
            self.error_weight = TegralPartition.ERROR_WEIGHT_LEFT
            self.max_err      = self.left.max_err

'''
  Calculate the integral of the callable func in the interval
  [a,b] usign the Tegral alogrithms by Hairer-Noerseth-Wanner
'''
def tegral(func,a,b,tol=1.0e-8,max_partitions=1000):

    if a==b:
        return 0.0
    
    a_b_interval = TegralPartition(func,a,b)

    n_parts = 0
    
    while a_b_interval.err/a_b_interval.resabs > tol and n_parts < max_partitions:
        a_b_interval.divide(func)
        n_parts += 1
  
    if n_parts >= max_partitions:
        log.warn("tegral: warning: weak convergence attested: res,resabs,err,max_parts=%lg,%lg,%lg,%d"%(
            a_b_interval.res,
            a_b_interval.resabs,
            a_b_interval.err,max_partitions))
    
    return a_b_interval.res
