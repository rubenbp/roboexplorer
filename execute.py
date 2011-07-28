from robot import Robot, ServerProxy, UrlGenerator, NextCellCalculator

__author__ = 'rubenbp'

def execute_robot(robot_name, total_moves):
    robot = Robot(
                robot_name,
                ServerProxy(UrlGenerator("http://188.165.135.37:81/game?")),
                NextCellCalculator(0, 100))
    
    print("Robot start!")
    robot.start(total_moves = total_moves)
    print("Robot finish!")
    print("Result: " + robot.status)
    print("Score.: " + str(robot.score))

if __name__ == '__main__':
    execute_robot("robocop", 50)
  