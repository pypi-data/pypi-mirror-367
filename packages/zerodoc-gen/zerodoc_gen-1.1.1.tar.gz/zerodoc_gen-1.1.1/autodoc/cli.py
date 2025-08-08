"""AutoDoc CLI - Main entry point for the documentation generator."""

from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from .scanner import scan_codebase
from .generator import build_markdown, generate_readme
from .exporter import export_site

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
    output: Path = typer.Option("docs", help="Output directory"),
    serve: bool = typer.Option(False, "--serve", "-s", help="Serve docs after generation"),
    port: int = typer.Option(3000, "--port", "-p", help="Port for serving docs"),
):
    """Generate complete documentation (scan + build + export) in one command."""
    console.print(Panel.fit(f"🚀 Generating complete documentation for [cyan]{path}[/cyan]..."))
    
    try:
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
        
        console.print(f"\n✨ Documentation ready at [green]{output}/index.html[/green]")
        console.print(f"\n[dim]To view your docs:[/dim]")
        console.print(f"  • Open [cyan]{output}/index.html[/cyan] in your browser")
        console.print(f"  • Or run: [cyan]autodoc generate . --serve[/cyan]")
        console.print(f"  • For Next.js/React: Copy [cyan]{output}[/cyan] to [cyan]public/docs[/cyan]")
        
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