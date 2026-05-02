#!/usr/bin/env python3
"""Extract and analyze sk_1 MeshSet from Man_Trivial bundle"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path
import zlib

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

# Parse Man_Trivial bundle
header_path = packs_dir / 'Man_Trivial.~h'
extractor = DFPFExtractor(str(header_path))
extractor.parse()

# Extract worlds/sk_1/sk_1
print('=== Extracting worlds/sk_1/sk_1 ===')
record = extractor.find_file('worlds/sk_1/sk_1')
if record:
    print(f'Found: {record.full_filename}')
    print(f'  Offset: {record.offset}')
    print(f'  Size (compressed): {record.size}')
    print(f'  Uncompressed size: {record.uncompressed_size}')
    print(f'  Compression type: {record.compression_type} ({record.compression_name})')

    # The file appears to be uncompressed_v5 (type 4), which means the data is stored raw
    # Read exactly uncompressed_size bytes starting at offset
    with open(extractor.data_path, 'rb') as f:
        f.seek(record.offset)
        # For uncompressed_v5, read uncompressed_size bytes
        data = f.read(record.uncompressed_size)

    print(f'  Read {len(data)} bytes')

    # For uncompressed_v5, there might be a 4-byte header with size
    # Let's check if first 4 bytes are size
    if len(data) >= 4:
        possible_size = int.from_bytes(data[0:4], 'little')
        print(f'  First 4 bytes as LE: {possible_size}')
        possible_size_be = int.from_bytes(data[0:4], 'big')
        print(f'  First 4 bytes as BE: {possible_size_be}')

    # Try to decode as text starting from byte 4 (skip potential size header)
    text_data = data[4:] if len(data) > 4 else data

    # Actually, let's just look at the raw bytes and find where text starts
    print(f'\n=== RAW BYTES ANALYSIS ===')
    print(f'Total bytes: {len(data)}')

    # Find where printable ASCII text starts
    text_start = 0
    for i, b in enumerate(data):
        if 32 <= b < 127 or b in (9, 10, 13):  # printable + tab, LF, CR
            continue
        else:
            text_start = i
            break

    print(f'Non-printable until offset: {text_start}')

    # Find "MeshSet" in the data
    meshset_pos = data.find(b'MeshSet')
    print(f'"MeshSet" found at offset: {meshset_pos}')

    if meshset_pos >= 0:
        # Extract from MeshSet to end
        text = data[meshset_pos:].decode('utf-8', errors='replace')
        print(f'\n=== FULL MeshSet CONTENT ===')
        print(text)
        print(f'\n=== END OF CONTENT ===')
        print(f'Total MeshSet text length: {len(text)}')

    # Also save full raw
    output_path = Path('sk_1_meshset_full.bin')
    with open(output_path, 'wb') as f:
        f.write(data)
    print(f'\nSaved raw to: {output_path.absolute()}')

else:
    print('File not found!')