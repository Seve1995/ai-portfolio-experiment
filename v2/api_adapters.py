"""
AI Portfolio Experiment V2 — API Adapters

Unified interface for interacting with different LLM providers.
Handles prompt construction, tool calling looping, and output parsing.
All models are forced to temperature=0 and parallel_tool_calls=False for fairness.
"""

import os
import json
import logging
from typing import Any, Optional, Dict, List

from .config import LLMProvider

logger = logging.getLogger(__name__)

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
        
        call_count = 0
        while call_count < max_calls:
            response = client.chat.completions.create(
                model=self.provider.model_id,
                messages=messages,
                tools=formatted_tools,
                temperature=self.provider.temperature,
                max_tokens=self.provider.max_tokens,
                parallel_tool_calls=self.provider.parallel_tool_calls
            )
            
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
        call_count = 0
        
        while call_count < max_calls:
            response = client.messages.create(
                model=self.provider.model_id,
                system=system_prompt,
                messages=messages,
                tools=anthropic_tools,
                max_tokens=self.provider.max_tokens,
                temperature=self.provider.temperature,
            )
            
            # Extract tool calls
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            text_blocks = [block.text for block in response.content if block.type == "text"]
            
            # Save assistant message
            messages.append({"role": "assistant", "content": response.content})
            
            if not tool_calls:
                return "\n".join(text_blocks)
                
            # Process first tool call (parallel execution is off practically)
            tool_call = tool_calls[0]
            func_name = tool_call.name
            args = tool_call.input
            
            if func_name == "propose_trades":
                return json.dumps(args)
                
            call_count += 1
            logger.info(f"{self.provider.name} called {func_name}")
            result = execute_tool(func_name, args)
            
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(result)
                    }
                ]
            })
            
        return ""

    def _run_google_loop(self, system_prompt: str, user_prompt: str, tools: List[Dict], max_calls: int) -> str:
        # For simplicity and standardization, we can use the official litellm routing or native python SDK.
        # Since v2 focuses on stability, and gemini SDK has tools, we implement basic wrapper.
        pass # Will implement via standard API later, or suggest liteLLM

    def _run_mistral_loop(self, system_prompt: str, user_prompt: str, tools: List[Dict], max_calls: int) -> str:
        # Mistral uses OpenAI compatible SDK generally
        import os
        from mistralai.client import MistralClient
        from mistralai.models.chat_completion import ChatMessage
        
        client = MistralClient(api_key=self.api_key)
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ]
        formatted_tools = self._convert_tools_to_openai(tools)
        
        from .mcp_servers import execute_tool
        call_count = 0
        
        while call_count < max_calls:
            response = client.chat(
                model=self.provider.model_id,
                messages=messages,
                tools=formatted_tools,
                temperature=self.provider.temperature,
            )
            
            message = response.choices[0].message
            messages.append(message)
            
            if not message.tool_calls:
                return message.content or ""
                
            tool_call = message.tool_calls[0]
            func_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except:
                args = {}
                
            if func_name == "propose_trades":
                return tool_call.function.arguments
                
            call_count += 1
            result = execute_tool(func_name, args)
            
            messages.append(ChatMessage(
                role="tool",
                name=func_name,
                content=json.dumps(result)
            ))
            
        return ""
