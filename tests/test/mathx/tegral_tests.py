'''
Created on 19.10.2015

@author: michi
'''

import logging
import unittest

from mathx.tegral import tegral
import math


handler = logging.StreamHandler(open('/dev/stderr', 'w'))
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s') 
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.DEBUG)

class Test(unittest.TestCase):

    def test_integrate(self):
        
        func = lambda x: math.sqrt(1.0-x*x)
        res = tegral(func,-1,1,tol=1.0e-15)
        self.assertAlmostEqual(math.pi*0.5,res,places=13)

if __name__ == "__main__":
    unittest.main()
