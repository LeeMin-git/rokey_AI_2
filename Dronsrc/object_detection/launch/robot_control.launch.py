import os
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch import LaunchDescription

def generate_launch_description():
    package_name = 'object_detection'
    
    init = Node(
        package='project',
        executable='init_pose',
        name='init_pose',
        output='screen',
    )
    
    detect = Node(
        package=package_name,
        executable='check_drone',
        name='check_drone',
        output='screen',
    )
    move = Node(
        package='project',
        executable='send_waypoint',
        name='send_waypoint',
        output='screen',
    )
    
    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([get_package_share_directory('turtlebot3_bringup'),'/launch/robot.launch.py']),
    )
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([get_package_share_directory('turtlebot3_navigation2'),'/launch/navigation2.launch.py']),
    )
    
    return LaunchDescription([
        init,
        move,
        # bringup,
        # nav2,
        detect,
    ])