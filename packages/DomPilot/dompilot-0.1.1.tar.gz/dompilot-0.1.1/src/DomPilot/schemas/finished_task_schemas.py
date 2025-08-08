final_output_when_task_done_schema = {
    "type": "object",
    "properties": {
        "task_completed": {
            "type": "boolean",
            "const": True
        },
        "data": {
            "type": "object",
            "description": "The final response, matching the response_schema provided by the user"
        }
    },
    "required": ["task_completed", "data"],
    "additionalProperties": False
}

final_output_when_failed_schema = {
    "type": "object",
    "properties": {
        "task_completed": {
            "type": "boolean",
            "const": False
        },
        "error": {
            "type": "string",
            "description": "Detailed message about why the task could not be completed"
        }
    },
    "required": ["task_completed", "error"],
    "additionalProperties": False
}
