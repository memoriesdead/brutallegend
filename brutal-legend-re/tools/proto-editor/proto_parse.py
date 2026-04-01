#!/usr/bin/env python3
"""
Prototype Parser for Brutal Legend

Parses the all.proto file (custom text DSL) and provides utilities for
querying, validating, and converting prototype definitions.

Format:
    Prototype <Name> : <Parent> { <Body> };

Body can contain:
    Add <ComponentName> { <properties> };
    Override { Entity:CoComponent:Property = value; };
    Apply <Condition> { <directives> };
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class PropertyValue:
    """Represents a property value of various types."""
    raw: str

    def get_bool(self) -> Optional[bool]:
        if self.raw.lower() == 'true':
            return True
        if self.raw.lower() == 'false':
            return False
        return None

    def get_int(self) -> Optional[int]:
        try:
            return int(self.raw)
        except ValueError:
            return None

    def get_float(self) -> Optional[float]:
        try:
            return float(self.raw)
        except ValueError:
            return None

    def is_vector(self) -> bool:
        return self.raw.startswith('<') and self.raw.endswith('>')

    def is_resource_ref(self) -> bool:
        return self.raw.startswith('@')

    def is_array(self) -> bool:
        return self.raw == '[]'

    def get_vector_components(self) -> List[float]:
        """Parse <x,y,z> or <r,g,b,a> into floats."""
        if not self.is_vector():
            return []
        inner = self.raw[1:-1]
        try:
            return [float(x.strip()) for x in inner.split(',')]
        except ValueError:
            return []


@dataclass
class Property:
    """A property assignment: Name = value;"""
    name: str
    value: PropertyValue


@dataclass
class ComponentAdd:
    """An Add directive: Add <ComponentName> { <properties> };"""
    component_name: str
    properties: List[Property]


@dataclass
class PropertyOverride:
    """An Override directive: Override { Entity:CoComponent:Property = value; };"""
    path: str  # e.g., "Entity:CoRenderMesh:MeshSet"
    value: PropertyValue


@dataclass
class Directive:
    """Base class for directives."""
    pass


@dataclass
class AddDirective(Directive):
    component_name: str
    properties: List[Property]


@dataclass
class OverrideDirective(Directive):
    overrides: List[PropertyOverride]


@dataclass
class Prototype:
    """A complete prototype definition."""
    name: str
    parent: str
    directives: List[Directive]
    line_number: int
    raw_text: str = ""


class ProtoParser:
    """Parser for Brutal Legend prototype definitions."""

    # Regex patterns
    PROTOTYPE_PATTERN = re.compile(
        r'Prototype\s+(\w+)\s*:\s*(\w+)\s*\{',
        re.MULTILINE
    )

    # Tokenize the file content
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.content = ""
        self.prototypes: Dict[str, Prototype] = {}
        self.errors: List[str] = []

    def load(self) -> bool:
        """Load and parse the proto file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                self.content = f.read()
        except Exception as e:
            self.errors.append(f"Failed to load file: {e}")
            return False

        self._parse_prototypes()
        return len(self.errors) == 0

    def _find_matching_brace(self, start: int) -> int:
        """Find the matching closing brace for an opening brace at position start."""
        depth = 1
        i = start + 1
        in_string = False
        while i < len(self.content) and depth > 0:
            c = self.content[i]
            if in_string:
                if c == '\\':
                    i += 2  # Skip escaped character
                elif c == '"':
                    in_string = False  # End of string
                i += 1
            else:
                if c == '"':
                    in_string = True  # Start of string
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                i += 1
        return i - 1 if depth == 0 else -1

    def _parse_body(self, body_start: int, body_end: int) -> List[Directive]:
        """Parse the body of a prototype (between { and })."""
        directives = []
        if body_end < body_start:
            self.errors.append(f"Invalid body range: {body_start}-{body_end}")
            return directives
        if body_start < 0 or body_end > len(self.content):
            self.errors.append(f"Body outside content bounds: {body_start}-{body_end} (len: {len(self.content)})")
            return directives
        if body_start == body_end:
            return directives  # Empty body is valid
        body = self.content[body_start:body_end]

        pos = 0
        body_len = len(body)

        while pos < body_len:
            # Skip whitespace
            while pos < body_len and body[pos] in ' \t\n\r':
                pos += 1
            if pos >= body_len:
                break

            remaining = body[pos:]

            # Check for Add directive
            if remaining.startswith('Add '):
                # Find component name
                name_end = pos + 4  # after "Add "
                while name_end < body_len and body[name_end] not in ' \t\n\r{':
                    name_end += 1
                comp_name = body[pos+4:name_end].strip()

                # Skip whitespace
                while name_end < body_len and body[name_end] in ' \t':
                    name_end += 1

                if name_end < body_len and body[name_end] == '{':
                    # Find matching closing brace
                    close_abs = self._find_matching_brace(body_start + name_end)
                    if close_abs != -1:
                        prop_text = body[name_end+1:close_abs - body_start]
                        properties = self._parse_properties(prop_text)
                        directives.append(AddDirective(comp_name, properties))
                        pos = (close_abs - body_start) + 1
                        continue

                # If no brace, skip to semicolon
                semi = body.find(';', pos)
                pos = semi + 1 if semi != -1 else body_len
                continue

            # Check for Override directive
            if remaining.startswith('Override '):
                # Find the opening brace
                brace_rel = body.find('{', pos)
                if brace_rel != -1:
                    close_abs = self._find_matching_brace(body_start + brace_rel)
                    if close_abs != -1:
                        override_text = body[brace_rel+1:close_abs - body_start]
                        overrides = self._parse_override_properties(override_text)
                        directives.append(OverrideDirective(overrides))
                        pos = (close_abs - body_start) + 1
                        continue

                # If no brace, skip to semicolon
                semi = body.find(';', pos)
                pos = semi + 1 if semi != -1 else body_len
                continue

            # Check for Apply directive (skip for now - complex)
            if remaining.startswith('Apply '):
                # Find opening brace
                brace_rel = body.find('{', pos)
                if brace_rel != -1:
                    close_abs = self._find_matching_brace(body_start + brace_rel)
                    if close_abs != -1:
                        pos = (close_abs - body_start) + 1
                        continue
                # Skip to semicolon
                semi = body.find(';', pos)
                pos = semi + 1 if semi != -1 else body_len
                continue

            # Skip unknown content (any word followed by potential semicolon)
            word_end = pos
            while word_end < body_len and body[word_end] not in ' \t\n\r;':
                word_end += 1
            if word_end < body_len and body[word_end] == ';':
                pos = word_end + 1
            else:
                pos = word_end + 1

        return directives

    def _parse_properties(self, text: str) -> List[Property]:
        """Parse property assignments from component body text."""
        properties = []
        # Pattern: Name = value;
        prop_pattern = re.compile(r'(\w+)\s*=\s*([^;]+);', re.MULTILINE)
        for match in prop_pattern.finditer(text):
            prop_name = match.group(1)
            prop_val = match.group(2).strip()
            properties.append(Property(prop_name, PropertyValue(prop_val)))
        return properties

    def _parse_override_properties(self, text: str) -> List[PropertyOverride]:
        """Parse Override property paths from text."""
        overrides = []
        # Pattern: [Entity:]CoComponent:Property = value;
        # The Entity prefix is optional (sometimes it's just CoComponent:Property)
        # Value can contain @, /, ., and other chars but ends with ;
        path_pattern = re.compile(r'(?:(\w+):)?(\w+):(\w+)\s*=\s*([^;]+?)\s*;', re.MULTILINE | re.DOTALL)
        for match in path_pattern.finditer(text):
            entity = match.group(1)  # Optional Entity prefix
            component = match.group(2)
            prop_name = match.group(3)
            value = match.group(4).strip()

            # Build path: if entity exists use Entity:Component:Property, else Component:Property
            if entity:
                path = f"{entity}:{component}:{prop_name}"
            else:
                path = f"{component}:{prop_name}"
            overrides.append(PropertyOverride(path, PropertyValue(value)))
        return overrides

    def _parse_prototypes(self):
        """Find and parse all prototype definitions."""
        for match in self.PROTOTYPE_PATTERN.finditer(self.content):
            name = match.group(1)
            parent = match.group(2)
            decl_end = match.end()

            # The regex ends with \{, so match.end() is AFTER the opening brace
            # We need the position OF the opening brace
            first_brace = decl_end - 1

            # Now find its matching closing brace (handles nested braces)
            brace_end = self._find_matching_brace(first_brace)

            if brace_end == -1:
                self.errors.append(f"Could not find matching brace for prototype '{name}' at position {first_brace}")
                continue

            # Extract raw text for debugging (include the closing brace)
            raw_text = self.content[match.start():brace_end+1]

            # Count newlines for line number
            line_number = self.content[:match.start()].count('\n') + 1

            # Parse directives (body is content between first { and matching }, exclusive)
            body_content_start = first_brace + 1
            body_content_end = brace_end
            if body_content_end < body_content_start:
                self.errors.append(f"Invalid body range for prototype '{name}': {body_content_start}-{body_content_end}")
                continue
            # Empty body is valid - just no directives
            directives = self._parse_body(body_content_start, body_content_end)

            self.prototypes[name] = Prototype(
                name=name,
                parent=parent,
                directives=directives,
                line_number=line_number,
                raw_text=raw_text
            )

    def get_prototype(self, name: str) -> Optional[Prototype]:
        """Get a prototype by name."""
        return self.prototypes.get(name)

    def get_children(self, parent_name: str) -> List[Prototype]:
        """Get all prototypes that inherit from a given parent."""
        return [p for p in self.prototypes.values() if p.parent == parent_name]

    def get_proto_tree(self, root: str = "BaseEntity") -> Dict[str, Any]:
        """Build a hierarchical tree of prototype inheritance."""
        def build_node(name: str) -> Dict[str, Any]:
            proto = self.prototypes.get(name)
            if not proto:
                return {"name": name, "error": "not found"}
            children = self.get_children(name)
            return {
                "name": proto.name,
                "parent": proto.parent,
                "directive_count": len(proto.directives),
                "children": [build_node(c.name) for c in children]
            }
        return build_node(root)

    def find_by_component(self, component_name: str) -> List[Prototype]:
        """Find all prototypes that add a specific component."""
        results = []
        for proto in self.prototypes.values():
            for directive in proto.directives:
                if isinstance(directive, AddDirective) and directive.component_name == component_name:
                    results.append(proto)
                    break
        return results

    def find_by_property(self, prop_name: str, value: Optional[str] = None) -> List[Prototype]:
        """Find prototypes by property name, optionally with specific value."""
        results = []
        for proto in self.prototypes.values():
            for directive in proto.directives:
                if isinstance(directive, AddDirective):
                    for prop in directive.properties:
                        if prop.name == prop_name:
                            if value is None or prop.value.raw == value:
                                results.append(proto)
                                break
        return results

    def validate(self) -> List[str]:
        """Validate the prototype hierarchy."""
        errors = []
        roots = set()

        for name, proto in self.prototypes.items():
            # Check parent exists
            if proto.parent != "BaseEntity" and proto.parent not in self.prototypes:
                errors.append(f"Prototype '{name}' has unknown parent '{proto.parent}'")

        # Check for circular inheritance (shouldn't be possible with single inheritance)
        return errors

    def to_json(self, proto_name: str) -> Optional[str]:
        """Export a single prototype as JSON."""
        proto = self.prototypes.get(proto_name)
        if not proto:
            return None

        def directive_to_dict(d):
            if isinstance(d, AddDirective):
                return {
                    "type": "Add",
                    "component": d.component_name,
                    "properties": {p.name: p.value.raw for p in d.properties}
                }
            elif isinstance(d, OverrideDirective):
                return {
                    "type": "Override",
                    "overrides": [{ "path": o.path, "value": o.value.raw } for o in d.overrides]
                }
            return None

        data = {
            "name": proto.name,
            "parent": proto.parent,
            "directives": [d for d in (directive_to_dict(d) for d in proto.directives) if d],
            "line_number": proto.line_number
        }
        return json.dumps(data, indent=2)

    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        component_counts: Dict[str, int] = {}
        parent_counts: Dict[str, int] = {}

        for proto in self.prototypes.values():
            parent_counts[proto.parent] = parent_counts.get(proto.parent, 0) + 1
            for directive in proto.directives:
                if isinstance(directive, AddDirective):
                    component_counts[directive.component_name] = component_counts.get(directive.component_name, 0) + 1

        return {
            "total_prototypes": len(self.prototypes),
            "parent_counts": parent_counts,
            "component_counts": component_counts,
        }


def main():
    if len(sys.argv) < 2:
        # Try default location
        default_paths = [
            Path("extracted/00Startup/all.proto"),
            Path("../extracted/00Startup/all.proto"),
            Path("brutal-legend-re/extracted/00Startup/all.proto"),
        ]
        filepath = None
        for p in default_paths:
            if p.exists():
                filepath = p
                break

        if filepath is None:
            print("Usage: python proto_parse.py <all.proto> [command] [args]")
            print("Commands:")
            print("  list                    - List all prototypes")
            print("  tree [root]             - Show inheritance tree")
            print("  get <name>              - Get single prototype as JSON")
            print("  find-component <name>   - Find prototypes by component")
            print("  find-property <name> [val] - Find prototypes by property")
            print("  summary                 - Show statistics")
            sys.exit(1)
    else:
        filepath = Path(sys.argv[1])

    cmd = sys.argv[2] if len(sys.argv) > 2 else "summary"

    parser = ProtoParser(str(filepath))
    if not parser.load():
        print(f"Failed to parse: {', '.join(parser.errors)}")
        sys.exit(1)

    if cmd == "summary":
        s = parser.summary()
        print(f"Total prototypes: {s['total_prototypes']}")
        print(f"\nTop-level parents:")
        for parent, count in sorted(s['parent_counts'].items(), key=lambda x: -x[1])[:20]:
            print(f"  {parent}: {count}")
        print(f"\nMost common components:")
        for comp, count in sorted(s['component_counts'].items(), key=lambda x: -x[1])[:15]:
            print(f"  {comp}: {count}")

    elif cmd == "list":
        for name in sorted(parser.prototypes.keys()):
            proto = parser.prototypes[name]
            print(f"{proto.name} : {proto.parent}")

    elif cmd == "tree":
        root = sys.argv[3] if len(sys.argv) > 3 else "BaseEntity"
        tree = parser.get_proto_tree(root)
        print(json.dumps(tree, indent=2))

    elif cmd == "get":
        if len(sys.argv) < 4:
            print("Usage: proto_parse.py get <name>")
            sys.exit(1)
        name = sys.argv[3]
        json_out = parser.to_json(name)
        if json_out:
            print(json_out)
        else:
            print(f"Prototype '{name}' not found")

    elif cmd == "find-component":
        if len(sys.argv) < 4:
            print("Usage: proto_parse.py find-component <name>")
            sys.exit(1)
        comp = sys.argv[3]
        results = parser.find_by_component(comp)
        print(f"Found {len(results)} prototypes with component '{comp}':")
        for p in results[:20]:
            print(f"  {p.name}")
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")

    elif cmd == "find-property":
        if len(sys.argv) < 4:
            print("Usage: proto_parse.py find-property <name> [value]")
            sys.exit(1)
        prop = sys.argv[3]
        val = sys.argv[4] if len(sys.argv) > 4 else None
        results = parser.find_by_property(prop, val)
        print(f"Found {len(results)} prototypes with property '{prop}'" +
              (f" = '{val}'" if val else ""))
        for p in results[:20]:
            print(f"  {p.name}")
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")

    elif cmd == "validate":
        errors = parser.validate()
        if errors:
            print(f"Found {len(errors)} validation errors:")
            for e in errors:
                print(f"  {e}")
        else:
            print("No validation errors found")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()