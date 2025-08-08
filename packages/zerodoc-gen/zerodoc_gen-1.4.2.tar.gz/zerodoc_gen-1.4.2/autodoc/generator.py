# generator.py
"""Generator module - Converts API data to Markdown documentation."""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import re
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

# --------------------------------------------------------------------------------------
# Logging & small utilities
# --------------------------------------------------------------------------------------

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def safe_get(d: Dict[str, Any], key: str, default=None):
    v = d.get(key, default)
    return v if v is not None else default


def safe_json_load(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in {path}: {e}") from e


def write_text_atomic(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", errors="replace") as f:
        f.write(content)
    os.replace(tmp, path)


_MD_BACKTICK_RE = re.compile(r"`{3,}")


def md_escape(text: Optional[str]) -> str:
    if not text:
        return ""
    # prevent accidental code-fence termination by bumping fence length
    text = _MD_BACKTICK_RE.sub(lambda m: "`" * (len(m.group(0)) + 1), text)
    # normalize newlines
    text = re.sub(r"\r\n?", "\n", text)
    # collapse >2 blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_example_lang(snippet: str) -> str:
    s = (snippet or "").strip()
    if s.startswith("$ ") or s.startswith("autodoc "):
        return "bash"
    if "await " in s or "async " in s:
        if re.search(r"\b(fetch|Response|req|res)\b", s):
            return "javascript"
    if re.search(r"\bimport\s+\w+\s+from\b", s):
        return "javascript"
    return "python"


def _infer_language(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".go": "go",
        ".rs": "rust",
    }.get(ext, "unknown")


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)


# --------------------------------------------------------------------------------------
# Docstring formatting
# --------------------------------------------------------------------------------------

def format_docstring(docstring: Optional[str], indent: int = 0) -> str:
    """Format a docstring for markdown output."""
    if not docstring:
        return "*No description available*"

    lines = [ln.strip() for ln in docstring.strip().splitlines()]
    cleaned: List[str] = []
    last_blank = True
    for ln in lines:
        if ln:
            cleaned.append(ln)
            last_blank = False
        elif not last_blank:
            cleaned.append("")
            last_blank = True

    result = md_escape("\n".join(cleaned))
    if indent > 0:
        result = textwrap.indent(result, " " * indent)
    return result


# --------------------------------------------------------------------------------------
# Markdown generators (functions/classes/modules)
# --------------------------------------------------------------------------------------

def generate_function_doc(func: Dict[str, Any]) -> str:
    """Generate markdown documentation for a function."""
    lines: List[str] = []

    # Function signature
    args: List[str] = []
    params = func.get("params") or func.get("args", [])
    for arg in params:
        name = arg.get("name", "")
        arg_str = name
        if arg.get("type"):
            arg_str += f": {arg['type']}"
        if arg.get("default") is not None:
            arg_str += f" = {arg['default']}"
        args.append(arg_str)

    signature = f"{func.get('name', 'unknown')}({', '.join(args)})"
    if func.get("returns"):
        signature += f" -> {func['returns']}"
    elif func.get("returns_detail", {}).get("type"):
        signature += f" -> {func['returns_detail']['type']}"

    if func.get("is_async"):
        signature = f"async {signature}"

    lines.append(f"### `{signature}`")
    lines.append("")

    # Decorators
    decorators = func.get("decorators", [])
    if decorators:
        lines.append("**Decorators:** " + ", ".join(decorators))
        lines.append("")

    # Description (AI-enhanced preferred)
    if func.get("detailed_description"):
        lines.append(md_escape(func["detailed_description"]))
    else:
        lines.append(format_docstring(func.get("docstring")))
    lines.append("")

    # Usage context
    if func.get("usage_context"):
        lines.append(f"**📍 Usage Context:** {md_escape(func['usage_context'])}")
        lines.append("")

    # Parameters
    if params:
        lines.append("#### Parameters")
        lines.append("")
        for arg in params:
            pname = arg.get("name", "")
            ptype = arg.get("type")
            pdesc = arg.get("description")
            pdef = arg.get("default")
            param_line = f"- **`{pname}`**"
            if ptype:
                param_line += f" *({ptype})*"
            if pdesc:
                param_line += f" — {md_escape(pdesc)}"
            elif pdef is not None:
                param_line += f" — defaults to `{pdef}`"
            lines.append(param_line)
        lines.append("")

    # Returns
    if func.get("returns_detail"):
        ret = func["returns_detail"]
        lines.append("#### Returns")
        lines.append("")
        if isinstance(ret, dict):
            ret_line = f"- **Type:** `{ret.get('type', 'Any')}`"
            lines.append(ret_line)
            if ret.get("description"):
                lines.append(f"- **Description:** {md_escape(ret['description'])}")
        else:
            lines.append(f"- `{ret}`")
        lines.append("")
    elif func.get("returns"):
        lines.append("#### Returns")
        lines.append("")
        lines.append(f"- `{func['returns']}`")
        lines.append("")

    # Example
    example = func.get("example")
    if example:
        ex = str(example)
        lang = detect_example_lang(ex)
        lines.append("#### Example")
        lines.append("")
        lines.append(f"```{lang}")
        lines.append(md_escape(ex))
        lines.append("```")
        lines.append("")

    # Notes
    if func.get("notes"):
        lines.append("#### Notes")
        lines.append("")
        for note in func["notes"]:
            lines.append(f"- {md_escape(str(note))}")
        lines.append("")

    return "\n".join(lines)


def generate_class_doc(cls: Dict[str, Any]) -> str:
    """Generate markdown documentation for a class."""
    lines: List[str] = []

    header = f"## Class: `{cls.get('name', 'Unknown')}`"
    bases = cls.get("bases")
    if bases:
        header += f" (inherits from: {', '.join(bases)})"
    lines.append(header)
    lines.append("")

    decorators = cls.get("decorators", [])
    if decorators:
        lines.append("**Decorators:** " + ", ".join(decorators))
        lines.append("")

    if cls.get("detailed_description"):
        lines.append(md_escape(cls["detailed_description"]))
    else:
        lines.append(format_docstring(cls.get("docstring")))
    lines.append("")

    if cls.get("use_cases"):
        lines.append("**Common Use Cases:**")
        for use_case in cls["use_cases"]:
            lines.append(f"- {md_escape(str(use_case))}")
        lines.append("")

    if cls.get("example"):
        lines.append("**Example:**")
        lines.append("")
        lines.append("```python")
        lines.append(md_escape(str(cls["example"])))
        lines.append("```")
        lines.append("")

    if cls.get("notes"):
        lines.append("**Design Notes:**")
        for note in cls["notes"]:
            lines.append(f"- {md_escape(str(note))}")
        lines.append("")

    attributes = cls.get("attributes", [])
    if attributes:
        lines.append("### Attributes")
        lines.append("")
        for attr in attributes:
            attr_line = f"- `{attr.get('name', '')}`"
            if attr.get("type"):
                attr_line += f": {attr['type']}"
            if attr.get("value") is not None:
                attr_line += f" = {attr['value']}"
            lines.append(attr_line)
        lines.append("")

    methods = cls.get("methods", [])
    if methods:
        lines.append("### Methods")
        lines.append("")
        init_methods = [m for m in methods if m.get("name") == "__init__"]
        special_methods = [m for m in methods if m.get("name", "").startswith("__") and m.get("name") != "__init__"]
        regular_methods = [m for m in methods if not m.get("name", "").startswith("__")]

        for method in init_methods:
            lines.append(generate_function_doc(method))

        for method in sorted(regular_methods, key=lambda x: x.get("name", "")):
            lines.append(generate_function_doc(method))

        for method in sorted(special_methods, key=lambda x: x.get("name", "")):
            lines.append(generate_function_doc(method))

    return "\n".join(lines)


def generate_python_doc(api: Dict[str, Any]) -> List[str]:
    """Generate Python-specific documentation."""
    lines: List[str] = []

    # Imports
    imports = api.get("imports", [])
    if imports:
        lines.append("## Imports")
        lines.append("")
        for imp in imports:
            if imp.get("type") == "import":
                imp_line = f"- `import {imp.get('module', '')}`"
                if imp.get("alias"):
                    imp_line += f" as `{imp['alias']}`"
            else:
                imp_line = f"- `from {imp.get('module', '')} import {imp.get('name', '')}`"
                if imp.get("alias"):
                    imp_line += f" as `{imp['alias']}`"
            lines.append(imp_line)
        lines.append("")

    # Variables
    variables = api.get("variables", [])
    if variables:
        lines.append("## Module Variables")
        lines.append("")
        for var in variables:
            var_line = f"- `{var.get('name', '')}`"
            if var.get("type"):
                var_line += f": {var['type']}"
            if var.get("value") is not None:
                var_line += f" = {var['value']}"
            lines.append(var_line)
        lines.append("")

    # Functions
    functions = api.get("functions", [])
    if functions:
        lines.append("## Functions")
        lines.append("")
        for func in sorted(functions, key=lambda x: x.get("name", "")):
            lines.append(generate_function_doc(func))

    # Classes
    classes = api.get("classes", [])
    if classes:
        lines.append("## Classes")
        lines.append("")
        for cls in sorted(classes, key=lambda x: x.get("name", "")):
            lines.append(generate_class_doc(cls))
            lines.append("---")
            lines.append("")

    return lines


def generate_module_doc(module: Dict[str, Any]) -> str:
    """Generate markdown documentation for a module."""
    lines: List[str] = []

    module_name = module.get("module", "Unknown Module")
    language = module.get("language") or _infer_language(module.get("path", ""))

    lines.append(f"# Module: `{module_name}`")
    lines.append("")

    if module.get("ai_enhanced"):
        lines.append("*✨ Enhanced with AI-generated documentation*")
        lines.append("")

    path_str = module.get("path", "")
    lines.append(f"**File:** `{path_str}`")
    lines.append(f"**Language:** {language.title()}")
    lines.append("")

    if module.get("docstring"):
        lines.append("## Description")
        lines.append("")
        lines.append(format_docstring(module["docstring"]))
        lines.append("")

    api = module.get("api", {})
    lang = language.lower()

    if lang == "python":
        lines.extend(generate_python_doc(api))
    elif lang in ["javascript", "typescript"]:
        try:
            # Optional import — keep your original structure if present
            from .generator_languages import generate_javascript_doc  # type: ignore
            lines.extend(generate_javascript_doc(api, lang))
        except Exception:
            lines.extend(generate_python_doc(api))  # fallback
    elif lang == "go":
        try:
            from .generator_languages import generate_go_doc  # type: ignore
            lines.extend(generate_go_doc(api))
        except Exception:
            lines.extend(generate_python_doc(api))
    elif lang == "rust":
        try:
            from .generator_languages import generate_rust_doc  # type: ignore
            lines.extend(generate_rust_doc(api))
        except Exception:
            lines.extend(generate_python_doc(api))
    else:
        lines.extend(generate_python_doc(api))

    return "\n".join(lines)


# --------------------------------------------------------------------------------------
# Index page
# --------------------------------------------------------------------------------------

def generate_index_page(modules: List[Dict[str, Any]], project_name: str) -> str:
    """Generate an enhanced index page for all modules."""
    lines: List[str] = []

    total_classes = sum(len(m.get("api", {}).get("classes", [])) for m in modules)
    total_functions = sum(len(m.get("api", {}).get("functions", [])) for m in modules)
    total_lines = 0
    languages: Dict[str, int] = {}

    for module in modules:
        # Count lines from file (best-effort)
        path = Path(module.get("path", ""))
        if path.exists() and path.is_file():
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    total_lines += sum(1 for _ in f)
            except OSError:
                pass
        else:
            # Heuristic fallback so "Lines of Code" isn't zeroed
            funcs = len(module.get("api", {}).get("functions", []))
            clss = len(module.get("api", {}).get("classes", []))
            total_lines += funcs * 8 + clss * 12

        lang = module.get("language") or _infer_language(module.get("path", ""))
        languages[lang] = languages.get(lang, 0) + 1

    lines.append(f"# {project_name} Documentation")
    lines.append("")
    lines.append(f"Welcome to the comprehensive API documentation for **{project_name}**.")
    lines.append("")
    lines.append("## 📊 Project Statistics")
    lines.append("")
    lines.append('<div class="stats-grid">')
    lines.append(f'<div class="stat-card"><div class="stat-value">{len(modules)}</div><div class="stat-label">Total Modules</div></div>')
    lines.append(f'<div class="stat-card"><div class="stat-value">{total_classes}</div><div class="stat-label">Classes</div></div>')
    lines.append(f'<div class="stat-card"><div class="stat-value">{total_functions}</div><div class="stat-label">Functions</div></div>')
    lines.append(f'<div class="stat-card"><div class="stat-value">{total_lines:,}</div><div class="stat-label">Lines of Code</div></div>')
    lines.append('</div>')
    lines.append("")

    if languages:
        lines.append("## 💻 Language Distribution")
        lines.append("")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            emoji = "🐍" if lang == "python" else "📜" if lang in ["javascript", "typescript"] else "📄"
            lines.append(f"- {emoji} **{(lang or 'unknown').title()}**: {count} files")
        lines.append("")

    lines.append("## 🗂️ Documentation Structure")
    lines.append("")

    # Group modules by containing directory
    packages: Dict[str, List[Dict[str, Any]]] = {}
    for module in modules:
        p = Path(module.get("path", ""))
        package = p.parent.name if p.parent.name else "root"
        packages.setdefault(package, []).append(module)

    for package, mods in sorted(packages.items()):
        lines.append(f"### 📁 {package}/" if package != "root" else "### 📁 Root")
        lines.append("")
        for module in sorted(mods, key=lambda x: x.get("module", "")):
            module_file = f"{module.get('module', 'unknown')}.md"
            html_file = module_file.replace(".md", ".html")
            icon = "📄"
            module_lower = module.get("module", "").lower()
            if any(x in module_lower for x in ["component", "ui"]):
                icon = "🧩"
            elif any(x in module_lower for x in ["route", "api"]):
                icon = "🔌"
            elif any(x in module_lower for x in ["util", "helper", "lib"]):
                icon = "🔧"
            elif any(x in module_lower for x in ["hook", "use"]):
                icon = "🪝"
            elif any(x in module_lower for x in ["test", "spec"]):
                icon = "🧪"

            lines.append(f"- {icon} [{module.get('module', 'unknown')}](./{html_file})")
            if module.get("docstring"):
                first_line = module["docstring"].split("\n")[0]
                if len(first_line) > 80:
                    first_line = first_line[:77] + "..."
                lines.append(f"  - *{md_escape(first_line)}*")
        lines.append("")

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

    return "\n".join(lines)


# --------------------------------------------------------------------------------------
# AI Enhancement (robust path)
# --------------------------------------------------------------------------------------

class AIEnhancer:
    """Resilient AI enhancement helper with retries, bounded concurrency, and lenient JSON parsing."""

    def __init__(self, api_key: Optional[str], model: str = "gpt-4o-mini", timeout_s: int = 20, concurrency: int = 4):
        self.api_key = api_key
        self.model = model
        self.timeout_s = timeout_s
        self.semaphore = asyncio.Semaphore(concurrency)
        self._session = None

    async def __aenter__(self):
        if not self.api_key:
            return self
        import aiohttp
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_s))
        return self

    async def __aexit__(self, *exc):
        if self._session:
            await self._session.close()

    @staticmethod
    def _extract_json(payload: str) -> Optional[Dict[str, Any]]:
        txt = (payload or "").strip()
        m = re.search(r"```json\s*(.*?)\s*```", txt, re.S)
        if m:
            txt = m.group(1)
        else:
            m2 = re.search(r"```(.*?)```", txt, re.S)
            if m2:
                txt = m2.group(1)
        try:
            return json.loads(txt)
        except Exception:
            return None

    @staticmethod
    def _build_prompt(func: Dict[str, Any], module_context: Dict[str, Any]) -> str:
        name = func.get("name", "unknown")
        params = func.get("params") or func.get("args", [])
        param_str = ", ".join([p.get("name", "") for p in params])
        returns = func.get("returns", "Any")
        docstring = func.get("docstring", "") or "None"
        module_name = module_context.get("module", "")
        module_path = module_context.get("path", "")

        return f"""You are documenting a function in the {module_name} module of a documentation generator tool.
Module path: {module_path}
Function: {name}({param_str}) -> {returns}
Current docstring: {docstring}

This tool scans code and generates Markdown docs.

Return ONLY a JSON object with:
{{
  "description": "Clear explanation of what this function does",
  "params": [{{"name":"param_name", "type":"type", "description":"..."}}, ...],
  "returns": {{"type":"return_type", "description":"..."}},
  "example": "Code snippet showing how this function is used in the autodoc workflow",
  "usage_context": "When/why to use this function in the documentation pipeline"
}}"""

    async def enhance_function(self, func: Dict[str, Any], module_context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key or not self._session:
            return func

        async with self.semaphore:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a documentation expert. Be concise and practical."},
                    {"role": "user", "content": self._build_prompt(func, module_context)},
                ],
                "temperature": 0.2,
                "max_tokens": 500,
            }

            for attempt in range(4):
                try:
                    async with self._session.post(
                        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
                    ) as r:
                        if r.status != 200:
                            txt = await r.text()
                            raise RuntimeError(f"LLM {r.status}: {txt[:200]}")
                        data = await r.json()
                        content = safe_get(safe_get(data, "choices", [{}])[0], "message", {}).get("content", "")
                        parsed = self._extract_json(content) or {"description": content.strip()}

                        out = dict(func)
                        desc = parsed.get("description")
                        if desc:
                            out["detailed_description"] = desc
                            out["doc"] = desc[:100]

                        if "params" in parsed:
                            name_to_param = {p.get("name"): p for p in out.get("params", out.get("args", []))}
                            for ap in parsed.get("params") or []:
                                n = ap.get("name")
                                if n and n in name_to_param:
                                    if ap.get("description"):
                                        name_to_param[n]["description"] = ap["description"]
                                    if ap.get("type") and not name_to_param[n].get("type"):
                                        name_to_param[n]["type"] = ap["type"]

                        if "returns" in parsed:
                            ret = parsed["returns"]
                            if isinstance(ret, dict):
                                out["returns_detail"] = {
                                    "type": ret.get("type", "Any"),
                                    "description": ret.get("description", ""),
                                }
                            else:
                                out["returns_detail"] = {"type": str(ret), "description": ""}

                        if parsed.get("example"):
                            out["example"] = parsed["example"]

                        if parsed.get("usage_context"):
                            out["usage_context"] = parsed["usage_context"]

                        out["ai_enhanced"] = True
                        return out
                except Exception as e:
                    wait = 2 ** attempt
                    logger.warning(
                        f"AI enhance retry {attempt+1}/4 for {func.get('name','?')}: {e}. Backing off {wait}s."
                    )
                    await asyncio.sleep(wait)

            logger.error(f"AI enhancement failed for {func.get('name','?')}; leaving original.")
            return func


# --------------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------------

def generate_module_docset(modules: List[Dict[str, Any]], output_dir: Path, verbose: bool) -> List[Path]:
    """Generate documentation files for all modules. Returns list of written files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_files: List[Path] = []

    for module in modules:
        if "error" in module:
            logger.warning("Skipping errored module: %s", module.get("module"))
            continue
        doc_content = generate_module_doc(module)
        doc_file = output_dir / f"{module.get('module', 'unknown')}.md"
        write_text_atomic(doc_file, doc_content)
        doc_files.append(doc_file)
        if verbose:
            logger.info("Generated: %s", doc_file)

    return doc_files


def build_markdown(project_path: Path, output_dir: Path, verbose: bool = False, ai_enhance: bool = False) -> Dict[str, Any]:
    """Build markdown documentation from scanned API data."""
    setup_logging(verbose)

    project_path = Path(project_path).resolve()
    output_dir = Path(output_dir).resolve()

    scan_output = project_path / "build" / "api.json"

    # Only scan if api.json doesn't exist
    if not scan_output.exists():
        from .scanner import scan_codebase  # type: ignore
        scan_output.parent.mkdir(parents=True, exist_ok=True)
        try:
            scan_codebase(project_path, scan_output, verbose, False)
        except Exception as e:
            raise RuntimeError(f"Scan failed: {e}") from e

    # Load the scanned data
    data = safe_json_load(scan_output)

    # Apply AI enhancement to the loaded data if requested
    if ai_enhance:
        import aiohttp  # noqa: F401  # ensure dependency error is visible early
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("AUTODOC_LLM_MODEL", "gpt-4o-mini")
        logger.info("🤖 AI enhancement %s", "enabled" if api_key else "disabled (no key)")

        async def enhance_all(mods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            async with AIEnhancer(api_key, model=model, timeout_s=20, concurrency=4) as enh:
                enhanced_modules: List[Dict[str, Any]] = []
                for i, module in enumerate(mods):
                    if "error" in module:
                        enhanced_modules.append(module)
                        continue

                    api = module.get("api", {})
                    funcs = api.get("functions", [])
                    cap = int(os.getenv("AUTODOC_AI_PER_MODULE", "8"))
                    tasks = [enh.enhance_function(func, module) for func in funcs[:cap]]
                    if tasks:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        for j, r in enumerate(results):
                            if not isinstance(r, Exception):
                                funcs[j] = r
                    module["ai_enhanced"] = True
                    enhanced_modules.append(module)
                return enhanced_modules

        data["modules"] = _run_async(enhance_all(data.get("modules", [])))
        # Save back to api.json atomically
        write_text_atomic(scan_output, json.dumps(data, indent=2))

    # Generate documentation for each module
    modules = data.get("modules", [])
    doc_files = generate_module_docset(modules, output_dir, verbose)

    # Generate index page
    if modules:
        index_content = generate_index_page(modules, data.get("project", "Project"))
        index_file = output_dir / "index.md"
        write_text_atomic(index_file, index_content)
        doc_files.append(index_file)

    return {
        "files": len(doc_files),
        "modules": len(modules),
    }


def generate_readme(project_path: Path, template_name: str = "default", force: bool = False) -> Dict[str, Any]:
    """Generate README.md from template."""
    project_path = Path(project_path).resolve()
    readme_path = project_path / "README.md"

    if readme_path.exists() and not force:
        return {
            "updated": False,
            "path": str(readme_path),
            "message": "README.md already exists. Use --force to overwrite.",
        }

    # Project info
    project_name = project_path.name
    description = "A Python project"
    version = "0.1.0"

    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            import tomllib  # py3.11+
        except ImportError:  # pragma: no cover
            import tomli as tomllib  # type: ignore

        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
            project_info = data.get("project", {})
            project_name = project_info.get("name", project_name)
            description = project_info.get("description", description)
            version = project_info.get("version", version)

    # Templates
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,  # Markdown, not HTML
        undefined=StrictUndefined,
    )

    try:
        template = env.get_template("README.md.j2")
    except Exception:
        # Default template
        template_content = """# {{ project_name }}

{{ description }}

## Installation

```bash
pip install {{ module_name }}
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

*Generated with AutoDoc*
"""
        template = env.from_string(template_content)

    module_name = project_name.replace("-", "_")
    readme_content = template.render(
        project_name=project_name,
        module_name=module_name,
        description=description,
        version=version,
    )

    write_text_atomic(readme_path, readme_content)

    return {
        "updated": True,
        "path": str(readme_path),
    }
