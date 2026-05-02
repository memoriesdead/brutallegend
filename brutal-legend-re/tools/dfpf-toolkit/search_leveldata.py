#!/usr/bin/env python3
"""Search for map-level LevelData files - looking for pattern like dlc1_1.LevelData"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

bundles = [
    '00Startup.~h',
    'DLC1_Stuff.~h',
    'DLC2_Stuff.~h',
    'RgB_World.~h',
    'RgS_World.~h',
    'RgS_World2.~h',
]

print("Searching for files with '.LevelData' extension that might be map-level...")
print("="*60)

for bundle_name in bundles:
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        continue

    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    for record in extractor.file_records:
        fn = record.full_filename.replace('\\', '/')
        fn_lower = fn.lower()

        # Check if it's a LevelData file
        if '.leveldata' not in fn_lower:
            continue

        # Check if filename matches pattern like "dlc1_1.LevelData" or "mp_rivers.LevelData"
        # i.e., the file is named the same as its parent directory
        parts = fn.split('/')
        if len(parts) >= 2:
            filename = parts[-1].lower()
            dirname = parts[-2].lower()

            # Remove extension from filename
            fname_base = filename.replace('.leveldata', '')

            # Check if dirname equals filename (without extension)
            if dirname == fname_base:
                print(f"MATCH (dirname=filename): {fn}")
                print(f"  Record size: {record.uncompressed_size} bytes")
            elif fname_base in dirname or dirname in fname_base:
                # Partial match
                pass

# Also list ALL LevelData files with full paths
print("\n\n" + "="*60)
print("ALL LevelData files by bundle:")
print("="*60)

for bundle_name in bundles:
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        continue

    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    leveldata_files = [r for r in extractor.file_records if '.leveldata' in r.full_filename.lower().replace('\\', '/')]

    if leveldata_files:
        print(f"\n{bundle_name}: {len(leveldata_files)} LevelData files")

        # Show first 20
        for r in leveldata_files[:20]:
            fn = r.full_filename.replace('\\', '/')
            print(f"  {fn}")
        if len(leveldata_files) > 20:
            print(f"  ... and {len(leveldata_files)-20} more")