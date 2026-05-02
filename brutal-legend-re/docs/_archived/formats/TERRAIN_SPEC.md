# Brutal Legend - Terrain Format Specification

**Status:** Active Research
**Game:** Brutal Legend (2009)
**Engine:** Buddha (Double Fine proprietary)
**Last Updated:** 2026-04-01

---

## Executive Summary

Brutal Legend uses a tile-based terrain streaming system with proprietary binary formats for heightmaps, collision meshes, and surface materials. This document details the discovered terrain data formats based on extracted game files.

**Key Findings:**
- Terrain tiles use a coordinate-based path system: `worlds/<world>/tile/x<coord>/y<coord>/<layer>.<type>`
- **CRITICAL:** Heightfield files are **DXT5 compressed textures** (128x128, 8 mipmaps), NOT raw heightmaps. GPU shader handles displacement.
- Collision uses Havok Physics 6.1.0-r1 format
- Terrain textures use DXT5 compression with material layer blending

---

## 1. Tile Directory Structure

### 1.1 Path Format

```
worlds/<worldname>/tile/x<coord>/y<coord>/<layer>.<resourcetype>
```

**Example tile paths:**
```
worlds/continent3/tile/x-6/y-5/height.bin
worlds/continent3/tile/x-6/y-5/base_tile.bin
worlds/continent3/tile/x-8/y-8/blend.bin
worlds/continent3/tile/x-8/y-8/blend.Texture
```

### 1.2 Tile Layers

| Layer | Type | Description |
|-------|------|-------------|
| height | Binary | Terrain heightfield data |
| blend | Binary+Texture | Terrain albedo/blend texture |
| occlusion | Texture | Ambient occlusion map |
| base_tile | Binary | Base terrain collision mesh |
| base_ptile | Binary | Pathfinding grid data |
| base_objects | Binary | Placed object collisions |
| base_visuals | Binary | Visual-only objects |

### 1.3 Known World Names

- `continent3` - Main campaign open world
- `dlc1_4` - DLC1 terrain
- `sk_1`, `sk_2`, `sk_5`, `sk_7`, `sk_9` - Skiply regions

### 1.4 Tile Coordinate Range (continent3)

From bundle analysis:
- **X:** -8 to +6
- **Y:** -8 to +7

---

## 2. Heightfield Format (.Heightfield)

### 2.0 NEW DISCOVERY: Heightfield is DDS Texture

**Analysis Date:** 2026-04-01

**Key Finding:** Extracted `.Heightfield` files from RgS_World bundle are **DXT5 compressed DDS textures**, NOT raw heightmaps. This is a GPU-based height representation.

**Sample Analysis:**
```
File: extracted/RgS_World/file_0106_offset_1495552.Heightfield
Size: 22,040 bytes
Structure:
  - 40-byte custom header
  - 124-byte DDS header
  - 21,876 bytes DXT5 compressed data
```

**DDS Header Parsed:**
| Field | Value |
|-------|-------|
| Magic | 'DDS ' |
| Flags | 0x21007 |
| Height | 128 |
| Width | 128 |
| Pixel Format | 'DXT5' |
| Mipmap Levels | 8 |

**Implications:**
1. Height is processed by GPU shader via texture sampling
2. DXT5 compression stores height in YCoCg-like format
3. Game uses GPU displacement mapping for terrain geometry

### 2.1 Custom Header (40 bytes)

| Offset | Size | Description |
|--------|------|-------------|
| 0x00-0x07 | 8 | Unknown metadata |
| 0x08 | 4 | 0x0b (type marker?) |
| 0x10 | 4 | Width hint (0x80 = 128) |
| 0x14 | 4 | Height hint (0x80 = 128) |
| 0x20 | 4 | 'rtxT' marker (texture?) |
| 0x24 | 4 | Data size |
| 0x28 | 4 | 'DDS ' magic |

### 2.2 File Structure (height.bin)

**NOTE:** The earlier analysis of `height.bin` with "hsem" magic may refer to a DIFFERENT resource format. Further research needed to reconcile.

### 2.3 File Structure

**Sample file:** `worlds/continent3/tile/x-6/y-5/height.bin` (49,973 bytes)

**Header Layout (first ~176 bytes):**

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 4 | Magic | `"hsem"` (reversed "mesh") |
| 0x04 | 4 | Unknown | 0x00000000 |
| 0x08 | 8 | Floats[2] | Float values (~1.27, ~0.897) - possibly scale |
| 0x10 | 8 | Floats[2] | Float values - possibly height range |
| 0x18 | 8 | Floats[2] | Float values |
| 0x20 | 4 | Magic | `"lrtm"` (terrain marker) |
| 0x24 | 4 | Version | 0x01000000 |
| 0x28 | 4 | Count | 0x2e000000 (46 decimal) |
| 0x2C | ... | String | "environments/materials/..." |
| ... | ... | ... | Material path references |
| 0x70 | 4 | Format | `"BVXD"` (Big-endian Var X Dim?) |
| 0x74 | 4 | Unknown | 0x02000000 |
| 0x78 | 4 | Unknown | 0x00000000 |
| 0x7C | 4 | Format | `"BIXD"` (Big-endian Int X Dim?) |

**Data Section (after header):**
- Contains uint16 indices in range 0x0400-0x04FF (1024-1279)
- These appear to be material layer indices or height bucket indices
- Example: `04 33 04 32 04 34 04 35...`

### 2.2 Header Analysis Notes

The height.bin format appears to be a **material index map** rather than raw height values:

- Float values at 0x08-0x1F appear to be bounding/dimension data
- Material paths reference terrain textures like `rock_rockmetal`, `sandbeach`
- The `BVXD`/`BIXD` markers suggest dimension-related metadata
- Indices (0x04xx range) likely map to terrain material layers

### 2.3 Height Data Interpretation

**Theory:** The game may store height data differently. Possible scenarios:
1. Height is derived from collision mesh (base_tile.bin)
2. Height data is embedded in other tile layers
3. Height uses a different encoding not yet identified

**Evidence:**
- height.bin files vary in size (2KB to 50KB) suggesting variable compression
- The 0x04xx indices could represent quantized height values
- 512KB size estimate from prior analysis doesn't match extracted files

---

## 3. Terrain Texture System (blend)

### 3.1 blend.Texture Header Format

**Path reference:** `worlds/continent3/tile/x-8/y-8/blend.Texture`
**Sample file size:** 8,510 bytes

**Header Structure (16 bytes, little-endian):**

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 4 | Magic | 0x00000001 (little-endian) |
| 0x04 | 4 | Version | 4 |
| 0x08 | 4 | Flags | 0x3F800000 (float 1.0, or flags field) |
| 0x0C | 4 | Unknown | 0x00000025 (37 decimal, often appears) |

**String Section:**

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x10 | N | blend_path | Null-terminated string: "worlds/continent3/tile/x-8/y-8/blend" |
| 0x35 | 4 | uint32 | Occlusion string length (41) |
| 0x39 | 41 | occlusion_path | Length-prefixed string (incl null): "worlds/continent3/tile/x-8/y-8/occlusion" |
| 0x62 | 4 | uint32 | Material count or marker (1) |
| 0x67 | 4 | uint32 | Material string 1 length (40) |
| 0x6B | 40 | material1_path | Length-prefixed string: "environments/terrainmaterials/sandbeach" |
| ... | ... | ... | Additional materials follow same pattern |
| 0xA5 | 4 | uint32 | Material string 2 length (45) |
| 0xA9 | 45 | material2_path | Length-prefixed string: "environments/terrainmaterials/introrockcliff" |

**Key References Found:**
- `worlds/continent3/tile/x-8/y-8/blend` - albedo texture path
- `worlds/continent3/tile/x-8/y-8/occlusion` - ambient occlusion path
- `environments/terrainmaterials/sandbeach` - terrain material layer 1
- `environments/terrainmaterials/introrockcliff` - terrain material layer 2

**File Format Notes:**
- Strings use length-prefixed format (uint32 length followed by string data)
- First string (blend_path) is null-terminated, subsequent strings are length-prefixed
- Material strings can include embedded float values (e.g., at 0x99: 3.5f)
- Total file contains: header + 2 path strings + N material entries

### 3.2 blend.bin Data

**Sample file:** `worlds/continent3/tile/x-8/y-8/blend.bin` (35,948 bytes)

**Structure:**
- Similar header to height.bin with "hsem" magic
- References same material system
- Contains compressed texture data (DXT5)

### 3.3 Creating/Editing blend.Texture Files

**To create a new blend.Texture:**

1. Start with 16-byte header:
   - Bytes 0-3: Magic = 0x00000001
   - Bytes 4-7: Version = 4
   - Bytes 8-11: Flags = 0x3F800000
   - Bytes 12-15: Unknown = 0x00000025

2. Add blend path string (null-terminated, starting at 0x10):
   - Format: "worlds/<world>/tile/x<coord>/y<coord>/blend"
   - Example: "worlds/continent3/tile/x0/y0/blend\0"

3. Add occlusion path (length-prefixed):
   - uint32 length (including null)
   - string data

4. Add material entries (repeat for each terrain layer):
   - uint32 count/marker
   - uint32 material string length
   - string data (path like "environments/terrainmaterials/<name>")

**Example Python structure:**
```python
def create_blend_texture(world, tile_x, tile_y, blend_path, occlusion_path, materials):
    header = struct.pack('<IIII', 0x00000001, 4, 0x3F800000, 0x00000025)
    header += blend_path.encode('ascii') + b'\x00'
    # Follow with length-prefixed strings...
```

---

## 4. Collision Mesh Format (base_tile.bin)

### 4.1 Havok Physics Format

**Sample file:** `worlds/continent3/tile/x6/y7/base_tile.bin` (340,064 bytes)

**Header Analysis:**

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 4 | Magic | `0x57E0E057` (Havok tag) |
| 0x04 | 4 | Unknown | 0x10C0C010 |
| 0x08 | 4 | Unknown | 0x06000000 (version?) |
| 0x10 | 4 | Flags | 0x04010001 |
| 0x14 | 4 | ShapeCount | 0x03000000 (3 shapes) |
| 0x18 | 4 | Unknown | 0x02000000 |
| 0x20 | 4 | Offset | Offset to classnames section |
| 0x24 | 4 | Unknown | 0x4B000000 |
| 0x28 | 12 | String | "Havok-6.1.0-r1\0" |
| 0x34 | 8 | Unknown | 0xFF... padding |
| 0x40 | ... | Section | `__classnames__` section |
| ... | ... | Section | `__types__` section |
| ... | ... | Section | `__data__` section |

### 4.2 Havok Section Types

**Classnames Section (`__classnames__`):**
- Contains HKClass structures
- References: `hkClass`, `hkClassMember`, `hkClassEnum`

**Types Section (`__types__`):**
- Type definitions for serialization

**Data Section (`__data__`):**
- Actual collision mesh vertices and indices
- Contains vertex positions (float[3]) and triangle indices (uint32[3])

---

## 5. PathTileData Format (base_ptile.bin)

### 5.1 Size Range

From WORLD_ANALYSIS.md:
- Empty tiles: 0 KB
- Simple tiles: 40-77 KB
- Complex intersections: up to 316 KB

### 5.2 Version

- Resource type version: 50
- Content: Navigation/pathfinding grid data

---

## 6. PhysicalSurfaceMap Format

### 6.1 File Extension

- Extension: `.PhysicalSurf`
- Version: 3

### 6.2 Sample Files

```
worlds/continent3/tile/x-2/y-2/2018e_bridgeok_ptile.PhysicalSurf (336 bytes)
worlds/continent3/tile/x-6/y0/base_visuals.PhysicalSurf (20 bytes)
worlds/continent3/tile/x-6/y-2/base_visuals.PhysicalSurf (564 bytes)
```

### 6.3 Purpose

- Maps blend texture layers to physical surface types
- Used for: footsteps, vehicle handling, audio cues
- Links material IDs to physics properties

---

## 7. QuadTileData (quad_N.bin)

### 7.1 Observed Files

```
worlds/continent3/tile/x4/y2/quad_0.bin (424,212 bytes)
worlds/continent3/tile/x-8/y3/quad_0.bin (131,240 bytes)
```

### 7.2 Purpose

- LOD (Level of Detail) data for terrain
- "Quad" naming suggests quadtree-based subdivision
- Multiple quad files per tile possible (quad_0, quad_1, etc.)

---

## 8. Terrain Tile Size Analysis

### 8.1 Observed Tile File Sizes

| File | Size (bytes) | Description |
|------|--------------|-------------|
| height.bin | 49,973 | Heightfield data |
| blend.bin | 35,948 | Blend texture data |
| blend.Texture | 8,510 | Texture metadata |
| base_tile.bin | 340,064 | Collision mesh |
| base_ptile.bin | 11,104 | Pathfinding data |

### 8.2 Prior Estimate vs Actual

**Prior estimate (from bundle analysis):**
- Heightfield per tile: 512 KB

**Actual extracted sizes:**
- Heightfield: 2KB to 50KB (varies by tile complexity)
- Blend: 2KB to 130KB

**Conclusion:**
- 512KB estimate was for uncompressed bundle data, not individual tiles
- Compression in DFPF bundles inflates apparent size
- Actual tile data is much smaller when decompressed

---

## 9. World Coordinate System

### 9.1 Tile Dimensions

- Tiles are not fixed size in world units
- Each tile contains full terrain mesh for its area
- Edge matching handled by shared vertices

### 9.2 World Origin

- Origin (0,0) tile at center of world
- Negative coordinates: SW quadrant
- Positive coordinates: NE quadrant
- No fixed world origin point discovered yet

### 9.3 World Extent

From bundle analysis (RgS_World):
- **continent3:** ~12x16 tile grid (-8 to +6 X, -8 to +7 Y)
- **DLC regions:** Smaller, typically 5-8 tiles

---

## 10. Resource Type Registry

From DFPF bundle manifest analysis:

| Type Index | Resource | Version | Hash |
|------------|----------|---------|------|
| 3 | Heightfield | 36 | 0x263f5813 |
| 5 | QuadTileData | 19 | 0x7c9651ff |
| 14 | TerrainMaterial | 3 | 0x3a83c2fc |
| 15 | LevelData | 6 | 0x2527f4a6 |
| 18 | PhysicalSurfaceMap | 3 | 0xc1c9fdc6 |
| 20 | CollisionShape | 6022 | 0xe6158ebb |
| 21 | PathTileData | 50 | 0x458bd6dd |

---

## 11. Next Steps

### 11.1 Immediate Research

- [ ] Confirm height.bin data interpretation (material indices vs heights)
- [ ] Analyze relationship between height.bin and base_tile.bin
- [ ] Determine if height data is embedded in collision mesh
- [ ] Parse QuadTileData structure for LOD system

### 11.2 Tool Development

- [ ] Heightfield parser (decode material indices)
- [ ] Collision mesh viewer (Havok format)
- [ ] Terrain texture unpacker (DXT5 extraction)
- [ ] Tile coordinate calculator (world position → tile)

### 11.3 Open Questions

1. How is raw height (Y coordinate) determined per vertex?
2. What is the exact format of material index encoding?
3. How are tile seams handled at edges?
4. What is the BVXD/BIXD format marker encoding?

---

## 12. Reference Materials

### 12.1 Related Documents

| Document | Path |
|----------|------|
| World Analysis | docs/formats/WORLD_ANALYSIS.md |
| DFPF Format | docs/formats/DFPF_ANALYSIS.md |
| Format Index | docs/formats/FORMAT_INDEX.md |

### 12.2 External References

- [Havok Physics Documentation](https://www.havok.com/physics/)
- [DXT Texture Compression](https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide)

---

## 13. Additional Findings (2026-04-01)

### 13.1 DDS-Based Heightfield Format

Two 512KB Heightfield files were found:
- `file_2325_offset_280576.Heightfield`
- `file_4144_offset_1565440.Heightfield`

**Analysis Results:**
- First non-zero byte at offset 0x45532
- 99.92% of file is zeros (sparse data or extraction artifact)
- Not raw heightmap data

**DDS-Based Format Structure (file_0106):**

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 16 | Custom Header | Zeros except 0x08=0x0B |
| 0x10 | 4 | Width | 128 |
| 0x14 | 4 | Height | 128 |
| 0x1C | 4 | Flags | 0x08000000 |
| 0x20 | 4 | Magic | "rtxT" (Texture backwards) |
| 0x24 | 4 | Size | 22000 |
| 0x28 | 128 | DDS Header | Standard DDS header |
| 0xA8 | 16384 | DXT5 Data | 128x128 compressed texture |
| 0x40A8 | 5488 | Extra Data | Additional binary (possibly heights) |

**128KB Heightfield Files:**
- `file_0946_offset_1771776.Heightfield` and similar
- Likely DXT5 texture at higher resolution

### 13.2 HSEM Format Clarification

Files like `file_0204_offset_615936.Heightfield` are **mesh/object containers**, NOT heightfield data:

| Offset | Field | Description |
|--------|-------|-------------|
| 0x00 | Magic | "hsem" (mesh backwards) |
| 0x50 | Magic | "lrtm" (mtrl backwards) |
| 0x58+ | String | Material paths |

Examples of embedded paths:
- `environments/materials/ambientmeshes/groundleaves`
- `environments/materials/ambientmeshes/spiderlairentranceclump`

### 13.3 Heightfield Count

Total .Heightfield files in RgS_World: **244 files**

Size distribution:
- 512KB: 2 files (possibly sparse/extraction issues)
- 128KB: ~10 files (DXT5 texture)
- 22KB: ~30 files (DXT5 + metadata)
- 2-4KB: ~200 files (mesh/object references)

---

## 14. File Format Summary

### 14.1 Heightfield Container

```
height.bin {
    header: "hsem" + metadata
    data: uint16[?] material_layer_indices
}
```

### 14.2 Blend/Texture Container

```
blend.bin {
    header: "hsem" + material_refs
    data: DXT5 compressed texture
}

blend.Texture {
    header: metadata + path_references
}
```

### 14.3 Collision Container

```
base_tile.bin {
    header: Havok-6.1.0-r1 magic
    sections: __classnames__, __types__, __data__
    data: vertex_buffer + index_buffer
}
```

---

*Document generated as part of Brutal Legend reverse engineering project*
*Repository: brutal-legend-re*
*Last updated: 2026-04-01*
