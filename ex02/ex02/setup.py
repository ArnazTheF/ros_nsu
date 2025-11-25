from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'ex02'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='TF2 Broadcaster and Listener exercise',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtle1_tf2_broadcaster = ex02.turtle1_tf2_broadcaster:main',
            'turtle2_tf2_broadcaster = ex02.turtle2_tf2_broadcaster:main',
            'carrot_tf2_broadcaster = ex02.carrot_tf2_broadcaster:main',
            'turtle2_tf2_listener = ex02.turtle2_tf2_listener:main',
        ],
    },
)