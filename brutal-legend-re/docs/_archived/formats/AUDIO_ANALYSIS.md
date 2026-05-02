# Brutal Legend Audio System Analysis

**Source:** DoubleFine Explorer by Bennyboy  
**Repository:** https://github.com/bgbennyboy/DoubleFine-Explorer  
**Analysis Date:** 2026-04-01  
**Status:** Documented

---

## Overview

Brutal Legend uses **FMOD** (Firelight Technologies) for its audio system. The game stores audio in **FSB (FMOD Sound Bank)** files, which contain compressed audio samples. These FSB files use a **custom encryption layer** with the key **DFm3t4lFTW**.

### Key Findings

- Audio Middleware: FMOD (Documented)
- Sound Bank Format: FSB5/FSB4 (Documented)
- Custom Encryption: Bit-reverse + XOR (Documented)
- Event System: FMOD Event (FEV) - In Recycle Bin
- Supported Codecs: MPEG, PCM8, PCM16 (Documented)

---

## FSB Format Details

### FSB5 Header Structure

- Offset 0-3: Magic (FSB5)
- Offset 4-7: Version
- Offset 8-11: NumSamples
- Offset 12-15: SampleHeaderSize
- Offset 16-19: NameSize
- Offset 20-23: Datasize
- Offset 24-27: Mode
- Offset 28-59: Hash/Zero

### FSB4 Header Structure

- Offset 0-3: Magic (FSB4)
- Offset 4-7: NumSamples
- Offset 8-11: SampleHeaderSize
- Offset 12-15: Datasize
- Offset 16-19: Version
- Offset 20-23: HeadMode
- Offset 24-47: Hash/Zero

---

## Encryption System

### Custom Encryption Key

Brutal Legend uses a **10-byte XOR encryption key**:

- Key Bytes (hex): 44 46 6D 33 74 34 6C 46 54 57
- Key String: DFm3t4lFTW

### Decryption Algorithm

The encryption uses a two-step process:

1. **Bit Reversal:** Each byte has its bits reversed (LSB becomes MSB)
2. **XOR:** Result is XORed with key byte (with wrapping)

Algorithm defined in uDFExplorer_FSBManager.pas lines 177-216.

Key offset calculation: j = KeyOffset mod 10 (wraps at 10)

---

## Audio Playback Architecture

### FMOD Integration

Brutal Legend uses FMOD for:
- Sound Effects (SFX): Stored in encrypted FSB banks
- Music: Likely in separate FSB banks
- Dynamic Audio: FMOD Event system for interactive audio

### FSB Parsing

The ParseFiles procedure (lines 281-297) shows how FSB files are parsed by checking magic bytes and dispatching to version-specific parsers (ParseFSB5 or ParseFSB4).

---

## FMOD Event Files (FEV)

### Known FEV Files

According to PROGRESS.md, multiple .fev FMOD Event configuration files were found in the Windows Recycle Bin. These files would contain:

- Event group definitions
- Event instance limits
- Parameter mappings
- Category assignments
- Bank references (pointing to FSB files)

### Missing Files

The FEV files are currently inaccessible in the Recycle Bin. Recovery needed for complete audio analysis.

---

## Codec Details

### Supported Codecs

- FMOD_SOUND_FORMAT_PCM8: 8-bit PCM (WAV)
- FMOD_SOUND_FORMAT_PCM16: 16-bit PCM (WAV)
- FMOD_SOUND_FORMAT_MPEG: MPEG Layer 2/3 (MP3)

### Codec Detection (FSB4)

Codec is determined by FSB4 Mode flags:
- FSOUND_DELTA () = MPEG
- FSOUND_8BITS () = PCM8
- Default = PCM16

---

## Type Definitions

### TFSBCodec Enum

Defined in uDFExplorer_Types.pas lines 105-122.

### TFSBFile Class

TFSBFile = class
  FileName: string;
  Size: integer;
  Offset: integer;
  FileType: TFileType;
  FileExtension: string;
  Codec: TFSBCodec;
  Channels: integer;
  Bits: integer;
  Freq: integer;
end;

---

## References

- Source: tools/reference/DoubleFine-Explorer/uDFExplorer_FSBManager.pas
- Types: tools/reference/DoubleFine-Explorer/uDFExplorer_Types.pas
- GitHub: https://github.com/bgbennyboy/DoubleFine-Explorer

---

*Generated from DoubleFine Explorer source analysis*
