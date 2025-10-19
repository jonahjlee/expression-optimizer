from expressions.operator import Operator, UnaryOperator, BinaryOperator


# =============================================================================
# EXPRESSIONS
# =============================================================================

class Expression:
    """A string expression that evaluates to an integer."""

    def __init__(self, string: str, score: int) -> None:
        if type(self) is Expression:
            raise TypeError("Expression cannot be instantiated directly.")
        self._string: str = string
        self._score: int = score

    def evaluate(self) -> int:
        """Evaluate the expression and return an integer."""
        return int(eval(self._string))

    def __str__(self):
        return self._string

    @property
    def string(self) -> str:
        return self._string

    @property
    def score(self) -> int:
        return self._score

class TrueExpression(Expression):
    """Base case expression. Evaluates to 1."""

    def __init__(self) -> None:
        super().__init__('True', 1)

class CompositeExpression(Expression):
    """Composite expression, composed of at least one operator and one expression."""

    def __init__(self,
                 operator: Operator,
                 expr_1: Expression,
                 expr_2: Expression = None) -> None:
        """Instantiate a CompositeExpression either from a unary or binary operator."""
        if expr_2 is None:  # Unary operator case
            if not isinstance(operator, UnaryOperator):
                raise TypeError("Operator is binary, but only one expression was given!")
            string = f"{operator.value}({expr_1._string})"
            score = expr_1.score + 1
        else:  # Binary operator case
            if not isinstance(operator, BinaryOperator):
                raise TypeError("Operator is unary, but two expressions were given!")
            string = f"({expr_1._string}){operator.value}({expr_2._string})"
            score = expr_1.score + expr_2.score + 1

        super().__init__(string, score)