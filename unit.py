import unittest
from hamcrest.core.assert_that import assert_that
from hamcrest.core.core.allof import all_of
from hamcrest.core.core.isequal import equal_to
from hamcrest.core.core.isnot import is_not
from hamcrest.library.number.ordering_comparison import greater_than_or_equal_to, less_than_or_equal_to
from pyDoubles.framework import *

__author__ = 'rubenbp'

class RobotTest(unittest.TestCase):
    def setUp(self):
        self.server_proxy = spy(ServerProxy())
        when(self.server_proxy.move).then_return(("OK", 10))

        next_cell_calculator = stub(NextCellCalculator(0, 100))
        when(next_cell_calculator.next).then_return(5)

        self.robot = Robot(
            "robocop",self.server_proxy, next_cell_calculator)

    def test_initial_score_is_zero(self):
        assert_that(self.robot.score, equal_to(0))

    def test_initialize_the_game(self):
        self.robot.start(1)

        assert_that_method(self.server_proxy.init
            ).was_called().with_args("robocop")

    def test_move_to_cell_one_time(self):
        self.robot.start(1)

        assert_that_method(self.server_proxy.move
            ).was_called().with_args("robocop", ANY_ARG)
        assert_that(self.robot.score, equal_to(10))

class RobotMovesTests(unittest.TestCase):
    def setUp(self):
        self.server_proxy_stub = stub(ServerProxy)

        next_cell_calculator = stub(NextCellCalculator(0, 100))
        when(next_cell_calculator.next).then_return(5)

        self.robot = Robot(
            "robocop", self.server_proxy_stub, next_cell_calculator)

    def test_move_to_cell_severals_times(self):
        server_proxy_spy = spy(ServerProxy())
        when(server_proxy_spy.move).then_return(("OK", 10))
        self.robot.server_proxy = server_proxy_spy

        self.robot.start(total_moves = 2)

        assert_that_method(server_proxy_spy.move).was_called().times(2)
        assert_that(self.robot.score, equal_to(20))

    def test_game_over_in_a_move(self):
        when(self.server_proxy_stub.move).then_return(("GameOver", 0))

        self.robot.start(total_moves = 2)

        assert_that(self.robot.status, equal_to("GameOver"))
        assert_that(self.robot.score, equal_to(0))

    def test_win_in_a_move(self):
        when(self.server_proxy_stub.move).then_return(("YouWin",10))

        self.robot.start(total_moves = 2)

        assert_that(self.robot.status, equal_to("YouWin"))
        assert_that(self.robot.score, equal_to(10))

    def test_robot_use_next_cell_calculator(self):
        next_cell_calculator = mock(NextCellCalculator(0, 100))
        expect_call(next_cell_calculator.next).returning(10)
        self.robot.next_cell_calculator = next_cell_calculator
        when(self.server_proxy_stub.move).then_return(("OK",10))

        self.robot.start(total_moves = 1)

        next_cell_calculator.assert_that_is_satisfied()

class NextCellCalculatorTests(unittest.TestCase):

    def test_return_next_cell_in_range(self):
        next_cell_calculator = NextCellCalculator(0, 100)
        for x in range(999):
            assert_that(
                next_cell_calculator.next(),
                all_of(greater_than_or_equal_to(0),
                        less_than_or_equal_to(100)))

    def test_dont_return_twice_the_same_number(self):
        next_cell_calculator = NextCellCalculator(0, 100)

        for x in range(100):
            assert_that(
                next_cell_calculator.next(),
                is_not(equal_to(next_cell_calculator.next())))

class NextCellCalculator():
    def __init__(self, min_cell, max_cell):
        self.min_cell = min_cell
        self.max_cell = max_cell
        self.last_cell = self.min_cell

    def next(self):
        self.last_cell += 1
        if self.last_cell > self.max_cell:
            self.last_cell = self.min_cell
        return self.last_cell

class ServerProxy():
    def init(self, robot_name):
        pass

    def move(self, robot_name, cell):
        pass

class Robot():
    def __init__(self, name, server_proxy, next_cell_calculator):
        self.name = name
        self.server_proxy = server_proxy
        self.next_cell_calculator = next_cell_calculator
        self.score = 0
        self.status = ""
        
    def start(self, total_moves):
        self.server_proxy.init(self.name)
        for x in range(total_moves):
            next_cell = self.next_cell_calculator.next()
            status, move_score = self.server_proxy.move(
                                    self.name, next_cell)
            self.status = status

            if status == "GameOver":
                break

            if status == "YouWin":
                self.score += move_score
                break

            self.score += move_score