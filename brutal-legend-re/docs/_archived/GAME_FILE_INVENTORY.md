# Brutal Legend - Game File Inventory

**Game Install Path:** Steam game installation directory
**Inventory Date:** April 1, 2026
**Total Game Size:** 8.06 GB
**Total File Count:** 546 files

---

## 1. Win/Packs/ Directory - Bundle Files (.~h and .~p)

The `Win/Packs/` directory contains 42 `.~h` (header) and `.~p` (data/patch) files. These are the main game data bundles used by the Buddha engine.

### 1.1 Header Files (.~h)

| File | Size (KB) | Description |
|------|-----------|-------------|
| 00Startup.~h | 2.62 | Startup bundle |
| DLC1_Stuff.~h | 528.07 | DLC1 content headers |
| DLC2_Stuff.~h | 2.25 | DLC2 content headers |
| Loc_deDE.~h | 4.96 | German localization |
| Loc_enUS.~h | 4.42 | English localization |
| Loc_esES.~h | 4.96 | Spanish localization |
| Loc_frFR.~h | 4.96 | French localization |
| Loc_itIT.~h | 4.96 | Italian localization |
| Man_Audio.~h | 8.21 | Audio manifest |
| Man_Gfx.~h | 123.67 | Graphics manifest |
| Man_Script.~h | 18.19 | Script manifest |
| Man_Trivial.~h | 700.19 | Trivial data manifest |
| RgB_Ctsn.~h | 1453.60 | Rags & Riches (B) Cutscene data |
| RgB_Faction.~h | 358.27 | Rags & Riches (B) Faction data |
| RgB_Mission.~h | 48.44 | Rags & Riches (B) Mission data |
| RgB_World.~h | 432.71 | Rags & Riches (B) World data |
| RgS_Ctsn.~h | 70.29 | Rags & Riches (S) Cutscene data |
| RgS_Faction.~h | 343.35 | Rags & Riches (S) Faction data |
| RgS_Mission.~h | 6.16 | Rags & Riches (S) Mission data |
| RgS_World.~h | 486.50 | Rags & Riches (S) World data |
| RgS_World2.~h | 172.59 | Rags & Riches (S) World2 data |

### 1.2 Data/Patch Files (.~p)

| File | Size (KB) | Description |
|------|-----------|-------------|
| 00Startup.~p | 1664 | Startup bundle data |
| DLC1_Stuff.~p | 145856 | DLC1 content data |
| DLC2_Stuff.~p | 64 | DLC2 content data |
| Loc_deDE.~p | 6400 | German localization |
| Loc_enUS.~p | 5760 | English localization |
| Loc_esES.~p | 6400 | Spanish localization |
| Loc_frFR.~p | 6400 | French localization |
| Loc_itIT.~p | 6400 | Italian localization |
| Man_Audio.~p | 2816 | Audio manifest data |
| Man_Gfx.~p | 76800 | Graphics manifest data |
| Man_Script.~p | 832 | Script manifest data |
| Man_Trivial.~p | 13312 | Trivial data manifest |
| RgB_Ctsn.~p | 77248 | Rags & Riches (B) Cutscene data |
| RgB_Faction.~p | 23040 | Rags & Riches (B) Faction data |
| RgB_Mission.~p | 4864 | Rags & Riches (B) Mission data |
| RgB_World.~p | 130176 | Rags & Riches (B) World data |
| RgS_Ctsn.~p | 87616 | Rags & Riches (S) Cutscene data |
| RgS_Faction.~p | 264320 | Rags & Riches (S) Faction data |
| RgS_Mission.~p | 4608 | Rags & Riches (S) Mission data |
| RgS_World.~p | 399360 | Rags & Riches (S) World data |
| RgS_World2.~p | 169344 | Rags & Riches (S) World2 data |

### 1.3 Total Win/Packs Size: 1404.35 MB

### 1.4 Bundle Naming Convention

- **RgB_*** = Rags & Riches Bundle (Base game)
- **RgS_*** = Rags & Riches Bundle (Streaming/loaded data)
- **Loc_*** = Localization bundles (deDE, enUS, esES, frFR, itIT)
- **Man_*** = Manifest bundles (Audio, Gfx, Script, Trivial)
- **DLC*_Stuff.*** = Downloadable content bundles
- **00Startup.*** = Initial startup loading bundle

---

## 2. Data/ Directory

The `Data/` directory contains 462 files organized into the following structure:

### 2.1 Top-Level Structure

| Directory | Contents |
|-----------|----------|
| `Data/Config/` | Configuration files (Lua scripts, Buddha.cfg) |
| `Data/Clumps/` | Preload data clumps |
| `Data/Cutscenes/` | Bik video files (DF_Logo, INTRO, END CREDITS, etc.) |
| `Data/DLC1/` | DLC1 additional content |
| `Data/Fonts/` | TTF fonts (Arial, FreeMono, FreeSans, ProggySquareSZ, Wolf4) |
| `Data/UI/` | User interface resources (gfx files, movies) |

### 2.2 Key File Types

| Extension | Description | Example |
|-----------|-------------|---------|
| `.bik` | Bink video (Radial Games video codec) | title.bik, INTR1.bik |
| `.gfx` | UI graphics bundle | HUD.gfx, FrontEnd.gfx |
| `.lua` | Lua configuration scripts | boot.lua, input.lua |
| `.cfg` | Buddha engine configuration | Buddha.cfg, BuddhaDefault.cfg |
| `.Clumps` | Game data clump archive | DLC1.Clumps |
| `.ttf` | TrueType fonts | arial.ttf, FreeSans.ttf |

### 2.3 Notable Data Files

#### Configuration Files (Data/Config/)
- `boot.lua` - Boot configuration
- `Buddha.cfg` - Buddha engine configuration
- `BuddhaDefault.cfg` - Default Buddha settings (references FMOD Designer)
- `input.lua` - Input configuration
- `Language.cfg` - Language settings
- `SDLGamepad.config` - Gamepad mapping
- `unmunged.cfg` - Unmunged configuration
- `user.lua` - User preferences

#### Cutscene Files (Data/Cutscenes/)
- `DF_Logo.bik` - Double Fine logo
- `DIST1.bik` - Distributor logo
- `INTR1.bik`, `INTR2.bik`, `INTR3_Gore.bik`, `INTR3_NoGore.bik` - Intro sequences
- `MPTU.bik`, `MPTU_PS3.bik` - ESRB ratings
- `FINI.bik`, `PREF.bik`, `SBST1.bik`, `TEDI1.bik` - Misc videos
- `endCreditsCELEB.bik`, `endCreditsDF.bik`, `endCreditsEA.bik`, `endCreditsTL.bik` - End credits
- Faction-specific jumbotron videos (FactionA through FactionL)
- Regional PEGI and ESRB variants

#### UI Structure (Data/UI/)
- `FrontEnd/` - Main menu (movies in DE, ES, FR, IT, FR, IT subdirs)
- `HUD/` - Heads-up display
- `Loading/` - Loading screens
- `Journal/` - In-game journal
- `Lore_01` through `Lore_13/` - Lore entries
- `Chapters/` - Chapter selection
- `ConceptArt/` - Concept art viewer
- `TitleCard/` - Title cards
- `MissionTitle/` - Mission titles
- `TC_*` directories - Tattoo Commander ability icons
- Controller icon sets: `Xbox360_ControllerIcons/`, `PS3_ControllerIcons/`, `PhysicalInputIcons/`

---

## 3. DLL Dependencies (Root Directory)

| DLL | Size (KB) | Purpose |
|-----|-----------|---------|
| `binkw32.dll` | 226.09 | Bink Video codec (Radial Games) |
| `steam_api.dll` | 101.48 | Steamworks API |

**Note:** FMOD is referenced in `BuddhaDefault.cfg` but the FMOD DLL is not present in the game root. The audio system likely loads FMOD dynamically or uses an embedded version.

---

## 4. Top-Level Files

| File | Size (KB) | Description |
|------|-----------|-------------|
| `BrutalLegend.exe` | - | Main executable |

---

## 5. Redistributable Directory (Redist/)

| File | Description |
|------|-------------|
| `DirectX/DXSETUP.exe` | DirectX installer |
| `DirectX/DSETUP.dll` | DirectX setup DLL |
| `DirectX/dsetup32.dll` | DirectX setup DLL (32-bit) |
| `vcredist_2008_x86.exe` | Visual C++ 2008 Redistributable |
| `vcredist_2010_x86.exe` | Visual C++ 2010 Redistributable |

---

## 6. Extraction Tools

### 6.1 DoubleFine Explorer (Reference)

**Location:** `brutal-legend-re/tools/reference/DoubleFine-Explorer/`

**Status:** Source code only (Delphi Pascal) - requires compilation

**Description:** A comprehensive explorer tool by Bennyboy that supports Brutal Legend and many other Double Fine games. It can view, extract, and convert resources including text, speech, music, scripts, and images.

**Supported Features:**
- View and extract bundle contents
- Decode FSB audio files
- Extract textures and images
- Handle various Buddha/Moai engine formats

**Requirements to Build:**
- Delphi IDE (Embarcadero RAD Studio)
- Bass.dll for audio preview

**Documentation:** `Readme/Double Fine Explorer.html`

### 6.2 dfpf-toolkit

**Location:** `brutal-legend-re/tools/dfpf-toolkit/dfpf_v5.ksy`

**Description:** Kaitai Struct definition for DFPF file format (Double Fine Pack File)

---

## 7. Bundle Format Summary

Based on the `.~h/.~p` file structure:

| Aspect | Description |
|--------|-------------|
| **Format** | Split header+data bundle system |
| **Header (.~h)** | Contains file manifest, names, offsets |
| **Data (.~p)** | Contains actual resource data |
| **Engine** | Buddha engine (Double Fine) |
| **Audio** | FMOD Designer (referenced) |
| **Video** | Bink Video codec |
| **Localization** | 5 languages (DE, EN, ES, FR, IT) |

---

## 8. File Count Summary

| Location | File Count |
|----------|------------|
| Win/Packs/ (.~h + .~p) | 42 |
| Data/ (all files) | 462 |
| **Total Game Files** | **546** |

---

## 9. Game Size Breakdown

| Component | Approximate Size |
|-----------|------------------|
| Win/Packs bundles | ~1404 MB |
| Data/ directory | ~7000 MB |
| **Total** | **~8257 MB (8.06 GB)** |

---

*Generated: April 1, 2026*
