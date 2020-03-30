# Task: 
	Differentiation
# Programmer: 
    Kogut Ivan Valentinovich ФИИТ-101 
# Description:
	Programm which calculates derivative of a function
# Available objects:
	( - left 
	) - right bracket
    + - plus as binary operator
	+ - plus as unary operator
    - - minus as binary operator
    - - minus as unary operator
    * - multiplication as binary operator
    / - division as binary operator
    ^ - powering as binary operator
    sin - sine as unary function operator
    cos - cosine as unary function operator
    tan - tangent as unary function operator
    cot - cotangent as unary function operator
    arcsin - arcsine as unary function operator
    arccos - arccosine as unary function operator
    arctan - arctangent as unary function operator
    arccot - arccotangent as unary function operator
    ln - natural logarithm as unary function operator
    lg - decimal logarithm as unary function operator
	e - constant e
	pi - contant pi
	['a'...'z'] - variables
	numbers
# Example of usage:
	python Differentiation.py arctan(x)
__!!!If you want to write unary minus in the beginnig of expression, wrap whole expression into ''__:
+ python Differentiation.py '-arctan(x)+3'
# Rules of writing expression:
	1. If you write unary function, argument must be in brackets:
		sin(x) - Correct
		sinx - Incorrect (It is identified as: s*i*n*x)
	2. If variable or unary function follows number, it is identified as number is a power of left object:
		sin(x)35z2 - Identified as: sin(x) ^ 35 * z ^ 2
	BUT!:	35sin(x)z2 - Identified as: 35 * sin(x) * z ^ 2 
--------------------------------------------------------------
####  positional arguments:
  exp - Expression to differentiate

#### optional arguments:
  -h, --help - show this help message and exit

