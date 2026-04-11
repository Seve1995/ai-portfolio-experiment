"""
AI Portfolio Experiment V2 — API Adapters

Unified interface for interacting with different LLM providers.
Handles prompt construction, tool calling looping, and output parsing.
All models are forced to temperature=0 and parallel_tool_calls=False for fairness.
"""

import os
import json
import time
import random
import logging
from typing import Any, Optional, Dict, List, Callable

from .config import LLMProvider

logger = logging.getLogger(__name__)

def retry_with_backoff(func: Callable, max_retries: int = 5, base_delay: float = 2.0):
    """Generic 2026-style exponential backoff wrapper."""
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                err_msg = str(e).lower()
                # Categorize common 2026 rate/quota limits
                is_rate_limit = any(x in err_msg for x in ["429", "rate limit", "quota", "resource exhausted"])
                is_timeout = any(x in err_msg for x in ["timeout", "timed out", "deadline exceeded"])
                is_unavailable = any(x in err_msg for x in ["503", "unavailable", "service unavailable"])
                
                if is_rate_limit or is_timeout or is_unavailable:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Max retries reached. Final error: {e}")
                        raise e
                    
                    delay = base_delay * (2 ** (retries - 1)) + random.uniform(0, 1)
                    # For Google Free Tier, we need even more aggressive delays
                    if "google" in err_msg or "gemini" in err_msg:
                        delay = max(delay, 30.0) 
                        
                    logger.warning(f"Retry {retries}/{max_retries} due to: {e}. Sleeping {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    # Non-retryable error
                    logger.error(f"Non-retryable error: {e}")
                    raise e
        return None
    return wrapper

class UnifiedLLMClient:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.api_key = os.getenv(provider.api_key_env)
        if not self.api_key:
            logger.warning(f"Key {provider.api_key_env} not found. Agent may fail.")
            
    def generate(self, system_prompt: str, user_prompt: str, tools: List[Dict], max_tool_calls: int = 8) -> str:
        """
        Run the LLM loop until it provides a final answer.
        Returns the final JSON string from propose_trades.
        """
        if self.provider.api_type == "openai":
            return self._run_openai_loop(system_prompt, user_prompt, tools, max_tool_calls)
        elif self.provider.api_type == "anthropic":
            return self._run_anthropic_loop(system_prompt, user_prompt, tools, max_tool_calls)
        elif self.provider.api_type == "google":
            return self._run_google_loop(system_prompt, user_prompt, tools, max_tool_calls)
        elif self.provider.api_type == "mistral":
            return self._run_mistral_loop(system_prompt, user_prompt, tools, max_tool_calls)
        elif self.provider.api_type == "perplexity":
            return self._run_openai_loop(system_prompt, user_prompt, tools, max_tool_calls) # Perplexity is OAI-compatible
        else:
            raise ValueError(f"Unsupported API type: {self.provider.api_type}")

    def _get_openai_client(self):
        import openai
        return openai.OpenAI(
            api_key=self.api_key,
            base_url=self.provider.base_url
        )

    def _convert_tools_to_openai(self, tools: List[Dict]) -> List[Dict]:
        return [{"type": "function", "function": t} for t in tools]

    def _run_openai_loop(self, system_prompt: str, user_prompt: str, tools: List[Dict], max_calls: int) -> str:
        client = self._get_openai_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        formatted_tools = self._convert_tools_to_openai(tools)
        
        from .mcp_servers import execute_tool
        
        if not formatted_tools or max_calls == 0:
            @retry_with_backoff
            def _call_oai():
                return client.chat.completions.create(
                    model=self.provider.model_id,
                    messages=messages,
                    temperature=self.provider.temperature,
                    max_tokens=self.provider.max_tokens,
                )
            response = _call_oai()
            return response.choices[0].message.content or ""
            
        call_count = 0
        while call_count < max_calls:
            @retry_with_backoff
            def _call_oai_tool():
                return client.chat.completions.create(
                    model=self.provider.model_id,
                    messages=messages,
                    tools=formatted_tools,
                    temperature=self.provider.temperature,
                    max_tokens=self.provider.max_tokens,
                    parallel_tool_calls=self.provider.parallel_tool_calls
                )
            response = _call_oai_tool()
            
            message = response.choices[0].message
            messages.append(message)
            
            if not message.tool_calls:
                # Agent didn't call a tool. It either failed to use propose_trades or it just answered.
                # If we are here, it means we don't have a strict forced tool, so we return the content.
                return message.content or ""
                
            tool_call = message.tool_calls[0] # parallel_tool_calls is False
            func_name = tool_call.function.name
            
            try:
                args = json.loads(tool_call.function.arguments)
            except Exception:
                args = {}
                
            if func_name == "propose_trades":
                # The agent has finalized its decision
                return tool_call.function.arguments
                
            # Execute standard tool
            call_count += 1
            logger.info(f"{self.provider.name} called {func_name}")
            result = execute_tool(func_name, args)
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": json.dumps(result)
            })
            
        logger.warning(f"{self.provider.name} hit max tool calls ({max_calls})")
        return ""

    def _run_anthropic_loop(self, system_prompt: str, user_prompt: str, tools: List[Dict], max_calls: int) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        
        messages = [{"role": "user", "content": user_prompt}]
        
        # Anthropic tool format
        anthropic_tools = [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["parameters"]
            } for t in tools
        ]
        
        from .mcp_servers import execute_tool
        
        if not tools or max_calls == 0:
            @retry_with_backoff
            def _call_anthropic():
                return client.messages.create(
                    model=self.provider.model_id,
                    system=system_prompt,
                    messages=messages,
                    max_tokens=self.provider.max_tokens,
                    temperature=self.provider.temperature,
                )
            response = _call_anthropic()
            return "".join([b.text for b in response.content if b.type == "text"])
            
        call_count = 0
        
        while call_count < max_calls:
            @retry_with_backoff
            def _call_anthropic_tool():
                return client.messages.create(
                    model=self.provider.model_id,
                    system=system_prompt,
                    messages=messages,
                    tools=anthropic_tools,
                    max_tokens=self.provider.max_tokens,
                    temperature=self.provider.temperature,
                )
            response = _call_anthropic_tool()
            
            # Extract tool calls and text
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            text_blocks = [block.text for block in response.content if block.type == "text"]
            
            # Append assistant's turn (must include the tool_use blocks)
            messages.append({"role": "assistant", "content": response.content})
            
            if not tool_calls:
                return "\n".join(text_blocks)
                
            # Anthropic requires a 'user' message with 'tool_result' for EVERY 'tool_use' in the turn
            results_content = []
            
            for tool_call in tool_calls:
                func_name = tool_call.name
                args = tool_call.input
                
                # Special handling for trade proposal
                if func_name == "propose_trades":
                    return json.dumps(args)
                
                logger.info(f"{self.provider.name} calling {func_name} with {args}")
                result = execute_tool(func_name, args)
                call_count += 1
                
                results_content.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": json.dumps(result)
                })
                
            # Submit all results in the next turn
            messages.append({"role": "user", "content": results_content})
            
        return ""

    def _run_google_loop(self, system_prompt: str, user_prompt: str, tools: List[Dict], max_calls: int) -> str:
        from google import genai
        from google.genai import types
        from .mcp_servers import execute_tool
        
        client = genai.Client(api_key=self.api_key)
        
        # Format tools for Google
        google_tools = []
        if tools and max_calls > 0:
            google_tools = [types.Tool(function_declarations=[
                types.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=t["parameters"]
                ) for t in tools
            ])]

        contents = [{"role": "user", "parts": [{"text": user_prompt}]}]
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=self.provider.temperature,
            tools=google_tools if google_tools else None
        )
        
        call_count = 0
        while call_count < max_calls or not google_tools:
            @retry_with_backoff
            def _call_google_iter():
                return client.models.generate_content(
                    model=self.provider.model_id,
                    contents=contents,
                    config=config
                )
            
            response = _call_google_iter()
            
            # Extract text and tool calls
            text = response.text
            parts = response.candidates[0].content.parts
            
            # Add assistant turn
            contents.append({"role": "model", "parts": parts})
            
            tool_calls = [p.function_call for p in parts if p.function_call]
            
            if not tool_calls:
                return text or ""
                
            # Execute all function calls in the turn
            response_parts = []
            for fc in tool_calls:
                func_name = fc.name
                args = fc.args
                
                if func_name == "propose_trades":
                    return json.dumps(args)
                
                call_count += 1
                logger.info(f"{self.provider.name} calling {func_name}")
                result = execute_tool(func_name, args)
                
                response_parts.append(types.Part(
                    function_response=types.FunctionResponse(
                        name=func_name,
                        response={"result": result}
                    )
                ))
            
            contents.append({"role": "user", "parts": response_parts})
            
        return ""

    def _run_mistral_loop(self, system_prompt: str, user_prompt: str, tools: List[Dict], max_calls: int) -> str:
        # Mistral uses Mistral class from mistralai.client in SDK v2+
        import os
        from mistralai.client import Mistral
        
        client = Mistral(api_key=self.api_key, timeout_ms=120000)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        if not tools or max_calls == 0:
            @retry_with_backoff
            def _call_mistral():
                return client.chat.complete(
                    model=self.provider.model_id,
                    messages=messages,
                    temperature=self.provider.temperature,
                )
            
            response = _call_mistral()
            return response.choices[0].message.content or ""
            
        call_count = 0
        
        while call_count < max_calls:
            formatted_tools = self._convert_tools_to_openai(tools)
            @retry_with_backoff
            def _call_mistral_tool():
                return client.chat.complete(
                    model=self.provider.model_id,
                    messages=messages,
                    tools=formatted_tools,
                    temperature=self.provider.temperature,
                )
            response = _call_mistral_tool()
            
            message = response.choices[0].message
            messages.append(message)
            
            if not getattr(message, "tool_calls", None):
                return message.content or ""
                
            from .mcp_servers import execute_tool
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except:
                    args = {}
                    
                if func_name == "propose_trades":
                    return tool_call.function.arguments
                    
                call_count += 1
                logger.info(f"{self.provider.name} calling {func_name}")
                result = execute_tool(func_name, args)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(result)
                })
            
        return ""

