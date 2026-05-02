#!/usr/bin/env python3
"""
Create TestCustom map bundle from sk_1 extraction.
Extracts sk_1 from RgS_World2 and metadata from Man_Trivial, renames to TestCustom, and repacks.
"""

import sys
import shutil
import re
import struct
import zlib
import os
from pathlib import Path

sys.path.insert(0, '.')
from dfpf_extract import DFPFExtractor

packs_dir = Path('C:/Users/kevin/OneDrive/Desktop/steam/steamapps/common/BrutalLegend/Win/Packs')
work_dir = Path('C:/Users/kevin/brutallegend/brutal-legend-re/tools/dfpf-toolkit')

COMPRESSION_UNCOMPRESSED_V5 = 4
COMPRESSION_ZLIB_V5 = 8

def extract_file_data(extractor, record):
    """Extract file data from a DFPF record."""
    with open(extractor.data_path, 'rb') as f:
        f.seek(record.offset)
        read_size = max(record.size, min(record.uncompressed_size * 2, 1024 * 1024)) if record.size > 0 else 65536
        data = f.read(read_size)

    if record.compressed:
        try:
            decompressor = zlib.decompressobj(zlib.MAX_WBITS)
            data = decompressor.decompress(data)
        except zlib.error:
            try:
                decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                data = decompressor.decompress(data)
            except:
                pass  # Use raw data
    return data

def get_all_extensions():
    """Get all unique file extensions from both RgS_World2 and Man_Trivial."""
    extensions = set()

    # Get from RgS_World2
    header_path = packs_dir / 'RgS_World2.~h'
    e = DFPFExtractor(str(header_path))
    e.parse()
    extensions.update(e.file_extensions)
    print(f'Extensions from RgS_World2: {len(e.file_extensions)}')

    # Get from Man_Trivial
    header_path = packs_dir / 'Man_Trivial.~h'
    e = DFPFExtractor(str(header_path))
    e.parse()
    extensions.update(e.file_extensions)
    print(f'Extensions from Man_Trivial: {len(e.file_extensions)}')

    # Return as sorted list, keeping original RgS_World2 order first
    ordered = []
    seen = set()
    # First RgS_World2
    header_path = packs_dir / 'RgS_World2.~h'
    e = DFPFExtractor(str(header_path))
    e.parse()
    for ext in e.file_extensions:
        if ext not in seen:
            ordered.append(ext)
            seen.add(ext)
    # Then Man_Trivial
    header_path = packs_dir / 'Man_Trivial.~h'
    e = DFPFExtractor(str(header_path))
    e.parse()
    for ext in e.file_extensions:
        if ext not in seen:
            ordered.append(ext)
            seen.add(ext)

    print(f'Total unique extensions: {len(ordered)}')
    return ordered

def extract_sk1_tiles():
    """Extract sk_1 tile files from RgS_World2."""
    print('=== Extracting sk_1 tiles from RgS_World2 ===')
    header_path = packs_dir / 'RgS_World2.~h'
    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    # Find sk_1 files
    sk1_files = [r for r in extractor.file_records if 'sk_1' in r.full_filename.replace(chr(92), '/')]
    print(f'Found {len(sk1_files)} sk_1 files')

    # Create output directory
    output_dir = work_dir / 'sk_1_extracted'
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # Extract each file, renaming path from sk_1 to TestCustom
    for i, record in enumerate(sk1_files):
        # Convert path: worlds/sk_1/... -> worlds/TestCustom/...
        original_path = record.full_filename.replace(chr(92), '/')
        new_path = original_path.replace('worlds/sk_1/', 'worlds/TestCustom/')

        output_path = output_dir / new_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = extract_file_data(extractor, record)

        with open(output_path, 'wb') as f:
            f.write(data)

        if (i + 1) % 50 == 0:
            print(f'  Extracted {i + 1}/{len(sk1_files)}')

    print(f'Extracted {len(sk1_files)} tile files')
    return output_dir

def extract_sk1_metadata():
    """Extract sk_1 metadata files from Man_Trivial and rename to TestCustom."""
    print('\n=== Extracting sk_1 metadata from Man_Trivial ===')
    header_path = packs_dir / 'Man_Trivial.~h'
    extractor = DFPFExtractor(str(header_path))
    extractor.parse()

    # Find sk_1 files in Man_Trivial
    sk1_files = [r for r in extractor.file_records if 'sk_1' in r.full_filename.replace(chr(92), '/')]
    print(f'Found {len(sk1_files)} sk_1 metadata files')
    for r in sk1_files:
        print(f'  {r.full_filename}')

    # Create output directory for metadata
    metadata_dir = work_dir / 'sk_1_extracted'
    output_count = 0

    for record in sk1_files:
        original_path = record.full_filename.replace(chr(92), '/')
        # Replace sk_1 with TestCustom
        new_path = original_path.replace('sk_1', 'TestCustom')

        output_path = metadata_dir / new_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = extract_file_data(extractor, record)

        with open(output_path, 'wb') as f:
            f.write(data)
        output_count += 1

    print(f'Extracted {output_count} metadata files')
    return output_count

def analyze_extracted(dir_path):
    """Analyze the extracted structure."""
    files = list(dir_path.glob('**/*'))
    files = [f for f in files if f.is_file()]
    print(f'\nTotal files: {len(files)}')

    # Find unique tile coordinates using Path
    xs = set()
    ys = set()
    for f in files:
        parts = f.parts
        for part in parts:
            if part.startswith('x') and part[1:].lstrip('-').isdigit():
                xs.add(part)
            elif part.startswith('y') and part[1:].lstrip('-').isdigit():
                ys.add(part)

    x_coords = sorted(xs, key=lambda x: int(x[1:]) if x[1:].lstrip('-').isdigit() else 0)
    y_coords = sorted(ys, key=lambda y: int(y[1:]) if y[1:].lstrip('-').isdigit() else 0)
    print(f'X coordinates: {x_coords}')
    print(f'Y coordinates: {y_coords}')

    # Count by extension
    ext_counts = {}
    for f in files:
        ext = f.suffix
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    print('\nFile counts by extension:')
    for ext, count in sorted(ext_counts.items()):
        print(f'  {ext}: {count}')

    # Show root-level files
    root_files = [f for f in files if 'tile' not in f.parts]
    if root_files:
        print('\nRoot-level files:')
        for f in root_files[:20]:
            print(f'  {f.relative_to(dir_path)}')

class FileRecord:
    def __init__(self):
        self.filename: str = ""
        self.extension: str = ""
        self.uncompressed_size: int = 0
        self.offset: int = 0
        self.size: int = 0
        self.file_type_index: int = 0
        self.compression_type: int = COMPRESSION_ZLIB_V5
        self.data: bytes = b''

def create_bundle_from_extracted(extracted_dir, output_name):
    """Create a new DFPF bundle from extracted files."""
    print(f'\n=== Creating {output_name} bundle ===')

    # Get combined file extensions from both bundles
    file_extensions = get_all_extensions()

    # Build case-insensitive extension lookup
    ext_lookup = {ext.lower(): i for i, ext in enumerate(file_extensions)}
    print(f'Extension lookup has {len(ext_lookup)} entries')

    # Build records from extracted files
    extracted_dir = Path(extracted_dir)
    records = []

    for root, dirs, files in os.walk(extracted_dir):
        for fname in files:
            fpath = Path(root) / fname
            rel_path = str(fpath.relative_to(extracted_dir)).replace('\\', '/')

            # Skip directories, only process files
            rec = FileRecord()
            rec.filename = rel_path  # Use the full path with extension as-is

            # Get extension from filename (case-insensitive lookup)
            if '.' in fname:
                ext = fname.rsplit('.', 1)[-1].lower()
            else:
                ext = 'bin'
            rec.extension = ext

            # Find file_type_index using case-insensitive lookup
            if ext in ext_lookup:
                rec.file_type_index = ext_lookup[ext]
            else:
                # Unknown extension - print warning and use bin
                print(f'  Warning: Unknown extension "{ext}" for {rel_path}, using bin')
                rec.file_type_index = ext_lookup.get('bin', 0)

            # Read file data
            with open(fpath, 'rb') as f:
                data = f.read()

            rec.uncompressed_size = len(data)
            rec.data = data

            # Compress the data
            if len(data) > 0:
                compressed = zlib.compress(data, 9)
                if len(compressed) < len(data):
                    rec.data = compressed
                    rec.compression_type = COMPRESSION_ZLIB_V5
                    rec.size = len(compressed)
                else:
                    rec.compression_type = COMPRESSION_UNCOMPRESSED_V5
                    rec.size = len(data)
            else:
                rec.compression_type = COMPRESSION_UNCOMPRESSED_V5
                rec.size = 0

            records.append(rec)

    print(f'Built {len(records)} records from extracted files')

    # Sort records by filename for consistent ordering
    records.sort(key=lambda r: r.filename)

    # Build name directory
    name_dir = b''
    name_offsets = {}
    for i, rec in enumerate(records):
        name_offsets[i] = len(name_dir)
        name_dir += rec.filename.encode('ascii') + b'\x00'
    name_dir_size = len(name_dir)

    # Calculate offsets
    header_fixed_size = 4 + 1 + 3 + 88  # 96 bytes
    ext_table_size = sum(4 + len(ext_name.encode('ascii')) + 12 for ext_name in file_extensions)
    file_records_size = len(records) * 16

    file_ext_offset = header_fixed_size
    name_dir_offset = file_ext_offset + ext_table_size
    file_records_offset = name_dir_offset + name_dir_size

    # Build the .~p data file
    out_path = Path(output_name)
    header_out = out_path.with_suffix(".~h")
    data_out = out_path.with_suffix(".~p")

    print(f'Writing data file...')
    data_offsets = []
    with open(data_out, 'wb') as f:
        for rec in records:
            data_offsets.append(f.tell())
            f.write(rec.data)
        current_offset = f.tell()

    # Build the .~h header file
    print(f'Writing header file...')
    with open(header_out, 'wb') as f:
        # Magic
        f.write(b"dfpf")
        # Version
        f.write(struct.pack("B", 5))
        # Padding
        f.write(b'\x00' * 3)

        # Header struct (88 bytes)
        header_data = bytearray(88)
        struct.pack_into(">Q", header_data, 0, file_ext_offset)
        struct.pack_into(">Q", header_data, 8, name_dir_offset)
        struct.pack_into(">I", header_data, 16, len(file_extensions))
        struct.pack_into(">I", header_data, 20, name_dir_size)
        struct.pack_into(">I", header_data, 24, len(records))
        struct.pack_into(">I", header_data, 28, 0x23A1CEAB)  # marker1
        struct.pack_into(">I", header_data, 32, 0)  # blank_bytes1
        struct.pack_into(">I", header_data, 36, 0)  # blank_bytes2
        struct.pack_into(">Q", header_data, 40, current_offset)  # junk_data_offset
        struct.pack_into(">Q", header_data, 48, file_records_offset)
        struct.pack_into(">Q", header_data, 56, 0)  # footer_offset1
        struct.pack_into(">Q", header_data, 64, 0)  # footer_offset2
        struct.pack_into(">I", header_data, 72, 0)  # unknown
        struct.pack_into(">I", header_data, 76, 0x23A1CEAB)  # marker2

        f.write(header_data)

        # File extension table
        for ext_name in file_extensions:
            ext_bytes = ext_name.encode('ascii')
            ext_entry = struct.pack(">I", len(ext_bytes)) + ext_bytes + b'\x00' * 12
            f.write(ext_entry)

        # Name directory
        f.write(name_dir)

        # File records
        for i, rec in enumerate(records):
            rec.offset = data_offsets[i]
            raw_dword0 = rec.uncompressed_size << 8
            raw_dword1 = name_offsets[i] << 11
            raw_dword2 = rec.offset << 3
            raw_dword3 = (rec.file_type_index << 20) | (rec.compression_type & 0x0F)
            f.write(struct.pack(">IIII", raw_dword0, raw_dword1, raw_dword2, raw_dword3))

    h_size = Path(header_out).stat().st_size
    p_size = Path(data_out).stat().st_size
    print(f'Created {output_name}.~h ({h_size} bytes)')
    print(f'Created {output_name}.~p ({p_size} bytes)')

    return str(header_out), str(data_out)

if __name__ == '__main__':
    # Step 1: Extract sk_1 tiles from RgS_World2 (already renamed to TestCustom)
    extract_sk1_tiles()

    # Step 2: Extract sk_1 metadata from Man_Trivial and add to TestCustom
    extract_sk1_metadata()

    # Step 3: Analyze structure
    print('\n=== Analyzing TestCustom structure ===')
    analyze_extracted(work_dir / 'sk_1_extracted')

    # Step 4: Create the bundle
    output_dir = work_dir / 'RgS_Testcustom'
    bundle_h, bundle_p = create_bundle_from_extracted(
        work_dir / 'sk_1_extracted',
        str(output_dir)
    )

    # Step 5: Copy to Win/Mods
    mods_dir = packs_dir.parent / 'Mods'
    mods_dir.mkdir(exist_ok=True)
    shutil.copy(bundle_h, mods_dir)
    shutil.copy(bundle_p, mods_dir)
    print(f'\nCopied to {mods_dir}')