import httpx
import base64

async def generate_response(messages: list, api_key: str, endpoint_url: str, model: str, max_tokens: int) -> str:
    is_azure = "openai.azure.com" in endpoint_url or "azure.com" in endpoint_url

    if is_azure:
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    data = {
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }

    if not is_azure:
        data["model"] = model

    # construct endpoint URL for Azure OpenAI
    if is_azure:
        if not endpoint_url.endswith('/chat/completions'):
            if '/openai/deployments/' not in endpoint_url:
                endpoint_url = f"{endpoint_url.rstrip('/')}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
    else:
        # regular OpenAI endpoint format
        if not (
            endpoint_url.endswith('/chat/completions') or
            '/v1/completions' in endpoint_url or
            '/v1/chat/completions' in endpoint_url
        ):
            endpoint_url = f"{endpoint_url.rstrip('/')}/v1/chat/completions"

    
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(endpoint_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]

def encode_image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string for API consumption"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_image_message(text: str, image_path: str, image_detail: str = "high") -> dict:
    """Create a message with both text and image content"""
    base64_image = encode_image_to_base64(image_path)
    
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": text
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": image_detail
                }
            }
        ]
    }