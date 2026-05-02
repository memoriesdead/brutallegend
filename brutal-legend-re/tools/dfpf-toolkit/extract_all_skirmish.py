#!/usr/bin/env python3
"""Extract and display MeshSet content from all skirmish maps (sk_1 through sk_9)"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

# Parse Man_Trivial bundle
header_path = packs_dir / 'Man_Trivial.~h'
extractor = DFPFExtractor(str(header_path))
extractor.parse()

print("=" * 80)
print("EXTRACTING ALL SKIRMISH MAP MESH SETS")
print("=" * 80)

skirmish_files = ['sk_1', 'sk_2', 'sk_3', 'sk_4', 'sk_5', 'sk_6', 'sk_7', 'sk_8', 'sk_9']

for sk_name in skirmish_files:
    # Try to find the file with various extensions
    patterns = [
        f'worlds/{sk_name}/{sk_name}',
    ]

    record = None
    for r in extractor.file_records:
        fn = r.full_filename.replace(chr(92), '/').lower()
        if f"worlds/{sk_name}/{sk_name}" in fn:
            record = r
            break

    if record:
        # Read the data
        with open(extractor.data_path, 'rb') as f:
            f.seek(record.offset)
            data = f.read(record.uncompressed_size)

        # Skip first 4 bytes (seems to be size header)
        text_data = data[4:] if len(data) > 4 else data

        # Find MeshSet start
        meshset_pos = text_data.find(b'MeshSet')
        if meshset_pos >= 0:
            text = text_data[meshset_pos:].decode('utf-8', errors='replace')
        else:
            text = text_data.decode('utf-8', errors='replace')

        print(f"\n{'='*80}")
        print(f"=== {sk_name.upper()} MeshSet CONTENT ===")
        print(f"{'='*80}")
        print(f"File: {record.full_filename}")
        print(f"Uncompressed size: {record.uncompressed_size}")
        print(f"File type index: {record.file_type_index}")
        print()
        print(text)
        print()
    else:
        print(f"\n{'='*80}")
        print(f"=== {sk_name.upper()} - NOT FOUND ===")
        print(f"{'='*80}")