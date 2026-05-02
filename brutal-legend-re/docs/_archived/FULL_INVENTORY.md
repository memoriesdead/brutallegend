# Brutal Legend DFPF Bundle Extraction Inventory

## Summary

Extracted **21 DFPF V5 bundles** from Brutal Legend (42 total files - .~h header and .~p data pairs).
Skipped **00Startup** as instructed (small bundle with different format, all.proto already manually extracted).

**Note:** The dfpf_extract.py tool has systematic issues with filename parsing. Most files are extracted with corrupted offset-based names (e.g., `file_0144_offset_1448448.Texture`) instead of proper game paths. See Extraction Issues section below.

---

## Bundle Inventory

### 1. 00Startup (SKIPPED)
- **Status:** Skipped - small bundle with different format
- **all.proto:** Already manually extracted
- **Location:** `extracted/00Startup/`

### 2. DLC1_Stuff
- **Header:** `DLC1_Stuff.~h` (1,317,765 bytes)
- **Data:** `DLC1_Stuff.~p` (149,356,544 bytes)
- **Files Extracted:** 418 total (2 proper, 416 corrupted)
- **Extracted Size:** 58,374,327 bytes (58 MB)
- **Errors:** Extensive decompression failures, size mismatches, embedded null characters in filenames
- **Key Files:** DLC content (textures, models)

### 3. DLC2_Stuff
- **Header:** `DLC2_Stuff.~h` (2,302 bytes)
- **Data:** `DLC2_Stuff.~p` (65,536 bytes)
- **Files Extracted:** 1 total (0 proper, 1 corrupted)
- **Extracted Size:** 2,048 bytes
- **Errors:** Severe decompression and filename corruption
- **Key Files:** DLC2 gameplay content (solos)

### 4. Loc_deDE (German Localization)
- **Header:** `Loc_deDE.~h` (5,078 bytes)
- **Data:** `Loc_deDE.~p` (6,553,600 bytes)
- **Files Extracted:** 37 total (1 proper, 36 corrupted)
- **Extracted Size:** 9,692,864 bytes (9.2 MB)
- **Errors:** Size mismatches, corrupted filenames
- **Key Files:** German localization textures

### 5. Loc_enUS (English Localization)
- **Header:** `Loc_enUS.~h` (4,522 bytes)
- **Data:** `Loc_enUS.~p` (5,898,240 bytes)
- **Files Extracted:** 37 total (1 proper, 36 corrupted)
- **Extracted Size:** 8,307,224 bytes (7.9 MB)
- **Errors:** Decompression failures, size mismatches
- **Key Files:** English localization textures (loading screens, UI)

### 6. Loc_esES (Spanish Localization)
- **Header:** `Loc_esES.~h` (5,078 bytes)
- **Data:** `Loc_esES.~p` (6,553,600 bytes)
- **Files Extracted:** 37 total (1 proper, 36 corrupted)
- **Extracted Size:** 9,714,760 bytes (9.3 MB)
- **Errors:** Size mismatches, corrupted filenames

### 7. Loc_frFR (French Localization)
- **Header:** `Loc_frFR.~h` (5,078 bytes)
- **Data:** `Loc_frFR.~p` (6,553,600 bytes)
- **Files Extracted:** 37 total (1 proper, 36 corrupted)
- **Extracted Size:** 9,692,864 bytes (9.2 MB)
- **Errors:** Size mismatches, corrupted filenames

### 8. Loc_itIT (Italian Localization)
- **Header:** `Loc_itIT.~h` (5,078 bytes)
- **Data:** `Loc_itIT.~p` (6,553,600 bytes)
- **Files Extracted:** 37 total (1 proper, 36 corrupted)
- **Extracted Size:** 9,692,864 bytes (9.2 MB)
- **Errors:** Size mismatches, corrupted filenames

### 9. Man_Audio
- **Header:** `Man_Audio.~h` (8,402 bytes)
- **Data:** `Man_Audio.~p` (2,883,584 bytes)
- **Files Extracted:** 69 total (1 proper, 68 corrupted)
- **Extracted Size:** 11,662,383 bytes (11.1 MB)
- **Errors:** Decompression failures, embedded null characters
- **Key Files:** Audio programmer reports, wavebank markers

### 10. Man_Gfx
- **Header:** `Man_Gfx.~h` (126,634 bytes)
- **Data:** `Man_Gfx.~p` (78,643,200 bytes)
- **Files Extracted:** 1,442 total (3 proper, 1,439 corrupted)
- **Extracted Size:** 726,791,110 bytes (693 MB)
- **Errors:** Invalid arguments, embedded null characters
- **Key Files:** UI textures (DUI movies, flash), HUD elements

### 11. Man_Script
- **Header:** `Man_Script.~h` (18,628 bytes)
- **Data:** `Man_Script.~p` (851,968 bytes)
- **Files Extracted:** 539 total (274 proper, 265 corrupted)
- **Extracted Size:** 29,647,116 bytes (28.3 MB)
- **Errors:** Decompression failures on some files
- **Key Files:** LUA scripts (275 .lua files found)

#### Man_Script Lua Scripts Found:
- `buddhastartup.lua`
- `defaultopponent*.lua` (multiple factions)
- `missionbase.lua`
- `campaigngamemission.lua`
- `campaignskirmishmission.lua`
- `buddha.lua`
- `assets.lua`
- `missions/*.lua`

### 12. Man_Trivial
- **Header:** `Man_Trivial.~h` (716,990 bytes)
- **Data:** `Man_Trivial.~p` (13,631,488 bytes)
- **Files Extracted:** 1,586 total (10 proper, 1,576 corrupted)
- **Extracted Size:** 3,449,223,428 bytes (3.2 GB)
- **Errors:** Invalid filename characters, embedded nulls
- **Key Files:** Audio environment data, particle effects, character materials

### 13. RgB_Ctsn
- **Header:** `RgB_Ctsn.~h` (1,488,486 bytes)
- **Data:** `RgB_Ctsn.~p` (79,101,952 bytes)
- **Files Extracted:** 11,182 total (59 proper, 11,123 corrupted)
- **Extracted Size:** 877,679,934 bytes (837 MB)
- **Errors:** Size mismatches, invalid filename characters
- **Key Files:** Cutscene animations, dialog reactions, character animations

### 14. RgB_Faction
- **Header:** `RgB_Faction.~h` (366,870 bytes)
- **Data:** `RgB_Faction.~p` (23,592,960 bytes)
- **Files Extracted:** 3,976 total (8 proper, 3,968 corrupted)
- **Extracted Size:** 128,458,114 bytes (122 MB)
- **Errors:** Size mismatches on thousands of files
- **Key Files:** Faction-specific animations and resources

### 15. RgB_Mission
- **Header:** `RgB_Mission.~h` (49,602 bytes)
- **Data:** `RgB_Mission.~p` (4,980,736 bytes)
- **Files Extracted:** 480 total (0 proper, 480 corrupted)
- **Extracted Size:** 5,993,688 bytes (5.7 MB)
- **Errors:** All files extracted with offset-based names

### 16. RgB_World
- **Header:** `RgB_World.~h` (443,092 bytes)
- **Data:** `RgB_World.~p` (133,300,224 bytes)
- **Files Extracted:** 6,754 total (11 proper, 6,743 corrupted)
- **Extracted Size:** 413,890,300 bytes (395 MB)
- **Errors:** Invalid filename characters
- **Key Files:** World geometry, environment textures

### 17. RgS_Ctsn
- **Header:** `RgS_Ctsn.~h` (71,972 bytes)
- **Data:** `RgS_Ctsn.~p` (89,718,784 bytes)
- **Files Extracted:** 844 total (1 proper, 843 corrupted)
- **Extracted Size:** 163,908,607 bytes (156 MB)
- **Errors:** Size mismatches

### 18. RgS_Faction
- **Header:** `RgS_Faction.~h` (351,588 bytes)
- **Data:** `RgS_Faction.~p` (270,663,680 bytes)
- **Files Extracted:** 4,441 total (4 proper, 4,437 corrupted)
- **Extracted Size:** 836,557,121 bytes (798 MB)
- **Errors:** Size mismatches on thousands of files
- **Key Files:** Faction textures, materials, fur data

### 19. RgS_Mission
- **Header:** `RgS_Mission.~h` (6,312 bytes)
- **Data:** `RgS_Mission.~p` (4,718,592 bytes)
- **Files Extracted:** 54 total (0 proper, 54 corrupted)
- **Extracted Size:** 9,625,590 bytes (9.2 MB)
- **Errors:** All files extracted with offset-based names

### 20. RgS_World
- **Header:** `RgS_World.~h` (498,172 bytes)
- **Data:** `RgS_World.~p` (408,944,640 bytes)
- **Files Extracted:** 6,560 total (17 proper, 6,543 corrupted)
- **Extracted Size:** 840,440,163 bytes (801 MB)
- **Errors:** Size mismatches, invalid filename characters
- **Key Files:** World models, environment textures

#### Sample Properly Named Files from RgS_World:
- `environments/a/canyonimpaler/props/model/largechaina.bin`
- `environments/a/headbangerquarry/model/cauldron_a_lod2.bin`
- `environments/a/spidercanyon/model/web_breakableframe.bin`
- `environments/b/trees/model/boneyhandtreeb_lod1.bin`

### 21. RgS_World2
- **Header:** `RgS_World2.~h` (176,734 bytes)
- **Data:** `RgS_World2.~p` (173,408,256 bytes)
- **Files Extracted:** 4,059 total (5 proper, 4,054 corrupted)
- **Extracted Size:** 690,646,272 bytes (659 MB)
- **Errors:** Size mismatches

---

## Key Files Found

### Proto Files (all.proto)
- `extracted/00Startup/all.proto`
- `extracted/00Startup/data/all.proto`
- `extracted/00Startup/data/all.proto.bin`

### Lua Scripts (275 total)
Located in `Man_Script/lua_scripts/`:
- `data/script/buddhastartup.lua`
- `data/script/compopponents/defaultopponent*.lua`
- `data/script/missionbase.lua`
- `data/script/missions/*.lua`
- And many more mission and component scripts

### Audio Files
Found in `Man_Audio/`:
- Audio programmer reports (.AudioProgram)
- Audio wavebank data

### Textures
Found across multiple bundles:
- Localization textures (loading screens, UI) in Loc_* bundles
- Environment textures in RgS_World, RgB_World
- UI textures in Man_Gfx

---

## Extraction Issues

### Systematic Filename Corruption
The dfpf_extract.py tool reads filenames from a name directory but most filenames are being parsed incorrectly, resulting in:
- Files named `file_XXXX_offset_YYYYYY.bin` instead of proper paths
- Files with embedded null characters causing "Invalid argument" errors
- Files with corrupted extension fields

**Root Cause:** The filename offset calculation in FileRecord parsing appears to be incorrect for this dataset. The name directory offset calculation at line 60:
```python
self.name_position = name_dir_offset + self.name_offset
```
produces incorrect positions for most files.

### Decompression Failures
Many files show:
- `Error -5 while decompressing data: incomplete or truncated stream`
- `Error -3 while decompressing data: invalid stored block lengths`
- `Second decompression attempt failed`

This suggests either:
1. The compression type detection is incorrect
2. The size/offset fields are misaligned
3. The data files use a different compression scheme

### Size Mismatch Warnings
Thousands of files produce "Warning: Size mismatch" messages, indicating the uncompressed size field doesn't match actual decompressed data.

---

## Extracted File Totals

| Bundle | Total Files | Proper Names | Corrupted | Size (bytes) |
|--------|-------------|--------------|-----------|--------------|
| 00Startup | 16 | 3 | 13 | 6,510,850 |
| DLC1_Stuff | 418 | 2 | 416 | 58,374,327 |
| DLC2_Stuff | 1 | 0 | 1 | 2,048 |
| Loc_deDE | 37 | 1 | 36 | 9,692,864 |
| Loc_enUS | 37 | 1 | 36 | 8,307,224 |
| Loc_esES | 37 | 1 | 36 | 9,714,760 |
| Loc_frFR | 37 | 1 | 36 | 9,692,864 |
| Loc_itIT | 37 | 1 | 36 | 9,692,864 |
| Man_Audio | 69 | 1 | 68 | 11,662,383 |
| Man_Gfx | 1,442 | 3 | 1,439 | 726,791,110 |
| Man_Script | 539 | 274 | 265 | 29,647,116 |
| Man_Trivial | 1,586 | 10 | 1,576 | 3,449,223,428 |
| RgB_Ctsn | 11,182 | 59 | 11,123 | 877,679,934 |
| RgB_Faction | 3,976 | 8 | 3,968 | 128,458,114 |
| RgB_Mission | 480 | 0 | 480 | 5,993,688 |
| RgB_World | 6,754 | 11 | 6,743 | 413,890,300 |
| RgS_Ctsn | 844 | 1 | 843 | 163,908,607 |
| RgS_Faction | 4,441 | 4 | 4,437 | 836,557,121 |
| RgS_Mission | 54 | 0 | 54 | 9,625,590 |
| RgS_World | 6,560 | 17 | 6,543 | 840,440,163 |
| RgS_World2 | 4,059 | 5 | 4,054 | 690,646,272 |

**Grand Total: 42,603 files extracted (403 proper names, 42,200 corrupted)**

---

## Recommendations for Fixing the Extractor

1. **Debug name directory parsing** - Add verbose logging of raw name directory bytes to understand the encoding
2. **Check compression type flags** - The compression type field may need different interpretation
3. **Verify offset calculations** - Compare parsed offsets against actual file positions in .~p files
4. **Handle null-padded filenames** - Filenames may use null padding instead of null terminators
5. **Reference DoubleFine Explorer** - The txt manifest files suggest the original tool could extract properly

---

## Manifest Files Reference

The Win/Packs directory contains .txt manifest files generated by DoubleFine Explorer that list expected bundle contents:
- `00Startup.txt`
- `dlc1_stuff.txt` (13,177,765 bytes - 12,284 assets)
- `loc_enus.txt` (4,140 bytes - 37 assets)
- `man_audio.txt` (11,168 bytes - 101 assets)
- `man_gfx.txt` (137,391 bytes)
- `man_script.txt` (28,647 bytes - 266 assets)
- `man_trivial.txt` (1,103,502 bytes)
- `rgb_ctsn.txt` (1,859,652 bytes - 16,453 assets)
- `rgs_ctsn.txt` (90,838 bytes)

These manifests can be used to validate extraction quality and identify missing files.

---

## Output Location

All files extracted to: `extracted/`

Generated: 2026-04-01