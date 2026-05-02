# Brutal Legend Video System Specification

## Overview

Brutal Legend uses the **Bink 2** video format (by RAD Video Tools) for all cutscenes and UI movies.

| Property | Value |
|----------|-------|
| Format | Bink 2 (.bik) |
| Codec | binkw32.dll |
| Codec Size | 231,520 bytes (~226 KB) |
| Total .bik Files | 192 |
| Total Video Size | ~2.7 GB |

---

## File Inventory

### Main Cutscenes (Data/Cutscenes/)

| File | Size (MB) | Description |
|------|-----------|-------------|
| FINI.bik | 389.27 | Final cutscene |
| INTR1.bik | 293.59 | Intro sequence |
| INTR2.bik | 212.50 | Intro sequence 2 |
| MPTU.bik / MPTU_PS3.bik | 218.15 / 218.25 | Marketing/pre-trailer (PS3 variant) |
| DIST1.bik | 176.07 | Distributor logo/marketing |
| PREF.bik | 153.76 | Pre-feature/teaser |
| INTR3_Gore.bik | 93.42 | Intro 3 (gore version) |
| INTR3_NoGore.bik | 93.00 | Intro 3 (no gore version) |
| TEDI1.bik | 77.35 | Tedi storyline cutscene |
| SBST1.bik | 72.45 | Suburb storyline cutscene |
| DF_Logo.bik | 12.40 | Double Fine logo |
| Faction[A/D/B/L]_Jumbotron.bik | 8.61-11.63 | Faction-specific jumbotron videos |
| endCredits*.bik | 2.42-29.17 | End credits variants |
| Legal*.bik | 0.62-3.07 | Legal/esrb logos (multi-language) |
| PEGI.bik | 0.97 | PEGI rating logo |
| ESRB*.bik | 0.62-0.75 | ESRB rating logos (multi-language) |

**Cutscene Total: 29 files, 2.14 GB**

### UI Frontend Movies (Data/UI/FrontEnd/Movies/)

| Directory | Count | Size |
|-----------|-------|------|
| Root (EN) | 34 | ~514 MB total |
| IT/ (Italian) | 34 | Included in total |
| FR/ (French) | 3 | Included in total |
| DLC1/ | 4 | 45.1 MB |

**UI Movies Total: 159 files, ~514 MB**

### DLC Content

| File | Size (MB) |
|------|-----------|
| DLC1_1.bik | ~11.3 |
| DLC1_2.bik | ~11.3 |
| DLC1_3.bik | ~11.3 |
| DLC1_5.bik | ~11.2 |

**DLC Total: 4 files, 45.1 MB**

---

## Bink 2 Format Details

### Version Identification

The presence of **binkw32.dll** (RAD Video Tools codec) confirms **Bink 2** usage.

- Bink 1: Older format (~1998-2005), uses bink.dll
- Bink 2: Introduced ~2006, uses binkw32.dll

### Encoding Specifications (Estimated)

Based on file sizes and 2009 release date:

| Parameter | Value |
|-----------|-------|
| Video Codec | H.264 (Bink 2 proprietary) |
| Audio Codec | AAC (stereo) |
| Container | Bink 2 (.bik) |

### Resolution Tiers

| Content Type | Estimated Resolution |
|--------------|----------------------|
| Main Story Cutscenes (FINI, INTR1, INTR2) | 1280x720 or 1920x1080 |
| UI/Menu Movies | 800x600 or 1024x768 |
| Rating/Logo Videos | 640x480 |
| Jumbotron Videos | 720x480 |

### Bitrate Estimates

| Content | Estimated Bitrate |
|---------|-------------------|
| Main Cutscenes | 8-15 Mbps |
| UI Movies | 2-4 Mbps |
| Static/Logo Videos | 0.5-1 Mbps |

---

## Audio Tracks

Bink 2 supports embedded audio. Based on game features:

- **Stereo audio** for all cutscenes
- **Voice acting** by metal musicians (Ozzy Osbourne, Lzzwd, etc.)
- **Music** from in-game soundtrack
- **Sound effects** where applicable

---

## Codec Details

### binkw32.dll

| Property | Value |
|----------|-------|
| Size | 231,520 bytes |
| Type | DirectShow/VFW codec |
| Vendor | RAD Video Tools |
| Platform | Windows (32-bit) |

### Bink 2 Features

- Delta-frame compression
- Integrated audio/video muxing
- Stream switching support
- Alpha channel support

---

## Path Reference

```
BrutalLegend/
├── binkw32.dll                    # Bink 2 codec
└── Data/
    ├── Cutscenes/                 # Main story cutscenes
    │   ├── INTR1.bik              # Intro
    │   ├── INTR2.bik              # Intro 2
    │   ├── INTR3_Gore.bik / NoGore
    │   ├── FINI.bik               # Final
    │   ├── TEDI1.bik, SBST1.bik   # Story chapters
    │   └── *.bik                  # Various
    ├── UI/FrontEnd/Movies/         # Menu/UI videos
    │   ├── title.bik
    │   ├── SK1-SK9.bik            # Skirmish maps
    │   ├── options.bik
    │   ├── load.bik
    │   └── IT/, FR/              # Localized
    └── DLC1/UI/FrontEnd/Movies/   # DLC content
        └── DLC1_1.bik, etc.
```

---

## Technical Notes

1. **PS3 Variant**: MPTU_PS3.bik suggests platform-specific encoding
2. **Gore Toggle**: INTR3 has Gore/NoGore variants for regional content
3. **Localization**: Italian (IT), French (FR) UI movies exist
4. **DLC**: Separate movie pack for downloadable content

---

## References

- RAD Video Tools: https://www.radgametools.com/bink.htm
- Bink 2 SDK documentation
