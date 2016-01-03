'''
Created on 26.10.2015

@author: michi
'''

import math

def root(r,x):
    return math.pow(x,1.0/r)

BUILTIN_FUNCTIONS = {
                      "sqrt": math.sqrt,
                      "exp": math.exp,
                      "ln": math.log,
                      "log": math.log10,
                      "sin": math.sin,
                      "cos": math.cos,
                      "tan": math.tan,
                      "asin": math.asin,
                      "acos": math.acos,
                      "atan": math.atan,
                      "sinh": math.sinh,
                      "cosh": math.cosh,
                      "tanh": math.tanh,
                      "asinh": math.asinh,
                      "acosh": math.acosh,
                      "atanh": math.atanh,
                      "root": root               
                    }
