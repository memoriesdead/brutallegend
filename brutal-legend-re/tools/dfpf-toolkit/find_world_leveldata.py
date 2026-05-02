#!/usr/bin/env python3
"""Find LevelData files in world bundles"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

# Check RgB_World and RgS_World for LevelData files
bundles = ['RgB_World.~h', 'RgS_World.~h']

for bundle_name in bundles:
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        print(f"\n{bundle_name}: NOT FOUND")
        continue

    print(f"\n{'='*60}")
    print(f"SEARCHING: {bundle_name}")
    print(f"{'='*60}")

    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    # Show all unique extensions
    print(f"\nExtensions in this bundle ({len(extractor.file_extensions)}):")
    for i, ext in enumerate(extractor.file_extensions):
        print(f"  {i}: {ext}")

    # Find LevelData files
    print("\n--- LevelData files ---")
    leveldata_files = []
    for r in extractor.file_records:
        fn = r.full_filename.replace(chr(92), '/').lower()
        if 'leveldata' in fn:
            leveldata_files.append((r, fn))

    print(f"Total LevelData files: {len(leveldata_files)}")

    # Group by directory
    by_dir = {}
    for r, fn in leveldata_files:
        parts = fn.split('/')
        if len(parts) >= 2:
            dir_name = '/'.join(parts[:-1])
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append((r, fn))

    print("\nLevelData files by directory:")
    for dir_name, files in sorted(by_dir.items())[:30]:
        print(f"  {dir_name}/")
        for r, fn in files[:5]:
            print(f"    {fn}")
        if len(files) > 5:
            print(f"    ... and {len(files)-5} more")

    # Find worlds/ directory files
    print("\n--- Files in worlds/ directory ---")
    worlds_files = []
    for r in extractor.file_records:
        fn = r.full_filename.replace(chr(92), '/').lower()
        if '/worlds/' in fn:
            worlds_files.append((r, fn))

    print(f"Total worlds/ files: {len(worlds_files)}")

    # Show first 30
    for r, fn in worlds_files[:30]:
        print(f"  {fn}")
        print(f"    Offset: {r.offset}, Size: {r.uncompressed_size}, Ext Index: {r.file_type_index}")