'''
Created on 09.01.2016

@author: michi
'''

import codecs
import json
import logging
import math
from mathx import formula

log = logging.getLogger("mathx.evaluate")

NUMBER_TYPES = (int,float)

STATE_KEYS = {"n":int,"xmin":NUMBER_TYPES,"xmax":NUMBER_TYPES,"ymin":NUMBER_TYPES,"ymax":NUMBER_TYPES,"f":str}

class valuesiter(list):
    def __init__(self,state):
        self.f = state["f"]
        self.xmin = state["xmin"]
        self.xmax = state["xmax"]
        self.ymin = state["ymin"]
        self.ymax = state["ymax"]
        self.n = state["n"]
        self.n1 = self.n-1
        
        self.ast = formula.Parser(self.f).parseAst()
        self.vvars = list(self.ast.findVars({}))
        log.debug("vvars=%s"%self.vvars)
        assert len(self.vvars)==2
        self._i = 0
        self._j = 0
        self._x = self.xmin

    def __next__(self):
        
        if self._i>=self.n:
            raise StopIteration()

        y = self.ymin + self._j*(self.ymax-self.ymin)/self.n1

        try:
            z = self.ast.evaluate({self.vvars[0]:self._x,self.vvars[1]:y})
        except:
            z = None

        self._j += 1

        if self._j>=self.n:
            self._i +=1
            if self._i < self.n:
                self._j = 0
                self._x = self.xmin + self._i*(self.xmax-self.xmin)/self.n1

        if isinstance(z, (int,float)) and (math.isnan(z.real) or math.isinf(z.real)):
            return None
        else:
            return z

    def __iter__(self):
        return self
    def __len__(self):
        return 1

def handler(env, start_response):
    
    inp = env['wsgi.input']
    reader = codecs.getreader("utf-8")
    state = json.load(reader(inp))
    
    ret = {}
    
    for key,vtype in STATE_KEYS.items():
        value = state[key]
        assert isinstance(value, vtype)
        ret[key] = value

    # validate the input, for sure.
    n = state["n"]
    if n < 2 or n > 201:
        ret["n"] = 101

    values = valuesiter(ret)

    ret["values"] = values
    
    start_response('200 OK', [('Content-Type','application/json')])
    je = json.JSONEncoder()
    viter = je.iterencode(ret)
    return codecs.iterencode(viter,"utf-8")
