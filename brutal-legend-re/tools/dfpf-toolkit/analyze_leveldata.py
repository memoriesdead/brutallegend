#!/usr/bin/env python3
"""Analyze LevelData binary format in Brutal Legend"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path
import struct
import zlib

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

def extract_leveldata(bundle_name, filename_pattern=None):
    """Extract LevelData files from a bundle"""
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        return []

    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    results = []
    for record in extractor.file_records:
        fn_lower = record.full_filename.lower()
        if 'leveldata' not in fn_lower:
            continue
        if filename_pattern and filename_pattern.lower() not in fn_lower:
            continue

        # Extract raw data
        with open(extractor.data_path, 'rb') as f:
            f.seek(record.offset)
            read_size = max(record.size, min(record.uncompressed_size * 2, 1024*1024)) if record.size > 0 else 65536
            data = f.read(read_size)

        if record.compressed:
            try:
                decompressor = zlib.decompressobj(zlib.MAX_WBITS)
                data = decompressor.decompress(data)
            except:
                try:
                    decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                    data = decompressor.decompress(data)
                except:
                    pass

        results.append({
            'bundle': bundle_name,
            'filename': record.full_filename,
            'size': len(data),
            'uncompressed_size': record.uncompressed_size,
            'compression': record.compression_name,
            'data': data
        })
    return results

def hex_dump(data, length=256, offset=0):
    """Print hex dump"""
    print(f'\n=== HEX DUMP (bytes {offset:#x} to {offset+length:#x}) ===')
    for i in range(offset, min(offset+length, len(data)), 16):
        hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f'{i:04x}: {hex_str:<48} {ascii_str}')

def analyze_leveldata(data, filename):
    """Analyze LevelData binary structure"""
    print(f'\n{"="*60}')
    print(f'Analyzing: {filename}')
    print(f'Size: {len(data)} bytes')
    print(f'{"="*60}')

    if len(data) < 16:
        print("File too small to analyze")
        return

    # Show first 256 bytes
    hex_dump(data, 256)

    print(f'\n{"="*60}')
    print('STRUCTURE ANALYSIS')
    print(f'{"="*60}')

    offset = 0

    # Check for magic bytes at start
    print(f'\n[Offset 0x{offset:04x}] First 4 bytes (possible magic):')
    magic = data[offset:offset+4]
    print(f'  Raw: {magic}')
    print(f'  Ascii: {magic.decode("ascii", errors="replace")}')
    print(f'  As hex: {" ".join(f"{b:02x}" for b in magic)}')

    # Check if starts with common magic
    if magic == b'hsem':
        print('  -> Matches "hshm" (mesh header?)')
    elif magic == b'lrtm':
        print('  -> Matches "lrtm" (material?)')
    elif magic == b'GFX ':
        print('  -> Matches "GFX " (graphics)')

    offset += 4
    print(f'\n[Offset 0x{offset:04x}] Bytes 4-7 (possible count/size):')
    val = struct.unpack('<I', data[offset:offset+4])[0]
    print(f'  LE uint32: {val}')
    val = struct.unpack('>I', data[offset:offset+4])[0]
    print(f'  BE uint32: {val}')
    offset += 4

    print(f'\n[Offset 0x{offset:04x}] Bytes 8-15 (possible floats or offsets):')
    if len(data) >= 16:
        # Try interpreting as floats
        f1, f2 = struct.unpack('<dd', data[offset:offset+16]) if len(data) >= offset+16 else (0, 0)
        print(f'  LE double[2]: {f1}, {f2}')
        f1, f2 = struct.unpack('>dd', data[offset:offset+16]) if len(data) >= offset+16 else (0, 0)
        print(f'  BE double[2]: {f1}, {f2}')
    offset += 8

    print(f'\n[Offset 0x{offset:04x}] Bytes 16-23:')
    if len(data) >= 24:
        f1, f2 = struct.unpack('<dd', data[offset:offset+16]) if len(data) >= offset+16 else (0, 0)
        print(f'  LE double[2]: {f1}, {f2}')
    offset += 8

    print(f'\n[Offset 0x{offset:04x}] Bytes 24-31:')
    if len(data) >= 32:
        f1, f2 = struct.unpack('<dd', data[offset:offset+16]) if len(data) >= offset+16 else (0, 0)
        print(f'  LE double[2]: {f1}, {f2}')
    offset += 8

    # Look for string tables
    print(f'\n{"="*60}')
    print('STRING SEARCH')
    print(f'{"="*60}')

    strings_found = []
    current_string = bytearray()
    for i, b in enumerate(data):
        if 32 <= b < 127:
            current_string.append(b)
        else:
            if len(current_string) >= 4:
                strings_found.append((i - len(current_string), bytes(current_string)))
            current_string = bytearray()

    print('\nStrings found (min 4 chars):')
    for offset_pos, s in strings_found[:30]:  # Show first 30
        print(f'  0x{offset_pos:04x}: {s.decode("ascii", errors="replace")}')

    # Look for "Worlds" or map name patterns
    print('\nSearching for "worlds" or ".LevelData" strings...')
    data_str = data.decode('latin-1', errors='replace')
    for i in range(len(data_str) - 10):
        substr = data_str[i:i+20]
        if 'worlds' in substr.lower() or 'leveldata' in substr.lower():
            start = max(0, i-10)
            end = min(len(data_str), i+20)
            print(f'  0x{i:04x}: ...{data_str[start:end].replace(chr(0), ".")}...')

    # Look for version markers
    print(f'\n{"="*60}')
    print('VERSION/SIZE FIELD SEARCH')
    print(f'{"="*60}')

    # Look for uint32 values that might be version 6
    print('\nSearching for uint32 value 6 (version?)...')
    for i in range(0, min(len(data)-4, 512), 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val == 6:
            print(f'  LE uint32 at 0x{i:04x}: {val}')
        val = struct.unpack('>I', data[i:i+4])[0]
        if val == 6:
            print(f'  BE uint32 at 0x{i:04x}: {val}')

    # Look for hash 0x2527f4a6
    print('\nSearching for hash 0x2527f4a6...')
    hash_val = 0x2527f4a6
    for i in range(0, min(len(data)-4, 512), 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        if val == hash_val:
            print(f'  LE uint32 at 0x{i:04x}: 0x{val:08x}')
        val = struct.unpack('>I', data[i:i+4])[0]
        if val == hash_val:
            print(f'  BE uint32 at 0x{i:04x}: 0x{val:08x}')

    return data

def main():
    print('Brutal Legend LevelData Binary Analyzer')
    print('='*60)

    # First, let's find and extract a map-level LevelData file
    # The map discovery files should be at Worlds/<mapname>/<mapname>.LevelData

    # Check DLC1_Stuff which seems to have worlds data
    print('\n[1] Searching DLC1_Stuff for map-level LevelData...')
    results = extract_leveldata('DLC1_Stuff.~h')

    map_level_files = []
    for r in results:
        fn = r['filename'].lower().replace('\\', '/')
        parts = fn.split('/')
        if len(parts) >= 2:
            filename = parts[-1]
            dirname = parts[-2]
            basename = filename.replace('.leveldata', '')
            if basename == dirname and '/tile/' not in fn and '/model/' not in fn:
                map_level_files.append(r)
                print(f'  MAP LEVEL: {r["filename"]} ({r["size"]} bytes)')

    # Also check RgB_World
    print('\n[2] Searching RgB_World for LevelData...')
    results2 = extract_leveldata('RgB_World.~h')
    for r in results2[:5]:
        print(f'  {r["filename"]} ({r["size"]} bytes)')

    # If we found map-level files, analyze the first one
    if map_level_files:
        data = map_level_files[0]['data']
        analyze_leveldata(data, map_level_files[0]['filename'])
    elif results:
        # Analyze first available LevelData
        r = results[0]
        data = analyze_leveldata(r['data'], r['filename'])

        # Save for further analysis
        output_path = Path('leveldata_raw.bin')
        with open(output_path, 'wb') as f:
            f.write(data)
        print(f'\nSaved raw data to: {output_path.absolute()}')
    else:
        print('No LevelData files found!')

if __name__ == '__main__':
    main()