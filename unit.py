import unittest
from hamcrest.core.assert_that import assert_that
from hamcrest.core.core.allof import all_of
from hamcrest.core.core.isequal import equal_to
from hamcrest.library.number.ordering_comparison import greater_than_or_equal_to, less_than_or_equal_to
from pyDoubles.framework import *

__author__ = 'rubenbp'

class RobotTest(unittest.TestCase):
    def setUp(self):
        self.server_proxy = spy(ServerProxy())
        when(self.server_proxy.move).then_return({"OK", 10})

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
        self.server_proxy_mock = mock(ServerProxy())
        expect_call(self.server_proxy_mock.init)

        next_cell_calculator = stub(NextCellCalculator(0, 100))
        when(next_cell_calculator.next).then_return(5)

        self.robot = Robot(
            "robocop", self.server_proxy_mock, next_cell_calculator)

    def tearDown(self):
        self.server_proxy_mock.assert_that_is_satisfied()

    def test_move_to_cell_severals_times(self):
        expect_call(self.server_proxy_mock.move
            ).returning({"OK",10}).times(2)

        self.robot.start(total_moves = 2)

        assert_that(self.robot.score, equal_to(20))

    def test_game_over_in_a_move(self):
        expect_call(self.server_proxy_mock.move
            ).returning({"GameOver",0})

        self.robot.start(total_moves = 2)

        assert_that(self.robot.status, equal_to("GameOver"))
        assert_that(self.robot.score, equal_to(0))

    def test_win_in_a_move(self):
        expect_call(self.server_proxy_mock.move
            ).returning({"YouWin",10})

        self.robot.start(total_moves = 2)

        assert_that(self.robot.status, equal_to("YouWin"))
        assert_that(self.robot.score, equal_to(10))

    def test_robot_use_next_cell_calculator(self):
        next_cell_calculator = mock(NextCellCalculator(0, 100))
        expect_call(next_cell_calculator.next
            ).returning(10)
        self.robot.next_cell_calculator = next_cell_calculator
        expect_call(self.server_proxy_mock.move
            ).returning({"OK",10})

        self.robot.start(total_moves = 1)

        next_cell_calculator.assert_that_is_satisfied()

class NextCellCalculatorTests(unittest.TestCase):

    def test_return_next_cell_in_range(self):
        next_cell_calculator = NextCellCalculator(0, 100)
        assert_that(
            next_cell_calculator.next(),
            all_of(greater_than_or_equal_to(0),
                    less_than_or_equal_to(100)))

class NextCellCalculator():
    def __init__(self, min_cell, max_cell):
        self.min_cell = min_cell
        self.max_cell = max_cell
        
    def next(self):
        return 0

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
            move_score, status = self.server_proxy.move(
                                    self.name, next_cell)
            self.status = status

            if status == "GameOver":
                break

            if status == "YouWin":
                self.score += move_score
                break

            self.score += move_score