from datetime import datetime
import unittest
from hamcrest.core.assert_that import assert_that
from hamcrest.library.number.ordering_comparison import greater_than_or_equal_to
from robot import *

__author__ = 'rubenbp'


class ServerProxyTests(unittest.TestCase):

    def test_no_more_than_one_move_at_a_minimum(self):
        base_url = "http://188.165.135.37:81/test?reponse=MoveOK&"
        server_proxy = ServerProxy(base_url)

        server_proxy.move("robocop", 10)
        time1 = datetime.now()
        server_proxy.move("robocop", 12)
        time2 = datetime.now()

        assert_that(
            (time2 - time1).microseconds,
            greater_than_or_equal_to(200))
  