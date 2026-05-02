#!/usr/bin/env python3
"""Final analysis: Compare hsem vs other LevelData formats"""

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

# Find the columnarches file that had hsem magic
target = None
for record in extractor.file_records:
    fn = record.full_filename.replace('\\', '/')
    if 'columnarches_sk_lod3' in fn and '.LevelData' in fn:
        target = record
        print(f"Found: {fn}")
        break

if not target:
    print("File not found")
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

print(f"\nFile: {target.full_filename}")
print(f"Size: {len(data)} bytes")

# Check magic
magic = data[0:4]
print(f"\nMagic at 0x00: {magic.hex()} ({magic.decode('ascii', errors='replace')})")

# Hex dump
print("\n" + "="*70)
print("HEX DUMP (first 256 bytes)")
print("="*70)
for i in range(0, min(256, len(data)), 16):
    hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
    print(f'{i:04x}: {hex_str:<48} {ascii_str}')

# Find lrtm
print("\n" + "="*70)
print("LRTM SEARCH")
print("="*70)
for i in range(0, min(len(data)-4, 512), 1):
    if data[i:i+4] == b'lrtm':
        print(f"Found 'lrtm' at offset 0x{i:04x}")
        for j in range(max(0, i-16), min(len(data), i+48), 16):
            hex_str = ' '.join(f'{b:02x}' for b in data[j:j+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[j:j+16])
            print(f'  {j:04x}: {hex_str:<48} {ascii_str}')

# Find tsbs
print("\n" + "="*70)
print("TSBS SEARCH (possible material type)")
print("="*70)
for i in range(0, min(len(data)-4, 512), 1):
    if data[i:i+4] == b'tsbs':
        print(f"Found 'tsbs' at offset 0x{i:04x}")
        for j in range(max(0, i-16), min(len(data), i+48), 16):
            hex_str = ' '.join(f'{b:02x}' for b in data[j:j+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[j:j+16])
            print(f'  {j:04x}: {hex_str:<48} {ascii_str}')

# Find BVXD
print("\n" + "="*70)
print("BVXD SEARCH (possible format ID)")
print("="*70)
for i in range(0, min(len(data)-4, 512), 1):
    if data[i:i+4] == b'BVXD':
        print(f"Found 'BVXD' at offset 0x{i:04x}")

print("\n" + "="*70)
print("SUMMARY: LevelData Binary Format Variants")
print("="*70)
print("""
Type 1: Mesh LOD LevelData (columnarches_sk_lod3)
  - Magic: 'hsem' at offset 0 (mesh = "hsem" backwards)
  - Contains bounding box floats at offset 0x08
  - Material string at offset 0x54: 'lrtm' = "matl" backwards
  - 'tsbs' appears to be material type marker

Type 2: Tile/Quad LevelData
  - Magic: 0x40 (64) at offset 0
  - Path string at offset 0x20
  - 'BVXD' at offset 0x54 (format identifier)
  - 'BIXD' also appears at offset 0x54 in some files

Type 3: DDS-based LevelData (textures)
  - No obvious magic, starts with zeros
  - Contains DDS header at offset ~0x20
""")