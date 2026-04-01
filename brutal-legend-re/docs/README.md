# Brutal Legend Documentation

**Project:** Brutal Legend Reverse Engineering  
**Last Updated:** 2026-04-01  
**Status:** Phase 2-3 ~75% Complete

---

## Quick Links

| Document | Description |
|----------|-------------|
| [TODO.md](../TODO.md) | Master task list with all phases |
| [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md) | Project overview and key findings |
| [PROJECT_STATUS.md](./PROJECT_STATUS.md) | Real-time status of everything |
| [PROGRESS.md](./PROGRESS.md) | Detailed progress report |

---

## Format Documentation

| Format | Status | Document | Key Finding |
|--------|--------|----------|-------------|
| **DFPF Container** | ✅ Complete | [DFPF_ANALYSIS.md](./formats/DFPF_ANALYSIS.md) | V5 format, 88B header, 16B records |
| **Mission/Lua** | ✅ Complete | [MISSION_API.md](./formats/MISSION_API.md) | **266 scripts, full API discovered** |
| **Mission System** | ✅ Complete | [MISSION_ANALYSIS.md](./formats/MISSION_ANALYSIS.md) | **240 missions identified** |
| **Audio/FMOD** | ✅ Complete | [AUDIO_SPEC.md](./formats/AUDIO_SPEC.md) | **156 FSB files, 4.1 GB** |
| **World/Terrain** | ✅ Complete | [WORLD_ANALYSIS.md](./formats/WORLD_ANALYSIS.md) | **Tile streaming, Heightfield format** |
| **Model Format** | ✅ Complete | [MODEL_FORMAT.md](./formats/MODEL_FORMAT.md) | **MeshSet V8 format** |
| **Animation** | ✅ Complete | [ANIM_FORMAT.md](./formats/ANIM_FORMAT.md) | **ComboAnim/ComboPose system** |
| **Video** | ✅ Complete | [VIDEO_SPEC.md](./formats/VIDEO_SPEC.md) | **192 .bik files, 2.7 GB, Bink 2** |
| **UI** | ✅ Complete | [UI_FORMAT.md](./formats/UI_FORMAT.md) | **80 .gfx files, Scaleform GFx 3.x** |
| **Prototype** | 🔄 Partial | [PROTO_SPEC.md](./formats/PROTO_SPEC.md) | Needs all.proto extraction |
| **Terrain Spec** | 🔄 Partial | [TERRAIN_SPEC.md](./formats/TERRAIN_SPEC.md) | Needs heightfield analysis |

---

## Engine Documentation

| System | Status | Document | Key Finding |
|--------|--------|----------|-------------|
| **Executable** | ✅ Complete | [EXPORT_TABLE.md](../ghidra/EXPORT_TABLE.md) | **611 exports, 27KB** |
| **Imports** | ✅ Complete | [IMPORT_TABLE.md](../ghidra/IMPORT_TABLE.md) | **21KB, 19 DLLs** |
| **Strings** | ✅ Complete | [STRING_CATALOG.md](../ghidra/STRING_CATALOG.md) | **30KB strings cataloged** |
| **Architecture** | ✅ Complete | [ARCHITECTURE.md](./engine/ARCHITECTURE.md) | Buddha engine overview |
| **Middleware** | ✅ Updated | [MIDDLEWARE.md](./engine/MIDDLEWARE.md) | **Scaleform GFx 3.x confirmed** |
| **Function Catalog** | 🔄 Partial | [FUNCTION_CATALOG.md](./engine/FUNCTION_CATALOG.md) | Needs full analysis |
| **Lua Engine** | ✅ Discovered | Via string analysis | Embedded Lua 5.x |

---

## Game File Inventory

| Metric | Value |
|--------|-------|
| **Total Files** | 546 |
| **Total Size** | 8.06 GB |
| **DFPF Bundles** | 42 pairs |
| **Lua Scripts** | 266 |
| **Missions** | 240 |
| **FSB Audio** | 156 files (4.1 GB) |
| **Video** | 192 .bik files (2.7 GB) |
| **UI Files** | 80 .gfx |

---

## Tutorials

| Tutorial | Status |
|----------|--------|
| [01_GETTING_STARTED.md](./tutorials/01_GETTING_STARTED.md) | 🟡 Updated |
| [02_EXTRACTING_ASSETS.md](./tutorials/02_EXTRACTING_ASSETS.md) | 🟡 Updated |
| [03_CREATING_A_MOD.md](./tutorials/03_CREATING_A_MOD.md) | 🟡 Updated |
| [04_ADVANCED_REVERSING.md](./tutorials/04_ADVANCED_REVERSING.md) | 🔴 |

---

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Foundation | ✅ Complete |
| 2 | Executable Analysis | ✅ ~75% Complete |
| 3 | Format Specifications | ✅ ~75% Complete |
| 4 | Core Tools | 🔴 Not Started |
| 5 | Mod Loader | 🔴 Not Started |
| 6 | Level Editor | 🔴 Not Started |

---

## Key Achievements (This Session)

- ✅ **611 Buddha.exe exports documented** (27KB table)
- ✅ **266 Lua scripts extracted and analyzed**
- ✅ **240 missions identified with full API** (game.*, dialog.*, hud.*, rtti.*)
- ✅ **156 FSB audio files (4.1 GB) cataloged**
- ✅ **192 .bik video files (2.7 GB) cataloged**
- ✅ **80 .gfx UI files cataloged** (Scaleform GFx 3.x confirmed)
- ✅ **Tile-based world streaming discovered**
- ✅ **Heightfield terrain format identified** (512KB/tile, 257x257 16-bit)
- ✅ **MeshSet V8 model format documented**
- ✅ **Python DFPF extractor created** (dfpf_extract.py)
- ✅ **All documentation updated**

---

## Key Findings

### Executable (BrutalLegend.exe)
- **Size:** 13,180,928 bytes (x86)
- **Internal Name:** Buddha.exe
- **Build Date:** 2013-05-06
- **Entry Point:** 0x88c8ae
- **FMOD:** Embedded (not external DLL)
- **Lua:** Embedded (not external DLL)
- **SDL:** SDL 2.x (611 functions exported)
- **Scaleform:** GFxLoader confirmed
- **Exports:** 611 Buddha.exe functions

### DFPF Container (V5)
- **Version:** V5 (Brutal Legend specific)
- **Endianness:** Big-endian
- **Header:** 88 bytes
- **File Records:** 16 bytes each with bit-shifting
- **Compression:** ZLib (type 8), Uncompressed (type 4), XMemCompress (type 12)

### Audio Encryption
- **Key:** `DFm3t4lFTW` (hex: 44 46 6D 33 74 34 6C 46 54 57)
- **Algorithm:** Bit-reverse + XOR

### World/Terrain System
- **Type:** Tile-based streaming
- **Tile Size:** 512KB per Heightfield tile
- **Grid:** worlds/continent3/tile/x{coord}/y{coord}/
- **Layers:** height, blend, occlusion, base_tile, base_ptile, base_objects
- **Formats:** Heightfield (v36), CollisionShape (v6022), PathTileData (v50)

### Mission System
- **Format:** PPAK + Lua 5.x
- **Scripts:** 266 Lua files
- **API:** game.*, dialog.*, hud.*, rtti.*, music.*, sound.*
- **Callbacks:** OnMissionStart, OnMissionComplete, OnKilled, OnTimerExpired, OnTriggerEntered

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| M1: Foundation | Week 1 | ✅ Complete |
| M2: Executable Analysis | Week 2 | ✅ ~75% Complete |
| M3: Format Specs 75%+ | Week 3 | ✅ Complete |
| M4: Core Tools Functional | Week 12 | 🔴 Not Started |
| M5: Mod Loader + Steam SDK | Week 20 | 🔴 Not Started |
| M6: Level Editor + Public | Week 24+ | 🔴 Not Started |

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

---

## References

- [DoubleFine Explorer](https://github.com/bgbennyboy/DoubleFine-Explorer)
- [Kaitai Struct](https://kaitai.io/)
- [Ghidra](https://ghidra-sre.org/)
- [FMOD](https://www.fmod.com/)
- [Bink Video](https://www.radgametools.com/bink/)
- [Scaleform](http://www.scaleform.com/)

---

*Last updated: 2026-04-01 - Session 1 Complete*
