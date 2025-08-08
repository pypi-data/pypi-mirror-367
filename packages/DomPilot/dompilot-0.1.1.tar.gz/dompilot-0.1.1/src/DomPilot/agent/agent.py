from ..llm_api.llm_client import LLMClient
import json
import os
import jsonschema
from playwright.async_api import async_playwright
from playwright_stealth.stealth import Stealth
import asyncio
from enum import Enum

class LogLevel(Enum):
    NONE = "none"
    MINIMAL = "minimal"
    VERBOSE = "verbose"

class DomPilotAgent:
    def __init__(self, client: LLMClient, log_level: LogLevel = LogLevel.VERBOSE):
        self.client = client
        self.log_level = log_level

    def provide_task(self, url: str, task_description_by_user: str, response_schema_from_user: object, headless: bool = False):
        task_obj = {
            "task_description": task_description_by_user,
            "url": url,
            "response_schema": response_schema_from_user
        }

        task_json = json.dumps(task_obj)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'llm_prompt.txt')

        with open(json_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()

        # set core context that will be sent with every request
        self.client.set_core_context(system_prompt, task_json)

        self.url = url
        self.headless = headless
        self.task_json = task_json

    def _log_(self, message: str, level: LogLevel = LogLevel.VERBOSE):
        """Log message based on current log level"""
        if self.log_level == LogLevel.NONE:
            return
        
        if level == LogLevel.MINIMAL and self.log_level in [LogLevel.MINIMAL, LogLevel.VERBOSE]:
            print(f"✨ [DomPilotAgent] {message}")
        elif level == LogLevel.VERBOSE and self.log_level == LogLevel.VERBOSE:
            print(f"✨ [DomPilotAgent] {message}")

    async def run_agent(self) -> object:
        async with Stealth().use_async(async_playwright()) as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
          
            await page.goto(self.url)

            page.set_default_timeout(2000)

            tool_call_schema = self.client.schemas.get("tool_call")
            final_output_when_task_done_schema = self.client.schemas.get("final_output_when_task_done")
            final_output_when_failed_schema = self.client.schemas.get("final_output_when_failed")
            
            if not all([tool_call_schema, final_output_when_task_done_schema, final_output_when_failed_schema]):
                raise ValueError("Required schemas are not defined in the client.")

            tool_call_count = 0
            max_retries = 10
            retry_count = 0
            
            tool_call_history = []
            max_identical_calls = 3
            
        
            
            # Main loop - handle ANY valid response format from the very first response
            while True:
                await asyncio.sleep(0.8) if tool_call_count > 0 else None  # No delay on first call

                response = await self.client.generate()
                
                # Add debugging to see what the LLM is actually returning
                self._log_(f"[LLMResponse] Raw response: {response[:200]}{'...' if len(response) > 200 else ''}", LogLevel.VERBOSE)
                
                try:
                    response_obj = json.loads(response)
                    self._log_(f"[LLMResponse] Parsed JSON keys: {list(response_obj.keys())}", LogLevel.VERBOSE)
                except json.JSONDecodeError as e:
                    self._log_(f"[JSONError] Invalid JSON from LLM: {e}", LogLevel.VERBOSE)
                    retry_count += 1
                    if retry_count >= max_retries:
                        await browser.close()
                        raise RuntimeError(f"LLM consistently returned invalid JSON after {max_retries} attempts")
                    
                    memory_reminder = ""
                    if hasattr(self, 'memory') and self.memory:
                        memory_reminder = f"\n\n🧠 CURRENT MEMORY: {json.dumps(self.memory)}"
                    
                    error_message = f"INVALID JSON. You must respond with valid JSON only. Error: {e}{memory_reminder}"
                    self.client.add_message("user", error_message)
                    continue

                if final_output_when_task_done_schema is None:
                    await browser.close()
                    raise ValueError("final_output_when_task_done_schema is None and cannot be used for validation.")
                try:
                    jsonschema.validate(instance=response_obj, schema=final_output_when_task_done_schema)
                    self._log_("[TaskCompleted] Final response received.", LogLevel.MINIMAL)
                    await browser.close()
                    return response_obj["data"]
                except jsonschema.ValidationError:
                    pass

                if final_output_when_failed_schema is None:
                    await browser.close()
                    raise ValueError("final_output_when_failed_schema is None and cannot be used for validation.")
                try:
                    jsonschema.validate(instance=response_obj, schema=final_output_when_failed_schema)
                    self._log_(f"[TaskFailed] {response_obj['error']}", LogLevel.MINIMAL)
                    await browser.close()
                    raise RuntimeError(response_obj["error"])
                except jsonschema.ValidationError:
                    pass

                if tool_call_schema is None:
                    await browser.close()
                    raise ValueError("tool_call_schema is None and cannot be used for validation.")
                try:
                    jsonschema.validate(instance=response_obj, schema=tool_call_schema)
                    tool_name = response_obj.get("tool_name")
                    reasoning_for_tool = response_obj.get("reasoning")
                    if not tool_name or not reasoning_for_tool:
                        raise ValueError("Missing tool_name or reasoning in tool call.")
                    
                    self._log_(f"[UsingTool {tool_name}]: {reasoning_for_tool}", LogLevel.MINIMAL)
                    
                    current_call = f"{tool_name}:{response_obj.get('parameters', {}).get('selector', '')}"
                    identical_count = tool_call_history.count(current_call)
                    
                    if identical_count >= max_identical_calls:
                        error_message = f"STOP REPEATING! You've used '{tool_name}' with the same selector {identical_count} times. Try a DIFFERENT approach or tool."
                        self.client.add_message("user", error_message)
                        continue
                    
                    tool_call_history.append(current_call)

                    try:
                        if tool_name == "goto":
                            await page.goto(response_obj.get("parameters", {}).get("url"))
                            result = f"Navigated to {response_obj.get('parameters', {}).get('url', 'URL')}"
                        
                        elif tool_name == "remember":
                            memory_data = response_obj.get("parameters", {})
                            if not hasattr(self, 'memory'):
                                self.memory = {}
                            
                            for key, value in memory_data.items():
                                self.memory[key] = value
                                self._log_(f"[Memory] Stored {key}: {value}", LogLevel.VERBOSE)
                            
                            result = f"Remembered: {list(memory_data.keys())}"
                        elif tool_name == "recall":
                            if not hasattr(self, 'memory'):
                                self.memory = {}
                            
                            key = response_obj.get("parameters", {}).get("key")
                            if key and key in self.memory:
                                result = f"Recalled {key}: {self.memory[key]}"
                            elif key:
                                result = f"No memory found for key: {key}"
                            else:
                                result = f"Current memory: {self.memory}"
                        elif tool_name == "text_content_multiple":
                            selectors = response_obj.get("parameters", {}).get("selectors", [])
                            results = {}
                            for selector in selectors:
                                try:
                                    text = await page.text_content(selector)
                                    results[selector] = text
                                except:
                                    results[selector] = None
                            result = results

                        elif tool_name == "get_all_links":
                            links = await page.evaluate("""
                                Array.from(document.querySelectorAll('a')).map(link => ({
                                    text: link.textContent.trim(),
                                    href: link.href,
                                    title: link.title
                                }))
                            """)
                            result = links
                        elif tool_name == "find_contact_info":
                            contact_data = await page.evaluate("""
                                () => {
                                    const text = document.body.innerText;
                                    
                                    // Better email regex
                                    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
                                    const emails = [...new Set(text.match(emailRegex) || [])];
                                    
                                    // Better phone regex
                                    const phoneRegex = /(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4})/g;
                                    const phones = [...new Set(text.match(phoneRegex) || [])];
                                    
                                    // Also check for social links (discord, github, etc.)
                                    const socialLinks = Array.from(document.querySelectorAll('a[href*="discord"], a[href*="github"], a[href*="twitter"], a[href*="linkedin"]'))
                                        .map(link => ({
                                            type: link.href.includes('discord') ? 'discord' : 
                                                link.href.includes('github') ? 'github' :
                                                link.href.includes('twitter') ? 'twitter' :
                                                'linkedin',
                                            url: link.href,
                                            text: link.textContent.trim()
                                        }));
                                    
                                    return { emails, phones, socialLinks };
                                }
                            """)
                            result = contact_data
                        elif tool_name == "extract_structured_data":
                            structured = await page.evaluate("""
                                const jsonLd = Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                                    .map(script => {
                                        try { return JSON.parse(script.textContent); }
                                        catch { return null; }
                                    }).filter(Boolean);
                                
                                const meta = Array.from(document.querySelectorAll('meta[property], meta[name]'))
                                    .reduce((acc, meta) => {
                                        const key = meta.getAttribute('property') || meta.getAttribute('name');
                                        acc[key] = meta.getAttribute('content');
                                        return acc;
                                    }, {});
                                    
                                return { jsonLd, meta };
                            """)
                            result = structured
                        elif tool_name == "search_page_text":
                            search_term = response_obj.get("parameters", {}).get("term", "")
                            case_sensitive = response_obj.get("parameters", {}).get("case_sensitive", False)
                            
                            matches = await page.evaluate(f"""
                                const term = {json.dumps(search_term)};
                                const caseSensitive = {json.dumps(case_sensitive)};
                                const text = document.body.innerText;
                                const regex = new RegExp(term, caseSensitive ? 'g' : 'gi');
                                const matches = [...text.matchAll(regex)];
                                
                                return matches.map(match => ({{
                                    text: match[0],
                                    index: match.index,
                                    context: text.substring(Math.max(0, match.index - 50), match.index + 50)
                                }}));
                            """)
                            result = matches

                        elif tool_name == "find_navigation_links":
                            nav_links = await page.evaluate("""
                                () => {
                                    const navSelectors = ['nav a', '.navbar a', '.menu a', '.navigation a', 'header a'];
                                    const links = [];
                                    
                                    navSelectors.forEach(selector => {
                                        document.querySelectorAll(selector).forEach(link => {
                                            links.push({
                                                text: link.textContent.trim(),
                                                href: link.href,
                                                selector: selector
                                            });
                                        });
                                    });
                                    
                                    return links;
                                }
                            """)
                            result = nav_links
                        elif tool_name == "get_all_forms":
                            forms = await page.evaluate("""
                                Array.from(document.forms).map((form, index) => ({
                                    id: form.id || `form-${index}`,
                                    action: form.action,
                                    method: form.method,
                                    inputs: Array.from(form.elements).map(input => ({
                                        name: input.name,
                                        type: input.type,
                                        placeholder: input.placeholder,
                                        required: input.required
                                    }))
                                }))
                            """)
                            result = forms
                        elif tool_name == "smart_fill_form":
                            form_data = response_obj.get("parameters", {}).get("data", {})
                            filled = await page.evaluate(f"""
                                const data = {json.dumps(form_data)};
                                const filled = [];
                                
                                // Smart field detection
                                if (data && Object.keys(data).length > 0) {{
                                    for (const [key, value] of Object.entries(data)) {{
                                        const selectors = [
                                            `input[name*="${{key}}"]`,
                                            `input[placeholder*="${{key}}"]`,
                                            `input[id*="${{key}}"]`,
                                            `textarea[name*="${{key}}"]`
                                        ];
                                        
                                        for (const selector of selectors) {{
                                            const input = document.querySelector(selector);
                                            if (input) {{
                                                input.value = value;
                                                filled.push({{field: key, selector, value}});
                                                break;
                                            }}
                                        }}
                                    }}
                                }}
                                
                                return filled;
                            """)
                            result = filled
                        else:
                            func = getattr(page, tool_name)
                            result = await func(**response_obj.get("parameters", {}))
                        
                       
                         # Handle massive content that overwhelms the LLM - more aggressive truncation
                        if tool_name == "content":
                            result_str = str(result)
                            original_size = len(result_str)
                            
                            # AGGRESSIVE truncation BEFORE any processing to prevent API limits
                            if original_size > 200000:  
                                import re
                                result_str = re.sub(r'<script[^>]*>.*?</script>', '', result_str, flags=re.DOTALL | re.IGNORECASE)
                                result_str = re.sub(r'<style[^>]*>.*?</style>', '', result_str, flags=re.DOTALL | re.IGNORECASE)
                                result_str = re.sub(r'\s*on\w+="[^"]*"', '', result_str, flags=re.IGNORECASE)
                                result_str = re.sub(r"\s*on\w+='[^']*'", '', result_str, flags=re.IGNORECASE)
                                result_str = re.sub(r'<!--.*?-->', '', result_str, flags=re.DOTALL)
                                result_str = re.sub(r'\s+', ' ', result_str)
                                result_str = result_str.strip()
                                
                                result = f"PAGE TOO LARGE ({original_size} chars). Use targeted selectors instead:\n\n" + \
                                        f"EXAMPLES FOR THIS TASK:\n" + \
                                        f"- text_content with selector='h1, h2, h3' → get headings/names\n" + \
                                        f"- text_content with selector='.bio, .about, .summary' → get bio/summary\n" + \
                                        f"- text_content with selector='.research, .interests' → get research info\n" + \
                                        f"- text_content with selector='main, article' → get main content\n\n" + \
                                        f"SAMPLE FROM PAGE:\n{result_str[:3000]}\n\n" + \
                                ""
                                self._log_(f"[ContentTruncated] Large page guided to use selectors", LogLevel.VERBOSE)
                            else:
                                # Process normally for smaller content
                                import re
                                result_str = re.sub(r'<script[^>]*>.*?</script>', '', result_str, flags=re.DOTALL | re.IGNORECASE)
                                result_str = re.sub(r'<style[^>]*>.*?</style>', '', result_str, flags=re.DOTALL | re.IGNORECASE)
                                result_str = re.sub(r'\s*on\w+="[^"]*"', '', result_str, flags=re.IGNORECASE)
                                result_str = re.sub(r"\s*on\w+='[^']*'", '', result_str, flags=re.IGNORECASE)
                                result_str = re.sub(r'<!--.*?-->', '', result_str, flags=re.DOTALL)
                                result_str = re.sub(r'\s+', ' ', result_str)
                                result = result_str.strip()
                        
                        elif hasattr(result, '__dict__') or str(type(result)).startswith('<'):
                            if tool_name in ['click', 'fill', 'type', 'check', 'uncheck', 'hover', 'press']:
                                result = "Action performed"
                            elif tool_name == 'goto':
                                result = f"Navigated to {response_obj.get('parameters', {}).get('url', 'URL')}"
                            elif tool_name == 'reload':
                                result = "Page reloaded"
                            elif tool_name == 'wait_for_selector':
                                result = f"Element found: {response_obj.get('parameters', {}).get('selector', 'selector')}"
                            elif tool_name == 'wait_for_timeout':
                                result = f"Waited {response_obj.get('parameters', {}).get('ms', 'N/A')}ms"
                            else:
                                result = str(result)
                        
                        try:
                            json.dumps(result)  # test if it's serializable
                        except (TypeError, ValueError):
                            result = str(result)

                            
                    except Exception as tool_error:
                        error_type = type(tool_error).__name__
                        self._log_(f"[ToolError] {tool_name} failed: {error_type} - {str(tool_error)}", LogLevel.VERBOSE)
                        
                        if "TimeoutError" in error_type:
                            error_feedback = f"TOOL FAILED: '{tool_name}' timed out. The selector doesn't exist."
                        else:
                            error_feedback = f"TOOL FAILED: '{tool_name}' error: {str(tool_error)}. Try different approach."

                        memory_reminder = ""
                        if hasattr(self, 'memory') and self.memory:
                            memory_reminder = f"\n\n🧠 CURRENT MEMORY: {json.dumps(self.memory)}"
                        
                        self.client.add_message("user", error_feedback + memory_reminder)
                        continue
                    
                    result_str = str(result)
                    display_str = result_str[:60] + f"...({len(result_str) - 60} more chars)" if len(result_str) > 60 else result_str
                    self._log_(f"[ToolResult] {tool_name} returned: {display_str}", LogLevel.VERBOSE)
                    
                    toolResponse = {"toolUsed": tool_name, "toolResponse": result}
                    
                    try:
                        toolResponse_json = json.dumps(toolResponse)
                        
                        response_size_mb = len(toolResponse_json.encode('utf-8')) / (1024 * 1024)
                        if response_size_mb > 50:
                            self._log_(f"[SizeWarning] Response too large ({response_size_mb:.1f}MB), truncating further", LogLevel.VERBOSE)
                            result_str = str(result)[:3000] + f"\n\n[EMERGENCY TRUNCATION - Response was {response_size_mb:.1f}MB]\nUse targeted selectors instead of 'content' tool!"
                            toolResponse = {"toolUsed": tool_name, "toolResponse": result_str}
                            toolResponse_json = json.dumps(toolResponse)
                            
                    except (TypeError, ValueError) as e:
                        self._log_(f"[SerializationError] Converting result to string: {e}", LogLevel.VERBOSE)
                        toolResponse = {"toolUsed": tool_name, "toolResponse": str(result)}
                        toolResponse_json = json.dumps(toolResponse)
                    
                    memory_reminder = ""
                    if hasattr(self, 'memory') and self.memory:
                        memory_reminder = f"\n\n🧠 CURRENT MEMORY: {json.dumps(self.memory)}"
                    
                    self.client.add_message("user", toolResponse_json + memory_reminder)
                    tool_call_count += 1
                    retry_count = 0
                    continue
                    
                except jsonschema.ValidationError:
                    pass

                retry_count += 1
                if retry_count >= max_retries:
                    await browser.close()
                    raise RuntimeError(f"LLM failed to follow format after {max_retries} attempts. Last response: {response}")

                self._log_(f"[FormatError] LLM ignored response format (attempt {retry_count}/{max_retries})", LogLevel.VERBOSE)
                
                task_info = json.loads(self.task_json)
                
                memory_reminder = ""
                if hasattr(self, 'memory') and self.memory:
                    memory_reminder = f"\n\n🧠 CURRENT MEMORY: {json.dumps(self.memory)}"
                
                strict_message = f"""STOP. You are NOT following the required format. 

    You provided: {list(response_obj.keys())}

    You MUST respond with EXACTLY one of these:

    1. TOOL CALL:
    {{"tool_name": "content", "parameters": {{}}, "reasoning": "explanation"}}

    2. TASK COMPLETE:
    {{"task_completed": true, "data": {task_info['response_schema']}}}

    3. TASK FAILED:
    {{"task_completed": false, "error": "reason"}}

    NO OTHER FORMAT IS ALLOWED. Your task: {task_info['task_description']}{memory_reminder}


    Respond with the EXACT format above."""
                
                self.client.add_message("user", strict_message)