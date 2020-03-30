#!usr/bin/env python3

CONSTANTS = {'e', 'pi'}
SHORT_OP = {'+', '-', '*', '/', '^'}
LONG_OP = {'sin', 'cos', 'tan', 'cot', 'arcsin', 'arccos',
           'arctan', 'arccot', 'ln', 'lg'}
PRIORITY_DICT = {
    '(': 0,
    ')': 0,
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
    'pos': 4,  # Унарный плюс
    'neg': 4,  # Унарный минус
    'sin': 5,
    'cos': 5,
    'tan': 5,
    'cot': 5,
    'arcsin': 5,
    'arccos': 5,
    'arctan': 5,
    'arccot': 5,
    'ln': 5,
    'lg': 5
}


def _create_message(expression, indices):
    n = len(expression)
    t = ["\n", expression, "\n"] + [' '] * n
    for index in indices:
        t[index + 3] = '^'
    return "".join(t)


class Errors(Exception):
    ERROR_TYPE = ''

    def __init__(self, expression, indices):
        super().__init__(self.ERROR_TYPE + '\n' +
                         _create_message(expression, indices))


class ExtraBracketsError(Errors):
    ERROR_TYPE = 'There is the extra bracket'


class TwoOperatorsAtTimeError(Errors):
    ERROR_TYPE = 'There are two operators at a time'


class UnaryOperatorWithoutArgumentError(Errors):
    ERROR_TYPE = 'There is unary operator without an argument'


class IrrelevantSymbolError(Errors):
    ERROR_TYPE = 'There is irrelevant symbol'


class NotEnoughArgumentsError(Errors):
    ERROR_TYPE = 'There are not enough arguments for operator'


class Node:
    def __init__(self, value, son1=None, son2=None, has_variable=False,
                 is_complex=False):
        self.value = value
        self.son1 = son1
        self.son2 = son2
        self.has_variable = has_variable
        self.is_complex = is_complex

    def __str__(self):
        son1_str = str(self.son1 or '')
        son2_str = str(self.son2 or '')
        if is_operator_func(self.value):
            return f'{self.value}({son1_str})'
        if self.value == 'neg':
            if not (self.son1.is_complex or son1_str[0] == '-'):
                return f'-{son1_str}'
            return f'-({son1_str})'
        if self.value in ({'/'} | {'*'} | {'^'}):
            if self.son1.is_complex:
                son1_str = f'({son1_str})'
            if self.son2.is_complex or son2_str[0] == '-':
                son2_str = f'({son2_str})'
            if (self.value == '*' and
                not (is_number(self.son1.value) and
                     is_number(self.son2.value))):
                return f'{son1_str}{son2_str}'
            return f'{son1_str} {self.value} {son2_str}'
        if self.value == '+':
            return f'{son1_str} + {son2_str}'
        if self.value == '-':
            if self.son2.is_complex:
                son2_str = f'({son2_str})'
            return f'{son1_str} - {son2_str}'
        return self.value


class NaturalLogarithm:

    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        return Node('/', der_of_son1, self.node.son1,
                    der_of_son1.has_variable or
                    self.node.son1.has_variable)


class DecimalLogarithm:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        den_node = Node('*', self.node.son1, Node('ln', Node('10')),
                        self.node.son1.has_variable)
        return Node('/', der_of_son1, den_node,
                    der_of_son1.has_variable or den_node.has_variable)


class Arccot:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        sqr_node = Node('^', self.node.son1, Node('2'),
                        has_variable=self.node.has_variable)
        plus_node = Node('+', Node('1'), sqr_node,
                         has_variable=sqr_node.has_variable)
        div_node = Node('/', Node('1'), plus_node, plus_node.has_variable)
        mult_node = Node('*', div_node, der_of_son1,
                         has_variable=div_node.has_variable or
                         der_of_son1.has_variable)
        return Node('neg', mult_node,
                    has_variable=div_node.has_variable or
                    der_of_son1.has_variable)


class Arctan:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        sqr_node = Node('^', self.node.son1, Node('2'),
                        has_variable=self.node.has_variable)
        plus_node = Node('+', Node('1'), sqr_node,
                         has_variable=sqr_node.has_variable)
        div_node = Node('/', Node('1'), plus_node, plus_node.has_variable)
        return Node('*', div_node, der_of_son1,
                    has_variable=div_node.has_variable or
                    der_of_son1.has_variable)


class Arccos:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        sqr_node = Node('^', self.node.son1, Node('2'),
                        has_variable=self.node.has_variable)
        minus_node = Node('-', Node('1'), sqr_node,
                          has_variable=sqr_node.has_variable)
        pow_node = Node('^', minus_node, Node('0.5'),
                        has_variable=minus_node.has_variable)
        div_node = Node('/', Node('1'), pow_node, pow_node.has_variable)
        mult_node = Node('*', div_node, der_of_son1,
                         has_variable=div_node.has_variable or
                         der_of_son1.has_variable)
        return Node('neg', mult_node, has_variable=mult_node.has_variable)


class Arcsin:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        sqr_node = Node('^', self.node.son1, Node('2'),
                        has_variable=self.node.has_variable)
        minus_node = Node('-', Node('1'), sqr_node,
                          has_variable=sqr_node.has_variable)
        pow_node = Node('^', minus_node, Node('0.5'),
                        has_variable=minus_node.has_variable)
        div_node = Node('/', Node('1'), pow_node, pow_node.has_variable)
        return Node('*', div_node, der_of_son1,
                    has_variable=div_node.has_variable or
                    der_of_son1.has_variable)


class Cot:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        sin_node = Node('sin', self.node.son1,
                        has_variable=self.node.has_variable)
        pow_node = Node('^', sin_node, Node('2'), sin_node.has_variable)
        div_node = Node('/', Node('1'), pow_node, pow_node.has_variable)
        mult_node = Node('*', div_node, der_of_son1,
                         div_node.has_variable or
                         der_of_son1.has_variable)
        return Node('neg', mult_node, has_variable=mult_node.has_variable)


class Tan:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        cos_node = Node('cos', self.node.son1,
                        has_variable=self.node.has_variable)
        pow_node = Node('^', cos_node, Node('2'), cos_node.has_variable)
        div_node = Node('/', Node('1'), pow_node, pow_node.has_variable)
        return Node('*', div_node, der_of_son1,
                    div_node.has_variable or der_of_son1.has_variable)


class Cos:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        sin_node = Node('sin', self.node.son1,
                        has_variable=self.node.son1.has_variable)
        mult_node = Node('*', sin_node, der_of_son1,
                         has_variable=sin_node.has_variable or
                         der_of_son1.has_variable)
        return Node('neg', mult_node, has_variable=mult_node.has_variable)


class Sin:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        cos_node = Node('cos', self.node.son1,
                        has_variable=self.node.son1.has_variable)
        return Node('*', cos_node, der_of_son1,
                    has_variable=cos_node.has_variable or
                    der_of_son1.has_variable)


class UnaryMinus:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        return Node('neg', der_of_son1, has_variable=der_of_son1.has_variable)


class UnaryPlus:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        return der_of_son1


class Power:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        if self.node.son1.has_variable and not self.node.son2.has_variable:
            nxt_deg = Node('-', self.node.son2, Node('1'), False)
            pow_node = Node('^', self.node.son1, nxt_deg, True)
            mult1 = Node('*', der_of_son1, pow_node, True)
            return Node('*', self.node.son2, mult1)
        if not self.node.son1.has_variable and self.node.son2.has_variable:
            node2 = Node('ln', self.node.son1)
            mult_node = Node('*', self.node, node2, self.node.has_variable)
            return Node('*', mult_node, der_of_son2,
                        mult_node.has_variable)
        if (not self.node.son1.has_variable and
                not self.node.son2.has_variable):
            return Node('0', has_variable=False)
        if (self.node.son1.has_variable and
                self.node.son2.has_variable):
            ln_node = Node('ln', self.node.son1, has_variable=True)
            g_and_ln_f_node = Node('*', self.node.son2, ln_node,
                                   has_variable=True)
            e_node = Node('^', Node('e'), g_and_ln_f_node, has_variable=True)
            s1_node = Node('*', der_of_son2, ln_node, has_variable=True)
            div_node = Node('/', self.node.son2, self.node.son1,
                            has_variable=True)
            s2_node = Node('*', div_node, der_of_son1, has_variable=True)
            sum_node = Node('+', s1_node, s2_node, has_variable=True)
            return Node('*', e_node, sum_node, has_variable=True)


class Division:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        num_node1 = Node('*', der_of_son1, self.node.son2,
                         der_of_son1.has_variable or
                         self.node.son2.has_variable)
        num_node2 = Node('*', self.node.son1, der_of_son2,
                         self.node.son1.has_variable or
                         der_of_son2.has_variable)
        son1 = Node('-', num_node1, num_node2,
                    num_node1.has_variable or num_node2.has_variable)
        son2 = Node('^', self.node.son2, Node('2'),
                    self.node.son2.has_variable)
        return Node('/', son1, son2, son1.has_variable or son2.has_variable)


class Multiplication:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        son1 = Node('*', der_of_son1, self.node.son2,
                    der_of_son1.has_variable or self.node.son2.has_variable)
        son2 = Node('*', self.node.son1, der_of_son2,
                    self.node.son1.has_variable or der_of_son2.has_variable)
        return Node('+', son1, son2, son1.has_variable or son2.has_variable)


class BinaryPlus:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        has_variable = der_of_son1.has_variable or der_of_son2.has_variable
        return Node('+', der_of_son1, der_of_son2, has_variable)


class BinaryMinus:
    def __init__(self, node):
        self.node = node

    def get_derivative_node(self, der_of_son1, der_of_son2):
        has_variable = der_of_son1.has_variable or der_of_son2.has_variable
        return Node('-', der_of_son1, der_of_son2, has_variable)


class Tree:

    @staticmethod
    def add_has_variable_field(cur_node, variable):
        if cur_node.son1 is None and cur_node.son2 is None:
            cur_node.has_variable = variable == cur_node.value
            return cur_node
        cur_node.has_variable = False
        if cur_node.son1 is not None:
            cur_node.has_variable |= (Tree.add_has_variable_field
                                      (cur_node.son1, variable).has_variable)
        if cur_node.son2 is not None:
            cur_node.has_variable |= (Tree.add_has_variable_field
                                      (cur_node.son2, variable).has_variable)
        return cur_node

    @staticmethod
    def build_operation_tree_and_get_root(infix_notation, variable):
        op_stack = []
        for x in infix_notation:
            if is_unary_operator(x):
                cur_node = Node(x, op_stack.pop())
            elif is_binary_operator(x):
                value_2 = op_stack.pop()
                value_1 = op_stack.pop()
                cur_node = Node(x, value_1, value_2)
            else:
                cur_node = Node(x)
            op_stack.append(cur_node)
        root = op_stack.pop()
        root = Tree.add_has_variable_field(root, variable)
        return root

    @staticmethod
    def build_differentiation_tree_and_get_root(op_node, variable):
        if op_node.son1 is None and op_node.son2 is None:
            if variable == op_node.value:
                return Node('1.0', has_variable=True)
            return Node('0.0')
        der_of_son1 = None
        der_of_son2 = None
        if op_node.son1 is not None:
            der_of_son1 = (Tree.build_differentiation_tree_and_get_root
                           (op_node.son1, variable))
        if op_node.son2 is not None:
            der_of_son2 = (Tree.build_differentiation_tree_and_get_root
                           (op_node.son2, variable))
        cur_op = OPERATIONS_CONSTRUCTIONS[op_node.value](op_node)
        return cur_op.get_derivative_node(der_of_son1, der_of_son2)


OPERATIONS_CONSTRUCTIONS = {'lg': DecimalLogarithm,
                            'ln': NaturalLogarithm,
                            'arccot': Arccot,
                            'arctan': Arctan,
                            'arccos': Arccos,
                            'arcsin': Arcsin,
                            'cot': Cot,
                            'tan': Tan,
                            'cos': Cos,
                            'sin': Sin,
                            'neg': UnaryMinus,
                            'pos': UnaryPlus,
                            '^': Power,
                            '/': Division,
                            '*': Multiplication,
                            '+': BinaryPlus,
                            '-': BinaryMinus}


def is_unary_operator(op):
    return op in (LONG_OP | {'pos', 'neg'})


def is_binary_operator(op):
    return op in SHORT_OP


def get_float_number_str_or_input_str(s):
    if is_number(s):
        return str(float(s))
    return s


def is_number(x):
    if x.isdigit():
        return True
    else:
        try:
            float(x)
            return True
        except ValueError:
            return False


def is_operator_func(op):
    return op in LONG_OP


def is_operator(s):
    return (s != '(' and s != ')' and
            s in PRIORITY_DICT)


def str_operator(operator):
    if operator == 'neg':
        return '-'
    if operator == 'pos':
        return '+'
    return operator


def get_first_invalid_ind(ind, string, pred):
    n = len(string)
    while ind != n and pred(ind, string):
        ind += 1
    return ind


def is_eng_letter(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z'
