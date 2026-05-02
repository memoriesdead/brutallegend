#!/usr/bin/env python3
"""Find map-level LevelData files"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path
import struct
import zlib

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

def list_bundle(bundle_name):
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        print(f"{bundle_name}: NOT FOUND")
        return []

    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    leveldata_files = [r for r in extractor.file_records if 'leveldata' in r.full_filename.lower()]
    return leveldata_files

# Check 00Startup
print("=== 00Startup ===")
files = list_bundle('00Startup.~h')
for r in files:
    print(f"  {r.full_filename} ({r.uncompressed_size} bytes)")

# Check all world bundles
for bundle in ['RgB_World.~h', 'RgS_World.~h', 'RgS_World2.~h']:
    print(f"\n=== {bundle} ===")
    leveldata_files = list_bundle(bundle)
    print(f"Total LevelData files: {len(leveldata_files)}")

    # Analyze path patterns
    map_files = []
    tile_files = []
    other_files = []

    for r in leveldata_files:
        fn = r.full_filename.lower()
        # Normalize path separators
        fn = fn.replace('\\', '/')

        if '/tile/' in fn:
            tile_files.append(r)
        elif '/worlds/' in fn or '/world/' in fn:
            parts = fn.split('/')
            if len(parts) >= 2:
                fname = parts[-1]
                dname = parts[-2]
                basename = fname.replace('.leveldata', '')
                if basename == dname:
                    map_files.append(r)
                else:
                    other_files.append(r)
            else:
                other_files.append(r)
        else:
            other_files.append(r)

    print(f"Map-level (dirname=filename): {len(map_files)}")
    for r in map_files[:5]:
        print(f"  {r.full_filename}")

    print(f"Tile-level: {len(tile_files)}")
    for r in tile_files[:3]:
        print(f"  {r.full_filename}")

    print(f"Other LevelData: {len(other_files)}")
    for r in other_files[:5]:
        print(f"  {r.full_filename}")

# Extract and analyze a map-level LevelData if found
if map_files:
    print(f"\n\n{'='*60}")
    print(f"EXTRACTING AND ANALYZING MAP-LEVEL LEVELDATA")
    print(f"{'='*60}")

    r = map_files[0]
    print(f"File: {r.full_filename}")

    # Get the extractor for this bundle
    header_path = packs_dir / 'RgB_World.~h'
    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    # Find the record again
    record = None
    for rec in extractor.file_records:
        if rec.full_filename == r.full_filename:
            record = rec
            break

    if record:
        # Read raw data
        with open(extractor.data_path, 'rb') as f:
            f.seek(record.offset)
            read_size = max(record.size, min(record.uncompressed_size * 2, 1024*1024)) if record.size > 0 else 65536
            data = f.read(read_size)

        if record.compressed:
            try:
                decompressor = zlib.decompressobj(zlib.MAX_WBITS)
                data = decompressor.decompress(data)
            except Exception as e:
                print(f"Decompression error: {e}")
                # Try raw deflate
                try:
                    decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                    data = decompressor.decompress(data)
                except:
                    pass

        print(f"Decompressed size: {len(data)} bytes")

        # Save raw data
        output_path = Path('map_leveldata_raw.bin')
        with open(output_path, 'wb') as f:
            f.write(data)
        print(f"Saved to: {output_path.absolute()}")

        # Hex dump
        print(f"\n{'='*60}")
        print("HEX DUMP (first 512 bytes)")
        print(f"{'='*60}")
        for i in range(0, min(512, len(data)), 16):
            hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f'{i:04x}: {hex_str:<48} {ascii_str}')

        # Analyze structure
        print(f"\n{'='*60}")
        print("STRUCTURE ANALYSIS")
        print(f"{'='*60}")

        if len(data) >= 4:
            magic = data[0:4]
            print(f"\n[0x0000] Magic: {magic} ({magic.decode('ascii', errors='replace')})")

        if len(data) >= 8:
            val = struct.unpack('<I', data[4:8])[0]
            print(f"[0x0004] uint32 LE: {val}")
            val = struct.unpack('>I', data[4:8])[0]
            print(f"[0x0004] uint32 BE: {val}")

        if len(data) >= 12:
            val = struct.unpack('<I', data[8:12])[0]
            print(f"[0x0008] uint32 LE: {val}")
            val = struct.unpack('>I', data[8:12])[0]
            print(f"[0x0008] uint32 BE: {val}")

        if len(data) >= 16:
            val = struct.unpack('<I', data[12:16])[0]
            print(f"[0x000c] uint32 LE: {val}")
            val = struct.unpack('>I', data[12:16])[0]
            print(f"[0x000c] uint32 BE: {val}")

        # Look for strings
        print(f"\n{'='*60}")
        print("STRINGS IN DATA")
        print(f"{'='*60}")

        strings = []
        current = bytearray()
        for i, b in enumerate(data):
            if 32 <= b < 127:
                current.append(b)
            else:
                if len(current) >= 4:
                    strings.append((i - len(current), bytes(current)))
                current = bytearray()

        print("\nReadable strings (4+ chars):")
        for offset, s in strings[:30]:
            print(f"  0x{offset:04x}: {s.decode('ascii', errors='replace')}")

        # Look for version 6
        print(f"\n{'='*60}")
        print("SEARCHING FOR VERSION 6")
        print(f"{'='*60}")
        for i in range(0, min(len(data)-4, 256), 4):
            val = struct.unpack('<I', data[i:i+4])[0]
            if val == 6:
                print(f"  LE uint32 at 0x{i:04x}: {val}")
            val = struct.unpack('>I', data[i:i+4])[0]
            if val == 6:
                print(f"  BE uint32 at 0x{i:04x}: {val}")

        # Look for hash 0x2527f4a6
        print(f"\n{'='*60}")
        print("SEARCHING FOR HASH 0x2527f4a6")
        print(f"{'='*60}")
        hash_val = 0x2527f4a6
        for i in range(0, min(len(data)-4, 512), 4):
            val = struct.unpack('<I', data[i:i+4])[0]
            if val == hash_val:
                print(f"  LE uint32 at 0x{i:04x}: 0x{val:08x}")
            val = struct.unpack('>I', data[i:i+4])[0]
            if val == hash_val:
                print(f"  BE uint32 at 0x{i:04x}: 0x{val:08x}")

elif other_files:
    print(f"\n\n{'='*60}")
    print(f"ANALYZING OTHER LEVELDATA FILE")
    print(f"{'='*60}")

    r = other_files[0]
    print(f"File: {r.full_filename}")

    header_path = packs_dir / 'RgB_World.~h'
    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    for rec in extractor.file_records:
        if rec.full_filename == r.full_filename:
            with open(extractor.data_path, 'rb') as f:
                f.seek(rec.offset)
                read_size = max(rec.size, min(rec.uncompressed_size * 2, 1024*1024)) if rec.size > 0 else 65536
                data = f.read(read_size)

            if rec.compressed:
                try:
                    decompressor = zlib.decompressobj(zlib.MAX_WBITS)
                    data = decompressor.decompress(data)
                except:
                    try:
                        decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                        data = decompressor.decompress(data)
                    except:
                        pass

            print(f"Size: {len(data)} bytes")

            # Save
            output_path = Path('other_leveldata_raw.bin')
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"Saved to: {output_path.absolute()}")

            # Hex dump
            print("\nHEX DUMP (first 512 bytes):")
            for i in range(0, min(512, len(data)), 16):
                hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
                print(f'{i:04x}: {hex_str:<48} {ascii_str}')
            break
else:
    print("No LevelData files found")