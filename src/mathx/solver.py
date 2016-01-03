'''
Created on 24.09.2015

@author: michi
'''

from mathx import formula
from mathx import ast
from copy import deepcopy
import os
import logging

log = logging.getLogger('mathx.gleichungslöser')

#handler = logging.StreamHandler(open('/dev/stderr', 'w'))
#formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s') 
#handler.setFormatter(formatter)
        
#root_logger = logging.getLogger()
#root_logger.addHandler(handler)
#root_logger.setLevel(logging.DEBUG)

class Solver:
    def __init__(self,g):
        self.gleichung = g
        filename = os.path.dirname(__file__)
        filename = os.path.join(filename,"gleichungslöser_history.txt")
        fp = open(filename,"a")
        fp.write(self.gleichung+"\n")
        fp.close()
        l = [formula.Parser(i).parseAst() for i in g.split("=")]
        self.lhs = l[0]
        self.rhs = l[-1]
    def evaluate(self)->dict:
        rhs = ast.AstBinaryOperator(self.lhs,"-",self.rhs)
        varsv = rhs.findVars()
        
        for i in varsv.keys():
            path = rhs.searchPath(ast.AstVariable(i))
            work = deepcopy(rhs)
            lhs = ast.AstConstant(0.0)
            
            while path != []:
                try:
                    work,path,lhs = work.reducePath(path,lhs)
                except ValueError:
                    if not(type(work)==ast.AstVariable) or lhs.count(ast.AstVariable)!=0:
                        raise
                    #elif type(work)==ast.AstVariable and lhs.count(ast.AstVariable)!=0:
                    else:
                        log.debug("1. %s = %s"%(work,lhs))
                        lhs = lhs.simplify()
                        log.debug("2. %s = %s"%(work,lhs))
                        break
                        
                log.debug("1. %s = %s"%(work,lhs))
                lhs = lhs.simplify()
                log.debug("2. %s = %s"%(work,lhs))
                
            log.debug("%s = %s"%(i,lhs))
            varsv[i] = lhs
        return varsv

class AstSolver(Solver):
    def __init__(self,lhs,rhs):
        filename = os.path.dirname(__file__)
        filename = os.path.join(filename,"gleichungslöser_history.txt")
        fp = open(filename,"a")
        fp.write("%s=%s\n"%(lhs,rhs))
        fp.close()
        self.lhs = lhs
        self.rhs = rhs

if __name__ == '__main__':
    g = input("geben Sie die Gleichung ein: ")
    '''
    assert len(g.split("="))==2
    filename = os.path.dirname(__file__)
    filename = os.path.join(filename,"gleichungslöser_history.txt")
    fp = open(filename,"a")
    fp.write(g+"\n")
    fp.close()
    l = [formula.Parser(i).parseAst() for i in g.split("=")]
    print("=".join([str(i) for i in l]))
    rhs = ast.AstBinaryOperator(l[0],"-",l[1])
    varsv = {}
    rhs.findVars(varsv)
    
    for i in varsv.keys():
        path = rhs.searchPath(ast.AstVariable(i))
        work = deepcopy(rhs)
        lhs = ast.AstConstant(0.0)
        
        while path != []:
            work,path,lhs= work.reducePath(path,lhs)
            print("1. %s = %s"%(work,lhs))
            lhs = lhs.simplify()
            print("2. %s = %s"%(work,lhs))
            
        print("%s = %s"%(i,lhs))
    '''
    
    handler = logging.StreamHandler(open('/dev/stderr', 'w'))
    formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s') 
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    
    evg = Solver(g).evaluate()
    print(evg)
    
    print("\n".join(["%s = %s"%(key,value) for key,value in evg.items()]))
    