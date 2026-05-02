# Brutal Legend Modding Docs

## File Formats

### DFPF V5 (.~h/.~p pairs)
Game data bundles - header + data separation.
- Header: 96 bytes (magic + version + 88-byte struct)
- Struct: file_ext_offset, name_dir_offset, num_files, marker
- File record: 16 bytes each (uncompressed_size, name_offset, offset, size, type_index, compression)
- **CRITICAL FIX**: file_type_index encoding is `(d3 >> 20) & 0xFF` NOT `(d3 >> 21)` or `(d3 >> 24)`

### Terrain (worlds/continent3/tile/x/y/)
| File | Format |
|------|--------|
| height.Heightfield | DDS DXT5 (40-byte header + DXT5, height in alpha) |
| height.bin | HSEM mesh format (material indices) |
| blend.bin | Material blend data |
| base_tile.bin | Havok collision mesh |

### Heightfield DDS Format
- 40-byte custom header (rtxT magic at 0x20)
- 128-byte DDS header
- DXT5 compressed (256x256, height in alpha channel 0-255)

### LevelData Binary Format
- Magic: `rdHp` at bytes 0-3
- Version 6 stored as big-endian uint32 at offset ~144
- Contains binary header + embedded tile path strings
- Paths reference tiles like `worlds/<mapname>/tile/x<coord>/y<coord>/<layer>`
- ZLIB compressed when stored in bundle

## Tools

### custom_map_pipeline.py
```bash
python custom_map_pipeline.py --map-name MyMap --tile-x 0 --tile-y 0 --preset mountain -o Win/Mods
python custom_map_pipeline.py --map-name Flat --tile-x 1 --tile-y 1 --operation set_all --height 128
```

Presets: mountain, valley, plateau, flat

### terrain_editor.py
```bash
python terrain_editor.py tile.Heightfield --show
python terrain_editor.py tile.Heightfield --raise-area 128 128 30 80
python terrain_editor.py tile.Heightfield --smooth 0.3
python terrain_editor.py tile.Heightfield --flatten 128 128 150
```

### dfpf_extract.py
```bash
python dfpf_extract.py RgS_World.~h
python dfpf_extract.py RgS_World.~h --name "worlds/continent3/tile/x-8/y-8/height.Heightfield"
```

### dfpf_repack.py
```bash
python dfpf_repack.py original.~h extracted_dir output_name
```

## Mod Loader

### Files
- `load_mod.exe` - Launches game + injects DLL
- `buddha_mod.dll` - IAT hook (CreateFileA/W → Win/Mods/ override)

### How It Works
1. IAT hook patches kernel32!CreateFileA/W
2. When game opens a file, checks `Win/Mods/` first
3. If found there, returns mod file instead of original

### Build
```bash
cd BrutalLegend
rebuild.bat   # uses MSVC x86
```

### Test
```bash
load_mod.exe  # auto-launches game + injects
```

Check `buddha_mod.log` for injection status.

## Directory Structure

```
BrutalLegend/
├── Win/Packs/           # Original game bundles
├── Win/Mods/            # Override files (mod loader checks here first)
│   ├── RgS_CustomMap.~h
│   └── RgS_CustomMap.~p
├── load_mod.exe
└── buddha_mod.dll
```

## Game Bundle Format (DFPF V5)

```
.~h header:
  0x00: "dfpf" magic
  0x04: version (5)
  0x05: padding (3 bytes)
  0x08: 88-byte header struct

Header struct:
  +0x00 (8): file_ext_offset
  +0x08 (8): name_dir_offset
  +0x10 (4): file_extension_count
  +0x14 (4): name_dir_size
  +0x18 (4): num_files
  +0x1C (4): marker (0x23A1CEAB)

File record (16 bytes each):
  dword0: uncompressed_size << 8
  dword1: name_offset << 11
  dword2: offset << 3  (size is derived as offset >> 1)
  dword3: (type_index << 20) | (compression & 0x0F)

Extensions: 16 bytes each (4 len + name + 12 padding)
```

## Multiplayer Map Discovery

### How Maps Are Found
From BuddhaDefault.cfg:
```lua
devMaps = {
    { "EmptyTestRoom", "Worlds/EmptyTestRoom/EmptyTestRoom.LevelData" },
}
```

Format: `{ "MapName", "Worlds/MapName/MapName.LevelData" }`

1. Game scans bundles for `Worlds/<mapname>/<mapname>.LevelData` pattern
2. LevelData file provides map metadata and tile references
3. UI Flash files (`ui/flash/frontend/map_<name>`) define MP map thumbnails
4. C++ `LevelList` class manages map enumeration

### Skirmish Maps
- Terrain tiles stored in `RgB_World.~h/.~p` bundle (not RgS_World2)
  - sk_1 through sk_9 each have ~285-320 tiles in 9x9 grid
  - Tiles at `worlds/sk_<N>/tile/x<coord>/y<coord>/<layer>.*`
- MeshSet metadata stored in `Man_Trivial.~h/.~p` at `worlds/sk_<N>/sk_<N>.MusicNameTable`
- UI references `map_sk1` through `map_sk9` (thumbnails)
- Bundle loading uses internal GSysFile::Open (NOT CreateFileA/W)

### Map Requirements
1. **LevelData** - `Worlds/<mapname>/<mapname>.LevelData` (MeshSet or binary format)
2. **Terrain tiles** - `worlds/<map>/tile/x<coord>/y<coord>/height.Heightfield`
3. **Collision** - `worlds/<map>/tile/x<coord>/y<coord>/base_tile.bin` (Havok)
4. **Materials** - `worlds/<map>/tile/x<coord>/y<coord>/blend.*`

### TestCustom Map Status
- **Created** LevelData at `Win/Mods/Worlds/TestCustom/TestCustom.LevelData` (111KB)
- **Created** Terrain bundle at `Win/Mods/RgS_Testcustom.~h/.~p` (291 files, 9x9 tile grid)
- **Modified** BuddhaDefault.cfg at `Win/Mods/Config/BuddhaDefault.cfg` with TestCustom and Custom in devMaps
- **Bundle structure**: worlds/TestCustom/tile/x-4 to x4, y-4 to y4 (complete 9x9 grid)
- **MeshSet**: worlds/TestCustom/TestCustom.MusicNameTable (text format)
- **ISSUE**: Bundle files opened via GSysFile::Open, not CreateFileA/W - mod loader hook cannot redirect bundles

## Known Issues

1. **load_mod.exe needs admin** for process injection
2. **DXT5 encoding** may not be perfect - terrain looks "blocky"
3. **Collision meshes** not editable (Havok format)
4. **Pathfinding data** not editable (format unknown)
5. **Bundle redirection BLOCKER** - Game opens bundles via GSysFile::Open (internal), NOT CreateFileA/W. **ACTIVE WORK**: Deploying agents to find GSysFile::Open vtable offset for hooking.

## Active Work: GSysFile::Open Hook (2026-04-01)

**Goal**: Hook GSysFile::Open to redirect bundle file opens to Win/Mods/

**Agents Deployed**:
- Agent 1: Find GSysFile::Open vtable offset in BrutalLegend.exe (a012a15b577d35b4d)
- Agent 2: Analyze GSysFile class hierarchy (af2b33eb38a0c57ab)

**Next Steps**:
1. Get vtable offset from agents
2. Build hook DLL that patches GSysFile vtable
3. Test that Win/Mods/ bundles are found
4. Verify TestCustom appears in MP
