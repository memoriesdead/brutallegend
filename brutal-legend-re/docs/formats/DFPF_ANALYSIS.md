# DFPF Format Analysis

**Source:** DoubleFine Explorer by Bennyboy  
**Repository:** https://github.com/bgbennyboy/DoubleFine-Explorer  
**Analyzed Files:**
- `uDFExplorer_PAKManager.pas` - Main PAK/DFPF format handler
- `uDFExplorer_FSBManager.pas` - FSB audio format handler
- `uDFExplorer_Types.pas` - Type definitions

---

## 1. DFPF Format Overview

DFPF (Double-Fine Pack File) is the archive format used by Double Fine games (e.g., Brutal Legend, Costume Quest, Psychonauts). The format has multiple versions (V2, V5, V6) with varying file record structures.

### Key Characteristics
- **Endianness:** Big-endian
- **Bundle Files:** Uses a two-file system:
  - `.dfpf` (or similar): Main index/header file
  - `.~p`: Data file containing actual file contents
- **Magic Bytes:** `dfpf` (4 bytes at offset 0)

---

## 2. Header Structure (All Versions)

### Common Header Layout (Bytes 0-87)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0 | 4 | Magic | `"dfpf"` |
| 4 | 1 | Version | 2, 5, or 6 |
| 5 | 3 | Unknown | Reserved |
| 8 | 8 | FileExtensionOffset | QWord - pointer to file extension table |
| 16 | 8 | NameDirOffset | QWord - pointer to filename directory |
| 24 | 4 | FileExtensionCount | DWORD - number of file types |
| 28 | 4 | NameDirSize | DWORD (often misread in V2/V5) |
| 32 | 4 | NumFiles | DWORD - total file count |
| 36 | 4 | Marker1 | DWORD LE - marker `23A1CEABh` |
| 40 | 4 | BlankBytes1 | |
| 44 | 4 | BlankBytes2 | |
| 48 | 8 | JunkDataOffset | QWord - start of extra bytes in .~p |
| 56 | 8 | FileRecordsOffset | QWord - pointer to file records table |
| 64 | 8 | FooterOffset1 | QWord |
| 72 | 8 | FooterOffset2 | QWord |
| 80 | 4 | Unknown | DWORD |
| 84 | 4 | Marker2 | DWORD LE - marker `23A1CEABh` |

---

## 3. File Record Structure (16 bytes per file)

### V2 Format - Bit Shifting Details

Each 16-byte record contains bitfield-encoded values:

```
Bytes 0-3: UncompressedSize and NameOffset
  - UncompressedSize = ReadDWord >> 9
  - NameOffset = ReadDWord (at byte 3) >> 11

Bytes 4-7: Size and Offset  
  - Size = (ReadDWord << 1) >> 10  (size in .~p file)
  - Offset = (ReadQWord << 7) >> 34  (30 bits from byte 7, bit 7)

Bytes 8-11: NameOffset and FileTypeIndex
  - FileTypeIndex = (ReadDWord << 5) >> 25

Byte 12: CompressionType (lower 4 bits only)
  - CompressionType = ReadByte AND 15

Bytes 13-15: Unknown
```

**V2 Compression Types:**
- `2` = Not compressed
- `4` = Compressed

---

### V5 Format - Bit Shifting Details

**Structure (16 bytes per record):**

```pascal
// Bytes 0-3: UncompressedSize and NameOffset
FileObject.UnCompressedSize := (fBundle.ReadDWord shr 8);
fBundle.Seek(-1, sofromcurrent);
FileObject.NameOffset := (fBundle.ReadDWord) shr 11;

// Bytes 4-7: Offset
FileObject.Offset := fBundle.ReadDWord shr 3;
fBundle.Seek(-1, soFromCurrent);

// Bytes 8-11: Size and FileTypeIndex
FileObject.Size := (fBundle.ReadDWord shl 5) shr 9;
fBundle.Seek(-1, soFromCurrent);
FileObject.FileTypeIndex := (fBundle.ReadDWord shl 4) shr 24;
FileObject.FileTypeIndex := FileObject.FileTypeIndex shr 1;

// Byte 12: CompressionType
FileObject.CompressionType := fBundle.ReadByte and 15;
```

**V5 Compression Types:**
- `4` = Not compressed
- `8` = ZLIB compressed
- `12` = XMemCompress (Xbox) compressed

---

### V6 Format - Bit Shifting Details

**Structure (16 bytes per record):**

```pascal
// Bytes 0-3: UncompressedSize (5 bits) + NameOffset (last 3 bits of byte 4 + 2 bytes)
FileObject.UnCompressedSize := (fBundle.ReadDWord shr 5);
fBundle.Seek(-2, soFromCurrent);
FileObject.NameOffset := (fBundle.ReadDWord shl 13) shr 13;

// Bytes 4-5: Unknown 2 bytes

// Bytes 6-9: Offset (last bit of byte 11 + next 3 bytes)
FileObject.Offset := fBundle.ReadDWord shr 1;

// Bytes 10-13: Size (last 7 bits of byte 11 + next 3 bytes)
fBundle.Seek(-1, soFromCurrent);
FileObject.Size := (fBundle.ReadDWord shl 7) shr 7;

// Byte 14: FileTypeIndex (first 6 bits)
FileObject.FileTypeIndex := fBundle.ReadByte shr 2;

// Byte 15: CompressionType (last 2 bits)
FileObject.CompressionType := Byte(fBundle.ReadByte shl 6) shr 6;
```

**V6 Compression Types:**
- `1` = Not compressed
- `2` = Compressed

---

## 4. File Extension Table

Located at `FileExtensionOffset`, each entry (16 bytes) contains:
- `DWORD`: Length of extension string
- `char[Length]`: Extension name (e.g., `.tex`, `.dds`, `.str`)
- `12 bytes`: Unknown data

---

## 5. Compression Support

### V2
| Type | Meaning |
|------|---------|
| 2 | Uncompressed |
| 4 | Compressed |

### V5
| Type | Meaning |
|------|---------|
| 4 | Uncompressed |
| 8 | ZLIB |
| 12 | XMemCompress (Xbox) |

### V6
| Type | Meaning |
|------|---------|
| 1 | Uncompressed |
| 2 | Compressed |

---

## 6. Version Differences Summary

| Feature | V2 | V5 | V6 |
|---------|----|----|-----|
| Used In | Costume Quest | Brutal Legend? | Later games |
| UncompressedSize bits | >> 9 | >> 8 | >> 5 |
| NameOffset bits | >> 11 | >> 11 | (3+16 bits) |
| Offset bits | (30 bits) | >> 3 | >> 1 |
| Size bits | << 1 >> 10 | << 5 >> 9 | << 7 >> 7 |
| FileTypeIndex bits | << 5 >> 25 | << 4 >> 24 >> 1 | >> 2 |
| Compression 4 | Compressed | Uncompressed | - |
| Compression 8 | - | ZLIB | - |
| Compression 12 | - | XMemCompress | - |

---

## 7. FSB Audio Format (FSB5/FSB4)

### FSB Header Structure

**FSB5:**
| Offset | Size | Field |
|--------|------|-------|
| 0 | 4 | Magic `"FSB5"` |
| 4 | 4 | Version |
| 8 | 4 | NumSamples |
| 12 | 4 | SampleHeaderSize |
| 16 | 4 | NameSize |
| 20 | 4 | Datasize |
| 24 | 4 | Mode |
| 28 | 32 | Hash/zero bytes |

**FSB4:**
| Offset | Size | Field |
|--------|------|-------|
| 0 | 4 | Magic `"FSB4"` |
| 4 | 4 | NumSamples |
| 8 | 4 | SampleHeaderSize |
| 12 | 4 | Datasize |
| 16 | 4 | Version |
| 20 | 4 | HeadMode |
| 24 | 24 | 8x zero bytes + hash |

### FSB Encryption

FSB files may be encrypted with key: `44 46 6D 33 74 34 6C 46 54 57` ("DFm3t4lFTW")

Decryption algorithm:
1. Reverse bits in each byte
2. XOR with key (key position wraps)

```pascal
function ReverseBitsInByte(input: byte): byte;
var i: integer;
begin
  result := 0;
  for i := 0 to 7 do
  begin
    result := result shl 1;
    result := result or (input and 1);
    input := input shr 1;
  end;
end;
```

### FSB Codec Detection

| Codec | Format | Extension |
|-------|--------|-----------|
| FMOD_SOUND_FORMAT_PCM8 | 8-bit PCM | WAV |
| FMOD_SOUND_FORMAT_PCM16 | 16-bit PCM | WAV |
| FMOD_SOUND_FORMAT_MPEG | MPEG (MP3) | MP3 |

### FSB5 Sample Flags

Sample header can contain extra data blocks:
- `2` = Channels override
- `4` = Frequency override
- `6` = Unknown (6 bytes)
- `20` = XWMA data

---

## 8. Type Definitions

### TDFFile (PAK File Entry)
```pascal
TDFFile = class
  FileName: string;
  UncompressedSize: integer;
  NameOffset: integer;
  Offset: int64;           // 64-bit for DOTT with large offsets
  Size: integer;           // Size in .~p data file
  FileTypeIndex: integer;
  CompressionType: integer;
  Compressed: boolean;
  FileExtension: string;
  FileType: TFileType;
  PsychonautsDDS: TPsychonautsDDS;
end;
```

### TFSBFile (Audio File Entry)
```pascal
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
```

### TFileType Enum
```pascal
TFileType = (
  ft_GenericImage,
  ft_DDSImage,
  ft_HeaderlessDDSImage,
  ft_HeaderlessPsychoDDSImage,
  ft_HeaderlessDOTTDDSImage,
  ft_DOTTFontImage,
  ft_DOTTXMLCostumeWithImage,
  ft_FTHeaderlessCHNKImage,
  ft_Text,
  ft_CSVText,
  ft_DelimitedText,
  ft_Audio,
  ft_FSBFile,
  ft_IMCAudio,
  ft_LUA,
  ft_Other,
  ft_Unknown
);
```

---

## 9. Key Code Snippets

### Reading V5 File Record
```pascal
procedure TPAKManager.ReadV5Bundle;
var
  FileObject: TDFFile;
  i: integer;
const
  sizeOfFileRecord: integer = 16;
begin
  // ... header reading ...
  
  for I := 0 to numFiles - 1 do
  begin
    fBundle.Position := FileRecordsOffset + (sizeOfFileRecord * i);
    FileObject := TDFFile.Create;

    // UncompressedSize: upper 24 bits of first 4 bytes
    FileObject.UnCompressedSize := (fBundle.ReadDWord shr 8);
    
    // NameOffset: bits 11-31 of bytes 1-4
    fBundle.Seek(-1, sofromcurrent);
    FileObject.NameOffset := (fBundle.ReadDWord) shr 11;
    
    // Offset: bits 3-31 of bytes 5-8
    fBundle.Seek(1, sofromcurrent);
    FileObject.Offset := fBundle.ReadDWord shr 3;
    
    // Size: bits 9-31 of bytes 9-12
    fBundle.Seek(-1, soFromCurrent);
    FileObject.Size := (fBundle.ReadDWord shl 5) shr 9;
    
    // FileTypeIndex: bits 24-30, then normalize
    fBundle.Seek(-1, soFromCurrent);
    FileObject.FileTypeIndex := (fBundle.ReadDWord shl 4) shr 24;
    FileObject.FileTypeIndex := FileObject.FileTypeIndex shr 1;
    
    // CompressionType: lower 4 bits of byte 13
    fBundle.Seek(-3, soFromCurrent);
    FileObject.CompressionType := fBundle.ReadByte and 15;

    // Get filename from names directory
    fBundle.Position := NameDirOffset + FileObject.NameOffset;
    FileObject.FileName := PChar(fBundle.ReadString(255));

    BundleFiles.Add(FileObject);
  end;
end;
```

### Decompression Logic
```pascal
procedure TPAKManager.SaveFileToStream(FileNo: integer; DestStream: TStream);
begin
  // ...
  if TDFFile(BundleFiles.Items[FileNo]).Compressed then
  begin
    TempStream := tmemorystream.Create;
    try
      TempStream.CopyFrom(fDataBundle, TDFFile(BundleFiles.Items[FileNo]).Size);
      Tempstream.Position := 0;

      // Comp type 12 is Xbox XMemDecompress. Others are ZLib
      if TDFFile(BundleFiles.Items[FileNo]).CompressionType = 12 then
        DecompressXCompress(TempStream, DestStream, 
          TDFFile(BundleFiles.Items[FileNo]).Size, 
          TDFFile(BundleFiles.Items[FileNo]).UnCompressedSize)
      else
        DecompressZLib(TempStream, 
          TDFFile(BundleFiles.Items[FileNo]).UnCompressedSize, DestStream);
    finally
      TempStream.Free;
    end
  end
  else
    DestStream.CopyFrom(fDataBundle, TDFFile(BundleFiles.Items[FileNo]).Size);
end;
```

---

## 10. Notes

1. **Big-endian format:** All multi-byte reads are in big-endian byte order
2. **Bit-shifting complexity:** File records use unaligned bitfields requiring precise shift operations
3. **Dual file system:** Index in `.dfpf` (or similar), data in `.~p` file
4. **Version detection:** Version byte at offset 4 determines parsing method
5. **Compression comparison:** V5 uses compressed vs uncompressed size comparison to detect compression for types 4/8
6. **Xbox support:** V5 type 12 indicates Xbox XMemCompress compression
7. **Encrypted FSB:** Audio files may use custom encryption with bit-reversal and XOR key

---

*Generated from analysis of DoubleFine Explorer source code*
*https://github.com/bgbennyboy/DoubleFine-Explorer*
