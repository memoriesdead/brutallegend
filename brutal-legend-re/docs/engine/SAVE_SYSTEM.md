# Brutal Legend Save System Documentation

**Status:** 🔴 Research Required  
**Game:** Brutal Legend (2009)  
**Engine:** Buddha (Double Fine proprietary)  
**Last Updated:** 2026-04-01

---

## Executive Summary

**No `.sav` files were found in the standard AppData location** (`%APPDATA%\Doublefine\BrutalLegend\`). The directory contains only:
- `screen.dat` (76 bytes) - Display settings (confirmed NOT save data)
- `SDLGamepad.config` (510 bytes) - Gamepad configuration
- A Steam ID folder (empty)

This suggests either:
1. Save files are stored elsewhere (Steam Cloud, game directory)
2. Save format uses a different extension
3. Save data is embedded within the DFPF archive structure

**Key Finding:** `screen.dat` contains display settings (resolution 3840x2160 @ 120Hz, vsync=true), NOT save data.

---

## 1. Save File Locations

### 1.1 Expected Locations

| Location | Status | Notes |
|----------|--------|-------|
| `%APPDATA%\Doublefine\BrutalLegend\` | ⚠️ No .sav files | Only screen.dat and config |
| `%LOCALAPPDATA%\Doublefine\BrutalLegend\` | ❓ Unknown | Not verified |
| Steam Cloud | ⚠️ Possible | Steam may store saves remotely |
| Game install directory | ❓ Unknown | Not verified |
| Documents folder | ❓ Unknown | Not verified |

### 1.2 Findings from User's System

```
AppData\Doublefine\BrutalLegend\
├── 76561199317189285\ (empty - Steam ID folder)
├── screen.dat (76 bytes) - Display settings ONLY
└── SDLGamepad.config (510 bytes)
```

**screen.dat contents (display settings, NOT save data):**
```
fullscreen = true
width = 3840
height = 2160
refreshrate = 120
vsync = true
```

**Note:** The Steam ID folder (76561199317189285) suggests the user is playing the Steam version.

---

## 2. Buddha Engine Architecture

### 2.1 Known Systems

Based on [ARCHITECTURE.md](ARCHITECTURE.md) and [FUNCTION_CATALOG.md](FUNCTION_CATALOG.md):

```
BrutalLegend.exe
├── DFPF Container System (.~h/.~p pairs)
│   ├── Man_Script.~h/.~p - Mission Lua scripts
│   ├── Man_Trivial.~h/.~p - Models, textures
│   └── 00Startup.~h/.~p - Core prototypes
├── Lua Engine - Mission scripting, game logic
├── FMOD Audio - FSB sound banks
├── Havok Physics - (expected for 2009)
├── Bink Video - Cutscenes
└── Scaleform GFx - UI system
```

### 2.2 Save System Functions

The [FUNCTION_CATALOG.md](FUNCTION_CATALOG.md) lists these placeholder functions:

| Category | Function | Status |
|----------|----------|--------|
| Save System | Save file read/write | 🔴 TODO |
| Save System | Checkpoint creation | 🔴 TODO |

These are placeholders to be populated after Ghidra analysis of BrutalLegend.exe.

---

## 3. DFPF Container Format

### 3.1 Format Overview

Brutal Legend uses the **DFPF V5** container format (big-endian) for game assets:

- `filename.~h` - Header/index file (88 bytes + file records)
- `filename.~p` - Data payload file

### 3.2 DFPF V5 Structure

See [DFPF_SPEC.md](../formats/DFPF_SPEC.md) and [DFPF_ANALYSIS.md](../formats/DFPF_ANALYSIS.md) for full details.

**Header (88 bytes):**

| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 4 | Magic: "dfpf" |
| 0x04 | 1 | Version (5 for Brutal Legend) |
| 0x05 | 8 | FileExtensionOffset |
| 0x0D | 8 | NameDirOffset |
| 0x15 | 4 | FileExtensionCount |
| 0x19 | 4 | NameDirSize |
| 0x1D | 4 | NumFiles |
| 0x21 | 8 | FileRecordsOffset |

**File Record (16 bytes each):**

```
Bytes 0-3:  UncompressedSize (>>8), NameOffset (>>11)
Bytes 4-7:  Offset (>>3)
Bytes 8-11: Size (<<5>>9), FileTypeIndex (<<4>>24>>1)
Byte 12:   CompressionType (AND 15)
```

**Compression Types (V5):**
| Type | Meaning |
|------|---------|
| 4 | Uncompressed |
| 8 | ZLIB compressed |
| 12 | XMemCompress (Xbox) |

---

## 4. Research Hypotheses

### 4.1 Hypothesis: Saves Inside DFPF Archives

**Possibility:** Save data might be stored within DFPF archives rather than as separate files.

**Evidence:**
- No external save files found in AppData
- Game assets use DFPF containers exclusively
- Some Double Fine games store save data in archives

**Investigation Needed:**
1. Search DFPF archives for save-related file names (save, game, progress, state)
2. Extract and analyze `00Startup.~h/.~p` for save data structures
3. Check if `Man_Script.~h/.~p` contains save/load Lua functions

### 4.2 Hypothesis: Steam Cloud Storage

**Possibility:** Saves are stored on Steam Cloud servers rather than locally.

**Evidence:**
- Steam ID folder found in AppData
- Steam Cloud is default for many Steam games
- No local .sav files found

**Investigation Needed:**
1. Check Steam Cloud storage via Steam client
2. Look for `%ProgramFiles%\Steam\userdata\<ID>\225360\`
3. Query Steam Web API for cloud save status

### 4.3 Hypothesis: Proprietary Save Format

**Possibility:** Save files exist but use a non-.sav extension.

**Evidence:**
- File listing shows screen.dat (but confirmed display settings only)
- Some games use .dat, .bin, or other extensions for saves

**Investigation Needed:**
1. Search for other .dat/.bin files in game directory
2. Look for any file with modified date after game played
3. Monitor file system changes during gameplay

---

## 5. Progress Tracking Mechanisms

### 5.1 Mission System

From [MISSION_API.md](../formats/MISSION_API.md):

```
Missions are written in Lua and control story progression, objectives, and events.
```

**Known Files:**
- `Man_Script.~h/.~p` - Contains Lua mission scripts
- Missions are text-editable Lua files

### 5.2 Unlocks System

From [ARCHITECTURE.md](ARCHITECTURE.md):

| Feature | Supported |
|---------|-----------|
| Character swaps | ✅ Yes |
| Faction swaps | ✅ Yes |
| Texture replacement | ✅ Yes |
| Audio replacement | ✅ Yes |
| New missions | 🔴 No (undocumented) |
| New maps | 🔴 No (undocumented) |
| New characters | 🔴 No (prototype limit) |

### 5.3 Checkpoints

The FUNCTION_CATALOG.md mentions checkpoint functions but they are undocumented.

---

## 6. Modding Community Resources

### 6.1 DoubleFine Explorer

**Repository:** https://github.com/bgbennyboy/DoubleFine-Explorer  
**Status:** Supports Brutal Legend asset extraction  

**Capabilities:**
- View/extract DFPF archives (.~h/.~p pairs)
- Support for .lua, .proto, .fsb, .dds, and other formats
- Does NOT support save file editing

### 6.2 Community Mods

From [PROTO_SPEC.md](../formats/PROTO_SPEC.md):
- Community mod example: "Hair Metal Militia"
- ModDB: https://www.moddb.com/mods/hair-metal-militia

**Note:** No known save editors or save-related mods exist for Brutal Legend.

---

## 7. Investigation Checklist

### File System
- [ ] Check `%LOCALAPPDATA%\Doublefine\BrutalLegend\`
- [ ] Check game install directory for .sav or .dat files
- [ ] Check Steam Cloud storage
- [ ] Check `%ProgramFiles%\Steam\userdata\<ID>\225360\`

### Game Assets
- [ ] Search `00Startup.~h/.~p` for save-related content
- [ ] Search `Man_Script.~h/.~p` for save/load Lua functions
- [x] ~~Extract and hex-analyze screen.dat~~ - **COMPLETE: screen.dat is display settings only**
- [ ] Look for any file containing "save", "game", "state", "progress"

### Executable Analysis
- [ ] Run Ghidra on BrutalLegend.exe
- [ ] Find save/load function addresses
- [ ] Identify save file format structures
- [ ] Document checkpoint creation functions

---

## 8. References

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Buddha engine overview |
| [FUNCTION_CATALOG.md](FUNCTION_CATALOG.md) | Exe function catalog (save functions TODO) |
| [DFPF_SPEC.md](../formats/DFPF_SPEC.md) | DFPF container format spec |
| [DFPF_ANALYSIS.md](../formats/DFPF_ANALYSIS.md) | Detailed DFPF analysis (413 lines) |
| [MISSION_API.md](../formats/MISSION_API.md) | Mission scripting API |
| [DoubleFine Explorer](https://github.com/bgbennyboy/DoubleFine-Explorer) | Asset extraction tool |

---

## 9. Next Steps

1. **~~Hex analyze screen.dat~~** - **COMPLETE: Not save data, just display settings**
2. **Search DFPF archives** - Look for save-related filenames in game bundles
3. **Executable analysis** - Use Ghidra to find save/load functions
4. **Steam Cloud check** - Verify if saves exist on Steam servers

---

## Appendix A: screen.dat Analysis

**File:** `screen.dat`  
**Location:** `%APPDATA%\Doublefine\BrutalLegend\`  
**Size:** 76 bytes  
**Format:** INI-style text

**Contents:**
```ini
fullscreen = true
width = 3840
height = 2160
refreshrate = 120
vsync = true
```

**Conclusion:** This is display configuration, NOT game save data.

---

## Appendix B: DoubleFine Explorer Notes

DoubleFine Explorer by Bennyboy (v1.4.1) supports Brutal Legend but focuses on:
- DFPF archive extraction (.~h/.~p pairs)
- Asset viewing/conversion (lua, fsb, dds, etc.)
- Does NOT handle save file editing

The tool's source code (`uDFExplorer_PAKManager.pas`, etc.) documents the DFPF format in detail.

---

*Research conducted: 2026-04-01*  
*Document version: 1.1*
