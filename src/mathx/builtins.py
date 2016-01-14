'''
Created on 26.10.2015

@author: michi
'''

import math

def root(r,x):
    return math.pow(x,1.0/r)

def sec(x):
    return 1/math.cos(x)

def csc(x):
    return 1/math.sin(x)

def cot(x):
    return 1/math.tan(x)

def acsc(x):
    return math.asin(1/x)

def asec(x):
    return math.acos(1/x)

def acoth(x):
    return math.cosh(x)/math.sinh(x)

def sech(x):
    return 1/math.cosh(x)

def csch(x):
    return 1/math.sinh(x)

BUILTIN_FUNCTIONS = {
                      "sqrt": math.sqrt,
                      "exp": math.exp,
                      "ln": math.log,
                      "log": math.log10,
                      "sin": math.sin,
                      "cos": math.cos,
                      "tan": math.tan,
                      "cot": cot,
                      "asin": math.asin,
                      "acos": math.acos,
                      "atan": math.atan,
                      "sinh": math.sinh,
                      "cosh": math.cosh,
                      "tanh": math.tanh,
                      "asinh": math.asinh,
                      "acosh": math.acosh,
                      "atanh": math.atanh,
                      "root": root,
                      "abs": abs,
                      "sec": sec,
                      "csc": csc,
                      "sech": sech,
                      "csch": csch,
                      "acsc": acsc,
                      "asec": asec
                    }
