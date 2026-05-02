#!/usr/bin/env python3
"""Search for SoloSetup and GameMode files that define MP map list"""

import sys
sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor
from pathlib import Path
import zlib

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')

# Check all bundles for SoloSetup and GameMode files
bundles = ['00Startup.~h', 'RgB_World.~h', 'RgS_World.~h', 'RgS_World2.~h', 'Man_Trivial.~h']

for bundle_name in bundles:
    header_path = packs_dir / bundle_name
    if not header_path.exists():
        print(f"\n{'='*60}")
        print(f"{bundle_name}: NOT FOUND")
        print(f"{'='*60}")
        continue

    print(f"\n{'='*60}")
    print(f"SEARCHING: {bundle_name}")
    print(f"{'='*60}")

    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    # Find SoloSetup files
    print("\n--- SoloSetup files ---")
    for r in extractor.file_records:
        fn = r.full_filename.replace(chr(92), '/').lower()
        if 'solosetup' in fn:
            print(f"  {r.full_filename}")
            print(f"    Offset: {r.offset}, Size: {r.uncompressed_size}")

            # Try to extract and show content
            with open(extractor.data_path, 'rb') as f:
                f.seek(r.offset)
                data = f.read(r.uncompressed_size)

            if len(data) >= 4:
                text_start = data.find(b'SoloSetup')
                if text_start < 0:
                    text_start = 0
                try:
                    text = data[text_start:].decode('utf-8', errors='replace')
                    print(f"    Content (first 500 chars):")
                    print(f"    {text[:500]}")
                except:
                    pass

    # Find GameMode files
    print("\n--- GameMode files ---")
    for r in extractor.file_records:
        fn = r.full_filename.replace(chr(92), '/').lower()
        if 'gamemode' in fn:
            print(f"  {r.full_filename}")
            print(f"    Offset: {r.offset}, Size: {r.uncompressed_size}")

            # Try to extract and show content
            with open(extractor.data_path, 'rb') as f:
                f.seek(r.offset)
                data = f.read(r.uncompressed_size)

            if len(data) >= 4:
                text_start = data.find(b'GameMode')
                if text_start < 0:
                    text_start = 0
                try:
                    text = data[text_start:].decode('utf-8', errors='replace')
                    print(f"    Content (first 500 chars):")
                    print(f"    {text[:500]}")
                except:
                    pass

    # Find files with 'skirmish' in name
    print("\n--- Files with 'skirmish' in name ---")
    for r in extractor.file_records:
        fn = r.full_filename.replace(chr(92), '/').lower()
        if 'skirmish' in fn:
            print(f"  {r.full_filename}")
            print(f"    Offset: {r.offset}, Size: {r.uncompressed_size}")

    # Find LevelData files that might be map definitions
    print("\n--- LevelData files (map-level, not tile) ---")
    for r in extractor.file_records:
        fn = r.full_filename.replace(chr(92), '/').lower()
        if 'leveldata' in fn:
            # Check if it's a map-level file (not tile)
            parts = fn.split('/')
            if '/tile/' not in fn and '/worlds/' in fn:
                print(f"  {r.full_filename}")
                print(f"    Offset: {r.offset}, Size: {r.uncompressed_size}")