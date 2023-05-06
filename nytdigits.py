# MIT License
#
# Copyright (c) 2023 Neil Webber
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# For use with puzzlesolver.py, this models the NYT Digits puzzle

import operator
import itertools


class DigitsPuzzle:

    CHAINMODE = object()                       # sentinel for forced_operand

    def __init__(self, target, *sources, forced_operand=None):
        """Initialize a NYT Digits Puzzle.

        target: the puzzle's ending/target value
        *sources: N integers, the starting numbers for the puzzle
        forced_operand: generalized version of the NYT "chain mode" rule.
           It can take on three different meanings:
             None (default): All source operands are available.

             DigitsPuzzle.CHAINMODE: This is the NYT "chain" mode indicator.
                 All source operands are available for the first move; after
                 that the forced_operand will be the output of the prior move.

             any value f, where "f in sources" is true.
                 f will be forced to be the first operand. This is a
                 generalization of NYT chain mode and also used by clone()
        """

        self.target = target
        self.forced_operand = forced_operand

        # keeping sources in descending order simplifies move generator
        self.sources = sorted(sources, reverse=True)

        # sanity check - no non-positive values allowed
        # NOTE: they are sorted, so checking the last (smallest) suffices
        if self.sources[-1] <= 0:
            raise ValueError(
                f"illegal (non-positive) source value ({self.sources[-1]})")

    def chainmode(self, v, /):
        """Change puzzle chain mode to True/False."""
        if v:
            self.forced_operand = self.CHAINMODE
        else:
            self.forced_operand = None

    @property
    def endstate(self):
        return self.target in self.sources

    def clone(self):
        return self.__class__(self.target, *self.sources,
                              forced_operand=self.forced_operand)

    def _sourcecombos(self):
        """Generate potential pairs, taking chain mode into account."""

        # NOTE: See discussion in legalmoves regarding ordering within tuples.
        if self.forced_operand in self.sources:
            # Because forced_operand is being, ummm, forced, it's important
            # not to double-use it from sources. But there's a catch: there
            # might be more than one entry in sources equal to this value.
            # So: can't just test "b != forced_operand" ... have to take
            # ONE forced_operand value out of the sources and then pair up.

            # this chains together a takewhile that takes from g up until
            # encountering a forced_operand (which is omitted if so), and
            # then the remainder of g (if any) after that.  Yeehah!
            g = iter(self.sources)
            return (
                (self.forced_operand, b) for b in
                itertools.chain(
                    itertools.takewhile(lambda x: x != self.forced_operand, g),
                    g))
        else:
            return itertools.combinations(self.sources, 2)

    def legalmoves(self):
        """Generate all legal moves. A move is a tuple (op, (a, b))."""

        # _sourcecombos returns (a, b) pairs where either:
        #     a >= b
        # OR  a is a "forced operand" and must be the first operand.
        #
        # Thus, operand "b" is as small as it *CAN* be, which simplifies
        # some of the operation filter tests.

        # ADD: all operations are legal - no filtering at all.
        yield from ((operator.add, ab) for ab in self._sourcecombos())

        # SUB: Do not allow negative (duh) or zero.
        yield from ((operator.sub, (a, b))
                    for a, b in self._sourcecombos() if a > b)

        # MUL: Filter out 1 as a minor optimization (search reduction).
        #      NOTE: Allows 'a' to be 1 if it was the forced operand.
        yield from ((operator.mul, (a, b))
                    for a, b in self._sourcecombos() if b != 1)

        # DIV: Has to be evenly divisible and optimize out divide-by-1
        yield from ((operator.floordiv, (a, b))
                    for a, b in self._sourcecombos()
                    if (a % b) == 0 and b != 1)

    def move(self, m):
        """Perform a move. Moves are tuples (op, (operands-iterable))."""
        op, operands = m
        for x in operands:
            self.sources.remove(x)
        rslt = op(*operands)

        # zero and negative results are not allowed into the puzzle
        if rslt <= 0:
            raise ValueError(f"illegal move: {m}")

        # in chain mode, this must be the next first operand
        if self.forced_operand:
            self.forced_operand = rslt
        self.sources = sorted(self.sources + [rslt], reverse=True)
        return self

    def copy_and_move(self, m):
        return self.clone().move(m)

    def canonicalstate(self):
        """Return hashable object corresponding to the puzzle state."""
        return tuple(self.sources + [self.forced_operand])


if __name__ == "__main__":
    import argparse
    from puzzlesolver import PuzzleSolver

    def cmdmain():
        parser = argparse.ArgumentParser()

        parser.add_argument('-c', '--chainmode',
                            action='store_const',
                            const=DigitsPuzzle.CHAINMODE)
        parser.add_argument('target', type=int)
        parser.add_argument('values', type=int, nargs='+')
        args = parser.parse_args()

        d = DigitsPuzzle(args.target, *args.values,
                         forced_operand=args.chainmode)
        ps = PuzzleSolver()
        moves = ps.solve(d)

        if not moves:
            print("No solution found")
        else:
            for m in moves:
                names = {operator.add: "+",
                         operator.sub: "-",
                         operator.mul: "*",
                         operator.floordiv: "/"}

                # ".get" with default just in case something gets
                # generalized from the known operators above
                op, rands = m
                print(f"{names.get(op, str(op))}    {rands}")
        print(ps.stats)

    cmdmain()
