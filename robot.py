import time
import urllib2
from django.utils import simplejson

__author__ = 'rubenbp'

class ServerProxy():
    def __init__(self, url_generator):
        self.url_generator = url_generator

    def init(self, robot_name):
        init_url = self.url_generator.init_url(robot_name)
        result = self._get_json_from_url(init_url)
        print("init game: status '%s'" % result["status"])
        return result["status"]

    def move(self, robot_name, cell):
        move_url = self.url_generator.move_url(robot_name, cell)
        result = self._get_json_from_url(move_url)
        time.sleep(0.2)
        if result.has_key("score"):
            print("new move: status '%s' & score '%s'" % (result["status"], result["score"]))
            return result["status"],result["score"]

        #need only for testing
        return result["status"], 0

    def _get_json_from_url(self, url):
        return simplejson.load(urllib2.build_opener().open(urllib2.Request(url)))

class UrlGenerator():
    def __init__(self, base_url):
        self.base_url = base_url

    def move_url(self, robot_name, cell):
        return self.base_url + "player=%s&command=Move&position=%s" % (robot_name, cell)

    def init_url(self, robot_name):
        return self.base_url + "player=%s&command=Init" % robot_name
    
class Robot():
    def __init__(self, name, server_proxy, next_cell_calculator):
        self.name = name
        self.server_proxy = server_proxy
        self.next_cell_calculator = next_cell_calculator
        self.score = 0
        self.status = ""

    def start(self, total_moves):
        status = self.server_proxy.init(self.name)
        if status == "GameOver":
            return

        last_score = 0
        for x in range(total_moves):
            next_cell = self.next_cell_calculator.next()
            self.status, score = self.server_proxy.move(
                                    self.name, next_cell)

            if status == "GameOver" or status == "YouWin":
                break

            score_of_this_movement = score - last_score
            self.next_cell_calculator.register_cell_score(next_cell, score_of_this_movement)
            last_score = score
            self.score = score

class NextCellCalculator():
    def __init__(self, min_cell, max_cell):
        self.min_cell_index = min_cell
        self.max_cell_index = max_cell
        self.last_cell = Cell(self.min_cell_index, -1)
        self.cell_scores = {}

    def next(self):
        next_cell_index = self.last_cell.index + 15
        if next_cell_index > self.max_cell_index:
            self.last_cell = Cell(self.min_cell_index)
        else:
            self.last_cell = Cell(next_cell_index)
        return self.last_cell.index

    def register_cell_score(self, cell_index, cell_score):
        self.cell_scores[cell_index] = cell_score
        self.last_cell = Cell(cell_index, cell_score)

class Cell():
    def __init__(self, index, score = -1):
        self.index = index
        self.score = score