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
        
        for x in range(total_moves):
            next_cell = self.next_cell_calculator.next()
            status, score = self.server_proxy.move(
                                    self.name, next_cell)
            self.status = status
            
            if status == "GameOver" or status == "YouWin":
                break

            self.score = score

class NextCellCalculator():
    def __init__(self, min_cell, max_cell):
        self.min_cell = min_cell
        self.max_cell = max_cell
        self.last_cell = self.min_cell

    def next(self):
        self.last_cell += 15
        if self.last_cell > self.max_cell:
            self.last_cell = self.min_cell
        return self.last_cell