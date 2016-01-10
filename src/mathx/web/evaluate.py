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

def valuesgen(state):
    f = state["f"]
    xmin = state["xmin"]
    xmax = state["xmax"]
    ymin = state["ymin"]
    ymax = state["ymax"]
    n = state["n"]
    n1 = n-1
    
    ast = formula.Parser(f).parseAst()
    vvars = list(ast.findVars())
    assert len(vvars)==2
    
    for i in range(n):
        
        x = xmin + i*(xmax-xmin)/n1
        
        for j in range(n):
            y = ymin + j*(ymax-ymin)/n1
            try:
                z = ast.evaluate({vvars[0]:x,vvars[1]:y})
            except:
                z = None
            
            if isinstance(z, (int,float)) and (math.isnan(z.real) or math.isinf(z.real)):
                yield None
            else:
                yield z

def handler(env, start_response):
    
    inp = env['wsgi.input']
    reader = codecs.getreader("utf-8")
    state = json.load(reader(inp))
    
    ret = {}
    
    for key,vtype in STATE_KEYS.items():
        value = state[key]
        assert isinstance(value, vtype)
        ret[key] = value
    
    values = valuesgen(state)

    ret["values"] = type("StreamArray",(list,),{"__iter__":lambda self:values,"__len__":lambda self: 1})()
    
    start_response('200 OK', [('Content-Type','application/json')])
    je = json.JSONEncoder()
    viter = je.iterencode(ret)
    return codecs.iterencode(viter,"utf-8")
