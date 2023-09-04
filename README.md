# NYTimes Digits Puzzle Solver

This is a command-line interface for solving NYTimes 'Digits' Puzzles:

[https://www.nytimes.com/games/digits](https://www.nytimes.com/games/digits)

## Generic Puzzle Solver

File puzzlesolver.py contains a generic breadth-first puzzle solver search:

```
from puzzlesolver import PuzzleSolver

ps = PuzzleSolver()
```

The generic puzzle solver has one method, `solve` which takes one
argument, a "puzzle" object and returns a list of moves that solve
the puzzle. The puzzle object must have these interface methods:

```
for m in puzzle.legalmoves():  -- generate legal 'moves'

puzzle.copy_and_move(m)        -- copy the puzzle, and perform move 'm'

s = puzzle.canonicalstate()    -- return a hashable canonical state
```

For details of that interface refer to the docstring of the PuzzleSolver class.

The interface also requires one attribute/property:

```
puzzle.endstate              -- True if the puzzle is 'solved'
```

This puzzle solver is generic and can be used to solve any type of puzzle
that provides (or is wrapped with something to provide) these interfaces.
See, for example, the Tower of Hanoi implementation contained in the unit
tests within the puzzlesolver.py file.


## NYTDigits puzzle object

File nytdigits.py contains an object implementing the solver's required
puzzle interface for the NYT Digits game. To create a puzzle object:

```
from nytdigits import DigitsPuzzle

z = DigitsPuzzle(123, 5, 9, 10, 14, 19, 21)
```

This example creates a puzzle where the target value is 123 and the six
starting values are 5, 9, 10, 14, 19, and 21. Any number of starting values
can be supplied and they do not need to be in sorted order.

The returned object is suitable for passing into a PuzzleSolver.

In "chain" mode the result of each operation must be the first operand of
the next operation. To create a chain mode puzzle:

```
z = DigitsPuzzle(123, 5, 9, 10, 14, 19, 21,
                 forced_operand=DigitsPuzzle.CHAINMODE)
```

Alternatively, a puzzle created without `DigitsPuzzle.CHAINMODE` can be put
into chain mode this way:
```
z = DigitsPuzzle(123, 5, 9, 10, 14, 19, 21)
z.chainmode(True)
```


## Solving a puzzle
Putting everything together:
```
from puzzlesolver import PuzzleSolver
from nytdigits import DigitsPuzzle

z = DigitsPuzzle(123, 5, 9, 10, 14, 19, 21)
ps = PuzzleSolver()
m = ps.solve(z)
print(m)
```

will output:
```
[(<built-in function add>, (19, 14)),
 (<built-in function mul>, (10, 9)),
 (<built-in function add>, (90, 33))]
```

## Command Line Mode
File nydigits.py can be run as a command:

```
% python3 nytdigits.py 123 5 9 10 14 19 21
```

This example will print:
```
+    (19, 14)
*    (10, 9)
+    (90, 33)
PuzzleStatistics(maxq=1997, iterations=210)
```

showing the three moves that solve the puzzle and some statistics from
the search.

Command argument -c will force chain mode:
```
% python3 nytdigits.py -c 123 5 9 10 14 19 21
-    (21, 14)
*    (7, 19)
-    (133, 10)
PuzzleStatistics(maxq=1041, iterations=193)
```

To see all the solutions instead of just one:
```
% python3 nytdigits.py -A 123 5 9 10 14 19 21
```
[ there are 83 solutions in this example; they are not shown here ]

## Tests
Unit tests for the DigitsPuzzle object:
```
% python3 nytdigitstests.py
```

Unit tests for the PuzzleSolver object:
```
% python3 puzzlesolver.py
```

