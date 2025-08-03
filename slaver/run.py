import json
import threading
import importlib
import rclpy
from functools import partial
from flag_scale.flagscale.agent.communication import Communicator
from tools.hospital_tools import HospitalRos2Bridge

class SlaverAgent:
    def __init__(self, config_path="slaver/config.yaml"):
        # ... (existing __init__ code) ...

        # --- New code for ROS2 integration ---
        self.ros2_node = rclpy.create_node('slaver_agent_node')
        self.ros2_bridge = HospitalRos2Bridge(self.ros2_node)
        self.ros2_thread = threading.Thread(target=rclpy.spin, args=(self.ros2_node,))
        self.ros2_thread.start()
        # --- End of new code ---

        self.tools = self.load_tools()

    # ... (existing code) ...

    def load_tools(self):
        return {
            "guide_patient": self.ros2_bridge.guide_patient,
            "speak": self.ros2_bridge.speak,
        }

    def _handle_task(self, data: Dict) -> None:
        """Handle tasks from the master."""
        task_id = data.get("task_id")
        task = data.get("task")
        # ... (existing code) ...

        try:
            task_details = json.loads(task)
            func_name = task_details.get("function_name")
            parameters = task_details.get("parameters", {})

            if func_name in self.tools:
                result = self.tools[func_name](**parameters)
                self.logger.info(f"Executed tool '{func_name}' with result: {result}")
                # ... (send result back to master) ...
            else:
                self.logger.error(f"Tool '{func_name}' not found.")
                # ... (send error back to master) ...

        except json.JSONDecodeError:
            self.logger.error(f"Could not decode task: {task}")
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")

if __name__ == "__main__":
    rclpy.init()
    agent = SlaverAgent()