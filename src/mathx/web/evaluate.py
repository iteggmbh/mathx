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

_cache = {}

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
            
            if math.isnan(z.real) or math.isinf(z.real):
                yield None
            else:
                yield z

def handler(env, start_response):
    
    inp = env['wsgi.input']
    reader = codecs.getreader("utf-8")
    state = json.load(reader(inp))
    
    log.info("state=%r"%state)
    
    if (state["f"], state["xmin"], state["xmax"], state["ymin"], state["ymax"], state["n"]) in _cache:
        ret = {"n":state["n"],"values":type("StreamArray",(list,),{"__iter__":lambda self:_cache[(state["f"], state["xmin"], state["xmax"], state["ymin"], state["ymax"], state["n"])],"__len__":lambda self: 1})()}
    else:
        values = valuesgen(state)
        _cache[(state["f"], state["xmin"], state["xmax"], state["ymin"], state["ymax"], state["n"])] = values
        ret = {"n":state["n"],"values":type("StreamArray",(list,),{"__iter__":lambda self:values,"__len__":lambda self: 1})()}
    
    start_response('200 OK', [('Content-Type','application/json')])
    je = json.JSONEncoder()
    viter = je.iterencode(ret)
    return codecs.iterencode(viter,"utf-8")
