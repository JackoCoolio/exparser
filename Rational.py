from __future__ import annotations
from math import gcd, log10, ceil, floor
from decimal import Decimal, InvalidOperation
from typing import List, Sequence, Tuple, Type
from abc import ABC, abstractmethod

def lcm(a: int, b: int) -> int:
    """Finds the least common multiple of any two integers."""

    return abs(a*b) // gcd(a, b)

class Calculatable(ABC):

    @abstractmethod
    def calculate(self) -> Rational:
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def is_expression(self) -> bool:
        pass


def is_digit(x: str) -> bool:
    try:
        int(x)
        return True
    except ValueError:
        return False


class Rational(Calculatable):
    """A class that represents a rational number."""

    def __init__(self, numer: int, denom: int = 1, simplify: bool = True):
        if denom == 0:
            raise ZeroDivisionError("The denominator must not be zero!")

        self.numer = numer
        self.denom = denom

        if self.denom != 1 and simplify:
            self.simplify()

    @staticmethod
    def copy(rat: Rational, simplify: bool = True) -> Rational:
        return Rational(rat.numer, rat.denom, simplify)

    @staticmethod
    def parse(s: Type[Decimal] | Type[float] | Type[str] | Type[Tuple[int, Sequence[int], int]]) -> Rational:
        try:
            numer, denom = Decimal(s).as_integer_ratio()
            return Rational(numer, denom, simplify=True)
        except InvalidOperation:
            raise ValueError("Couldn't parse as a Rational!")

    def simplify(self) -> None:
        """Simplifies this Rational."""

        x = gcd(int(self.numer), int(self.denom))
        # print("simplifying", self.numer, self.denom, x)
        self.numer = int(self.numer / x)
        self.denom = int(self.denom / x)

    def scale(self, x: int) -> None:
        """Scales this Rational's numerator and denominator by x."""

        if x == 0:
            raise ZeroDivisionError("Cannot scale a Rational number by zero!")

        self.numer *= x
        self.denom *= x

    @staticmethod
    def reciprocal(x: Rational) -> Rational:
        """Returns the reciprocal of a Rational."""

        if x.denom == 0:
            raise ZeroDivisionError("Cannot take the reciprocal of zero!")

        return Rational(x.denom, x.numer, False)

    @staticmethod
    def match_denominators(a: Rational, b: Rational) -> int:
        if a.denom != b.denom:
            a_denom = a.denom
            a.scale(b.denom)
            b.scale(a_denom)
        return a.denom

    @staticmethod
    def multiply(a: Rational, b: Rational, simplify: bool = True) -> Rational:
        return Rational(int(a.numer * b.numer), int(a.denom * b.denom), simplify)

    @staticmethod
    def divide(a: Rational, b: Rational, simplify: bool = True) -> Rational:
        return Rational.multiply(a, Rational.reciprocal(b), simplify)

    @staticmethod
    def add(a: Rational, b: Rational, simplify: bool = True) -> Rational:
        denom = Rational.match_denominators(a, b)

        result = Rational(a.numer + b.numer, denom, simplify)

        a.simplify()
        b.simplify()

        return result

    @staticmethod
    def subtract(a: Rational, b: Rational, simplify: bool = True) -> Rational:
        denom = Rational.match_denominators(a, b)

        result = Rational(int(a.numer - b.numer), int(denom), simplify)

        a.simplify()
        b.simplify()

        return result

    def is_positive(self) -> bool:
        return self.numer > 0 and self.denom > 0

    def is_zero(self) -> bool:
        return self.numer == 0

    def is_negative(self) -> bool:
        return not self.is_positive() and not self.is_zero()

    def as_egyptian_fraction(self) -> List[Rational]:
        """
        Calculates the shortest Egyptian Fraction for this Rational. This algorithm is horrible, as it checks every possible integer.
        For example, if the shortest Egyptian Fraction includes 1/x, this algorithm will check every integer up to and including x.
        """
        x = Rational.copy(self)

        result = []

        i = 2
        while not x.is_zero():
            candidate = Rational(1, i)
            y = Rational.subtract(x, candidate)

            if not y.is_negative():
                result.append(candidate)
                x = y

            i += 1

        return result

    def as_float(self) -> float:
        return float(self.numer / self.denom)

    def to_string(self, float_only=False) -> str:
        if float_only or (self.denom != 1 and ceil(log10(self.denom)) == floor(log10(self.denom))):
            return str(self.numer / self.denom)
        else:
            return str(self)

    def __str__(self) -> str:
        if self.denom == 1:
            return str(self.numer)
        return str(self.numer) + "/" + str(self.denom)

    def __repr__(self) -> str:
        return "Rational(" + self.__str__() + ")"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Rational):
            return False

        a = Rational.copy(self, simplify=True)
        b = Rational.copy(o, simplify=True)

        return a.numer == b.numer and a.denom == b.denom

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def calculate(self) -> Rational:
        return self

    def is_valid(self) -> bool:
        return True

    def is_expression(self) -> bool:
        return False
