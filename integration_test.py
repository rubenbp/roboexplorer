from datetime import datetime
import unittest
from hamcrest.core.assert_that import assert_that
from hamcrest.library.number.ordering_comparison import greater_than_or_equal_to
from pyDoubles.framework import spy, assert_that_method, when
from robot import *

__author__ = 'rubenbp'

class ServerProxyTests(unittest.TestCase):

    def setUp(self):
        self.url_generator_spy = spy(UrlGenerator(None))
        when(self.url_generator_spy.move_url).then_return("http://fake/")

        self.server_proxy = ServerProxy(self.url_generator_spy)

    def test_no_more_than_one_move_at_a_minimum(self):
        self.server_proxy.move("robocop", 10)
        time1 = datetime.now()
        self.server_proxy.move("robocop", 12)
        time2 = datetime.now()

        assert_that(
            (time2 - time1).microseconds,
            greater_than_or_equal_to(200))

    def test_use_url_server_generator_to_move(self):
        self.server_proxy.move("robocop", 10)

        assert_that_method(self.url_generator_spy.move_url
            ).was_called().with_args("robocop",10)

    def test_use_url_server_generator_to_init(self):
        self.server_proxy.init("robocop")

        assert_that_method(self.url_generator_spy.init_url
            ).was_called().with_args("robocop")