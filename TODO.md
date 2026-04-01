# Brutal Legend Reverse Engineering - TODO

## Status Legend
🔴 Not Started | 🟡 In Progress | 🟢 Complete | ⏸️ Blocked

---

## Phase 1: Foundation (Week 1)
### Project Setup
- [🟡] Create GitHub Organization: `brutal-legend-reverse` (repo created locally)
- [🟡] Create Repository: `brutal-legend-re` (created)
- [🔴] Setup Discord Server: `Brutal Legend RE` (pending)
- [🟢] Initialize repo structure (docs/, tools/, ghidra/, resources/)
- [🟢] Set LICENSE: MIT
- [🟢] Create README.md
- [🟢] Create CONTRIBUTING.md

### Toolchain Setup
- [🔴] Install Ghidra + analyze BrutalLegend.exe ⏸️ BLOCKED - game not installed
- [🔴] Install rizin + Cutter
- [🔴] Install x64dbg
- [🔴] Install ImHex
- [🔴] Install Kaitai Struct
- [🔴] Install Visual Studio 2022 (C++ dev)
- [🔴] Install Python 3.10+ with packages

### Knowledge Capture
- [🟢] Clone DoubleFine Explorer, study source code → `tools/reference/DoubleFine-Explorer/`
- [🟢] Document DFPF V5 format → `docs/formats/DFPF_ANALYSIS.md` (413 lines)
- [🟢] Create Kaitai .ksy file for DFPF V5 → `tools/dfpf-toolkit/dfpf_v5.ksy`
- [🔴] Generate Python parser from Kaitai spec (shell issues - need manual)
- [🔴] Extract all DFPF bundles, catalog file types ⏸️ BLOCKED - game not installed
- [🔴] Run dumpbin on executable, document imports ⏸️ BLOCKED - game not installed
- [🔴] Write `FILETYPE_INVENTORY.md` (created, empty)

---

## Phase 2: Executable Analysis (Weeks 2-4)
### Ghidra Static Analysis
- [🔴] Load BrutalLegend.exe, run full auto-analysis
- [🔴] Harvest all strings → categorize
- [🔴] Identify entry point + main game loop
- [🔴] Find DFPF read/write functions
- [🔴] Find Lua engine functions
- [🔴] Find prototype loader functions
- [🔴] Find save system functions
- [🔴] Find Stage Battle/RTS functions
- [🔴] Find mission trigger functions

### x64dbg Dynamic Analysis
- [🔴] Trace startup sequence → file load order
- [🔴] Breakpoint on CreateFile/ReadFile
- [🔴] Trace mission load triggers
- [🔴] Trace unit spawn system
- [🔴] Memory search → unit/health/position

### Function Catalog
- [🔴] Create spreadsheet: Address | Name | Purpose | Notes
- [🔴] Document 100+ functions minimum
- [🔴] Export Ghidra database to repo

---

## Phase 3: Format Deep Dive (Weeks 4-8)
### Mission System
- [🔴] Extract Man_Script, analyze Lua scripts
- [🔴] Identify mission structure (triggers, objectives)
- [🔴] Document `MISSION_API.md`
- [🔴] Test: create minimal test mission

### Prototype System
- [🔴] Extract and parse `all.proto`
- [🔴] Document complete format → `PROTO_SPEC.md`
- [🔴] Test: add minimal new prototype

### World/Terrain System
- [🔴] Find terrain/heightmap files
- [🔴] Identify zone format
- [🔴] Document `TERRAIN_SPEC.md`
- [🔴] Find world streaming system

### Animation/Skeleton
- [🔴] Find animation file format
- [🔴] Document `ANIM_FORMAT.md`
- [🔴] Find 3D mesh format

### Audio System
- [🔴] Study FSB (FMOD) format
- [🔴] Document `AUDIO_SPEC.md`
- [🔴] Test: replace audio files

---

## Phase 4: Core Tool Development (Weeks 6-12)
### dfpf-toolkit
- [🔴] C++ DFPF extractor
- [🔴] C++ DFPF repacker
- [🔴] Python bindings (pybind11)
- [🔴] CLI interface
- [🔴] Verification mode

### proto-editor
- [🔴] Prototype parser (read/edit all.proto)
- [🔴] GUI editor (Qt/ImGui)
- [🔴] Validation system
- [🔴] Diff tool

### Asset Pipeline
- [🔴] Texture converter (DDS import/export)
- [🔴] Model converter (3D mesh)
- [🔴] Audio extractor/repacker (FSB)

### Lua Script Tools
- [🔴] Lua decompiler
- [🔴] Lua compiler/validator
- [🔴] Script debugger

---

## Phase 5: Mod Loader Framework (Weeks 12-20)
### buddha-mod
- [🔴] Mod package format: `.bmod`
- [🔴] Mod loader (intercept DFPF reads)
- [🔴] Priority/load order system
- [🔴] Hot reload capability
- [🔴] Steam integration

### Steam Workshop SDK
- [🔴] Steam API authentication
- [🔴] Download manager
- [🔴] Upload tool
- [🔴] Version compatibility checker

### Validator & Debugger
- [🔴] Crash prevention (pre-load validation)
- [🔴] Conflict detector
- [🔴] In-game debug menu

---

## Phase 6: Level Editor (Week 20+)
### buddha-forge
- [🔴] Zone editor
- [🔴] Terrain editor (heightmap, textures)
- [🔴] Object placement tool
- [🔴] Mission editor
- [🔴] Preview mode
- [🔴] Export to Steam Workshop

---

## Phase 7: Documentation & Community
- [🔴] Setup GitHub Wiki
- [🔴] API reference documentation
- [🔴] Tutorial series (01-04+)
- [🔴] Video guides (YouTube)
- [🔴] Sample mods repository
- [🔴] Discord recruitment
- [🔴] CONTRIBUTING.md + Code of Conduct

---

## Phase 8: Public Release
- [🔴] Stable releases: dfpf-toolkit v1.0, buddha-mod v1.0
- [🔴] Steam Early Access modding tools
- [🔴] Announcement posts (r/games, r/gamedev)
- [🔴] Mod showcase events
- [🔴] Ongoing support + bug fixes

---

## Milestones
| Milestone | Target | Deliverables |
|-----------|--------|--------------|
| M1 | Week 1 | Repo ready, DFPF spec, toolchain setup |
| M2 | Week 4 | 100+ functions cataloged |
| M3 | Week 8 | All format specs complete |
| M4 | Week 12 | Core tools functional |
| M5 | Week 20 | Mod loader + Steam SDK |
| M6 | Week 24+ | Level editor + public release |

---

## Team Assignments
```
RE Lead: _______________
├── RE Team: _______________
│   ├── Ghidra Analysis: _______________
│   └── x64dbg Tracing: _______________
├── Dev Team: _______________
│   ├── C++ (dfpf-toolkit): _______________
│   ├── Python (scripts): _______________
│   └── Kaitai Struct: _______________
├── Docs Team: _______________
│   ├── Format Docs: _______________
│   └── Tutorials: _______________
└── Community: _______________
```

---

## Project Info
- **Engine:** Buddha (Double Fine custom engine)
- **Game:** Brutal Legend (2009)
- **License:** MIT
- **Status:** 🟡 Phase 1 In Progress

## Session Accomplishments (2026-04-01)
- ✅ Created full project structure in `brutal-legend-re/`
- ✅ Cloned DoubleFine Explorer reference (Pascal source)
- ✅ Documented DFPF V5 format (413 lines in DFP_ANALYSIS.md)
- ✅ Created Kaitai Struct spec (dfpf_v5.ksy - 4.7KB)
- ✅ Created PROGRESS.md with comprehensive status report
- ⚠️ Game NOT INSTALLED - reinstall required for executable analysis
