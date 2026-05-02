#!/usr/bin/env python3
"""Extract and analyze a tile-level LevelData file in detail"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path
import struct
import zlib

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

# Extract a tile-level LevelData file
bundle_name = 'DLC1_Stuff.~h'
header_path = packs_dir / bundle_name
extractor = DFPFExtractor(str(header_path))
extractor.parse()

# Find a tile-level height.LevelData file
target = None
for record in extractor.file_records:
    fn = record.full_filename.replace('\\', '/').lower()
    if 'worlds/' in fn and '/tile/' in fn and 'height.leveldata' in fn:
        target = record
        print(f"Selected: {record.full_filename}")
        break

if not target:
    print("No suitable file found")
    sys.exit(1)

# Extract raw data
with open(extractor.data_path, 'rb') as f:
    f.seek(target.offset)
    read_size = max(target.size, min(target.uncompressed_size * 2, 1024*1024)) if target.size > 0 else 65536
    data = f.read(read_size)

if target.compressed:
    try:
        decompressor = zlib.decompressobj(zlib.MAX_WBITS)
        data = decompressor.decompress(data)
    except Exception as e:
        print(f"Decompression error (zlib): {e}")
        try:
            decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
            data = decompressor.decompress(data)
        except Exception as e2:
            print(f"Decompression error (raw deflate): {e2}")
            # Try using the data as-is
            pass

print(f"File: {target.full_filename}")
print(f"Compressed size: {target.size}")
print(f"Uncompressed size: {target.uncompressed_size}")
print(f"Actual data size: {len(data)} bytes")
print(f"Compression type: {target.compression_name}")

# Save raw data
output_path = Path('tile_leveldata.bin')
with open(output_path, 'wb') as f:
    f.write(data)
print(f"\nSaved to: {output_path.absolute()}")

# Detailed hex dump
print("\n" + "="*70)
print("HEX DUMP (first 512 bytes)")
print("="*70)
for i in range(0, min(512, len(data)), 16):
    hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
    print(f'{i:04x}: {hex_str:<48} {ascii_str}')

# If there's more data, show continuation
if len(data) > 512:
    print(f"\n... (total {len(data)} bytes)")
    print("\n" + "="*70)
    print("HEX DUMP (bytes 512 to 1024)")
    print("="*70)
    for i in range(512, min(1024, len(data)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f'{i:04x}: {hex_str:<48} {ascii_str}')

# Structure analysis
print("\n" + "="*70)
print("STRUCTURE ANALYSIS")
print("="*70)

def analyze_at_offset(data, offset, length=16, label=""):
    if offset + length > len(data):
        print(f"[0x{offset:04x}] {label}: Not enough data (need {length}, have {len(data)-offset})")
        return

    print(f"\n[0x{offset:04x}] {label} ({length} bytes):")
    chunk = data[offset:offset+length]

    # Try different interpretations
    print(f"  Raw: {' '.join(f'{b:02x}' for b in chunk)}")

    if length >= 2:
        print(f"  LE uint16: {struct.unpack('<H', chunk[0:2])[0]}")
        print(f"  BE uint16: {struct.unpack('>H', chunk[0:2])[0]}")
    if length >= 4:
        print(f"  LE uint32: {struct.unpack('<I', chunk[0:4])[0]}")
        print(f"  BE uint32: {struct.unpack('>I', chunk[0:4])[0]}")
    if length >= 8:
        print(f"  LE double: {struct.unpack('<d', chunk[0:8])[0]}")
        print(f"  BE double: {struct.unpack('>d', chunk[0:8])[0]}")
    if length >= 4:
        print(f"  LE int32: {struct.unpack('<i', chunk[0:4])[0]}")
        print(f"  BE int32: {struct.unpack('>i', chunk[0:4])[0]}")
        # Float interpretation
        import math
        le_float = struct.unpack('<f', chunk[0:4])[0]
        be_float = struct.unpack('>f', chunk[0:4])[0]
        print(f"  LE float: {le_float} ({'inf' if math.isinf(le_float) else 'ok' if le_float == le_float else 'nan'})")
        print(f"  BE float: {be_float} ({'inf' if math.isinf(be_float) else 'ok' if be_float == be_float else 'nan'})")

# Analyze header structure
print("\n--- HEADER ANALYSIS ---")
analyze_at_offset(data, 0, 4, "Magic (4 bytes)")

# Check for 'hsem' (mesh) or 'lrtm' (material) or other magic
magic = data[0:4]
print(f"  As ASCII: {magic.decode('ascii', errors='replace')}")

analyze_at_offset(data, 4, 4, "Unknown/Flags")
analyze_at_offset(data, 8, 8, "Floats? (8 bytes)")
analyze_at_offset(data, 16, 8, "Floats? (8 bytes)")
analyze_at_offset(data, 24, 8, "Floats? (8 bytes)")
analyze_at_offset(data, 32, 8, "Floats? (8 bytes)")

# Look at bytes 0x40-0x60 which might contain strings
print("\n--- STRING TABLE SEARCH ---")
string_regions = []
for i in range(0, min(len(data)-64, 256), 1):
    # Look for printable ASCII strings
    if 32 <= data[i] < 127:
        # Start of potential string
        start = i
        while i < len(data) and 32 <= data[i] < 127:
            i += 1
        end = i
        if end - start >= 4:  # Min 4 char string
            string_regions.append((start, data[start:end]))

print(f"Found {len(string_regions)} string regions in first 256 bytes:")
for offset, s in string_regions[:20]:
    print(f"  0x{offset:04x}: {s.decode('ascii', errors='replace')}")

# Look for version marker
print("\n--- VERSION SEARCH ---")
for i in range(0, min(len(data)-4, 128), 4):
    val = struct.unpack('<I', data[i:i+4])[0]
    if val == 6:
        print(f"  LE uint32 at 0x{i:04x}: {val} (possible version)")
    val = struct.unpack('>I', data[i:i+4])[0]
    if val == 6:
        print(f"  BE uint32 at 0x{i:04x}: {val} (possible version)")

# Look for hash
hash_val = 0x2527f4a6
print(f"\n--- HASH SEARCH (0x{hash_val:08x}) ---")
for i in range(0, min(len(data)-4, 256), 4):
    val = struct.unpack('<I', data[i:i+4])[0]
    if val == hash_val:
        print(f"  LE at 0x{i:04x}: 0x{val:08x}")
    val = struct.unpack('>I', data[i:i+4])[0]
    if val == hash_val:
        print(f"  BE at 0x{i:04x}: 0x{val:08x}")

# Analyze full file size distribution
print("\n--- FILE SIZE STATS ---")
print(f"Total file size: {len(data)} bytes")
if len(data) >= 4:
    print(f"First 4 bytes as uint32 LE: {struct.unpack('<I', data[0:4])[0]}")
if len(data) >= 8:
    print(f"Bytes 4-7 as uint32 LE: {struct.unpack('<I', data[4:8])[0]}")

# Look at the end of the file too
if len(data) > 64:
    print("\n--- TAIL HEX DUMP (last 64 bytes) ---")
    for i in range(max(0, len(data)-64), len(data), 16):
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f'{i:04x}: {hex_str:<48} {ascii_str}')