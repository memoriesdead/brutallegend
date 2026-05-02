#!/usr/bin/env python3
"""
Custom Map Pipeline for Brutal Legend

Creates a modified DFPF terrain bundle from heightfield modifications.

Usage:
    python custom_map_pipeline.py --source <original_bundle.~h> --world <world_path>
                                 --tile-x X --tile-y Y --output <output_name>
                                 [--raise-area X Y RADIUS AMOUNT]
                                 [--lower-area X Y RADIUS AMOUNT]
                                 [--flatten X Y HEIGHT]
                                 [--set HEIGHT]

Example:
    python custom_map_pipeline.py --source ../../Win/Packs/00Startup.~h \
                                  --world "worlds/testworld" \
                                  --tile-x 100 --tile-y 100 \
                                  --output ModMap \
                                  --raise-area 64 64 20 50
"""

import argparse
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def setup_terrain_editor():
    """Setup terrain_editor imports."""
    # Change to terrain-editor directory to import its modules
    terrain_editor_dir = Path(__file__).parent.parent / 'terrain-editor'
    if terrain_editor_dir.exists():
        sys.path.insert(0, str(terrain_editor_dir))


def extract_terrain_from_bundle(bundle_path: str, world_path: str, output_dir: str) -> list:
    """Extract terrain files from a DFPF bundle."""
    setup_terrain_editor()

    from terrain_editor import DFPFBundleExtractor

    extractor = DFPFBundleExtractor(bundle_path)
    if not extractor.parse():
        raise ValueError(f"Failed to parse bundle: {bundle_path}")

    extracted = extractor.extract_terrain_files(world_path, output_dir)
    print(f"Extracted {len(extracted)} terrain files")
    return extracted


def find_heightfield(terrain_dir: str, tile_x: int, tile_y: int) -> str:
    """Find the heightfield file for a given tile coordinate."""
    terrain_path = Path(terrain_dir)

    # Expected patterns
    patterns = [
        f"*/tile/x{tile_x}/y{tile_y}/height.Heightfield",
        f"*/tile/x{tile_x}/y{tile_y}/height.bin",
        f"*/height.Heightfield",
        f"*/height.bin",
    ]

    for pattern in patterns:
        for path in terrain_path.rglob(pattern.replace('*', '')):
            if path.exists():
                return str(path)

    # Fallback: search for any heightfield
    for heightfield in terrain_path.rglob("height.*"):
        if heightfield.suffix in ['.Heightfield', '.bin', '. DDS']:
            return str(heightfield)

    return None


def create_modified_heightfield(source_path: str, output_path: str,
                                  raise_areas: list = None,
                                  lower_areas: list = None,
                                  flatten_areas: list = None,
                                  set_height: float = None) -> bool:
    """Create a modified heightfield with terrain edits."""
    setup_terrain_editor()

    from terrain_editor import DDSHeightfield

    # Load heightfield
    hf = DDSHeightfield(source_path)
    if not hf.parse():
        print(f"Warning: Could not parse {source_path} as DDS Heightfield")
        # Try as generic terrain file
        return False

    # Apply modifications
    if raise_areas:
        for x, y, radius, amount in raise_areas:
            hf.raise_area(int(x), int(y), int(radius), amount)

    if lower_areas:
        for x, y, radius, amount in lower_areas:
            hf.lower_area(int(x), int(y), int(radius), amount)

    if flatten_areas:
        for x, y, height in flatten_areas:
            hf.flatten(int(x), int(y), height)

    if set_height is not None:
        hf.fill(set_height)

    # Save modified heightfield
    hf.save(output_path)
    print(f"Saved modified heightfield to: {output_path}")
    return True


def create_terrain_heightfield(output_path: str, width: int = 1024, height: int = 1024,
                                base_height: float = 128) -> bool:
    """Create a new flat heightfield."""
    setup_terrain_editor()

    from terrain_editor import DDSHeightfield, encode_dxt5_image, apply_heightmap

    if not HAS_NUMPY:
        print("Error: numpy required for creating new heightfields")
        return False

    # Create heightmap filled with base_height
    heightmap = np.full((height, width), base_height, dtype=np.float32)

    # Create RGBA image from heightmap
    image = np.zeros((height, width, 4), dtype=np.uint8)
    image[:, :, 3] = heightmap.astype(np.uint8)

    # Encode to DXT5
    dxt5_data = encode_dxt5_image(width, height, image)

    # Create a minimal DDS heightfield file
    # This is a placeholder - actual format requires custom header
    with open(output_path, 'wb') as f:
        # Custom header (40 bytes)
        f.write(b'\x00' * 0x20)  # unknown_metadata
        f.write(b'rtxT')          # magic
        struct.pack('<I', f.write(b'\x00' * 4))  # data_size placeholder

        # DDS header (128 bytes)
        f.write(b'DDS ')
        dds_header = bytearray(128)
        struct.pack('<I', dds_header, 0, 128)  # dwSize
        struct.pack('<I', dds_header, 4, 0x1 | 0x2 | 0x4 | 0x1000)  # dwFlags
        struct.pack('<I', dds_header, 8, height)  # dwHeight
        struct.pack('<I', dds_header, 12, width)  # dwWidth
        struct.pack('<I', dds_header, 16, width * height * 4)  # dwPitchOrLinearSize
        struct.pack('<I', dds_header, 20, 0)  # dwDepth
        struct.pack('<I', dds_header, 24, 0)  # dwMipMapCount
        f.write(dds_header)

        # Write DXT5 data
        f.write(dxt5_data)

    print(f"Created new heightfield at: {output_path}")
    return True


def repack_bundle(source_bundle: str, modified_files_dir: str, output_name: str,
                  game_mods_path: str = None) -> str:
    """Repack modified files into a new DFPF bundle."""
    from dfpf_repack import DFPFRepacker

    # Determine output path
    if game_mods_path:
        output_path = os.path.join(game_mods_path, output_name)
    else:
        output_path = output_name

    print(f"Repacking to: {output_path}")

    # Create repacker
    repacker = DFPFRepacker(source_bundle)

    # Load from original header to preserve structure
    repacker.load_from_header(source_bundle)

    # Update with modified files
    repacker.load_from_extracted(modified_files_dir)

    # Repack
    repacker.repack(output_path)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Custom Map Pipeline - Create modified DFPF terrain bundles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract terrain from a bundle
    python custom_map_pipeline.py --source ../../Win/Packs/00Startup.~h \\
        --world "worlds/testworld" --tile-x 100 --tile-y 100 \\
        --extract-only --output /tmp/terrain_extract

    # Modify and repack
    python custom_map_pipeline.py --source ../../Win/Packs/00Startup.~h \\
        --modified-dir /tmp/terrain_extract \\
        --output MyModMap --repack-only
        """
    )

    parser.add_argument('--source', help='Source DFPF bundle header file (.~h)')
    parser.add_argument('--world', help='World path pattern to match (e.g., "worlds/testworld")')
    parser.add_argument('--tile-x', type=int, help='Tile X coordinate')
    parser.add_argument('--tile-y', type=int, help='Tile Y coordinate')
    parser.add_argument('--output', required=True, help='Output name for the modified bundle')

    # Extraction options
    parser.add_argument('--extract-only', action='store_true',
                        help='Only extract terrain files, do not modify')

    # Modification options
    parser.add_argument('--modified-dir',
                        help='Directory containing already-modified terrain files')
    parser.add_argument('--raise-area', nargs=4, type=float, metavar=('X', 'Y', 'RADIUS', 'AMOUNT'),
                        action='append', help='Raise circular area')
    parser.add_argument('--lower-area', nargs=4, type=float, metavar=('X', 'Y', 'RADIUS', 'AMOUNT'),
                        action='append', help='Lower circular area')
    parser.add_argument('--flatten', nargs=3, type=float, metavar=('X', 'Y', 'HEIGHT'),
                        action='append', help='Flatten area to height')
    parser.add_argument('--set', type=float, help='Set all heights to value')
    parser.add_argument('--smooth', type=float, help='Smooth heightmap')

    # Repacking options
    parser.add_argument('--repack-only', action='store_true',
                        help='Only repack, assuming files already modified')
    parser.add_argument('--game-mods-path',
                        default='C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Mods',
                        help='Path to game mods directory')

    args = parser.parse_args()

    # Create temp directory for work
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir)

        # Step 1: Extract terrain files
        if not args.repack_only:
            if not args.source:
                print("Error: --source required for extraction")
                return 1

            extracted = extract_terrain_from_bundle(args.source, args.world or "", extract_dir)
            if not extracted:
                print("Warning: No terrain files extracted")

            # Find heightfield to modify
            if args.tile_x is not None and args.tile_y is not None:
                heightfield_path = find_heightfield(extract_dir, args.tile_x, args.tile_y)
                if heightfield_path:
                    print(f"Found heightfield: {heightfield_path}")

                    # Apply modifications
                    if any([args.raise_area, args.lower_area, args.flatten, args.set is not None]):
                        output_path = heightfield_path  # Overwrite
                        success = create_modified_heightfield(
                            heightfield_path, output_path,
                            raise_areas=args.raise_area,
                            lower_areas=args.lower_area,
                            flatten_areas=args.flatten,
                            set_height=args.set
                        )
                        if not success:
                            print("Warning: Could not modify heightfield")

        # Use provided modified directory if specified
        if args.modified_dir:
            work_dir = args.modified_dir
        else:
            work_dir = extract_dir

        # Step 2: Repack into new bundle
        if args.source and not args.extract_only:
            output_bundle = repack_bundle(
                args.source,
                work_dir,
                args.output,
                game_mods_path=args.game_mods_path if not args.modified_dir else None
            )
            print(f"\nCustom map bundle created: {output_bundle}")
            print(f"  Header: {output_bundle}.~h")
            print(f"  Data: {output_bundle}.~p")

    return 0


if __name__ == '__main__':
    sys.exit(main())
