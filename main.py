import copy
import warnings
from pathlib import Path
from expressions.expression import Expression, TrueExpression, CompositeExpression
from expressions.operator import UnaryOperator, BinaryCommutativeOperator, BinaryNonCommutativeOperator


# =============================================================================
# OPTIMIZER
# =============================================================================

class ExpressionOptimizer:
    def __init__(self, out_file: Path=None, max_bit_shift=None) -> None:

        # Open output file
        if out_file is not None:
            self._out_file = open(out_file, 'w')
            self._out_file.write(f"Score, Target, Expression\n")
            self._out_file.write(f"1, 1, True\n")
        else:
            self._out_file = None

        # Maximum allowed bit shift
        # If this is not None, ExpressionOptimizer cannot guarantee min-s for all targets found
        self._max_bit_shift = max_bit_shift

        # ExpressionOptimizer contains an expression for all targets which can
        # be reached with a score less than or equal to `_max_score`
        self._max_score: int = 1

        # Map of score to list of expressions with that score
        # Each expression in the list must have a different target,
        # and a target will only be found once in the entire dictionary
        self._min_s_exprs: dict[int, list[Expression]] = {
            1: [TrueExpression()]
        }

        # Map of targets to min-s expression with that target
        self._targs: dict[int, Expression] = {
            1: TrueExpression()
        }

    def _get_score_exprs(self, score: int) -> list[Expression]:
        return self._min_s_exprs[score]

    def _add_expr_if_better(self, expr: Expression, console_print: bool=False) -> bool:

        # Check if expression is valid
        try:
            target = expr.evaluate()
        except ZeroDivisionError:
            return False

        if target in self._targs.keys():
            # An equal or better expression was already found
            return False

        # New target reached!
        self._targs[target] = expr
        self._min_s_exprs[expr.score] = self._min_s_exprs.get(expr.score, []) + [expr]
        if self._out_file is not None:
            try:
                value_str = str(target)
            except ValueError:
                value_str = "Too large to print!"
            line_out = f"{expr.score},{value_str},{expr.string}"
            self._out_file.write(line_out + "\n")
            if console_print:
                print(line_out)
        return True

    def get_min_s_exprs(self):
        return copy.deepcopy(self._min_s_exprs)

    def get_targ_exprs(self):
        return copy.deepcopy(self._targs)

    def print_score_exprs(self, score: int):
        expr_list = self._get_score_exprs(score)
        score_formatter = "{:0>" + str(len(str(self._max_score))) + "}"
        for expr in expr_list:
            try:
                value_str = str(expr.evaluate())
            except ValueError:
                value_str = "Too large to print!"

            # print(f"Score: {score_formatter.format(score)}, "
            #       f"Target: {value_str}, Expression: {expr.string}")
            print(f"Score {score_formatter.format(score)}: "
                  f"{expr.string} = {value_str}")


    def print_min_s_exprs(self):
        for score in range(1, self._max_score + 1):
            self.print_score_exprs(score)

    def print_newest_exprs(self):
        self.print_score_exprs(self._max_score)

    @property
    def max_score(self):
        return self._max_score

    def increase_max_score(self, print_new: bool=False) -> int:
        """
        Increase the maximum allowed score of the expressions.
        Returns the number of new targets reached.
        """
        # Search for composite expressions that will have a score of max_score + 1
        new_exprs = []

        # Unary operators
        for expr in self._get_score_exprs(self._max_score):
            for op in UnaryOperator:
                new_exprs.append(CompositeExpression(op, expr))

        # Binary non-commutative operators
        for score_1 in range(1, self._max_score):
            score_2 = self._max_score - score_1
            # score_1 + score_2 + 1 = max_score + 1

            # Iterate over all pairs of expressions which yield expressions
            # with a score of max_score + 1 when combined via a binary operator
            for expr_1 in self._get_score_exprs(score_1):
                for expr_2 in self._get_score_exprs(score_2):

                    if expr_1.evaluate() <= expr_2.evaluate():
                        # Commutative operators (no need calculate both ways)
                        for op in BinaryCommutativeOperator:
                            new_exprs.append(CompositeExpression(op, expr_1, expr_2))

                    # Non-commutative operators
                    for op in BinaryNonCommutativeOperator:

                        if (op in [BinaryNonCommutativeOperator.BIT_SHIFT_LEFT,
                            BinaryNonCommutativeOperator.BIT_SHIFT_RIGHT]):

                            shift_count = expr_2.evaluate()

                            # Cannot bit-shift by negative value,
                            # and bit-shift by zero is pointless
                            if shift_count <= 0:
                                continue

                            # Cap bit shift counts to avoid insanely large numbers
                            # NOTE: technically this invalidates min-s guarantee!
                            elif (self._max_bit_shift is not None
                                and shift_count > self._max_bit_shift):
                                continue

                        new_exprs.append(CompositeExpression(op, expr_1, expr_2))

        for new_expr in new_exprs:
            self._add_expr_if_better(new_expr, console_print=print_new)

        self._max_score += 1

        return len(self._get_score_exprs(self._max_score))


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Python doesn't like it when you do ~True, because it thinks you're doing it by mistake! I am not.
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    output_csv = Path.cwd() / "outputs" / "out.csv"

    optimizer = ExpressionOptimizer(out_file=output_csv)

    while optimizer.max_score < 5:
        try:
            # optimizer.get_min_s_exprs()
            # optimizer.print_newest_exprs()
            optimizer.increase_max_score(print_new=True)
        except OverflowError:
            break

    for targ in sorted(list(optimizer.get_targ_exprs())):
        try:
            print(targ)
        except ValueError:
            print("Too large to print!")