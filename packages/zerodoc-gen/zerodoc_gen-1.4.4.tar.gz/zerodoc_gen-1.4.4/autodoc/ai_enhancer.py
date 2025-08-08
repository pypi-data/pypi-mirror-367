"""AI Enhancement module - Uses OpenAI to generate meaningful documentation."""

import os
import time
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
import aiohttp
from rich.console import Console

console = Console()


class AIDocumentationEnhancer:
    """Enhances documentation using OpenAI GPT models."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI enhancer with API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY env var or pass api_key parameter.")
        
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"  # Use 3.5 for speed and cost efficiency
        self.timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    async def enhance_function_doc(self, func_data: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Enhance a single function's documentation."""
        # Build prompt for the function
        prompt = self._build_function_prompt(func_data, context)
        
        # Get enhanced documentation from OpenAI
        enhanced_doc = await self._call_openai(prompt)
        
        if enhanced_doc:
            # Parse the response and update func_data
            func_data = self._parse_enhancement(func_data, enhanced_doc)
        
        return func_data
    
    async def enhance_class_doc(self, class_data: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Enhance a class's documentation."""
        # Build prompt for the class
        prompt = self._build_class_prompt(class_data, context)
        
        # Get enhanced documentation from OpenAI
        enhanced_doc = await self._call_openai(prompt)
        
        if enhanced_doc:
            # Parse the response and update class_data
            class_data = self._parse_enhancement(class_data, enhanced_doc)
        
        return class_data
    
    def _build_function_prompt(self, func_data: Dict[str, Any], context: str) -> str:
        """Build a prompt for enhancing function documentation."""
        func_name = func_data.get("name", "unknown")
        params = func_data.get("params", [])
        returns = func_data.get("returns", "")
        current_doc = func_data.get("doc", "")
        
        param_str = ", ".join([p.get("name", "") for p in params])
        
        prompt = f"""Generate comprehensive documentation for this function.

Function: {func_name}({param_str})
Current doc: {current_doc or 'None'}
Returns: {returns or 'Unknown'}
Context: {context[:500] if context else 'General purpose function'}

Create documentation that explains:
1. What this function does (clear summary)
2. When and why to use it (real scenarios)
3. Parameter details with expected values
4. Return value and how to use it
5. A practical code example
6. Important tips or warnings

IMPORTANT: Return ONLY valid JSON, no markdown, no extra text. Use this exact structure:
{{
    "summary": "One-line explanation of what this function does",
    "description": "Detailed explanation of when and why you'd use this function, with real use cases",
    "params": [
        {{"name": "param_name", "type": "type", "description": "What this parameter is for and what values to pass"}}
    ],
    "returns": {{"type": "return_type", "description": "What gets returned and how to use it"}},
    "example": "practical_code_example_here",
    "notes": ["Important tip or common pitfall", "Another helpful note"]
}}"""
        
        return prompt
    
    def _build_class_prompt(self, class_data: Dict[str, Any], context: str) -> str:
        """Build a prompt for enhancing class documentation."""
        class_name = class_data.get("name", "unknown")
        current_doc = class_data.get("doc", "")
        methods = class_data.get("methods", [])
        
        method_names = [m.get("name", "") for m in methods[:5]]  # First 5 methods
        
        prompt = f"""Generate comprehensive documentation for this class.

Class: {class_name}
Current doc: {current_doc or 'None'}
Key methods: {', '.join(method_names)}
Context: {context[:500] if context else 'General purpose class'}

Create documentation that explains:
1. What this class does (clear purpose)
2. When to use it (real scenarios)
3. How to instantiate and use it
4. Key methods and how they work together
5. Best practices and patterns

IMPORTANT: Return ONLY valid JSON, no markdown, no extra text. Use this exact structure:
{{
    "summary": "One-line explanation of what this class does",
    "description": "Detailed explanation of the class purpose and when to use it",
    "use_cases": ["Specific use case 1", "Specific use case 2"],
    "example": "practical_code_example_showing_class_usage",
    "notes": ["Important tip or pattern", "Another helpful note"]
}}"""
        
        return prompt
    
    async def _call_openai(self, prompt: str) -> Optional[str]:
        """Make an API call to OpenAI with retry logic."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a technical documentation expert. Generate clear, helpful documentation in valid JSON format only. No markdown, no code blocks, just pure JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,  # Balanced temperature for natural but consistent documentation
            "max_tokens": 1000
        }
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data["choices"][0]["message"]["content"]
                        elif response.status == 429:  # Rate limit
                            wait_time = self.retry_delay * (2 ** attempt)
                            console.print(f"[yellow]Rate limited, waiting {wait_time}s...[/yellow]")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            error_text = await response.text()
                            console.print(f"[red]API error {response.status}: {error_text[:200]}[/red]")
                            return None
                            
            except asyncio.TimeoutError:
                console.print(f"[yellow]Timeout on attempt {attempt + 1}/{self.max_retries}[/yellow]")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                return None
                
            except Exception as e:
                console.print(f"[red]Error calling OpenAI: {e}[/red]")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                return None
        
        return None
    
    def _parse_enhancement(self, original_data: Dict[str, Any], enhanced_doc: str) -> Dict[str, Any]:
        """Parse the AI enhancement and merge with original data."""
        try:
            # Clean up the response - sometimes GPT wraps JSON in markdown code blocks
            enhanced_doc = enhanced_doc.strip()
            if enhanced_doc.startswith("```json"):
                enhanced_doc = enhanced_doc[7:]  # Remove ```json
            if enhanced_doc.startswith("```"):
                enhanced_doc = enhanced_doc[3:]  # Remove ```
            if enhanced_doc.endswith("```"):
                enhanced_doc = enhanced_doc[:-3]  # Remove trailing ```
            enhanced_doc = enhanced_doc.strip()
            
            # Try to parse as JSON
            if enhanced_doc.startswith("{"):
                enhancement = json.loads(enhanced_doc)
            else:
                # Extract JSON from the response if wrapped in text
                import re
                json_match = re.search(r'\{.*\}', enhanced_doc, re.DOTALL)
                if json_match:
                    enhancement = json.loads(json_match.group())
                else:
                    # Fallback: use the text as description
                    enhancement = {"description": enhanced_doc}
            
            # Merge enhancement with original data
            if "summary" in enhancement:
                original_data["doc"] = enhancement["summary"]
            
            if "description" in enhancement:
                original_data["detailed_description"] = enhancement["description"]
            
            if "params" in enhancement and isinstance(enhancement["params"], list):
                # Enhance parameter descriptions
                for enhanced_param in enhancement["params"]:
                    for orig_param in original_data.get("params", []):
                        if orig_param.get("name") == enhanced_param.get("name"):
                            orig_param["description"] = enhanced_param.get("description", "")
                            orig_param["type"] = enhanced_param.get("type", orig_param.get("type", ""))
            
            if "returns" in enhancement:
                original_data["returns_detail"] = enhancement["returns"]
            
            if "example" in enhancement:
                original_data["example"] = enhancement["example"]
            
            if "notes" in enhancement:
                original_data["notes"] = enhancement["notes"]
            
            if "use_cases" in enhancement:
                original_data["use_cases"] = enhancement["use_cases"]
                
        except json.JSONDecodeError as e:
            # If JSON parsing fails completely, try to extract what we can
            console.print(f"[yellow]Warning: JSON parsing failed, extracting text: {str(e)[:100]}[/yellow]")
            # Store the raw text as detailed description
            original_data["detailed_description"] = enhanced_doc
        except Exception as e:
            console.print(f"[yellow]Warning: Could not parse enhancement: {e}[/yellow]")
        
        return original_data


async def enhance_module_documentation(module_data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """Enhance all documentation in a module using AI."""
    try:
        enhancer = AIDocumentationEnhancer(api_key)
        
        # Get module context
        module_name = module_data.get("module", "")
        module_doc = module_data.get("doc", "")
        context = f"Module: {module_name}\n{module_doc}"
        
        # Enhance classes
        enhanced_classes = []
        for class_data in module_data.get("classes", []):
            console.print(f"  Enhancing class: {class_data.get('name', 'unknown')}")
            enhanced_class = await enhancer.enhance_class_doc(class_data, context)
            
            # Enhance methods within the class
            enhanced_methods = []
            for method in enhanced_class.get("methods", []):
                enhanced_method = await enhancer.enhance_function_doc(
                    method, 
                    f"{context}\nClass: {class_data.get('name', '')}"
                )
                enhanced_methods.append(enhanced_method)
            enhanced_class["methods"] = enhanced_methods
            
            enhanced_classes.append(enhanced_class)
        
        module_data["classes"] = enhanced_classes
        
        # Enhance standalone functions
        enhanced_functions = []
        for func_data in module_data.get("functions", []):
            console.print(f"  Enhancing function: {func_data.get('name', 'unknown')}")
            enhanced_func = await enhancer.enhance_function_doc(func_data, context)
            enhanced_functions.append(enhanced_func)
        
        module_data["functions"] = enhanced_functions
        
        # Add AI enhancement flag
        module_data["ai_enhanced"] = True
        
    except Exception as e:
        console.print(f"[yellow]AI enhancement failed: {e}. Using original documentation.[/yellow]")
        module_data["ai_enhanced"] = False
    
    return module_data


def enhance_documentation_sync(module_data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for enhancing documentation."""
    try:
        # Run the async function
        return asyncio.run(enhance_module_documentation(module_data, api_key))
    except Exception as e:
        console.print(f"[yellow]AI enhancement error: {e}[/yellow]")
        return module_data