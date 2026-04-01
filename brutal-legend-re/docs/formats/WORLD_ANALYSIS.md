# Brutal Legend - World/Terrain System Analysis

**Status:** Active Research  
**Game:** Brutal Legend (2009)  
**Engine:** Buddha (Double Fine proprietary)  
**Last Updated:** 2026-04-01

---

## Executive Summary

Brutal Legend features an open world of approximately **40 square miles** with a **tile-based streaming system**. The world is organized into coordinate-grid tiles that stream dynamically as the player moves.

**Key Finding:** World data is stored in proprietary DFPF bundles (RgB_World, RgS_World, RgS_World2) with resource types including Heightfield, CollisionShape, PathTileData, and PhysicalSurfaceMap.

---

## 1. World Bundle Files

### 1.1 World Bundle Sizes

| Bundle | Header (~h) | Data (~p) | Total |
|-------|-------------|-----------|-------|
| RgS_World.~h/.~p | 0.48 MB | 390 MB | **390.48 MB** |
| RgS_World2.~h/.~p | 0.17 MB | 165.38 MB | **165.55 MB** |
| RgB_World.~h/.~p | 0.42 MB | 127.12 MB | **127.54 MB** |

**Prefix Convention:**
- **RgS_** = Runtime game (shipped on disc)
- **RgB_** = Redistributable/runtime

### 1.2 World Bundle Comparison

| Bundle | Purpose | Size |
|--------|---------|------|
| RgS_World.~p | Main world terrain & data | 390 MB |
| RgS_World2.~p | Additional world data (DLC?) | 165 MB |
| RgB_World.~p | Base runtime world | 127 MB |
| DLC1_Stuff.~p | DLC terrain & objects | 142 MB |

---

## 2. Tile-Based World Structure

### 2.1 World Coordinate System

World path format: worlds/<worldname>/tile/x<coord>/y<coord>/<layer>:<resourcetype>

Example tile path:
`
worlds/continent3/tile/x-6/y5/height:Heightfield
worlds/continent3/tile/x-6/y5/blend:PhysicalSurfaceMap
worlds/continent3/tile/x-6/y5/base_tile:CollisionShape
worlds/continent3/tile/x-6/y5/base_ptile:PathTileData
`

**Main world:** continent3 (the campaign open world)

### 2.2 Per-Tile Data Layers

Each tile contains multiple data layers:

| Layer | Resource Type | Description | Typical Size |
|-------|---------------|-------------|--------------|
| height | Heightfield | Terrain heightmap | 512 KB |
| blend | Texture | Terrain albedo/blend texture | 128 KB |
| blend | RndTileData | Random tile variation data | 8 KB |
| occlusion | Texture | Ambient occlusion map | 128 KB |
| base_tile | CollisionShape | Base terrain collision mesh | varies |
| base_ptile | PathTileData | Pathfinding grid data | 0-316 KB |
| base_objects | CollisionShape | Placed object collision | varies |
| base_objects | ObjectData | Game objects in tile | varies |
| base_visuals | ObjectData | Visual-only objects | varies |
| blend | PhysicalSurfaceMap | Surface material IDs | varies |

### 2.3 Tile Coordinate Range

From preload analysis, tiles span approximately:
- **X:** -8 to +3 (at least 12 columns)
- **Y:** -4 to +7 (at least 12 rows)

Estimated total tiles: ~100-150 tiles for full continent

---

## 3. Resource Type Versions

### 3.1 World Resource Type Registry

| Type Index | Resource Type | Version | Hash |
|------------|---------------|---------|------|
| 3 | Heightfield | 36 | 0x263f5813 |
| 5 | QuadTileData | 19 | 0x7c9651ff |
| 14 | TerrainMaterial | 3 | 0x3a83c2fc |
| 15 | LevelData | 6 | 0x2527f4a6 |
| 18 | PhysicalSurfaceMap | 3 | 0xc1c9fdc6 |
| 20 | CollisionShape | 6022 | 0xe6158ebb |
| 21 | PathTileData | 50 | 0x458bd6dd |

### 3.2 Resource Type Descriptions

**Heightfield (Ver: 36)**
- Stores terrain heightmap data
- Stored as proprietary binary format
- Size per tile: 512 KB (uncompressed)
- Uses 16-bit height values (inferred from size)

**CollisionShape (Ver: 6022)**
- Terrain collision mesh
- Base tile collision + object collisions
- Binary mesh format

**PathTileData (Ver: 50)**
- Navigation pathfinding data
- Size varies: 0 KB (empty) to 316 KB (complex)
- Grid-based representation

**PhysicalSurfaceMap (Ver: 3)**
- Maps blend texture to physical materials
- Links terrain texture layers to surface types
- Used for footsteps, vehicle handling

**TerrainMaterial (Ver: 3)**
- Material definitions for terrain layers
- Multiple terrain materials per world:
  - forestgrass
  - intriorockcliff
  - introbonepile
  - canyonofimpaler
  - etc.

**LevelData (Ver: 6)**
- World-level metadata
- continent3: 896 KB uncompressed
- Contains global objects and world settings

---

## 4. Terrain Texture System

### 4.1 Texture Layers Per Tile

Each tile has a lend:Texture (128 KB) that combines multiple terrain materials.

Blend texture channels (inferred):
- **R:** Material layer 1 mask
- **G:** Material layer 2 mask
- **B:** Material layer 3 mask
- **A:** Material layer 4 mask OR height

### 4.2 Terrain Material Examples

From resource manifests:
- orestgrass - Forest floor
- intriorockcliff - Rock cliffs
- introbonepile - Bone pile surfaces
- canyonofimpaler - Canyon terrain
- jungledirt - Jungle dirt
- lavarock - Lava rock

---

## 5. Navigation System

### 5.1 Navigation Graph

Resource: worlds/continent3/continent3:NavigationSystemGraph

Single navigation graph for the entire continent.

### 5.2 PathTileData Structure

PathTileData is stored per-tile with varying complexity:
- Empty tiles: ~0 KB
- Road tiles: ~40-77 KB
- Complex intersections: up to 316 KB

Pathfinding can be disabled via config: DisablePathFinding = false

---

## 6. Collision System

### 6.1 Collision Layers

| Layer | Description |
|-------|-------------|
| base_tile | Base terrain collision |
| base_objects | Placed object collisions |

### 6.2 Collision Shape Version

**CollisionShape Version 6022** - Very high version suggests:
- Complex collision geometry
- Frequent updates during development
- Mesh-based collision (not heightfield)

---

## 7. World Streaming System

### 7.1 Buddha Engine Streaming

From BuddhaDefault.cfg:
- Uses intermediate data system
- Clump-based loading for tiles
- Memory management via managedResourceMem

### 7.2 Tile Loading Triggers

Tiles load based on:
- Player proximity (streaming radius)
- Encounter zones (Stage Battle areas)
- Mission requirements

### 7.3 Configuration

`
campaignLevel = "Worlds/Continent3/Continent3.LevelData"
`

---

## 8. DLC World Data

### 8.1 DLC1 World Structure

DLC1 adds tiles in worlds/dlc1_1/tile/ with similar structure:
- Tile coordinates: x-4 to x3, y-4 to y1
- Each tile has: height, blend, occlusion, base_ptile, base_tile

### 8.2 DLC Terrain Materials

DLC adds unique terrain materials:
- nvil_surface
- cliffwallschunky
- darkrock
- dirt_pebbles
- ieldstone
- lesh_guts, lesh_lumps
- motorforge_dirt
- 	emplefloorstone

---

## 9. Known File Formats

### 9.1 Heightmap Format

**Suspected Format:** Custom binary (NOT standard .raw, .hm, .heightmap)

Evidence:
- No .raw, .hm, or .heightmap files found
- Heightfield resource type with version 36
- 512 KB per tile suggests 257x257 or 513x513 16-bit heightmap

**Possible formats:**
- 16-bit integer grid
- Possibly split into chunks (QuadTileData)
- Compression applied (ZLIB likely)

### 9.2 Zone/Region Format

**Not a separate format** - world uses coordinate-based tile system

Zone data is inherent in the tile coordinate system.

### 9.3 Terrain Texture Format

Standard texture format:
- DDS (DirectDraw Surface)
- 128 KB per tile blend texture
- Full mipmaps
- Compression: DXT1/DXT5 (based on size)

### 9.4 Collision Mesh Format

Proprietary binary format:
- CollisionShape version 6022
- Triangular mesh data
- Material IDs per face

---

## 10. Next Steps for Analysis

### 10.1 Immediate Tasks

| Priority | Task | Status |
|----------|------|--------|
| High | Extract Heightfield binary data | Not Started |
| High | Analyze Heightfield header structure | Not Started |
| High | Determine heightmap dimensions | Not Started |
| Medium | Parse CollisionShape binary | Not Started |
| Medium | Map PathTileData structure | Not Started |
| Low | Reverse PhysicalSurfaceMap format | Not Started |

### 10.2 Tools Needed

1. **DFPF Extractor** - Extract resources from .~p bundles
2. **Heightfield Viewer** - Custom tool to visualize Heightfield data
3. **Collision Shape Viewer** - Parse CollisionShape to mesh

### 10.3 Research Questions

1. What are the exact dimensions of each Heightfield tile?
2. How are height values encoded (16-bit, float, etc.)?
3. What is the world coordinate system origin?
4. How are tiles stitched together at edges?
5. What is the QuadTileData structure for LOD?

---

## 11. Hypotheses

### 11.1 Heightmap Format

Based on 512 KB per tile:
- 257x257 x 2 bytes = 132 MB (too large)
- 129x129 x 2 bytes = 33 MB (too small)
- 513x513 x 2 bytes = 527 MB (too large)
- **Most likely:** 257x257 with header/metadata = 512 KB

### 11.2 Tile Seam Handling

Likely uses:
- Edge matching via shared vertices
- Blend textures for smooth transitions
- No explicit seam data needed

### 11.3 LOD System

QuadTileData (Ver: 19) suggests:
- Quad-tree based LOD
- Multiple detail levels per tile
- Distance-based selection

---

## 12. Related Documentation

| Document | Path | Status |
|----------|------|--------|
| DFPF Format Analysis | docs/formats/DFPF_ANALYSIS.md | Complete |
| Resource Type Registry | docs/formats/RESOURCE_TYPES.md | Partial |
| Buddha Engine Config | docs/engine/BUDDHA_CONFIG.md | Started |

---

*Document generated as part of Brutal Legend reverse engineering project*
*Repository: brutal-legend-re*
