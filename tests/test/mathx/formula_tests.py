'''
Created on 19.10.2015

@author: michi
'''

import logging
import unittest

from mathx import ast
from mathx import formula
from mathx.ast import AstConstant


handler = logging.StreamHandler(open('/dev/stderr', 'w'))
formatter = logging.Formatter( '%(asctime)s %(levelname)s %(message)s') 
handler.setFormatter(formatter)
        
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.DEBUG)

class Test(unittest.TestCase):

    def _test_formula(self,res,f,variables={}):
        o = formula.Parser(f)
        i = o.evaluate(variables)
        print("%s = %g"%(f,i))
        self.assertEqual(res, i)
        node = o.parseAst()
        print("%s = %s"%(f,node))
        print(repr(node))
        try:
            self.nodes += [node]
        except:
            self.nodes = [node] 
        x = node.evaluate(variables)
        self.assertEqual(res, x)

    def testPlus(self):
        self._test_formula(3,"1+1+1")

    def testPlusProduct(self):
        self._test_formula(14,"2+3*4")

    def testPlusParenthesesProduct(self):
        self._test_formula(20,"(2+3)*4")

    def testProductPlus(self):
        self._test_formula(10,"2*3+4")

    def testExponentiation(self):
        self._test_formula(512,"2^3^2")
        self._test_formula(64,"(2^3)^2")

    def testRoot(self):
        self._test_formula(3,"root(3,27)")
        
    def testVariable(self):
        self._test_formula(7,"3+x",{"x":4})
        
    def testBuiltin(self):
        self._test_formula(2,"log(100)")
        
    def testSearchPath(self):
        p = formula.Parser("3*y+4*x")
        node = p.parseAst()
        
        path = node.searchPath(ast.AstVariable("x"))
        print ("path=%s"%_readastpath(path))
        
        p = formula.Parser("x*y+4*x")
        node = p.parseAst()
        
        path = node.searchPath(ast.AstVariable("x"))
        print ("path=%s"%_readastpath(path))
        
    def testLinCombReduction(self):
        p = formula.Parser("3*x+5+x*4")
        
        node = p.parseAst()
        path = node.searchPath(ast.AstVariable("x"))
        
        print ("path=%s"%_readastpath(path))
        ret,rpath,other = node.reducePath(path,AstConstant(0.0))
        
        print ("res = %s,%s,%s"%(ret,rpath,other))
        self.assertEqual([],rpath)
        self.assertEqual("(0.0-5.0)/(4.0+3.0)",str(other))
        
        other = other.simplify()
        self.assertEqual("-0.7142857142857143",str(other))
        
    def testLinCombOne(self):
        p = formula.Parser("x+5+x")
        
        node = p.parseAst()
        path = node.searchPath(ast.AstVariable("x"))
        
        print ("path=%s"%_readastpath(path))
        ret,rpath,other = node.reducePath(path,AstConstant(0.0))
        
        print ("res = %s,%s,%s"%(ret,rpath,other))
        self.assertEqual([],rpath)
        self.assertEqual("(0.0-5.0)/(1.0+1.0)",str(other))
        
        other = other.simplify()
        self.assertEqual("-2.5",str(other))

    def testLinCombOneSimple(self):
        p = formula.Parser("x+x")
        
        node = p.parseAst()
        path = node.searchPath(ast.AstVariable("x"))
        
        print ("path=%s"%_readastpath(path))
        ret,rpath,other = node.reducePath(path,AstConstant(0.0))
        
        print ("res = %s,%s,%s"%(ret,rpath,other))
        self.assertEqual([],rpath)
        self.assertEqual("0.0/(1.0+1.0)",str(other))
        
        other = other.simplify()
        self.assertEqual("0.0",str(other))

    def testExpProdReduction(self):
        
        p = formula.Parser("(x-2)^3 * (x-2)^5")
        
        # (x-2)^(3+5) = 0
        # x-2 = root(3+5,0)
        # x = root(3+5,0)+2
        
        node = p.parseAst()
        path = node.searchPath(ast.AstVariable("x"))
        
        print ("path=%s"%_readastpath(path))
        ret,rpath,other = node.reducePath(path,AstConstant(0.0))
        
        ret,rpath,other = ret.reducePath(rpath,other)
        ret,rpath,other = ret.reducePath(rpath,other)
        
        print ("res = %s,%s,%s"%(ret,rpath,other))
        self.assertEqual([],rpath)
        self.assertEqual("root(3.0+5.0,0.0)+2.0",str(other))
        
        other = other.simplify()
        self.assertEqual("2.0",str(other))
        
def _readastpath(astpath):
    if type(astpath)==list:
        res = []
        for i in astpath:
            if type(i)==tuple or type(i)==list:
                res.append(_readastpath(i))
            else:
                res.append(str(i))
    elif type(astpath)==tuple:
        res = []
        for i in astpath:
            if type(i)==tuple or type(i)==list:
                res.append(_readastpath(i))
            else:
                res.append(str(i))
        res = tuple(res)
    return res
if __name__ == "__main__":
    unittest.main()
