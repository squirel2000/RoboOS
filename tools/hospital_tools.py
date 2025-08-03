import rclpy
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus

# This dictionary maps symbolic location names to real-world coordinates.
# In a real system, this could be loaded from a file or a database.
LOCATION_COORDINATES = {
    "Front Desk": {"x": 0.5, "y": 0.5, "z": 0.0, "w": 1.0},
    "Room 001":   {"x": 1.5, "y": -0.5, "z": 0.0, "w": 1.0},
    "Room 002":   {"x": 2.5, "y": -1.5, "z": 0.0, "w": 1.0},
    "Pharmacy":   {"x": -1.0, "y": 2.0, "z": 0.0, "w": 1.0},
}

class HospitalRos2Bridge:
    def __init__(self, node):
        self.node = node
        self.nav_to_pose_client = ActionClient(self.node, NavigateToPose, 'navigate_to_pose')

    def _send_nav_goal(self, location_name: str):
        """Sends a navigation goal to a named location."""
        self.node.get_logger().info(f'Attempting to navigate to symbolic location: {location_name}')
        if location_name not in LOCATION_COORDINATES:
            self.node.get_logger().error(f'Location "{location_name}" is unknown.')
            return False

        coords = LOCATION_COORDINATES[location_name]
        goal_pose = NavigateToPose.Goal()
        goal_pose.pose.header.frame_id = 'map'
        goal_pose.pose.pose.position.x = coords["x"]
        goal_pose.pose.pose.position.y = coords["y"]
        goal_pose.pose.pose.orientation.z = coords["z"]
        goal_pose.pose.pose.orientation.w = coords["w"]

        self.node.get_logger().info(f'Sending navigation goal for {location_name} at {coords}...')
        self.nav_to_pose_client.wait_for_server()
        goal_future = self.nav_to_pose_client.send_goal_async(goal_pose, feedback_callback=self.feedback_callback)
        rclpy.spin_until_future_complete(self.node, goal_future)
        goal_handle = goal_future.result()

        if not goal_handle.accepted:
            self.node.get_logger().info(f'Goal for {location_name} was rejected')
            return False

        self.node.get_logger().info(f'Goal for {location_name} accepted. Waiting for result...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self.node, result_future)
        status = result_future.result().status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.node.get_logger().info(f'Successfully navigated to {location_name}')
            return True
        else:
            self.node.get_logger().warn(f'Navigation to {location_name} failed with status: {status}')
            return False

    def guide_patient(self, start_location: str, end_location: str):
        """Guides a patient from a start location to an end location."""
        self.node.get_logger().info(f'Received task to guide patient from {start_location} to {end_location}')
        
        # 1. Go to the patient's starting location
        self.speak(f"On my way to the {start_location} to find you.")
        if not self._send_nav_goal(start_location):
            return f"Failed to navigate to the {start_location}. Aborting task."

        # 2. Announce arrival and lead the way
        self.speak(f"I have arrived at the {start_location}. Please follow me to the {end_location}.")
        
        # 3. Go to the final destination
        if not self._send_nav_goal(end_location):
            return f"Failed to navigate to the {end_location}."

        self.speak(f"We have arrived at the {end_location}. Please let me know if you need anything else.")
        return f"Successfully guided patient from {start_location} to {end_location}."

    def feedback_callback(self, feedback_msg):
        # You can process feedback here, e.g., distance remaining
        pass

    def speak(self, message: str):
        self.node.get_logger().info(f'ROBOT SPEAKS: "{message}"')
        # In a real system, this would call a ROS2 TTS service.
        return 'Message spoken.'
