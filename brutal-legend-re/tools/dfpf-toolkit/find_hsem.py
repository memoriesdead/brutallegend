#!/usr/bin/env python3
"""Find and analyze hsem LevelData file"""

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

# Find all LevelData files
files_found = []
for record in extractor.file_records:
    fn = record.full_filename.replace('\\', '/')
    if 'LevelData' in fn:
        files_found.append((fn, record))

print(f"Total LevelData files: {len(files_found)}")

# Search for hsem magic
for fn, r in files_found:
    with open(extractor.data_path, 'rb') as f:
        f.seek(r.offset)
        read_size = max(r.size, min(r.uncompressed_size * 2, 1024*1024)) if r.size > 0 else 65536
        data = f.read(read_size)

    if r.compressed:
        try:
            decompressor = zlib.decompressobj(zlib.MAX_WBITS)
            data = decompressor.decompress(data)
        except:
            try:
                decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                data = decompressor.decompress(data)
            except:
                pass

    magic = data[0:4]
    if magic == b'hsem':
        print(f"\n\nFound hsem file: {fn}")
        print(f"Size: {len(data)} bytes")
        print(f"\nMagic: {magic} ({magic.decode('ascii', errors='replace')})")

        # Hex dump
        print("\nHEX DUMP (first 256 bytes):")
        for i in range(0, min(256, len(data)), 16):
            hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f'{i:04x}: {hex_str:<48} {ascii_str}')

        # Find lrtm
        print("\n--- LRTM SEARCH ---")
        for i in range(0, min(len(data)-4, 512), 1):
            if data[i:i+4] == b'lrtm':
                print(f"Found 'lrtm' at offset 0x{i:04x}")
                for j in range(max(0, i-16), min(len(data), i+48), 16):
                    hex_str = ' '.join(f'{b:02x}' for b in data[j:j+16])
                    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[j:j+16])
                    print(f'  {j:04x}: {hex_str:<48} {ascii_str}')

        # Find BVXD
        print("\n--- BVXD SEARCH ---")
        for i in range(0, min(len(data)-4, 512), 1):
            if data[i:i+4] == b'BVXD':
                print(f"Found 'BVXD' at offset 0x{i:04x}")

        # Find tsbs
        print("\n--- TSBS SEARCH ---")
        for i in range(0, min(len(data)-4, 512), 1):
            if data[i:i+4] == b'tsbs':
                print(f"Found 'tsbs' at offset 0x{i:04x}")

        break
else:
    print("No hsem file found")