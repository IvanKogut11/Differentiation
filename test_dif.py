#!/usr/bin/env python3


import unittest
from dif_main import DerivativeCalculator, get_infix_notation
from utils.dif_utils import (ExtraBracketsError,
                             TwoOperatorsAtTimeError,
                             UnaryOperatorWithoutArgumentError,
                             IrrelevantSymbolError,
                             NotEnoughArgumentsError)


class InfixNotationTests(unittest.TestCase):

    def setUp(self):
        self.Calculator = DerivativeCalculator()

    def tearDown(self):
        pass

    def test_unary_operators(self):
        self.assertEqual(['5'], get_infix_notation('5'))
        self.assertEqual(['5'], get_infix_notation('((5))'))
        self.assertEqual(['5', 'neg'], get_infix_notation('-5'))
        self.assertEqual(['5', 'pos'], get_infix_notation('+5'))
        self.assertEqual(['x', 'ln'], get_infix_notation('ln(x)'))
        self.assertEqual(['x', 'lg'], get_infix_notation('lg(x)'))
        self.assertEqual(['x', 'cos'], get_infix_notation('cos(x)'))
        self.assertEqual(['x', 'arctan'], get_infix_notation('arctan(x)'))
        self.assertEqual(['x', 'sin'], get_infix_notation('sin(x)'))

    def test_unary_operators_error(self):
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('-')
        with self.assertRaises(TwoOperatorsAtTimeError):
            get_infix_notation('--2')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('arcsin')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('sin')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('cos')

    def test_binary_operators(self):
        self.assertEqual(['3', '5', '+'], get_infix_notation('3+5'))
        self.assertEqual(['343', '53', '^'], get_infix_notation('343^53'))
        self.assertEqual(['45', '3', '2', '^', '^'],
                         get_infix_notation('45^3^2'))
        self.assertEqual(['x', 'y', '*', 'z', '*',
                          '45', 'y', '2', '^', '*', 'z', '*', '+'],
                         get_infix_notation('xyz+45y2z'))

    def test_binary_operators_error(self):
        with self.assertRaises(TwoOperatorsAtTimeError):
            get_infix_notation('23--2')
        with self.assertRaises(TwoOperatorsAtTimeError):
            get_infix_notation('123*-3')
        with self.assertRaises(ExtraBracketsError):
            get_infix_notation('(3+5))')
        with self.assertRaises(ExtraBracketsError):
            get_infix_notation('3*((2/2)')
        with self.assertRaises(ExtraBracketsError):
            get_infix_notation('sin(x')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('x+')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('/5')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('x*3+')

    def test_complex_operator(self):
        self.assertEqual(['5', 'neg', 'x', '*', 'sin'],
                         get_infix_notation('sin(-5x)'))
        self.assertEqual(['x', '3', '^', 'arctan'],
                         get_infix_notation('arctan(x^3)'))
        self.assertEqual(['10', 'lg', '3', 'neg', '^', 'ln'],
                         get_infix_notation('ln(lg(10)^(-3))'))

    def test_complex_operator_errors(self):
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('arcsin(-)')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('sin(sin())')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('x+()')
        with self.assertRaises(NotEnoughArgumentsError):
            get_infix_notation('cos(x/(()))+5')

    def test_combined_operators(self):
        self.assertEqual(['5', 'neg', '32', '3', '^', '*'],
                         get_infix_notation('-5*32^3'))
        self.assertEqual(['5', '2', '^', 'x', '+', 'ln', 'y', 'sin', '*'],
                         get_infix_notation('ln(5^2+x)sin(y)'))
        self.assertEqual(['1', 'x', '20', '^', '20', 'x', '6',
                          '^', '*', '-', '/', 'lg'],
                         get_infix_notation('lg(1/(x^20-20x^6))'))
        self.assertEqual(['x', 'y', '3', '^', '*', '6', '+',
                          'tan', 'neg', 'sin', 'neg'],
                         get_infix_notation('-sin(-tan(xy3+6))'))
        self.assertEqual(['x', 'y', '+', 'z', '*', '32', '*'],
                         get_infix_notation('(x+y)z(32)'))
        self.assertEqual(['z', '3', '+', 'sin'],
                         get_infix_notation('sin(((z)+3))'))
        self.assertEqual(['x', 'neg', 'sin'],
                         get_infix_notation('sin(-((x)))'))

    def test_irrelevant_symbol_error(self):
        with self.assertRaises(IrrelevantSymbolError):
            get_infix_notation('3+5=')
        with self.assertRaises(IrrelevantSymbolError):
            get_infix_notation('3/7*(3~4)')
        with self.assertRaises(IrrelevantSymbolError):
            get_infix_notation('4!')
        with self.assertRaises(IrrelevantSymbolError):
            get_infix_notation('4^[2+3]')
        with self.assertRaises(IrrelevantSymbolError):
            get_infix_notation('1 3x')
        with self.assertRaises(IrrelevantSymbolError):
            get_infix_notation('1 +  3.  2x')
        with self.assertRaises(IrrelevantSymbolError):
            get_infix_notation('132 123')

    def test_operations_with_constants(self):
        self.assertEqual(['pi', 'x', '*'], get_infix_notation('pix'))
        self.assertEqual(['1', 'pi', '3', '*', '+'],
                         get_infix_notation('1+pi*3'))
        self.assertEqual(['pi', 'neg', 't', '*', 'y', '*'],
                         get_infix_notation('-pity'))
        self.assertEqual(['pi', 'pi', '1', '+', '^', '44', 'pi', '*', '-'],
                         get_infix_notation('pi^(pi+1)-44pi'))
        self.assertEqual(['pi', 'pi', '*', 'i', '*', 'p', '*'],
                         get_infix_notation('pipiip'))

    def test_return_zero_if_user_variable_is_not_in_expression(self):
        calc = DerivativeCalculator()
        self.assertEqual(0, calc.get_derivative("(x+5)*y^3", "z"))
        self.assertEqual(0, calc.get_derivative("123+123*123", "x"))
        self.assertEqual(0, calc.get_derivative("pi", "p"))
        self.assertEqual(0, calc.get_derivative("ln(x+y)*a", "b"))

    def test_complex_expressions(self):
        calc = DerivativeCalculator()
        self.assertEqual('(-x) ^ (-2.0)', calc.get_derivative('-x^(-1)', 'x'))
        self.assertEqual('3.0 + 4.0x', calc.get_derivative(
            "x+ xx+x +xx+  x", 'x'))
        self.assertEqual('x ^ (-2.0)', calc.get_derivative("-(x^(-1))", 'x'))
        self.assertEqual('213.0cos(213.0x)',
                         calc.get_derivative('sin(213x  )', 'x'))
        self.assertEqual('2.0x', calc.get_derivative('x ^ 2 + 1', 'x'))
        self.assertEqual('2.0(x + y)',
                         calc.get_derivative('(x+y) ^ 2', 'x'))
        self.assertEqual('(e ^ (xln(x)))(ln(x) + 1.0)',
                         calc.get_derivative('x ^ x', 'x'))
        self.assertEqual('e ^ x', calc.get_derivative('e^x', 'x'))
        self.assertEqual('(1.0 / (x + y))a',
                         calc.get_derivative('ln(x  + y)*a', 'x'))
        self.assertEqual('8.0', calc.get_derivative('6x+3x-1x', 'x'))
        self.assertEqual('-(sin(ln(-x))(-1.0 / (-x)))',
                         calc.get_derivative('cos(  ln(-x))', 'x'))
        self.assertEqual('1.0', calc.get_derivative('lg(10)x', 'x'))
        self.assertEqual('pi/2 + (pi/4)(2.0x)',
                         calc.get_derivative('arccot(0)x +'
                                             ' arccot(1)x^2', 'x'))
        self.assertEqual('(pi/4)(2.0x)',
                         calc.get_derivative('arctan(0)x +'
                                             ' arctan(1)x^2', 'x'))
        self.assertEqual('-pi + pi/2',
                         calc.get_derivative('arccos(1)x - arccos(-1)x'
                                             '+ arccos(0)x', 'x'))
        self.assertEqual('pi/2 - (3pi/2)',
                         calc.get_derivative('arcsin(1)x - arcsin(-1)x'
                                             '+ arcsin(0)x', 'x'))
        self.assertEqual('1.0', calc.get_derivative(
                                'cot(pi  /2)x + cot(pi/  4)x', 'x'))
        self.assertEqual('-1.0', calc.get_derivative(
                                '-tan(pi  /4)x + tan(0.0000)x', 'x'))
        self.assertEqual('2.0',
                         calc.get_derivative('cos(0)x + cos(pi/  2)x'
                                             ' - cos(pi  )x', 'x'))
        self.assertEqual('3.0',
                         calc.get_derivative('2sin(0)x + 3sin(pi /  2)x'
                                             ' - sin(pi  )x', 'x'))
        self.assertEqual('8.0x', calc.get_derivative('+4x^2', 'x'))

    def test_default_expressions(self):
        calc = DerivativeCalculator()
        self.assertEqual('1.0 / (x ^ 2.0 + 1.0)',
                         calc.get_derivative('arctan(x)', 'x'))
        self.assertEqual('-(1.0 / (x ^ 2.0 + 1.0))',
                         calc.get_derivative('arccot(x)', 'x'))
        self.assertEqual('1.0 / ((-(x ^ 2.0) + 1.0) ^ 0.5)',
                         calc.get_derivative('arcsin(x)', 'x'))
        self.assertEqual('-(1.0 / ((-(x ^ 2.0) + 1.0) ^ 0.5))',
                         calc.get_derivative('arccos(x)', 'x'))
        self.assertEqual('1.0 / (cos(x) ^ 2.0)',
                         calc.get_derivative('tan(x)', 'x'))
        self.assertEqual('-(1.0 / (sin(x) ^ 2.0))',
                         calc.get_derivative('cot(x)', 'x'))
        self.assertEqual('cos(x)', calc.get_derivative('sin(x)', 'x'))
        self.assertEqual('-sin(x)',
                         calc.get_derivative('cos(x)', 'x'))
        self.assertEqual('1.0 / (xln(10.0))',
                         calc.get_derivative('lg(x)', 'x'))
        self.assertEqual('(5.0 ^ x)ln(5.0)', calc.get_derivative('5^x', 'x'))
        self.assertEqual('e ^ x', calc.get_derivative('e  ^x', 'x'))

    def test_unary_minus_priority(self):
        calc = DerivativeCalculator()
        self.assertEqual('2.0x', calc.get_derivative('-x^2', 'x'))
        self.assertEqual('2.0x', calc.get_derivative('(-x)^2', 'x'))
        self.assertEqual('-(2.0x)', calc.get_derivative('-(x^2)', 'x'))
        self.assertEqual('(-x) ^ (-2.0)', calc.get_derivative('-x^(-1)', 'x'))
        self.assertEqual('(-x) ^ (-2.0)',
                         calc.get_derivative('(-x)^(-1)', 'x'))
        self.assertEqual('x ^ (-2.0)', calc.get_derivative('-(x^(-1))', 'x'))


if __name__ == "__main__":
    unittest.main()
