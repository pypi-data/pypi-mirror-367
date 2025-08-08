tool_call_schema = {
    "type": "object",
    "properties": {
        "tool_name": {
            "type": "string",
            "description": "Name of the tool to use, must be one of available_playwright_tools"
        },
        "parameters": {
            "type": "object",
            "description": "Key-value arguments to pass to the tool",
            "additionalProperties": {
                "type": ["string", "number", "boolean", "null"],
                "description": "Parameter value based on tool's expected type"
            }
        },
        "reasoning": {
            "type": "string",
            "description": "Explanation of why this tool was chosen"
        }
    },
    "required": ["tool_name", "reasoning"],
    "additionalProperties": False
}
