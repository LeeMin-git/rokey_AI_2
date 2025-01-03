import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped


class MovingRobot(Node):
    def __init__(self):
        super().__init__('moving_robor')
        



def main():
    rclpy.init()
    node=MovingRobot()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()