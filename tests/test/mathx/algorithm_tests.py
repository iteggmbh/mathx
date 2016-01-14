'''
Created on 19.10.2015

@author: michi
'''

import logging
import unittest

from mathx.algorithms import findRootSecant
import math


handler = logging.StreamHandler(open('/dev/stderr', 'w'))
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s') 
handler.setFormatter(formatter)
        
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.DEBUG)

class Test(unittest.TestCase):

    def test_findRootSecant(self):
        
        func = lambda x: pow(x,1/x)
        x = findRootSecant(func,math.sqrt(2),1.0,2.5,tol=1.0e-8)
        self.assertAlmostEqual(2.0,x,places=6)
        
        x = findRootSecant(func,math.sqrt(2),2.9,10000.0,tol=1.0e-8)
        self.assertAlmostEqual(4.0,x,places=6)
        
        
    

if __name__ == "__main__":
    unittest.main()
