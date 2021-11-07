from __future__ import annotations
from typing import List, Tuple, Type
from Rational import Calculatable, Rational, is_digit
from enum import Enum, auto


def find_matching_parens(s: str, i: int) -> int:
  level = 0
  for j, char in enumerate(s[i + 1:], i + 1):
    # print(j, char, level)
    if char == "(":
      level += 1
    elif char == ")":
      if level == 0:
        return j
      else:
        level -= 1
  raise ValueError("Couldn't find a matching parens!")


def op(a: Rational, b: Rational, operation: Operation) -> Rational:
    if operation == Operation.ADD:
        return Rational.add(a, b)
    elif operation == Operation.SUBTRACT:
        return Rational.subtract(a, b)
    elif operation == Operation.MULTIPLY:
        return Rational.multiply(a, b)
    elif operation == Operation.DIVIDE:
        return Rational.divide(a, b)
    elif operation == Operation.EXPONENT:
        # this isn't necessarily rational, but whatever
        return Rational(a.as_float() ** b.as_float())
    raise ValueError("Invalid operation!")


class Operation(Enum):
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    EXPONENT = auto()

    def __str__(self: Operation) -> str:
      if self == Operation.ADD:
        return "+"
      elif self == Operation.SUBTRACT:
        return "-"
      elif self == Operation.MULTIPLY:
        return "*"
      elif self == Operation.DIVIDE:
        return "/"
      elif self == Operation.EXPONENT:
        return "^"

    def __repr__(self) -> str:
      return self.__str__()

    @staticmethod
    def parse(x: str) -> Operation:
      if x == "+":
        return Operation.ADD
      elif x == "-":
        return Operation.SUBTRACT
      elif x == "*":
        return Operation.MULTIPLY
      elif x == "/":
        return Operation.DIVIDE
      elif x == "^":
        return Operation.EXPONENT


class Token:

  # switch this to from_operation, from_value, and from_expression
  def __init__(self, operation: Operation = None, value: Calculatable = None, is_expression: bool = False):
    if operation:
      self.operation = operation
      self.value = None
    elif value:
      self.value = value
      self.operation = None

  @staticmethod
  def build_from(x: Operation | float | int | Rational | Expression) -> bool:
    if isinstance(x, Operation):
      return Token(operation=x)
    elif isinstance(x, Rational):
      return Token(value=x, is_expression=False)
    elif isinstance(x, Expression):
      return Token(value=x, is_expression=True)
    elif isinstance(x, float) or isinstance(x, int):
      return Token(value=Rational(x), is_expression=False)

  def is_operation(self) -> bool:
    return self.operation is not None

  def is_value(self) -> bool:
    return self.value is not None

  def unwrap(self) -> Operation | Calculatable:
    if self.is_operation():
      return self.operation
    elif self.is_value():
      return self.value

  def to_string(self, str=str) -> bool:
    if self.is_operation():
      return str(self.operation)
    elif self.is_value():
      return str(self.value)

  def __str__(self) -> bool:
    return self.to_string(str)

  def __repr__(self) -> bool:
    return self.to_string(repr)


class Expression(Calculatable):

  def __init__(self, *tokens: Tuple[Token]):
    self.tokens: List[Token] = list(tokens)

  @staticmethod
  def build_from(*tokens: Tuple[Operation | float | int | Rational | Expression]) -> Expression:
    ex = Expression()
    for token in tokens:
      ex.add_token(Token.build_from(token))
    return ex

  @staticmethod
  def parse(s: str, indent: int = 0) -> Expression:
    s = s.replace(" ", "")
    # print("%sParsing '%s'" % ("\t" * indent, s))
    ex = Expression()

    building_digit = False
    working_digit = ""
    i = 0
    while i < len(s):
      char = s[i]

      # print("\t%sChar at %i: '%s'" % ("\t" * indent, i, char))

      if is_digit(char) or char == ".":
        working_digit += char
        building_digit = True
      else:
        if building_digit:
          x = Rational.parse(working_digit)
          ex.add_token(Token(value=x))
          building_digit = False
          working_digit = ""

        # now worry about what else it is
        if char in ["+", "-", "*", "/", "^"]:
          # it's an operation
          ex.add_token(Token(operation=Operation.parse(char)))
        elif char == "(":

          # allow writing things like '2(5-3)' and '(2-1)(3/4)'
          if len(ex.tokens) > 0 and ex.tokens[-1].is_value():
            ex.add_token(Token(operation=Operation.MULTIPLY))
          parens_location = find_matching_parens(s, i)
          subex = Expression.parse(s[i+1:parens_location], indent + 1)
          ex.add_token(Token(value=subex, is_expression=True))
          i = parens_location
        else:
          raise ValueError("Couldn't parse an invalid Expression!")
      i += 1
    if building_digit:
      x = Rational.parse(working_digit)
      ex.add_token(Token(value=x))
    # print("%sParsed '%s' -> %s" % ("\t" * indent, s, str(ex)))
    return ex

  def add_token(self, token: Token) -> None:
    self.tokens.append(token)

  def is_valid(self) -> bool:
    on_value = True
    for token in self.tokens:
      if token.is_value() is not on_value:
        return False
      on_value = not on_value
    return True

  def calculate(self) -> Rational:
    """Reduces this Expression's list of Tokens down to a single Rational Token."""

    if not self.is_valid():
      raise Exception("Can't calculate an invalid expression!")

    if len(self.tokens) == 1:
      return self.tokens[0].value.calculate()

    # PEMDAS
    self.pemdas()

    if not self.is_valid():
      raise Exception("Something really went wrong!")

    a = self.tokens[0].value.calculate()
    b = self.tokens[2].value.calculate()
    result = op(a, b, self.tokens[1].operation)

    return result

  def pemdas(self) -> None:
    self.consolidate([Operation.EXPONENT])
    self.consolidate([Operation.MULTIPLY, Operation.DIVIDE])
    self.consolidate([Operation.ADD, Operation.SUBTRACT])

  def consolidate(self, operations: List[Operation]) -> None:
    """Consolidates this Expression and all of its subexpressions into 3 token expressions."""
    i = 0
    while i < len(self.tokens) and len(self.tokens) >= 4:
      if self.tokens[i].is_operation() and self.tokens[i].operation in operations:
        ex = Expression(self.tokens[i - 1], self.tokens[i], self.tokens[i + 1])
        self.tokens = self.tokens[:i-1] + [Token(value=ex, is_expression=True)] + self.tokens[i+2:]

        # restart consolidation
        i = 0
      i += 1


  def is_expression(self) -> bool:
    return True

  def __str__(self) -> str:
    result = ""
    for token in self.tokens:
      if token.is_value() and token.value.is_expression():
        result += "(" + str(token) + ")"
      else:
        result += str(token)
    return result

  def get_formatted_string(self, indent: int = 0) -> str:
    result = ""
    for token in self.tokens:
      if token.is_value() and token.value.is_expression():
        result += "\n(" + token.value.get_formatted_string(indent + 1) + "\n" + ("  " * indent) + ")"
      else:
        result += "\n" + "  " * indent + repr(token)
    return result

