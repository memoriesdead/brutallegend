#!/usr/bin/env python3
"""Find and extract all skirmish map files (sk_1 through sk_9) from Man_Trivial"""

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

print(f"Total files in Man_Trivial: {len(extractor.file_records)}")
print(f"File extensions: {extractor.file_extensions[:20]}")

# Find all skirmish map files (worlds/sk_*/sk_*)
print("\n=== ALL SKIRMISH MAP MESH SET FILES (worlds/sk_*/sk_*) ===")
sk_maps = {}
for i in range(1, 10):
    sk_name = f"sk_{i}"
    for r in extractor.file_records:
        fn = r.full_filename.replace(chr(92), '/').lower()
        # Looking for worlds/sk_X/sk_X.MusicNameTable or similar
        if f"worlds/{sk_name}/{sk_name}" in fn:
            sk_maps[sk_name] = r
            print(f"{sk_name}: {r.full_filename}")
            print(f"  Offset: {r.offset}, Uncompressed: {r.uncompressed_size}")
            print(f"  File type index: {r.file_type_index} -> extension: {extractor.file_extensions[r.file_type_index] if r.file_type_index < len(extractor.file_extensions) else '?'}")
            break

# Find LevelData files for each sk_ map
print("\n=== SKIRMISH MAP LEVELDATA FILES ===")
# LevelData extension should be found via file_type_index or name pattern
# In DFPF format, (d3>>20)&0xFF gives file_type_index
leveldata_ext = None
for i, ext in enumerate(extractor.file_extensions):
    if 'leveldata' in ext.lower():
        print(f"LevelData extension index {i}: {ext}")
        if leveldata_ext is None:
            leveldata_ext = i

# Search for leveldata files in worlds/sk_*/
leveldata_files = {}
for r in extractor.file_records:
    fn = r.full_filename.replace(chr(92), '/').lower()
    if '/worlds/sk_' in fn and 'leveldata' in fn:
        # Extract sk_X from path
        parts = fn.split('/')
        for part in parts:
            if part.startswith('sk_') and '_' in part:
                sk_map = part.replace('.leveldata', '')
                leveldata_files[sk_map] = r
                print(f"{sk_map}: {r.full_filename}")
                break

# Find SoloSetup or GameMode files
print("\n=== SOLOSETUP AND GAMEMODE FILES ===")
solo_setup_files = []
game_mode_files = []
for r in extractor.file_records:
    fn = r.full_filename.replace(chr(92), '/').lower()
    if 'solosetup' in fn:
        solo_setup_files.append(r)
        print(f"SoloSetup: {r.full_filename}")
    if 'gamemode' in fn:
        game_mode_files.append(r)
        print(f"GameMode: {r.full_filename}")

# Also look for any MP (multiplayer) related files
print("\n=== MP-RELATED FILES ===")
mp_files = []
for r in extractor.file_records:
    fn = r.full_filename.replace(chr(92), '/').lower()
    if 'mp' in fn or 'multiplayer' in fn or 'skirmish' in fn:
        mp_files.append(r)
        print(f"  {r.full_filename}")

print(f"\nTotal SoloSetup files: {len(solo_setup_files)}")
print(f"Total GameMode files: {len(game_mode_files)}")
print(f"Total MP-related files: {len(mp_files)}")