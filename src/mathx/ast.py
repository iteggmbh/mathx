'''
Created on 26.10.2015

@author: michi
'''

from mathx.builtins import BUILTIN_FUNCTIONS
import math

class EvaluateException(Exception):
    pass

class AstNode:
    def evaluate(self,variables={}):
        raise NotImplementedError()
    
    def findVars(self,variables={}):
        return variables

    def simplify(self):
        return self
    
    def count(self,asttype):
        return 0
    def __eq__(self,other):
        raise NotImplementedError()
    def isEquivalent(self,other):
        other = other.simplify()
        if other.count(AstVariable)==0 and self.count(AstVariable)==0:
            return self.evaluate()==other.evaluate()
        else:
            new_self = self.simplify()
            res = new_self==other
            if res:
                return res
            else:
                return False
    def searchPath(self,ast):
        return []
    def reducePath(self,path,other):
        '''
         @param path The path returned by searchPath to reduce
         @param other The AST node to extend by the inverse operation
         @return:  (new_self,new_path,new_other)
        '''
        if path == [self]:
            return(self,[],other)
        else:
            raise ValueError('Path and node are not compatible.')

class AstConstant(AstNode):
    
    def __init__(self,x):
        self.value=x
    
    def evaluate(self, variables={}):
        return self.value
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return "AstConstant(%r)"%self.value
    def count(self, asttype):
        if asttype==AstConstant:
            return 1
        else:
            return 0
    def __eq__(self, other):
        if type(other)==AstConstant:
            return self.value==other.value
        else:
            return False
    
    def isEquivalent(self, other):
        other = other.simplify()
        return self == other
    
    def searchPath(self, ast):
        if type(ast)==AstConstant and self.value==ast.value:
            return [self]
        else:
            return []

    
class AstVariable(AstNode):
    
    def __init__(self,v):
        self.variable=v

    def findVars(self,variables={}):
        if not(self.variable in variables):
            variables[self.variable] = None
        return variables

    def evaluate(self, variables={}):
        
        x = variables.get(self.variable)
        
        if x == None:
            raise EvaluateException("Variable %s is undefined."%self.variable)
        
        return x
    
    def count(self, asttype):
        if asttype==AstVariable:
            return 1
        else:
            return 0
    def __str__(self):
        return self.variable
    
    def __repr__(self):
        return "AstVariable(%r)"%self.variable
    def __eq__(self, other):
        if type(other)==AstVariable:
            return self.variable==other.variable
        else:
            return False
    def isEquivalent(self, other):
        other = other.simplify()
        return self==other
    def searchPath(self, ast):
        if ast==self:
            return [self]
        else:
            return []

KNOWN_BINARY_OPERATORS = { "+": 1,
                           "-": 1,
                           "*": 2,
                           "/": 2,
                           "^": 3
                          }

class AstBinaryOperator(AstNode):
    
    def __init__(self,lhs,op,rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        self.precedence = KNOWN_BINARY_OPERATORS[op]
    
    def findVars(self,variables={}):
        self.lhs.findVars(variables)
        self.rhs.findVars(variables)
        return variables
    
    def simplify(self):
        if type(self.lhs) == AstConstant and type(self.rhs) == AstConstant:
            return AstConstant(self.evaluate())
        else:
            self.lhs = self.lhs.simplify()
            self.rhs = self.rhs.simplify()
            
            if type(self.lhs) == AstConstant and type(self.rhs) == AstConstant:
                return AstConstant(self.evaluate())
            
            if type(self.lhs) == AstConstant and self.lhs.value == 0.0:
                # 0 + x -> x
                if self.op == "+":
                    return self.rhs
                
                # 0 - x -> -x
                if self.op == "-":
                    return AstNegation(self.rhs).simplify()
                
                # 0 * x -> 0,  0/x -> 0, 0^x -> 0
                if self.op == "*" or self.op == "/" or self.op == "^":
                    return AstConstant(0.0)
                
            if type(self.lhs) == AstConstant and self.lhs.value == 1.0:
                
                # 1 * x -> x
                if self.op == "*":
                    return self.rhs
                
                # 1^x -> 1
                if self.op == "^":
                    return AstConstant(1.0)

            if type(self.lhs) == AstConstant and self.lhs.value == -1.0:
                
                # -1 * x -> -x
                if self.op == "*":
                    return AstNegation(self.rhs).simplify()

            if type(self.rhs) == AstConstant and self.rhs.value == 0.0:
                # x + 0 -> x, x - 0 -> x
                if self.op == "+" or self.op == "-":
                    return self.lhs
                
                # x * 0 -> 0
                if self.op == "*":
                    return AstConstant(0.0)

                # x^0 -> 1
                if self.op == "^":
                    return AstConstant(1.0)
                
            if type(self.rhs) == AstConstant and self.rhs.value == 1.0:
                
                # x * 1 -> x, x / 1 -> x
                if self.op == "*" or self.op == "/": 
                    return self.rhs
                
                # x ^ 1 -> x
                if self.op == "^":
                    return self.lhs

            if type(self.rhs) == AstConstant and self.rhs.value == -1.0:
                
                # x * -1 -> -x, x / -1 -> -x
                if self.op == "*" or self.op == "/":
                    return AstNegation(self.rhs).simplify()
            return self
            
    def evaluate(self, variables={}):
        
        if self.op == "+":
            return self.lhs.evaluate(variables) + self.rhs.evaluate(variables)
        elif self.op == "-":
            return self.lhs.evaluate(variables) - self.rhs.evaluate(variables)
        elif self.op == "*":
            return self.lhs.evaluate(variables) * self.rhs.evaluate(variables)
        elif self.op == "/":
            return self.lhs.evaluate(variables) / self.rhs.evaluate(variables)
        elif self.op == "^":
            return math.pow(self.lhs.evaluate(variables),self.rhs.evaluate(variables))
        else:
            raise EvaluateException("Operator %s is unknown."%self.op)

    def count(self, asttype):
        if asttype==AstBinaryOperator:
            return 1+self.lhs.count(asttype)+self.rhs.count(asttype)
        else:
            return self.lhs.count(asttype)+self.rhs.count(asttype)
        
    def __str__(self):
        
        ret = ""
        
        if hasattr(self.lhs,"precedence") and (self.lhs.precedence < self.precedence or self.lhs.precedence == 3 and self.precedence==3):
            ret += "(" + str(self.lhs) + ")"
        else:
            ret += str(self.lhs)
        
        ret += self.op
        
        if hasattr(self.rhs,"precedence") and self.rhs.precedence < self.precedence:
            ret += "(" + str(self.rhs) + ")"
        else:
            ret += str(self.rhs)

        return ret
    
    def __repr__(self):
        return "AstBinaryOperator(%r,%r,%r)"%(self.lhs,self.op,self.rhs)
    def __eq__(self, other):
        if type(other)==AstBinaryOperator:
            return (self.rhs==other.rhs)and(self.lhs==other.lhs)and(self.op==other.op)
        else:
            return False
    def searchPath(self, ast):
        if ast == self:
            return [self]
        else:
            rpath =  self.rhs.searchPath(ast)
            lpath = self.lhs.searchPath(ast)    
                
            if lpath==[] and rpath==[]:
                return []
            else:
                return [self,(lpath,rpath)]

    def reducePath(self,path,other):
        
        if path == [self]:
            return self,[],other
        
        elif type(path) == list and path[0] == self and type(path[1]) == tuple:
            
            lpath,rpath = path[1]
            
            if lpath == []:
                if rpath == []:
                    raise ValueError('forked path contain two dead ends.')
            
                # destination found on rhs.
                
                if self.op == '+':
                    # lhs+rhs = other -> rhs = other - lhs  
                    return(self.rhs,rpath,AstBinaryOperator(other,'-',self.lhs))
                elif self.op == '-':
                    # lhs-rhs = other -> -rhs = other - lhs -> rhs = lhs - other 
                    return(self.rhs,rpath,AstBinaryOperator(self.lhs,'-',other))
                elif self.op == '*':
                    # lhs*rhs = other -> rhs = other/lhs 
                    return(self.rhs,rpath,AstBinaryOperator(other,'/',self.lhs))
                elif self.op == '/':
                    # lhs/rhs = other -> lhs = other*rhs -> rhs = lhs/other 
                    return(self.rhs,rpath,AstBinaryOperator(self.lhs,'/',other))
                elif self.op == '^':
                    # lhs^rhs = other -> exp(ln(lhs)*rhs) = other -> ln(lhs) * rhs = ln(other) -> rhs = ln(other)/ln(lhs)
                    return(self.rhs,rpath,AstBinaryOperator(AstFunctionCall('ln',other),'/',AstFunctionCall('ln',self.lhs)))
                else:
                    raise ValueError('Unsupported binary operator %s in reducePath.'%self.op)
            elif rpath == []:
                
                # destination found on lhs.
                
                if self.op == '+':
                    # lhs+rhs = other -> lhs = other - rhs  
                    return(self.lhs,lpath,AstBinaryOperator(other,'-',self.rhs))
                elif self.op == '-':
                    # lhs-rhs = other -> lhs = other + rhs 
                    return(self.lhs,lpath,AstBinaryOperator(other,'+',self.rhs))
                elif self.op == '*':
                    # lhs*rhs = other -> lhs = other/rhs 
                    return(self.lhs,lpath,AstBinaryOperator(other,'/',self.rhs))
                elif self.op == '/':
                    # lhs/rhs = other -> lhs = other*rhs 
                    return(self.lhs,lpath,AstBinaryOperator(other,'*',self.rhs))
                elif self.op == '^':
                    # lhs^rhs = other -> lhs = other^(1/rhs)
                    return(self.lhs,lpath,AstRoot(other, self.rhs))
                else:
                    raise ValueError('Unsupported binary operator %s in reducePath.'%self.op)
                
            elif self.op == '+' or self.op == '-':
                
                # accumulate linear combinations
                
                # x*a + c + b*x -> (a+b)*x + c aka (+,(+,(*,x,a),c),(*,b,x)) -> (+,(*,(+,a,b),x),c)  
                # x + a*x -> (a+1) * x 
                work = self
                factor = None
                remainder = None
                
                while work == None or work.op == '+' or work.op == '-':
                    
                    nfactor = None
                    nrem = None
                    
                    if len(rpath) == 0 and work != None:
                        nrem = work.rhs

                    # +- x
                    elif len(rpath) == 1:
                        nfactor = AstConstant(1.0)
                    
                    # a * x
                    elif len(rpath) == 2 and type(rpath[0])==AstBinaryOperator and rpath[0].op == '*':
                        nlpath,nrpath = rpath[1]
                        if nlpath == []:
                            if nrpath == []:
                                raise ValueError('Unable to reduce forked path of square type.')

                            nfactor = rpath[0].lhs
                            
                        elif nrpath == []:
                            nfactor = rpath[0].rhs
                            
                        else:
                            raise ValueError('Impossible, unable to reduce forked path (path ende prematurely).')
                    else:
                        raise ValueError('Unable to reduce forked path (no linear combination).')

                    op = '+' if work == None else work.op 

                    if nfactor != None:
                        if factor == None:
                            if op == '-':
                                factor = AstNegation(nfactor)
                            else:
                                factor = nfactor
                        else:
                            factor = AstBinaryOperator(factor,op,nfactor)
                        
                    if nrem != None:
                        if remainder == None:
                            if op == '-':
                                remainder = AstNegation(nrem)
                            else:
                                remainder = nrem
                        else:
                            remainder = AstBinaryOperator(remainder,op,nrem)

                    if lpath == None:
                        break
                    
                    # descend in to lhs
                    if len(lpath) == 2 and type(lpath[1]) == tuple and lpath[0].op in ("+","-"):
                        work = lpath[0]
                        lpath,rpath = lpath[1]
                    
                    else:
                        rpath = lpath
                        lpath = None
                        work = None
                    
                if lpath != None:
                    # destination found on both ends.
                    raise ValueError('Unable to reduce forked linear combination.')
                
                # factor * x + remainder = other -> x = (other - remainder) / factor
                if remainder == None:
                    return (self.lhs,[],AstBinaryOperator(other,'/',factor))
                else:
                    return (self.lhs,[],AstBinaryOperator(AstBinaryOperator(other,'-',remainder),'/',factor))
                    
            elif self.op == '*':
            #    
                # accumulate products
                
                if (len(rpath) == 2 and type(rpath[0])==AstBinaryOperator and rpath[0].op == '^' and 
                    len(lpath) == 2 and type(lpath[0])==AstBinaryOperator and lpath[0].op == '^'):
             
                
                    # x^a * x^b = x^(a+b)
                    if (type(lpath[1]) == tuple and lpath[1][1] == [] and
                        type(rpath[1]) == tuple and rpath[1][1] == [] and
                         lpath[1][0] == rpath[1][0] ):
                        
                        return (self.lhs.lhs,lpath[1][0],AstRoot(other,AstBinaryOperator(lpath[0].rhs,'+',rpath[0].rhs)))
                        
                    
                raise ValueError('Unable to reduce forked product.')
            
            else:
                raise ValueError('Unable to reduce forked path.')
            
        else:
            raise ValueError('Path and node are not compatible.')

class AstRoot(AstNode):
    def __init__(self,target,power):
        self.target = target
        if isinstance(power, (float,int)):
            self.power = AstConstant(float(power))
        else:
            self.power = power
    def evaluate(self, variables={}):
        return self.target.evaluate(variables)**(1/self.power.evaluate(variables))
    def findVars(self,variables={}):
        self.target.findVars(variables)
        self.power.findVars(variables)
        return variables
    def count(self, asttype):
        if asttype==AstRoot:
            return 1+self.target.count(asttype)+self.power.count(asttype)
        else:
            return self.target.count(asttype)+self.power.count(asttype)
    def searchPath(self, ast):
        if ast == self:
            return [self]
        else:
            powerpath =  self.power.searchPath(ast)
            targetpath = self.target.searchPath(ast)    
                
            if targetpath==[] and powerpath==[]:
                return []
            else:
                return [self,(targetpath,powerpath)]
    def reducePath(self, path, other):
        if path == [self]:
            return self,[],other
        
        elif type(path) == list and path[0] == self and type(path[1]) == tuple:
            targetpath,powerpath = path[1]
            if targetpath == []:
                if powerpath == []:
                    raise ValueError('forked path contain two dead ends.')
                
                # root(target,power) = other -> power = ln(target)/ln(other)
                return(self.power,powerpath,AstBinaryOperator(AstFunctionCall("ln", self.target),"/",AstFunctionCall("ln", other)))
            elif powerpath == []:
                # root(target,power) = other -> target = other ^ power
                return (self.target,targetpath,AstBinaryOperator(other,"^",self.power))
        else:
            raise ValueError('Path and node are not compatible.')

    def simplify(self):
        if self.count(AstVariable):
            return self
        else:
            return AstConstant(self.evaluate())
    def __eq__(self, other):
        if type(other)==AstRoot:
            return self.power==other.power and self.target==other.target
        else:
            return False

    def __str__(self):
        
        return "root(" + str(self.power) +","+ str(self.target) +")"

        
    def __repr__(self):
        return "AstRoot(%r,%r)"%(self.target,self.power)
class AstNegation(AstNode):
    
    def __init__(self,target):
        self.target = target
        self.precedence = 0
    
    def evaluate(self, variables={}):
        
        return -self.target.evaluate(variables)

    def findVars(self,variables={}):
        self.target.findVars(variables)
        
    def simplify(self):
        if type(self.target) == AstConstant:
            return AstConstant(self.evaluate())
        else:
            self.target = self.target.simplify()
            
            if type(self.target) == AstBinaryOperator and self.target.op == "*":
                # -(c*x) -> -c * x 
                if type(self.target.lhs) == AstConstant:
                    self.target.lhs.value = -self.target.lhs.value
                    return self.target
                
                # -(x*c)  -> x * -c 
                if type(self.target.rhs) == AstConstant:
                    self.target.rhs.value = -self.target.rhs.value
                    return self.target

            # -(x-y) -> y-x
            if type(self.target) == AstBinaryOperator and self.target.op == "-":
                
                self.target.lhs.value,self.target.rhs.value = self.target.rhs.value,self.target.lhs.value
                return self.target
                
            # -(-(x)) -> x
            if type(self.target) == AstNegation:
                
                return self.target.target

            return self

    def count(self, asttype):
        if asttype==AstNegation:
            return 1+self.target.count(asttype)
        else:
            return self.target.count(asttype)

    def __str__(self):
        
        return "-" + str(self.target)
    
    def __repr__(self):
        return "AstNegation(%r)"%self.target
    def __eq__(self, other):
        if type(other)==AstNegation:
            return self.target==other.target
        else:
            return False
    def searchPath(self, ast):
        path = self.target.searchPath(ast)
        if ast == self:
            return [self]+path
        else:
            if path == []:
                return []
            else:
                return [self]+path
    
    def reducePath(self,path,other):
        if type(path) == list and path[0] == self:
            return(self.target,path[1:],AstNegation(other))
        else:
            raise ValueError('Path and node are not compatible.')


class AstFunctionCall(AstNode):
    
    def __init__(self,func,target):
        self.func = func
        self.target = target
        
    def evaluate(self, variables={}):
        
        return BUILTIN_FUNCTIONS[self.func](self.target.evaluate(variables))
        
    def findVars(self,variables={}):
        self.target.findVars(variables)
        return variables

    def simplify(self):
        if type(self.target) == AstConstant:
            return AstConstant(self.evaluate())
        else:
            self.target = self.target.simplify()
            return self
        
    def count(self, asttype):
        if asttype==AstFunctionCall:
            return 1+self.target.count(asttype)
        else:
            return self.target.count(asttype)
        
    def __str__(self):
        
        return self.func + "(" + str(self.target) + ")"
    
    def __repr__(self):
        return "AstFunctionCall(%r,%r)"%(self.func,self.target)
    def __eq__(self, other):
        if type(other)==AstFunctionCall:
            return (self.target==other.target)and(self.func==other.func)
        else:
            return False
    def searchPath(self, ast):
        path = self.target.searchPath(ast)
        if self==ast:
            return [self]+path
        else:
            if path == []:
                return []
            else:
                return [self]+path
    
    def reducePath(self,path,other):
        if type(path) == list and path[0] == self:
            
            if self.func == 'sqrt':
                # sqrt(target) = other -> target = other ^ 2  
                return(self.target,path[1:],AstBinaryOperator(other,'^',AstConstant(2.0)))
            elif self.func == 'exp':
                # exp(target) = other -> target = ln(other)  
                return(self.target,path[1:],AstFunctionCall('ln',other))
            elif self.func == 'ln':
                # ln(target) = other -> target = exp(other)  
                return(self.target,path[1:],AstFunctionCall('exp',other))
            elif self.func == 'log':
                # log(target) = other -> target = 10 ^ other  
                return(self.target,path[1:],AstBinaryOperator(AstConstant(10.0),'^',other))
            elif self.func == 'sin':
                # sin(target) = other -> target = asin(other)  
                return(self.target,path[1:],AstFunctionCall('asin',other))
            elif self.func == 'cos':
                # cos(target) = other -> target = acos(other)  
                return(self.target,path[1:],AstFunctionCall('acos',other))
            elif self.func == 'tan':
                # tan(target) = other -> target = atan(other)  
                return(self.target,path[1:],AstFunctionCall('atan',other))
            elif self.func == 'sinh':
                # sinh(target) = other -> target = asinh(other)  
                return(self.target,path[1:],AstFunctionCall('asinh',other))
            elif self.func == 'cosh':
                # cosh(target) = other -> target = acosh(other)  
                return(self.target,path[1:],AstFunctionCall('acosh',other))
            elif self.func == 'tanh':
                # tanh(target) = other -> target = atanh(other)  
                return(self.target,path[1:],AstFunctionCall('atanh',other))
            elif self.func == 'asin':
                # asin(target) = other -> target = sin(other)  
                return(self.target,path[1:],AstFunctionCall('sin',other))
            elif self.func == 'acos':
                # acos(target) = other -> target = cos(other)  
                return(self.target,path[1:],AstFunctionCall('cos',other))
            elif self.func == 'atan':
                # atan(target) = other -> target = tan(other)  
                return(self.target,path[1:],AstFunctionCall('tan',other))
            elif self.func == 'asinh':
                # asinh(target) = other -> target = sinh(other)  
                return(self.target,path[1:],AstFunctionCall('sinh',other))
            elif self.func == 'acosh':
                # acosh(target) = other -> target = cosh(other)  
                return(self.target,path[1:],AstFunctionCall('cosh',other))
            elif self.func == 'atanh':
                # atanh(target) = other -> target = tanh(other)  
                return(self.target,path[1:],AstFunctionCall('tanh',other))
            else:
                raise ValueError('Unsupported builtin function %s in reducePath.'%self.func)
            
        else:
            raise ValueError('Path and node are not compatible.')
    