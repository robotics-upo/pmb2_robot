# Copyright (c) 2024 PAL Robotics S.L. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
import os

from ament_index_python.packages import get_package_share_directory
from controller_manager.launch_utils import generate_load_controller_launch_description
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import GroupAction
from launch_pal.arg_utils import LaunchArgumentsBase
from launch_pal.robot_arguments import CommonArgs
from launch_pal.arg_utils import read_launch_argument
from launch.actions import SetLaunchConfiguration, OpaqueFunction
from launch.substitutions import LaunchConfiguration


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):
    is_public_sim: DeclareLaunchArgument = CommonArgs.is_public_sim


def generate_launch_description():

    # Create the launch description and populate
    ld = LaunchDescription()
    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld


def declare_actions(
    launch_description: LaunchDescription, launch_args: LaunchArguments
):
    pkg_share_folder = get_package_share_directory('pmb2_controller_configuration')

    launch_description.add_action(OpaqueFunction(
        function=set_base_config_file))

    # Base controller
    base_controller = GroupAction(
        [
            generate_load_controller_launch_description(
                controller_name='mobile_base_controller',
                controller_params_file=LaunchConfiguration("base_config_file"),
                controller_type='diff_drive_controller/DiffDriveController'
            )
        ],
    )
    launch_description.add_action(base_controller)

    # Joint state broadcaster
    joint_state_broadcaster = GroupAction(
        [
            generate_load_controller_launch_description(
                controller_name='joint_state_broadcaster',
                controller_params_file=os.path.join(
                    pkg_share_folder, 'config', 'joint_state_broadcaster.yaml'),
                controller_type='joint_state_broadcaster/JointStateBroadcaster'
            )
        ],
    )
    launch_description.add_action(joint_state_broadcaster)

    # IMU sensor broadcaster
    imu_sensor_broadcaster = GroupAction(
        [
            generate_load_controller_launch_description(
                controller_name='imu_sensor_broadcaster',
                controller_params_file=os.path.join(
                    pkg_share_folder, 'config', 'imu_sensor_broadcaster.yaml'),
                controller_type='imu_sensor_broadcaster/IMUSensorBroadcaster'
            )
        ],
    )
    launch_description.add_action(imu_sensor_broadcaster)

    return


def set_base_config_file(context):

    is_public_sim = read_launch_argument("is_public_sim", context)
    pkg_share_folder = get_package_share_directory('pmb2_controller_configuration')

    controller_file = 'mobile_base_controller.yaml'

    if is_public_sim:
        controller_file = 'mobile_base_controller_public_sim.yaml'

    base_config_file = os.path.join(pkg_share_folder, 'config', controller_file)

    return [SetLaunchConfiguration("base_config_file", base_config_file)]
