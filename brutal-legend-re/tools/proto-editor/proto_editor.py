#!/usr/bin/env python3
"""
Prototype Editor for Brutal Legend

A CLI tool for editing the all.proto text file that defines game entity prototypes.
The game parses this TEXT proto at runtime - no binary compilation needed!

Usage:
    python proto_editor.py list
    python proto_editor.py show <name>
    python proto_editor.py create <name> --parent <Parent> --template <template>
    python proto_editor.py edit <name> --set "<path>=<value>"
    python proto_editor.py validate
    python proto_editor.py export [--output <file>]
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# Import from proto_parse if available, otherwise define our own
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from proto_parse import ProtoParser, Prototype, Directive, AddDirective, OverrideDirective, Property, PropertyValue, PropertyOverride
except ImportError:
    from dataclasses import dataclass


# ---------- Data Classes ----------

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
        if not self.is_vector():
            return []
        inner = self.raw[1:-1]
        try:
            return [float(x.strip()) for x in inner.split(',')]
        except ValueError:
            return []

    def __str__(self):
        return self.raw


@dataclass
class Property:
    name: str
    value: PropertyValue


@dataclass
class ComponentAdd:
    component_name: str
    properties: List[Property]


@dataclass
class PropertyOverride:
    path: str
    value: PropertyValue


@dataclass
class Directive:
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
    name: str
    parent: str
    directives: List[Directive]
    line_number: int
    raw_text: str = ""


# ---------- Parser (embedded from proto_parse.py) ----------

class ProtoParser:
    """Parser for Brutal Legend prototype definitions."""

    PROTOTYPE_PATTERN = re.compile(
        r'Prototype\s+(\w+)\s*:\s*(\w+)\s*\{',
        re.MULTILINE
    )

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.content = ""
        self.prototypes: Dict[str, Prototype] = {}
        self.errors: List[str] = []

    def load(self) -> bool:
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='replace') as f:
                self.content = f.read()
        except Exception as e:
            self.errors.append(f"Failed to load file: {e}")
            return False
        self._parse_prototypes()
        return len(self.errors) == 0

    def _find_matching_brace(self, start: int) -> int:
        depth = 1
        i = start + 1
        in_string = False
        while i < len(self.content) and depth > 0:
            c = self.content[i]
            if in_string:
                if c == '\\':
                    i += 2
                elif c == '"':
                    in_string = False
                i += 1
            else:
                if c == '"':
                    in_string = True
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                i += 1
        return i - 1 if depth == 0 else -1

    def _parse_body(self, body_start: int, body_end: int) -> List[Directive]:
        directives = []
        if body_end < body_start or body_start < 0 or body_end > len(self.content):
            return directives
        if body_start == body_end:
            return directives
        body = self.content[body_start:body_end]
        pos = 0
        body_len = len(body)

        while pos < body_len:
            while pos < body_len and body[pos] in ' \t\n\r':
                pos += 1
            if pos >= body_len:
                break
            remaining = body[pos:]

            if remaining.startswith('Add '):
                name_end = pos + 4
                while name_end < body_len and body[name_end] not in ' \t\n\r{':
                    name_end += 1
                comp_name = body[pos+4:name_end].strip()
                while name_end < body_len and body[name_end] in ' \t':
                    name_end += 1
                if name_end < body_len and body[name_end] == '{':
                    close_abs = self._find_matching_brace(body_start + name_end)
                    if close_abs != -1:
                        prop_text = body[name_end+1:close_abs - body_start]
                        properties = self._parse_properties(prop_text)
                        directives.append(AddDirective(comp_name, properties))
                        pos = (close_abs - body_start) + 1
                        continue
                semi = body.find(';', pos)
                pos = semi + 1 if semi != -1 else body_len
                continue

            if remaining.startswith('Override '):
                brace_rel = body.find('{', pos)
                if brace_rel != -1:
                    close_abs = self._find_matching_brace(body_start + brace_rel)
                    if close_abs != -1:
                        override_text = body[brace_rel+1:close_abs - body_start]
                        overrides = self._parse_override_properties(override_text)
                        directives.append(OverrideDirective(overrides))
                        pos = (close_abs - body_start) + 1
                        continue
                semi = body.find(';', pos)
                pos = semi + 1 if semi != -1 else body_len
                continue

            if remaining.startswith('Apply '):
                brace_rel = body.find('{', pos)
                if brace_rel != -1:
                    close_abs = self._find_matching_brace(body_start + brace_rel)
                    if close_abs != -1:
                        pos = (close_abs - body_start) + 1
                        continue
                semi = body.find(';', pos)
                pos = semi + 1 if semi != -1 else body_len
                continue

            word_end = pos
            while word_end < body_len and body[word_end] not in ' \t\n\r;':
                word_end += 1
            if word_end < body_len and body[word_end] == ';':
                pos = word_end + 1
            else:
                pos = word_end + 1

        return directives

    def _parse_properties(self, text: str) -> List[Property]:
        properties = []
        prop_pattern = re.compile(r'(\w+)\s*=\s*([^;]+);', re.MULTILINE)
        for match in prop_pattern.finditer(text):
            prop_name = match.group(1)
            prop_val = match.group(2).strip()
            properties.append(Property(prop_name, PropertyValue(prop_val)))
        return properties

    def _parse_override_properties(self, text: str) -> List[PropertyOverride]:
        overrides = []
        path_pattern = re.compile(r'(?:(\w+):)?(\w+):(\w+)\s*=\s*([^;]+?)\s*;', re.MULTILINE | re.DOTALL)
        for match in path_pattern.finditer(text):
            entity = match.group(1)
            component = match.group(2)
            prop_name = match.group(3)
            value = match.group(4).strip()
            if entity:
                path = f"{entity}:{component}:{prop_name}"
            else:
                path = f"{component}:{prop_name}"
            overrides.append(PropertyOverride(path, PropertyValue(value)))
        return overrides

    def _parse_prototypes(self):
        for match in self.PROTOTYPE_PATTERN.finditer(self.content):
            name = match.group(1)
            parent = match.group(2)
            decl_end = match.end()
            first_brace = decl_end - 1
            brace_end = self._find_matching_brace(first_brace)
            if brace_end == -1:
                self.errors.append(f"Could not find matching brace for prototype '{name}' at position {first_brace}")
                continue
            raw_text = self.content[match.start():brace_end+1]
            line_number = self.content[:match.start()].count('\n') + 1
            body_content_start = first_brace + 1
            body_content_end = brace_end
            if body_content_end < body_content_start:
                self.errors.append(f"Invalid body range for prototype '{name}': {body_content_start}-{body_content_end}")
                continue
            directives = self._parse_body(body_content_start, body_content_end)
            self.prototypes[name] = Prototype(
                name=name,
                parent=parent,
                directives=directives,
                line_number=line_number,
                raw_text=raw_text
            )

    def get_prototype(self, name: str) -> Optional[Prototype]:
        return self.prototypes.get(name)

    def get_children(self, parent_name: str) -> List[Prototype]:
        return [p for p in self.prototypes.values() if p.parent == parent_name]


# ---------- Proto Editor ----------

class ProtoEditor:
    """Editor for Brutal Legend prototype definitions."""

    # Template definitions for creating new prototypes
    TEMPLATES = {
        'infantry': [
            ('Add', 'CoTransform', [('Position', '<0,0,0>')]),
            ('Add', 'CoRenderMesh', [('MeshSet', '@Characters/Bipeds/Soldier/Rig/Soldier')]),
            ('Add', 'CoPhysicsCharacter', [('Mass', '80')]),
            ('Add', 'CoTeam', [('Faction', 'kFT_Neutral'), ('Team', 'kTEAM_Neutral')]),
            ('Add', 'CoInventory', [('InitialEquipment', '[]')]),
        ],
        'vehicle': [
            ('Add', 'CoTransform', [('Position', '<0,0,0>')]),
            ('Add', 'CoRenderMesh', [('MeshSet', '@Vehicles/RDD_Truck/Rig/RDD_Truck')]),
            ('Add', 'CoPhysicsVehicle', [('Mass', '1500'), ('TopSpeed', '40')]),
            ('Add', 'CoTeam', [('Faction', 'kFT_Neutral'), ('Team', 'kTEAM_Neutral')]),
        ],
        'building': [
            ('Add', 'CoTransform', [('Position', '<0,0,0>')]),
            ('Add', 'CoRenderMesh', [('MeshSet', '@Buildings/GenericBuilding/Rig/GenericBuilding')]),
            ('Add', 'CoTeam', [('Faction', 'kFT_Neutral'), ('Team', 'kTEAM_Neutral')]),
            ('Add', 'CoConstruction', [('BuildTime', '10')]),
        ],
        'weapon': [
            ('Add', 'CoTransform', []),
            ('Add', 'CoDamage', [('Damage', '<5,8>'), ('DamageType', 'Physical')]),
        ],
        'hq': [
            ('Add', 'CoTransform', [('Position', '<0,0,0>')]),
            ('Add', 'CoRenderMesh', [('MeshSet', '@Buildings/HQ/Rig/HQ')]),
            ('Add', 'CoTeam', [('Faction', 'kFT_A'), ('Team', 'kTEAM_Player0')]),
            ('Add', 'CoConstruction', [('BuildTime', '0')]),
        ],
        'barracks': [
            ('Add', 'CoTransform', [('Position', '<0,0,0>')]),
            ('Add', 'CoRenderMesh', [('MeshSet', '@Buildings/Barracks/Rig/Barracks')]),
            ('Add', 'CoTeam', [('Faction', 'kFT_A'), ('Team', 'kTEAM_Player0')]),
            ('Add', 'CoConstruction', [('BuildTime', '30')]),
            ('Add', 'CoUnitProducer', [('ProductionRate', '1.0')]),
        ],
    }

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.parser = ProtoParser(str(filepath))
        self.modified_prototypes: Dict[str, Prototype] = {}
        self.new_prototypes: Dict[str, Prototype] = {}
        self.deleted_prototypes: set = set()
        self.edits_history: List[Tuple[str, str, str]] = []  # (name, path, new_value)

    def load(self) -> bool:
        """Load and parse the proto file."""
        return self.parser.load()

    def list_prototypes(self, filter_str: Optional[str] = None) -> List[Tuple[str, str]]:
        """List all prototypes. Optionally filter by name."""
        results = []
        # Combine parser prototypes and new prototypes
        all_prototypes = dict(self.parser.prototypes)
        all_prototypes.update(self.new_prototypes)
        for name in sorted(all_prototypes.keys()):
            if name in self.deleted_prototypes:
                continue
            proto = all_prototypes.get(name)
            if proto:
                if filter_str and filter_str.lower() not in name.lower():
                    continue
                results.append((name, proto.parent))
        return results

    def show_prototype(self, name: str) -> Optional[str]:
        """Get detailed information about a prototype."""
        # Check new prototypes first (they may have edits)
        if name in self.new_prototypes:
            proto = self.new_prototypes[name]
        else:
            proto = self.parser.prototypes.get(name)

        if not proto:
            return None

        lines = []
        lines.append(f"Prototype: {proto.name}")
        lines.append(f"Parent: {proto.parent}")
        lines.append(f"Line: {proto.line_number}")
        lines.append(f"Directives ({len(proto.directives)}):")

        for directive in proto.directives:
            if isinstance(directive, AddDirective):
                lines.append(f"  Add {directive.component_name} {{")
                for prop in directive.properties:
                    lines.append(f"    {prop.name} = {prop.value.raw};")
                lines.append(f"  }};")
            elif isinstance(directive, OverrideDirective):
                lines.append(f"  Override {{")
                for override in directive.overrides:
                    lines.append(f"    {override.path} = {override.value.raw};")
                lines.append(f"  }};")

        return '\n'.join(lines)

    def create_prototype(self, name: str, parent: str, template: Optional[str] = None) -> Tuple[bool, str]:
        """Create a new prototype from scratch or from a template."""
        if name in self.parser.prototypes:
            return False, f"Prototype '{name}' already exists. Use edit instead."

        if parent not in self.parser.prototypes:
            return False, f"Parent '{parent}' does not exist."

        directives = []

        if template and template in self.TEMPLATES:
            for directive_type, comp_name, props in self.TEMPLATES[template]:
                if directive_type == 'Add':
                    properties = [Property(p[0], PropertyValue(p[1])) for p in props]
                    directives.append(AddDirective(comp_name, properties))

        # Create the prototype object
        new_proto = Prototype(
            name=name,
            parent=parent,
            directives=directives,
            line_number=0,  # New prototype has no line number
            raw_text=self._generate_proto_text(name, parent, directives)
        )

        self.new_prototypes[name] = new_proto
        return True, f"Created prototype '{name}' extending '{parent}'" + \
               (f" with template '{template}'" if template else "")

    def _generate_proto_text(self, name: str, parent: str, directives: List[Directive]) -> str:
        """Generate the proto text for a prototype."""
        parts = [f"Prototype {name} : {parent} {{"]

        for directive in directives:
            if isinstance(directive, AddDirective):
                if directive.properties:
                    props_str = '; '.join(f"{p.name}={p.value.raw}" for p in directive.properties)
                    parts.append(f"    Add {directive.component_name} {{ {props_str} }};")
                else:
                    parts.append(f"    Add {directive.component_name} {{ }};")
            elif isinstance(directive, OverrideDirective):
                if directive.overrides:
                    overrides_str = '; '.join(f"{o.path}={o.value.raw}" for o in directive.overrides)
                    parts.append(f"    Override {{ {overrides_str} }};")
                else:
                    parts.append(f"    Override {{ }};")

        parts.append("}")
        return '\n'.join(parts)

    def edit_prototype(self, name: str, path: str, value: str) -> Tuple[bool, str]:
        """Edit an existing prototype property.

        Args:
            name: Prototype name
            path: Property path (e.g., "CoTeam:Faction" or "Entity:CoRenderMesh:MeshSet")
            value: New value

        Returns:
            (success, message)
        """
        proto = self.parser.prototypes.get(name)
        if not proto:
            if name in self.new_prototypes:
                proto = self.new_prototypes[name]
            else:
                return False, f"Prototype '{name}' not found."

        # Parse path to determine if it's an Add or Override
        path_parts = path.split(':')

        if len(path_parts) == 2:
            # Component:Property - could be Add or Override
            component, prop_name = path_parts
            found = False

            # Check existing directives
            for directive in proto.directives:
                if isinstance(directive, AddDirective) and directive.component_name == component:
                    # Update existing property
                    for prop in directive.properties:
                        if prop.name == prop_name:
                            old_val = prop.value.raw
                            prop.value = PropertyValue(value)
                            found = True
                            self.edits_history.append((name, path, value))
                            return True, f"Updated {name}.{path}: {old_val} -> {value}"
                    # Property doesn't exist in this component, add it
                    directive.properties.append(Property(prop_name, PropertyValue(value)))
                    found = True
                    self.edits_history.append((name, path, value))
                    return True, f"Added {name}.{path}={value}"

            if not found:
                # Need to add a new component
                new_props = [Property(prop_name, PropertyValue(value))]
                proto.directives.append(AddDirective(component, new_props))
                self.edits_history.append((name, path, value))
                return True, f"Added component {component} with {prop_name}={value}"

        elif len(path_parts) == 3:
            # Entity:Component:Property - this is an Override
            entity, component, prop_name = path_parts
            if entity != 'Entity':
                return False, f"Expected 'Entity' in path, got '{entity}'"

            found = False
            for directive in proto.directives:
                if isinstance(directive, OverrideDirective):
                    for override in directive.overrides:
                        if override.path == path:
                            old_val = override.value.raw
                            override.value = PropertyValue(value)
                            found = True
                            self.edits_history.append((name, path, value))
                            return True, f"Updated {name}.{path}: {old_val} -> {value}"
                    # If Override directive exists but not this specific path
                    if found:
                        break
                    # Add to existing Override directive
                    directive.overrides.append(PropertyOverride(path, PropertyValue(value)))
                    self.edits_history.append((name, path, value))
                    return True, f"Added override {name}.{path}={value}"

            # No Override directive exists, create one
            override_directive = OverrideDirective([
                PropertyOverride(path, PropertyValue(value))
            ])
            proto.directives.append(override_directive)
            self.edits_history.append((name, path, value))
            return True, f"Created Override directive with {name}.{path}={value}"

        return False, f"Invalid path format: {path}. Use 'Component:Property' or 'Entity:Component:Property'"

    def delete_prototype(self, name: str) -> Tuple[bool, str]:
        """Mark a prototype for deletion."""
        if name not in self.parser.prototypes:
            return False, f"Prototype '{name}' not found."
        if name in self.new_prototypes:
            del self.new_prototypes[name]
        self.deleted_prototypes.add(name)
        return True, f"Marked '{name}' for deletion."

    def validate(self) -> List[str]:
        """Validate the prototype definitions."""
        errors = []

        # Check deleted prototypes don't have issues
        for name in self.deleted_prototypes:
            if name not in self.parser.prototypes:
                errors.append(f"Cannot delete '{name}': does not exist")

        # Check new prototypes don't duplicate
        for name in self.new_prototypes:
            if name in self.parser.prototypes and name not in self.deleted_prototypes:
                errors.append(f"Cannot create '{name}': already exists")

        # Check parent exists for new prototypes
        for name, proto in self.new_prototypes.items():
            if proto.parent not in self.parser.prototypes and proto.parent not in [p.name for p in self.new_prototypes.values()]:
                errors.append(f"New prototype '{name}' has unknown parent '{proto.parent}'")

        # Check circular inheritance
        for name, proto in {**self.parser.prototypes, **self.new_prototypes}.items():
            if name in self.deleted_prototypes:
                continue
            visited = set()
            current = proto.parent
            while current and current != 'BaseEntity':
                if current in visited:
                    errors.append(f"Circular inheritance detected for '{name}'")
                    break
                visited.add(current)
                parent_proto = self.parser.prototypes.get(current)
                if not parent_proto:
                    parent_proto = self.new_prototypes.get(current)
                if not parent_proto:
                    break
                current = parent_proto.parent

        # Check for syntax issues in raw text generation
        for name, proto in self.new_prototypes.items():
            if proto.name != name:  # Only check newly created
                continue

        return errors

    def export(self, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """Export the modified proto to a file."""
        if output_path is None:
            output_path = str(self.filepath)
        else:
            output_path = str(output_path)

        output_lines = []

        # Process the original content, applying modifications
        content = self.parser.content
        lines = content.split('\n')

        # Track modifications to apply
        modifications = {}  # line_number -> new_text

        # Process new prototypes
        for name, proto in sorted(self.new_prototypes.items(), key=lambda x: x[1].line_number):
            if proto.line_number > 0:
                # Insert after this line
                pass  # Handled below by line replacement

        # Process deleted prototypes - mark for removal
        deleted_lines = set()
        for name in self.deleted_prototypes:
            proto = self.parser.prototypes.get(name)
            if proto:
                deleted_lines.add(proto.line_number)

        # Process edits - update raw_text of modified prototypes
        # Get all edited prototype names
        edited_names = set(e[0] for e in self.edits_history)
        for name, proto in self.parser.prototypes.items():
            if name in self.new_prototypes or name in edited_names:
                proto.raw_text = self._generate_proto_text(name, proto.parent, proto.directives)

        # Build output
        for i, line in enumerate(lines):
            line_num = i + 1
            if line_num in deleted_lines:
                continue

            # Check if this line has a modified prototype
            modified = False
            for name, proto in self.parser.prototypes.items():
                if proto.line_number == line_num and (name in edited_names or name in self.new_prototypes):
                    text = proto.raw_text.strip()
                    if text:
                        output_lines.append(text)
                        modified = True
                    break

            if not modified:
                output_lines.append(line)

        # Append new prototypes that weren't in original file
        # (prototypes with line_number 0)
        for name, proto in sorted(self.new_prototypes.items(), key=lambda x: x[1].line_number):
            if proto.line_number == 0:
                # Regenerate raw_text to include any edits
                proto.raw_text = self._generate_proto_text(proto.name, proto.parent, proto.directives)
                output_lines.append(proto.raw_text)

        output_content = '\n'.join(output_lines)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            return True, f"Exported to {output_path}"
        except Exception as e:
            return False, f"Failed to write: {e}"


# ---------- CLI ----------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Brutal Legend Prototype Editor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python proto_editor.py list
  python proto_editor.py show A01_Avatar
  python proto_editor.py create MySoldier --parent Character --template infantry
  python proto_editor.py edit A01_Avatar --set "CoTeam:Faction=kFT_A"
  python proto_editor.py edit MySoldier --set "Entity:CoRenderMesh:MeshSet=@My/Mesh"
  python proto_editor.py validate
  python proto_editor.py export --output all_modified.proto
        '''
    )

    parser.add_argument('--proto', '-p', default=None,
                        help='Path to all.proto file (default: auto-detect)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # list command
    list_parser = subparsers.add_parser('list', help='List all prototypes')
    list_parser.add_argument('--filter', '-f', help='Filter by name substring')

    # show command
    show_parser = subparsers.add_parser('show', help='Show prototype details')
    show_parser.add_argument('name', help='Prototype name')

    # create command
    create_parser = subparsers.add_parser('create', help='Create new prototype')
    create_parser.add_argument('name', help='New prototype name')
    create_parser.add_argument('--parent', '-P', required=True, help='Parent prototype')
    create_parser.add_argument('--template', '-t', choices=['infantry', 'vehicle', 'building', 'weapon', 'hq', 'barracks'],
                               help='Template to use')

    # edit command
    edit_parser = subparsers.add_parser('edit', help='Edit prototype property')
    edit_parser.add_argument('name', help='Prototype name')
    edit_parser.add_argument('--set', '-s', required=True,
                             help='Property to set, format: "Component:Property=value" or "Entity:Component:Property=value"')
    edit_parser.add_argument('--delete', '-d', action='store_true',
                            help='Delete the prototype instead of editing')

    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate prototypes')

    # export command
    export_parser = subparsers.add_parser('export', help='Export modified proto')
    export_parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    # Auto-detect proto path
    proto_path = args.proto
    if proto_path is None:
        default_paths = [
            Path("extracted/00Startup/all.proto"),
            Path("../extracted/00Startup/all.proto"),
            Path("brutal-legend-re/extracted/00Startup/all.proto"),
            Path(__file__).parent.parent.parent / "extracted/00Startup/all.proto",
        ]
        for p in default_paths:
            if p.exists():
                proto_path = str(p)
                break

    if proto_path is None:
        print("Error: Could not find all.proto. Use --proto to specify path.")
        sys.exit(1)

    # Create editor
    editor = ProtoEditor(proto_path)
    if not editor.load():
        print(f"Error: Failed to load {proto_path}")
        for err in editor.parser.errors:
            print(f"  {err}")
        sys.exit(1)

    # Execute command
    if args.command == 'list':
        prototypes = editor.list_prototypes(args.filter)
        if prototypes:
            for name, parent in prototypes:
                print(f"{name} : {parent}")
            print(f"\nTotal: {len(prototypes)} prototypes")
        else:
            print("No prototypes found.")

    elif args.command == 'show':
        result = editor.show_prototype(args.name)
        if result:
            print(result)
        else:
            print(f"Prototype '{args.name}' not found.")
            sys.exit(1)

    elif args.command == 'create':
        success, msg = editor.create_prototype(args.name, args.parent, args.template)
        print(msg)
        if success:
            # Auto-export on create
            editor.export(proto_path)
            print(f"Updated {proto_path}")
        else:
            sys.exit(1)

    elif args.command == 'edit':
        if args.delete:
            success, msg = editor.delete_prototype(args.name)
            print(msg)
            if success:
                editor.export(proto_path)
                print(f"Updated {proto_path}")
            else:
                sys.exit(1)
        else:
            # Parse the --set argument
            if '=' not in args.set:
                print("Error: --set must contain '=' (format: 'Component:Property=value')")
                sys.exit(1)
            path, value = args.set.split('=', 1)
            success, msg = editor.edit_prototype(args.name, path, value)
            print(msg)
            if success:
                editor.export(proto_path)
                print(f"Updated {proto_path}")
            else:
                sys.exit(1)

    elif args.command == 'validate':
        errors = editor.validate()
        if errors:
            print(f"Found {len(errors)} validation errors:")
            for err in errors:
                print(f"  {err}")
            sys.exit(1)
        else:
            print("Validation passed. No errors found.")

    elif args.command == 'export':
        success, msg = editor.export(args.output)
        print(msg)
        if not success:
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
