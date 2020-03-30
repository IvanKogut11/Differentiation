#!usr/bin/env python3


from utils.dif_utils import Node
from utils.dif_utils import (is_number, get_float_number_str_or_input_str,
                             is_operator)


EPS = 0.00000000001


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def get_truncated_value(value, decimals=0):
    sign = 1 if value >= 0 else -1
    return truncate(value + sign * EPS, decimals)


def simplify_tree_and_get_it(root_node, variable):
    if root_node.son1 is None and root_node.son2 is None:
        return root_node
    son1_simplified = None
    son2_simplified = None
    if root_node.son1 is not None:
        son1_simplified = simplify_tree_and_get_it(root_node.son1, variable)
        son1_simplified.value = (get_float_number_str_or_input_str(
                                son1_simplified.value))
    if root_node.son2 is not None:
        son2_simplified = simplify_tree_and_get_it(root_node.son2, variable)
        son2_simplified.value = (get_float_number_str_or_input_str(
            son2_simplified.value))
    return SIMPLIFYING_FUNCS[root_node.value](son1_simplified,
                                              son2_simplified)


def lg_simplify(son1, son2):
    if son1.value == '10.0':
        return Node('1.0')
    return Node('lg', son1=son1)


def ln_simplify(son1, son2):
    if son1.value == 'e':
        return Node('1.0')
    return Node('ln', son1=son1)


def arccot_simplify(son1, son2):
    if son1.value == '0.0':
        return Node('pi/2', is_complex=True)
    if son1.value == '1.0':
        return Node('pi/4', is_complex=True)
    return Node('arccot', son1=son1)


def arctan_simplify(son1, son2):
    if son1.value == '0.0':
        return Node('0.0')
    if son1.value == '1.0':
        return Node('pi/4', is_complex=True)
    return Node('arctan', son1=son1)


def arccos_simplify(son1, son2):
    if son1.value == '0.0':
        return Node('pi/2', is_complex=True)
    if son1.value == '1.0':
        return Node('0.0')
    if son1.value == '-1.0':
        return Node('pi')
    return Node('arccos', son1=son1)


def arcsin_simplify(son1, son2):
    if son1.value == '0.0':
        return Node('0.0')
    if son1.value == '1.0':
        return Node('pi/2', is_complex=True)
    if son1.value == '-1.0':
        return Node('3pi/2', is_complex=True)
    return Node('arcsin', son1=son1)


def cot_simplify(son1, son2):
    if (son1.value == '/' and son1.son1.value == 'pi' and
            get_float_number_str_or_input_str(son1.son2.value) == '2.0'):
        return Node('0.0')
    if (son1.value == '/' and son1.son1.value == 'pi' and
            get_float_number_str_or_input_str(son1.son2.value) == '4.0'):
        return Node('1.0')
    return Node('cot', son1=son1)


def tan_simplify(son1, son2):
    if son1.value == '0.0':
        return Node('0.0')
    if (son1.value == '/' and son1.son1.value == 'pi' and
            get_float_number_str_or_input_str(son1.son2.value) == '4.0'):
        return Node('1.0')
    return Node('tan', son1=son1)


def cos_simplify(son1, son2):
    if son1.value == '0.0':
        return Node('1.0')
    if (son1.value == '/' and son1.son1.value == 'pi' and
            get_float_number_str_or_input_str(son1.son2.value) == '2.0'):
        return Node('0.0')
    if son1.value == 'pi':
        return Node('-1.0')
    return Node('cos', son1=son1)


def sin_simplify(son1, son2):
    if (son1.value == '/' and son1.son1.value == 'pi' and
            get_float_number_str_or_input_str(son1.son2.value) == '2.0'):
        return Node('1.0')
    if son1.value in ({'0.0'} | {'pi'}):
        return Node('0.0')
    return Node('sin', son1=son1)


def unary_plus_simplify(son1, son2):
    return son1


def unary_minus_simplify(son1, son2):
    if son1.value == '0.0':
        return Node('0')
    if is_number(son1.value):
        return Node(str(-float(son1.value)))
    cnt = 1
    while son1.value == 'neg':
        cnt += 1
        son1 = son1.son1
    return Node('neg', son1=son1, is_complex=True) if cnt % 2 != 0 else son1


def pow_simplify(son1, son2):
    if son2.value == '0.0' or son1.value == '1.0':
        return Node('1.0')
    if son2.value == '1.0':
        return son1
    return Node('^', son1=son1, son2=son2, is_complex=True)


def div_simplify(son1, son2):
    if is_number(son1.value) and is_number(son2.value):
        return Node(str(get_truncated_value(
            float(son1.value) / float(son2.value), 7)))
    if son2.value == '1.0':
        return son1
    if son1.value == '0.0':
        return Node('0.0')
    if son1.value == son2.value:
        return Node('1.0')
    return Node('/', son1=son1, son2=son2, is_complex=True)


def mult_simplify(son1, son2):
    if is_number(son1.value) and is_number(son2.value):
        return Node(str(get_truncated_value(
            float(son1.value) * float(son2.value), 7)))
    if son1.value == '0.0' or son2.value == '0.0':
        return Node('0')
    if son1.value == '1.0':
        return son2
    if son2.value == '1.0':
        return son1
    if son2.value == 'neg' and is_number(son1.value):
        return mult_simplify(Node(str(get_truncated_value(
            float(son1.value) * -1.0, 7))), son2.son1)
    if son1.value == 'neg' and is_number(son2.value):
        return mult_simplify(Node(str(get_truncated_value(
            float(son2.value) * -1.0, 7))), son1.son1)
    if (is_number(son1.value) and son2.value == '*' and
            is_number(son2.son1.value)):
        return mult_simplify(Node(str(get_truncated_value(
            float(son1.value) * float(son2.son1.value), 7))), son2.son2)
    if (is_number(son2.value) and son1.value == '*' and
            is_number(son1.son1.value)):
        return mult_simplify(Node(str(get_truncated_value(
            float(son2.value) * float(son1.son1.value), 7))))
    if son1.value == '-1.0':
        return Node('neg', son2)
    if is_number(son2.value):
        return Node('*', son1=son2, son2=son1, is_complex=True)
    return Node('*', son1=son1, son2=son2, is_complex=True)


def binary_minus_simplify(son1, son2):
    if is_number(son1.value) and is_number(son2.value):
        return Node(str(get_truncated_value(
            float(son1.value) - float(son2.value), 7)))
    if son1.value == '0.0':
        return unary_minus_simplify(son2, son1)
    if son2.value == '0.0':
        return son1
    return _deep_simplify_for_minus_and_plus('-', son1, son2)


def binary_plus_simplify(son1, son2):
    if is_number(son1.value) and is_number(son2.value):
        return Node(str(get_truncated_value(
            float(son1.value) + float(son2.value), 7)))
    if son1.value == '0.0':
        return son2
    if son2.value == '0.0':
        return son1
    return _deep_simplify_for_minus_and_plus('+', son1, son2)


def _deep_simplify_for_minus_and_plus(operation, son1, son2):
    bfs_arr = [(son1, 0)]
    if operation == '-':
        bfs_arr.append((son2, 1))
    else:
        bfs_arr.append((son2, 0))
    nodes_to_sum = []
    n = 2
    i = 0
    while i < n:
        cur_node = bfs_arr[i][0]
        cur_sign = bfs_arr[i][1]
        if not is_operator(cur_node.value) and not cur_node.is_complex:
            nodes_to_sum.append((cur_node, cur_sign))
        elif cur_node.value != '+' and cur_node.value != '-':
            if cur_node.value == 'neg':
                cur_sign += 1
            nodes_to_sum.append((cur_node, cur_sign))
        else:
            bfs_arr.append((cur_node.son1, cur_sign))
            if cur_node.value == '-':
                bfs_arr.append((cur_node.son2, cur_sign + 1))
            else:
                bfs_arr.append((cur_node.son2, cur_sign))
            n += 2
        i += 1
    res_node = None
    plus_dict = {'number': 0.0}
    for cur_tuple in nodes_to_sum:
        cur_node = cur_tuple[0]
        cur_sign = float(pow(-1, cur_tuple[1]))
        if (cur_node.value == '*' and
                (is_number(cur_node.son1.value) and
                 not is_number(cur_node.son2.value) and
                 not is_operator(cur_node.son2.value) and
                 not cur_node.son2.is_complex)):
            coef = float(cur_node.son1.value) * cur_sign
            if cur_node.son2.value in plus_dict.keys():
                plus_dict[cur_node.son2.value] += coef
            else:
                plus_dict[cur_node.son2.value] = coef
        elif not is_operator(cur_node.value) and not cur_node.is_complex:
            if is_number(cur_node.value):
                plus_dict['number'] = get_truncated_value(
                    plus_dict['number'] + float(cur_node.value) * cur_sign, 7)
            elif cur_node.value in plus_dict.keys():
                plus_dict[cur_node.value] += cur_sign
            else:
                plus_dict[cur_node.value] = cur_sign
        else:
            if cur_node.value == 'neg':
                cur_node = cur_node.son1
            if res_node is None:
                if cur_sign < 0:
                    res_node = Node('neg', cur_node)
                else:
                    res_node = cur_node
            else:
                if cur_sign < 0:
                    res_node = Node('-', son1=res_node, son2=cur_node,
                                    is_complex=True)
                else:
                    res_node = Node('+', son1=res_node, son2=cur_node,
                                    is_complex=True)
    if plus_dict['number'] != 0.0:
        if res_node is not None:
            if plus_dict['number'] < 0:
                res_node = Node('-', res_node,
                                Node(str(-plus_dict['number'])))
            else:
                res_node = Node('+', res_node, Node(str(plus_dict['number'])))
        else:
            res_node = Node(str(plus_dict['number']))
    for x in plus_dict.keys():
        if x != 'number':
            if res_node is not None:
                if plus_dict[x] < 0:
                    res_node = Node('-', res_node,
                                    mult_simplify(Node(str(-plus_dict[x])),
                                                  Node(x)))
                else:
                    res_node = Node('+', res_node,
                                    mult_simplify(Node(str(plus_dict[x])),
                                                  Node(x)))
            else:
                if plus_dict[x] < 0:
                    res_node = Node('neg',
                                    mult_simplify(Node(str(plus_dict[x])),
                                                  Node(x)))
                else:
                    res_node = mult_simplify(Node(str(plus_dict[x])),
                                             Node(x))
    res_node.is_complex = True
    return res_node


SIMPLIFYING_FUNCS = {
    'lg': lg_simplify,
    'ln': ln_simplify,
    'arccot': arccot_simplify,
    'arctan': arctan_simplify,
    'arccos': arccos_simplify,
    'arcsin': arcsin_simplify,
    'cot': cot_simplify,
    'tan': tan_simplify,
    'cos': cos_simplify,
    'sin': sin_simplify,
    'pos': unary_plus_simplify,
    'neg': unary_minus_simplify,
    '^': pow_simplify,
    '*': mult_simplify,
    '/': div_simplify,
    '+': binary_plus_simplify,
    '-': binary_minus_simplify}
