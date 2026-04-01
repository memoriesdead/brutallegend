# Brutal Legend Reverse Engineering - Progress Report

**Last Updated:** 2026-04-01  
**Status:** Phase 1 - Foundation (In Progress)  
**Team:** Expert Reverse Engineering Team  

---

## Executive Summary

This document tracks the progress of the Brutal Legend reverse engineering project. We are systematically documenting and reverse engineering Double Fine's proprietary "Buddha" engine to enable community modding, new content creation, and ultimately a level editor.

---

## What We Know About the Game

| Attribute | Details |
|-----------|---------|
| **Game** | Brütal Legend |
| **Developer** | Double Fine Productions |
| **Publisher** | Electronic Arts |
| **Release** | October 2009 (PS3/Xbox 360), February 2013 (PC) |
| **Engine** | Buddha (proprietary, unnamed until community) |
| **Platform** | Windows (Steam), PlayStation 3, Xbox 360 |
| **Genre** | Action-adventure with RTS (Stage Battle) |

---

## Known Middleware

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Audio** | FMOD | FSB sound banks, custom encryption key: `DFm3t4lFTW` |
| **Physics** | Havok | Expected for 2009 era games |
| **UI** | Scaleform GFx | Unconfirmed |
| **Video** | Bink | Cutscenes |
| **Compression** | ZLib | Used in DFPF containers |
| **Scripting** | Lua | Mission scripts in `.lua` format |

---

## Project Structure

```
brutal-legend-re/
├── README.md                      # Project overview
├── TODO.md                        # Master task list
├── LICENSE                        # MIT License
├── CONTRIBUTING.md                # Contribution guidelines
│
├── docs/
│   ├── README.md                  # Documentation index
│   ├── PROGRESS.md               # This file
│   │
│   ├── formats/
│   │   ├── DFPF_SPEC.md          # Container format spec
│   │   ├── DFPF_ANALYSIS.md      # Detailed format analysis (413 lines)
│   │   ├── PROTO_SPEC.md          # Prototype format (placeholder)
│   │   ├── MISSION_API.md        # Mission scripting (placeholder)
│   │   ├── TERRAIN_SPEC.md       # Map/terrain (placeholder)
│   │   ├── ANIM_FORMAT.md        # Animation format (placeholder)
│   │   ├── AUDIO_SPEC.md         # Audio format spec
│   │   └── FILETYPES.md          # File type inventory
│   │
│   ├── engine/
│   │   ├── ARCHITECTURE.md       # Engine architecture overview
│   │   ├── FUNCTION_CATALOG.md    # Discovered functions (empty)
│   │   ├── LUA_ENGINE.md         # Lua integration (placeholder)
│   │   └── MIDDLEWARE.md        # Middleware notes
│   │
│   └── tutorials/
│       ├── 01_GETTING_STARTED.md
│       ├── 02_EXTRACTING_ASSETS.md
│       ├── 03_CREATING_A_MOD.md
│       └── 04_ADVANCED_REVERSING.md
│
├── tools/
│   ├── dfpf-toolkit/
│   │   ├── dfpf_v5.ksy          # Kaitai Struct spec (CREATED)
│   │   └── README.md
│   ├── buddha-mod/              # (reserved)
│   ├── proto-editor/            # (reserved)
│   ├── mission-builder/         # (reserved)
│   ├── buddha-forge/            # (reserved)
│   └── reference/
│       └── DoubleFine-Explorer/ # Cloned reference (CREATED)
│
├── ghidra/
│   └── scripts/                  # (reserved)
│
└── x64dbg/
    └── traces/                  # (reserved)
```

---

## Accomplishments (Session 1)

### ✅ Completed

| Task | Status | Details |
|------|--------|---------|
| Project structure | ✅ Complete | Full directory tree created |
| README/TODO | ✅ Complete | 500+ line TODO with phases |
| MIT License | ✅ Complete | Permissive license for Steam |
| CONTRIBUTING.md | ✅ Complete | Guidelines for contributors |
| Documentation framework | ✅ Complete | All placeholder docs created |

### ✅ Created Files (This Session)

| File | Size | Description |
|------|------|-------------|
| `docs/formats/DFPF_ANALYSIS.md` | 413 lines | **Comprehensive DFPF V5 format documentation** |
| `tools/dfpf-toolkit/dfpf_v5.ksy` | ~4.7KB | **Kaitai Struct specification** |
| `tools/reference/DoubleFine-Explorer/` | Full repo | **Cloned Pascal source** |

---

## DFPF Container Format - Key Findings

### What is DFPF?
DFPF (Double-Fine Pack File) is the container format used by Buddha engine. Files come in pairs:
- `filename.~h` - Header/index file
- `filename.~p` - Data payload file

### Brutal Legend Specifics (V5)

| Field | Value |
|-------|-------|
| **Magic** | `dfpf` (4 bytes at offset 0) |
| **Version** | 0x05 (V5 for Brutal Legend) |
| **Endian** | Big-endian |
| **Header Size** | 88 bytes |
| **File Records** | 16 bytes each with bit-shifted fields |

### Compression Types

| Type | Name | Notes |
|------|------|-------|
| 1 | Uncompressed (V6) | Later games |
| 2 | ZLib (V2) | Costume Quest |
| 4 | Uncompressed (V5) | Brutal Legend |
| 8 | ZLib (V5) | Brutal Legend (common) |
| 12 | XMemCompress | Xbox360 only |

### Bit-Field Structure (16-byte file record)
```
DWord 0: Uncompressed Size = value >> 8
DWord 1: Name Offset = value >> 11
DWord 2: Offset = value >> 3, Size = (value << 5) >> 9
DWord 3: File Type Index = ((value << 4) >> 24) >> 1
Byte 15: Compression Type = raw_bytes[15] & 0x0F
```

---

## Game Installation Status

### ⚠️ CRITICAL: Game Not Currently Installed

The Brutal Legend Steam installation was **NOT found** on this machine.

**Searched Locations:**
- `C:\Program Files (x86)\Steam\steamapps\common\Brutal Legend\` ❌
- `C:\Program Files\Steam\steamapps\common\Brutal Legend\` ❌
- Registry showed Steam at standard Steam installation path

**Recoverable Files Found:**
- `BrutalLegend.exe` - In Windows Recycle Bin (inaccessible)
- Multiple `.fev` audio config files - In Recycle Bin
- `BrutalLegendModManagerSetup.msi` - Mod manager installer in Recycle Bin

### Required Action
**Reinstall Brutal Legend from Steam before executable analysis can proceed.**

---

## Toolchain Status

| Tool | Status | Notes |
|------|--------|-------|
| **Ghidra** | 🔴 Not Installed | Needed for executable analysis |
| **x64dbg** | 🔴 Not Installed | Needed for dynamic analysis |
| **ImHex** | 🔴 Not Installed | Hex editor for binary analysis |
| **rizin/Cutter** | 🔴 Not Installed | Alternative RE framework |
| **Visual Studio 2022** | 🔴 Not Installed | For C++ tool development |
| **Python 3.10+** | 🔴 Not Installed | For scripting/automation |
| **Kaitai Struct** | ⚠️ Spec Created | Parser generation ready |

---

## Known File Types

| Extension | Type | Editable |
|-----------|------|----------|
| `.~h` / `.~p` | DFPF container | ✅ Yes (with tools) |
| `.proto` | Prototype definitions | ✅ Yes (text) |
| `.lua` | Mission scripts | ✅ Yes |
| `.fsb` | FMOD audio | ⚠️ Partial (encrypted) |
| `.dds` | Textures | ✅ Yes (replace) |
| `.bik` | Bink video | ❌ No |

---

## Reference Materials

### DoubleFine Explorer (bgbennyboy)
- **GitHub:** https://github.com/bgbennyboy/DoubleFine-Explorer
- **Source:** Cloned to `tools/reference/DoubleFine-Explorer/`
- **License:** Mozilla Public License 2.0
- **Language:** Pascal/Delphi
- **Contains:** Complete DFPF format implementation

### Kaitai Struct
- **Website:** https://kaitai.io/
- **Spec Created:** `tools/dfpf-toolkit/dfpf_v5.ksy`
- **Generates:** Python, C++, Java parsers

---

## Immediate Next Steps

### Before Executable Analysis
- [ ] **Reinstall Brutal Legend from Steam**

### Phase 1 Tasks Remaining
- [ ] Run `dumpbin /imports` on BrutalLegend.exe
- [ ] Load executable in Ghidra, run full analysis
- [ ] Verify middleware presence (FMOD, Havok, Scaleform)
- [ ] Extract all game bundles

### Phase 2 (Executable Analysis)
- [ ] Identify DFPF loading functions
- [ ] Identify Lua engine functions
- [ ] Identify prototype system
- [ ] Identify Stage Battle RTS logic
- [ ] Build function catalog (target: 100+ functions)

---

## Milestone Progress

| Milestone | Target | Status |
|-----------|--------|--------|
| M1: Foundation | Week 1 | 🔴 In Progress |
| M2: 100+ Functions | Week 4 | 🔴 Not Started |
| M3: Format Specs Complete | Week 8 | 🔴 Not Started |
| M4: Core Tools Functional | Week 12 | 🔴 Not Started |
| M5: Mod Loader + Steam SDK | Week 20 | 🔴 Not Started |
| M6: Level Editor + Public | Week 24+ | 🔴 Not Started |

---

## Team Status

| Role | Assigned | Status |
|------|---------|--------|
| RE Lead | TBD | 🔴 Open |
| Ghidra Analysis | TBD | 🔴 Open |
| x64dbg Tracing | TBD | 🔴 Open |
| C++ Development | TBD | 🔴 Open |
| Python/Scripts | TBD | 🔴 Open |
| Documentation | TBD | 🔴 Open |

---

## Discord

**Server:** TBD  
**Recruitment:** Not started

---

## License

This project is licensed under MIT. All tools created will be open source.

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## References

- DoubleFine Explorer: https://github.com/bgbennyboy/DoubleFine-Explorer
- Kaitai Struct: https://kaitai.io/
- Ghidra: https://ghidra-sre.org/
- x64dbg: https://x64dbg.com/
- ImHex: https://github.com/WerWolv/ImHex
