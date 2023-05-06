import unittest
import operator
from nytdigits import DigitsPuzzle


class TestMethods(unittest.TestCase):
    # these are simpler tests than the typical NYT puzzle
    def test1(self):
        d = DigitsPuzzle(10, 3, 7)
        # there should be three legal moves from this
        # (not four; division doesn't work for 7/3).
        moves = list(d.legalmoves())
        self.assertEqual(len(moves), 3)

    def test2(self):
        d = DigitsPuzzle(10, 3, 7)
        moves = list(d.legalmoves())
        # there should be a subtract move in the legal moves
        # and it has to be (7, 3) not (3, 7)
        self.assertTrue((operator.sub, (7, 3)) in moves)

    def test3(self):
        d = DigitsPuzzle(10, 3, 7)
        moves = list(d.legalmoves())
        # check for the legal add and multiply moves without
        # enforcing that the operands are sorted (because
        # that's an implementation detail not a behavior)

        for op, rands in d.legalmoves():
            if op == operator.add:
                self.assertTrue(rands in ((3, 7), (7, 3)))
                break
        else:
            self.assertTrue(False, "didn't find operator.add")

        for op, rands in d.legalmoves():
            if op == operator.mul:
                self.assertTrue(rands in ((3, 7), (7, 3)))
                break
        else:
            self.assertTrue(False, "didn't find operator.mul")

    def test4(self):
        d = DigitsPuzzle(10, 3, 14, 2)
        moves = list(d.legalmoves())
        # by inspection there should be 10 moves; there are three
        # combinations each for add/mul/sub plus div is legal 14/2
        self.assertEqual(len(moves), 10)

        # check to see if the div is in there since no prev test was div
        for op, rands in moves:
            if op == operator.floordiv:
                self.assertEqual(rands, (14, 2))
                break
        else:
            self.assertTrue(False, "didn't find operator.floordiv")

    def test5(self):
        # chain mode test - with the __init__ method and
        # with the chainmode() method
        d1 = DigitsPuzzle(10, 3, 14, 2, 13,
                          forced_operand=DigitsPuzzle.CHAINMODE)

        d2 = DigitsPuzzle(10, 3, 14, 2, 13)
        d2.chainmode(True)

        for d in (d1, d2):
            moves = list(d.legalmoves())
            # there are 19 moves, by inspection (6 add/mul/sub, 1 div)
            self.assertEqual(len(moves), 19)

            # do the 1 division move
            d.move((operator.floordiv, (14, 2)))

            # now every legal move should have the (new) 7 as
            # its first operand, making the legal moves:
            #   add (7, 3)
            #   add (7, 13)
            #   mul (7, 3)
            #   mul (7, 13)
            #   sub (7, 3)
            moves = list(d.legalmoves())
            self.assertEqual(len(moves), 5)
            for m in (
                    (operator.add, (7, 3)),
                    (operator.add, (7, 13)),
                    (operator.mul, (7, 3)),
                    (operator.mul, (7, 13)),
                    (operator.sub, (7, 3))):
                with self.subTest(m=m):
                    self.assertTrue(m in moves)

    def test6(self):
        # another chain mode test verifying the thing where
        # duplicated forced operand values work

        d = DigitsPuzzle(10, 3, 14, 2, 7,
                         forced_operand=DigitsPuzzle.CHAINMODE)

        moves = list(d.legalmoves())
        # there are 20 moves, by inspection (6 add/mul/sub, 2 div)
        self.assertEqual(len(moves), 20)

        # do the division move that makes a 7, which will be
        # a duplicate (i.e., there will be two 7's in sources)
        d.move((operator.floordiv, (14, 2)))

        # now every legal move should have the (new) 7 as
        # its first operand, making the legal moves:
        #   add (7, 3)
        #   add (7, 7)
        #   mul (7, 3)
        #   mul (7, 7)
        #   sub (7, 3)
        #   div (7, 7)
        moves = list(d.legalmoves())
        self.assertEqual(len(moves), 6)
        for m in (
                (operator.add, (7, 3)),
                (operator.add, (7, 7)),
                (operator.mul, (7, 3)),
                (operator.mul, (7, 7)),
                (operator.sub, (7, 3)),
                (operator.floordiv, (7, 7))):
            with self.subTest(m=m):
                self.assertTrue(m in moves)

    def test7(self):
        # endstate tests
        d = DigitsPuzzle(10, 3, 14, 2, 13)
        self.assertFalse(d.endstate)
        d.move((operator.floordiv, (14, 2)))
        self.assertFalse(d.endstate)
        d.move((operator.add, (7, 3)))
        self.assertTrue(d.endstate)

    def test8(self):
        # illegal move tests
        d = DigitsPuzzle(10, 3, 14, 2, 13, 13)

        illegals = ((operator.add, (16, 17)),
                    (operator.sub, (13, 13)),
                    (operator.sub, (13, 14)))

        for m in illegals:
            with self.subTest(m=m):
                with self.assertRaises(ValueError):
                    d.move(m)


if __name__ == "__main__":
    unittest.main()
