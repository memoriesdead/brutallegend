# Middleware Documentation

**Status:** In Progress  
**Game:** Brutal Legend  

---

## Confirmed Middleware

### FMOD (Audio)
- FSB sound banks
- Custom encryption
- See [AUDIO_SPEC.md](../formats/AUDIO_SPEC.md)

### ZLib (Compression)
- Standard DEFLATE compression
- Used in DFPF containers and UI .gfx files

### Scaleform GFx (CONFIRMED)
- UI middleware: Scaleform GFx 3.x
- Binary header analysis: 47 46 58 08 (GFX signature, version 3.x)
- ZLib compressed .gfx files
- See [UI_FORMAT.md](../formats/UI_FORMAT.md)

---

## Unconfirmed Middleware

### Havok Physics
- Expected for 2009 era games
- Needs verification

### Bink Video
- Cutscene codec
- Needs verification

---

## TODO

Verify Havok and Bink via dumpbin /imports on BrutalLegend.exe