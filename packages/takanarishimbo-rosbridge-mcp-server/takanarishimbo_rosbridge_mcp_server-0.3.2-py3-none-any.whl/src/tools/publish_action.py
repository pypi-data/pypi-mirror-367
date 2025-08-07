"""
Publish Action Tool

Sends goals to ROS action servers via rosbridge.
"""

import asyncio
from typing import Any
import uuid

import roslibpy
import roslibpy.actionlib
from mcp.types import Tool


PUBLISH_ACTION_TOOL = Tool(
    name="publish_action",
    description="Send a goal to a ROS action server",
    inputSchema={
        "type": "object",
        "properties": {
            "action_name": {
                "type": "string",
                "description": "The ROS action server name (e.g., '/move_base')",
            },
            "action_type": {
                "type": "string",
                "description": "The ROS action type (e.g., 'move_base_msgs/MoveBaseAction')",
            },
            "goal": {
                "type": "object",
                "description": "The goal data as a JSON object",
            },
            "timeout": {
                "type": "number",
                "description": "Timeout in seconds to wait for result (default: 30)",
                "default": 30,
            },
        },
        "required": ["action_name", "action_type", "goal"],
    },
)


async def publish_action(ros: roslibpy.Ros, action_name: str, action_type: str, goal: dict[str, Any], timeout: float = 30.0) -> dict[str, Any]:
    """
    Send a goal to a ROS action server.

    Args:
        ros: The ROS connection instance
        action_name: The ROS action server name
        action_type: The ROS action type
        goal: The goal data as a dictionary
        timeout: Timeout in seconds to wait for result

    Returns:
        A dictionary containing the result or error information
    """
    try:
        # Create action client
        action_client = roslibpy.actionlib.ActionClient(ros, action_name, action_type)

        # Generate a unique goal ID
        goal_id = str(uuid.uuid4())

        # Create futures for tracking the action
        result_future = asyncio.Future()
        feedback_messages = []

        def handle_result(result):
            result_future.set_result({"success": True, "result": result, "goal_id": goal_id, "feedback": feedback_messages})

        def handle_feedback(feedback):
            feedback_messages.append(feedback)

        def handle_failure(error):
            result_future.set_result({"success": False, "error": str(error), "goal_id": goal_id, "feedback": feedback_messages})

        # Create goal message with roslibpy.Message
        goal_msg = roslibpy.Message(goal)

        # Create and configure the goal
        goal_handle = roslibpy.actionlib.Goal(action_client, goal_msg)
        goal_handle.on("result", handle_result)
        goal_handle.on("feedback", handle_feedback)
        goal_handle.on("status", lambda status: None)  # Status updates
        goal_handle.on("timeout", lambda: handle_failure("Goal timeout"))

        # Send goal and wait for result
        goal_handle.send()

        try:
            result = await asyncio.wait_for(result_future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            # Cancel the goal on timeout
            goal_handle.cancel()
            return {"success": False, "error": f"Timeout waiting for action result after {timeout} seconds", "goal_id": goal_id, "feedback": feedback_messages}
        finally:
            # Clean up the action client
            action_client.dispose()

    except Exception as e:
        return {"success": False, "error": f"Failed to send action goal: {str(e)}"}
