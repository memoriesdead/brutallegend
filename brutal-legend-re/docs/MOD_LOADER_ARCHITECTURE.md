# Brutal Legend Mod Loader Architecture

**Status:** Research Complete - Implementation Not Started
**Engine:** Buddha (Double Fine proprietary)
**Game:** Brutal Legend (PC/Steam)
**Last Updated:** 2026-04-01

---

## Executive Summary

This document outlines the architecture for a mod loader for Brutal Legend, enabling community-created content including new maps, missions, characters, and game modes. The mod loader builds upon the existing Buddha engine DFPF bundle system and leverages Steam Workshop for distribution.

**Key Finding:** No Steam-specific exports exist in Buddha.exe (611 exports analyzed). Steam integration uses the standard `steam_api.dll` rather than custom exports. Workshop support requires implementing standard Steamworks API patterns.

---

## 1. Bundle Loading System

### 1.1 Bundle Format (DFPF V5)

The Buddha engine uses DFPF (Double-Fine Pack File) containers for all game content:

| Component | File | Purpose |
|-----------|------|---------|
| Header/Index | `filename.~h` | File manifest, names, offsets (88 byte header + 16 byte records) |
| Data/Payload | `filename.~p` | Actual resource data |

**Technical Details:**
- **Version:** V5 (0x05 magic)
- **Endianness:** Big-endian
- **Compression:** ZLib (type 8) or uncompressed (type 4)
- **File Record Size:** 16 bytes per file entry
- **Bit-shifting:** Offsets and sizes use bit-shifting encoding

### 1.2 Bundle Loading Order

Based on file naming convention and bundle sizes:

| Order | Bundle | Size | Contents |
|-------|--------|------|----------|
| 1 | `00Startup.~h/.~p` | 1.67 MB | Core prototypes (`all.proto`), engine initialization |
| 2 | `Man_Script.~h/.~p` | 850 KB | 266 Lua mission scripts |
| 3 | `Man_Trivial.~h/.~p` | 14 MB | Models, textures (10,249 assets) |
| 4 | `Man_Gfx.~h/.~p` | 77 MB | Graphics manifest |
| 5 | `Man_Audio.~h/.~p` | 2.8 MB | Audio manifest |
| 6 | `RgB_World.~h/.~p` | 130 MB | Base world data |
| 7 | `RgB_Faction.~h/.~p` | 23 MB | Faction definitions |
| 8 | `RgB_Mission.~h/.~p` | 5 MB | Mission data |
| 9 | `RgB_Ctsn.~h/.~p` | 78 MB | Cutscene data |
| 10 | `RgS_World.~h/.~p` | 400 MB | Streaming world tiles |
| 11 | `RgS_Faction.~h/.~p` | 264 MB | Streaming faction data |
| 12 | `RgS_Ctsn.~h/.~p` | 88 MB | Streaming cutscenes |
| 13 | `Loc_enUS.~h/.~p` | 5.8 MB | English localization |
| 14 | `DLC1_Stuff.~h/.~p` | 146 MB | DLC content |
| 15 | `DLC2_Stuff.~h/.~p` | 64 KB | DLC2 content |

**Note:** Localization bundles (Loc_*) load based on selected language. DLC bundles load conditionally.

### 1.3 Bundle Search Paths

The Buddha engine searches for bundles in the following locations:

```
1. <GameDir>/Win/Packs/           # Primary game bundles
2. <GameDir>/Win/DLC/             # DLC bundles (if present)
3. <SteamCloud>/BrutalLegend/      # Cloud-saved data
4. <ModDir>/Win/Packs/            # [INJECTION POINT] Mod bundles
```

**Proposed Mod Directory Structure:**
```
<GameDir>/
├── Win/
│   ├── Packs/                    # Original game bundles
│   └── Mods/                     # [NEW] Mod loader directory
│       ├── 00Mods.~h/.~p        # Mod manifest/scripts
│       └── 01CustomMaps.~h/.~p   # Custom map bundles
├── Data/
│   ├── Mods/                     # [NEW] Unpacked mod data
│   └── Config/
└── Mods/                         # [NEW] Mod metadata
    ├── mod清单.json              # Mod manifest
    └── workshop/                 # Workshop content cache
```

### 1.4 File I/O Classes (Buddha Engine)

From 611 Buddha.exe exports, the following file I/O classes are available:

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `GSysFile` | Low-level file I/O | `Open()`, `Close()`, `Read()`, `Seek()` |
| `GBufferedFile` | Buffered file wrapper | `Read()`, `Write()`, `Flush()` |
| `GZLibFile` | Compressed file I/O | `Open()`, `Read()`, `Decompress()` |

**Bundle Loading Flow:**
```
GSysFile::Open(bundle_path)
    → GBufferedFile::Read(header)
    → GZLibFile::Open(data_file)
    → ParseFileRecords()
    → LoadIndividualAssets()
```

---

## 2. Asset Override System

### 2.1 Override Mechanism

The Buddha engine uses a **last-loaded-wins** approach for asset loading:

1. Game loads `00Startup` bundle first (contains `all.proto`)
2. Subsequent bundles (RgB_*, RgS_*, DLC*) load in order
3. When the same filename exists in multiple bundles, the later bundle's file takes precedence
4. DLC bundles load after base game, allowing DLC to override base content

**Implication for Mods:** If a mod bundle loads AFTER a game bundle with the same internal filename, the mod's file will override the game's.

### 2.2 Override Rules

| Override Type | Mechanism | Example |
|---------------|-----------|---------|
| Prototype | `all.proto` entry with same name | `Prototype MySoldier : Character` |
| Script | `.lua` file with same mission ID | `P1_MyMission.lua` |
| Texture | `.dds` file with same path | `Textures/CustomSkin.dds` |
| Audio | `.fsb` file with same bank name | `MyModAudio.fsb` |
| World | Tile files with same coordinates | `tile/x0/y0/heightfield.dds` |

### 2.3 Asset Path Resolution

Assets are referenced by path within bundles. Resolution order:

```
1. Check loaded bundles in reverse order (latest first)
2. If found, return asset
3. If not found, return error or fallback
```

**Prototype Reference Example:**
```
MeshSet=@Characters/Bipeds/A01_Avatar/Rig/A01_Avatar;
```

---

## 3. Steam SDK Integration

### 3.1 Current Steam Integration

**Steam Components Present:**
| Component | File | Purpose |
|-----------|------|---------|
| Steamworks API | `steam_api.dll` | Standard Steam API DLL (101.48 KB) |
| Steam Cloud | `%APPDATA%/BrutalLegend/` | Cloud save storage |

**What We Know:**
- Buddha.exe has NO direct Steam exports (611 exports analyzed)
- Steam integration uses standard `steam_api.dll` calls
- Steam Cloud saves detected in `%APPDATA%`
- No Workshop-specific functions visible in exports

### 3.2 Steamworks API Requirements

For Workshop integration, the following Steamworks API usage is needed:

**Required Interfaces:**
```cpp
// Steamworks interfaces needed for Workshop
ISteamUGC*        // User-generated content
ISteamRemoteStorage* // Cloud storage
ISteamAppList*    // App list enumeration
SteamUGCQuery_t   // Query handle type
```

**Key Steamworks Functions:**
| Function | Purpose |
|----------|---------|
| `SteamUGC()->CreateItem()` | Create new Workshop item |
| `SteamUGC()->StartItemUpdate()` | Begin editing item |
| `SteamUGC()->SetItemContent()` | Set local content directory |
| `SteamUGC()->SubmitItemUpdate()` | Upload changes |
| `SteamUGC()->GetItemInstallInfo()` | Get installed mod info |
| `SteamUGC()->BInitWorkshopForGameServer()` | Server-side workshop |

### 3.3 Steam Integration Points

**Publish Mod Flow:**
```
1. User clicks "Publish Mod" in-game
2. Mod loader creates .bmod package
3. SteamUGC()->CreateItem() → Workshop item ID
4. SteamUGC()->StartItemUpdate()
5. SteamUGC()->SetItemContent("Win/Mods/MyMod/")
6. SteamUGC()->SubmitItemUpdate() → Upload to Workshop
```

**Download Mod Flow:**
```
1. User browses Workshop in-game
2. Mod loader queries SteamUGC()->CreateQuery()
3. User subscribes to mod
4. Steam downloads to workshop content directory
5. Mod loader validates and installs to Win/Mods/
```

### 3.4 Steam Cloud Integration

**Current Behavior:**
- Save files stored in `%APPDATA%/BrutalLegend/`
- `screen.dat` confirmed (display settings)
- Full save file analysis not yet complete

**For Mod Loader:**
- Mod configurations could sync via Steam Cloud
- Save game compatibility across mod versions needs validation

---

## 4. Buddha.exe Export Analysis

### 4.1 File I/O Exports (Relevant to Bundle Loading)

From `ghidra/EXPORT_TABLE.md`:

| Ordinal | Function | Address | Purpose |
|---------|----------|---------|---------|
| 1-2 | `GBufferedFile` constructors | 0x6bb280, 0x6bb2d0 | Buffered file wrapper |
| 12-13 | `GSysFile` constructors | 0x6bb800, 0x6bb780 | Low-level file I/O |
| 17 | `GZLibFile` constructor | 0x6c6920 | ZLib compressed file |
| 45-176 | `GBufferedFile` methods | Various | Read, Write, Seek, etc. |
| 80-157 | `GZLibFile` methods | Various | Decompress operations |

**Key Insight:** Bundle loading functions are likely internal (not exported). They call the exported file I/O classes.

### 4.2 Missing Export Functions

The following are NOT exported but likely exist internally:
- Bundle manifest parsing
- DFPF header reading
- `all.proto` loading
- Prototype system initialization

**To find these:** Ghidra decompilation of internal functions is required.

### 4.3 No Steam-Specific Exports

**Confirmed:** Zero Steam_ prefixed exports in Buddha.exe

This means:
- Steam API calls go through `steam_api.dll` directly
- No custom Steam implementation in the game executable
- Standard Steamworks patterns apply

---

## 5. Mod Loader Architecture (.bmod Format)

### 5.1 .bmod Package Format

A `.bmod` (Brutal Mod) package is a ZIP archive containing:

```
MyMod.bmod/
├── manifest.json          # Mod metadata (required)
├── content/               # Mod content (required)
│   ├── Win/
│   │   └── Packs/         # Bundle overrides
│   └── Data/
│       └── Config/       # Configuration overrides
├── scripts/               # Optional scripts
│   └── mod_main.lua       # Entry point script
├── icon.png               # Mod icon (optional)
├── preview/               # Workshop preview images
│   └── preview_1.png
└── changelog.txt          # Version history (optional)
```

### 5.2 manifest.json Schema

```json
{
    "name": "CustomMapPack",
    "version": "1.0.0",
    "game_version": "1.0.0",
    "author": "ModderName",
    "description": "A collection of custom maps",
    "category": "maps",
    "dependencies": [],
    "workshop_id": null,
    "content_dirs": ["Win", "Data"],
    "scripts": ["scripts/mod_main.lua"],
    "load_order": 100
}
```

### 5.3 Mod Loading Pipeline

```
1. Game Startup
   └─> Mod Loader Init
       └─> Scan Win/Mods/ directory
           └─> Load mod清单.json files
               └─> Sort by load_order
                   └─> Validate dependencies
                       └─> Extract/install mods
                           └─> Register mod bundles
                               └─> Game continues startup
```

### 5.4 Mod Categories

| Category | Content Type | Override Behavior |
|----------|--------------|-------------------|
| `maps` | World tiles, terrain | Full replacement |
| `missions` | Lua scripts, mission data | Merge/replace scripts |
| `characters` | Prototypes, models | Add new or override |
| `audio` | FSB sound banks | Add new banks |
| `textures` | DDS textures | Replace by path |
| `ui` | GFx files | Replace by path |
| `full` | Complete packages | Full bundle replacement |

---

## 6. Recommended Mod Loader Architecture

### 6.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Brutal Legend Mod Loader                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │ Mod Scanner │  │ Bundle Loader│  │ Steam Workshop Mgr ││
│  │             │  │             │  │                     ││
│  │ - Validate  │  │ - Override   │  │ - Publish mods     ││
│  │ - Deps check│  │ - Merge      │  │ - Download mods    ││
│  │ - Version   │  │ - Hot reload │  │ - Subscribe mods   ││
│  └─────────────┘  └─────────────┘  └─────────────────────┘│
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │Proto Compiler│  │Asset Resolver│ │ Save Game Manager   ││
│  │             │  │             │  │                     ││
│  │ - Parse     │  │ - Path lookup│  │ - Mod conflict det ││
│  │ - Validate  │  │ - Fallback   │  │ - Save compat       ││
│  │ - Compile   │  │ - Override   │  │ - Cloud sync        ││
│  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Core Interfaces

**IModLoader (Interface)**
```cpp
class IModLoader {
    virtual void Initialize() = 0;
    virtual void ScanMods(const char* modDir) = 0;
    virtual void LoadMod(IMod* mod) = 0;
    virtual void UnloadMod(IMod* mod) = 0;
    virtual IMod* GetMod(const char* modId) = 0;
    virtual void SetLoadOrder(IMod* mod, int order) = 0;
};
```

**IMod (Interface)**
```cpp
class IMod {
    virtual const char* GetId() = 0;
    virtual const char* GetName() = 0;
    virtual const char* GetVersion() = 0;
    virtual bool Validate() = 0;
    virtual void Install() = 0;
    virtual void Uninstall() = 0;
    virtual IModContent* GetContent() = 0;
};
```

**IModContent (Interface)**
```cpp
class IModContent {
    virtual const char* GetContentPath() = 0;
    virtual void RegisterBundle(const char* bundlePath) = 0;
    virtual void RegisterScript(const char* scriptPath) = 0;
    virtual void RegisterPrototype(const char* protoPath) = 0;
};
```

### 6.3 Hook Points

**Potential Hook Locations for Mod Loader:**

| Hook | Location | Purpose |
|------|----------|---------|
| `BundleLoader::Load` | After bundle loaded | Apply mod overrides |
| `PrototypeDB::Get` | On prototype lookup | Return mod prototypes |
| `LuaEngine::Execute` | Before script execution | Inject mod scripts |
| `AssetResolver::Resolve` | On asset request | Check mod assets first |
| `SteamUGC::Download` | After mod downloaded | Trigger install |

### 6.4 Implementation Priority

**Phase 1: Basic Mod Loading (Priority: HIGH)**
1. Mod directory scanning
2. Manifest.json parsing
3. Bundle override system
4. In-memory bundle merging

**Phase 2: Script Integration (Priority: HIGH)**
1. Lua script hooks
2. Mission system integration
3. Prototype injection

**Phase 3: Steam Workshop (Priority: MEDIUM)**
1. Steamworks API integration
2. Publish/download flow
3. Subscription management

**Phase 4: Advanced Features (Priority: LOW)**
1. Hot reload
2. Mod conflict detection
3. Save game compatibility
4. Multiplayer mod sync

---

## 7. Injection Points Summary

### 7.1 Bundle Path Injection

**Current:** `Win/Packs/*.~h/.~p`

**Proposed:** `Win/Mods/*.~h/.~p` (loaded after Win/Packs/)

**Injection Method:**
1. Hook `GSysFile::Open()` or bundle scanning function
2. Prepend mod directory to search paths
3. Ensure mod bundles load after game bundles

### 7.2 Script Injection

**Location:** `Man_Script` bundle (266 Lua scripts)

**Method:**
1. Add custom scripts to mod bundle
2. Register in `mod_main.lua`
3. Hook mission callback system

### 7.3 Prototype Injection

**Location:** `all.proto` in `00Startup` bundle

**Method:**
1. Extract `all.proto` from mod bundle
2. Merge with game prototypes (mod takes precedence)
3. Recompile and inject at load time

### 7.4 Steam Integration Points

**For Workshop Support:**
1. Initialize Steamworks at game startup
2. Use `ISteamUGC` for mod publishing/subscribing
3. Use `ISteamRemoteStorage` for cloud saves
4. Implement `STEAMUGCUpdateHandle_t` callbacks

---

## 8. Research Gaps & Next Steps

### 8.1 Required Ghidra Analysis

To fully understand bundle loading:

1. **Find internal bundle loading functions** - Not exported, need Ghidra search for:
   - `dfpf` magic string references
   - File record parsing code
   - `all.proto` loading

2. **Find Lua engine functions:**
   - `luaL_loadfile`
   - `lua_pcall`
   - `all.proto` parser

3. **Find Steam initialization:**
   - Where `steam_api.dll` is loaded
   - Where SteamUGC is initialized

### 8.2 Testing Plan

1. Create test mod with simple texture override
2. Place in `Win/Mods/` directory
3. Verify override occurs
4. Test load order

### 8.3 Milestones

| Milestone | Description | Status |
|-----------|-------------|--------|
| M0 | DFPF extractor/repacker working | ✅ Complete |
| M1 | Prototype editor functional | 🔄 In Progress |
| M2 | Mod loader architecture documented | ✅ This Document |
| M3 | Basic mod loading implemented | 🔴 Not Started |
| M4 | Steam Workshop integration | 🔴 Not Started |

---

## 9. References

| Resource | Location | Purpose |
|----------|----------|---------|
| EXPORT_TABLE.md | `ghidra/EXPORT_TABLE.md` | 611 Buddha.exe exports |
| DFPF_SPEC.md | `docs/formats/DFPF_SPEC.md` | DFPF container format |
| PROTO_SPEC.md | `docs/formats/PROTO_SPEC.md` | Prototype system |
| MISSION_API.md | `docs/formats/MISSION_API.md` | Lua mission scripting |
| GAME_FILE_INVENTORY.md | `docs/GAME_FILE_INVENTORY.md` | Game file listing |
| DoubleFine Explorer | `tools/reference/DoubleFine-Explorer/` | Reference implementation |

---

## 10. Appendix: Bundle Override Example

### Example: Texture Override

**Original Texture Path:** `Textures/UI/MenuBackground.dds`

**Game Bundle Loading Order:**
1. `00Startup` - Loads `all.proto`
2. `Man_Gfx` - Contains `Textures/UI/MenuBackground.dds`
3. `DLC1_Stuff` - Does NOT contain this file

**Mod Structure:**
```
MyMod.bmod/
└── content/
    └── Win/
        └── Packs/
            └── MyModBundle.~h/.~p
                └── Textures/UI/MenuBackground.dds
```

**Result:** When `MyModBundle` loads AFTER `Man_Gfx`, the mod's texture overrides the game texture.

---

*Document Version: 1.0*
*Research by: Claude Code*
*Last Updated: 2026-04-01*
