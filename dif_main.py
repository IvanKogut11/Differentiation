#!/usr/bin/env python3

import re
import utils.dif_utils as u
from dif_simplifier import simplify_tree_and_get_it


def get_operator_or_none(s, ind):
    if s[ind] in u.SHORT_OP:
        if (ind == 0 or s[ind-1] in ({'('} | u.SHORT_OP)) and s[ind] in '-+':
            return 'neg' if s[ind] == '-' else 'pos'
        return s[ind]
    last_valid_ind = u.get_first_invalid_ind(
        ind, s, lambda i, s: u.is_eng_letter(s[i]))
    cur_s = s[ind:last_valid_ind]
    if cur_s in u.LONG_OP:
        return cur_s
    return None


def add_op_to_stack(stack_op, queue_out, op_tuple):
    cur_pr = u.PRIORITY_DICT[op_tuple[0]]
    while stack_op:
        prev_op = stack_op.pop()
        prev_pr = u.PRIORITY_DICT[prev_op[0]]
        if prev_pr < cur_pr or prev_op[0] == op_tuple[0] == '^':
            stack_op.append(prev_op)
            break
        queue_out.append(prev_op)
    stack_op.append(op_tuple)


def is_there_hidden_operator(s, obj, ind, is_prev_op):
    return ((u.is_operator_func(obj) or not u.is_operator(obj)) and
            ind != 0 and not is_prev_op and s[ind - 1] != '(')


def deal_with_operator_and_return_new_ind(cur_op, stack_op, queue_out, s, i,
                                          is_prev_op):
    if is_prev_op and not u.is_operator_func(cur_op):
        raise u.TwoOperatorsAtTimeError(s, [i - 1, i])
    if is_there_hidden_operator(s, cur_op, i, is_prev_op):
        add_op_to_stack(stack_op, queue_out, ('*', i))
    add_op_to_stack(stack_op, queue_out, (cur_op, i))
    i += len(cur_op) if u.is_operator_func(cur_op) else 1
    return i


def deal_with_operand_and_return_new_ind(stack_op, queue_out, s, i,
                                         is_prev_op):
    n = len(s)
    if s[i].isdigit():
        last_valid_ind = u.get_first_invalid_ind(i, s,
                                                 lambda i, s: s[i].isdigit())
        cur_operand = s[i:last_valid_ind]
        if last_valid_ind < n and s[last_valid_ind] == '.':
            cur_operand += '.'
            last_valid_ind += 1
            nxt_valid_ind = u.get_first_invalid_ind(last_valid_ind, s,
                                                    lambda i, s:
                                                    s[i].isdigit())
            if last_valid_ind == nxt_valid_ind:
                raise u.IrrelevantSymbolError(s, [last_valid_ind])
            cur_operand += s[last_valid_ind:nxt_valid_ind]
            last_valid_ind = nxt_valid_ind
        if is_there_hidden_operator(s, cur_operand, i, is_prev_op):
            add_op_to_stack(stack_op, queue_out, ('^', i - 1))
        i = last_valid_ind
    elif u.is_eng_letter(s[i]):
        cur_operand = s[i]
        if i != n - 1 and s[i:i + 2] == 'pi':
            cur_operand = 'pi'
        if is_there_hidden_operator(s, cur_operand, i, is_prev_op):
            add_op_to_stack(stack_op, queue_out, ('*', i))
        i += len(cur_operand)
    else:
        raise u.IrrelevantSymbolError(s, [i])
    queue_out.append((cur_operand, i - len(cur_operand)))
    return i


def check_for_NotEnoughArgumentsError(s, queue_out):
    operations_st = []
    for cur_tuple in queue_out:
        obj = cur_tuple[0]
        ind = cur_tuple[1]
        if not u.is_operator(obj):
            operations_st.append(obj)
            continue
        if u.is_unary_operator(obj) and not operations_st:
            raise u.NotEnoughArgumentsError(s, [ind])
        if u.is_binary_operator(obj):
            if len(operations_st) < 2:
                raise u.NotEnoughArgumentsError(s, [ind])
            operations_st.pop()


def finish_work_with_stack_op(stack_op, queue_out, s):
    stack_size = len(stack_op)
    for i in range(stack_size - 1, -1, -1):
        cur_el = stack_op.pop()
        if cur_el[0] == '(':
            raise u.ExtraBracketsError(s, [cur_el[1]])
        queue_out.append(cur_el)


def get_infix_notation(s):
    stack_op = []
    queue_out = []
    n = len(s)
    is_prev_op = False
    i = 0
    while i != n:
        if s[i] == '(':
            if is_there_hidden_operator(s, '(', i, is_prev_op):
                add_op_to_stack(stack_op, queue_out, ('*', i))
            stack_op.append(('(', i))
            is_prev_op = False
            i += 1
            continue
        if s[i] == ')':
            j = len(stack_op) - 1
            while stack_op and stack_op[j][0] != '(':
                queue_out.append(stack_op.pop())
                j -= 1
            if len(stack_op) == 0:
                raise u.ExtraBracketsError(s, [i])
            stack_op.pop()
            is_prev_op = False
            i += 1
            continue
        op_or_none = get_operator_or_none(s, i)
        if op_or_none is not None:
            i = deal_with_operator_and_return_new_ind(op_or_none, stack_op,
                                                      queue_out, s,
                                                      i, is_prev_op)
            is_prev_op = True
        else:
            i = deal_with_operand_and_return_new_ind(stack_op, queue_out, s,
                                                     i, is_prev_op)
            is_prev_op = False
    finish_work_with_stack_op(stack_op, queue_out, s)
    check_for_NotEnoughArgumentsError(s, queue_out)
    return [x[0] for x in queue_out]


def check_for_incorrect_spaces(expression):
    n = len(expression)
    last_not_space_ind = -1
    last_space_ind = -2
    for (i, ch) in enumerate(expression):
        if ch != ' ':
            if (last_not_space_ind != -1 and ch.isdigit() and
                    (expression[last_not_space_ind].isdigit() or
                     expression[last_not_space_ind] == '.') and
                    last_space_ind > last_not_space_ind):
                raise u.IrrelevantSymbolError(expression, [last_space_ind])
            last_not_space_ind = i
        else:
            last_space_ind = i


class DerivativeCalculator:

    def __init__(self):
        self.variable = ''

    def get_derivative(self, expression, user_variable=''):
        check_for_incorrect_spaces(expression)
        expression = expression.replace(' ', '')
        infix_notation = get_infix_notation(expression)
        possible_variables = set(
            filter(lambda x: u.is_eng_letter(x) and x != 'e',
                   infix_notation))
        if user_variable not in possible_variables:
            return 0
        root = u.Tree.build_operation_tree_and_get_root(
            infix_notation, user_variable)
        self.variable = user_variable
        dif_root = u.Tree.build_differentiation_tree_and_get_root(
            root, user_variable)
        dif_simplified_root = simplify_tree_and_get_it(
            dif_root, user_variable)
        return str(dif_simplified_root)
