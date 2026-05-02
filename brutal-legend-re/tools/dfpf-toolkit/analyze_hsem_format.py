#!/usr/bin/env python3
"""Analyze the mesh LOD LevelData format (hsem magic)"""

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

# Find a model LOD file
target = None
for record in extractor.file_records:
    fn = record.full_filename.replace('\\', '/').lower()
    if '/model/' in fn and '_lod' in fn and '.leveldata' in fn:
        target = record
        print(f"Found: {record.full_filename}")
        break

if not target:
    print("No model LOD LevelData found")
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

print(f"File: {target.full_filename}")
print(f"Size: {len(data)} bytes")
print(f"Compression: {target.compression_name}")

# Check for hsem magic
magic = data[0:4]
print(f"\nMagic: {magic} ({magic.decode('ascii', errors='replace')})")

# Detailed hex dump
print("\n" + "="*70)
print("HEX DUMP (first 512 bytes)")
print("="*70)
for i in range(0, min(512, len(data)), 16):
    hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
    print(f'{i:04x}: {hex_str:<48} {ascii_str}')

print("\n" + "="*70)
print("HEADER ANALYSIS")
print("="*70)

# hsem header
print("\n[0x00] Magic 'hsem' + flags:")
print(f"  Bytes 0-3: {data[0:4]} (hsem)")
val = struct.unpack('<I', data[4:8])[0]
print(f"  Bytes 4-7 (uint32): {val}")

print("\n[0x08] Bytes 8-15 (2 floats - bounds?):")
f1, f2 = struct.unpack('<dd', data[8:24]) if len(data) >= 24 else (0, 0)
print(f"  LE double[0]: {f1}")
print(f"  LE double[1]: {f2}")

print("\n[0x18] Bytes 24-31 (2 floats):")
f1, f2 = struct.unpack('<dd', data[24:40]) if len(data) >= 40 else (0, 0)
print(f"  LE double[0]: {f1}")
print(f"  LE double[1]: {f2}")

# String at offset 0x50
print("\n[0x50] String area:")
if len(data) > 0x50:
    null_pos = data.find(b'\x00', 0x50)
    if null_pos > 0:
        str_data = data[0x50:null_pos]
        print(f"  String: {str_data.decode('ascii', errors='replace')}")
    # Also check for lrtm magic
    if len(data) > 0x54:
        print(f"  Bytes 0x50-0x57: {data[0x50:0x58]}")

print("\n" + "="*70)
print("LRTM MATERIAL HEADER SEARCH")
print("="*70)

# Look for 'lrtm' magic (material)
for i in range(0, min(len(data)-4, 256), 1):
    if data[i:i+4] == b'lrtm':
        print(f"Found 'lrtm' at offset 0x{i:04x}")
        # Show context
        for j in range(max(0, i-8), min(len(data), i+32), 16):
            hex_str = ' '.join(f'{b:02x}' for b in data[j:j+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[j:j+16])
            print(f'  {j:04x}: {hex_str:<48} {ascii_str}')

print("\n" + "="*70)
print("FILE FORMAT NOTES")
print("="*70)
print("""
Mesh LOD LevelData (hsem magic):
- 'hsem' = "mesh" backwards - indicates this is mesh LOD data
- Appears to use a different header format than tile LevelData
- Contains float bounding values (possibly min/max bounds)
- Contains material reference string at offset 0x50+
- 'lrtm' = "matl" backwards - material section marker
""")