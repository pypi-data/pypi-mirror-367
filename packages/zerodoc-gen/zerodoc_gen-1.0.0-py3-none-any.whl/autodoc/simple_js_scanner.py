"""Simple JavaScript/TypeScript scanner using regex patterns."""

import re
from pathlib import Path
from typing import Dict, Any, List


def scan_js_file(file_path: Path) -> Dict[str, Any]:
    """Simple scanner for JavaScript/TypeScript files using regex."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Detect language
        is_typescript = file_path.suffix in ['.ts', '.tsx']
        
        api_data = {
            "classes": [],
            "functions": [],
            "variables": [],
            "imports": [],
            "exports": []
        }
        
        # Extract imports
        import_pattern = r'import\s+(?:(?:\*\s+as\s+\w+)|(?:\{[^}]+\})|(?:\w+))?\s*(?:,\s*(?:\{[^}]+\}|\w+))?\s*from\s*[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, content):
            api_data["imports"].append({
                "statement": match.group(0),
                "module": match.group(1)
            })
        
        # Extract classes
        class_pattern = r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, content):
            class_info = {
                "name": match.group(1),
                "extends": match.group(2),
                "exported": match.group(0).startswith('export'),
                "methods": [],
                "properties": []
            }
            
            # Try to find methods in the class
            class_start = match.end()
            brace_count = 0
            class_end = class_start
            
            # Find the class body
            for i, char in enumerate(content[class_start:], class_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break
            
            if class_end > class_start:
                class_body = content[class_start:class_end]
                
                # Extract methods
                method_pattern = r'(?:async\s+)?(?:static\s+)?(\w+)\s*\([^)]*\)'
                for method_match in re.finditer(method_pattern, class_body):
                    method_name = method_match.group(1)
                    if method_name not in ['if', 'for', 'while', 'switch', 'catch']:
                        class_info["methods"].append({
                            "name": method_name,
                            "is_async": 'async' in method_match.group(0),
                            "is_static": 'static' in method_match.group(0)
                        })
            
            api_data["classes"].append(class_info)
        
        # Extract functions (not in classes)
        function_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'
        arrow_pattern = r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>'
        
        for match in re.finditer(function_pattern, content):
            # Extract a docstring/comment if it exists before the function
            start = match.start()
            lines_before = content[:start].split('\n')[-5:]  # Get last 5 lines before function
            docstring = None
            for line in lines_before:
                if '/**' in line or '//' in line:
                    docstring = line.strip().replace('/**', '').replace('*/', '').replace('//', '').strip()
                    break
            
            api_data["functions"].append({
                "name": match.group(1),
                "params": [{"name": p.strip()} for p in match.group(2).split(',') if p.strip()],
                "exported": match.group(0).startswith('export'),
                "is_async": 'async' in match.group(0),
                "docstring": docstring
            })
        
        for match in re.finditer(arrow_pattern, content):
            api_data["functions"].append({
                "name": match.group(1),
                "params": [{"name": p.strip()} for p in match.group(2).split(',') if p.strip()],
                "exported": match.group(0).startswith('export'),
                "is_async": 'async' in match.group(0),
                "is_arrow": True
            })
        
        # Extract exported constants/variables
        const_pattern = r'export\s+(?:const|let|var)\s+(\w+)(?:\s*:\s*(\w+))?\s*='
        for match in re.finditer(const_pattern, content):
            if match.group(1) not in [f["name"] for f in api_data["functions"]]:
                api_data["variables"].append({
                    "name": match.group(1),
                    "type": match.group(2) if is_typescript else None,
                    "exported": True
                })
        
        # Extract React components (common in portfolios)
        component_pattern = r'(?:export\s+)?(?:default\s+)?function\s+([A-Z]\w+)\s*\('
        for match in re.finditer(component_pattern, content):
            name = match.group(1)
            # Check if it's likely a React component
            if name[0].isupper() and name not in [c["name"] for c in api_data["classes"]]:
                api_data["functions"].append({
                    "name": name,
                    "exported": 'export' in match.group(0),
                    "is_component": True
                })
        
        return {
            "path": str(file_path),
            "module": file_path.stem,
            "language": "typescript" if is_typescript else "javascript",
            "api": api_data
        }
        
    except Exception as e:
        return {
            "path": str(file_path),
            "error": str(e)
        }