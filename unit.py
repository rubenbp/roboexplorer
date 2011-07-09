import unittest
from hamcrest.core.assert_that import assert_that
from hamcrest.core.core.isequal import equal_to
from pyDoubles.framework import *

__author__ = 'rubenbp'

class RobotTest(unittest.TestCase):
    def setUp(self):
        self.server_proxy = spy(ServerProxy())
        when(self.server_proxy.move).then_return({"OK", 10})
        self.robot = Robot("robocop",self.server_proxy)

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

    def test_move_to_cell_severals_times(self):
        server_proxy_mock = mock(ServerProxy())
        expect_call(server_proxy_mock.init)
        expect_call(server_proxy_mock.move
            ).returning({"OK",10}).times(2)

        self.robot = Robot("robocop", server_proxy_mock)
        self.robot.start(total_moves = 2)

        server_proxy_mock.assert_that_is_satisfied()
        assert_that(self.robot.score, equal_to(20))

    def test_game_over_in_a_move(self):
        server_proxy_mock = mock(ServerProxy())
        expect_call(server_proxy_mock.init)
        expect_call(server_proxy_mock.move
            ).returning({"GameOver",0})

        self.robot = Robot("robocop", server_proxy_mock)
        self.robot.start(total_moves = 2)

        server_proxy_mock.assert_that_is_satisfied()
        assert_that(self.robot.status, equal_to("GameOver"))
        assert_that(self.robot.score, equal_to(0))

    def test_win_in_a_move(self):
        server_proxy_mock = mock(ServerProxy())
        expect_call(server_proxy_mock.init)
        expect_call(server_proxy_mock.move
            ).returning({"YouWin",10})

        self.robot = Robot("robocop", server_proxy_mock)
        self.robot.start(total_moves = 2)

        server_proxy_mock.assert_that_is_satisfied()
        assert_that(self.robot.status, equal_to("YouWin"))
        assert_that(self.robot.score, equal_to(10))

class ServerProxy():
    def init(self, robot_name):
        pass

    def move(self, robot_name, cell):
        pass

class Robot():
    def __init__(self, name, server_proxy):
        self.name = name
        self.server_proxy = server_proxy
        self.score = 0
        self.status = ""
        
    def start(self, total_moves):
        self.server_proxy.init(self.name)
        for x in range(total_moves):
            move_score, status = self.server_proxy.move(self.name, 20)
            self.status = status

            if status == "GameOver":
                break

            if status == "YouWin":
                self.score += move_score
                break

            self.score += move_score