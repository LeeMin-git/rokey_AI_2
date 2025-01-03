from setuptools import find_packages, setup

package_name = 'project'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rokey6',
    maintainer_email='rokey6@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot=project.project:main',
            'robot_2d_estimate=project.init_pose:main',
            'send_waypoint=project.send_waypoint:main',
            'init_pose=project.init_pose:main'
        ],
    },
)
