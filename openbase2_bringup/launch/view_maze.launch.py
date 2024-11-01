from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
import os
import xacro
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    urdf_dir = get_package_share_directory('openbase2_description')
    this_dir = get_package_share_directory('openbase2_bringup')
    world_dir = get_package_share_directory('aws_robomaker_small_house_world')

    xacro_file = os.path.join(urdf_dir, 'urdf', 'openbase2.xacro')
    maze_world_file = os.path.join(this_dir, 'worlds', 'maze.world')
    house_world_file = os.path.join(world_dir, 'worlds', 'small_house.world')

    robot_description_config = xacro.process_file(xacro_file)
    robot_urdf = robot_description_config.toxml()

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {'robot_description': robot_urdf,
             'use_sim_time': True}
        ]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': True}]
    )

    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzserver.launch.py'
            ])
        ]),
        launch_arguments={
            'pause': 'false',
            'world': maze_world_file
        }.items()
    )

    # gazebo_server = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([
    #         PathJoinSubstitution([
    #             FindPackageShare('gazebo_ros'),
    #             'launch',
    #             'gzserver.launch.py'
    #         ])
    #     ]),
    #     launch_arguments={
    #         'pause': 'false'
    #     }.items()
    # )


    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzclient.launch.py'
            ])
        ])
    )

    urdf_spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'openbase2',
            '-topic', 'robot_description'
        ],
        output='screen'
    )


    return LaunchDescription([
        LogInfo(msg="Launching robot state publisher..."),
        robot_state_publisher_node,
        LogInfo(msg="Launching joint state publisher..."),
        joint_state_publisher_node,
        LogInfo(msg="Launching Gazebo server..."),
        gazebo_server,
        LogInfo(msg="Launching Gazebo client..."),
        gazebo_client,
        LogInfo(msg="Spawning robot in Gazebo..."),
        urdf_spawn_node
    ])
