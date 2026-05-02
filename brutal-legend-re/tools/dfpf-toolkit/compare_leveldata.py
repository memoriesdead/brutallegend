#!/usr/bin/env python3
"""Extract and analyze multiple types of LevelData files to understand the format"""

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

def extract_file(extractor, record):
    with open(extractor.data_path, 'rb') as f:
        f.seek(record.offset)
        read_size = max(record.size, min(record.uncompressed_size * 2, 1024*1024)) if record.size > 0 else 65536
        data = f.read(read_size)

    if record.compressed:
        try:
            decompressor = zlib.decompressobj(zlib.MAX_WBITS)
            data = decompressor.decompress(data)
        except Exception as e:
            try:
                decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                data = decompressor.decompress(data)
            except:
                pass
    return data

# Find different types of LevelData files
tile_height = None
tile_blend = None
model_lod = None
texture_leveldata = None
climate_leveldata = None

for record in extractor.file_records:
    fn = record.full_filename.replace('\\', '/').lower()
    if 'worlds/' in fn and '/tile/' in fn:
        if 'height.leveldata' in fn and not tile_height:
            tile_height = record
        elif 'blend.leveldata' in fn and not tile_blend:
            tile_blend = record
    elif '/model/' in fn and '_lod' in fn and '.leveldata' in fn and not model_lod:
        model_lod = record
    elif 'textures/' in fn and '.leveldata' in fn and not texture_leveldata:
        texture_leveldata = record
    elif 'climate' in fn and '.leveldata' in fn and not climate_leveldata:
        climate_leveldata = record

files_to_analyze = [
    ("Tile Height (worlds/dlc1_1b/tile/x-4/y-1/height.LevelData)", tile_height),
    ("Tile Blend", tile_blend),
    ("Model LOD", model_lod),
    ("Texture LevelData", texture_leveldata),
    ("Climate LevelData", climate_leveldata),
]

def hex_dump(data, offset=0, length=256):
    for i in range(offset, min(offset+length, len(data)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f'{i:04x}: {hex_str:<48} {ascii_str}')

def analyze_leveldata(data, filename):
    print(f"\n{'='*70}")
    print(f"FILE: {filename}")
    print(f"SIZE: {len(data)} bytes")
    print(f"{'='*70}")

    # Check for common magic bytes
    magic = data[0:4] if len(data) >= 4 else b''
    print(f"\nMagic: {magic.hex()} ({magic.decode('ascii', errors='replace') if magic else ''})")

    # First 4 bytes as different types
    if len(data) >= 4:
        val_u32_le = struct.unpack('<I', data[0:4])[0]
        val_u32_be = struct.unpack('>I', data[0:4])[0]
        val_f32_le = struct.unpack('<f', data[0:4])[0]
        val_f32_be = struct.unpack('>f', data[0:4])[0]
        print(f"Bytes 0-3: uint32 LE={val_u32_le}, BE={val_u32_be}")
        print(f"           float LE={val_f32_le}, BE={val_f32_be}")

    # Strings at offset 0x20 (32) - common for many game formats
    if len(data) >= 36:
        print(f"\nOffset 0x20-0x40:")
        chunk = data[0x20:0x40]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  Hex: {hex_str}")
        print(f"  ASCII: {ascii_str}")

    # Look for strings
    print(f"\nStrings (min 8 chars):")
    strings_found = []
    current = bytearray()
    for i, b in enumerate(data[:min(len(data), 4096)]):
        if 32 <= b < 127:
            current.append(b)
        else:
            if len(current) >= 8:
                strings_found.append((i - len(current), bytes(current)))
            current = bytearray()
    for offset, s in strings_found[:10]:
        print(f"  0x{offset:04x}: {s.decode('ascii', errors='replace')}")

    # Hex dump of first 256 bytes
    print(f"\n--- HEX DUMP (first 256 bytes) ---")
    hex_dump(data, 0, 256)

    return data

for label, record in files_to_analyze:
    if record:
        data = extract_file(extractor, record)
        analyze_leveldata(data, f"{label}: {record.full_filename}")
        print()
    else:
        print(f"\n{'='*70}")
        print(f"FILE: {label}")
        print(f"STATUS: Not found")
        print(f"{'='*70}")