"""AutoDoc CLI - Main entry point for the documentation generator."""

from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from .scanner import scan_codebase
from .generator import build_markdown, generate_readme
from .exporter import export_site
from .framework_detector import detect_framework, setup_route

app = typer.Typer(
    name="autodoc",
    help="📝 AutoDoc — zero-config docs generator",
    add_completion=False,
)
console = Console()


@app.command()
def scan(
    path: Path = typer.Argument(".", help="Codebase root"),
    out: Path = typer.Option("build/api.json", help="JSON output"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Scan codebase and dump API schema."""
    console.print(Panel.fit(f"🔍 Scanning codebase at [cyan]{path}[/cyan]..."))
    
    try:
        result = scan_codebase(path, out, verbose)
        console.print(f"✅ Scanned {result['files']} files, found {result['modules']} modules")
        console.print(f"📄 Output saved to [green]{out}[/green]")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def readme(
    project: Path = typer.Argument(".", help="Repo root"),
    template: str = typer.Option("default", help="Template name"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing README"),
):
    """Generate or update README.md."""
    console.print(Panel.fit(f"📝 Generating README for [cyan]{project}[/cyan]..."))
    
    try:
        result = generate_readme(project, template, force)
        console.print(f"✅ README.md {'updated' if result['updated'] else 'created'}")
        console.print(f"📄 Location: [green]{result['path']}[/green]")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def docs(
    path: Path = typer.Argument(".", help="Codebase root"),
    output: Path = typer.Option("docs", help="Output directory for markdown docs"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Generate markdown documentation for the codebase."""
    console.print(Panel.fit(f"📚 Generating documentation for [cyan]{path}[/cyan]..."))
    
    try:
        result = build_markdown(path, output, verbose)
        console.print(f"✅ Generated {result['files']} documentation files")
        console.print(f"📄 Output directory: [green]{output}[/green]")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def export(
    source: Path = typer.Option("docs", help="Source markdown directory"),
    dest: Path = typer.Option("site", help="Export directory"),
    theme: str = typer.Option("simple", help="Site theme"),
    serve: bool = typer.Option(False, "--serve", "-s", help="Start local server after export"),
):
    """Export docs as static site."""
    console.print(Panel.fit(f"🌐 Exporting static site to [cyan]{dest}[/cyan]..."))
    
    try:
        result = export_site(source, dest, theme)
        console.print(f"✅ Exported {result['pages']} pages")
        console.print(f"🌐 Site available at [green]{dest}/index.html[/green]")
        
        if serve:
            import http.server
            import socketserver
            import os
            import webbrowser
            
            os.chdir(dest)
            PORT = 8000
            Handler = http.server.SimpleHTTPRequestHandler
            
            console.print(f"\n🚀 Starting server at [cyan]http://localhost:{PORT}[/cyan]")
            console.print("Press Ctrl+C to stop the server\n")
            
            webbrowser.open(f"http://localhost:{PORT}")
            
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                httpd.serve_forever()
                
    except KeyboardInterrupt:
        console.print("\n👋 Server stopped")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def generate(
    path: Path = typer.Argument(".", help="Codebase root"),
    output: Path = typer.Option(None, help="Output directory (auto-detected if not specified)"),
    serve: bool = typer.Option(False, "--serve", "-s", help="Serve docs after generation"),
    port: int = typer.Option(3000, "--port", "-p", help="Port for serving docs"),
    auto: bool = typer.Option(True, "--auto/--no-auto", help="Auto-detect framework and configure"),
):
    """Generate complete documentation (scan + build + export) in one command."""
    console.print(Panel.fit(f"🚀 Generating complete documentation for [cyan]{path}[/cyan]..."))
    
    try:
        # Detect framework if auto mode
        framework_name = "unknown"
        framework_config = {}
        
        if auto:
            console.print("\n[bold]🔍 Detecting framework...[/bold]")
            framework_name, framework_config = detect_framework(Path(path))
            
            if framework_name != "unknown":
                console.print(f"  ✅ Detected: [green]{framework_name}[/green]")
                
                # Use framework-specific output path if not specified
                if output is None:
                    output = Path(framework_config["docs_path"])
                    console.print(f"  📁 Using framework path: [cyan]{output}[/cyan]")
            else:
                console.print("  ℹ️  No framework detected, using default settings")
                if output is None:
                    output = Path("docs")
        
        if output is None:
            output = Path("docs")
        
        # Step 1: Scan
        console.print("\n[bold]Step 1:[/bold] Scanning codebase...")
        api_json = output / "api.json"
        scan_result = scan_codebase(path, api_json, False)
        console.print(f"  ✅ Scanned {scan_result['files']} files")
        
        # Step 2: Generate markdown
        console.print("\n[bold]Step 2:[/bold] Generating markdown documentation...")
        docs_result = build_markdown(path, output, False)
        console.print(f"  ✅ Generated {docs_result['files']} documentation files")
        
        # Step 3: Export to HTML
        console.print("\n[bold]Step 3:[/bold] Exporting to HTML...")
        export_result = export_site(output, output, "simple")
        console.print(f"  ✅ Exported {export_result['pages']} pages")
        
        # Step 4: Setup route if needed
        if auto and framework_name != "unknown":
            if framework_config.get("needs_setup") or framework_config.get("needs_route_file"):
                console.print("\n[bold]Step 4:[/bold] Setting up route...")
                modified_file = setup_route(framework_name, Path(path), output, framework_config)
                if modified_file:
                    console.print(f"  ✅ Created route: [green]{modified_file}[/green]")
                else:
                    console.print(f"  ℹ️  Route already configured or manual setup needed")
        
        console.print(f"\n✨ Documentation ready!")
        
        if framework_name != "unknown":
            console.print(f"\n[bold]📚 Access your docs:[/bold]")
            console.print(f"  [cyan]{framework_config['instructions']}[/cyan]")
            console.print(f"  Route: [green]{framework_config['route']}[/green]")
        else:
            console.print(f"\n[dim]To view your docs:[/dim]")
            console.print(f"  • Open [cyan]{output}/index.html[/cyan] in your browser")
            console.print(f"  • Or run: [cyan]autodoc generate . --serve[/cyan]")
        
        if serve:
            import http.server
            import socketserver
            import os
            import webbrowser
            
            os.chdir(output)
            Handler = http.server.SimpleHTTPRequestHandler
            
            console.print(f"\n🚀 Starting server at [cyan]http://localhost:{port}/[/cyan]")
            console.print("Press Ctrl+C to stop the server\n")
            
            webbrowser.open(f"http://localhost:{port}/")
            
            with socketserver.TCPServer(("", port), Handler) as httpd:
                httpd.serve_forever()
                
    except KeyboardInterrupt:
        console.print("\n👋 Server stopped")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"AutoDoc version [cyan]{__version__}[/cyan]")


if __name__ == "__main__":
    app()