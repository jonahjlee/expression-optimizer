from enum import Enum


# =============================================================================
# OPERATORS
# =============================================================================

class Operator(Enum):
    pass # subclasses distinguish unary/binary

class UnaryOperator(Operator):
    MINUS = '-'
    BITWISE_NOT = '~'

class BinaryOperator(Operator):
    pass # subclasses distinguish commutative/noncommutative

class BinaryNonCommutativeOperator(BinaryOperator):
    BIT_SHIFT_LEFT = '<<'
    BIT_SHIFT_RIGHT = '>>'
    SUBTRACT = '-'
    EXPONENTIATE = '**'
    INT_DIVIDE = '//'
    MODULO = '%'

class BinaryCommutativeOperator(BinaryOperator):
    ADD = '+'
    MULTIPLY = '*'
    BITWISE_AND = '&'
    BITWISE_OR = '|'
    BITWISE_XOR = '^'