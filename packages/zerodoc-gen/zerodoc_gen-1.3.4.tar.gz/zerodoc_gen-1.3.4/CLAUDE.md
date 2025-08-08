# AutoDoc Typer – 2‑Hour MVP Design Doc

*(Draft v0.1 – feel free to tweak and commit directly in the canvas)*

## 1. Problem & Opportunity

- GitBook’s **\$65–\$79/site/month** pricing is prohibitive for side‑projects. ([saasworthy.com](https://www.saasworthy.com/product/gitbook/pricing?utm_source=chatgpt.com), [gitbook.com](https://www.gitbook.com/pricing?utm_source=chatgpt.com))
- 73 % of devs say poor docs kill productivity – teams lose **5.3 h/week** per engineer. ([dev.to](https://dev.to/teamcamp/developer-first-documentation-why-73-of-teams-fail-and-how-to-build-docs-that-actually-get-used-36fb?utm_source=chatgpt.com))
- Start‑ups like Featurebase cite “bad docs” as their #1 churn driver.

**Goal:** one‑command, zero‑config *open‑source* doc generator that any repo can bundle.

---

## 2. MVP Scope (finishable in \~2 focused hours)

| Component                 | What it Does                                                                | Est. time |
| ------------------------- | --------------------------------------------------------------------------- | --------- |
| **CLI shell** (`autodoc`) | Typer app with `scan`, `readme`, `export` commands                          | 15 min    |
| **Scanner**               | Walk source tree, parse Python files with `ast` → JSON structure            | 25 min    |
| **Doc generator**         | Convert JSON → Markdown (per module) + index                                | 25 min    |
| **README template**       | Jinja2 template ⇒ `README.md` with badges, install, usage                   | 10 min    |
| **Static‑site exporter**  | Render Markdown → HTML with `markdown_it` + minimalist CSS; copy to `site/` | 25 min    |
| **Quick demo workflow**   | GitHub Action: on `push`, run `autodoc export` & upload Pages artifact      | 20 min    |
| **Packaging**             | `pyproject.toml`, MIT license, `__version__`                                | 10 min    |

Total ≈ **2 h** if you copy‑paste skeletons and stay laser‑focused.

---

## 3. Directory Layout

```
autodoc-typer/
├── autodoc/
│   ├── __init__.py
│   ├── cli.py         # Typer entrypoint
│   ├── scanner.py
│   ├── generator.py
│   ├── exporter.py
│   └── templates/
│       └── README.md.j2
├── tests/
├── pyproject.toml
└── README.md
```

---

## 4. Code Skeleton

### `autodoc/cli.py`

```python
from pathlib import Path
import typer
from .scanner import scan_codebase
from .generator import build_markdown
from .exporter import export_site

app = typer.Typer(help="📝 AutoDoc — zero‑config docs generator")

@app.command()
def scan(
    path: Path = typer.Argument(".", help="Codebase root"),
    out: Path = typer.Option("build/api.json", help="JSON output"),
):
    """Scan codebase and dump API schema."""
    scan_codebase(path, out)

@app.command()
def readme(
    project: Path = typer.Argument(".", help="Repo root"),
    template: str = typer.Option("default", help="Template name"),
):
    """Generate or update README.md."""
    build_markdown(project, template)

@app.command()
def export(
    dest: Path = typer.Option("site", help="Export directory"),
    theme: str = typer.Option("simple", help="Site theme"),
):
    """Export docs as static site."""
    export_site(dest, theme)

if __name__ == "__main__":
    app()
```

*(**`scanner.py`**, **`generator.py`**, **`exporter.py`** come with minimal implementations + TODOs to keep the 2‑hour scope.)*

---

## 5. Install & Quick Start

```bash
pipx install autodoc-typer  # local dev
autodoc scan .
autodoc readme
autodoc export --dest site
open site/index.html
```

---

## 6. Good First Issues

1. **Add language support**: extend `scanner.py` to parse TypeScript using `tree_sitter`.
2. **Improve theme**: swap inline CSS for Tailwind; dark‑mode toggle.
3. **Git integration**: auto‑commit generated docs on successful run.

---

## 7. Growth Roadmap

- **AI enrichment** – call OpenAI or Ollama locally to expand terse docstrings into full explanations.
- **Multiple output formats** – Docusaurus, MkDocs Yaml export.
- **“docs‑as‑code” CI** – PR comment bot that shows diff of API changes vs docs.

---

## 8. License

MIT – because low friction encourages contributions.

---

## 9. Next Steps Right Now

1. `git init && gh repo create autodoc-typer --public`
2. Paste this document into `docs/ROADMAP.md`.
3. Copy the code skeleton into place.
4. **Run** the CLI on one of your existing repos to smoke‑test.

