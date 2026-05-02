# DFPF Container Format Specification (V5)

**Status:** 🔴 In Progress  
**Game:** Brutal Legend  
**Engine:** Buddha  

---

## Overview

DFPF is the primary container format used by Double Fine's Buddha engine. Files come in pairs:
- `filename.~h` - Header/index file
- `filename.~p` - Data payload file

**Endianness:** Big-endian

---

## Header Structure (.~h file)

| Offset | Size | Type | Description |
|--------|------|------|-------------|
| 0x00 | 4 | char[4] | Magic: "dfpf" |
| 0x04 | 1 | uint8 | Version (V5 = 0x05 for Brutal Legend) |
| 0x05 | 8 | uint64 | FileExtensionOffset - pointer to file type table |
| 0x0D | 8 | uint64 | NameDirOffset - pointer to filename table |
| 0x15 | 4 | uint32 | FileExtensionCount |
| 0x19 | 4 | uint32 | NameDirSize |
| 0x1D | 4 | uint32 | NumFiles |
| 0x21 | 8 | uint64 | FileRecordsOffset |

---

## File Record (16 bytes each)

Each file in the archive has a 16-byte record:

```
[UncompressedSize (bitshifted)]  - bits 0-31
[NameOffset (bitshifted)]        - bits 32-63  
[FileOffset (bitshifted)]        - bits 64-95
[CompressedSize (bitshifted)]   - bits 96-127
[FileTypeIndex (bitshifted)]     - bits 128-143
[CompressionType]               - byte at offset 15
```

**Compression Types:**
| Type | Name |
|------|------|
| 1 | Uncompressed |
| 2 | ZLib compressed |
| 4 | Uncompressed (V5 variant) |
| 8 | ZLib (V5 variant) |
| 12 | XMemCompress (Xbox) |

---

## File Type Table

Located at FileExtensionOffset, contains file type strings (e.g., "lua", "dds", "fsb")

---

## Name Directory

Located at NameDirOffset, contains null-separated filename strings referenced by NameOffset in file records.

---

## Extraction Process

1. Read header to verify "dfpf" magic
2. Read version (must be 5 for Brutal Legend)
3. Parse file extension table
4. Parse name directory
5. For each file record:
   - Calculate actual offsets using bit-shifting
   - Read compressed/uncompressed data from .~p file
   - Decompress if necessary
   - Write to output with correct filename

---

## Known Issues

- Some audio FSB files don't decode correctly
- XMemCompress decompression requires Xbox-specific decompression

---

## References

- DoubleFine Explorer source: `uDFExplorer_PAKManager.pas`
- Original implementation: Bennyboy (bgbennyboy)
