"""Scanner module - Parses Python source files and extracts API information."""

import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import textwrap
import os


class APIExtractor(ast.NodeVisitor):
    """AST visitor to extract API information from Python files."""
    
    def __init__(self):
        self.api_data = {
            "classes": [],
            "functions": [],
            "variables": [],
            "imports": []
        }
        self.current_class = None
    
    def visit_ClassDef(self, node):
        """Extract class definitions."""
        class_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "methods": [],
            "attributes": [],
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "bases": [self._get_name(base) for base in node.bases],
            "lineno": node.lineno
        }
        
        # Temporarily store current class for method extraction
        old_class = self.current_class
        self.current_class = class_info
        
        # Visit child nodes
        self.generic_visit(node)
        
        self.api_data["classes"].append(class_info)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Extract function definitions."""
        func_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "args": self._extract_arguments(node.args),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "returns": self._get_annotation(node.returns),
            "lineno": node.lineno,
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }
        
        if self.current_class:
            # This is a method
            func_info["is_method"] = True
            func_info["is_classmethod"] = "@classmethod" in func_info["decorators"]
            func_info["is_staticmethod"] = "@staticmethod" in func_info["decorators"]
            self.current_class["methods"].append(func_info)
        else:
            # This is a top-level function
            self.api_data["functions"].append(func_info)
        
        # Don't visit child nodes to avoid nested functions
    
    visit_AsyncFunctionDef = visit_FunctionDef
    
    def visit_AnnAssign(self, node):
        """Extract annotated variable assignments."""
        if isinstance(node.target, ast.Name):
            var_info = {
                "name": node.target.id,
                "type": self._get_annotation(node.annotation),
                "value": self._get_value(node.value) if node.value else None,
                "lineno": node.lineno
            }
            
            if self.current_class:
                self.current_class["attributes"].append(var_info)
            else:
                self.api_data["variables"].append(var_info)
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Extract import statements."""
        for alias in node.names:
            self.api_data["imports"].append({
                "module": alias.name,
                "alias": alias.asname,
                "type": "import"
            })
    
    def visit_ImportFrom(self, node):
        """Extract from-import statements."""
        module = node.module or ""
        for alias in node.names:
            self.api_data["imports"].append({
                "module": module,
                "name": alias.name,
                "alias": alias.asname,
                "type": "from"
            })
    
    def _extract_arguments(self, args):
        """Extract function arguments."""
        arg_list = []
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            arg_info = {
                "name": arg.arg,
                "type": self._get_annotation(arg.annotation),
                "default": None
            }
            
            # Check for defaults
            defaults_offset = len(args.args) - len(args.defaults)
            if i >= defaults_offset:
                default_idx = i - defaults_offset
                arg_info["default"] = self._get_value(args.defaults[default_idx])
            
            arg_list.append(arg_info)
        
        # *args
        if args.vararg:
            arg_list.append({
                "name": f"*{args.vararg.arg}",
                "type": self._get_annotation(args.vararg.annotation),
                "default": None
            })
        
        # **kwargs
        if args.kwarg:
            arg_list.append({
                "name": f"**{args.kwarg.arg}",
                "type": self._get_annotation(args.kwarg.annotation),
                "default": None
            })
        
        return arg_list
    
    def _get_decorator_name(self, decorator):
        """Get decorator name as string."""
        if isinstance(decorator, ast.Name):
            return f"@{decorator.id}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return f"@{decorator.func.id}"
            elif isinstance(decorator.func, ast.Attribute):
                return f"@{self._get_name(decorator.func)}"
        elif isinstance(decorator, ast.Attribute):
            return f"@{self._get_name(decorator)}"
        return "@unknown"
    
    def _get_name(self, node):
        """Get name from various node types."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, str):
            return node
        return "unknown"
    
    def _get_annotation(self, node):
        """Get type annotation as string."""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[{self._get_annotation(node.slice)}]"
        elif isinstance(node, ast.Attribute):
            return self._get_name(node)
        elif isinstance(node, ast.Tuple):
            elements = [self._get_annotation(e) for e in node.elts]
            return f"({', '.join(elements)})"
        return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    
    def _get_value(self, node):
        """Get value from node."""
        if node is None:
            return None
        if isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return f"{node.__class__.__name__}(...)"
        elif isinstance(node, ast.Dict):
            return "Dict(...)"
        return "..."


def scan_python_file(file_path: Path) -> Dict[str, Any]:
    """Scan a single Python file and extract API information."""
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(file_path))
        
        # Get module docstring
        module_docstring = ast.get_docstring(tree)
        
        # Extract API information
        extractor = APIExtractor()
        extractor.visit(tree)
        
        return {
            "path": str(file_path),
            "module": file_path.stem,
            "docstring": module_docstring,
            "api": extractor.api_data
        }
    except Exception as e:
        return {
            "path": str(file_path),
            "error": str(e)
        }


def scan_codebase(path: Path, output: Path, verbose: bool = False, enhance_with_ai: bool = False) -> Dict[str, Any]:
    """Scan entire codebase and extract API information from multiple languages."""
    path = Path(path).resolve()
    output = Path(output).resolve()
    
    # Import for progress
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.console import Console
    import random
    
    console = Console()
    
    # Cocky messages for scanning
    SCAN_MESSAGES = [
        "🔍 Reading your messy code...",
        "📖 Decoding your cryptic functions...",
        "🧩 Untangling your spaghetti...",
        "🎯 Finding the good stuff...",
        "🔬 Analyzing your masterpiece...",
    ]
    
    # Create output directory if it doesn't exist
    output.parent.mkdir(parents=True, exist_ok=True)
    
    # For now, focus on Python files due to tree-sitter compatibility issues
    # Multi-language support is implemented but needs tree-sitter fix
    source_files = list(path.rglob("*.py"))
    
    # Also find JS/TS files for basic info
    js_files = list(path.rglob("*.js")) + list(path.rglob("*.jsx"))
    ts_files = list(path.rglob("*.ts")) + list(path.rglob("*.tsx"))
    
    # Exclude common directories and build artifacts
    exclude_dirs = {
        "__pycache__", ".git", ".venv", "venv", "env", "build", "dist", ".tox", 
        "node_modules", "target", "vendor", ".next", ".cache", ".turbo",
        "coverage", ".nyc_output", ".pytest_cache", "__tests__", "test",
        ".vercel", ".netlify", "out", "public", "static"
    }
    
    # Also exclude common build/config files
    exclude_patterns = [
        "**/node_modules/**",
        "**/.next/**", 
        "**/dist/**",
        "**/build/**",
        "**/*.min.js",
        "**/*.bundle.js",
        "**/chunk-*.js",
        "**/vendor*.js",
        "**/*-manifest.json",
        "**/*-manifest.js",
        "**/webpack*.js"
    ]
    def should_include_file(file_path: Path) -> bool:
        """Check if file should be included in documentation."""
        # Check directory exclusions
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            return False
        
        # Check file name patterns
        name = file_path.name.lower()
        stem = file_path.stem.lower()
        
        # Exclude build artifacts and config files
        exclude_names = [
            'webpack', 'rollup', 'vite', 'babel', 'jest', 'karma',
            '.min.', '.bundle.', 'chunk-', 'vendor', 'manifest',
            'polyfill', 'runtime', 'config.', '.config.', '.test.',
            '.spec.', '.d.ts', 'shims-', 'setup-', 'LICENSE',
            'tailwind', 'postcss', 'eslint', 'prettier', 'tsconfig',
            'next.config', 'package.json', 'package-lock', 'bun.lockb',
            'sitemap', 'robots.txt', 'favicon', '.lock'
        ]
        
        if any(pattern in name for pattern in exclude_names):
            return False
        
        # Exclude Next.js specific build files
        if stem in ['middleware', 'next-env', 'components.json']:
            return False
            
        # Include only source files (not in .next, node_modules, etc)
        path_str = str(file_path)
        if '/.next/' in path_str or '/node_modules/' in path_str or '/build/' in path_str:
            return False
        
        # Only include files in source directories
        preferred_dirs = ['src', 'app', 'components', 'lib', 'pages', 'utils', 'hooks', 'services', 'api', 'store', 'contexts', 'autodoc', 'scripts']
        is_in_preferred = any(dir_name in file_path.parts for dir_name in preferred_dirs)
        
        if not is_in_preferred:
            return False
        
        # For files in app directory, be more selective (Next.js app router)
        if 'app' in file_path.parts:
            # Include page.tsx, layout.tsx, route.ts, etc
            valid_app_files = ['page', 'layout', 'route', 'loading', 'error', 'not-found', 'template', 'provider', 'client']
            
            # Check if it's a valid app file or a React component
            is_valid_app_file = any(valid in stem for valid in valid_app_files)
            is_react_component = (len(stem) > 0 and stem[0].isupper()) or 'component' in stem.lower()
            
            if not (is_valid_app_file or is_react_component):
                return False
        
        return True
    
    source_files = [f for f in source_files if should_include_file(f)]
    js_files = [f for f in js_files if should_include_file(f)]
    ts_files = [f for f in ts_files if should_include_file(f)]
    
    # Combine all files
    all_files = source_files + js_files + ts_files
    
    # Scan all files
    results = {
        "project": path.name,
        "root": str(path),
        "modules": [],
        "languages": {},
        "summary": {
            "total_files": len(all_files),
            "total_classes": 0,
            "total_functions": 0,
            "total_lines": 0,
            "languages": {
                "python": len(source_files),
                "javascript": len(js_files),
                "typescript": len(ts_files)
            }
        }
    }
    
    # Scan Python files with progress
    if enhance_with_ai and (source_files or js_files or ts_files):
        # Show cocky message only when AI is enabled
        scan_msg = random.choice(SCAN_MESSAGES)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True
        ) as progress:
            # Python files
            if source_files:
                task = progress.add_task(f"[cyan]{scan_msg}[/cyan]", total=len(source_files))
                for file_path in source_files:
                    module_data = scan_python_file(file_path)
                    if "error" not in module_data:
                        # Enhance with AI if requested
                        if enhance_with_ai:
                            api_key = os.getenv("OPENAI_API_KEY")
                            if api_key:
                                if verbose:
                                    print(f"  Enhancing with AI: {module_data.get('module', 'unknown')}")
                                try:
                                    from .ai_providers import enhance_module_parallel_sync
                                    # Restructure data for AI enhancer
                                    api_data = module_data.get("api", {})
                                    enhanced_data = {
                                        "module": module_data.get("module"),
                                        "doc": module_data.get("docstring"),
                                        "classes": api_data.get("classes", []),
                                        "functions": api_data.get("functions", [])
                                    }
                                    enhanced_data = enhance_module_parallel_sync(enhanced_data)
                                    # Put enhanced data back
                                    module_data["api"]["classes"] = enhanced_data.get("classes", [])
                                    module_data["api"]["functions"] = enhanced_data.get("functions", [])
                                    module_data["ai_enhanced"] = enhanced_data.get("ai_enhanced", False)
                                    module_data["ai_provider"] = enhanced_data.get("ai_provider", "Unknown")
                                except Exception as e:
                                    if verbose:
                                        print(f"  AI enhancement failed: {e}")
                        
                        results["modules"].append(module_data)
                        
                        # Update summary
                        api = module_data.get("api", {})
                        results["summary"]["total_classes"] += len(api.get("classes", []))
                        results["summary"]["total_functions"] += len(api.get("functions", []))
                        
                        # Count lines
                        try:
                            lines = file_path.read_text().count('\n')
                            results["summary"]["total_lines"] += lines
                        except:
                            pass
    
    # Scan JavaScript/TypeScript files with simple scanner
    from .simple_js_scanner import scan_js_file
    
    for file_path in js_files + ts_files:
        if verbose:
            print(f"Scanning: {file_path}")
        
        module_data = scan_js_file(file_path)
        if "error" not in module_data:
            # Enhance with AI if requested
            if enhance_with_ai:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    if verbose:
                        print(f"  Enhancing with AI: {module_data.get('module', 'unknown')}")
                    try:
                        from .ai_providers import enhance_module_parallel_sync
                        # Restructure data for AI enhancer
                        api_data = module_data.get("api", {})
                        enhanced_data = {
                            "module": module_data.get("module"),
                            "doc": module_data.get("docstring"),
                            "classes": api_data.get("classes", []),
                            "functions": api_data.get("functions", [])
                        }
                        enhanced_data = enhance_module_parallel_sync(enhanced_data)
                        # Put enhanced data back
                        module_data["api"]["classes"] = enhanced_data.get("classes", [])
                        module_data["api"]["functions"] = enhanced_data.get("functions", [])
                        module_data["ai_enhanced"] = enhanced_data.get("ai_enhanced", False)
                        module_data["ai_provider"] = enhanced_data.get("ai_provider", "Unknown")
                    except Exception as e:
                        if verbose:
                            print(f"  AI enhancement failed: {e}")
            
            results["modules"].append(module_data)
            
            # Update summary
            api = module_data.get("api", {})
            results["summary"]["total_classes"] += len(api.get("classes", []))
            results["summary"]["total_functions"] += len(api.get("functions", []))
            
            # Count lines
            try:
                lines = file_path.read_text().count('\n')
                results["summary"]["total_lines"] += lines
            except:
                pass
    
    # Save to JSON
    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
    
    return {
        "files": len(all_files),
        "modules": len(results["modules"]),
        "languages": results["summary"]["languages"] if results["summary"]["languages"] else {}
    }