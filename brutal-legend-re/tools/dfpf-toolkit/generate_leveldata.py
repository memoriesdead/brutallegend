#!/usr/bin/env python3
"""
Generate a minimal LevelData binary file for a custom map in Brutal Legend format.

LevelData Structure:
- Starts with 'rdHp' magic (4 bytes)
- Header fields (at least 44 bytes of unknown purpose)
- Path entries: 4-byte LE length + null-terminated path string
- Havok physics data (GLLp/LHp markers)

Usage:
    python generate_leveldata.py [--map-name TestCustom] [--output path]
"""

import struct
import zlib
import argparse
from pathlib import Path

# LevelData magic
LEVELDATA_MAGIC = b'rdHp'

# Havok markers found in LevelData
HAVOK_MAGICS = [b'GLLp', b'LHp', b'hkCL', b'hkSC']


def parse_leveldata(data: bytes) -> dict:
    """Parse a LevelData binary and extract its structure."""
    if len(data) < 4:
        raise ValueError("Data too short")

    magic = data[0:4]
    if magic != LEVELDATA_MAGIC:
        raise ValueError(f"Invalid magic: {magic!r}")

    result = {
        'magic': magic,
        'header': {},
        'paths': [],
        'havok_data': None
    }

    # Header is always 44 bytes
    HEADER_SIZE = 44

    # Parse header as raw bytes and key fields
    result['header']['raw'] = data[0:HEADER_SIZE]
    result['header']['size'] = HEADER_SIZE

    # Parse header fields for display
    header_fields = []
    for i in range(4, HEADER_SIZE, 4):
        val = struct.unpack('<I', data[i:i+4])[0]
        header_fields.append(val)
    result['header']['fields'] = header_fields

    # Parse path entries starting at offset 44
    path_offset = HEADER_SIZE
    while path_offset < len(data):
        if path_offset + 4 > len(data):
            break

        # Check for Havok magic - this marks end of path entries
        if data[path_offset:path_offset+4] in HAVOK_MAGICS:
            result['havok_offset'] = path_offset
            break

        str_len = struct.unpack('<I', data[path_offset:path_offset+4])[0]
        if str_len < 4 or str_len > 4096 or path_offset + 4 + str_len > len(data):
            break

        str_data = data[path_offset+4:path_offset+4+str_len]

        # Validate string is actually a path (starts with printable ASCII, contains valid path chars)
        if not str_data or str_data[0] < 32 or str_data[0] > 126:
            # Not a valid string, might be alignment or garbage
            # Move past this 4-byte length field and continue
            path_offset += 4
            continue

        path_str = str_data.decode('ascii', errors='replace').rstrip('\x00')

        # Additional validation: must look like a path (contains / or \ or alphanumeric)
        if not any(c.isalnum() or c in '/\\.-_' for c in path_str[:10]):
            # Doesn't look like a valid path
            path_offset += 4
            continue

        result['paths'].append({
            'offset': path_offset,
            'length': str_len,
            'string': path_str,
            'raw': str_data
        })
        path_offset += 4 + str_len
    else:
        # No Havok magic found, but check if there's data after paths
        result['havok_offset'] = path_offset

    # Havok data starts at the first Havok magic found
    if 'havok_offset' in result:
        for havok_off in range(result['havok_offset'], min(len(data), 256)):
            if data[havok_off:havok_off+4] in HAVOK_MAGICS:
                result['havok_data'] = data[havok_off:]
                result['havok_offset'] = havok_off
                break

    return result


def create_leveldata(map_name: str, paths: list, header_base: bytes = None, havok_data: bytes = None) -> bytes:
    """Create a new LevelData binary with the given paths."""

    # Default header if not provided
    if header_base is None:
        # Build a minimal header based on observed structure
        header = bytearray()
        header.extend(LEVELDATA_MAGIC)  # 0-3: magic
        header.extend(struct.pack('<I', 0xFFFFFFFF))  # 4-7: unknown (-1)
        header.extend(struct.pack('<I', 0x1B2))  # 8-11: some size (434)
        header.extend(struct.pack('<I', 2))  # 12-15: version/count
        header.extend(struct.pack('<I', 0xFFFFFFFD))  # 16-19: unknown
        header.extend(struct.pack('<Q', 0))  # 20-27: unknown
        header.extend(struct.pack('<I', 0x44800000))  # 28-31: float 1024.0
        header.extend(struct.pack('<I', 0x44000000))  # 32-35: float 512.0 or 768.0
        header.extend(struct.pack('<I', 0x44000000))  # 36-39: float 768.0
        header.extend(struct.pack('<I', 0x2000200))  # 40-43: tile range
        header = bytes(header)
    else:
        header = header_base[:44]  # Take first 44 bytes of header

    # Build path entries
    path_data = bytearray()
    for path in paths:
        path_bytes = path.encode('ascii') + b'\x00'
        path_data.extend(struct.pack('<I', len(path_bytes)))
        path_data.extend(path_bytes)

    # Combine
    result = bytearray(header)
    result.extend(path_data)

    # NOTE: Original LevelData does NOT align before Havok data
    # Havok data typically starts at a non-16-byte-aligned offset

    # Add Havok data if provided
    if havok_data:
        result.extend(havok_data)

    return bytes(result)


def extract_paths_from_continent3(packs_dir: Path) -> tuple:
    """Extract and parse the continent3 LevelData to understand the structure."""

    # We need to use DFPFExtractor to get the continent3 base_objects.bin
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from dfpf_extract import DFPFExtractor

    header_path = packs_dir / 'RgB_World.~h'
    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    # Find worlds/continent3/global/base_objects.bin
    record = None
    for r in extractor.file_records:
        fn = r.full_filename.replace('\\', '/')
        if fn == 'worlds/continent3/global/base_objects.bin':
            record = r
            break

    if not record:
        raise ValueError("Could not find continent3 base_objects.bin")

    # Read data
    with open(extractor.data_path, 'rb') as f:
        f.seek(record.offset)
        read_size = max(record.size, min(record.uncompressed_size * 2, 1024*1024)) if record.size > 0 else 65536
        data = f.read(read_size)

    # Decompress if needed
    if record.compressed:
        try:
            decompressor = zlib.decompressobj(zlib.MAX_WBITS)
            data = decompressor.decompress(data)
        except Exception as e:
            print(f"Decompression error: {e}, trying raw deflate")
            try:
                decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                data = decompressor.decompress(data)
            except:
                pass

    return data


def generate_custom_leveldata(map_name: str, packs_dir: Path, output_path: Path):
    """Generate a new LevelData for a custom map."""

    print(f"Generating LevelData for map: {map_name}")

    # Extract the continent3 base_objects.bin to use as template
    print("Extracting continent3 LevelData as template...")
    template_data = extract_paths_from_continent3(packs_dir)

    print(f"Template size: {len(template_data)} bytes")

    # Parse the template
    print("Parsing template structure...")
    parsed = parse_leveldata(template_data)

    print(f"  Magic: {parsed['magic']}")
    print(f"  Header fields: {len(parsed['header']['fields'])}")
    print(f"  Paths found: {len(parsed['paths'])}")
    if parsed['havok_data']:
        print(f"  Havok data offset: {parsed['havok_offset']}")
        print(f"  Havok data size: {len(parsed['havok_data'])} bytes")

    # Show first few paths
    print("\n  First 5 paths:")
    for i, p in enumerate(parsed['paths'][:5]):
        print(f"    {i}: {p['string']}")

    # Create new paths for TestCustom
    print(f"\nCreating new paths for {map_name}...")
    new_paths = []
    for path_info in parsed['paths']:
        old_path = path_info['string']
        # Replace continent3 with map_name and use tile x100/y100
        new_path = old_path.replace('continent3', map_name)
        # For a minimal test, we could just change the first path
        # But let's keep all paths and just change the map name
        new_paths.append(new_path)

    # Actually, for a minimal test, let's only create paths for x100/y100
    # that reference the TestCustom map
    minimal_paths = [
        f"worlds/{map_name}/tile/x100/y100/base_tile",
        f"worlds/{map_name}/tile/x100/y100/height",
    ]

    print(f"\n  New paths (minimal set):")
    for p in minimal_paths:
        print(f"    {p}")

    # Get the header and Havok data from template
    header_base = template_data[:parsed['havok_offset'] if parsed['havok_offset'] else 44]
    havok_data = parsed['havok_data']

    # Create new LevelData
    print("\nCreating new LevelData...")
    new_data = create_leveldata(
        map_name,
        minimal_paths,
        header_base=header_base,
        havok_data=havok_data
    )

    print(f"  New LevelData size: {len(new_data)} bytes")

    # Compress the data (zlib)
    print("Compressing data...")
    compressed = zlib.compress(new_data, level=9)

    print(f"  Compressed size: {len(compressed)} bytes")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(new_data)  # Save uncompressed for now

    print(f"\nSaved LevelData to: {output_path}")

    return new_data


def main():
    parser = argparse.ArgumentParser(description='Generate LevelData for custom map')
    parser.add_argument('--map-name', default='TestCustom',
                       help='Name of the custom map (default: TestCustom)')
    parser.add_argument('--output', default=None,
                       help='Output path (default: <Mods>/LevelData_<mapname>.bin)')
    parser.add_argument('--packs-dir', default=None,
                       help='Path to Win/Packs directory')

    args = parser.parse_args()

    # Default paths
    if args.packs_dir:
        packs_dir = Path(args.packs_dir)
    else:
        packs_dir = Path(r'C:\Users\kevin\OneDrive\Desktop\steam\steamapps\common\BrutalLegend\Win\Packs')

    if args.output:
        output_path = Path(args.output)
    else:
        mods_dir = Path(r'C:\Users\kevin\OneDrive\Desktop\steam\steamapps\common\BrutalLegend\Win\Mods')
        output_path = mods_dir / f'LevelData_{args.map_name}.bin'

    try:
        generate_custom_leveldata(args.map_name, packs_dir, output_path)
        print("\nDone!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())