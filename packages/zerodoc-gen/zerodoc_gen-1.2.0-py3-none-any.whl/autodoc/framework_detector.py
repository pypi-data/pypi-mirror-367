"""Framework detection and auto-configuration for documentation routes."""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple


def detect_framework(project_path: Path) -> Tuple[str, Dict]:
    """
    Detect the framework used in the project and return configuration.
    
    Returns:
        Tuple of (framework_name, config_dict)
    """
    # Check for Next.js
    if (project_path / "next.config.js").exists() or (project_path / "next.config.ts").exists():
        return "nextjs", {
            "docs_path": "public/docs",
            "route": "/docs",
            "instructions": "Docs available at http://localhost:3000/docs"
        }
    
    # Check for package.json
    package_json = project_path / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            data = json.load(f)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}
            
            # React (Create React App)
            if "react-scripts" in all_deps:
                return "create-react-app", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Docs available at http://localhost:3000/docs"
                }
            
            # Vite
            if "vite" in all_deps:
                return "vite", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Docs available at http://localhost:5173/docs"
                }
            
            # Express
            if "express" in all_deps:
                return "express", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Add to your app: app.use('/docs', express.static('public/docs'))",
                    "needs_setup": True
                }
            
            # Vue
            if "vue" in all_deps or "@vue/cli-service" in all_deps:
                return "vue", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Docs available at http://localhost:8080/docs"
                }
            
            # Angular
            if "@angular/core" in all_deps:
                return "angular", {
                    "docs_path": "src/assets/docs",
                    "route": "/assets/docs",
                    "instructions": "Docs available at http://localhost:4200/assets/docs"
                }
    
    # Python frameworks
    requirements = project_path / "requirements.txt"
    pyproject = project_path / "pyproject.toml"
    
    if requirements.exists():
        with open(requirements) as f:
            content = f.read().lower()
            
            # Django
            if "django" in content:
                return "django", {
                    "docs_path": "static/docs",
                    "route": "/static/docs",
                    "instructions": "Add to STATICFILES_DIRS and run collectstatic"
                }
            
            # Flask
            if "flask" in content:
                return "flask", {
                    "docs_path": "static/docs",
                    "route": "/static/docs",
                    "instructions": "Docs available at http://localhost:5000/static/docs"
                }
            
            # FastAPI
            if "fastapi" in content:
                return "fastapi", {
                    "docs_path": "static/docs",
                    "route": "/docs-static",
                    "instructions": "Mount with app.mount('/docs-static', StaticFiles(directory='static/docs'))",
                    "needs_setup": True
                }
    
    # Ruby on Rails
    if (project_path / "Gemfile").exists():
        return "rails", {
            "docs_path": "public/docs",
            "route": "/docs",
            "instructions": "Docs available at http://localhost:3000/docs"
        }
    
    # PHP/Laravel
    if (project_path / "composer.json").exists():
        return "php", {
            "docs_path": "public/docs",
            "route": "/docs",
            "instructions": "Docs available at http://localhost:8000/docs"
        }
    
    # Default fallback
    return "unknown", {
        "docs_path": "docs",
        "route": "/docs",
        "instructions": "Serve docs folder with any static file server"
    }


def setup_route(framework: str, project_path: Path, docs_path: Path) -> Optional[str]:
    """
    Automatically set up routing for certain frameworks.
    Returns the file that was modified, or None.
    """
    if framework == "express":
        # Look for main app file
        for app_file in ["app.js", "server.js", "index.js", "src/app.js", "src/server.js", "src/index.js"]:
            app_path = project_path / app_file
            if app_path.exists():
                with open(app_path, 'r') as f:
                    content = f.read()
                
                # Check if route already exists
                if "/docs" in content and "express.static" in content:
                    return None
                
                # Find where to insert (after other app.use statements)
                lines = content.split('\n')
                insert_index = -1
                
                for i, line in enumerate(lines):
                    if 'app.use(' in line:
                        insert_index = i + 1
                    elif 'app.listen' in line or 'module.exports' in line:
                        if insert_index == -1:
                            insert_index = i
                        break
                
                if insert_index > -1:
                    # Insert the static route
                    route_line = "\n// Auto-generated documentation route\napp.use('/docs', express.static('public/docs'));\n"
                    lines.insert(insert_index, route_line)
                    
                    with open(app_path, 'w') as f:
                        f.write('\n'.join(lines))
                    
                    return str(app_path)
    
    elif framework == "fastapi":
        # Look for main FastAPI app
        for app_file in ["main.py", "app.py", "src/main.py", "src/app.py"]:
            app_path = project_path / app_file
            if app_path.exists():
                with open(app_path, 'r') as f:
                    content = f.read()
                
                # Check if route already exists
                if "StaticFiles" in content and "/docs-static" in content:
                    return None
                
                # Add import if needed
                if "from fastapi.staticfiles import StaticFiles" not in content:
                    lines = content.split('\n')
                    # Add import after other imports
                    for i, line in enumerate(lines):
                        if line.startswith('from fastapi'):
                            lines.insert(i + 1, 'from fastapi.staticfiles import StaticFiles')
                            break
                    content = '\n'.join(lines)
                
                # Add mount statement
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'app = FastAPI' in line:
                        mount_line = '\n# Auto-generated documentation route\napp.mount("/docs-static", StaticFiles(directory="static/docs", html=True), name="docs")\n'
                        lines.insert(i + 1, mount_line)
                        break
                
                with open(app_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                return str(app_path)
    
    return None