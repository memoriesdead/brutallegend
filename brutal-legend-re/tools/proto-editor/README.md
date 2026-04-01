# Brutal Legend Prototype Editor

A Python-based parser and analysis tool for Brutal Legend's prototype definitions.

## Overview

The `all.proto` file (1.77 MB, 3,516 prototypes) defines all game entity prototypes using a custom text-based DSL. This tool parses, validates, and analyzes those definitions.

## Format

Prototypes use the format:
```
Prototype <Name> : <Parent> {
    Add <Component> { property=value; };
    Override { Component:Property = value; };
};
```

## Usage

```bash
# Show summary statistics
python proto_parse.py <path/to/all.proto> summary

# List all prototypes
python proto_parse.py <path/to/all.proto> list

# Get a specific prototype as JSON
python proto_parse.py <path/to/all.proto> get <PrototypeName>

# Find prototypes by component
python proto_parse.py <path/to/all.proto> find-component <ComponentName>

# Find prototypes by property
python proto_parse.py <path/to/all.proto> find-property <PropertyName> [value]

# Validate prototype hierarchy
python proto_parse.py <path/to/all.proto> validate
```

## Examples

```bash
# Parse the extracted proto file
python proto_parse.py extracted/00Startup/all.proto summary

# Find all character prototypes
python proto_parse.py extracted/00Startup/all.proto get A01_Avatar

# Find all prototypes with CoTeam component
python proto_parse.py extracted/00Startup/all.proto find-component CoTeam

# Find all prototypes with Health property
python proto_parse.py extracted/00Startup/all.proto find-property MaxHealth
```

## Output Formats

- **summary**: Statistics on prototypes, parents, and components
- **list**: All prototype names and parents
- **get**: Single prototype as formatted JSON
- **find-component**: Prototypes containing a specific component
- **find-property**: Prototypes with a specific property
- **validate**: Validation errors in the hierarchy

## Components

Most common components found:
- CoRenderMesh (866 prototypes) - Visual mesh assignment
- CoPhysicsRigidBody (622) - Physics body
- CoSkeleton (334) - Skeleton/bone structure
- CoTalking (329) - Dialog/talking
- CoTeam (327) - Faction and team membership
- CoDamageable (288) - Health and damage settings
- CoRenderFoliage (240) - Foliage rendering
- CoSoundEmitter (193) - Audio emission
- CoInventory (156) - Equipment/inventory
- CoWeapon (122) - Weapon configuration