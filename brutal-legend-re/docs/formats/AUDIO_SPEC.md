# Audio Format Specification

**Status:** Documented  
**Game:** Brutal Legend  
**Total Audio Size:** 4.1 GB (4,315,634,592 bytes)  
**FSB Files:** 156  
**FEV Files:** 29  

---

## Overview

Brutal Legend uses **FMOD** (Firelight Technologies) for its audio system with:
- **FSB (FMOD Sound Bank)** files for audio data
- **FEV (FMOD Event)** files for event configuration
- **Custom encryption** using bit-reversal + XOR with key "DFm3t4lFTW"
- **Embedded FMOD** (no external DLL required)
- **Multi-language support** for 4 languages + DLC

---

## FSB Format Details

### FSB5 Header Structure (60 bytes + sample headers)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0-3 | 4 | Magic | "FSB5" (0x46425335) |
| 4-7 | 4 | Version | Format version |
| 8-11 | 4 | NumSamples | Number of audio samples |
| 12-15 | 4 | SampleHeaderSize | Size of sample header block |
| 16-19 | 4 | NameSize | Size of name block |
| 20-23 | 4 | Datasize | Total data size |
| 24-27 | 4 | Mode | Mode flags |
| 28-59 | 32 | Hash/Zero | Reserved/hash data |

### FSB4 Header Structure (48 bytes)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0-3 | 4 | Magic | "FSB4" (0x46425334) |
| 4-7 | 4 | NumSamples | Number of audio samples |
| 8-11 | 4 | SampleHeaderSize | Size of sample header block |
| 12-15 | 4 | Datasize | Total data size |
| 16-19 | 4 | Version | Format version |
| 20-23 | 4 | HeadMode | Mode flags |
| 24-47 | 24 | Hash/Zero | Reserved/hash data |

---

## Encryption System

### Custom XOR Encryption

- **Key Bytes (hex):** 44 46 6D 33 74 34 6C 46 54 57
- **Key String:** "DFm3t4lFTW" (10 bytes)

### Decryption Algorithm

1. **Bit Reversal:** Each encrypted byte has its bits reversed (LSB becomes MSB)
2. **XOR:** Result is XORed with key byte (key offset wraps at 10)

Algorithm (from uDFExplorer_FSBManager.pas lines 177-216):
- Key offset: j = KeyOffset mod 10

---

## Codec Types

| Codec | FMOD Flag | Description |
|-------|-----------|-------------|
| MPEG | FSOUND_DELTA | MP3 compressed audio |
| PCM8 | FSOUND_8BITS | 8-bit Pulse Code Modulation |
| PCM16 | (default) | 16-bit Pulse Code Modulation |

---

## Audio Asset Inventory

### By Category

| Category | FSB Count | Description |
|----------|-----------|-------------|
| Music_Scripted | 28 | Scripted background music |
| Cutscenes | 31 | Cinematic audio |
| Ambience | 23 | Environmental sounds |
| Faction Units | 13+ | Unit sound effects |
| Faction Vehicles | 10+ | Vehicle sounds |
| Faction Buildings | 6 | Building sounds |
| Bosses | 4 | Boss-specific audio |
| GUI | 1 | Interface sounds |
| Objects | 1 | Interactive objects |
| GuitarStings | 4 | Guitar sting samples |
| Streaming (VO) | 4 | Voice-over by language |

### By Language (Streaming Audio)

| Language | File | Size |
|----------|------|------|
| French | French_Streaming.fsb | 633 MB |
| US English | USEnglish_Streaming.fsb | 630 MB |
| Spanish | Spanish_Streaming.fsb | 629 MB |
| German | German_Streaming.fsb | 628 MB |

### Largest FSB Files

| File | Size | Type |
|------|------|------|
| French_Streaming.fsb | 633 MB | Voice-over |
| USEnglish_Streaming.fsb | 630 MB | Voice-over |
| Spanish_Streaming.fsb | 629 MB | Voice-over |
| German_Streaming.fsb | 628 MB | Voice-over |
| Music_Licenced_3.fsb | 226 MB | Licensed music |
| Music_Licenced_2.fsb | 219 MB | Licensed music |
| Music_Licenced_4.fsb | 200 MB | Licensed music |
| Music_Licenced_1.fsb | 195 MB | Licensed music |
| Ambience_Stream.fsb | 130 MB | Ambient audio |

---

## FMOD Event Files (FEV)

### Known FEV Files (29 total)

- Ambience.fev
- Bosses.fev
- BrutalLegend_French.fev
- BrutalLegend_German.fev
- BrutalLegend_Italian.fev
- BrutalLegend_Spanish.fev
- BrutalLegend_USEnglish.fev
- BL1Patch1_USEnglish.fev
- Cutscenes.fev
- FactionA_Buildings.fev
- FactionA_Units.fev
- FactionA_Vehicles.fev
- FactionB_Buildings.fev
- FactionB_Units.fev
- FactionB_Vehicles.fev
- FactionD_Buildings.fev
- FactionD_Units.fev
- FactionD_Vehicles.fev
- FactionL_Units.fev
- FactionN.fev
- Faction_Common.fev
- GUI.fev
- GuitarStings.fev
- Music_Scripted.fev
- Objects.fev
- Reverbs.fev
- Scripted.fev
- Vehicles_Common.fev
- Voice.fev

---

## Audio Directory Structure

Win/Audio/
  Ambience/              - Environmental sounds
  BL1Patch1_USEnglish/   - DLC patch audio
  Bosses/                - Boss-specific SFX
  BrutalLegend_French/   - French VO
  BrutalLegend_German/   - German VO
  BrutalLegend_Italian/  - Italian VO
  BrutalLegend_Spanish/  - Spanish VO
  BrutalLegend_USEnglish/ - English VO
  Cutscenes/             - Cinematic audio
  FactionA_Buildings/    - Ironheade faction buildings
  FactionA_Units/        - Ironheade units
  FactionA_Vehicles/    - Ironheade vehicles
  FactionB_Buildings/    - Tainted Coil faction buildings
  FactionB_Units/       - Tainted Coil units
  FactionB_Vehicles/    - Tainted Coil vehicles
  FactionD_Buildings/   - Dlc1 faction buildings
  FactionD_Units/       - Dlc1 units
  FactionD_Vehicles/    - Dlc1 vehicles
  FactionL_Units/       - Dlc2 units
  FactionN/             - Death Magnetic faction
  Faction_Common/       - Shared faction audio
  GUI/                  - Interface sounds
  GuitarStings/         - Musical stingers
  Music_Scripted/       - Background music
  Objects/              - Interactive objects
  Reverbs/              - Reverb presets
  Scripted/             - Scripted audio events
  Vehicles_Common/     - Shared vehicle sounds
  Voice/                - Voice-over events

---

## Estimated Track Counts

Based on man_audio.txt analysis:

| Category | Tracks (est.) | Notes |
|----------|---------------|-------|
| Music | 60-80 | Scripted + licensed tracks |
| Cutscenes | 40-50 | Story cinematics |
| Voice-over | 4 languages | ~70k audio entries total |
| SFX | 500+ | Units, vehicles, buildings, objects |
| Ambience | 20-30 | Location-specific environments |

---

## Technical Notes

1. FMOD Integration: Game uses embedded FMOD (no external DLL)
2. Multi-platform: Audio reports exist for PC, PS3, and 360
3. Compression: Most audio uses MPEG (MP3) encoding
4. Streaming: Voice-over files are large streaming assets (~630 MB each)
5. Localization: 4 full voice-over languages + 1 DLC patch

---

## References

- DoubleFine Explorer: tools/reference/DoubleFine-Explorer/uDFExplorer_FSBManager.pas
- FMOD Documentation: https://fmod.com/docs
- Source Code Analysis: brutal-legend-re/docs/formats/AUDIO_ANALYSIS.md
