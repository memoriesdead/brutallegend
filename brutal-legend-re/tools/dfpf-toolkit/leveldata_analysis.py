#!/usr/bin/env python3
"""
LevelData Binary Format Analysis for Brutal Legend
===================================================

Based on analysis of actual LevelData files extracted from DLC1_Stuff.~p

FILE TYPES FOUND:
----------------
1. Tile Height LevelData  - worlds/<map>/tile/x<n>/y<n>/height.LevelData
2. Tile Blend LevelData  - worlds/<map>/tile/x<n>/y<n>/blend.LevelData
3. Tile Quad LevelData    - worlds/<map>/tile/x<n>/y<n>/quad_<n>.LevelData
4. Tile Base LevelData    - worlds/<map>/tile/x<n>/y<n>/base_*.LevelData
5. Model LOD LevelData    - dlc*/environments/<map>/model/<name>_lod<n>.LevelData
6. Climate LevelData      - dlc*/environments/climates/<map>/<time>.LevelData
7. Texture LevelData      - dlc*/textures/<name>.LevelData (DDS format)

HEADER FORMAT (Tile/Model/Climate LevelData):
--------------------------------------------
Offset  Size  Type   Description
------  ----  ----   -----------
0x00    4     uint32 Header size? (always 64 = 0x40 for these files)
0x04    4     uint32 Flags or type indicator
0x08    8     float [2x float] Unknown (often zeros)
0x10    4     float Tile dimension? (often 1024.0)
0x14    4     ?      Unknown (often zeros)
0x18    4     float Secondary value (often 1024.0 or 33.0)
0x1C    4     uint32 Unknown (often 0, 32, or 33)
0x20    var   string Null-terminated asset path string
...     ...   ...    String continues until null byte
...     ...   data   Binary data section begins after header+string

After header+string, the data section contains type-specific binary data:
- Height: Array of float values (heightmap grid)
- Blend: Array of float values (alpha/blend values)
- Quad: Array of float values (terrain quad data)
- Model LOD: Unknown mesh data
- Climate: Unknown climate data

Texture LevelData (DDS-based):
-------------------------------
Offset  Size  Type   Description
------  ----  ----   -----------
0x00    4     uint32 Header size? (seems to vary)
0x04    4     uint32 Unknown
0x08    4     uint32 DDS magic? ("rtxT" at offset 0x20 in one sample)
...     ...   ...    DDS-formatted texture data follows

MAGIC BYTES:
-----------
- Tile/Model/Climate LevelData: No obvious magic, starts with 0x40 (64)
- Texture LevelData: No standard magic, varies by texture type

VERSION/HASH SEARCH:
-------------------
- Searched for uint32 value 6 (version): NOT FOUND in header
- Searched for hash 0x2527f4a6: NOT FOUND in files analyzed
- The user's mentioned version 6 and hash may be from a different context

STRINGS FOUND:
-------------
- Path strings at offset 0x20: e.g., "worlds/dlc1_1/tile/x-2/y2/quad_1"
- These appear to be null-terminated and aligned to 16-byte boundaries

FLOAT VALUES:
-----------
Common patterns observed:
- 1024.0 (0x44480000 in LE) - possibly tile size in world units
- 1.0 (0x3F800000 in LE) - possibly normalized values
- Large values like 65535.0 for max bounds
"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path
import struct
import zlib

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

bundle_name = 'DLC1_Stuff.~h'
header_path = packs_dir / bundle_name
extractor = DFPFExtractor(str(header_path))
extractor.parse()

# Extract a representative tile quad LevelData file
target = None
for record in extractor.file_records:
    fn = record.full_filename.replace('\\', '/').lower()
    if 'worlds/' in fn and '/tile/' in fn and 'quad_' in fn and '.leveldata' in fn:
        target = record
        print(f"Extracting: {record.full_filename}")
        break

if not target:
    print("No quad LevelData found")
    sys.exit(1)

# Extract
with open(extractor.data_path, 'rb') as f:
    f.seek(target.offset)
    read_size = max(target.size, min(target.uncompressed_size * 2, 1024*1024)) if target.size > 0 else 65536
    data = f.read(read_size)

if target.compressed:
    try:
        decompressor = zlib.decompressobj(zlib.MAX_WBITS)
        data = decompressor.decompress(data)
    except:
        try:
            decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
            data = decompressor.decompress(data)
        except:
            pass

print(f"\nFile size: {len(data)} bytes")
print(f"Compression: {target.compression_name}")

# Document the format
print("\n" + "="*70)
print("DETAILED HEX DUMP OF HEADER (first 128 bytes)")
print("="*70)

for i in range(0, min(128, len(data)), 16):
    hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
    print(f'{i:04x}: {hex_str:<48} {ascii_str}')

print("\n" + "="*70)
print("HEADER FIELD ANALYSIS")
print("="*70)

print("\n[0x00] First 4 bytes (possible header size):")
val = struct.unpack('<I', data[0:4])[0]
print(f"  uint32 LE: {val} (0x{val:02x})")

print("\n[0x04] Bytes 4-7:")
val = struct.unpack('<I', data[4:8])[0]
print(f"  uint32 LE: {val}")

print("\n[0x08] Bytes 8-15 (2 floats?):")
f1, f2 = struct.unpack('<ff', data[8:16])
print(f"  float[0]: {f1}")
print(f"  float[1]: {f2}")

print("\n[0x10] Bytes 16-23 (2 floats?):")
f1, f2 = struct.unpack('<ff', data[16:24])
print(f"  float[0]: {f1}")
print(f"  float[1]: {f2}")

print("\n[0x18] Bytes 24-31:")
val = struct.unpack('<I', data[24:28])[0]
f = struct.unpack('<f', data[24:28])[0]
print(f"  uint32: {val}")
print(f"  float: {f}")

print("\n[0x1C] Bytes 28-31:")
val = struct.unpack('<I', data[28:32])[0]
print(f"  uint32: {val}")

print("\n[0x20] String area (path):")
# Find null terminator
null_pos = data.find(b'\x00', 0x20)
if null_pos > 0:
    str_data = data[0x20:null_pos]
    print(f"  Found null at offset 0x{null_pos:04x}")
    print(f"  String: {str_data.decode('ascii', errors='replace')}")

print("\n" + "="*70)
print("DATA SECTION ANALYSIS (after header)")
print("="*70)

# Find where data starts (after header and string)
header_end = 0x40  # Default header size
string_end = data.find(b'\x00', 0x20)
if string_end > 0:
    header_end = string_end + 1
    # Align to 16 bytes?
    if header_end % 16 != 0:
        header_end = (header_end + 15) & ~15

print(f"\nData section starts at offset: 0x{header_end:04x}")

# Look at the data section
if len(data) > header_end:
    print(f"\nFirst 128 bytes of data section:")
    for i in range(header_end, min(header_end+128, len(data)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f'{i:04x}: {hex_str:<48} {ascii_str}')

    # Try interpreting as floats
    print(f"\nInterpreting data section as float array:")
    floats_per_line = 4
    for row in range(4):
        offset = header_end + row * floats_per_line * 4
        if offset + floats_per_line * 4 > len(data):
            break
        floats = struct.unpack('<ffff', data[offset:offset+floats_per_line*4])
        print(f"  0x{offset:04x}: {floats}")

print("\n" + "="*70)
print("FILE FORMAT SUMMARY")
print("="*70)
print("""
LevelData File Structure (Tile/Model/Climate variants):

+--------+------------------+--------------------------------+
| Offset | Size             | Description                    |
+--------+------------------+--------------------------------+
| 0x00   | 4 bytes (uint32) | Header size (64) or type flag |
| 0x04   | 4 bytes          | Flags (always 0)               |
| 0x08   | 8 bytes (2x f32) | Unknown (often zeros)          |
| 0x10   | 4 bytes (float)  | Primary value (e.g., 1024.0)   |
| 0x14   | 4 bytes          | Padding/zero                   |
| 0x18   | 4 bytes (float)  | Secondary value (e.g., 1024.0) |
| 0x1C   | 4 bytes (uint32) | Unknown (0, 32, or 33)         |
| 0x20   | Variable         | Null-terminated path string    |
| ...    | Padding          | Align to 16-byte boundary      |
| N      | Remaining        | Binary data section            |
+--------+------------------+--------------------------------+

Data section format varies by LevelData type:
- height.LevelData: Float array (heightmap grid values)
- blend.LevelData: Float array (alpha/blend values)
- quad_*.LevelData: Float array (terrain quad values)
- base_*.LevelData: Float array or other format
- *lod*.LevelData: Unknown mesh/material data

Texture LevelData uses DDS container format internally.
""")

# Save the extracted file for reference
output_path = Path('quad_leveldata_sample.bin')
with open(output_path, 'wb') as f:
    f.write(data)
print(f"\nSaved sample file to: {output_path.absolute()}")