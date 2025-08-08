"""Framework detection and auto-configuration for documentation routes."""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple


def detect_language(project_path: Path) -> str:
    """Detect if project uses TypeScript or JavaScript."""
    # Check for TypeScript config
    if (project_path / "tsconfig.json").exists():
        return "typescript"
    
    # Check for .ts or .tsx files in common directories
    for pattern in ["*.ts", "*.tsx", "**/*.ts", "**/*.tsx"]:
        try:
            # Get first matching file if any exist
            next(project_path.glob(pattern))
            return "typescript"
        except StopIteration:
            continue
    
    return "javascript"


def detect_package_manager(project_path: Path) -> str:
    """Detect which package manager is being used."""
    if (project_path / "pnpm-lock.yaml").exists():
        return "pnpm"
    elif (project_path / "yarn.lock").exists():
        return "yarn"
    elif (project_path / "package-lock.json").exists():
        return "npm"
    elif (project_path / "bun.lockb").exists():
        return "bun"
    return "npm"  # default


def detect_framework(project_path: Path) -> Tuple[str, Dict]:
    """
    Detect the framework used in the project and return configuration.
    
    Returns:
        Tuple of (framework_name, config_dict)
    """
    lang = detect_language(project_path)
    pkg_manager = detect_package_manager(project_path)
    
    # Check for Next.js
    if (project_path / "next.config.js").exists() or \
       (project_path / "next.config.mjs").exists() or \
       (project_path / "next.config.ts").exists():
        
        app_dir = project_path / "app"
        src_app_dir = project_path / "src" / "app"
        pages_dir = project_path / "pages"
        src_pages_dir = project_path / "src" / "pages"
        
        # Detect App Router
        if app_dir.exists() or src_app_dir.exists():
            return "nextjs-app", {
                "docs_path": "public/docs",
                "route": "/docs",
                "instructions": f"Docs will be available at http://localhost:3000/docs",
                "needs_route_file": True,
                "language": lang,
                "src_dir": "src" if src_app_dir.exists() else None
            }
        # Detect Pages Router
        elif pages_dir.exists() or src_pages_dir.exists():
            return "nextjs-pages", {
                "docs_path": "public/docs",
                "route": "/docs",
                "instructions": "Docs available at http://localhost:3000/docs (static files)",
                "language": lang
            }
    
    # Check for Remix
    if (project_path / "remix.config.js").exists():
        return "remix", {
            "docs_path": "public/docs",
            "route": "/docs",
            "instructions": "Docs available at http://localhost:3000/docs",
            "needs_route_file": True,
            "language": lang
        }
    
    # Check for Nuxt
    if (project_path / "nuxt.config.js").exists() or \
       (project_path / "nuxt.config.ts").exists():
        # Detect Nuxt 3 vs Nuxt 2
        package_json = project_path / "package.json"
        nuxt_version = 3  # default
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "nuxt" in deps:
                    version = deps["nuxt"]
                    if version.startswith("^2") or version.startswith("~2"):
                        nuxt_version = 2
        
        if nuxt_version == 3:
            return "nuxt3", {
                "docs_path": "public/docs",
                "route": "/docs",
                "instructions": "Docs available at http://localhost:3000/docs",
                "needs_route_file": True,
                "language": lang
            }
        else:
            return "nuxt2", {
                "docs_path": "static/docs",
                "route": "/docs",
                "instructions": "Docs available at http://localhost:3000/docs",
                "language": lang
            }
    
    # Check for SvelteKit
    if (project_path / "svelte.config.js").exists():
        return "sveltekit", {
            "docs_path": "static/docs",
            "route": "/docs",
            "instructions": "Docs available at http://localhost:5173/docs",
            "needs_route_file": True,
            "language": lang
        }
    
    # Check for Astro
    if (project_path / "astro.config.mjs").exists():
        return "astro", {
            "docs_path": "public/docs",
            "route": "/docs",
            "instructions": "Docs available at http://localhost:4321/docs",
            "language": lang
        }
    
    # Check package.json for other frameworks
    package_json = project_path / "package.json"
    if package_json.exists():
        with open(package_json) as f:
            data = json.load(f)
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}
            scripts = data.get("scripts", {})
            
            # Check for Vite
            if "vite" in all_deps:
                # Check if it's Vue + Vite
                if "vue" in all_deps:
                    vue_version = all_deps.get("vue", "3")
                    if vue_version.startswith("^3") or vue_version.startswith("~3") or "3" in vue_version:
                        return "vue3-vite", {
                            "docs_path": "public/docs",
                            "route": "/docs",
                            "instructions": "Docs available at http://localhost:5173/docs",
                            "language": lang
                        }
                    else:
                        return "vue2-vite", {
                            "docs_path": "public/docs",
                            "route": "/docs",
                            "instructions": "Docs available at http://localhost:5173/docs",
                            "language": lang
                        }
                # Check if it's React + Vite
                elif "react" in all_deps:
                    return "react-vite", {
                        "docs_path": "public/docs",
                        "route": "/docs",
                        "instructions": "Docs available at http://localhost:5173/docs",
                        "language": lang
                    }
                # Check if it's Svelte (not SvelteKit)
                elif "svelte" in all_deps:
                    return "svelte-vite", {
                        "docs_path": "public/docs",
                        "route": "/docs",
                        "instructions": "Docs available at http://localhost:5173/docs",
                        "language": lang
                    }
                else:
                    return "vite", {
                        "docs_path": "public/docs",
                        "route": "/docs",
                        "instructions": "Docs available at http://localhost:5173/docs",
                        "language": lang
                    }
            
            # React (Create React App)
            if "react-scripts" in all_deps:
                return "create-react-app", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Docs available at http://localhost:3000/docs",
                    "language": lang
                }
            
            # Vue CLI
            if "@vue/cli-service" in all_deps:
                return "vue-cli", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Docs available at http://localhost:8080/docs",
                    "language": lang
                }
            
            # Angular
            if "@angular/core" in all_deps:
                return "angular", {
                    "docs_path": "src/assets/docs",
                    "route": "/assets/docs",
                    "instructions": "Docs available at http://localhost:4200/assets/docs",
                    "language": lang
                }
            
            # Express
            if "express" in all_deps:
                # Check if it's using ES modules or CommonJS
                module_type = data.get("type", "commonjs")
                return "express", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Add to your app: app.use('/docs', express.static('public/docs'))",
                    "needs_setup": True,
                    "module_type": module_type,
                    "language": lang
                }
            
            # Fastify
            if "fastify" in all_deps:
                return "fastify", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Register static plugin for docs",
                    "needs_setup": True,
                    "language": lang
                }
            
            # Koa
            if "koa" in all_deps:
                return "koa", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Use koa-static for serving docs",
                    "needs_setup": True,
                    "language": lang
                }
            
            # Gatsby
            if "gatsby" in all_deps:
                return "gatsby", {
                    "docs_path": "static/docs",
                    "route": "/docs",
                    "instructions": "Docs available at http://localhost:8000/docs",
                    "language": lang
                }
    
    # Python frameworks
    requirements = project_path / "requirements.txt"
    pyproject = project_path / "pyproject.toml"
    pipfile = project_path / "Pipfile"
    
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
        with open(project_path / "Gemfile") as f:
            content = f.read()
            if "rails" in content:
                return "rails", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Docs available at http://localhost:3000/docs"
                }
    
    # PHP/Laravel
    if (project_path / "composer.json").exists():
        with open(project_path / "composer.json") as f:
            data = json.load(f)
            if "laravel/framework" in data.get("require", {}):
                return "laravel", {
                    "docs_path": "public/docs",
                    "route": "/docs",
                    "instructions": "Docs available at http://localhost:8000/docs"
                }
    
    # Go frameworks
    if (project_path / "go.mod").exists():
        with open(project_path / "go.mod") as f:
            content = f.read()
            if "gin-gonic/gin" in content:
                return "gin", {
                    "docs_path": "static/docs",
                    "route": "/docs",
                    "instructions": "Use Static() to serve docs",
                    "needs_setup": True
                }
            elif "fiber" in content:
                return "fiber", {
                    "docs_path": "static/docs",
                    "route": "/docs",
                    "instructions": "Use Static() middleware",
                    "needs_setup": True
                }
            elif "echo" in content:
                return "echo", {
                    "docs_path": "static/docs",
                    "route": "/docs",
                    "instructions": "Use Static() middleware",
                    "needs_setup": True
                }
    
    # Default fallback
    return "unknown", {
        "docs_path": "docs",
        "route": "/docs",
        "instructions": "Serve docs folder with any static file server"
    }


def create_nextjs_app_route(project_path: Path, config: Dict) -> bool:
    """Create a Next.js App Router page for serving documentation."""
    import shutil
    
    # Determine file extension
    ext = ".tsx" if config.get("language") == "typescript" else ".jsx"
    
    # Determine app directory
    src_dir = config.get("src_dir")
    app_base = project_path / src_dir / "app" if src_dir else project_path / "app"
    
    # Create app/docs directory
    docs_dir = app_base / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create page file
    page_file = docs_dir / f"page{ext}"
    page_content = '''export default function DocsPage() {
  return (
    <iframe
      src="/docs/index.html"
      style={{
        width: '100vw',
        height: '100vh',
        border: 'none',
        position: 'fixed',
        top: 0,
        left: 0,
      }}
      title="Documentation"
    />
  );
}
'''
    
    # Create layout file to remove default padding
    layout_file = docs_dir / f"layout{ext}"
    
    if config.get("language") == "typescript":
        layout_content = '''export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
'''
    else:
        layout_content = '''export default function DocsLayout({ children }) {
  return <>{children}</>;
}
'''
    
    with open(page_file, 'w') as f:
        f.write(page_content)
    
    with open(layout_file, 'w') as f:
        f.write(layout_content)
    
    return True


def create_remix_route(project_path: Path, config: Dict) -> bool:
    """Create a Remix route for serving documentation."""
    ext = ".tsx" if config.get("language") == "typescript" else ".jsx"
    
    # Create app/routes/docs.tsx
    routes_dir = project_path / "app" / "routes"
    routes_dir.mkdir(parents=True, exist_ok=True)
    
    route_file = routes_dir / f"docs._index{ext}"
    route_content = '''export default function DocsRoute() {
  return (
    <iframe
      src="/docs/index.html"
      style={{
        width: '100vw',
        height: '100vh',
        border: 'none',
      }}
      title="Documentation"
    />
  );
}
'''
    
    with open(route_file, 'w') as f:
        f.write(route_content)
    
    return True


def create_nuxt3_route(project_path: Path, config: Dict) -> bool:
    """Create a Nuxt 3 page for serving documentation."""
    # Create pages/docs.vue
    pages_dir = project_path / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    page_file = pages_dir / "docs.vue"
    page_content = '''<template>
  <iframe
    src="/docs/index.html"
    style="width: 100vw; height: 100vh; border: none; position: fixed; top: 0; left: 0;"
    title="Documentation"
  />
</template>

<script setup>
// Documentation page
</script>
'''
    
    with open(page_file, 'w') as f:
        f.write(page_content)
    
    return True


def create_sveltekit_route(project_path: Path, config: Dict) -> bool:
    """Create a SvelteKit route for serving documentation."""
    # Create src/routes/docs/+page.svelte
    routes_dir = project_path / "src" / "routes" / "docs"
    routes_dir.mkdir(parents=True, exist_ok=True)
    
    page_file = routes_dir / "+page.svelte"
    page_content = '''<iframe
  src="/docs/index.html"
  style="width: 100vw; height: 100vh; border: none; position: fixed; top: 0; left: 0;"
  title="Documentation"
/>
'''
    
    with open(page_file, 'w') as f:
        f.write(page_content)
    
    return True


def setup_route(framework: str, project_path: Path, docs_path: Path, config: Dict) -> Optional[str]:
    """
    Automatically set up routing for certain frameworks.
    Returns the file that was modified, or None.
    """
    if framework == "nextjs-app":
        if create_nextjs_app_route(project_path, config):
            ext = ".tsx" if config.get("language") == "typescript" else ".jsx"
            src_dir = config.get("src_dir")
            path = f"{src_dir}/app/docs/page{ext}" if src_dir else f"app/docs/page{ext}"
            return path
    
    elif framework == "remix":
        if create_remix_route(project_path, config):
            ext = ".tsx" if config.get("language") == "typescript" else ".jsx"
            return f"app/routes/docs._index{ext}"
    
    elif framework == "nuxt3":
        if create_nuxt3_route(project_path, config):
            return "pages/docs.vue"
    
    elif framework == "sveltekit":
        if create_sveltekit_route(project_path, config):
            return "src/routes/docs/+page.svelte"
    
    elif framework == "express":
        # Look for main app file
        exts = [".ts", ".js", ".mjs", ".cjs"]
        files = ["app", "server", "index", "main"]
        dirs = ["", "src/", "server/"]
        
        for dir in dirs:
            for file in files:
                for ext in exts:
                    app_path = project_path / f"{dir}{file}{ext}"
                    if app_path.exists():
                        with open(app_path, 'r') as f:
                            content = f.read()
                        
                        # Check if route already exists
                        if "/docs" in content and "express.static" in content:
                            return None
                        
                        # Find where to insert
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
        for app_file in ["main.py", "app.py", "server.py", "src/main.py", "src/app.py"]:
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
                    for i, line in enumerate(lines):
                        if line.startswith('from fastapi'):
                            lines.insert(i + 1, 'from fastapi.staticfiles import StaticFiles')
                            break
                    content = '\n'.join(lines)
                
                # Add mount statement
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'app = FastAPI' in line or 'FastAPI()' in line:
                        mount_line = '\n# Auto-generated documentation route\napp.mount("/docs-static", StaticFiles(directory="static/docs", html=True), name="docs")\n'
                        lines.insert(i + 1, mount_line)
                        break
                
                with open(app_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                return str(app_path)
    
    return None