import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Quaternion
from nav2_msgs.action import FollowWaypoints
import math
import threading
import sys
import select
import termios
import tty
from interface.msg import CenterPoint
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class WaypointFollower(Node):
    def __init__(self):
        super().__init__('waypoint_follower')
        self.action_client = ActionClient(self, FollowWaypoints, '/follow_waypoints')
        self._goal_handle = None
        self.point_index = 0
        self.circuit = False
        self.waypoints = self.create_waypoints(1)  # 웨이포인트 리스트 생성
        self.homeoutpoint = self.create_waypoints(2)  # 웨이포인트 리스트 생성
        self.homeinpoint = self.create_waypoints(3)  # 웨이포인트 리스트 생성
        
        ### LEE
        self.pub_cmd_vel=self.create_publisher(Twist,'/cmd_vel',10)
        self.sub_center_point = self.create_subscription(CenterPoint,'/center_point',self.callback_center_point,10)
        self.publisher = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10) 
        self.sub_nav_state = self.create_subscription(String,'/robot_actions',self.callback_nav_state,10)
        self.pub_nav_state = self.create_publisher(String,'/robot_actions',10)
        self.detect_object = False
        self.center_p = Twist()
        self.home_out = False
        self.goal_seq = -1
        self.cnt = 0
        self.pose_init()

    def euler_to_quaternion(self, roll, pitch, yaw):
        # Convert Euler angles to a quaternion
        qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) - math.cos(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
        qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2)
        qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2) - math.sin(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2)
        qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
        return Quaternion(x=qx, y=qy, z=qz, w=qw)

    def create_waypoints(self, num):
        # 웨이포인트들을 정의하는 함수
        waypoints = []

        if num == 1:#순회 포인트
            # 첫 번째 웨이포인트
            waypoint1 = PoseStamped()
            waypoint1.header.stamp.sec = 0
            waypoint1.header.stamp.nanosec = 0
            waypoint1.header.frame_id = "map"
            waypoint1.pose.position.x = -0.428#-0.576
            waypoint1.pose.position.y = -0.539#-0.529
            waypoint1.pose.position.z = 0.0
            waypoint1_yaw = math.pi  # Target orientation in radians
            waypoint1.pose.orientation = self.euler_to_quaternion(0, 0, waypoint1_yaw)
            waypoints.append(waypoint1)

            # 두 번째 웨이포인트
            waypoint2 = PoseStamped()
            waypoint2.header.stamp.sec = 0
            waypoint2.header.stamp.nanosec = 0
            waypoint2.header.frame_id = "map"
            waypoint2.pose.position.x = -0.566#-0.645
            waypoint2.pose.position.y = -0.076#-0.078
            waypoint2.pose.position.z = 0.0
            waypoint2_yaw = math.pi/2
            waypoint2.pose.orientation = self.euler_to_quaternion(0, 0, waypoint2_yaw)
            waypoints.append(waypoint2)

            # 세 번째 웨이포인트
            waypoint3 = PoseStamped()
            waypoint3.header.stamp.sec = 0
            waypoint3.header.stamp.nanosec = 0
            waypoint3.header.frame_id = "map"
            waypoint3.pose.position.x = -1.549#-1.48
            waypoint3.pose.position.y = 0.040#0.621
            waypoint3.pose.position.z = 0.0
            waypoint3_yaw = math.pi
            waypoint3.pose.orientation = self.euler_to_quaternion(0, 0, waypoint3_yaw)
            waypoints.append(waypoint3)

            # 네 번째 웨이포인트
            waypoint4 = PoseStamped()
            waypoint4.header.stamp.sec = 0
            waypoint4.header.stamp.nanosec = 0
            waypoint4.header.frame_id = "map"
            waypoint4.pose.position.x = -1.612#-1.55
            waypoint4.pose.position.y = -0.533#-0.291
            waypoint4.pose.position.z = 0.0
            waypoint4_yaw = -math.pi / 2
            waypoint4.pose.orientation = self.euler_to_quaternion(0, 0, waypoint4_yaw)
            waypoints.append(waypoint4) 
            
            # 5 번째 웨이포인트
            waypoint5 = PoseStamped()
            waypoint5.header.stamp.sec = 0
            waypoint5.header.stamp.nanosec = 0
            waypoint5.header.frame_id = "map"
            waypoint5.pose.position.x = -1.549#-1.48
            waypoint5.pose.position.y = 0.040#-0.621
            waypoint5.pose.position.z = 0.0
            waypoint5_yaw = math.pi / 2
            waypoint5.pose.orientation = self.euler_to_quaternion(0, 0, waypoint5_yaw)
            waypoints.append(waypoint5) 
            
            # 6 번째 웨이포인트
            waypoint6 = PoseStamped()
            waypoint6.header.stamp.sec = 0
            waypoint6.header.stamp.nanosec = 0
            waypoint6.header.frame_id = "map"
            waypoint6.pose.position.x = -0.566
            waypoint6.pose.position.y = -0.076
            waypoint6.pose.position.z = 0.0
            waypoint6_yaw = 0
            waypoint6.pose.orientation = self.euler_to_quaternion(0, 0, waypoint6_yaw)
            waypoints.append(waypoint6) 
            
        elif num == 2 :# 홈 아웃 포인트
            # 첫 번째 웨이포인트
            waypoint1 = PoseStamped()
            waypoint1.header.stamp.sec = 0
            waypoint1.header.stamp.nanosec = 0
            waypoint1.header.frame_id = "map"
            waypoint1.pose.position.x = 0.35#0.313
            waypoint1.pose.position.y = -0.026#-0.015
            waypoint1.pose.position.z = 0.0
            waypoint1_yaw = 0.0  # Target orientation in radians
            waypoint1.pose.orientation = self.euler_to_quaternion(0, 0, waypoint1_yaw)
            waypoints.append(waypoint1)

            # 두 번째 웨이포인트
            waypoint2 = PoseStamped()
            waypoint2.header.stamp.sec = 0
            waypoint2.header.stamp.nanosec = 0
            waypoint2.header.frame_id = "map"
            waypoint2.pose.position.x = 0.273#0.244
            waypoint2.pose.position.y = -0.644#-0.541
            waypoint2.pose.position.z = 0.0
            waypoint2_yaw = -math.pi / 2
            waypoint2.pose.orientation = self.euler_to_quaternion(0, 0, waypoint2_yaw)
            waypoints.append(waypoint2)

            # 세 번째 웨이포인트
            waypoint3 = PoseStamped()
            waypoint3.header.stamp.sec = 0
            waypoint3.header.stamp.nanosec = 0
            waypoint3.header.frame_id = "map"
            waypoint3.pose.position.x = -0.10#-0.056
            waypoint3.pose.position.y = -0.622#-0.572
            waypoint3.pose.position.z = 0.0
            waypoint3_yaw = -math.pi
            waypoint3.pose.orientation = self.euler_to_quaternion(0, 0, waypoint3_yaw)
            waypoints.append(waypoint3)

        elif num == 3:# 홈 인 포인트
            # 첫 번째 웨이포인트
            waypoint1 = PoseStamped()
            waypoint1.header.stamp.sec = 0
            waypoint1.header.stamp.nanosec = 0
            waypoint1.header.frame_id = "map"
            waypoint1.pose.position.x = -0.10
            waypoint1.pose.position.y = -0.622
            waypoint1.pose.position.z = 0.0
            waypoint1_yaw = 0#-math.pi  # Target orientation in radians
            waypoint1.pose.orientation = self.euler_to_quaternion(0, 0, waypoint1_yaw)
            waypoints.append(waypoint1)

            # 두 번째 웨이포인트
            waypoint2 = PoseStamped()
            waypoint2.header.stamp.sec = 0
            waypoint2.header.stamp.nanosec = 0
            waypoint2.header.frame_id = "map"
            waypoint2.pose.position.x = 0.273
            waypoint2.pose.position.y = -0.644
            waypoint2.pose.position.z = 0.0
            waypoint2_yaw = 0#0-math.pi
            waypoint2.pose.orientation = self.euler_to_quaternion(0, 0, waypoint2_yaw)
            waypoints.append(waypoint2)

            # 세 번째 웨이포인트
            waypoint3 = PoseStamped()
            waypoint3.header.stamp.sec = 0
            waypoint3.header.stamp.nanosec = 0
            waypoint3.header.frame_id = "map"
            waypoint3.pose.position.x =  0.35
            waypoint3.pose.position.y = -0.026
            waypoint3.pose.position.z = 0.0
            waypoint3_yaw = math.pi/2#0.0
            waypoint3.pose.orientation = self.euler_to_quaternion(0, 0, waypoint3_yaw)
            waypoints.append(waypoint3)
            
            # 네 번째 웨이포인트
            waypoint4 = PoseStamped()
            waypoint4.header.stamp.sec = 0
            waypoint4.header.stamp.nanosec = 0
            waypoint4.header.frame_id = "map"
            waypoint4.pose.position.x = 0.00
            waypoint4.pose.position.y = 0.00
            waypoint4.pose.position.z = 0.0
            waypoint4_yaw = math.pi#0.0
            waypoint4.pose.orientation = self.euler_to_quaternion(0, 0, waypoint4_yaw)
            waypoints.append(waypoint4)
        else :
            pass

        return waypoints

    def send_goal(self, num):
        # FollowWaypoints 액션 목표 생성 및 전송
        self.detect_object = False
        goal_msg = FollowWaypoints.Goal()

        if num == 1:
            transwaypoints = []
            len_index = len(self.waypoints)
            for i in range(len_index):
                index = self.point_index % len_index
                transwaypoints.append(self.waypoints[index])
                self.point_index += 1

            #self.get_logger().info(f'{transwaypoints}')
            self.point_index = 0
            self.waypoints = transwaypoints
            goal_msg.poses = self.waypoints
            self.circuit = True
        elif num == 2:
            goal_msg.poses = self.homeoutpoint
            self.circuit = False
        elif num == 3:
            goal_msg.poses = self.homeinpoint
            self.circuit = False
        else :
            pass


        # 서버 연결 대기
        self.action_client.wait_for_server()

        # 목표 전송 및 피드백 콜백 설정
        self._send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')
        self._goal_handle = goal_handle  # 목표 핸들을 저장s
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        # self.get_logger().info(f'Current Waypoint Index: {feedback.current_waypoint}')
        
        if self.circuit == True: 
            self.point_index = feedback.current_waypoint
        else : 
            pass

    def cancel_goal(self):
        if self._goal_handle is not None:
            self.get_logger().info('Attempting to cancel the goal...')
            self.circuit = False  # 순회를 중단
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_done_callback)
        else:
            self.get_logger().info('No active goal to cancel.')

    def cancel_done_callback(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info('Goal cancellation accepted. Exiting program...')
        else:
            self.get_logger().info('Goal cancellation failed or no active goal to cancel.')

    def get_result_callback(self, future):
        result = future.result().result
        missed_waypoints = result.missed_waypoints
        if missed_waypoints:
            self.get_logger().info(f'Missed waypoints: {missed_waypoints}')
        else:
            self.get_logger().info('All waypoints completed successfully!')
        
        ## home_out 후 바로 순회를 시키기 위한 로직
        if self.home_out == False and self.goal_seq == '2':
            self.home_out = True
            pub_state = String()
            pub_state.data = '1'
            self.pub_nav_state.publish(pub_state)
            # self.send_goal(1)
        
        # 순회가 활성화된 경우 무한 반복
        if self.circuit:
            self.get_logger().info('Restarting waypoint circuit...')
            self.send_goal(1)  # 순회를 다시 시작
            
    def callback_center_point(self,data):
        if data.centerx != 0.0:
            if self.detect_object == False:
                self.detect_object = True
                self.get_logger().info('현재 목적지 취소')
                self.cancel_goal()
            else:
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
                        self.center_p.angular.z=0.0
                        self.center_p.linear.x=-data.centery/500
                        if self.center_p.linear.x >= 0.22:
                            self.center_p.linear.x=0.2
                        self.pub_cmd_vel.publish(self.center_p)
                else:
                    self.center_p.linear.x=0.0
                    self.center_p.angular.z=-data.centerx/500
                    self.pub_cmd_vel.publish(self.center_p)

        elif data.centerx == 0.0:
            if self.detect_object == True:
                #self.get_logger().info('물체 놓힘.')
                self.center_p.linear.x=0.0
                self.center_p.angular.z=-0.50
                self.pub_cmd_vel.publish(self.center_p)
       
    def callback_nav_state(self,data):
        self.goal_seq = data.data
        if self.goal_seq == '2':
            self.send_goal(2)
            print('cur_data = 2')
            # self.get_logger().info(f'cur_data = {data.data}')
        elif self.goal_seq == '3':
            self.send_goal(3)
            self.home_out = False ## 홈으로 들어가니까 home_out 후에 바로 순회시키기 위해
            print('cur_data = 3')
        elif self.goal_seq == '1':
            self.send_goal(1)
            print('cur_data = 1')
        elif self.goal_seq == '4':
            self.get_logger().info('현재 목적지 취소')
            self.cancel_goal()
            print('cur_data = 4')
        elif self.goal_seq == '5':
            self.pose_init()
        else:
            print('aaaa: {0}'.format(self.goal_seq))
        
    def pose_init(self):
        initial_pose = PoseWithCovarianceStamped()
        initial_pose.header.frame_id = 'map'  # The frame in which the pose is defined
        initial_pose.header.stamp = self.get_clock().now().to_msg()

            # Set the position (adjust these values as needed)
        initial_pose.pose.pose.position.x = 0.0#0.1750425100326538 # X-coordinate
        initial_pose.pose.pose.position.y = 0.070#0.05808566138148308 # Y-coordinate
        initial_pose.pose.pose.position.z = 0.0  # Z should be 0 for 2D navigation

            # Set the orientation (in quaternion form)
        initial_pose.pose.pose.orientation = Quaternion(
            x=0.0,
            y=0.0,
            z=0.0,#-0.0872,#0.0,  # 90-degree rotation in yaw (example)
            w=1.0#0.9962#1.0#0.9989004975549108  # Corresponding quaternion w component
        )

            # Set the covariance values for the pose estimation
        initial_pose.pose.covariance = [
            0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891909122467
        ]
            # Publish the initial pose
        print('zzzzzzzzzzzzzzzzzzzzzzz')
        self.publisher.publish(initial_pose)
        

def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollower()
    node.pose_init()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()