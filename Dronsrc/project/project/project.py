import rclpy
from rclpy.node import Node
from interface.msg import CenterPoint
from geometry_msgs.msg import Twist

class AmrController(Node):
    def __init__(self):
        ## publisher
        super().__init__('armrobot')
        self.pub_cmd_vel=self.create_publisher(Twist,'/cmd_vel',10)

        ## subscriber
        self.sub_center_point = self.create_subscription(CenterPoint,'/center_point',self.callback_center_point,10)

    def callback_center_point(self,data):
        if data:
            self.center_p = Twist()
            if data.centerx>=-200 and data.centerx<=200:
                if data.centery >= -10 and data.centery<=10:
                    self.center_p.linear.x=0.0
                    self.pub_cmd_vel.publish(self.center_p)
                    if data.centerx >= -30 and data.centerx<=30:
                        self.center_p.angular.z=0.0
                    else:
                        self.center_p.linear.x=0.0
                        self.center_p.angular.z=-data.centerx/500
                        self.pub_cmd_vel.publish(self.center_p)
                else:
                    self.center_p.linear.x=-data.centery/500
                    if self.center_p.linear.x >= 0.22:
                        self.center_p.linear.x=0.2
                    self.pub_cmd_vel.publish(self.center_p)
            else:
                self.center_p.linear.x=0.0
                self.center_p.angular.z=-data.centerx/500
                self.pub_cmd_vel.publish(self.center_p)
    
def main():
    rclpy.init()
    amr = AmrController()
    rclpy.spin(amr)
    amr.destroy_node()
    rclpy.shutdown()