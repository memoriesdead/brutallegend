# Brutal Legend Reverse Engineering - Project Status

**Last Updated:** 2026-04-01  
**Project:** Open source reverse engineering of Brutal Legend (2009)  
**Repository:** `brutal-legend-re/`

---

## Overall Status

| Metric | Value |
|--------|-------|
| **Phase** | Phase 2: Executable Analysis |
| **Overall Progress** | ~35% complete |
| **Documentation** | 500+ lines across 15+ documents |
| **Executable Analysis** | ✅ Import analysis complete |
| **Format Documentation** | ~60% (DFPF/Audio/Mission done) |
| **Tool Development** | 0% (no tools built yet) |

---

## Phase Progress

### Phase 1: Foundation
**Status:** ✅ COMPLETE

| Task | Status |
|------|--------|
| Project structure | ✅ Complete |
| Documentation framework | ✅ Complete |
| README/TODO | ✅ Complete |
| MIT License | ✅ Complete |
| CONTRIBUTING.md | ✅ Complete |

### Phase 2: Executable Analysis
**Status:** 🔄 IN PROGRESS (~40%)

| Task | Status | Notes |
|------|--------|-------|
| Import analysis | ✅ Complete | 779 lines documented |
| Function catalog | 🔄 In Progress | Empty - needs Ghidra |
| Middleware verification | 🔄 In Progress | FMOD/Bink confirmed, Havok/S scaleform unconfirmed |
| String analysis | ✅ Complete | FMOD, Lua, FSB strings found |

### Phase 3: Format Specifications
**Status:** 🔄 IN PROGRESS (~40%)

| Format | Status | Document |
|--------|--------|----------|
| DFPF Container | ✅ Complete | DFPF_ANALYSIS.md (413 lines) |
| Audio/FMOD | ✅ Complete | AUDIO_ANALYSIS.md (151 lines) |
| Mission System | 🔄 In Progress | MISSION_ANALYSIS.md (371 lines) |
| World/Terrain | 🔄 In Progress | WORLD_ANALYSIS.md (300 lines) |
| Prototype | 🔴 Not Started | PROTO_SPEC.md (placeholder) |
| Animation | 🔴 Not Started | ANIM_FORMAT.md (placeholder) |
| Save System | 🔴 Not Started | SAVE_SYSTEM.md (research done) |
| Video/UI | 🔴 Not Started | No document |

### Phase 4: Tool Development
**Status:** 🔴 NOT STARTED (0%)

| Tool | Status |
|------|--------|
| DFPF extractor | 🔴 Not started |
| DFPF repacker | 🔴 Not started |
| Prototype editor | 🔴 Not started |
| Lua tools | 🔴 Not started |

### Phase 5: Mod Loader
**Status:** 🔴 NOT STARTED (0%)

### Phase 6: Level Editor
**Status:** 🔴 NOT STARTED (0%)

---

## Component Status

### Executable (BrutalLegend.exe)

| Attribute | Value |
|-----------|-------|
| Size | 13,180,928 bytes |
| Architecture | x86 (32-bit) |
| Build Date | 2013-05-06 |
| Internal Name | Buddha.exe |
| Exports | 611 functions |

**Analysis Status:** ✅ Complete (IMPORT_ANALYSIS.md)

### DFPF Container System

| Attribute | Value |
|-----------|-------|
| Versions Supported | V2, V5, V6 |
| Brutal Legend Uses | V5 |
| Header Size | 88 bytes |
| File Record Size | 16 bytes |
| Compression | ZLib, XMemCompress |

**Analysis Status:** ✅ Complete (DFPF_ANALYSIS.md)

### Audio System

| Attribute | Value |
|-----------|-------|
| Middleware | FMOD Ex |
| Format | FSB5/FSB4 |
| Encryption | ✅ Yes (DFm3t4lFTW) |
| Codecs | PCM8, PCM16, MPEG |

**Analysis Status:** ✅ Complete (AUDIO_ANALYSIS.md)

### Mission System

| Attribute | Value |
|-----------|-------|
| Scripting | Lua (embedded) |
| Bundle | Man_Script.~h/.~p |
| Format | PPAK (custom) |
| Mission API | 🔴 Not documented |

**Analysis Status:** 🔄 Research Complete (MISSION_ANALYSIS.md)

### World/Terrain System

| Attribute | Value |
|-----------|-------|
| World Size | ~40 square miles |
| System | Zone-based streaming |
| Terrain Format | 🔴 Unknown |
| Zone Format | 🔴 Unknown |

**Analysis Status:** 🔄 Research Phase (WORLD_ANALYSIS.md)

### Save System

| Attribute | Value |
|-----------|-------|
| Save Location | Unknown |
| Steam Cloud | Possibly |
| Format | 🔴 Unknown |

**Analysis Status:** 🔴 Research Required

---

## File Format Inventory

| Extension | Type | Documented | Editable |
|-----------|------|------------|----------|
| .~h/.~p | DFPF container | ✅ Yes | ✅ With tools |
| .lua | Lua script | ✅ Yes | ✅ Yes |
| .proto | Prototype | ❌ No | ❌ No |
| .fsb | FMOD audio | ✅ Yes | ⚠️ Encrypted |
| .dds | Texture | ❌ No | ✅ Replace |
| .bik | Bink video | ❌ No | ❌ No |
| .gfx | UI bundle | ❌ No | ❌ No |
| .Clumps | Data clump | ❌ No | ❌ No |

---

## Tool Status

| Tool | Available | Status |
|------|-----------|--------|
| Ghidra | ❌ No | Needed for function analysis |
| x64dbg | ❌ No | Needed for debugging |
| ImHex | ❌ No | Needed for hex analysis |
| DoubleFine Explorer | ⚠️ Source only | Reference only |
| Kaitai Struct | ⚠️ Spec created | Parser ready |
| Python | ❌ No | Needed for scripts |
| Visual Studio | ❌ No | Needed for C++ tools |

---

## Game Files Status

**Location:** Steam game installation directory

| Component | Status |
|-----------|--------|
| BrutalLegend.exe | ✅ Present |
| Win/Packs/ (42 files) | ✅ Complete |
| Data/ (462 files) | ✅ Complete |
| DLC Content | ✅ Present |
| Localization (5 langs) | ✅ Present |
| Total Size | 8.06 GB |

---

## Milestone Progress

| Milestone | Target | Progress | Status |
|-----------|--------|----------|--------|
| M1: Foundation | Week 1 | 100% | ✅ Complete |
| M2: 100+ Functions | Week 4 | 0% | 🔴 Not Started |
| M3: Format Specs | Week 8 | 40% | 🔄 In Progress |
| M4: Core Tools | Week 12 | 0% | 🔴 Not Started |
| M5: Mod Loader | Week 20 | 0% | 🔴 Not Started |
| M6: Level Editor | Week 24+ | 0% | 🔴 Not Started |

---

## Key Discoveries This Session

### 1. Executable Analysis
- BrutalLegend.exe is internally named **Buddha.exe**
- FMOD and Lua are **embedded** (not external DLLs)
- SDL 2.x is the primary windowing/input framework
- 611 Buddha.exe exports include GBufferedFile, GThread, GMutex classes

### 2. Audio Encryption
- Custom FSB encryption key: `DFm3t4lFTW`
- Algorithm: Bit-reverse + XOR
- Affects all FSB audio files in the game

### 3. DFPF Format
- V5 format fully reverse-engineered
- Bit-shifting details for all fields documented
- Kaitai Struct specification created

### 4. Save System
- No local save files found
- screen.dat contains display settings, NOT save data
- Saves may be on Steam Cloud or use non-standard format

---

## Blockers

| Blocker | Impact | Solution |
|---------|--------|----------|
| Ghidra not installed | Cannot analyze exe functions | Install Ghidra |
| Havok/Scalform unconfirmed | Unknown physics/UI | Ghidra analysis |
| Prototype format unknown | Cannot create new characters | Bundle extraction + analysis |
| Terrain format unknown | Cannot create new maps | Bundle extraction + analysis |
| Save format unknown | Cannot backup/restore saves | Ghidra analysis |

---

## Next Actions

### Priority 1: Install Ghidra
```
1. Download Ghidra from https://ghidra-sre.org/
2. Install Java JDK 11+
3. Load BrutalLegend.exe
4. Run full analysis
5. Begin function catalog
```

### Priority 2: Extract Man_Script
```
1. Use DoubleFine Explorer to extract Man_Script.~h
2. List all Lua scripts
3. Identify mission structure
4. Attempt to decompile with luadec
```

### Priority 3: Prototype Research
```
1. Extract 00Startup.~h/.~p
2. Find all.proto file
3. Begin format analysis
4. Cross-reference with Hair Metal Militia mod
```

---

## Team Status

| Role | Assigned | Status |
|------|---------|--------|
| RE Lead | TBD | 🔴 Open |
| Ghidra Analysis | TBD | 🔴 Open |
| x64dbg Tracing | TBD | 🔴 Open |
| C++ Development | TBD | 🔴 Open |
| Documentation | Active | 🔄 In Progress |

---

## Repository Statistics

| Metric | Value |
|--------|-------|
| Total Documents | 18+ |
| Documentation Lines | 2500+ |
| Source Files | 1 (Pascal reference) |
| Specifications | 2 (DFPF Kaitai, DFPF spec) |
| Analysis Documents | 6 |

---

*Last updated: 2026-04-01*
