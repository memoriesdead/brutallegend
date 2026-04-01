# Brutal Legend — Prototype Definition Format (PROTO) Specification

## Overview

The `all.proto` file (1,770,625 bytes, 3,530 lines) defines all game entity prototypes for Brutal Legend using a custom text-based DSL. **This is NOT Google Protocol Buffers** — it is a bespoke prototype/component inheritance system.

---

## File Format Structure

### General Syntax

```
Prototype <Name> : <Parent> { <Body> };
```

- `Prototype` keyword begins a new prototype definition
- `Name` is the unique identifier (PascalCase, e.g., `A01_Avatar`, `Deuce`, `FightingNode`)
- `Parent` is the prototype to inherit from (can be `BaseEntity` for roots)
- `Body` contains `Add`, `Override`, and `Apply` directives
- Each definition terminates with a semicolon

### Directives

| Directive | Purpose |
|-----------|---------|
| `Add <ComponentName> { <properties> };` | Attach a new component with its configuration |
| `Override { <Entity:CoComponent:Property = value>; };` | Override specific properties on existing components |
| `Apply <Condition> { <directives> };` | Conditional application (rare) |

### Whitespace and Delimiters

- Newlines are cosmetic — the parser is line-agnostic
- Components within `Add { }` blocks use semicolons to separate property assignments
- Prototype bodies themselves end with `};` (note: no semicolon before the closing brace)

---

## Prototype Class Hierarchy

### Root: `BaseEntity`

The apex parent with no visual/renderable representation. All gameplay objects descend from here.

```
BaseEntity
├── Character
│   ├── A01_Avatar (player)
│   ├── W青少年 (minor faction soldier)
│   └── <many infantry types>
├── DeuceBase
│   └── Deuce (guitar-case weapon)
├── DecoratorNode
│   └── FightingNode
├── TerrainNode
│   └── CombatAreaNode
├── Vehicle
│   ├── RDD_GrouptyRally
│   ├── RDD_Typesetter
│   ├── RDD_Transporter (DLC van)
│   └── <other vehicles>
├── Building
│   ├── HQSite
│   │   ├── HQ_A (blue faction HQ)
│   │   └── HQ_B (red faction HQ)
│   ├── Barracks
│   ├── Stage
│   └── <other structures>
└── Projectile / Effect / etc.
```

### Key Subclasses

| Class | Role |
|-------|------|
| `BaseEntity` | Abstract root — provides `CoTeam` and `CoTransform` only |
| `Character` | Mobile units; adds `CoPhysicsCharacter`, `CoRenderMesh`, `CoInventory` |
| `Vehicle` | Mountable vehicles; adds vehicle-specific physics and mesh |
| `Building` | Static structures; placed by map designers |
| `DecoratorNode` | Decorative world objects |
| `TerrainNode` | World area definitions |
| `RDD_*` | Ride-style vehicles (RDD = Rage Defense D |

---

## Property Types and Syntax

### Primitives

| Syntax | Type | Example |
|--------|------|---------|
| `Name = false;` | Boolean | `Concrete=false;` |
| `Name = 42;` | Integer | `MaxProximity=0;` |
| `Name = 3.14;` | Float | `BlendTime=0.1;` |
| `Name = <x,y,z>;` | Vector3 | `Position=<0,0,0>;` |
| `Name = <r,g,b,a>;` | Color | `TextColor=<1,1,1,1>;` |
| `Name = <min,max>;` | Range | `Damage=<5,8>;` |
| `Name = "string";` | String | `Annotation="";` |

### Resource References

Paths prefixed with `@` reference other game assets:

```
MeshSet=@Characters/Bipeds/A01_Avatar/Rig/A01_Avatar;
Material=@Terrain/GDC_Desert/Materials/GDC_Desert_Dirt;
Texture=@VFX/Decals/Slash/Slash_Decal_01;
Audio=@Audio/SFX/Entourage/SummonEntourage;
```

### Component Property Override Syntax

To change a property on a component attached by a parent prototype, use the dotted path:

```
Override {
    Entity:CoRenderMesh:MeshSet=@Characters/Bipeds/A01_Avatar/Rig/A01_Avatar;
    Entity:CoTransform:Position=<10,0,5>;
    Entity:CoTeam:Faction=kFT_Neutral;
};
```

- `Entity` is the literal keyword referring to the prototype's own entity
- `CoComponentName` must exactly match the parent's component name
- Property name is case-sensitive

### Vector Notation

- `<x,y,z>` — 3D vectors for positions, scales, directions
- `<r,g,b,a>` — RGBA color (0.0–1.0 float range)
- `<min,max>` — Damage ranges, numeric bounds

---

## Component System

### Component Naming Convention

All components are prefixed with `Co`:

| Component | Purpose |
|-----------|---------|
| `CoTransform` | World position, rotation, scale |
| `CoRenderMesh` | Visual mesh and material assignment |
| `CoPhysicsCharacter` | Character movement physics |
| `CoPhysicsVehicle` | Vehicle physics |
| `CoTeam` | Faction and team membership |
| `CoInventory` | Equipment / loadout |
| `CoAISpacing` | AI spacing rules |
| `CoAIProximity` | AI proximity triggers |
| `CoAIMovement` | AI movement parameters |
| `CoAnnotation` | Editor annotation / text labels |
| `CoInventory` | Item containers, weapon slots |
| `CoEntourage` | Entourage/follower system |
| `CoMountedWeapon` | Weapons mounted on vehicles |
| `CoRumble` | Haptic/audio rumble effects |
| `CoDamage` | Damage configuration |
| `CoHealth` | Health points |
| `CoConstruction` | Build site behavior |

### Add vs. Override

- `Add CoXxx { }` — Attach a new component to this prototype
- `Override { Entity:CoXxx:Property = value; }` — Modify a component already present via inheritance

---

## Faction System

### Faction Types (`kFT_*`)

| Constant | Value | Description |
|----------|-------|-------------|
| `kFT_Neutral` | 0 | Neutral — does not engage |
| `kFT_A` | 1 | Blue faction (player-adjacent) |
| `kFT_B` | 2 | Red faction (enemy) |
| `kFT_D` | 3 | D: The Darkness faction |
| `kFT_L` | 4 | L: Layer 8 (multiplayer factions) |

### Team Types (`kTEAM_*`)

| Constant | Value | Description |
|----------|-------|-------------|
| `kTEAM_Player0` | 0 | Player-controlled |
| `kTEAM_Hostile` | 1 | Always hostile |
| `kTEAM_EndGame` | 2 | End-game enemy |
| `kTEAM_Neutral` | 3 | Neutral passive |
| `kTEAM_NPC` | 4 | NPC / non-combatant |
| `kTEAM_Player1` | 5 | Multiplayer player 1 |
| `kTEAM_Player2` | 6 | Multiplayer player 2 |
| `kTEAM_Player3` | 7 | Multiplayer player 3 |
| `kTEAM_Neutral2` | 8 | Second neutral team |

### Faction Example

```
Add CoTeam {
    Faction=kFT_A;
    Team=kTEAM_Player0;
};
```

---

## Special Patterns and Conventions

### Prototype Conditional Inheritance

Some prototypes use `Concrete=false` to mark abstract intermediates:

```
Prototype Character : BaseEntity {
    Override { Concrete=false; };
    Add CoVoice;
};
```

Only `Concrete=true` prototypes can spawn in the world.

### Initial Equipment Pattern

Characters and units carry initial weapons via `CoInventory`:

```
Add CoInventory {
    InitialEquipment=[Deuce_EmptyPrimaryWeapon, Deuce_EmptySecondaryWeapon];
    InfiniteAmmo[PrimaryWeapon]=true;
    InfiniteAmmo[SecondaryWeapon]=true;
};
```

### Multi-Component Add Blocks

Some prototypes attach multiple components in sequence:

```
Add CoRenderMesh { MeshSet=@...; };
Add CoPhysicsCharacter { ...; };
Add CoTeam { Faction=kFT_A; };
```

### Annotation Component

For editor/debug annotations visible in game world:

```
Add CoAnnotation {
    Annotation="";
    TextColor=<1,1,1,1>;
    MaxDrawDistance=500;
};
```

### Range Damage

Damage values use `<min,max>` tuple notation:

```
Add CoDamage {
    Damage=<5,8>;
    DamageType=Electric;
};
```

### Overriding Inherited Components

The `Entity:CoXxx:Property` syntax overrides parent component properties:

```
Prototype A01_Avatar : Character {
    Override {
        Entity:CoRenderMesh:MeshSet=@...A01_Avatar;
        Entity:CoTeam:Faction=kFT_A;
    };
};
```

### Empty Components

Some components appear with empty braces when used only to inherit default values:

```
Add CoAIProximity { };
```

---

## File Layout

The `all.proto` file is structured as follows:

1. **File header** — blank / metadata
2. **Core class definitions** — `BaseEntity`, `Character`, `Vehicle`, `Building`, etc.
3. **Concrete prototypes** — actual game entities (soldiers, vehicles, structures)
4. **World/object definitions** — `HQ_A`, `HQ_B`, map markers, effects
5. **End of file**

---

## Quick Reference: Common Patterns

### Minimal Character Prototype

```
Prototype MySoldier : Character {
    Add CoTransform { Position=<0,0,0>; };
    Add CoRenderMesh { MeshSet=@...; };
    Add CoPhysicsCharacter { Mass=80; };
    Add CoTeam { Faction=kFT_B; Team=kTEAM_Hostile; };
    Add CoInventory { InitialEquipment=[Soldier_Weapon]; };
};
```

### Override Parent's Mesh

```
Prototype MyUnit : Character {
    Override {
        Entity:CoRenderMesh:MeshSet=@Characters/Bipeds/NewUnit/Rig/NewUnit;
    };
};
```

### Vehicle Prototype

```
Prototype MyVehicle : Vehicle {
    Add CoTransform { Position=<0,0,0>; };
    Add CoRenderMesh { MeshSet=@Vehicles/RDD_MyVehicle/Rig/RDD_MyVehicle; };
    Add CoPhysicsVehicle { Mass=1500; TopSpeed=40; }; 
    Add CoTeam { Faction=kFT_A; Team=kTEAM_Player0; };
};
```

---

*Generated from analysis of `all.proto` (Brutal Legend prototype definition file).*
