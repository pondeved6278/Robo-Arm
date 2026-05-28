import launch
from launch.substitutions import Command, LaunchConfiguration
import launch_ros
from launch.conditions import IfCondition
import os
from launch_ros.descriptions import ParameterValue

def generate_launch_description():
    pkg_share = launch_ros.substitutions.FindPackageShare(package='Robo_description').find('Robo_description')
    default_model_path = os.path.join(pkg_share, 'urdf/Robo_macro.urdf.xacro')
    default_rviz_config_path = os.path.join(pkg_share, 'config/display.rviz')
    world_path = os.path.join(pkg_share, 'worlds/room.sdf')

    use_sim_time = LaunchConfiguration('use_sim_time')

    # ✅ Robot State Publisher (provides robot_description)
    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': ParameterValue(
                Command(['xacro ', LaunchConfiguration('model')]),
                value_type=str
            ),
        }],
        output='screen'
    )

    # ✅ Joint State Publisher GUI (with enforced limits)
    joint_state_publisher_gui_node = launch_ros.actions.Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{
            'use_sim_time': use_sim_time,
            'enforce_limits': True
        }],
        output='screen'
    )

    # ✅ RViz2 for visualization
    rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # ✅ Spawn entity (only when using simulation)
    spawn_entity = launch_ros.actions.Node(
        condition=IfCondition(use_sim_time),
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'Robo', '-topic', 'robot_description'],
        output='screen'
    )

    return launch.LaunchDescription([
        # Arguments
        launch.actions.DeclareLaunchArgument(
            name='use_sim_time',
            default_value='True',
            description='Flag to enable use_sim_time'
        ),
        launch.actions.DeclareLaunchArgument(
            name='model',
            default_value=default_model_path,
            description='Absolute path to robot urdf file'
        ),
        launch.actions.DeclareLaunchArgument(
            name='rvizconfig',
            default_value=default_rviz_config_path,
            description='Absolute path to rviz config file'
        ),

        # ✅ Start Gazebo (if sim mode)
        launch.actions.ExecuteProcess(
            condition=IfCondition(use_sim_time),
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so',
                 '-s', 'libgazebo_ros_factory.so', world_path],
            output='screen'
        ),

        # ✅ Correct launch order
        robot_state_publisher_node,      # publish robot_description first
        joint_state_publisher_gui_node,  # GUI reads limits properly now
        spawn_entity,                    # then spawn robot in Gazebo
        rviz_node,                       # finally, launch RViz
    ])
