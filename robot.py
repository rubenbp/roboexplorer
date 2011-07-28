import time
import urllib2
from django.utils import simplejson

__author__ = 'rubenbp'

class ServerProxy():
    def __init__(self, url_generator):
        self.url_generator = url_generator

    def init(self, robot_name):
        init_url = self.url_generator.init_url(robot_name)
        result = simplejson.load(urllib2.build_opener().open(urllib2.Request(init_url)))
        return result["status"]

    def move(self, robot_name, cell):
        move_url = self.url_generator.move_url(robot_name, cell)
        result = simplejson.load(urllib2.build_opener().open(urllib2.Request(move_url)))
        time.sleep(0.2)
        if result.has_key("score"):
            return result["status"],result["score"]
        return result["status"], 0

class UrlGenerator():
    def __init__(self, base_url):
        self.base_url = base_url

    def move_url(self, robot_name, cell):
        pass

    def init_url(self, robot_name):
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