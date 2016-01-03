'''
Created on 18.10.2015

@author: michi
'''

import logging
import string
import math
from mathx import ast
from mathx.builtins import BUILTIN_FUNCTIONS
 
log = logging.getLogger('mathx.formula')

class Token:
    '''
      operator '+', '-', '*', '/' or '(' or ')' or None (end-of-string marker).
               ' ' means number
      precedence:
        -1 number
        0  terminator (')' or EOS) or comma ','
        1  '+','-' 
        2  '*','/' 
        3 '^' 
        15 '(', builtin functions
    
     numeric value, if precedence == -1
        for groups and builtin function, value is set to 1.0 or -1.0
        in order to reflect a minus sign, which immediately precedes
        the builtin function or group like in "-(a+b)" or "a*-sin(x)"
    '''
    
    def __init__(self,operator,precedence,sign):
        self.operator = operator
        self.precedence = precedence
        self.value = sign
    
    @staticmethod
    def newOperator(operator,precedence):
        return Token(operator,precedence,1.0)

    @staticmethod
    def newBuiltin(operator,sign):
        return Token(operator,0xf,sign)

    @staticmethod
    def newOpeningParentheses(sign):
        return Token('(',0xf,sign)

    @staticmethod
    def newClosingParentheses():
        return Token(')',0,1.0)

    @staticmethod
    def newNumber(value):
        return Token('',-1,value)
    
    @staticmethod
    def newVariable(variable,sign):
        return Token(variable,-1,sign)

    @staticmethod
    def newEOS():
        return Token(None,0,1.0)

    def isNumber(self):
        return self.precedence < 0
    
    def hasAst(self):
        return hasattr(self,"ast") or self.isNumber()
    
    def getAst(self):
        if hasattr(self,"ast"):
            return self.ast
        elif self.isNumber():
            if self.operator == '':
                return ast.AstConstant(self.value)
            elif self.value < 0:
                return ast.AstNegation(ast.AstVariable(self.operator))
            else:
                return ast.AstVariable(self.operator)
        else:
            return None
            
    def setAst(self,ast):
        self.ast = ast

    def __str__(self):
        if self.operator == None:
            return "EOS"
        
        if self.precedence < 0 and self.operator == '':
            return str(self.value)
        
        if hasattr(self,"ast"):
            return str(self.ast)
        
        return self.operator
    
    def __repr__(self):
        return str(self)

class ParseException(Exception):
    
    def __init__(self,message,formula,position=None):
        Exception.__init__(self,message)
        self.formula = formula
        if position is not None:
            self.position = position
    def __str__(self):
        if hasattr(self, "position"):
            return "%s in %s at position %s"%(", ".join(self.args),self.formula,self.position)
        else:
            return "%s in %s"%(", ".join(self.args),self.formula)
    def __repr__(self):
        if hasattr(self, "position"):
            return "ParseException(%r,%r,%r)"%(self.args[0],self.formula,self.position)
        else:
            return "ParseException(%r,%r)"%(self.args[0],self.formula)

GREEK_LETTERS = "".join([chr(i) for i in range(0x3b1,0x3ca)])

class Parser(object):
    '''
       Parser for mathematic formulae.
    '''
    
    def __init__(self,formula):
        self.formula = formula
    
    def _skipWhite(self):
        
        while (self.position < len(self.formula) and
               self.formula[self.position] in string.whitespace):
            self.position += 1
            
        if self.position >= len(self.formula):
            return None
        else:
            return self.formula[self.position]
    
    def _advance(self):
        self.position += 1
        if self.position >= len(self.formula):
            return None
        else:
            return self.formula[self.position]
    
    def _pushToken(self):
        
        c = self._skipWhite()
        
        if c == None:
            self.stack.append(Token.newEOS())
            if (log.isEnabledFor(logging.DEBUG)):
                log.debug("_pushToken(EOS): stack is now %s"%self.stack)
            return False
            
        token = None
        sign = 1.0
        
        if c == "(":
            token = Token.newOpeningParentheses(sign)
            c = self._advance()
        elif c == ")":
            token = Token.newClosingParentheses()
            c = self._advance()
        elif c == ",":
            token = Token.newOperator(c,0)
            c = self._advance()
        elif c == "^":
            token = Token.newOperator(c,3)
            c = self._advance()
        elif c == "/" or c == "*":
            token = Token.newOperator(c,2)
            c = self._advance()
        elif c == "+":
            token = Token.newOperator(c,1)
            c = self._advance()
        elif c == "-":
            # check, whether this is a sign after an operator or at the start of an expression.
            if (len(self.stack) <= 0 or
                self.stack[-1].precedence > 0):
                
                c = self._advance()
                
                if c != None:
                    c = self._skipWhite()
                
                if c == None:
                    raise ParseException("Unexpected end of formula after minus sign.",self.formula,self.position)
                
                sign = -1.0;
                
                if c=='-':
                    raise ParseException("Formula contains superfluous minus signs.",self.formula,self.position)
                
                if c=='(':
                    token = Token.newOpeningParentheses(sign);
                    c = self._advance()
                    
            else:
                # binary minus operator.
                token = Token.newOperator(c,1)
                c = self._advance()
        
        if token == None:
           
            # check for identifier
            if c in string.ascii_letters or c in GREEK_LETTERS or c == "_":
                
                spos = self.position
                c = self._advance()
                
                # valid variable names are _asdf123 ___3 _asd2_3d
                
                while (c != None and
                       (c in string.ascii_letters or
                        c in GREEK_LETTERS or
                        c == '_' or c in string.digits)):
                    c = self._advance()

                variable = self.formula[spos:self.position]
                
                # FIXME check for builtin function
                func = BUILTIN_FUNCTIONS.get(variable)
                
                if func == None:
                
                    if self.variables == None:
                        # AST parsing
                        token = Token.newVariable(variable,sign)
                    else: 
                        # classical, immediate evaluation
                        value = self.variables.get(variable)
                
                        if value == None:
                            raise ParseException("Formula contains unknown variable [%s]."%variable,self.formula,self.position)

                        token = Token.newNumber(value*sign)
                
                else:
                    c = self._skipWhite()
                    
                    if c != "(":
                        raise ParseException("Formula does not contain an openeing paraentheses after builin function [%s]."%variable,self.formula,self.position)
                    
                    c = self._advance()
   
                    token = Token.newBuiltin(variable,sign)
                
            elif c in string.digits or c == ".":
                
                spos = self.position
                ndigits = 0
                
                # number befor the decimal point
                while (c != None and
                       c in string.digits):
                    c = self._advance()
                    ndigits += 1
                
                # decimal point present?
                if (self.position < len(self.formula) and
                       c == '.'):
                    
                    c = self._advance()
                
                    # digits after the decimal point
                    while (c != None and
                       c in string.digits):
                        c = self._advance()
                        ndigits += 1
                        
                # no digits so far
                if ndigits == 0:
                    raise ParseException("Formula contains a plain dot.",self.formula,self.position)
                
                # check for exponent
                if c == 'E' or c == 'e':
                    
                    edigits = 0
                    # check for sign of exponent
                    c = self._advance()
                    
                    if c == '+' or c == '-':
                        c = self._advance()
                    
                    # digits after the decimal point
                    while (c != None and
                       c in string.digits):
                        c = self._advance()
                        edigits += 1
                    
                    if edigits == 0:
                        raise ParseException("Formula contains number with no digist after exponent.",self.formula,self.position)
                 
                numberString = self.formula[spos:self.position]
                token = Token.newNumber(float(numberString)*sign)
            
            else:
                raise ParseException("Formula contains unexpected character [%s]."%c,self.formula,self.position)
                
        self.stack.append(token)
    
        if (log.isEnabledFor(logging.DEBUG)):
            log.debug("_pushToken: stack is now %s"%self.stack)
    
        return True
    
    def _reduce(self):
        
        if len(self.stack)<4:
            return False
        
        last = self.stack[-1];
        last1 = self.stack[-2];
        last2 = self.stack[-3];
        last3 = self.stack[-4];
        
        if last3.precedence == 0xf and last2.isNumber() and last1.operator == ')':
        
            func = BUILTIN_FUNCTIONS.get(last3.operator)
        
            # take into account sign before brace...
            if func != None:
                # builtin function
                if type(last2.value) == tuple:
                    # multi-arg functions.
                    last2.value = last3.value * func(*last2.value)
                else:
                    last2.value = last3.value * func(last2.value)
            else:
                # opening brace
                last2.value *= last3.value;
            
            # x( <number> ) yyy -> x( <number> yyy
            self.stack.pop(-2)
            # x( <number> yyy -> <number> yyy
            self.stack.pop(-3)
            
            if (log.isEnabledFor(logging.DEBUG)):
                log.debug("_reduce(parentheses): stack is now %s"%self.stack)

            return True
        
        
        # <number> <op1> <number> <op2>
        if last3.isNumber() and last1.isNumber() :
            
            # <op1> has a lower precedence than pending <op2>, do nothing
            if last2.precedence < last.precedence:
                return False
             
            # exponentiation is right-associative.
            if last.precedence == 3 and last2.precedence == 3:
                return False
            
            if last2.operator == ',':
                if type(last3.value) == tuple:
                    last3.value += (last1.value,)
                else:
                    last3.value = (last3.value,last1.value)
            elif last2.operator == '+':
                last3.value += last1.value
            elif last2.operator == '-':
                last3.value -= last1.value
            elif last2.operator == '*':
                last3.value *= last1.value;
            elif last2.operator == '/':
                last3.value /= last1.value;
            elif last2.operator ==  '^':
                last3.value = math.pow(last3.value,last1.value);
            else:
                return False
            
            # <number> <op1> <number> <op2> -> <number> <op2> -> 
            self.stack.pop(-2)
            self.stack.pop(-2)
            
            if (log.isEnabledFor(logging.DEBUG)):
                log.debug("_reduce(binary): stack is now %s"%self.stack)

            return True

        return False
    
    def _getValue(self):
        if (len(self.stack) != 2 or
            not self.stack[0].isNumber() or 
            self.stack[1].operator != None  or
            type(self.stack[0].value) == tuple):
            raise ParseException("Cannot reduce formula.",self.formula,self.position);
        
        return self.stack[0].value;
    
    def evaluate(self, variables = {}):
        
        self.variables = variables
        self.stack = []
        self.position = 0
        
        while self._pushToken():
            while self._reduce():
                pass
        
        while self._reduce():
            pass
        
        return self._getValue()

    def _reduceAst(self):
        
        if len(self.stack)<4:
            return False
        
        last = self.stack[-1];
        last1 = self.stack[-2];
        last2 = self.stack[-3];
        last3 = self.stack[-4];
        
        if last3.precedence == 0xf and last2.hasAst() and last1.operator == ')':
        
            func = BUILTIN_FUNCTIONS.get(last3.operator)
        
            # take into account sign before brace...
            if func != None:
                
                ast2 = last2.getAst()
                
                if last3.operator == "root":

                    if type(ast2) != tuple or len(ast2) != 2:
                        raise ParseException("root must have exaclty two positional arguments.",self.formula,self.position);
                    
                    # root operator
                    if last3.value < 0.0 :
                        last2.ast = ast.AstNegation(ast.AstRoot(ast2[1],ast2[0]))
                    else:
                        last2.ast = ast.AstRoot(ast2[1],ast2[0])
                    
                else:
                    if type(ast2) == tuple:
                        raise ParseException("builtin function must not have more than one positional argument.",self.formula,self.position);

                    # builtin function
                    if last3.value < 0.0 :
                        last2.ast = ast.AstNegation(ast.AstFunctionCall(last3.operator,ast2))
                    else:
                        last2.ast = ast.AstFunctionCall(last3.operator,ast2)
                    
            else:
                # open brace with negation
                if last3.value < 0.0 :
                    last2.ast = ast.AstNegation(last2.getAst())
            
            # x( <number> ) yyy -> x( <number> yyy
            self.stack.pop(-2)
            # x( <number> yyy -> <number> yyy
            self.stack.pop(-3)
            
            if (log.isEnabledFor(logging.DEBUG)):
                log.debug("_reduceAst(parentheses): stack is now %s"%self.stack)

            return True
        
        
        # <number> <op1> <number> <op2>
        if last3.hasAst() and last1.hasAst() :
            
            # <op1> has a lower precedence than pending <op2>, do nothing
            if last2.precedence < last.precedence:
                return False
             
            # exponentiation is right-associative.
            if last.precedence == 3 and last2.precedence == 3:
                return False
            
            if last2.operator == ',':
                
                ast3 = last3.getAst()
                
                if type(ast3) == tuple:
                    last3.ast = ast3 + (last1.getAst(),)
                else:
                    last3.ast = (ast3,last1.getAst())

            elif last2.operator == '+' or last2.operator == '-' or last2.operator == '*' or last2.operator == '/'or last2.operator ==  '^':
                last3.ast = ast.AstBinaryOperator(last3.getAst(),last2.operator,last1.getAst());
            else:
                return False
            
            # <number> <op1> <number> <op2> -> <number> <op2> -> 
            self.stack.pop(-2)
            self.stack.pop(-2)
            
            if (log.isEnabledFor(logging.DEBUG)):
                log.debug("_reduceAst(binary): stack is now %s"%self.stack)

            return True

        return False

    def _getAst(self):
        if (len(self.stack) != 2 or
            not (self.stack[0].hasAst()) or 
            self.stack[1].operator != None or
            type(self.stack[0].getAst()) == tuple):
            raise ParseException("Cannot reduce formula.",self.formula,self.position)
            
        return self.stack[0].getAst()

    def parseAst(self):
        
        self.variables = None
        self.stack = []
        self.position = 0
        
        while self._pushToken():
            while self._reduceAst():
                pass
        
        while self._reduceAst():
            pass
        
        return self._getAst()
