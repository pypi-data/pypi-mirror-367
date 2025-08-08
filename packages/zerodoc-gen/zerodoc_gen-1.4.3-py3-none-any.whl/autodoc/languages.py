"""Multi-language scanner using tree-sitter for parsing various programming languages."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
try:
    from tree_sitter_languages import get_language, get_parser
    from tree_sitter import Node
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Node = None


class LanguageParser:
    """Base class for language-specific parsers."""
    
    def __init__(self, language: str):
        self.language = language
        if TREE_SITTER_AVAILABLE:
            self.parser = get_parser(language)
        
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a single file and extract API information."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = self.parser.parse(bytes(content, 'utf-8'))
            
            return {
                "path": str(file_path),
                "module": file_path.stem,
                "language": self.language,
                "api": self.extract_api(tree.root_node, content)
            }
        except Exception as e:
            return {
                "path": str(file_path),
                "error": str(e)
            }
    
    def extract_api(self, root: Node, source: str) -> Dict[str, Any]:
        """Extract API information from the syntax tree."""
        return {
            "classes": [],
            "functions": [],
            "variables": [],
            "imports": [],
            "exports": []
        }
    
    def get_node_text(self, node: Node, source: str) -> str:
        """Get the text content of a node."""
        return source[node.start_byte:node.end_byte]
    
    def get_comment_before(self, node: Node, source: str) -> Optional[str]:
        """Get comment/docstring before a node."""
        # Look for comments in previous siblings
        prev = node.prev_sibling
        comments = []
        
        while prev and prev.type in ['comment', 'block_comment']:
            comment_text = self.get_node_text(prev, source)
            comments.insert(0, comment_text)
            prev = prev.prev_sibling
        
        if comments:
            return '\n'.join(comments)
        return None
    
    def clean_comment(self, comment: str) -> str:
        """Clean comment text from comment markers."""
        if not comment:
            return ""
        
        lines = comment.split('\n')
        cleaned = []
        
        for line in lines:
            line = line.strip()
            # Remove common comment markers
            if line.startswith('//'):
                line = line[2:].strip()
            elif line.startswith('#'):
                line = line[1:].strip()
            elif line.startswith('/*'):
                line = line[2:].strip()
            elif line.endswith('*/'):
                line = line[:-2].strip()
            elif line.startswith('*'):
                line = line[1:].strip()
            
            if line:
                cleaned.append(line)
        
        return ' '.join(cleaned)


class JavaScriptParser(LanguageParser):
    """Parser for JavaScript and TypeScript files."""
    
    def __init__(self, is_typescript: bool = False):
        language = 'tsx' if is_typescript else 'javascript'
        super().__init__(language)
        self.is_typescript = is_typescript
    
    def extract_api(self, root: Node, source: str) -> Dict[str, Any]:
        """Extract JavaScript/TypeScript API information."""
        api = {
            "classes": [],
            "functions": [],
            "variables": [],
            "imports": [],
            "exports": []
        }
        
        for node in root.children:
            self._extract_node(node, source, api)
        
        return api
    
    def _extract_node(self, node: Node, source: str, api: Dict, parent_class: Optional[Dict] = None):
        """Recursively extract API information from a node."""
        
        # Handle imports
        if node.type in ['import_statement', 'import_declaration']:
            self._extract_import(node, source, api)
        
        # Handle exports
        elif node.type in ['export_statement', 'export_declaration']:
            # Check what's being exported
            for child in node.children:
                if child.type in ['class_declaration', 'class']:
                    self._extract_class(child, source, api, is_exported=True)
                elif child.type in ['function_declaration', 'function']:
                    self._extract_function(child, source, api, is_exported=True)
                elif child.type in ['lexical_declaration', 'variable_declaration']:
                    self._extract_variable(child, source, api, is_exported=True)
                else:
                    self._extract_node(child, source, api, parent_class)
        
        # Handle classes
        elif node.type in ['class_declaration', 'class']:
            self._extract_class(node, source, api)
        
        # Handle functions
        elif node.type in ['function_declaration', 'function', 'arrow_function']:
            if parent_class:
                self._extract_method(node, source, parent_class)
            else:
                self._extract_function(node, source, api)
        
        # Handle variables
        elif node.type in ['lexical_declaration', 'variable_declaration']:
            self._extract_variable(node, source, api)
        
        # Handle method definitions in classes
        elif node.type == 'method_definition' and parent_class:
            self._extract_method(node, source, parent_class)
        
        # Recurse into children
        else:
            for child in node.children:
                self._extract_node(child, source, api, parent_class)
    
    def _extract_class(self, node: Node, source: str, api: Dict, is_exported: bool = False):
        """Extract class information."""
        name_node = None
        extends_node = None
        body_node = None
        
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
            elif child.type == 'class_heritage':
                # Look for extends clause
                for heritage_child in child.children:
                    if heritage_child.type == 'identifier':
                        extends_node = heritage_child
            elif child.type == 'class_body':
                body_node = child
        
        if name_node:
            class_info = {
                "name": self.get_node_text(name_node, source),
                "docstring": self.clean_comment(self.get_comment_before(node, source)),
                "methods": [],
                "properties": [],
                "extends": self.get_node_text(extends_node, source) if extends_node else None,
                "exported": is_exported,
                "lineno": node.start_point[0] + 1
            }
            
            # Extract methods and properties from class body
            if body_node:
                for child in body_node.children:
                    if child.type == 'method_definition':
                        self._extract_method(child, source, class_info)
                    elif child.type in ['field_definition', 'property_definition']:
                        self._extract_property(child, source, class_info)
            
            api["classes"].append(class_info)
    
    def _extract_function(self, node: Node, source: str, api: Dict, is_exported: bool = False):
        """Extract function information."""
        name_node = None
        params_node = None
        body_node = None
        is_async = False
        
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
            elif child.type == 'formal_parameters':
                params_node = child
            elif child.type in ['statement_block', 'block']:
                body_node = child
            elif child.type == 'async':
                is_async = True
        
        # Handle arrow functions
        if node.type == 'arrow_function':
            # Try to get name from parent assignment
            parent = node.parent
            if parent and parent.type in ['variable_declarator', 'assignment_expression']:
                for sibling in parent.children:
                    if sibling.type == 'identifier':
                        name_node = sibling
                        break
        
        if name_node:
            func_info = {
                "name": self.get_node_text(name_node, source),
                "docstring": self.clean_comment(self.get_comment_before(node, source)),
                "params": self._extract_parameters(params_node, source) if params_node else [],
                "is_async": is_async,
                "exported": is_exported,
                "lineno": node.start_point[0] + 1
            }
            
            api["functions"].append(func_info)
    
    def _extract_method(self, node: Node, source: str, class_info: Dict):
        """Extract method information from a class."""
        name_node = None
        params_node = None
        is_async = False
        is_static = False
        is_private = False
        kind = "method"  # method, get, set, constructor
        
        for child in node.children:
            if child.type in ['property_identifier', 'identifier']:
                name_node = child
            elif child.type == 'formal_parameters':
                params_node = child
            elif child.type == 'async':
                is_async = True
            elif child.type == 'static':
                is_static = True
            elif child.type in ['get', 'set']:
                kind = child.type
        
        if name_node:
            method_name = self.get_node_text(name_node, source)
            is_private = method_name.startswith('#') or method_name.startswith('_')
            
            method_info = {
                "name": method_name,
                "docstring": self.clean_comment(self.get_comment_before(node, source)),
                "params": self._extract_parameters(params_node, source) if params_node else [],
                "is_async": is_async,
                "is_static": is_static,
                "is_private": is_private,
                "kind": kind if kind != "method" else ("constructor" if method_name == "constructor" else "method"),
                "lineno": node.start_point[0] + 1
            }
            
            class_info["methods"].append(method_info)
    
    def _extract_property(self, node: Node, source: str, class_info: Dict):
        """Extract property/field from a class."""
        name_node = None
        type_node = None
        value_node = None
        is_static = False
        is_private = False
        
        for child in node.children:
            if child.type in ['property_identifier', 'identifier']:
                name_node = child
            elif child.type == 'type_annotation' and self.is_typescript:
                type_node = child
            elif child.type in ['number', 'string', 'true', 'false', 'null']:
                value_node = child
            elif child.type == 'static':
                is_static = True
        
        if name_node:
            prop_name = self.get_node_text(name_node, source)
            is_private = prop_name.startswith('#') or prop_name.startswith('_')
            
            prop_info = {
                "name": prop_name,
                "type": self.get_node_text(type_node, source) if type_node else None,
                "value": self.get_node_text(value_node, source) if value_node else None,
                "is_static": is_static,
                "is_private": is_private,
                "lineno": node.start_point[0] + 1
            }
            
            class_info["properties"].append(prop_info)
    
    def _extract_variable(self, node: Node, source: str, api: Dict, is_exported: bool = False):
        """Extract variable/constant declaration."""
        kind = "let"  # let, const, var
        
        for child in node.children:
            if child.type in ['let', 'const', 'var']:
                kind = child.type
            elif child.type == 'variable_declarator':
                name_node = None
                type_node = None
                value_node = None
                
                for declarator_child in child.children:
                    if declarator_child.type == 'identifier':
                        name_node = declarator_child
                    elif declarator_child.type == 'type_annotation' and self.is_typescript:
                        type_node = declarator_child
                    elif declarator_child.type != '=':
                        value_node = declarator_child
                
                if name_node:
                    var_info = {
                        "name": self.get_node_text(name_node, source),
                        "kind": kind,
                        "type": self.get_node_text(type_node, source) if type_node else None,
                        "value": self.get_node_text(value_node, source) if value_node else None,
                        "exported": is_exported,
                        "lineno": node.start_point[0] + 1
                    }
                    
                    api["variables"].append(var_info)
    
    def _extract_import(self, node: Node, source: str, api: Dict):
        """Extract import statement."""
        import_text = self.get_node_text(node, source)
        api["imports"].append({
            "statement": import_text,
            "lineno": node.start_point[0] + 1
        })
    
    def _extract_parameters(self, params_node: Node, source: str) -> List[Dict]:
        """Extract function parameters."""
        params = []
        
        if params_node:
            for child in params_node.children:
                if child.type in ['required_parameter', 'optional_parameter', 'identifier']:
                    param_name = None
                    param_type = None
                    default_value = None
                    
                    if child.type == 'identifier':
                        param_name = self.get_node_text(child, source)
                    else:
                        for param_child in child.children:
                            if param_child.type == 'identifier':
                                param_name = self.get_node_text(param_child, source)
                            elif param_child.type == 'type_annotation':
                                param_type = self.get_node_text(param_child, source)
                            elif param_child.type not in ['=', ',', '(', ')']:
                                default_value = self.get_node_text(param_child, source)
                    
                    if param_name:
                        params.append({
                            "name": param_name,
                            "type": param_type,
                            "default": default_value
                        })
        
        return params


class GoParser(LanguageParser):
    """Parser for Go files."""
    
    def __init__(self):
        super().__init__('go')
    
    def extract_api(self, root: Node, source: str) -> Dict[str, Any]:
        """Extract Go API information."""
        api = {
            "package": None,
            "imports": [],
            "structs": [],
            "interfaces": [],
            "functions": [],
            "methods": [],
            "constants": [],
            "variables": [],
            "types": []
        }
        
        for node in root.children:
            if node.type == 'package_clause':
                api["package"] = self._extract_package(node, source)
            elif node.type == 'import_declaration':
                self._extract_imports(node, source, api)
            elif node.type == 'function_declaration':
                self._extract_function(node, source, api)
            elif node.type == 'method_declaration':
                self._extract_method(node, source, api)
            elif node.type == 'type_declaration':
                self._extract_type(node, source, api)
            elif node.type in ['const_declaration', 'var_declaration']:
                self._extract_variable(node, source, api)
        
        return api
    
    def _extract_package(self, node: Node, source: str) -> str:
        """Extract package name."""
        for child in node.children:
            if child.type == 'package_identifier':
                return self.get_node_text(child, source)
        return "unknown"
    
    def _extract_imports(self, node: Node, source: str, api: Dict):
        """Extract import statements."""
        for child in node.children:
            if child.type == 'import_spec_list':
                for spec in child.children:
                    if spec.type == 'import_spec':
                        import_path = None
                        alias = None
                        
                        for spec_child in spec.children:
                            if spec_child.type == 'interpreted_string_literal':
                                import_path = self.get_node_text(spec_child, source).strip('"')
                            elif spec_child.type == 'package_identifier':
                                alias = self.get_node_text(spec_child, source)
                        
                        if import_path:
                            api["imports"].append({
                                "path": import_path,
                                "alias": alias
                            })
    
    def _extract_function(self, node: Node, source: str, api: Dict):
        """Extract function declaration."""
        name = None
        params = []
        returns = []
        receiver = None
        
        for child in node.children:
            if child.type == 'identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'parameter_list':
                params = self._extract_parameters(child, source)
            elif child.type == 'result':
                returns = self._extract_returns(child, source)
        
        if name:
            func_info = {
                "name": name,
                "docstring": self.clean_comment(self.get_comment_before(node, source)),
                "params": params,
                "returns": returns,
                "exported": name[0].isupper() if name else False,
                "lineno": node.start_point[0] + 1
            }
            
            api["functions"].append(func_info)
    
    def _extract_method(self, node: Node, source: str, api: Dict):
        """Extract method declaration."""
        name = None
        params = []
        returns = []
        receiver = None
        
        for child in node.children:
            if child.type == 'field_identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'parameter_list':
                if not receiver:  # First parameter list is the receiver
                    receiver = self._extract_receiver(child, source)
                else:
                    params = self._extract_parameters(child, source)
            elif child.type == 'result':
                returns = self._extract_returns(child, source)
        
        if name and receiver:
            method_info = {
                "name": name,
                "receiver": receiver,
                "docstring": self.clean_comment(self.get_comment_before(node, source)),
                "params": params,
                "returns": returns,
                "exported": name[0].isupper() if name else False,
                "lineno": node.start_point[0] + 1
            }
            
            api["methods"].append(method_info)
    
    def _extract_type(self, node: Node, source: str, api: Dict):
        """Extract type declaration (struct, interface, alias)."""
        for spec in node.children:
            if spec.type == 'type_spec':
                name = None
                type_def = None
                
                for child in spec.children:
                    if child.type == 'type_identifier':
                        name = self.get_node_text(child, source)
                    elif child.type == 'struct_type':
                        type_def = self._extract_struct(child, source)
                        type_def["name"] = name
                        type_def["exported"] = name[0].isupper() if name else False
                        api["structs"].append(type_def)
                    elif child.type == 'interface_type':
                        type_def = self._extract_interface(child, source)
                        type_def["name"] = name
                        type_def["exported"] = name[0].isupper() if name else False
                        api["interfaces"].append(type_def)
                    else:
                        # Type alias
                        if name:
                            api["types"].append({
                                "name": name,
                                "type": self.get_node_text(child, source),
                                "exported": name[0].isupper()
                            })
    
    def _extract_struct(self, node: Node, source: str) -> Dict:
        """Extract struct fields."""
        fields = []
        
        for child in node.children:
            if child.type == 'field_declaration_list':
                for field_node in child.children:
                    if field_node.type == 'field_declaration':
                        field_names = []
                        field_type = None
                        field_tag = None
                        
                        for field_child in field_node.children:
                            if field_child.type == 'field_identifier':
                                field_names.append(self.get_node_text(field_child, source))
                            elif field_child.type in ['type_identifier', 'pointer_type', 'slice_type']:
                                field_type = self.get_node_text(field_child, source)
                            elif field_child.type == 'raw_string_literal':
                                field_tag = self.get_node_text(field_child, source)
                        
                        for fname in field_names:
                            fields.append({
                                "name": fname,
                                "type": field_type,
                                "tag": field_tag,
                                "exported": fname[0].isupper() if fname else False
                            })
        
        return {
            "fields": fields,
            "docstring": self.clean_comment(self.get_comment_before(node, source))
        }
    
    def _extract_interface(self, node: Node, source: str) -> Dict:
        """Extract interface methods."""
        methods = []
        
        for child in node.children:
            if child.type == 'method_spec':
                method_name = None
                params = []
                returns = []
                
                for method_child in child.children:
                    if method_child.type == 'field_identifier':
                        method_name = self.get_node_text(method_child, source)
                    elif method_child.type == 'parameter_list':
                        params = self._extract_parameters(method_child, source)
                    elif method_child.type == 'result':
                        returns = self._extract_returns(method_child, source)
                
                if method_name:
                    methods.append({
                        "name": method_name,
                        "params": params,
                        "returns": returns
                    })
        
        return {
            "methods": methods,
            "docstring": self.clean_comment(self.get_comment_before(node, source))
        }
    
    def _extract_variable(self, node: Node, source: str, api: Dict):
        """Extract const or var declaration."""
        is_const = node.type == 'const_declaration'
        
        for spec in node.children:
            if spec.type in ['const_spec', 'var_spec']:
                names = []
                var_type = None
                values = []
                
                for child in spec.children:
                    if child.type == 'identifier':
                        names.append(self.get_node_text(child, source))
                    elif child.type in ['type_identifier', 'pointer_type', 'slice_type']:
                        var_type = self.get_node_text(child, source)
                    elif child.type == 'expression_list':
                        for expr in child.children:
                            if expr.type != ',':
                                values.append(self.get_node_text(expr, source))
                
                for i, name in enumerate(names):
                    var_info = {
                        "name": name,
                        "type": var_type,
                        "value": values[i] if i < len(values) else None,
                        "is_const": is_const,
                        "exported": name[0].isupper() if name else False,
                        "lineno": node.start_point[0] + 1
                    }
                    
                    if is_const:
                        api["constants"].append(var_info)
                    else:
                        api["variables"].append(var_info)
    
    def _extract_parameters(self, node: Node, source: str) -> List[Dict]:
        """Extract function parameters."""
        params = []
        
        for child in node.children:
            if child.type == 'parameter_declaration':
                param_names = []
                param_type = None
                
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_names.append(self.get_node_text(param_child, source))
                    elif param_child.type != ',':
                        param_type = self.get_node_text(param_child, source)
                
                for pname in param_names:
                    params.append({
                        "name": pname,
                        "type": param_type
                    })
        
        return params
    
    def _extract_receiver(self, node: Node, source: str) -> Dict:
        """Extract method receiver."""
        for child in node.children:
            if child.type == 'parameter_declaration':
                name = None
                receiver_type = None
                
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        name = self.get_node_text(param_child, source)
                    elif param_child.type != ',':
                        receiver_type = self.get_node_text(param_child, source)
                
                return {
                    "name": name,
                    "type": receiver_type
                }
        
        return None
    
    def _extract_returns(self, node: Node, source: str) -> List[Dict]:
        """Extract function return types."""
        returns = []
        
        if node.type == 'result':
            for child in node.children:
                if child.type == 'parameter_list':
                    returns = self._extract_parameters(child, source)
                elif child.type not in ['(', ')', ',']:
                    returns.append({
                        "type": self.get_node_text(child, source)
                    })
        
        return returns


class RustParser(LanguageParser):
    """Parser for Rust files."""
    
    def __init__(self):
        super().__init__('rust')
    
    def extract_api(self, root: Node, source: str) -> Dict[str, Any]:
        """Extract Rust API information."""
        api = {
            "modules": [],
            "structs": [],
            "enums": [],
            "traits": [],
            "functions": [],
            "impl_blocks": [],
            "constants": [],
            "statics": [],
            "type_aliases": [],
            "uses": []
        }
        
        for node in root.children:
            self._extract_item(node, source, api)
        
        return api
    
    def _extract_item(self, node: Node, source: str, api: Dict):
        """Extract various Rust items."""
        if node.type == 'use_declaration':
            self._extract_use(node, source, api)
        elif node.type == 'function_item':
            self._extract_function(node, source, api)
        elif node.type == 'struct_item':
            self._extract_struct(node, source, api)
        elif node.type == 'enum_item':
            self._extract_enum(node, source, api)
        elif node.type == 'trait_item':
            self._extract_trait(node, source, api)
        elif node.type == 'impl_item':
            self._extract_impl(node, source, api)
        elif node.type == 'const_item':
            self._extract_const(node, source, api)
        elif node.type == 'static_item':
            self._extract_static(node, source, api)
        elif node.type == 'type_item':
            self._extract_type_alias(node, source, api)
        elif node.type == 'mod_item':
            self._extract_module(node, source, api)
        else:
            # Recurse for other nodes
            for child in node.children:
                self._extract_item(child, source, api)
    
    def _extract_function(self, node: Node, source: str, api: Dict):
        """Extract function declaration."""
        name = None
        params = []
        return_type = None
        is_async = False
        is_pub = False
        
        for child in node.children:
            if child.type == 'identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
            elif child.type == 'parameters':
                params = self._extract_parameters(child, source)
            elif child.type == 'type':
                return_type = self.get_node_text(child, source)
            elif child.type == 'async':
                is_async = True
        
        if name:
            func_info = {
                "name": name,
                "docstring": self._extract_doc_comment(node, source),
                "params": params,
                "return_type": return_type,
                "is_async": is_async,
                "is_pub": is_pub,
                "lineno": node.start_point[0] + 1
            }
            
            api["functions"].append(func_info)
    
    def _extract_struct(self, node: Node, source: str, api: Dict):
        """Extract struct declaration."""
        name = None
        fields = []
        is_pub = False
        
        for child in node.children:
            if child.type == 'type_identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
            elif child.type == 'field_declaration_list':
                fields = self._extract_fields(child, source)
        
        if name:
            struct_info = {
                "name": name,
                "docstring": self._extract_doc_comment(node, source),
                "fields": fields,
                "is_pub": is_pub,
                "lineno": node.start_point[0] + 1
            }
            
            api["structs"].append(struct_info)
    
    def _extract_enum(self, node: Node, source: str, api: Dict):
        """Extract enum declaration."""
        name = None
        variants = []
        is_pub = False
        
        for child in node.children:
            if child.type == 'type_identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
            elif child.type == 'enum_variant_list':
                for variant_node in child.children:
                    if variant_node.type == 'enum_variant':
                        variant_name = None
                        variant_fields = []
                        
                        for variant_child in variant_node.children:
                            if variant_child.type == 'identifier':
                                variant_name = self.get_node_text(variant_child, source)
                            elif variant_child.type in ['field_declaration_list', 'ordered_field_declaration_list']:
                                variant_fields = self._extract_fields(variant_child, source)
                        
                        if variant_name:
                            variants.append({
                                "name": variant_name,
                                "fields": variant_fields
                            })
        
        if name:
            enum_info = {
                "name": name,
                "docstring": self._extract_doc_comment(node, source),
                "variants": variants,
                "is_pub": is_pub,
                "lineno": node.start_point[0] + 1
            }
            
            api["enums"].append(enum_info)
    
    def _extract_trait(self, node: Node, source: str, api: Dict):
        """Extract trait declaration."""
        name = None
        methods = []
        is_pub = False
        
        for child in node.children:
            if child.type == 'type_identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
            elif child.type == 'declaration_list':
                for item in child.children:
                    if item.type in ['function_signature_item', 'function_item']:
                        method_info = self._extract_trait_method(item, source)
                        if method_info:
                            methods.append(method_info)
        
        if name:
            trait_info = {
                "name": name,
                "docstring": self._extract_doc_comment(node, source),
                "methods": methods,
                "is_pub": is_pub,
                "lineno": node.start_point[0] + 1
            }
            
            api["traits"].append(trait_info)
    
    def _extract_impl(self, node: Node, source: str, api: Dict):
        """Extract impl block."""
        type_name = None
        trait_name = None
        methods = []
        
        for child in node.children:
            if child.type == 'type_identifier':
                if not type_name:
                    type_name = self.get_node_text(child, source)
                else:
                    trait_name = type_name
                    type_name = self.get_node_text(child, source)
            elif child.type == 'declaration_list':
                for item in child.children:
                    if item.type == 'function_item':
                        method_info = self._extract_impl_method(item, source)
                        if method_info:
                            methods.append(method_info)
        
        if type_name:
            impl_info = {
                "type": type_name,
                "trait": trait_name,
                "methods": methods,
                "lineno": node.start_point[0] + 1
            }
            
            api["impl_blocks"].append(impl_info)
    
    def _extract_parameters(self, node: Node, source: str) -> List[Dict]:
        """Extract function parameters."""
        params = []
        
        for child in node.children:
            if child.type == 'parameter':
                param_name = None
                param_type = None
                is_mut = False
                
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_name = self.get_node_text(param_child, source)
                    elif param_child.type == 'mutable_specifier':
                        is_mut = True
                    elif param_child.type not in [':', ',']:
                        param_type = self.get_node_text(param_child, source)
                
                if param_name:
                    params.append({
                        "name": param_name,
                        "type": param_type,
                        "is_mut": is_mut
                    })
            elif child.type == 'self_parameter':
                params.append({
                    "name": "self",
                    "type": self.get_node_text(child, source),
                    "is_mut": '&mut' in self.get_node_text(child, source)
                })
        
        return params
    
    def _extract_fields(self, node: Node, source: str) -> List[Dict]:
        """Extract struct/enum fields."""
        fields = []
        
        for child in node.children:
            if child.type == 'field_declaration':
                field_name = None
                field_type = None
                is_pub = False
                
                for field_child in child.children:
                    if field_child.type == 'field_identifier':
                        field_name = self.get_node_text(field_child, source)
                    elif field_child.type == 'visibility_modifier':
                        is_pub = 'pub' in self.get_node_text(field_child, source)
                    elif field_child.type not in [':', ',']:
                        field_type = self.get_node_text(field_child, source)
                
                if field_name:
                    fields.append({
                        "name": field_name,
                        "type": field_type,
                        "is_pub": is_pub
                    })
        
        return fields
    
    def _extract_doc_comment(self, node: Node, source: str) -> str:
        """Extract Rust doc comments (///)."""
        comments = []
        prev = node.prev_sibling
        
        while prev and prev.type == 'line_comment':
            comment_text = self.get_node_text(prev, source)
            if comment_text.startswith('///'):
                comments.insert(0, comment_text[3:].strip())
            prev = prev.prev_sibling
        
        return '\n'.join(comments) if comments else None
    
    def _extract_trait_method(self, node: Node, source: str) -> Optional[Dict]:
        """Extract trait method signature."""
        name = None
        params = []
        return_type = None
        
        for child in node.children:
            if child.type == 'identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'parameters':
                params = self._extract_parameters(child, source)
            elif child.type == 'type':
                return_type = self.get_node_text(child, source)
        
        if name:
            return {
                "name": name,
                "params": params,
                "return_type": return_type
            }
        
        return None
    
    def _extract_impl_method(self, node: Node, source: str) -> Optional[Dict]:
        """Extract impl block method."""
        name = None
        params = []
        return_type = None
        is_pub = False
        
        for child in node.children:
            if child.type == 'identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
            elif child.type == 'parameters':
                params = self._extract_parameters(child, source)
            elif child.type == 'type':
                return_type = self.get_node_text(child, source)
        
        if name:
            return {
                "name": name,
                "docstring": self._extract_doc_comment(node, source),
                "params": params,
                "return_type": return_type,
                "is_pub": is_pub
            }
        
        return None
    
    def _extract_const(self, node: Node, source: str, api: Dict):
        """Extract const item."""
        name = None
        const_type = None
        value = None
        is_pub = False
        
        for child in node.children:
            if child.type == 'identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
            elif child.type == 'type':
                const_type = self.get_node_text(child, source)
            elif child.type not in ['const', ':', '=', ';']:
                value = self.get_node_text(child, source)
        
        if name:
            api["constants"].append({
                "name": name,
                "type": const_type,
                "value": value,
                "is_pub": is_pub,
                "lineno": node.start_point[0] + 1
            })
    
    def _extract_static(self, node: Node, source: str, api: Dict):
        """Extract static item."""
        name = None
        static_type = None
        value = None
        is_pub = False
        is_mut = False
        
        for child in node.children:
            if child.type == 'identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
            elif child.type == 'mutable_specifier':
                is_mut = True
            elif child.type == 'type':
                static_type = self.get_node_text(child, source)
            elif child.type not in ['static', ':', '=', ';']:
                value = self.get_node_text(child, source)
        
        if name:
            api["statics"].append({
                "name": name,
                "type": static_type,
                "value": value,
                "is_pub": is_pub,
                "is_mut": is_mut,
                "lineno": node.start_point[0] + 1
            })
    
    def _extract_type_alias(self, node: Node, source: str, api: Dict):
        """Extract type alias."""
        name = None
        alias_type = None
        is_pub = False
        
        for child in node.children:
            if child.type == 'type_identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
            elif child.type not in ['type', '=', ';']:
                alias_type = self.get_node_text(child, source)
        
        if name:
            api["type_aliases"].append({
                "name": name,
                "type": alias_type,
                "is_pub": is_pub,
                "lineno": node.start_point[0] + 1
            })
    
    def _extract_use(self, node: Node, source: str, api: Dict):
        """Extract use statement."""
        use_text = self.get_node_text(node, source)
        api["uses"].append({
            "statement": use_text,
            "lineno": node.start_point[0] + 1
        })
    
    def _extract_module(self, node: Node, source: str, api: Dict):
        """Extract module declaration."""
        name = None
        is_pub = False
        
        for child in node.children:
            if child.type == 'identifier':
                name = self.get_node_text(child, source)
            elif child.type == 'visibility_modifier':
                is_pub = 'pub' in self.get_node_text(child, source)
        
        if name:
            api["modules"].append({
                "name": name,
                "is_pub": is_pub,
                "lineno": node.start_point[0] + 1
            })


# Language file extensions mapping
LANGUAGE_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.cs': 'c_sharp',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.r': 'r',
    '.lua': 'lua',
    '.dart': 'dart',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.jl': 'julia',
    '.ml': 'ocaml',
    '.mli': 'ocaml',
    '.hs': 'haskell',
    '.elm': 'elm',
    '.clj': 'clojure',
    '.cljs': 'clojure',
    '.erl': 'erlang',
    '.hrl': 'erlang',
}


def get_language_parser(file_path: Path) -> Optional[LanguageParser]:
    """Get the appropriate parser for a file based on its extension."""
    ext = file_path.suffix.lower()
    lang = LANGUAGE_EXTENSIONS.get(ext)
    
    if not lang:
        return None
    
    # Use specialized parsers where available
    if lang == 'javascript':
        return JavaScriptParser(is_typescript=False)
    elif lang == 'typescript':
        return JavaScriptParser(is_typescript=True)
    elif lang == 'go':
        return GoParser()
    elif lang == 'rust':
        return RustParser()
    elif lang == 'python':
        # Import the existing Python scanner
        from .scanner import scan_python_file
        return None  # Will use the existing Python scanner
    else:
        # Generic parser for other languages
        try:
            return LanguageParser(lang)
        except:
            return None


def scan_file(file_path: Path) -> Dict[str, Any]:
    """Scan a single file using the appropriate language parser."""
    # Check if it's a Python file
    if file_path.suffix.lower() == '.py':
        from .scanner import scan_python_file
        return scan_python_file(file_path)
    
    # Get parser for other languages
    parser = get_language_parser(file_path)
    if parser:
        return parser.parse_file(file_path)
    
    # Unsupported file type
    return {
        "path": str(file_path),
        "error": f"Unsupported file type: {file_path.suffix}"
    }