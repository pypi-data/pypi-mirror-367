from .generate_response import generate_response
from ..schemas.tool_call_schema import tool_call_schema
from ..schemas.finished_task_schemas import final_output_when_failed_schema, final_output_when_task_done_schema

class LLMClient:
    def __init__(self, api_key: str, endpoint_url: str, model: str, max_tokens: int = 1000):
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

        self.schemas = {
            "tool_call": tool_call_schema,
            "final_output_when_task_done": final_output_when_task_done_schema,
            "final_output_when_failed": final_output_when_failed_schema
        }

        self.messages = []
        # Store core context separately
        self.system_prompt = None
        self.task_info = None

    def set_core_context(self, system_prompt: str, task_info: str):
        """Set the core context that will be included in every request"""
        self.system_prompt = system_prompt
        self.task_info = task_info

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation. Will be used in the next response generation request."""
        self.messages.append({"role": role, "content": content})


    async def generate(self) -> str:
        """Generate a response from the LLM with fresh context on every call."""
        # Build fresh message list with core context + recent conversation
        fresh_messages = []
        
        # Always include system prompt and task
        if self.system_prompt:
            fresh_messages.append({"role": "system", "content": self.system_prompt})
        if self.task_info:
            fresh_messages.append({"role": "user", "content": self.task_info})
        
        # Include only the most recent conversation (last 10 messages to avoid token limits)
        recent_messages = self.messages[-10:] if len(self.messages) > 10 else self.messages
        fresh_messages.extend(recent_messages)
        
        response = await generate_response(
            messages=fresh_messages,
            api_key=self.api_key,
            endpoint_url=self.endpoint_url,
            model=self.model,
            max_tokens=self.max_tokens
        )
        
        # Only store the assistant response, not the full context
        self.messages.append({"role": "assistant", "content": response})
        return response