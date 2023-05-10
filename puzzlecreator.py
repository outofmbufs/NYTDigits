import random
import itertools

from nytdigits import DigitsPuzzle
from puzzlesolver import PuzzleSolver

DEFAULT_SOURCES = range(1, 26)        # based on observations of NYT
DEFAULT_TARGETS = range(50, 450)      # based on observations of NYT


def puzzle_maker(*, minsteps=3, chainmode=True,
                 targets=None, sources=None, puzzle_size=6,
                 required_ops=None, attempt_limit=None):
    """Make a NYTimes Digits puzzle meeting various criteria.

    minsteps: Default = 3
        Minimum number of steps required in solution.

    chainmode: Default = True   (** NOTE: YES, TRUE**)
        Require a solution be *possible* in chain mode. Note that a
        non-chain solution likely also exists.

    targets: Default = None
        A sequence of targets to try, randomly, in search.
        Can also be a single value (not a sequence).
        If None, a default range of potential target values.

    sources: Default = None
        A sequence of potential source values to use in making a puzzle.
        NOTE: this can, and usually should, be larger than the number of
        source values the puzzle should contain. This is the population of
        potential choices for sources.
        If None, a default range of potential source values.

    puzzle_size: Default = 6
        How many sources should be in the puzzle.

    required_ops: Default None
        A sequence of op values (generally: operator.add, etc) that
        must be in the solution PuzzleSolver() finds. Note that this
        does not guarantee that all possible solutions require the op,
        just that at least one solution uses the op.

    attempt_limit: Default None
        The number of times to loop trying to find a puzzle that meets
        all the criteria. Loops forever if default.
    """

    try:
        nt = len(targets)
    except TypeError:
        if targets is None:
            nt = 0
        else:
            targets = [targets]
            nt = 1
    if nt == 0:
        targets = DEFAULT_TARGETS

    if sources is None or len(sources) == 0:
        sources = DEFAULT_SOURCES
    if required_ops is None:
        reqds = set()
    else:
        reqds = set(required_ops)

    for attempt in itertools.count():
        if attempt_limit is not None and attempt >= attempt_limit:
            return None

        z = DigitsPuzzle(random.choice(targets),
                         *random.sample(sources, puzzle_size))
        z.chainmode(chainmode)
        soln = PuzzleSolver().solve(z)
        if soln is not None and len(soln) >= minsteps:
            soln_ops = {op for op, rands in soln}
            if (soln_ops & reqds) == reqds:
                return z


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--steps', type=int, default=3)
    parser.add_argument('-r', '--require', action='append',
                        choices=['+', '-', '/', '*'])
    parser.add_argument('targets', type=int, nargs='*', default=None)
    args = parser.parse_args()

    if args.require:
        syms2op = {sym: op for op, sym in DigitsPuzzle.OPSYMS.items()}
        reqd = [syms2op[s] for s in args.require]
    else:
        reqd = None

    z = puzzle_maker(minsteps=args.steps,
                     targets=args.targets, required_ops=reqd)
    print(z.target, z.sources)
    soln = PuzzleSolver().solve(z)
    for op, rands in soln:
        opstr = DigitsPuzzle.OPSYMS.get(op, str(op))
        print(f"{opstr} {rands}")
