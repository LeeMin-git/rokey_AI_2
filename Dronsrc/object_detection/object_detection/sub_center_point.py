import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from interface.msg import CenterPoint
class CenterPointSubscriber(Node):

    def __init__(self):
        super().__init__('center_point_subscriber')
        self.subscription = self.create_subscription(
            CenterPoint,
            'center_point',
            self.point_callback,
            10
        )
        self.subscription  # prevent unused variable warning

    def point_callback(self, msg):
        if msg is not None:
            # Display the image using OpenCV
            print(msg)
        else:
            pass
def main(args=None):
    rclpy.init(args=args)
    center_point_subscriber = CenterPointSubscriber()
    rclpy.spin(center_point_subscriber)
    center_point_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
