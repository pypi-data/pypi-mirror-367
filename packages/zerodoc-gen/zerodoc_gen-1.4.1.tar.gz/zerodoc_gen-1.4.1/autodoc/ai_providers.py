"""Multi-provider AI system with parallel processing."""

import os
import asyncio
import aiohttp
import random
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

console = Console()


# Cocky loading messages
LOADING_MESSAGES = [
    "🚀 Making your docs actually readable...",
    "⚡ Injecting intelligence into your code...",
    "🧠 Teaching your functions to explain themselves...",
    "✨ Sprinkling AI magic dust...",
    "🔥 Cooking up some fire documentation...",
    "🎯 Turning code into English...",
    "💎 Polishing your rough docs into diamonds...",
    "🎨 Painting a masterpiece of documentation...",
    "🏎️ Turbochaging your docs with AI...",
    "🌟 Making your code famous...",
    "🎭 Giving your functions a personality...",
    "🍳 Cooking documentation with secret sauce...",
    "🎪 Performing documentation magic tricks...",
    "🦾 Upgrading docs to superhuman level...",
    "🌈 Adding colors to your boring docs...",
]


class AIProvider(ABC):
    """Base class for AI providers."""
    
    @abstractmethod
    async def enhance(self, prompt: str) -> Optional[str]:
        """Enhance documentation with AI."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def enhance(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You're a documentation expert. Be concise, practical, and helpful."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 600
        }
        
        timeout = aiohttp.ClientTimeout(total=15)  # Faster timeout
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
        except:
            return None
        
        return None


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")  # Fastest model
        
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def enhance(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
            
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 600,
            "temperature": 0.3
        }
        
        timeout = aiohttp.ClientTimeout(total=15)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["content"][0]["text"]
        except:
            return None
        
        return None


class GroqProvider(AIProvider):
    """Groq ultra-fast inference provider."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")  # Fast and good
        
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def enhance(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You're a documentation expert. Be concise and practical."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 600
        }
        
        timeout = aiohttp.ClientTimeout(total=10)  # Groq is super fast
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
        except:
            return None
        
        return None


class OllamaProvider(AIProvider):
    """Local Ollama provider for privacy."""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama2")
        
    def is_available(self) -> bool:
        # Check if Ollama is running
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=1)
            return response.status_code == 200
        except:
            return False
    
    async def enhance(self, prompt: str) -> Optional[str]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 600
            }
        }
        
        timeout = aiohttp.ClientTimeout(total=20)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["response"]
        except:
            return None
        
        return None


class ParallelAIEnhancer:
    """Parallel AI enhancement with multiple providers and batching."""
    
    def __init__(self):
        self.providers = self._init_providers()
        self.active_provider = self._select_provider()
        
    def _init_providers(self) -> List[AIProvider]:
        """Initialize all available providers."""
        providers = []
        
        # Check each provider in order of preference
        if os.getenv("GROQ_API_KEY"):
            providers.append(GroqProvider())  # Fastest
        if os.getenv("ANTHROPIC_API_KEY"):
            providers.append(AnthropicProvider())  # Good quality
        if os.getenv("OPENAI_API_KEY"):
            providers.append(OpenAIProvider())  # Most common
        if OllamaProvider().is_available():
            providers.append(OllamaProvider())  # Local/private
            
        return providers
    
    def _select_provider(self) -> Optional[AIProvider]:
        """Select the best available provider."""
        for provider in self.providers:
            if provider.is_available():
                provider_name = provider.__class__.__name__.replace("Provider", "")
                return provider
        return None
    
    def get_provider_name(self) -> str:
        """Get the name of active provider."""
        if self.active_provider:
            return self.active_provider.__class__.__name__.replace("Provider", "")
        return "None"
    
    async def enhance_batch(self, items: List[Dict[str, Any]], item_type: str = "function") -> List[Dict[str, Any]]:
        """Enhance multiple items in parallel."""
        if not self.active_provider:
            return items
        
        # Process in parallel with limited concurrency
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def bounded_enhance(item_data, prompt):
            async with semaphore:
                return await self._enhance_single(item_data, prompt)
        
        bounded_tasks = [
            bounded_enhance(items[i], self._build_prompt(items[i], item_type))
            for i in range(len(items))
        ]
        
        # Wait for all tasks
        results = await asyncio.gather(*bounded_tasks, return_exceptions=True)
        
        # Merge results
        enhanced_items = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                enhanced_items.append(items[i])  # Keep original if failed
            else:
                enhanced_items.append(result)
        
        return enhanced_items
    
    def _build_prompt(self, item: Dict[str, Any], item_type: str) -> str:
        """Build a concise prompt for the item."""
        if item_type == "function":
            name = item.get("name", "unknown")
            params = item.get("params", item.get("args", []))
            param_str = ", ".join([p.get("name", "") for p in params])
            
            return f"""Function: {name}({param_str})
Purpose: Explain what this does in 1-2 sentences. Be specific about its real use.
Returns: {item.get("returns", "unknown")}

Generate a JSON response:
{{
    "summary": "What this function does in plain English",
    "params": [{{"name": "x", "description": "what to pass"}}],
    "returns": "what you get back",
    "example": "practical usage"
}}"""
        
        elif item_type == "class":
            name = item.get("name", "unknown")
            return f"""Class: {name}
Purpose: Explain this class's role in 1-2 sentences.

Generate a JSON response:
{{
    "summary": "What this class is for",
    "use_case": "When you'd use this",
    "example": "How to use it"
}}"""
        
        return ""
    
    async def _enhance_single(self, item: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Enhance a single item."""
        if not self.active_provider:
            return item
        
        response = await self.active_provider.enhance(prompt)
        
        if response:
            try:
                # Clean up response if wrapped in markdown
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]  # Remove ```
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing ```
                cleaned_response = cleaned_response.strip()
                
                # Parse JSON response
                if "{" in cleaned_response:
                    json_str = cleaned_response[cleaned_response.find("{"):cleaned_response.rfind("}")+1]
                    enhancement = json.loads(json_str)
                    
                    # Merge with original
                    if "summary" in enhancement:
                        item["doc"] = enhancement["summary"]
                        item["ai_enhanced"] = True
                    
                    if "description" in enhancement:
                        item["detailed_description"] = enhancement["description"]
                    
                    if "params" in enhancement:
                        for enhanced_param in enhancement["params"]:
                            for orig_param in item.get("params", item.get("args", [])):
                                if orig_param.get("name") == enhanced_param.get("name"):
                                    orig_param["description"] = enhanced_param.get("description", "")
                    
                    if "returns" in enhancement:
                        item["returns_detail"] = enhancement["returns"]
                    
                    if "example" in enhancement:
                        item["example"] = enhancement["example"]
                    
                    if "notes" in enhancement:
                        item["notes"] = enhancement["notes"]
                    
                    if "use_cases" in enhancement:
                        item["use_cases"] = enhancement["use_cases"]
            except json.JSONDecodeError:
                # If parsing fails, store the raw response as detailed_description
                # This happens when AI returns markdown-wrapped JSON that we couldn't parse
                item["detailed_description"] = response
            except Exception:
                pass
        
        return item


async def enhance_module_parallel(module_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance module documentation using parallel processing."""
    enhancer = ParallelAIEnhancer()
    
    if not enhancer.active_provider:
        return module_data
    
    # Show cocky loading message
    loading_msg = random.choice(LOADING_MESSAGES)
    
    # Process functions and classes in parallel
    functions = module_data.get("functions", [])
    classes = module_data.get("classes", [])
    
    # Enhance in parallel
    if functions:
        module_data["functions"] = await enhancer.enhance_batch(functions, "function")
    
    if classes:
        module_data["classes"] = await enhancer.enhance_batch(classes, "class")
        
        # Enhance methods within classes (in parallel per class)
        for cls in module_data["classes"]:
            methods = cls.get("methods", [])
            if methods:
                cls["methods"] = await enhancer.enhance_batch(methods, "function")
    
    module_data["ai_enhanced"] = True
    module_data["ai_provider"] = enhancer.get_provider_name()
    
    return module_data


def enhance_module_parallel_sync(module_data: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for parallel enhancement."""
    try:
        return asyncio.run(enhance_module_parallel(module_data))
    except Exception:
        return module_data