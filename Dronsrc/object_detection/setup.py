from setuptools import find_packages, setup
import glob
import os

package_name = 'object_detection'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/'+package_name+'/launch',['launch/robot_control.launch.py']),
    ],
    install_requires=['setuptools','pytest'],
    zip_safe=True,
    maintainer='g1',
    maintainer_email='jwchoi0017@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    #tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'check_drone = object_detection.check_drone:main',
            'sub_compress_image = object_detection.sub_compress_image:main',
            'sub_center_point = object_detection.sub_center_point:main',
        ],
    },
)
