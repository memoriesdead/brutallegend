# Inventory Index

**Project:** Brutal Legend Reverse Engineering  
**Last Updated:** 2026-04-01

---

## Overview

This index catalogs all extracted files and inventories from the Brutal Legend game installation.

**Game Path:** Steam game installation directory

---

## Game File Inventory

**Full Listing:** [docs/GAME_FILE_INVENTORY.md](../docs/GAME_FILE_INVENTORY.md)

| Metric | Value |
|--------|-------|
| Total Game Size | 8.06 GB |
| Total File Count | 546 files |
| Bundle Files | 42 (.~h + .~p pairs) |
| Data Files | 462 files |

---

## Win/Packs/ Directory - Bundle Files

### Bundle Inventory

| Bundle Name | Header Size | Data Size | Description |
|-------------|-------------|-----------|-------------|
| 00Startup.~h/.~p | 2.62 KB | 1.66 MB | Core prototypes/scripts |
| Man_Script.~h/.~p | 18.19 KB | 832 KB | Mission Lua scripts |
| Man_Trivial.~h/.~p | 700.19 KB | 13.31 MB | Models, textures |
| Man_Gfx.~h/.~p | 123.67 KB | 76.80 MB | Graphics manifest |
| Man_Audio.~h/.~p | 8.21 KB | 2.82 MB | Audio manifest |
| RgB_World.~h/.~p | 432.71 KB | 130.18 MB | Base game world |
| RgS_World.~h/.~p | 486.50 KB | 399.36 MB | Streaming world data |
| RgS_World2.~h/.~p | 172.59 KB | 169.34 MB | World2 streaming |
| RgB_Faction.~h/.~p | 358.27 KB | 23.04 MB | Faction data |
| RgS_Faction.~h/.~p | 343.35 KB | 264.32 MB | Faction streaming |
| RgB_Ctsn.~h/.~p | 1453.60 KB | 77.25 MB | Cutscene data |
| RgS_Ctsn.~h/.~p | 70.29 KB | 87.62 MB | Cutscene streaming |
| RgB_Mission.~h/.~p | 48.44 KB | 4.86 MB | Mission data |
| RgS_Mission.~h/.~p | 6.16 KB | 4.61 MB | Mission streaming |
| DLC1_Stuff.~h/.~p | 528.07 KB | 145.86 MB | DLC content |
| DLC2_Stuff.~h/.~p | 2.25 KB | 64 KB | DLC2 content |
| Loc_enUS.~h/.~p | 4.42 KB | 5.76 MB | English localization |
| Loc_deDE.~h/.~p | 4.96 KB | 6.40 MB | German localization |
| Loc_esES.~h/.~p | 4.96 KB | 6.40 MB | Spanish localization |
| Loc_frFR.~h/.~p | 4.96 KB | 6.40 MB | French localization |
| Loc_itIT.~h/.~p | 4.96 KB | 6.40 MB | Italian localization |

**Total Win/Packs Size:** ~1.4 GB

---

## Data/ Directory Structure

### Top-Level Directories

| Directory | Contents |
|-----------|----------|
| `Data/Config/` | Configuration files (Lua, .cfg) |
| `Data/Clumps/` | Preload data clumps |
| `Data/Cutscenes/` | Bink video files |
| `Data/DLC1/` | DLC additional content |
| `Data/Fonts/` | TrueType fonts |
| `Data/UI/` | User interface resources |

### Key Configuration Files

| File | Size | Description |
|------|------|-------------|
| `boot.lua` | - | Boot configuration |
| `Buddha.cfg` | - | Buddha engine config |
| `BuddhaDefault.cfg` | - | Default settings (references FMOD Designer) |
| `input.lua` | - | Input configuration |
| `Language.cfg` | - | Language settings |
| `SDLGamepad.config` | 510 B | Gamepad mapping |
| `user.lua` | - | User preferences |

### Cutscene Files (Data/Cutscenes/)

| File | Description |
|------|-------------|
| DF_Logo.bik | Double Fine logo |
| INTR1.bik - INTR3_*.bik | Intro sequences |
| DIST1.bik | Distributor logo |
| MPTU.bik | ESRB rating |
| FINI.bik, PREF.bik | Misc videos |
| SBST1.bik, TEDI1.bik | Story videos |
| endCredits*.bik | End credit sequences |
| FactionA.bik - FactionL.bik | Faction jumbotron videos |

**Total Cutscenes:** 40+ .bik files

### UI Structure (Data/UI/)

| Directory | Contents |
|-----------|----------|
| FrontEnd/ | Main menu (with language subdirs: DE, ES, FR, IT) |
| HUD/ | Heads-up display |
| Loading/ | Loading screens |
| Journal/ | In-game journal |
| Lore_01 - Lore_13/ | Lore entries |
| Chapters/ | Chapter selection |
| ConceptArt/ | Concept art viewer |
| TitleCard/ | Title cards |
| MissionTitle/ | Mission titles |
| TC_*/ | Tattoo Commander ability icons |
| Xbox360_ControllerIcons/ | Controller icons |
| PS3_ControllerIcons/ | Controller icons |
| PhysicalInputIcons/ | Input icons |

### Fonts (Data/Fonts/)

| Font | Description |
|------|-------------|
| arial.ttf | Arial |
| FreeMono.ttf | FreeMono |
| FreeSans.ttf | FreeSans |
| ProggySquareSZ.ttf | Proggy Square |
| Wolf4.ttf | Wolf |

---

## Inventory Status

| Category | Status | Notes |
|----------|--------|-------|
| Win/Packs bundles | ✅ Inventoried | 42 files documented |
| Data/ directory | ✅ Inventoried | 462 files documented |
| Bundle contents | 🔴 Not extracted | Requires extraction tools |
| Individual file inventory | 🔴 Not started | Need to extract all bundles |
| DLC contents | 🔴 Not documented | Need to extract |

---

## Extraction Tools

### DoubleFine Explorer

| Property | Value |
|----------|-------|
| Location | `tools/reference/DoubleFine-Explorer/` |
| Status | Source only (requires Delphi) |
| Purpose | Extract .~h/.~p bundles |
| Repository | https://github.com/bgbennyboy/DoubleFine-Explorer |

### dfpf-toolkit

| Property | Value |
|----------|-------|
| Location | `tools/dfpf-toolkit/` |
| Contains | dfpf_v5.ksy (Kaitai Struct spec) |
| Status | Parser specification created |
| Purpose | Generate parsers for DFPF format |

---

## Extracted Content Inventory

*No extractions recorded yet.*

### Planned Extractions

| Bundle | Contents | Priority |
|--------|----------|----------|
| Man_Script.~h/.~p | Lua mission scripts | High |
| 00Startup.~h/.~p | Prototype definitions | High |
| Man_Trivial.~h/.~p | Models/textures | Medium |
| RgB_Mission.~h/.~p | Mission data | Medium |
| DLC1_Stuff.~h/.~p | DLC content | Low |

---

## Next Steps for Inventory

1. **Extract Man_Script bundle** - List all Lua scripts
2. **Extract 00Startup bundle** - Find all.proto
3. **Create content database** - Index all extracted files
4. **Build file catalog** - Document each file's purpose

---

## Related Documents

| Document | Description |
|----------|-------------|
| [GAME_FILE_INVENTORY.md](../docs/GAME_FILE_INVENTORY.md) | Full game file listing |
| [FORMAT_INDEX.md](../docs/formats/FORMAT_INDEX.md) | Format documentation index |
| [MISSION_ANALYSIS.md](../docs/formats/MISSION_ANALYSIS.md) | Mission system analysis |

---

## File Count Summary

| Location | File Count |
|----------|------------|
| Win/Packs/ (bundles) | 42 |
| Data/ (all files) | 462 |
| **Total** | **546** |

---

## Directory Tree

```
BrutalLegend/
├── BrutalLegend.exe          # Main executable
├── binkw32.dll                # Bink video codec
├── steam_api.dll              # Steamworks API
├── Redist/                    # Redistributables
│   ├── DirectX/
│   └── vcredist_*.exe
├── Win/
│   └── Packs/                 # 42 bundle files
│       ├── 00Startup.~h/.~p
│       ├── Man_Script.~h/.~p
│       ├── Man_Trivial.~h/.~p
│       ├── Man_Gfx.~h/.~p
│       ├── Man_Audio.~h/.~p
│       ├── RgB_*.~h/.~p
│       ├── RgS_*.~h/.~p
│       ├── DLC*_Stuff.~h/.~p
│       └── Loc_*.~h/.~p
└── Data/
    ├── Config/
    ├── Clumps/
    ├── Cutscenes/             # 40+ .bik files
    ├── DLC1/
    ├── Fonts/
    └── UI/                    # Multiple subdirs
```

---

*Last updated: 2026-04-01*
