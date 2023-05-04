import unittest

import converters
from boards.str_board import StrBoard
from move_generation.legal_pos_generator import LegalPosGenerator


class MovesTestCase(unittest.TestCase):
    def setUp(self):
        self.str_board = StrBoard()
        self.generator = LegalPosGenerator()

    def test_queen(self):
        self.str_board.str_array[4, 3] = 'wq'
        long_num = converters.str_board_to_binary_number(self.str_board)
        positions = self.generator.generate_legal_positions(long_num)
        self.assertTrue(len(positions) == 27)

    def test_rook(self):
        self.str_board.str_array[4, 5] = 'wr'
        long_num = converters.str_board_to_binary_number(self.str_board)
        positions = self.generator.generate_legal_positions(long_num)
        self.assertTrue(len(positions) == 14)

    def test_bishop(self):
        self.str_board.str_array[4, 5] = 'wb'
        long_num = converters.str_board_to_binary_number(self.str_board)
        positions = self.generator.generate_legal_positions(long_num)
        self.assertTrue(len(positions) == 11)

    def test_king(self):
        self.str_board.str_array[4, 5] = 'wke'
        long_num = converters.str_board_to_binary_number(self.str_board)
        positions = self.generator.generate_legal_positions(long_num)
        self.assertTrue(len(positions) == 8)

    def test_pawn(self):
        self.str_board.str_array[4, 5] = 'wp'
        long_num = converters.str_board_to_binary_number(self.str_board)
        positions = self.generator.generate_legal_positions(long_num)
        self.assertTrue(len(positions) == 1)

    def test_knight(self):
        self.str_board.str_array[4, 5] = 'wk'
        long_num = converters.str_board_to_binary_number(self.str_board)
        positions = self.generator.generate_legal_positions(long_num)
        self.assertTrue(len(positions) == 8)


if __name__ == '__main__':
    unittest.main()
