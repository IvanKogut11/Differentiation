#!/usr/bin/env python3

import argparse
from dif_main import DerivativeCalculator
from utils.dif_utils import Errors
import sys


POSSIBLE_VARIABLES = set('qwrtyuiopasdfghjklzxcvbnm')


def possible_variable(s):
    if s not in POSSIBLE_VARIABLES:
        raise argparse.ArgumentTypeError('\nNot valid variable.\n'
                                         'Please choose between valid '
                                         'ones:\n' +
                                         ', '.join(possible_variables))
    return s


def handle():
    parser = argparse.ArgumentParser()
    parser.add_argument('exp', help='Expression to differentiate')
    parser.add_argument('-v', '--variable', help='Variable by which'
                        'derivative is taken', type=possible_variable,
                        default='x')
    args = parser.parse_args()
    expression = args.exp
    variable = args.variable
    calculator = DerivativeCalculator()
    try:
        print(calculator.get_derivative(expression, variable))
    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(5)


if __name__ == "__main__":
    handle()
