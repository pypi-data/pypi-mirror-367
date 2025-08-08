"""Generator module - Converts API data to Markdown documentation."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import textwrap


def format_docstring(docstring: Optional[str], indent: int = 0) -> str:
    """Format a docstring for markdown output."""
    if not docstring:
        return "*No description available*"
    
    # Clean up the docstring
    lines = docstring.strip().split('\n')
    cleaned = []
    
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)
        elif cleaned and cleaned[-1]:  # Add blank line only between paragraphs
            cleaned.append('')
    
    result = '\n'.join(cleaned)
    
    if indent > 0:
        result = textwrap.indent(result, ' ' * indent)
    
    return result


def generate_function_doc(func: Dict[str, Any]) -> str:
    """Generate markdown documentation for a function."""
    lines = []
    
    # Function signature
    args = []
    params = func.get("params") or func.get("args", [])
    for arg in params:
        arg_str = arg["name"]
        if arg.get("type"):
            arg_str += f": {arg['type']}"
        if arg.get("default"):
            arg_str += f" = {arg['default']}"
        args.append(arg_str)
    
    signature = f"{func['name']}({', '.join(args)})"
    if func.get("returns"):
        signature += f" -> {func['returns']}"
    elif func.get("returns_detail", {}).get("type"):
        signature += f" -> {func['returns_detail']['type']}"
    
    # Add async keyword if needed
    if func.get("is_async"):
        signature = f"async {signature}"
    
    lines.append(f"### `{signature}`")
    lines.append("")
    
    # Add decorators
    decorators = func.get("decorators", [])
    if decorators:
        lines.append("**Decorators:** " + ", ".join(decorators))
        lines.append("")
    
    # Add docstring or AI-enhanced description
    if func.get("detailed_description"):
        lines.append(func["detailed_description"])
    else:
        lines.append(format_docstring(func.get("docstring")))
    lines.append("")
    
    # Add parameter details if available
    params = func.get("params") or func.get("args", [])
    if params:
        lines.append("**Parameters:**")
        lines.append("")
        for arg in params:
            param_line = f"- `{arg['name']}`"
            if arg.get("type"):
                param_line += f" ({arg['type']})"
            if arg.get("description"):
                param_line += f": {arg['description']}"
            elif arg.get("default"):
                param_line += f" - default: `{arg['default']}`"
            lines.append(param_line)
        lines.append("")
    
    # Add return type
    if func.get("returns_detail"):
        ret = func["returns_detail"]
        ret_line = "**Returns:** "
        if isinstance(ret, dict):
            ret_line += f"`{ret.get('type', 'Any')}`"
            if ret.get("description"):
                ret_line += f" - {ret['description']}"
        else:
            ret_line += str(ret)
        lines.append(ret_line)
        lines.append("")
    elif func.get("returns"):
        lines.append(f"**Returns:** `{func['returns']}`")
        lines.append("")
    
    # Add example if available (from AI enhancement)
    if func.get("example"):
        lines.append("**Example:**")
        lines.append("")
        lines.append("```python")
        lines.append(func["example"])
        lines.append("```")
        lines.append("")
    
    # Add notes if available (from AI enhancement)
    if func.get("notes"):
        lines.append("**Notes:**")
        for note in func["notes"]:
            lines.append(f"- {note}")
        lines.append("")
    
    return '\n'.join(lines)


def generate_class_doc(cls: Dict[str, Any]) -> str:
    """Generate markdown documentation for a class."""
    lines = []
    
    # Class header
    header = f"## Class: `{cls['name']}`"
    if cls.get("bases"):
        header += f" (inherits from: {', '.join(cls['bases'])})"
    lines.append(header)
    lines.append("")
    
    # Add decorators
    decorators = cls.get("decorators", [])
    if decorators:
        lines.append("**Decorators:** " + ", ".join(decorators))
        lines.append("")
    
    # Add docstring or AI-enhanced description
    if cls.get("detailed_description"):
        lines.append(cls["detailed_description"])
    else:
        lines.append(format_docstring(cls.get("docstring")))
    lines.append("")
    
    # Add use cases if available (from AI enhancement)
    if cls.get("use_cases"):
        lines.append("**Common Use Cases:**")
        for use_case in cls["use_cases"]:
            lines.append(f"- {use_case}")
        lines.append("")
    
    # Add example if available (from AI enhancement)
    if cls.get("example"):
        lines.append("**Example:**")
        lines.append("")
        lines.append("```python")
        lines.append(cls["example"])
        lines.append("```")
        lines.append("")
    
    # Add notes if available (from AI enhancement)
    if cls.get("notes"):
        lines.append("**Design Notes:**")
        for note in cls["notes"]:
            lines.append(f"- {note}")
        lines.append("")
    
    # Add attributes
    attributes = cls.get("attributes", [])
    if attributes:
        lines.append("### Attributes")
        lines.append("")
        for attr in attributes:
            attr_line = f"- `{attr['name']}`"
            if attr.get("type"):
                attr_line += f": {attr['type']}"
            if attr.get("value"):
                attr_line += f" = {attr['value']}"
            lines.append(attr_line)
        lines.append("")
    
    # Add methods
    methods = cls.get("methods", [])
    if methods:
        lines.append("### Methods")
        lines.append("")
        
        # Group methods
        init_methods = [m for m in methods if m["name"] == "__init__"]
        special_methods = [m for m in methods if m["name"].startswith("__") and m["name"] != "__init__"]
        regular_methods = [m for m in methods if not m["name"].startswith("__")]
        
        # Document __init__ first
        for method in init_methods:
            lines.append(generate_function_doc(method))
        
        # Then regular methods
        for method in sorted(regular_methods, key=lambda x: x["name"]):
            lines.append(generate_function_doc(method))
        
        # Finally special methods
        for method in sorted(special_methods, key=lambda x: x["name"]):
            lines.append(generate_function_doc(method))
    
    return '\n'.join(lines)


def generate_module_doc(module: Dict[str, Any]) -> str:
    """Generate markdown documentation for a module."""
    lines = []
    
    # Module header
    module_name = module.get("module", "Unknown Module")
    language = module.get("language", "unknown")
    lines.append(f"# Module: `{module_name}`")
    lines.append("")
    
    # Check if AI enhanced
    if module.get("ai_enhanced"):
        lines.append("*✨ Enhanced with AI-generated documentation*")
        lines.append("")
    
    # File path and language
    lines.append(f"**File:** `{module['path']}`")
    lines.append(f"**Language:** {language.title()}")
    lines.append("")
    
    # Module docstring
    if module.get("docstring"):
        lines.append("## Description")
        lines.append("")
        lines.append(format_docstring(module["docstring"]))
        lines.append("")
    
    api = module.get("api", {})
    
    # Handle different languages
    language = module.get("language", "python")
    
    if language == "python":
        lines.extend(generate_python_doc(api))
    elif language in ["javascript", "typescript"]:
        from .generator_languages import generate_javascript_doc
        lines.extend(generate_javascript_doc(api, language))
    elif language == "go":
        from .generator_languages import generate_go_doc
        lines.extend(generate_go_doc(api))
    elif language == "rust":
        from .generator_languages import generate_rust_doc
        lines.extend(generate_rust_doc(api))
    else:
        # Fallback to basic structure
        lines.extend(generate_python_doc(api))
    
    return '\n'.join(lines)


def generate_python_doc(api: Dict[str, Any]) -> List[str]:
    """Generate Python-specific documentation."""
    lines = []
    
    # Document imports
    imports = api.get("imports", [])
    if imports:
        lines.append("## Imports")
        lines.append("")
        for imp in imports:
            if imp["type"] == "import":
                imp_line = f"- `import {imp['module']}`"
                if imp.get("alias"):
                    imp_line += f" as `{imp['alias']}`"
            else:
                imp_line = f"- `from {imp['module']} import {imp['name']}`"
                if imp.get("alias"):
                    imp_line += f" as `{imp['alias']}`"
            lines.append(imp_line)
        lines.append("")
    
    # Document variables
    variables = api.get("variables", [])
    if variables:
        lines.append("## Module Variables")
        lines.append("")
        for var in variables:
            var_line = f"- `{var['name']}`"
            if var.get("type"):
                var_line += f": {var['type']}"
            if var.get("value"):
                var_line += f" = {var['value']}"
            lines.append(var_line)
        lines.append("")
    
    # Document functions
    functions = api.get("functions", [])
    if functions:
        lines.append("## Functions")
        lines.append("")
        for func in sorted(functions, key=lambda x: x["name"]):
            lines.append(generate_function_doc(func))
    
    # Document classes
    classes = api.get("classes", [])
    if classes:
        lines.append("## Classes")
        lines.append("")
        for cls in sorted(classes, key=lambda x: x["name"]):
            lines.append(generate_class_doc(cls))
            lines.append("---")
            lines.append("")
    
    return lines


def generate_index_page(modules: List[Dict[str, Any]], project_name: str) -> str:
    """Generate an enhanced index page for all modules."""
    lines = []
    
    # Calculate statistics
    total_classes = sum(len(m.get("api", {}).get("classes", [])) for m in modules)
    total_functions = sum(len(m.get("api", {}).get("functions", [])) for m in modules)
    total_lines = 0
    languages = {}
    
    for module in modules:
        # Count lines (rough estimate)
        path = Path(module["path"])
        if path.exists():
            try:
                with open(path, 'r') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        
        # Count languages
        lang = module.get("language", "unknown")
        languages[lang] = languages.get(lang, 0) + 1
    
    # Generate header and stats
    lines.append(f"# {project_name} Documentation")
    lines.append("")
    lines.append(f"Welcome to the comprehensive API documentation for **{project_name}**.")
    lines.append("")
    lines.append("## 📊 Project Statistics")
    lines.append("")
    lines.append('<div class="stats-grid">')
    lines.append(f'<div class="stat-card">')
    lines.append(f'<div class="stat-value">{len(modules)}</div>')
    lines.append(f'<div class="stat-label">Total Modules</div>')
    lines.append(f'</div>')
    lines.append(f'<div class="stat-card">')
    lines.append(f'<div class="stat-value">{total_classes}</div>')
    lines.append(f'<div class="stat-label">Classes</div>')
    lines.append(f'</div>')
    lines.append(f'<div class="stat-card">')
    lines.append(f'<div class="stat-value">{total_functions}</div>')
    lines.append(f'<div class="stat-label">Functions</div>')
    lines.append(f'</div>')
    lines.append(f'<div class="stat-card">')
    lines.append(f'<div class="stat-value">{total_lines:,}</div>')
    lines.append(f'<div class="stat-label">Lines of Code</div>')
    lines.append(f'</div>')
    lines.append('</div>')
    lines.append("")
    
    # Language breakdown
    if languages:
        lines.append("## 💻 Language Distribution")
        lines.append("")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            emoji = "🐍" if lang == "python" else "📜" if lang in ["javascript", "typescript"] else "📄"
            lines.append(f"- {emoji} **{lang.title()}**: {count} files")
        lines.append("")
    
    # Documentation structure
    lines.append("## 🗂️ Documentation Structure")
    lines.append("")
    
    # Group modules by package/directory
    packages = {}
    for module in modules:
        path = Path(module["path"])
        # Get package path relative to project root
        parts = path.parts
        if len(parts) > 1:
            package = parts[-2]
        else:
            package = "root"
        
        if package not in packages:
            packages[package] = []
        packages[package].append(module)
    
    # Generate organized TOC
    for package, mods in sorted(packages.items()):
        if package != "root":
            lines.append(f"### 📁 {package}/")
        else:
            lines.append("### 📁 Root")
        lines.append("")
        
        for module in sorted(mods, key=lambda x: x["module"]):
            module_file = f"{module['module']}.md"
            
            # Determine icon based on module type
            icon = "📄"
            module_lower = module['module'].lower()
            if any(x in module_lower for x in ['component', 'ui']):
                icon = "🧩"
            elif any(x in module_lower for x in ['route', 'api']):
                icon = "🔌"
            elif any(x in module_lower for x in ['util', 'helper', 'lib']):
                icon = "🔧"
            elif any(x in module_lower for x in ['hook', 'use']):
                icon = "🪝"
            elif any(x in module_lower for x in ['test', 'spec']):
                icon = "🧪"
            
            # Fix: Use .html extension for links
            html_file = module_file.replace('.md', '.html')
            lines.append(f"- {icon} [{module['module']}](./{html_file})")
            
            # Add brief description if available
            if module.get("docstring"):
                first_line = module["docstring"].split('\n')[0]
                if len(first_line) > 80:
                    first_line = first_line[:77] + "..."
                lines.append(f"  - *{first_line}*")
        lines.append("")
    
    # Add quick start section
    lines.append("## 🚀 Quick Start")
    lines.append("")
    lines.append("Navigate through the documentation using the sidebar or search for specific modules, functions, or classes.")
    lines.append("")
    lines.append("### Key Features")
    lines.append("")
    lines.append("- 🔍 **Searchable**: Use the search box to quickly find what you need")
    lines.append("- 📱 **Responsive**: Works great on desktop and mobile devices")
    lines.append("- 🌙 **Dark Mode**: Automatically adapts to your system preferences")
    lines.append("- 📊 **Statistics**: Get insights into your codebase structure")
    lines.append("")
    
    return '\n'.join(lines)


def build_markdown(project_path: Path, output_dir: Path, verbose: bool = False, ai_enhance: bool = False) -> Dict[str, Any]:
    """Build markdown documentation from scanned API data."""
    project_path = Path(project_path).resolve()
    output_dir = Path(output_dir).resolve()
    
    scan_output = project_path / "build" / "api.json"
    
    # Only scan if api.json doesn't exist
    if not scan_output.exists():
        from .scanner import scan_codebase
        scan_output.parent.mkdir(parents=True, exist_ok=True)
        scan_result = scan_codebase(project_path, scan_output, verbose, False)
    
    # Load the scanned data
    with open(scan_output, 'r') as f:
        data = json.load(f)
    
    # Apply AI enhancement to the loaded data if requested
    if ai_enhance:
        import os
        import aiohttp
        import asyncio
        import json as json_lib
        
        # Check if we have an API key
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("🤖 Enhancing documentation with AI...")
            print(f"✓ Using OpenAI for AI enhancement")
            
            async def enhance_function(func):
                """Enhance a single function with AI."""
                try:
                    name = func.get("name", "unknown")
                    params = func.get("params", func.get("args", []))
                    param_str = ", ".join([p.get("name", "") for p in params])
                    
                    prompt = f"""Generate a concise documentation for this function:
Function: {name}({param_str})
Current description: {func.get("docstring", "None")}

Return a JSON object with:
- description: 1-2 sentence explanation of what this function does
- params: array of parameter descriptions
- returns: what the function returns
- example: short usage example (optional)

Be concise and practical."""

                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are a documentation expert. Be concise and practical."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 300
                    }
                    
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(
                            "https://api.openai.com/v1/chat/completions",
                            headers=headers,
                            json=payload
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                content = data["choices"][0]["message"]["content"]
                                
                                # Try to parse JSON from response
                                try:
                                    # Clean up markdown if present
                                    if "```json" in content:
                                        content = content.split("```json")[1].split("```")[0]
                                    elif "```" in content:
                                        content = content.split("```")[1].split("```")[0]
                                    
                                    ai_data = json_lib.loads(content.strip())
                                    
                                    # Merge AI data into function
                                    if ai_data.get("description"):
                                        func["detailed_description"] = ai_data["description"]
                                        func["doc"] = ai_data["description"][:100]  # Short version
                                    
                                    if ai_data.get("params"):
                                        for ai_param in ai_data["params"]:
                                            for orig_param in func.get("params", func.get("args", [])):
                                                if orig_param.get("name") == ai_param.get("name"):
                                                    orig_param["description"] = ai_param.get("description", "")
                                    
                                    if ai_data.get("example"):
                                        func["example"] = ai_data["example"]
                                    
                                    func["ai_enhanced"] = True
                                except:
                                    # If JSON parsing fails, use as plain description
                                    func["detailed_description"] = content
                                    func["ai_enhanced"] = True
                except Exception as e:
                    print(f"    ⚠️ Failed to enhance {func.get('name', 'unknown')}: {str(e)[:50]}")
                
                return func
            
            async def process_module(module):
                """Process a single module with AI enhancement."""
                if "error" in module:
                    return module
                
                api = module.get("api", {})
                functions = api.get("functions", [])
                
                # Process only first 5 functions to avoid timeout
                if functions:
                    tasks = [enhance_function(func) for func in functions[:5]]
                    enhanced = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for i, result in enumerate(enhanced):
                        if not isinstance(result, Exception):
                            functions[i] = result
                    
                    module["ai_enhanced"] = True
                
                return module
            
            # Process all modules
            async def enhance_all():
                modules = data.get("modules", [])
                print(f"  Processing {len(modules)} modules...")
                
                enhanced_modules = []
                for i, module in enumerate(modules):
                    module_name = module.get("module", "unknown")
                    print(f"  [{i+1}/{len(modules)}] Enhancing {module_name}...")
                    enhanced_module = await process_module(module)
                    enhanced_modules.append(enhanced_module)
                
                return enhanced_modules
            
            # Run the enhancement
            data["modules"] = asyncio.run(enhance_all())
            print("✓ AI enhancement complete")
            
            # Save the enhanced data back to api.json
            with open(scan_output, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            print("⚠️ No OpenAI API key found, skipping AI enhancement")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate documentation for each module
    modules = data.get("modules", [])
    doc_files = []
    
    for module in modules:
        if "error" not in module:
            doc_content = generate_module_doc(module)
            
            # Save to file
            doc_file = output_dir / f"{module['module']}.md"
            doc_file.write_text(doc_content)
            doc_files.append(doc_file)
            
            if verbose:
                print(f"Generated: {doc_file}")
    
    # Generate index page
    if modules:
        index_content = generate_index_page(modules, data.get("project", "Project"))
        index_file = output_dir / "index.md"
        index_file.write_text(index_content)
        doc_files.append(index_file)
    
    return {
        "files": len(doc_files),
        "modules": len(modules)
    }


def generate_readme(project_path: Path, template_name: str = "default", force: bool = False) -> Dict[str, Any]:
    """Generate README.md from template."""
    project_path = Path(project_path).resolve()
    readme_path = project_path / "README.md"
    
    # Check if README exists and force is False
    if readme_path.exists() and not force:
        return {
            "updated": False,
            "path": str(readme_path),
            "message": "README.md already exists. Use --force to overwrite."
        }
    
    # Get project info
    project_name = project_path.name
    
    # Check for package.json or pyproject.toml for more info
    description = "A Python project"
    version = "0.1.0"
    
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        with open(pyproject, 'rb') as f:
            data = tomllib.load(f)
            project_info = data.get("project", {})
            project_name = project_info.get("name", project_name)
            description = project_info.get("description", description)
            version = project_info.get("version", version)
    
    # Load template
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape()
    )
    
    try:
        template = env.get_template("README.md.j2")
    except:
        # Use a default template if file doesn't exist
        template_content = """# {{ project_name }}

{{ description }}

## Installation

```bash
pip install {{ project_name }}
```

## Usage

```python
import {{ module_name }}

# Your code here
```

## Documentation

Full documentation is available in the `docs/` directory.

To generate documentation:

```bash
autodoc docs .
autodoc export --dest site
```

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Generate docs
autodoc docs .
```

## License

MIT License - see LICENSE file for details.

---

*Generated with [AutoDoc](https://github.com/autodoc-team/autodoc-typer)*
"""
        template = env.from_string(template_content)
    
    # Render template
    module_name = project_name.replace("-", "_")
    readme_content = template.render(
        project_name=project_name,
        module_name=module_name,
        description=description,
        version=version
    )
    
    # Write README
    readme_path.write_text(readme_content)
    
    return {
        "updated": True,
        "path": str(readme_path)
    }