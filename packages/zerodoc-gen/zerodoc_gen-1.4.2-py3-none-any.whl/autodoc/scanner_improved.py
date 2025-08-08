"""Improved scanner with progress bars and parallel processing."""

import os
import ast
import json
import random
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console

console = Console()

# Import existing scanners
from .scanner import scan_python_file, APIExtractor
from .simple_js_scanner import scan_js_file
from .ai_providers import enhance_module_parallel_sync


def scan_codebase_fast(path: Path, output: Path, verbose: bool = False, enhance_with_ai: bool = False) -> Dict[str, Any]:
    """Fast codebase scanner with parallel AI enhancement."""
    path = Path(path).resolve()
    output = Path(output).resolve()
    
    # Cocky loading messages
    SCAN_MESSAGES = [
        "🔍 Reading your messy code",
        "📖 Decoding your cryptic functions", 
        "🧩 Untangling your spaghetti",
        "🎯 Finding the good stuff",
        "🔬 Analyzing your masterpiece",
    ]
    
    AI_MESSAGES = [
        "🚀 Making your docs actually readable",
        "⚡ Injecting intelligence into your code",
        "🧠 Teaching functions to explain themselves",
        "✨ Sprinkling AI magic dust",
        "🔥 Cooking up fire documentation",
    ]
    
    # Create output directory
    output.parent.mkdir(parents=True, exist_ok=True)
    
    # Find source files
    source_files = list(path.rglob("*.py"))
    js_files = list(path.rglob("*.js")) + list(path.rglob("*.jsx"))
    ts_files = list(path.rglob("*.ts")) + list(path.rglob("*.tsx"))
    
    # Filter files (exclude build artifacts, node_modules, etc.)
    exclude_dirs = {
        "node_modules", ".next", "dist", "build", ".git", 
        "__pycache__", ".pytest_cache", "venv", ".venv",
        "site-packages", ".tox", "htmlcov", ".coverage"
    }
    
    def should_include(f: Path) -> bool:
        return not any(excluded in f.parts for excluded in exclude_dirs)
    
    source_files = [f for f in source_files if should_include(f)]
    js_files = [f for f in js_files if should_include(f)]
    ts_files = [f for f in ts_files if should_include(f)]
    
    all_files = source_files + js_files + ts_files
    
    # Initialize results
    results = {
        "project": path.name,
        "root": str(path),
        "modules": [],
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
    
    if not all_files:
        # Save empty results
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        return {"files": 0, "modules": 0}
    
    # Process files with progress bar
    modules_to_enhance = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True
    ) as progress:
        
        # Scan phase
        scan_msg = random.choice(SCAN_MESSAGES)
        scan_task = progress.add_task(f"[cyan]{scan_msg}[/cyan]", total=len(all_files))
        
        # Process Python files
        for file_path in source_files:
            module_data = scan_python_file(file_path)
            if "error" not in module_data:
                module_data["language"] = "python"
                modules_to_enhance.append(module_data)
                
                # Update stats
                api = module_data.get("api", {})
                results["summary"]["total_classes"] += len(api.get("classes", []))
                results["summary"]["total_functions"] += len(api.get("functions", []))
            
            progress.update(scan_task, advance=1)
        
        # Process JavaScript/TypeScript files
        for file_path in js_files + ts_files:
            module_data = scan_js_file(file_path)
            if "error" not in module_data:
                module_data["language"] = "typescript" if file_path.suffix in [".ts", ".tsx"] else "javascript"
                modules_to_enhance.append(module_data)
                
                # Update stats
                api = module_data.get("api", {})
                results["summary"]["total_classes"] += len(api.get("classes", []))
                results["summary"]["total_functions"] += len(api.get("functions", []))
            
            progress.update(scan_task, advance=1)
    
    # AI Enhancement phase (if enabled)
    if enhance_with_ai and modules_to_enhance:
        # Check if any provider is available
        from .ai_providers import ParallelAIEnhancer
        enhancer = ParallelAIEnhancer()
        
        if enhancer.active_provider:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
                transient=True
            ) as progress:
                
                ai_msg = random.choice(AI_MESSAGES)
                ai_task = progress.add_task(
                    f"[green]{ai_msg} with {enhancer.get_provider_name()}[/green]", 
                    total=len(modules_to_enhance)
                )
                
                # Process in batches for speed
                batch_size = 5
                for i in range(0, len(modules_to_enhance), batch_size):
                    batch = modules_to_enhance[i:i+batch_size]
                    
                    # Enhance batch in parallel
                    for module_data in batch:
                        try:
                            # Restructure data for enhancer
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
                        except:
                            pass  # Silent fail, keep original
                        
                        progress.update(ai_task, advance=1)
    
    # Add all modules to results
    results["modules"] = modules_to_enhance
    
    # Count total lines
    for module in modules_to_enhance:
        try:
            file_path = Path(module["path"])
            if file_path.exists():
                lines = file_path.read_text().count('\n')
                results["summary"]["total_lines"] += lines
        except:
            pass
    
    # Save results
    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
    
    return {
        "files": len(all_files),
        "modules": len(results["modules"]),
        "ai_enhanced": enhance_with_ai and any(m.get("ai_enhanced") for m in results["modules"])
    }