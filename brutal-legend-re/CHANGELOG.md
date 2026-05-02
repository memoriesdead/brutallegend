# Brutal Legend RE - Change Log

## 2026-04-01 (Continued)

### Multiplayer Map Research Complete
- **MeshSet format fully documented** - Text format `MeshSet{Key=Value;...}` with LODData arrays
- **Map discovery mechanism understood** - LevelList class scans bundles for `Worlds/<map>/<map>.LevelData`
- **Bundle loading bypasses CreateFileA/W** - Game uses GSysFile::Open internally, not CreateFileA/W
- **Config file redirection works** - Mod loader hooks CreateFileA/W, configs can be overridden

### TestCustom Map Bundle Created
- `Win/Mods/RgS_Testcustom.~h/.~p` - Complete 291-file bundle
- 8x8 tile grid (x-4 to x3, y-4 to y3) from sk_1 template
- MeshSet at `worlds/TestCustom/TestCustom.MusicNameTable`
- Climate data (day/night/sunrise/sunset)
- `Win/Mods/Worlds/TestCustom/TestCustom.LevelData` - LevelData (111KB)
- `Win/Mods/Config/BuddhaDefault.cfg` - Modified with TestCustom in devMaps

### MeshSet Text Format
```
MeshSet{HighMipForceDistance=0;_NonMagicalLODCache=[LODData{Flags=1073;MaxJoint=-1;Mesh=@path;Materials=[@mat1,@mat2];},LODData{Flags=0...}...];_BoundingBox=<<x,y,z>,<x,y,z>>;VisualType=kVT_SetDressing;}
```

## 2026-04-01

### Tools Built
- `tools/dfpf-toolkit/dfpf_extract.py` - Extracts DFPF V5 bundles
- `tools/dfpf-toolkit/dfpf_repack.py` - Repacks DFPF V5 bundles
- `tools/terrain-editor/terrain_editor.py` - Edit DDS heightfield terrain
- `tools/map-pipeline/custom_map_pipeline.py` - Create custom map bundles

### Mod Loader (WORKING)
- `load_mod.exe` - Auto-launches BrutalLegend.exe + injects DLL
- `buddha_mod.dll` - IAT hook for file override (redirects to Win/Mods/)
- Verified 32-bit DLL loads successfully at 0x67880000
- Log file `buddha_mod.log` created on injection

### Critical Bug Fixes
- dfpf_extract.py: file_type_index formula corrected to `(d3 >> 20) & 0xFF`
- dfpf_repack.py: encoder corrected to `file_type_index << 20` (not `* 2 << 20`)
- dfpf_extract.py: Extension handling fixed (was causing empty names)
- custom_map_pipeline.py & create_test_map.py: Same encoder fix applied

### LevelData Discovery
- LevelData binary format found at `worlds/<mapname>/<mapname>` in RgB_World bundle
- Magic: `rdHp` at bytes 0-3
- Version 6 at offset ~144 (big-endian uint32)
- Contains tile path references for map tiles
- ZLIB compressed when stored
- Extracted to `Win/Mods/LevelData_TestCustom.bin`

### MP Map Discovery (UPDATED)
- From BuddhaDefault.cfg: `{ "MapName", "Worlds/MapName/MapName.LevelData" }` format
- Game scans for LevelData at `Worlds/<mapname>/<mapname>.LevelData`
- Skirmish maps use MeshSet text format (not binary LevelData)
- 3 agents deployed to solve MP map loading:
  1. Parse MeshSet format from sk_1-sk_9
  2. Build complete TestCustom map from sk_1 template
  3. Investigate map registration in configs

### Custom Maps Created
- `Win/Mods/RgS_Testcustom.~h/.~p` - Mountain terrain (5 tiles)
- `Win/Mods/Worlds/TestCustom/TestCustom.LevelData` - LevelData placeholder
- `Win/Mods/LevelData_TestCustom.bin` - LevelData template

### Files in Game Directory
```
BrutalLegend/
├── load_mod.exe      (32-bit, auto-launch + inject)
├── buddha_mod.dll    (32-bit, IAT hook mod loader)
├── Win/Mods/
│   ├── RgS_Testcustom.~h/.~p  (custom mountain map)
│   ├── LevelData_TestCustom.bin (LevelData template)
│   └── RgS_Testworld.~h/.~p  (original test map)
```

## 2026-03-31

### Initial Setup
- Created brutal-legend-re repository
- Documented DFPF V5 container format
- Documented terrain tile structure (worlds/continent3/tile/x/y/)
- Discovered heightfield stored as DXT5 texture (256x256)
