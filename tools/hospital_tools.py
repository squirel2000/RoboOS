import json

# This is our "database" of doctors. In a real system, this would be a database query.
HOSPITAL_DOCTORS = {
    "Gastroenterology": {"name": "Dr. Smith", "room": "001"},
    "Cardiology": {"name": "Dr. Jones", "room": "102"},
    "Neurology": {"name": "Dr. Patel", "room": "205"},
    "General Practice": {"name": "Dr. Williams", "room": "003"},
}

def find_doctor_by_specialty(specialty: str) -> str:
    """
    Finds an available doctor's name and room number based on their medical specialty.
    
    Args:
        specialty (str): The medical specialty to search for.
        
    Returns:
        str: A JSON string containing the doctor's name and room, or an error message.
    """
    print(f"Executing tool: find_doctor_by_specialty with specialty='{specialty}'")
    if specialty in HOSPITAL_DOCTORS:
        doctor_info = HOSPITAL_DOCTORS[specialty]
        print(f"Found doctor: {doctor_info}")
        return json.dumps(doctor_info)
    else:
        print(f"No doctor found for specialty: {specialty}")
        return json.dumps({"error": f"No doctor found for specialty '{specialty}'."})

def guide_patient_to_room(room_number: str) -> str:
    """
    Dispatches a mobile robot to guide a patient to a specific room number.
    This function would typically send a command to the RoboOS Slaver.
    For the Master, we just confirm that the task has been initiated.
    
    Args:
        room_number (str): The destination room number.
        
    Returns:
        str: A JSON string confirming the task was dispatched.
    """
    print(f"Executing tool: guide_patient_to_room with room_number='{room_number}'")
    # In a real implementation, this would publish a message to Redis for the Slaver.
    # For now, it just confirms the plan step is complete.
    result = {"status": "SUCCESS", "message": f"Task to guide patient to room {room_number} has been dispatched."}
    return json.dumps(result)

def speak(message: str) -> str:
    """
    Allows the robot to say a message out loud.
    
    Args:
        message (str): The message for the robot to speak.
        
    Returns:
        str: A JSON string confirming the action.
    """
    print(f"Executing tool: speak with message='{message}'")
    # This would also be a task for the Slaver.
    result = {"status": "SUCCESS", "message": f"Speak task with message '{message}' dispatched."}
    return json.dumps(result)

# We can create a dictionary to easily map tool names to functions
HOSPITAL_TOOL_FUNCTIONS = {
    "find_doctor_by_specialty": find_doctor_by_specialty,
    "guide_patient_to_room": guide_patient_to_room,
    "speak": speak,
}
