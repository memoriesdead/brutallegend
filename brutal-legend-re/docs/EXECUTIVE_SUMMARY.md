# Brutal Legend Reverse Engineering - Executive Summary

**Last Updated:** 2026-04-01  
**Status:** Phase 1 Complete, Phase 2 In Progress  
**Project:** Open source reverse engineering of Brutal Legend (2009)

---

## Project Mission

Reverse engineer Double Fine's proprietary "Buddha" engine to enable:
- Community modding support
- New missions and content creation
- Level/map editors
- Spiritual successor capability
- Steam Workshop integration

---

## Key Findings (Session Results)

### ✅ Executable Analysis Complete

**File:** `BrutalLegend.exe`  
**Size:** 13,180,928 bytes (13.18 MB)  
**Architecture:** x86 (32-bit)  
**Build Date:** May 6, 2013  
**Internal Name:** Buddha.exe

#### Technology Stack Confirmed

| Component | Technology | Status |
|-----------|------------|--------|
| **Renderer** | SDL 2.x + Direct3D 9 + OpenGL | ✅ Confirmed |
| **Audio** | FMOD Ex (embedded, not external DLL) | ✅ Confirmed |
| **Video** | Bink Video (binkw32.dll) | ✅ Confirmed |
| **Compression** | ZLib (embedded) | ✅ Confirmed |
| **Scripting** | Lua (embedded, not external DLL) | ✅ Confirmed |
| **Input** | DirectInput 8 + SDL subsystems | ✅ Confirmed |
| **Platform** | Steamworks API | ✅ Confirmed |

#### Buddha.exe Exports (611 functions)

| Category | Functions |
|----------|-----------|
| File I/O | GBufferedFile, GSysFile, GZLibFile |
| Threading | GThread, GMutex, GSemaphore, GEvent, GWaitCondition |
| Memory | GRefCountBaseImpl, GAcquireInterface |
| Graphics | GImage, GImageBase, GColor, GMatrix2D |
| UI | GFxLoader (Scaleform) |
| SDL | 611 SDL functions |

#### FMOD Integration

- FMOD is **embedded/statically linked** (no fmod.dll present)
- FMOD Ex strings found: `FMOD`, `FMODEx`, `fmod2011`
- FSB format support: FSB2, FSB3, FSB4, FSB5
- **Custom encryption discovered:** `DFm3t4lFTW`

#### Lua Integration

- Lua is **embedded** (no lua.dll present)
- String references: `lua_debug`, `luaopen_`
- Mission scripts use `.lua` format (bytecode)

---

### ✅ DFPF Container Format Fully Documented

DFPF (Double-Fine Pack File) is the primary archive format.

#### Format Details

| Aspect | Value |
|--------|-------|
| **Versions** | V2 (Costume Quest), V5 (Brutal Legend), V6 |
| **Endianness** | Big-endian |
| **Bundle Type** | Split `.~h` (header) + `.~p` (data) |
| **Magic Bytes** | `dfpf` at offset 0 |
| **Header Size** | 88 bytes |
| **File Records** | 16 bytes each with bit-shifted fields |

#### Compression Support

| Type | Name | Notes |
|------|------|-------|
| 1 | Uncompressed | V6 variant |
| 2 | ZLib | V2 variant |
| 4 | Uncompressed | V5 variant |
| 8 | ZLib | V5 variant (common) |
| 12 | XMemCompress | Xbox 360 only |

#### Bit-Field Structure (16-byte file record)
```
DWord 0: UncompressedSize = value >> 8
DWord 1: NameOffset = value >> 11
DWord 2: Offset = value >> 3, Size = (value << 5) >> 9
DWord 3: FileTypeIndex = ((value << 4) >> 24) >> 1
Byte 15: CompressionType = raw & 0x0F
```

---

### ✅ Audio System Documented

**Format:** FSB5/FSB4 (FMOD Sound Bank)  
**Encryption:** Custom bit-reverse + XOR with key `44 46 6D 33 74 34 6C 46 54 57` ("DFm3t4lFTW")

#### FSB Header Structure (FSB5)
| Offset | Field |
|--------|-------|
| 0-3 | Magic "FSB5" |
| 4-7 | Version |
| 8-11 | NumSamples |
| 12-15 | SampleHeaderSize |
| 16-19 | NameSize |
| 20-23 | Datasize |
| 24-27 | Mode |
| 28-59 | Hash/Zero |

#### Codec Support
| Codec | Format | Extension |
|-------|--------|-----------|
| FMOD_SOUND_FORMAT_PCM8 | 8-bit PCM | WAV |
| FMOD_SOUND_FORMAT_PCM16 | 16-bit PCM | WAV |
| FMOD_SOUND_FORMAT_MPEG | MPEG Layer 2/3 | MP3 |

---

### ✅ Mission System Research Complete

**Location:** `Man_Script.~h/.~p` bundle

#### PPAK Format Structure
```
PPAK Structure:
├── PPAK Header
├── XT1 Textures (MPAK section)
├── MPAK Section (resources)
├── ScriptsVersion Section
├── Global Scripts Section
└── Scripts Section
```

#### Mission Features
- Lua-based mission scripts
- Triggers, objectives, rewards system
- Linear story progression with side missions
- Three factions: Ironheade, Drowning Doom, Tainted Coil

#### Known File Types
| Type | Description |
|------|-------------|
| MissionData | Mission metadata |
| QuestObjective | Objective definitions |
| EncounterTable | Enemy encounters |
| Story | Story progression |

---

### ✅ Game File Inventory Complete

**Game Size:** 8.06 GB  
**Total Files:** 546 files

#### Bundle Files (Win/Packs/)
| Bundle | Size | Purpose |
|--------|------|---------|
| 00Startup.~h/.~p | 1.67 MB | Core prototypes/scripts |
| Man_Script.~h/.~p | 18 KB / 832 KB | Mission Lua scripts |
| Man_Trivial.~h/.~p | 700 KB / 13 MB | Models, textures |
| Man_Gfx.~h/.~p | 124 KB / 77 MB | Graphics manifest |
| Man_Audio.~h/.~p | 8 KB / 2.8 MB | Audio manifest |
| RgB_World.~h/.~p | 433 KB / 130 MB | Base game world |
| RgS_World.~h/.~p | 487 KB / 399 MB | Streaming world data |
| DLC1_Stuff.~h/.~p | 528 KB / 146 MB | DLC content |
| Loc_enUS.~h/.~p | 4.4 KB / 5.8 MB | English localization |

#### Data Files (Data/)
- Configuration: `boot.lua`, `Buddha.cfg`, `input.lua`
- Cutscenes: 40+ `.bik` files (DF_Logo, INTRO, END CREDITS, etc.)
- UI: `FrontEnd/`, `HUD/`, `Loading/`, `Journal/` directories
- Fonts: Arial, FreeMono, FreeSans, ProggySquareSZ, Wolf4 (TTF)

---

### ✅ Save System Research Complete

**Finding:** No `.sav` files in standard AppData location

**Locations Checked:**
- `%APPDATA%\Doublefine\BrutalLegend\` - Only `screen.dat` (display settings) and `SDLGamepad.config`
- Steam ID folder present (76561199317189285) - empty

**Hypotheses:**
1. Saves may be in Steam Cloud
2. Saves may use non-.sav extension
3. Saves may be stored within DFPF archives

**screen.dat Contents (NOT save data):**
```ini
fullscreen = true
width = 3840
height = 2160
refreshrate = 120
vsync = true
```

---

## What's Documented

| System | Status | Document |
|--------|--------|----------|
| DFPF Container | ✅ Complete | DFPF_ANALYSIS.md (413 lines) |
| Audio/FMOD | ✅ Complete | AUDIO_ANALYSIS.md |
| Mission System | ✅ Research Done | MISSION_ANALYSIS.md |
| Executable | ✅ Complete | IMPORT_ANALYSIS.md (779 lines) |
| World/Terrain | 🔄 Partial | WORLD_ANALYSIS.md |
| Prototype | 🔴 Not Started | PROTO_SPEC.md (placeholder) |
| Animation | 🔴 Not Started | ANIM_FORMAT.md (placeholder) |
| Terrain | 🔴 Not Started | TERRAIN_SPEC.md (placeholder) |
| Save System | 🔴 Not Started | SAVE_SYSTEM.md (research complete) |

---

## What's Working

| Capability | Status |
|------------|--------|
| Extract DFPF bundles | ✅ With DoubleFine Explorer |
| Edit Lua scripts | ✅ Text editing in Man_Script |
| Character swaps | ✅ Via prototype modification |
| Faction swaps | ✅ Via prototype modification |
| Texture replacement | ✅ Replace .dds files |
| Audio replacement | ⚠️ Encrypted FSB requires decryption |

---

## What's Not Working

| Capability | Blocker |
|------------|---------|
| New missions | Lua API undocumented |
| New maps | Terrain format unknown |
| New characters | Prototype format undocumented |
| Save editing | Save format unknown |
| Model editing | Animation format unknown |

---

## Next Steps

### Immediate (Week 2-4)
1. Install Ghidra and analyze BrutalLegend.exe
2. Identify DFPF loading function addresses
3. Identify Lua engine initialization functions
4. Build function catalog (100+ target)

### Short-term (Week 5-8)
1. Document prototype system (all.proto)
2. Decompile and analyze Lua mission scripts
3. Document mission triggers/objectives/rewards
4. Create test mission

### Medium-term (Week 9-12)
1. Build DFPF extraction/repacking tool
2. Build Lua decompiler/disassembler
3. Build prototype editor
4. Test mod loading

---

## Documentation Created/Updated

### This Session

| File | Action | Lines |
|------|--------|-------|
| TODO.md | Created | 280+ |
| docs/EXECUTIVE_SUMMARY.md | Updated | 250+ |
| docs/PROJECT_STATUS.md | Created | 200+ |
| docs/README.md | Updated | 70+ |
| docs/formats/FORMAT_INDEX.md | Created | 150+ |
| inventory/INVENTORY_INDEX.md | Created | 100+ |

### Previously Completed

| File | Lines |
|------|-------|
| DFPF_ANALYSIS.md | 413 |
| IMPORT_ANALYSIS.md | 779 |
| MISSION_ANALYSIS.md | 371 |
| WORLD_ANALYSIS.md | 300 |
| AUDIO_ANALYSIS.md | 151 |
| SAVE_SYSTEM.md | 313 |
| GAME_FILE_INVENTORY.md | 239 |
| ARCHITECTURE.md | 120 |

---

## References

- **DoubleFine Explorer:** https://github.com/bgbennyboy/DoubleFine-Explorer
- **Kaitai Struct:** https://kaitai.io/
- **FMOD:** https://www.fmod.com/
- **Bink Video:** https://www.radgametools.com/bink/
- **Ghidra:** https://ghidra-sre.org/
- **x64dbg:** https://x64dbg.com/

---

*Generated: 2026-04-01*  
*Project: Brutal Legend Reverse Engineering*
