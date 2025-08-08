"""Exporter module - Converts markdown docs to static HTML site."""

from pathlib import Path
from typing import Dict, Any, List
from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
import shutil
import json


# Linear/GitHub-style minimal CSS
SIMPLE_CSS = """
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #fafafa;
    --bg-tertiary: #f5f5f5;
    --bg-hover: #f8f8f8;
    --text-primary: #0a0a0a;
    --text-secondary: #737373;
    --text-tertiary: #a3a3a3;
    --border: #e5e5e5;
    --border-light: #f0f0f0;
    --accent: #0969da;
    --accent-hover: #0860ca;
    --accent-light: #dbeafe;
    --code-bg: #f6f8fa;
    --code-border: #d1d9e0;
    --success: #1a7f37;
    --warning: #9a6700;
    --error: #cf222e;
    --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
    --shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    --radius: 6px;
    --radius-lg: 8px;
    --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-sans);
    font-size: 14px;
    line-height: 1.5;
    color: var(--text-primary);
    background: var(--bg-secondary);
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.container {
    display: flex;
    height: 100vh;
    overflow: hidden;
}

/* Sidebar */
.sidebar {
    width: 240px;
    background: var(--bg-primary);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
}

.sidebar h2 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sidebar h2 svg {
    width: 16px;
    height: 16px;
    opacity: 0.8;
}

.sidebar-content {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

.search-box {
    width: 100%;
    padding: 6px 8px;
    font-size: 13px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 12px;
    outline: none;
    transition: all 0.15s;
}

.search-box:focus {
    background: var(--bg-primary);
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-light);
}

.search-box::placeholder {
    color: var(--text-tertiary);
}

.nav-section {
    margin-bottom: 4px;
}

.nav-section-title {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 8px 4px 8px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: var(--text-tertiary);
    user-select: none;
}

.nav-section-title::before {
    content: "▸";
    font-size: 10px;
    transition: transform 0.15s;
}

.nav-section.expanded .nav-section-title::before {
    transform: rotate(90deg);
}

.sidebar ul {
    list-style: none;
    margin: 0;
    padding: 0;
}

.sidebar li {
    margin: 1px 0;
}

.sidebar a {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 8px 5px 24px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 13px;
    border-radius: var(--radius);
    transition: all 0.1s;
    position: relative;
}

.sidebar a:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

.sidebar a.active {
    background: var(--accent-light);
    color: var(--accent);
    font-weight: 500;
}

.sidebar a .icon {
    width: 14px;
    height: 14px;
    opacity: 0.6;
    flex-shrink: 0;
}

/* Content Area */
.content {
    flex: 1;
    overflow-y: auto;
    background: var(--bg-primary);
}

.content-inner {
    max-width: 900px;
    margin: 0 auto;
    padding: 32px 48px;
}

.breadcrumb {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 16px;
    font-size: 13px;
    color: var(--text-tertiary);
}

.breadcrumb a {
    color: var(--text-secondary);
    text-decoration: none;
}

.breadcrumb a:hover {
    color: var(--accent);
}

.breadcrumb .separator {
    color: var(--text-tertiary);
}

.content h1 {
    font-size: 32px;
    font-weight: 600;
    line-height: 1.25;
    color: var(--text-primary);
    margin: 0 0 8px 0;
    letter-spacing: -0.02em;
}

.content-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
    font-size: 13px;
    color: var(--text-secondary);
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    background: var(--bg-tertiary);
    border-radius: var(--radius);
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
}

.badge-accent {
    background: var(--accent-light);
    color: var(--accent);
}

.badge-success {
    background: #dcfce7;
    color: var(--success);
}

.content h2 {
    font-size: 24px;
    font-weight: 600;
    margin: 32px 0 16px 0;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

.content h3 {
    font-size: 18px;
    font-weight: 600;
    margin: 24px 0 12px 0;
    color: var(--text-primary);
}

.content h4 {
    font-size: 16px;
    font-weight: 600;
    margin: 16px 0 8px 0;
    color: var(--text-primary);
}

.content p {
    margin: 0 0 16px 0;
    line-height: 1.6;
    color: var(--text-secondary);
}

.content ul, .content ol {
    margin: 0 0 16px 0;
    padding-left: 24px;
    color: var(--text-secondary);
}

.content li {
    margin-bottom: 8px;
    line-height: 1.6;
}

.content li::marker {
    color: var(--text-tertiary);
}

/* Code Styling */
.content code {
    background: var(--code-bg);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: var(--font-mono);
    font-size: 0.85em;
    color: var(--text-primary);
}

.content pre {
    background: var(--code-bg);
    border: 1px solid var(--border);
    padding: 16px;
    border-radius: var(--radius);
    overflow-x: auto;
    margin: 16px 0;
    position: relative;
}

.content pre code {
    background: none;
    padding: 0;
    color: var(--text-primary);
    font-size: 13px;
    line-height: 1.45;
}

/* Blockquotes */
.content blockquote {
    border-left: 3px solid var(--border);
    padding: 0 16px;
    margin: 16px 0;
    color: var(--text-secondary);
}

/* Tables */
.content table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 14px;
}

.content th, .content td {
    padding: 8px 12px;
    text-align: left;
    border: 1px solid var(--border);
}

.content th {
    background: var(--bg-secondary);
    font-weight: 500;
    color: var(--text-primary);
    font-size: 13px;
}

.content tr:hover {
    background: var(--bg-hover);
}

/* Links */
.content a {
    color: var(--accent);
    text-decoration: none;
    transition: color 0.15s;
}

.content a:hover {
    color: var(--accent-hover);
    text-decoration: underline;
}

.content hr {
    border: none;
    height: 1px;
    background: var(--border);
    margin: 2.5rem 0;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #21262d;
        --bg-hover: #30363d;
        --text-primary: #f0f6fc;
        --text-secondary: #8b949e;
        --text-tertiary: #6e7681;
        --border: #30363d;
        --border-light: #21262d;
        --accent: #58a6ff;
        --accent-hover: #79c0ff;
        --accent-light: #1f6feb;
        --code-bg: #161b22;
        --code-border: #30363d;
    }
}

/* Mobile responsive */
@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        position: static;
        height: auto;
        max-height: 40vh;
        border-right: none;
        border-bottom: 1px solid var(--border);
    }
    
    .content-inner {
        padding: 20px;
    }
    
    .content h1 {
        font-size: 24px;
    }
    
    .content h2 {
        font-size: 20px;
    }
    
    .content h3 {
        font-size: 16px;
    }
}

/* Remove animations for cleaner experience */

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
    border: 2px solid var(--bg-primary);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-tertiary);
}

/* Stats Cards */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 24px 0;
}

.stat-card {
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    transition: border-color 0.2s;
}

.stat-card:hover {
    border-color: var(--accent);
}

.stat-value {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
}

.stat-label {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 500;
}
"""


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {project_name}</title>
    <meta name="description" content="API documentation for {project_name}">
    <style>
        {css}
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"/>
                    </svg>
                    {project_name}
                </h2>
            </div>
            <div class="sidebar-content">
                <input type="text" class="search-box" placeholder="Search..." id="searchBox">
                {nav_items}
            </div>
        </nav>
        <main class="content">
            <div class="content-inner">
                {content}
            </div>
        </main>
    </div>
    <script>
        // Search functionality
        const searchBox = document.getElementById('searchBox');
        const navLinks = document.querySelectorAll('.sidebar a');
        const navSections = document.querySelectorAll('.nav-section');
        
        searchBox.addEventListener('input', (e) => {{
            const searchTerm = e.target.value.toLowerCase();
            
            navLinks.forEach(link => {{
                const text = link.textContent.toLowerCase();
                const parent = link.parentElement;
                
                if (text.includes(searchTerm)) {{
                    parent.style.display = '';
                }} else {{
                    parent.style.display = 'none';
                }}
            }});
            
            // Show/hide sections
            navSections.forEach(section => {{
                const visibleItems = section.querySelectorAll('li:not([style*="display: none"])');
                section.style.display = visibleItems.length > 0 ? '' : 'none';
            }});
        }});
        
        // Highlight current page
        const currentPath = window.location.pathname.split('/').pop() || 'index.html';
        navLinks.forEach(link => {{
            if (link.getAttribute('href') === currentPath) {{
                link.classList.add('active');
            }}
        }});
        
        // Collapsible sections
        document.querySelectorAll('.nav-section-title').forEach(title => {{
            title.addEventListener('click', () => {{
                title.parentElement.classList.toggle('expanded');
            }});
        }});
        
        // Initialize all sections as expanded
        navSections.forEach(section => section.classList.add('expanded'));
    </script>
</body>
</html>
"""


def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML using markdown-it-py."""
    md = MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": True})
    
    # Enable useful plugins
    md.enable(["table", "strikethrough"])
    
    return md.render(markdown_content)


def generate_navigation(files: List[Path], current_file: Path) -> str:
    """Generate navigation menu HTML with smart grouping."""
    # Group files by category
    categories = {
        'Overview': [],
        'Components': [],
        'API Routes': [],
        'Utilities': [],
        'Hooks': [],
        'Types': [],
        'Other': []
    }
    
    for file in sorted(files):
        if file.suffix == '.md':
            name = file.stem
            html_file = file.with_suffix('.html')
            active = 'active' if file == current_file else ''
            
            # Smart categorization based on file name patterns
            if name == 'index':
                categories['Overview'].append(
                    f'<li><a href="{html_file.name}" class="{active}">Overview</a></li>'
                )
            elif any(x in name.lower() for x in ['component', 'button', 'card', 'modal', 'nav', 'header', 'footer', 'sidebar', 'menu', 'icon', 'badge']):
                display_name = name.replace('_', ' ').replace('-', ' ').title()
                categories['Components'].append(
                    f'<li><a href="{html_file.name}" class="{active}">{display_name}</a></li>'
                )
            elif any(x in name.lower() for x in ['route', 'api', 'endpoint']):
                display_name = name.replace('_', ' ').replace('-', ' ').title()
                categories['API Routes'].append(
                    f'<li><a href="{html_file.name}" class="{active}">{display_name}</a></li>'
                )
            elif any(x in name.lower() for x in ['util', 'helper', 'service', 'lib', 'auth', 'storage', 'cache']):
                display_name = name.replace('_', ' ').replace('-', ' ').title()
                categories['Utilities'].append(
                    f'<li><a href="{html_file.name}" class="{active}">{display_name}</a></li>'
                )
            elif any(x in name.lower() for x in ['hook', 'use']):
                display_name = name.replace('_', ' ').replace('-', ' ').title()
                categories['Hooks'].append(
                    f'<li><a href="{html_file.name}" class="{active}">{display_name}</a></li>'
                )
            elif any(x in name.lower() for x in ['type', 'interface', 'enum']):
                display_name = name.replace('_', ' ').replace('-', ' ').title()
                categories['Types'].append(
                    f'<li><a href="{html_file.name}" class="{active}">{display_name}</a></li>'
                )
            else:
                display_name = name.replace('_', ' ').replace('-', ' ').title()
                categories['Other'].append(
                    f'<li><a href="{html_file.name}" class="{active}">{display_name}</a></li>'
                )
    
    # Build navigation HTML
    nav_html = []
    for category, items in categories.items():
        if items:  # Only show categories with items
            nav_html.append(f'<div class="nav-section">')
            nav_html.append(f'<div class="nav-section-title">{category}</div>')
            nav_html.append('<ul>')
            nav_html.extend(items)
            nav_html.append('</ul>')
            nav_html.append('</div>')
    
    return '\n'.join(nav_html)


def export_site(source_dir: Path, dest_dir: Path, theme: str = "simple") -> Dict[str, Any]:
    """Export markdown documentation as a static HTML site."""
    source_dir = Path(source_dir).resolve()
    dest_dir = Path(dest_dir).resolve()
    
    # Check if source directory exists
    if not source_dir.exists():
        # Try to generate docs first
        from .generator import build_markdown
        
        project_root = Path.cwd()
        build_markdown(project_root, source_dir, verbose=False)
    
    # Create destination directory
    # If source and dest are the same, don't delete!
    if dest_dir != source_dir and dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all markdown files
    md_files = list(source_dir.glob("*.md"))
    
    if not md_files:
        # No markdown files, create a simple index
        index_content = """# Documentation

No documentation files found. 

Run `autodoc docs .` to generate documentation from your codebase.
"""
        index_file = source_dir / "index.md"
        index_file.write_text(index_content)
        md_files = [index_file]
    
    # Get project name from pyproject.toml or use directory name
    project_name = source_dir.parent.name
    try:
        pyproject = source_dir.parent / "pyproject.toml"
        if pyproject.exists():
            import tomllib
            with open(pyproject, 'rb') as f:
                data = tomllib.load(f)
                project_name = data.get("project", {}).get("name", project_name)
    except:
        pass
    
    # Convert each markdown file to HTML
    converted_files = []
    
    for md_file in md_files:
        # Read markdown content
        md_content = md_file.read_text(encoding='utf-8')
        
        # Convert to HTML
        html_content = markdown_to_html(md_content)
        
        # Generate navigation
        nav_html = generate_navigation(md_files, md_file)
        
        # Create full HTML page
        page_title = md_file.stem.replace('_', ' ').title()
        if md_file.stem == 'index':
            page_title = 'Overview'
        
        css = SIMPLE_CSS
        
        full_html = HTML_TEMPLATE.format(
            title=page_title,
            project_name=project_name,
            css=css,
            nav_items=nav_html,
            content=html_content
        )
        
        # Save HTML file
        html_file = dest_dir / md_file.with_suffix('.html').name
        html_file.write_text(full_html, encoding='utf-8')
        converted_files.append(html_file)
    
    # Create index.html redirect if it doesn't exist
    index_html = dest_dir / "index.html"
    if not index_html.exists():
        # Find the best candidate for index
        candidates = [f for f in converted_files if 'index' in f.stem.lower()]
        if not candidates:
            candidates = converted_files
        
        if candidates:
            # Create a redirect
            redirect_to = candidates[0].name
            redirect_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url={redirect_to}">
    <title>Redirecting...</title>
</head>
<body>
    <p>Redirecting to <a href="{redirect_to}">documentation</a>...</p>
</body>
</html>"""
            index_html.write_text(redirect_html)
    
    # Write a simple manifest
    manifest = {
        "project": project_name,
        "pages": len(converted_files),
        "theme": theme,
        "files": [str(f.name) for f in converted_files]
    }
    
    manifest_file = dest_dir / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return {
        "pages": len(converted_files),
        "theme": theme,
        "dest": str(dest_dir)
    }