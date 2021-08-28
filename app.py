#!/usr/bin/python3

from __future__ import annotations
import sys
from itertools import permutations
from enum import Enum, auto
from Rational import Rational
from Expression import Expression, Operation, Token, find_matching_parens
from argparse import ArgumentParser


def get_permutations(numbers: list) -> set:
    all = set()
    for l in range(len(numbers)):
        perm = set(permutations(numbers, l + 1))
        all = all.union(perm)
    return all


def init_argparse() -> ArgumentParser:
    parser = ArgumentParser(prog="exparser", usage="%(prog)s [options] [expression]", description="Parse an arithmetic expression.")
    parser.add_argument(
        "-f", "--float-only", action="store_true", default=False, required=False
    )
    parser.add_argument(
        "expression", nargs="*"
    )

    return parser


def main(parser=init_argparse(), argv=sys.argv, should_print=True) -> str:
    args = parser.parse_args(argv)

    ex = Expression.parse(" ".join(args.expression))
    result = ex.calculate().to_string(args.float_only)
    if should_print:
        print(result)
    return result


if __name__ == "__main__":
    main()
