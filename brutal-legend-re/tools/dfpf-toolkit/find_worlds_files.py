#!/usr/bin/env python3
"""Find files in Worlds/ directories across all bundles"""

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

all_worlds_files = {}

for bundle_name in bundles:
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        continue

    print(f"\n=== {bundle_name} ===")
    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    worlds_files = []
    for record in extractor.file_records:
        fn = record.full_filename.lower()
        fn_norm = fn.replace('\\', '/')
        if '/worlds/' in fn_norm or '/world/' in fn_norm:
            worlds_files.append(record)
            if fn not in all_worlds_files:
                all_worlds_files[fn] = (bundle_name, record)

    print(f"Found {len(worlds_files)} files in Worlds/ directories")

    # Show unique path patterns
    paths = set()
    for r in worlds_files:
        fn = r.full_filename.replace('\\', '/')
        # Extract the path up to the map name
        parts = fn.split('/')
        if len(parts) >= 3:
            # worlds/<mapname>/<rest>
            paths.add('/'.join(parts[:3]))
        elif len(parts) >= 2:
            paths.add('/'.join(parts[:2]))

    print("Unique path patterns:")
    for p in sorted(paths)[:20]:
        print(f"  {p}")

    if len(paths) > 20:
        print(f"  ... and {len(paths) - 20} more")

    # Show sample files
    print("Sample files:")
    for r in worlds_files[:10]:
        print(f"  {r.full_filename}")

print(f"\n\n{'='*60}")
print("SUMMARY: All unique Worlds/ files across bundles")
print(f"{'='*60}")

# Group by map name
maps = {}
for fn in sorted(all_worlds_files.keys()):
    parts = fn.replace('\\', '/').split('/')
    if len(parts) >= 3 and parts[1] == 'worlds':
        mapname = parts[2]
        if mapname not in maps:
            maps[mapname] = []
        maps[mapname].append(fn)

print(f"\nFound {len(maps)} unique maps:")
for mapname in sorted(maps.keys()):
    print(f"  {mapname}: {len(maps[mapname])} files")
    for f in maps[mapname][:5]:
        print(f"    {f}")
    if len(maps[mapname]) > 5:
        print(f"    ... and {len(maps[mapname]) - 5} more")