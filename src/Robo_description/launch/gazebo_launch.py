from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Paths
    pkg_share = FindPackageShare("Robo_description")

    # Robot description (URDF from xacro)
    robot_description = Command([
        "xacro ",
        PathJoinSubstitution([pkg_share, "urdf", "Robo_macro.urdf.xacro"])
    ])

    # Start robot_state_publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}]
    )

    # Joint state publisher (for testing)
    joint_state_publisher = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen"
    )

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"])
        ])
    )

    # Spawn entity in Gazebo
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "robot_description", "-entity", "roboarm"],
        output="screen"
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        gazebo,
        spawn_entity,
    ])

