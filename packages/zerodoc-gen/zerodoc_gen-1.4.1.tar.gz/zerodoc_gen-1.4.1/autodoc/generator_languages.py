"""Language-specific documentation generators."""

from typing import Dict, Any, List


def generate_javascript_doc(api: Dict[str, Any], language: str) -> List[str]:
    """Generate JavaScript/TypeScript documentation."""
    lines = []
    
    # Document imports
    imports = api.get("imports", [])
    if imports:
        lines.append("## Imports")
        lines.append("")
        lines.append("```" + language)
        for imp in imports:
            lines.append(imp.get("statement", ""))
        lines.append("```")
        lines.append("")
    
    # Document exports
    exports = api.get("exports", [])
    if exports:
        lines.append("## Exports")
        lines.append("")
        for exp in exports:
            lines.append(f"- {exp}")
        lines.append("")
    
    # Document variables/constants
    variables = api.get("variables", [])
    if variables:
        lines.append("## Variables & Constants")
        lines.append("")
        for var in variables:
            kind = var.get("kind", "const")
            var_line = f"- `{kind} {var['name']}`"
            if var.get("type"):
                var_line += f": {var['type']}"
            if var.get("value"):
                var_line += f" = {var['value']}"
            if var.get("exported"):
                var_line += " (exported)"
            lines.append(var_line)
        lines.append("")
    
    # Document functions
    functions = api.get("functions", [])
    if functions:
        lines.append("## Functions")
        lines.append("")
        for func in functions:
            lines.extend(generate_js_function_doc(func))
    
    # Document classes
    classes = api.get("classes", [])
    if classes:
        lines.append("## Classes")
        lines.append("")
        for cls in classes:
            lines.extend(generate_js_class_doc(cls))
            lines.append("---")
            lines.append("")
    
    return lines


def generate_js_function_doc(func: Dict[str, Any]) -> List[str]:
    """Generate JavaScript function documentation."""
    lines = []
    
    # Function signature
    params = func.get("params", [])
    param_str = ", ".join([p.get("name", "") for p in params if p.get("name")])
    
    signature = f"{func['name']}({param_str})"
    if func.get("is_async"):
        signature = f"async {signature}"
    if func.get("exported"):
        signature = f"export {signature}"
    
    lines.append(f"### `{signature}`")
    lines.append("")
    
    # Add description - check for AI enhancement first
    if func.get("detailed_description"):
        desc = func["detailed_description"]
        # Check if it's JSON wrapped in markdown
        if isinstance(desc, str) and desc.strip().startswith("```json"):
            try:
                import json
                # Extract and parse the JSON
                desc_clean = desc.strip()
                if desc_clean.startswith("```json"):
                    desc_clean = desc_clean[7:]
                if desc_clean.endswith("```"):
                    desc_clean = desc_clean[:-3]
                desc_clean = desc_clean.strip()
                
                parsed = json.loads(desc_clean)
                # Use the parsed content
                if parsed.get("description"):
                    lines.append(parsed["description"])
                    lines.append("")
                elif parsed.get("summary"):
                    lines.append(parsed["summary"])
                    lines.append("")
                    
                # Add example if in the parsed JSON
                if parsed.get("example") and not func.get("example"):
                    func["example"] = parsed["example"]
                    
                # Add notes if in the parsed JSON
                if parsed.get("notes") and not func.get("notes"):
                    func["notes"] = parsed["notes"]
                    
                # Add returns if in the parsed JSON
                if parsed.get("returns") and not func.get("returns_detail"):
                    func["returns_detail"] = parsed["returns"]
            except:
                # If parsing fails, use as is
                lines.append(desc)
                lines.append("")
        else:
            lines.append(desc)
            lines.append("")
    elif func.get("doc"):
        lines.append(func["doc"])
        lines.append("")
    elif func.get("docstring"):
        lines.append(func["docstring"])
        lines.append("")
    
    # Add parameter details with descriptions if available
    if params:
        lines.append("**Parameters:**")
        lines.append("")
        for param in params:
            param_line = f"- `{param['name']}`"
            if param.get("type"):
                param_line += f" ({param['type']})"
            if param.get("description"):
                param_line += f": {param['description']}"
            elif param.get("default"):
                param_line += f" - default: `{param['default']}`"
            lines.append(param_line)
        lines.append("")
    
    # Add return type with description if available
    if func.get("returns_detail"):
        ret = func["returns_detail"]
        if isinstance(ret, dict):
            lines.append(f"**Returns:** `{ret.get('type', 'Any')}` - {ret.get('description', '')}")
        else:
            lines.append(f"**Returns:** {ret}")
        lines.append("")
    elif func.get("returns"):
        lines.append(f"**Returns:** `{func['returns']}`")
        lines.append("")
    
    # Add example if available (from AI enhancement)
    if func.get("example"):
        lines.append("**Example:**")
        lines.append("")
        lines.append("```javascript")
        lines.append(func["example"])
        lines.append("```")
        lines.append("")
    
    # Add notes if available (from AI enhancement)
    if func.get("notes"):
        lines.append("**Notes:**")
        for note in func["notes"]:
            lines.append(f"- {note}")
        lines.append("")
    
    return lines


def generate_js_class_doc(cls: Dict[str, Any]) -> List[str]:
    """Generate JavaScript class documentation."""
    lines = []
    
    # Class header
    header = f"## Class: `{cls['name']}`"
    if cls.get("extends"):
        header += f" extends `{cls['extends']}`"
    if cls.get("exported"):
        header = f"**[Exported]** {header}"
    lines.append(header)
    lines.append("")
    
    # Add description - check for AI enhancement first
    if cls.get("detailed_description"):
        desc = cls["detailed_description"]
        # Check if it's JSON wrapped in markdown
        if isinstance(desc, str) and desc.strip().startswith("```json"):
            try:
                import json
                # Extract and parse the JSON
                desc_clean = desc.strip()
                if desc_clean.startswith("```json"):
                    desc_clean = desc_clean[7:]
                if desc_clean.endswith("```"):
                    desc_clean = desc_clean[:-3]
                desc_clean = desc_clean.strip()
                
                parsed = json.loads(desc_clean)
                # Use the parsed content
                if parsed.get("description"):
                    lines.append(parsed["description"])
                    lines.append("")
                elif parsed.get("summary"):
                    lines.append(parsed["summary"])
                    lines.append("")
                    
                # Add use_cases if in the parsed JSON
                if parsed.get("use_cases") and not cls.get("use_cases"):
                    cls["use_cases"] = parsed["use_cases"]
                    
                # Add example if in the parsed JSON
                if parsed.get("example") and not cls.get("example"):
                    cls["example"] = parsed["example"]
                    
                # Add notes if in the parsed JSON
                if parsed.get("notes") and not cls.get("notes"):
                    cls["notes"] = parsed["notes"]
            except:
                # If parsing fails, use as is
                lines.append(desc)
                lines.append("")
        else:
            lines.append(desc)
            lines.append("")
    elif cls.get("doc"):
        lines.append(cls["doc"])
        lines.append("")
    elif cls.get("docstring"):
        lines.append(cls["docstring"])
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
        lines.append("```javascript")
        lines.append(cls["example"])
        lines.append("```")
        lines.append("")
    
    # Add notes if available (from AI enhancement)
    if cls.get("notes"):
        lines.append("**Design Notes:**")
        for note in cls["notes"]:
            lines.append(f"- {note}")
        lines.append("")
    
    # Properties
    properties = cls.get("properties", [])
    if properties:
        lines.append("### Properties")
        lines.append("")
        for prop in properties:
            prop_line = f"- `{prop['name']}`"
            if prop.get("type"):
                prop_line += f": {prop['type']}"
            if prop.get("value"):
                prop_line += f" = {prop['value']}"
            if prop.get("is_static"):
                prop_line = f"- `static {prop['name']}`"
            if prop.get("is_private"):
                prop_line += " (private)"
            lines.append(prop_line)
        lines.append("")
    
    # Methods
    methods = cls.get("methods", [])
    if methods:
        lines.append("### Methods")
        lines.append("")
        
        # Group methods
        constructors = [m for m in methods if m.get("kind") == "constructor" or m.get("name") == "constructor"]
        getters = [m for m in methods if m.get("kind") == "get"]
        setters = [m for m in methods if m.get("kind") == "set"]
        regular = [m for m in methods if m.get("kind", "method") == "method" and m.get("name") != "constructor"]
        
        for constructor in constructors:
            lines.extend(generate_js_method_doc(constructor))
        
        for method in sorted(regular, key=lambda x: x["name"]):
            lines.extend(generate_js_method_doc(method))
        
        for getter in getters:
            lines.extend(generate_js_method_doc(getter))
        
        for setter in setters:
            lines.extend(generate_js_method_doc(setter))
    
    return lines


def generate_js_method_doc(method: Dict[str, Any]) -> List[str]:
    """Generate JavaScript method documentation."""
    lines = []
    
    # Method signature
    params = method.get("params", [])
    param_str = ", ".join([p.get("name", "") for p in params if p.get("name")])
    
    signature = f"{method['name']}({param_str})"
    
    if method.get("kind") == "constructor" or method.get("name") == "constructor":
        signature = f"constructor({param_str})"
    elif method.get("kind") == "get":
        signature = f"get {method['name']}()"
    elif method.get("kind") == "set":
        signature = f"set {method['name']}({param_str})"
    
    if method.get("is_async"):
        signature = f"async {signature}"
    if method.get("is_static"):
        signature = f"static {signature}"
    
    lines.append(f"#### `{signature}`")
    lines.append("")
    
    # Add description - check for AI enhancement first
    if method.get("detailed_description"):
        desc = method["detailed_description"]
        # Check if it's JSON wrapped in markdown
        if isinstance(desc, str) and desc.strip().startswith("```json"):
            try:
                import json
                # Extract and parse the JSON
                desc_clean = desc.strip()
                if desc_clean.startswith("```json"):
                    desc_clean = desc_clean[7:]
                if desc_clean.endswith("```"):
                    desc_clean = desc_clean[:-3]
                desc_clean = desc_clean.strip()
                
                parsed = json.loads(desc_clean)
                # Use the parsed content
                if parsed.get("description"):
                    lines.append(parsed["description"])
                    lines.append("")
                elif parsed.get("summary"):
                    lines.append(parsed["summary"])
                    lines.append("")
                    
                # Add example if in the parsed JSON
                if parsed.get("example") and not method.get("example"):
                    method["example"] = parsed["example"]
                    
                # Add notes if in the parsed JSON
                if parsed.get("notes") and not method.get("notes"):
                    method["notes"] = parsed["notes"]
                    
                # Add returns if in the parsed JSON
                if parsed.get("returns") and not method.get("returns_detail"):
                    method["returns_detail"] = parsed["returns"]
            except:
                # If parsing fails, use as is
                lines.append(desc)
                lines.append("")
        else:
            lines.append(desc)
            lines.append("")
    elif method.get("doc"):
        lines.append(method["doc"])
        lines.append("")
    elif method.get("docstring"):
        lines.append(method["docstring"])
        lines.append("")
    
    # Add parameter details with descriptions if available
    if params and method.get("kind", "") != "get":
        lines.append("**Parameters:**")
        lines.append("")
        for param in params:
            param_line = f"- `{param['name']}`"
            if param.get("type"):
                param_line += f" ({param['type']})"
            if param.get("description"):
                param_line += f": {param['description']}"
            elif param.get("default"):
                param_line += f" - default: `{param['default']}`"
            lines.append(param_line)
        lines.append("")
    
    # Add return type with description if available
    if method.get("returns_detail"):
        ret = method["returns_detail"]
        if isinstance(ret, dict):
            lines.append(f"**Returns:** `{ret.get('type', 'Any')}` - {ret.get('description', '')}")
        else:
            lines.append(f"**Returns:** {ret}")
        lines.append("")
    elif method.get("returns"):
        lines.append(f"**Returns:** `{method['returns']}`")
        lines.append("")
    
    # Add example if available (from AI enhancement)
    if method.get("example"):
        lines.append("**Example:**")
        lines.append("")
        lines.append("```javascript")
        lines.append(method["example"])
        lines.append("```")
        lines.append("")
    
    # Add notes if available (from AI enhancement)
    if method.get("notes"):
        lines.append("**Notes:**")
        for note in method["notes"]:
            lines.append(f"- {note}")
        lines.append("")
    
    return lines


def generate_go_doc(api: Dict[str, Any]) -> List[str]:
    """Generate Go documentation."""
    lines = []
    
    # Package
    if api.get("package"):
        lines.append(f"## Package: `{api['package']}`")
        lines.append("")
    
    # Imports
    imports = api.get("imports", [])
    if imports:
        lines.append("## Imports")
        lines.append("")
        lines.append("```go")
        for imp in imports:
            if imp.get("alias"):
                lines.append(f'{imp["alias"]} "{imp["path"]}"')
            else:
                lines.append(f'"{imp["path"]}"')
        lines.append("```")
        lines.append("")
    
    # Constants
    constants = api.get("constants", [])
    if constants:
        lines.append("## Constants")
        lines.append("")
        for const in constants:
            const_line = f"- `const {const['name']}`"
            if const.get("type"):
                const_line += f" {const['type']}"
            if const.get("value"):
                const_line += f" = {const['value']}"
            if const.get("exported"):
                const_line += " (exported)"
            lines.append(const_line)
        lines.append("")
    
    # Variables
    variables = api.get("variables", [])
    if variables:
        lines.append("## Variables")
        lines.append("")
        for var in variables:
            var_line = f"- `var {var['name']}`"
            if var.get("type"):
                var_line += f" {var['type']}"
            if var.get("value"):
                var_line += f" = {var['value']}"
            if var.get("exported"):
                var_line += " (exported)"
            lines.append(var_line)
        lines.append("")
    
    # Types
    types = api.get("types", [])
    if types:
        lines.append("## Type Aliases")
        lines.append("")
        for typ in types:
            lines.append(f"- `type {typ['name']} = {typ['type']}`")
        lines.append("")
    
    # Functions
    functions = api.get("functions", [])
    if functions:
        lines.append("## Functions")
        lines.append("")
        for func in functions:
            lines.extend(generate_go_function_doc(func))
    
    # Structs
    structs = api.get("structs", [])
    if structs:
        lines.append("## Structs")
        lines.append("")
        for struct in structs:
            lines.extend(generate_go_struct_doc(struct))
    
    # Interfaces
    interfaces = api.get("interfaces", [])
    if interfaces:
        lines.append("## Interfaces")
        lines.append("")
        for iface in interfaces:
            lines.extend(generate_go_interface_doc(iface))
    
    # Methods
    methods = api.get("methods", [])
    if methods:
        lines.append("## Methods")
        lines.append("")
        # Group by receiver type
        methods_by_receiver = {}
        for method in methods:
            receiver = method.get("receiver", {})
            receiver_type = receiver.get("type", "unknown")
            if receiver_type not in methods_by_receiver:
                methods_by_receiver[receiver_type] = []
            methods_by_receiver[receiver_type].append(method)
        
        for receiver_type, type_methods in methods_by_receiver.items():
            lines.append(f"### Methods on `{receiver_type}`")
            lines.append("")
            for method in type_methods:
                lines.extend(generate_go_method_doc(method))
    
    return lines


def generate_go_function_doc(func: Dict[str, Any]) -> List[str]:
    """Generate Go function documentation."""
    lines = []
    
    # Function signature
    params = func.get("params", [])
    param_strs = []
    for p in params:
        param_str = p["name"] if p.get("name") else "_"
        if p.get("type"):
            param_str += f" {p['type']}"
        param_strs.append(param_str)
    
    returns = func.get("returns", [])
    return_str = ""
    if len(returns) == 1:
        return_str = f" {returns[0].get('type', '')}"
    elif len(returns) > 1:
        return_types = [r.get("type", "") for r in returns]
        return_str = f" ({', '.join(return_types)})"
    
    signature = f"func {func['name']}({', '.join(param_strs)}){return_str}"
    
    lines.append(f"### `{signature}`")
    lines.append("")
    
    # Add docstring
    if func.get("docstring"):
        lines.append(func["docstring"])
        lines.append("")
    
    # Exported status
    if func.get("exported"):
        lines.append("**Exported**")
        lines.append("")
    
    return lines


def generate_go_struct_doc(struct: Dict[str, Any]) -> List[str]:
    """Generate Go struct documentation."""
    lines = []
    
    header = f"### `type {struct['name']} struct`"
    if struct.get("exported"):
        header += " (exported)"
    lines.append(header)
    lines.append("")
    
    # Add docstring
    if struct.get("docstring"):
        lines.append(struct["docstring"])
        lines.append("")
    
    # Fields
    fields = struct.get("fields", [])
    if fields:
        lines.append("**Fields:**")
        lines.append("")
        for field in fields:
            field_line = f"- `{field['name']}`"
            if field.get("type"):
                field_line += f" {field['type']}"
            if field.get("tag"):
                field_line += f" {field['tag']}"
            if field.get("exported"):
                field_line += " (exported)"
            lines.append(field_line)
        lines.append("")
    
    return lines


def generate_go_interface_doc(iface: Dict[str, Any]) -> List[str]:
    """Generate Go interface documentation."""
    lines = []
    
    header = f"### `type {iface['name']} interface`"
    if iface.get("exported"):
        header += " (exported)"
    lines.append(header)
    lines.append("")
    
    # Add docstring
    if iface.get("docstring"):
        lines.append(iface["docstring"])
        lines.append("")
    
    # Methods
    methods = iface.get("methods", [])
    if methods:
        lines.append("**Methods:**")
        lines.append("")
        for method in methods:
            params = method.get("params", [])
            param_strs = [p.get("type", "") for p in params]
            returns = method.get("returns", [])
            return_str = ""
            if len(returns) == 1:
                return_str = f" {returns[0].get('type', '')}"
            elif len(returns) > 1:
                return_types = [r.get("type", "") for r in returns]
                return_str = f" ({', '.join(return_types)})"
            
            lines.append(f"- `{method['name']}({', '.join(param_strs)}){return_str}`")
        lines.append("")
    
    return lines


def generate_go_method_doc(method: Dict[str, Any]) -> List[str]:
    """Generate Go method documentation."""
    lines = []
    
    # Method signature
    receiver = method.get("receiver", {})
    params = method.get("params", [])
    param_strs = []
    for p in params:
        param_str = p["name"] if p.get("name") else "_"
        if p.get("type"):
            param_str += f" {p['type']}"
        param_strs.append(param_str)
    
    returns = method.get("returns", [])
    return_str = ""
    if len(returns) == 1:
        return_str = f" {returns[0].get('type', '')}"
    elif len(returns) > 1:
        return_types = [r.get("type", "") for r in returns]
        return_str = f" ({', '.join(return_types)})"
    
    signature = f"func ({receiver.get('name', '_')} {receiver.get('type', '')}) {method['name']}({', '.join(param_strs)}){return_str}"
    
    lines.append(f"#### `{signature}`")
    lines.append("")
    
    # Add docstring
    if method.get("docstring"):
        lines.append(method["docstring"])
        lines.append("")
    
    return lines


def generate_rust_doc(api: Dict[str, Any]) -> List[str]:
    """Generate Rust documentation."""
    lines = []
    
    # Uses
    uses = api.get("uses", [])
    if uses:
        lines.append("## Use Statements")
        lines.append("")
        lines.append("```rust")
        for use in uses:
            lines.append(use["statement"])
        lines.append("```")
        lines.append("")
    
    # Modules
    modules = api.get("modules", [])
    if modules:
        lines.append("## Modules")
        lines.append("")
        for mod in modules:
            mod_line = f"- `mod {mod['name']}`"
            if mod.get("is_pub"):
                mod_line = f"- `pub mod {mod['name']}`"
            lines.append(mod_line)
        lines.append("")
    
    # Constants
    constants = api.get("constants", [])
    if constants:
        lines.append("## Constants")
        lines.append("")
        for const in constants:
            const_line = f"- `const {const['name']}`"
            if const.get("type"):
                const_line += f": {const['type']}"
            if const.get("value"):
                const_line += f" = {const['value']}"
            if const.get("is_pub"):
                const_line = f"- `pub {const_line[3:]}`"
            lines.append(const_line)
        lines.append("")
    
    # Statics
    statics = api.get("statics", [])
    if statics:
        lines.append("## Static Variables")
        lines.append("")
        for static in statics:
            static_line = f"- `static {static['name']}`"
            if static.get("is_mut"):
                static_line = f"- `static mut {static['name']}`"
            if static.get("type"):
                static_line += f": {static['type']}"
            if static.get("value"):
                static_line += f" = {static['value']}"
            if static.get("is_pub"):
                static_line = f"- `pub {static_line[3:]}`"
            lines.append(static_line)
        lines.append("")
    
    # Type aliases
    type_aliases = api.get("type_aliases", [])
    if type_aliases:
        lines.append("## Type Aliases")
        lines.append("")
        for alias in type_aliases:
            alias_line = f"- `type {alias['name']} = {alias['type']}`"
            if alias.get("is_pub"):
                alias_line = f"- `pub {alias_line[3:]}`"
            lines.append(alias_line)
        lines.append("")
    
    # Functions
    functions = api.get("functions", [])
    if functions:
        lines.append("## Functions")
        lines.append("")
        for func in functions:
            lines.extend(generate_rust_function_doc(func))
    
    # Structs
    structs = api.get("structs", [])
    if structs:
        lines.append("## Structs")
        lines.append("")
        for struct in structs:
            lines.extend(generate_rust_struct_doc(struct))
    
    # Enums
    enums = api.get("enums", [])
    if enums:
        lines.append("## Enums")
        lines.append("")
        for enum in enums:
            lines.extend(generate_rust_enum_doc(enum))
    
    # Traits
    traits = api.get("traits", [])
    if traits:
        lines.append("## Traits")
        lines.append("")
        for trait in traits:
            lines.extend(generate_rust_trait_doc(trait))
    
    # Impl blocks
    impl_blocks = api.get("impl_blocks", [])
    if impl_blocks:
        lines.append("## Implementations")
        lines.append("")
        for impl in impl_blocks:
            lines.extend(generate_rust_impl_doc(impl))
    
    return lines


def generate_rust_function_doc(func: Dict[str, Any]) -> List[str]:
    """Generate Rust function documentation."""
    lines = []
    
    # Function signature
    params = func.get("params", [])
    param_strs = []
    for p in params:
        param_str = p.get("name", "_")
        if p.get("type"):
            param_str += f": {p['type']}"
        if p.get("is_mut"):
            param_str = f"mut {param_str}"
        param_strs.append(param_str)
    
    return_type = func.get("return_type", "")
    if return_type:
        return_type = f" -> {return_type}"
    
    signature = f"fn {func['name']}({', '.join(param_strs)}){return_type}"
    if func.get("is_async"):
        signature = f"async {signature}"
    if func.get("is_pub"):
        signature = f"pub {signature}"
    
    lines.append(f"### `{signature}`")
    lines.append("")
    
    # Add docstring
    if func.get("docstring"):
        lines.append(func["docstring"])
        lines.append("")
    
    return lines


def generate_rust_struct_doc(struct: Dict[str, Any]) -> List[str]:
    """Generate Rust struct documentation."""
    lines = []
    
    header = f"### `struct {struct['name']}`"
    if struct.get("is_pub"):
        header = f"### `pub struct {struct['name']}`"
    lines.append(header)
    lines.append("")
    
    # Add docstring
    if struct.get("docstring"):
        lines.append(struct["docstring"])
        lines.append("")
    
    # Fields
    fields = struct.get("fields", [])
    if fields:
        lines.append("**Fields:**")
        lines.append("")
        for field in fields:
            field_line = f"- `{field['name']}`"
            if field.get("type"):
                field_line += f": {field['type']}"
            if field.get("is_pub"):
                field_line = f"- `pub {field['name']}`" + (f": {field['type']}" if field.get("type") else "")
            lines.append(field_line)
        lines.append("")
    
    return lines


def generate_rust_enum_doc(enum: Dict[str, Any]) -> List[str]:
    """Generate Rust enum documentation."""
    lines = []
    
    header = f"### `enum {enum['name']}`"
    if enum.get("is_pub"):
        header = f"### `pub enum {enum['name']}`"
    lines.append(header)
    lines.append("")
    
    # Add docstring
    if enum.get("docstring"):
        lines.append(enum["docstring"])
        lines.append("")
    
    # Variants
    variants = enum.get("variants", [])
    if variants:
        lines.append("**Variants:**")
        lines.append("")
        for variant in variants:
            variant_line = f"- `{variant['name']}`"
            if variant.get("fields"):
                field_strs = [f.get("type", "") for f in variant["fields"] if f.get("type")]
                if field_strs:
                    variant_line += f"({', '.join(field_strs)})"
            lines.append(variant_line)
        lines.append("")
    
    return lines


def generate_rust_trait_doc(trait: Dict[str, Any]) -> List[str]:
    """Generate Rust trait documentation."""
    lines = []
    
    header = f"### `trait {trait['name']}`"
    if trait.get("is_pub"):
        header = f"### `pub trait {trait['name']}`"
    lines.append(header)
    lines.append("")
    
    # Add docstring
    if trait.get("docstring"):
        lines.append(trait["docstring"])
        lines.append("")
    
    # Methods
    methods = trait.get("methods", [])
    if methods:
        lines.append("**Required Methods:**")
        lines.append("")
        for method in methods:
            params = method.get("params", [])
            param_strs = [p.get("type", "") for p in params if p.get("name") != "self"]
            return_type = method.get("return_type", "")
            if return_type:
                return_type = f" -> {return_type}"
            
            lines.append(f"- `fn {method['name']}({', '.join(param_strs)}){return_type}`")
        lines.append("")
    
    return lines


def generate_rust_impl_doc(impl: Dict[str, Any]) -> List[str]:
    """Generate Rust impl block documentation."""
    lines = []
    
    header = f"### `impl {impl['type']}`"
    if impl.get("trait"):
        header = f"### `impl {impl['trait']} for {impl['type']}`"
    lines.append(header)
    lines.append("")
    
    # Methods
    methods = impl.get("methods", [])
    if methods:
        lines.append("**Methods:**")
        lines.append("")
        for method in methods:
            lines.extend(generate_rust_method_doc(method))
    
    return lines


def generate_rust_method_doc(method: Dict[str, Any]) -> List[str]:
    """Generate Rust method documentation."""
    lines = []
    
    # Method signature
    params = method.get("params", [])
    param_strs = []
    for p in params:
        if p.get("name") == "self":
            param_strs.append(p.get("type", "self"))
        else:
            param_str = p.get("name", "_")
            if p.get("type"):
                param_str += f": {p['type']}"
            param_strs.append(param_str)
    
    return_type = method.get("return_type", "")
    if return_type:
        return_type = f" -> {return_type}"
    
    signature = f"fn {method['name']}({', '.join(param_strs)}){return_type}"
    if method.get("is_pub"):
        signature = f"pub {signature}"
    
    lines.append(f"#### `{signature}`")
    lines.append("")
    
    # Add docstring
    if method.get("docstring"):
        lines.append(method["docstring"])
        lines.append("")
    
    return lines