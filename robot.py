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
            print(
                "new move to %s: status '%s' & score '%s'" %
                (cell, result["status"], result["score"]))
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

    def start(self, max_moves):
        status = self.server_proxy.init(self.name)
        if status == "GameOver":
            return

        last_score = 0
        total_moves = 0
        for x in range(max_moves):
            next_cell = self.next_cell_calculator.next()
            total_moves = total_moves + 1
            print("Move number %s" % total_moves)
            self.status, score = self.server_proxy.move(self.name, next_cell)

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
        self.seek = self.min_cell_index
        self.min_cell_score_to_move = 15
        self.jump = 15

    def next(self):
        if self._get_cell_with_max_score() is not None and \
           self._get_cell_with_max_score().index != self.last_cell.index and \
           self._is_valid_next_cell(self._get_cell_with_max_score().index):
            next_cell_index = self._get_cell_with_max_score().index
        else:
            while True:
                self.seek = self.seek + self.jump
                next_cell_index = self.seek % self.max_cell_index
                if self._is_valid_next_cell(next_cell_index):
                    break
                    
        self.last_cell = Cell(next_cell_index)
        return self.last_cell.index

    def _is_valid_next_cell(self, cell_index):
        if cell_index < self.min_cell_index or \
           cell_index > self.max_cell_index:
            return False
        if self.cell_scores.has_key(cell_index) and \
           self.cell_scores[cell_index] < self.min_cell_score_to_move:
            return False
        return True

    def _get_cell_with_max_score(self):
        result = None
        for key in self.cell_scores.keys():
            if result is None or self.cell_scores[key] > result.score:
                result = Cell(key, self.cell_scores[key])
        return result

    def register_cell_score(self, cell_index, cell_score):
        self.cell_scores[cell_index] = cell_score
        self.last_cell = Cell(cell_index, cell_score)

class Cell():
    def __init__(self, index, score = -1):
        self.index = index
        self.score = score