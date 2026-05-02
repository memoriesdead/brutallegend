# Format Document Index

**Project:** Brutal Legend Reverse Engineering  
**Last Updated:** 2026-04-01

---

## Overview

This index catalogs all format-related documentation in the project.

---

## Container Formats

### DFPF (Double-Fine Pack File)

| Document | Status | Description |
|----------|--------|-------------|
| [DFPF_ANALYSIS.md](./DFPF_ANALYSIS.md) | ✅ Complete | 413 lines - Full format analysis from DoubleFine Explorer source |
| [DFPF_SPEC.md](./DFPF_SPEC.md) | 🔄 Partial | Format specification (94 lines) |
| Kaitai Struct | ✅ Created | `tools/dfpf-toolkit/dfpf_v5.ksy` |

**Key Details:**
- Versions: V2 (Costume Quest), V5 (Brutal Legend), V6
- Structure: `.~h` (header) + `.~p` (data) pairs
- Endianness: Big-endian
- Compression: ZLib, XMemCompress

---

## Audio Formats

### FSB (FMOD Sound Bank)

| Document | Status | Description |
|----------|--------|-------------|
| [AUDIO_ANALYSIS.md](./AUDIO_ANALYSIS.md) | ✅ Complete | 151 lines - Full FSB5/FSB4 analysis |
| [AUDIO_SPEC.md](./AUDIO_SPEC.md) | 🔄 Partial | Audio format specification |

**Key Details:**
- Formats: FSB5, FSB4
- Encryption: Custom bit-reverse + XOR (`DFm3t4lFTW`)
- Codecs: PCM8, PCM16, MPEG

---

## Mission/Script Formats

### Mission System

| Document | Status | Description |
|----------|--------|-------------|
| [MISSION_ANALYSIS.md](./MISSION_ANALYSIS.md) | ✅ Research | 371 lines - Mission system analysis |
| [MISSION_API.md](./MISSION_API.md) | 🔴 Not Started | Mission scripting API |

**Key Details:**
- Bundle: `Man_Script.~h/.~p`
- Format: PPAK (custom archive format)
- Scripting: Lua (embedded bytecode)
- Contains: Mission Lua scripts, global scripts, quest scripts

### Lua Scripts

| Document | Status | Description |
|----------|--------|-------------|
| [LUA_ENGINE.md](../engine/LUA_ENGINE.md) | 🔴 Not Started | Lua engine integration |
| Mission API | 🔴 Not Started | Game-specific Lua functions |

**Note:** Lua is embedded in the executable (no external DLL)

---

## World/Terrain Formats

### World System

| Document | Status | Description |
|----------|--------|-------------|
| [WORLD_ANALYSIS.md](./WORLD_ANALYSIS.md) | 🔄 Research | 300 lines - World system analysis |
| [TERRAIN_SPEC.md](./TERRAIN_SPEC.md) | 🔴 Not Started | Terrain format specification |

**Key Details:**
- World Size: ~40 square miles
- System: Zone-based streaming
- Terrain Format: Unknown
- Zone Format: Unknown

---

## Prototype System

### Unit/Character Definitions

| Document | Status | Description |
|----------|--------|-------------|
| [PROTO_SPEC.md](./PROTO_SPEC.md) | 🔴 Not Started | Prototype format specification |

**Key Details:**
- File: `all.proto` in `00Startup.~h/.~p`
- Contains: Unit, character, vehicle definitions
- Allows: Character/faction swaps
- Community Example: Hair Metal Militia mod (ModDB)

---

## Animation Formats

### Skeleton/Animation Data

| Document | Status | Description |
|----------|--------|-------------|
| [ANIM_FORMAT.md](./ANIM_FORMAT.md) | 🔴 Not Started | Animation format specification |

---

## UI Formats

### User Interface

| Document | Status | Description |
|----------|--------|-------------|
| FILETYPES.md | 🔴 Not Started | UI file type inventory |

**Known UI Files:**
- Location: `Data/UI/` directory
- Format: `.gfx` Scaleform bundles
- Components: HUD, FrontEnd, Loading, Journal, Lore entries

---

## Video Formats

### Cutscene Videos

| Document | Status | Description |
|----------|--------|-------------|
| Middleware | 🔴 Not Started | Bink video documentation |

**Key Details:**
- Codec: Bink Video (binkw32.dll)
- Location: `Data/Cutscenes/` directory
- Extension: `.bik`
- Files: 40+ cutscene files

---

## Save Format

### Game Save Data

| Document | Status | Description |
|----------|--------|-------------|
| [SAVE_SYSTEM.md](../engine/SAVE_SYSTEM.md) | 🔄 Research | 313 lines - Save system investigation |

**Key Findings:**
- No `.sav` files in AppData
- `screen.dat` contains display settings only
- Saves may be on Steam Cloud
- Save format unknown

---

## File Type Inventory

### All Known File Types

| Extension | Type | Documented | Location |
|-----------|------|------------|----------|
| `.~h/.~p` | DFPF container | ✅ Yes | Win/Packs/ |
| `.lua` | Lua script | ✅ Yes | Man_Script.~h |
| `.fsb` | FMOD audio | ✅ Yes | Various |
| `.dds` | Texture | ❌ No | Various |
| `.bik` | Bink video | ❌ No | Data/Cutscenes/ |
| `.gfx` | Scaleform UI | ❌ No | Data/UI/ |
| `.proto` | Prototype | ❌ No | 00Startup.~h |
| `.Clumps` | Data clump | ❌ No | Data/ |
| `.ttf` | Font | ❌ No | Data/Fonts/ |
| `.cfg` | Config | ❌ No | Data/Config/ |

---

## Document Statistics

| Category | Count | Complete | Partial | Not Started |
|----------|-------|----------|---------|-------------|
| Container Formats | 1 | 1 | 1 | 0 |
| Audio Formats | 1 | 1 | 1 | 0 |
| Mission/Script | 2 | 1 | 0 | 1 |
| World/Terrain | 2 | 0 | 1 | 1 |
| Prototype | 1 | 0 | 0 | 1 |
| Animation | 1 | 0 | 0 | 1 |
| UI | 1 | 0 | 0 | 1 |
| Video | 1 | 0 | 0 | 1 |
| Save | 1 | 0 | 1 | 0 |
| **Total** | **11** | **3** | **5** | **6** |

---

## Reference Materials

### External Sources

| Source | Description |
|--------|-------------|
| [DoubleFine Explorer](https://github.com/bgbennyboy/DoubleFine-Explorer) | Pascal source code for DFPF/FSA handling |
| [Kaitai Struct](https://kaitai.io/) | Parser generation framework |
| [FMOD Documentation](https://www.fmod.com/docs/) | FMOD audio engine |
| [Bink Video](https://www.radgametools.com/bink/) | RAD Video Tools Bink codec |

### Internal Tools

| Tool | Location | Status |
|------|----------|--------|
| dfpf_v5.ksy | `tools/dfpf-toolkit/` | ✅ Created |
| DoubleFine Explorer | `tools/reference/DoubleFine-Explorer/` | ✅ Cloned |

---

## Related Documents

| Document | Path | Description |
|----------|------|-------------|
| Architecture | [ARCHITECTURE.md](../engine/ARCHITECTURE.md) | Buddha engine overview |
| Import Analysis | [IMPORT_ANALYSIS.md](../engine/IMPORT_ANALYSIS.md) | Executable imports |
| Progress | [PROGRESS.md](../PROGRESS.md) | Project progress |
| TODO | [TODO.md](../TODO.md) | Master task list |

---

*Last updated: 2026-04-01*
