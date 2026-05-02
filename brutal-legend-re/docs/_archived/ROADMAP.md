# Brutal Legend Reverse Engineering - Roadmap

**Last Updated:** 2026-04-01 (Session 2)  
**Status:** Phase 3 ~80% Complete  
**Goal:** 100% Reverse Engineering  

---

## What's Complete ✅

### Phase 1: Foundation
- [x] Project structure
- [x] Documentation framework
- [x] MIT License
- [x] Python DFPF extractor + repacker

### Phase 2: Executable Analysis (~75%)
- [x] 611 Buddha.exe exports documented
- [x] 19 DLL imports analyzed
- [x] Entry point: 0x88c8ae
- [x] Internal classes: GBufferedFile, GZLibFile, GSysFile
- [x] Threading: GThread, GMutex, GEvent, GSemaphore
- [x] GFxLoader confirmed (Scaleform)
- [x] FMOD embedded
- [x] Lua embedded
- [x] Bink Video confirmed

### Phase 3: Format Specifications (~80%)
- [x] DFPF V5 format complete (88B header, 16B records)
- [x] **all.proto extracted (1.77MB)** ✅ NEW
- [x] **PROTO_SPEC.md complete (9KB, 337 lines)** ✅ NEW
- [x] 266 Lua scripts extracted and analyzed
- [x] 240 missions identified with full API
- [x] 156 FSB audio files (4.1 GB)
- [x] **FSB extractor created (fsb_extract.py)** ✅ NEW
- [x] 192 .bik video files (2.7 GB)
- [x] 80 .gfx UI files (Scaleform GFx 3.x)
- [x] Tile-based world streaming discovered
- [x] Heightfield terrain format identified
- [x] MeshSet V8 model format documented
- [x] Audio encryption key: DFm3t4lFTW
- [x] **Bundle extraction IN PROGRESS (7 bundles, ~1.2GB extracted)** ✅ NEW

### Phase 4: Tool Development (~40%)
- [x] dfpf_extract.py (extractor)
- [x] dfpf_repack.py (repacker) ✅ NEW
- [x] fsb_extract.py (audio extractor) ✅ NEW
- [x] Bundle extraction (20/21 bundles, ~5GB) ✅ NEW
- [ ] Heightfield parser/viewer (agent running)
- [ ] Prototype editor
- [ ] Mission builder
- [ ] Model viewer

---

## What's Missing 🔴

### Phase 2: Executable Analysis (25% remaining)
- [ ] Complete function catalog with purposes for all 611 exports
- [ ] Identify DFPF loading functions in executable
- [ ] Identify Lua engine initialization functions
- [ ] Identify prototype loading functions (all.proto)
- [ ] Identify Stage Battle RTS logic functions
- [ ] Identify memory management implementation
- [ ] Havok Physics confirmation (need Ghidra deep dive)

### Phase 3: Format Specifications (20% remaining)

#### 3.2 Prototype System ✅ NEW
- [x] **Extract all.proto from 00Startup bundle**
- [x] **Parse prototype format completely (PROTO_SPEC.md)**
- [x] **Document every property type**
- [x] **Document unit/character/vehicle structures**
- [x] **Identify faction system**

#### 3.5 Terrain/World ✅
- [x] **TERRAIN_SPEC.md (heightfield format)** ✅
- [x] **Heightfield is DXT5 compressed DDS texture (128x128)** ✅ NEW
- [x] **Extract Heightfield binary data (found in RgS_World)** ✅
- [x] **Determine exact dimensions (128x128, 8 mipmaps)** ✅ NEW
- [ ] Build heightfield viewer/parser (needs DXT5 decoder)

#### 3.8 Save System 🔴
- [ ] Locate actual save files
- [ ] Investigate Steam Cloud storage
- [ ] Analyze save file structure
- [ ] Create PROTO_SPEC.md

#### 3.5 World/Terrain (50% remaining)
- [ ] **Extract Heightfield binary data**
- [ ] Determine exact heightmap dimensions
- [ ] Analyze header structure of Heightfield
- [ ] Build Heightfield viewer/parser
- [ ] Document collision mesh format
- [ ] Document pathfinding format
- [ ] Create TERRAIN_SPEC.md

#### 3.6 Animation/Skeleton (50% remaining)
- [ ] Extract MeshSet V8 binary data
- [ ] Analyze vertex format (position, normal, uv, weights)
- [ ] Document bone hierarchy from rig data
- [ ] Identify animation keyframe format
- [ ] Build model viewer tool

#### 3.8 Save System 🔴
- [ ] Locate actual save files
- [ ] Investigate Steam Cloud storage
- [ ] Analyze save file structure
- [ ] Document save format
- [ ] Create SAVE_FORMAT.md

### Phase 4: Tool Development 🔴 NOT STARTED

#### 4.1 Core Tools
- [ ] dfpf_repack.py (repack DFPF bundles)
- [ ] C++ dfpf-toolkit (performance)
- [ ] Heightfield parser/viewer
- [ ] FSB extractor with decryption

#### 4.2 Prototype Tools
- [ ] Prototype parser
- [ ] GUI editor
- [ ] Validation system

#### 4.3 Mission Tools
- [ ] Lua decompiler
- [ ] Mission script editor
- [ ] Trigger builder

#### 4.4 Asset Tools
- [ ] Model viewer
- [ ] Texture converter
- [ ] Audio converter with decryption

### Phase 5: Mod Loader 🔴 NOT STARTED
- [ ] Steam SDK integration
- [ ] Mod loading system (.bmod format)
- [ ] Hot reload capability

### Phase 6: Level Editor 🔴 NOT STARTED
- [ ] Zone editor
- [ ] Terrain editor
- [ ] Heightfield editor
- [ ] Object placement
- [ ] Export to Steam Workshop

---

## Critical Path to 100%

```
Step 1: Extract all.proto
         ↓
Step 2: Document prototype format
         ↓
Step 3: Create prototype editor
         ↓
Step 4: Extract and analyze heightfield data
         ↓
Step 5: Build terrain editor
         ↓
Step 6: Build mission builder
         ↓
Step 7: Integrate with Steam Workshop
         ↓
Step 8: BuddhaForge (Level Editor)
```

---

## Immediate Next Actions

### Day 1 (Next Session)
1. Run: `python tools/dfpf-toolkit/dfpf_extract.py Win/Packs/00Startup.~h extracted/00Startup`
2. Extract all.proto → Parse format → Create PROTO_SPEC.md
3. Run full bundle extraction on all 42 bundles

### Week 1
1. Complete prototype format documentation
2. Build prototype editor
3. Analyze heightfield format
4. Build heightfield parser

### Week 2-4
1. Mission builder tools
2. Model viewer
3. Audio extractor with decryption
4. Begin mod loader development

---

## Documentation Missing

| Document | Priority | Status |
|----------|----------|---------|
| PROTO_SPEC.md | CRITICAL | Not started |
| TERRAIN_SPEC.md | CRITICAL | Partial |
| SAVE_FORMAT.md | HIGH | Not started |
| FUNCTION_CATALOG.md | HIGH | Partial |
| HEIGHTFIELD_SPEC.md | HIGH | Not started |
| MODEL_VIEWER_TOOL.md | MEDIUM | Not started |
| MISSION_BUILDER_TOOL.md | MEDIUM | Not started |

---

## File Inventory (What We Have)

### Extracted/Created by Agents
| File | Location | Size |
|------|----------|------|
| EXPORT_TABLE.md | ghidra/ | 27KB |
| IMPORT_TABLE.md | ghidra/ | 21KB |
| STRING_CATALOG.md | ghidra/ | 30KB |
| FUNCTION_CATALOG.md | ghidra/ | 9KB |
| SECTION_LAYOUT.md | ghidra/ | 729B |
| MISSION_API.md | docs/formats/ | Agent created |
| MISSION_ANALYSIS.md | docs/formats/ | Agent created |
| AUDIO_SPEC.md | docs/formats/ | Agent created |
| WORLD_ANALYSIS.md | docs/formats/ | Agent created |
| MODEL_FORMAT.md | docs/formats/ | Agent created |
| ANIM_FORMAT.md | docs/formats/ | Agent created |
| VIDEO_SPEC.md | docs/formats/ | 172 lines |
| UI_FORMAT.md | docs/formats/ | 253 lines |
| dfpf_extract.py | tools/dfpf-toolkit/ | Complete |

### Still Needed
| File | Purpose |
|------|---------|
| all.proto | Prototype definitions (in 00Startup) |
| Heightfield samples | For format analysis |
| Save files | For save format analysis |

---

## Continuation

See [CONTINUATION_PROMPT.md](./CONTINUATION_PROMPT.md) for ready-to-use prompt to continue in next chat session.

---

*Last updated: 2026-04-01*
