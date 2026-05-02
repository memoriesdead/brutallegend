#!/usr/bin/env python3
"""Find actual path patterns in bundles"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path
from collections import Counter

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

bundles = [
    'DLC1_Stuff.~h',
    'RgB_World.~h',
    'RgS_World.~h',
]

# Collect all path prefixes
prefix_counts = Counter()

for bundle_name in bundles:
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        continue

    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    for record in extractor.file_records:
        fn = record.full_filename.replace('\\', '/')
        parts = fn.split('/')
        # Count path prefixes
        for i in range(1, min(len(parts), 5)):
            prefix = '/'.join(parts[:i])
            prefix_counts[prefix] += 1

print("Most common path prefixes:")
for prefix, count in prefix_counts.most_common(30):
    print(f"  {count:5d}  {prefix}")

# Look for LevelData files specifically
print("\n\n=== All LevelData files ===")
for bundle_name in bundles:
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        continue

    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    for record in extractor.file_records:
        if 'leveldata' in record.full_filename.lower():
            fn = record.full_filename.replace('\\', '/')
            print(f"  {bundle_name}: {fn}")