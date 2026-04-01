#!/usr/bin/env python3
"""
DFPF V5 Repacker for Brutal Legend
Builds a .~h/.~p pair from extracted files.

Usage:
    python dfpf_repack.py <original_header.~h> <extracted_dir> [output_name]

Example:
    python dfpf_repack.py ../../Win/Packs/Man_Script.~h ./Man_Script_extracted Man_Script_new
"""

import struct
import zlib
import os
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Optional

COMPRESSION_UNCOMPRESSED_V5 = 4
COMPRESSION_ZLIB_V5 = 8
COMPRESSION_XMEMCOMPRESS_XBOX = 12


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


class DFPFRepacker:
    MAGIC = b"dfpf"
    VERSION = 5
    HEADER_SIZE = 88
    MARKER_VALUE = 0x23A1CEAB

    def __init__(self, header_path: str):
        self.header_path = Path(header_path)
        self.data_path = self.header_path.with_suffix(".~p")
        self.file_extensions: List[str] = []
        self.records: List[FileRecord] = []

    def load_from_extracted(self, extracted_dir: str) -> None:
        """Load file info from an extracted directory structure."""
        ext_dir = Path(extracted_dir)
        if not ext_dir.exists():
            raise FileNotFoundError(f"Extracted directory not found: {ext_dir}")

        # Scan for files and determine extensions
        found_exts = set()
        found_files = []

        for root, dirs, files in os.walk(ext_dir):
            for fname in files:
                fpath = Path(root)
                rel_path = fpath.relative_to(ext_dir)
                ext = fname.split('.')[-1].lower() if '.' in fname else ''

                found_exts.add(ext)
                found_files.append((rel_path, fname, ext, fpath / fname))

        # Sort extensions for consistent ordering
        self.file_extensions = sorted(found_exts)

        # Create records
        self.records = []
        for i, (rel_path, fname, ext, fpath) in enumerate(found_files):
            record = FileRecord()
            record.filename = str(rel_path).replace('\\', '/')
            record.extension = ext
            record.file_type_index = self.file_extensions.index(ext)

            # Read file data
            with open(fpath, 'rb') as f:
                record.data = f.read()

            record.uncompressed_size = len(record.data)

            # Determine compression - use zlib if data compresses well
            if len(record.data) > 0:
                compressed = zlib.compress(record.data, 9)
                if len(compressed) < len(record.data):
                    record.data = compressed
                    record.compression_type = COMPRESSION_ZLIB_V5
                    record.size = len(compressed)
                else:
                    record.compression_type = COMPRESSION_UNCOMPRESSED_V5
                    record.size = record.uncompressed_size
            else:
                record.compression_type = COMPRESSION_UNCOMPRESSED_V5
                record.size = 0

            self.records.append(record)

        print(f"Loaded {len(self.records)} files with {len(self.file_extensions)} extensions")
        print(f"Extensions: {', '.join(self.file_extensions)}")

    def load_from_header(self, original_header_path: str) -> None:
        """Load file metadata from original header (for preserving structure)."""
        from dfpf_extract import DFPFExtractor

        extractor = DFPFExtractor(original_header_path)
        extractor.parse()

        self.file_extensions = extractor.file_extensions
        self.records = []

        for rec in extractor.file_records:
            record = FileRecord()
            record.filename = rec.filename
            record.extension = rec.extension
            record.file_type_index = rec.file_type_index
            record.compression_type = rec.compression_type
            record.uncompressed_size = rec.uncompressed_size

            # Read raw data from .~p file
            with open(extractor.data_path, 'rb') as f:
                f.seek(rec.offset)
                record.data = f.read(rec.size)
                record.size = rec.size

            # If compressed, decompress for repacking
            if rec.compressed and rec.compression_type == COMPRESSION_ZLIB_V5:
                try:
                    record.data = zlib.decompress(record.data, zlib.MAX_WBITS)
                    record.uncompressed_size = len(record.data)
                except zlib.error:
                    print(f"  Warning: Could not decompress {rec.full_filename}, storing as-is")

            self.records.append(record)

        print(f"Loaded {len(self.records)} files from original header")

    def _pack_file_record(self, record: FileRecord, name_offset: int) -> bytes:
        """Pack a file record into 16 bytes.

        Verified decode formulas from extractor:
          uncompressed_size = raw_dword0 >> 8
          name_offset = raw_dword1 >> 11
          offset = raw_dword2 >> 3
          size = (raw_dword2 << 5) >> 9  (equivalent to raw_dword2 >> 4)
          file_type_index = ((raw_dword3 << 4) >> 24) >> 1
          compression_type = data[15] & 0x0F

        Verified encode formulas (tested):
          raw_dword0 = uncompressed_size << 8
          raw_dword1 = name_offset << 11
          raw_dword2 = (offset << 3) | (size & 0xFFFFFFF0)
          raw_dword3 = ((file_type_index * 2) << 20) | (compression_type & 0x0F)
        """
        raw_dword0 = record.uncompressed_size << 8
        raw_dword1 = name_offset << 11
        raw_dword2 = (record.offset << 3) | (record.size & 0xFFFFFFF0)
        raw_dword3 = ((record.file_type_index * 2) << 20) | (record.compression_type & 0x0F)

        return struct.pack(">IIII", raw_dword0, raw_dword1, raw_dword2, raw_dword3)

    def repack(self, output_path: str) -> None:
        """Repack files into a .~h/.~p pair."""
        out_path = Path(output_path)
        header_out = out_path.with_suffix(".~h")
        data_out = out_path.with_suffix(".~p")

        print(f"Repacking to {header_out} / {data_out}")

        # Build name directory
        name_dir = b''
        name_offsets: Dict[int, int] = {}

        for i, rec in enumerate(self.records):
            name_offsets[i] = len(name_dir)
            name_dir += rec.filename.encode('ascii') + b'\x00'

        name_dir_size = len(name_dir)

        # Calculate offsets for header
        # Header file layout:
        # 0: magic (4 bytes) = "dfpf"
        # 4: version (1 byte) = 5
        # 5: padding (3 bytes)
        # 8: header struct (88 bytes)
        # After header: file extension table, then file records, then name dir

        header_fixed_size = 4 + 1 + 3 + self.HEADER_SIZE  # 96 bytes

        ext_table_size = len(self.file_extensions) * 16
        file_records_size = len(self.records) * 16

        file_ext_offset = header_fixed_size
        name_dir_offset = file_ext_offset + ext_table_size
        file_records_offset = name_dir_offset + name_dir_size

        # Build the .~p data file
        data_parts = []
        current_offset = 0

        for rec in self.records:
            rec.offset = current_offset
            data_parts.append(rec.data)
            current_offset += rec.size

        # Write .~p data file
        with open(data_out, 'wb') as f:
            for data in data_parts:
                f.write(data)

        # Build the .~h header file
        with open(header_out, 'wb') as f:
            # Magic
            f.write(self.MAGIC)

            # Version
            f.write(struct.pack("B", self.VERSION))

            # Padding
            f.write(b'\x00' * 3)

            # Header struct (88 bytes)
            header_data = bytearray(self.HEADER_SIZE)

            struct.pack_into(">Q", header_data, 0, file_ext_offset)
            struct.pack_into(">Q", header_data, 8, name_dir_offset)
            struct.pack_into(">I", header_data, 16, len(self.file_extensions))
            struct.pack_into(">I", header_data, 20, name_dir_size)
            struct.pack_into(">I", header_data, 24, len(self.records))
            struct.pack_into(">I", header_data, 28, self.MARKER_VALUE)
            struct.pack_into(">I", header_data, 32, 0)  # blank_bytes1
            struct.pack_into(">I", header_data, 36, 0)  # blank_bytes2
            struct.pack_into(">Q", header_data, 40, current_offset)  # junk_data_offset
            struct.pack_into(">Q", header_data, 48, file_records_offset)
            struct.pack_into(">Q", header_data, 56, 0)  # footer_offset1
            struct.pack_into(">Q", header_data, 64, 0)  # footer_offset2
            struct.pack_into(">I", header_data, 72, 0)  # unknown
            struct.pack_into(">I", header_data, 76, self.MARKER_VALUE)

            f.write(header_data)

            # File extension table (variable size: 4 bytes length + name_length + 12 bytes unknown)
            for ext_name in self.file_extensions:
                ext_bytes = ext_name.encode('ascii')
                # Format: 4 bytes name_length + name + 12 bytes unknown (padding)
                ext_entry = struct.pack(">I", len(ext_bytes)) + ext_bytes + b'\x00' * 12
                f.write(ext_entry)

            # Name directory
            f.write(name_dir)

            # File records (16 bytes each)
            for i, rec in enumerate(self.records):
                rec_bytes = self._pack_file_record(rec, name_offsets[i])
                f.write(rec_bytes)

        print(f"Repacked {len(self.records)} files")
        print(f"  Header: {header_out} ({Path(header_out).stat().st_size} bytes)")
        print(f"  Data: {data_out} ({Path(data_out).stat().st_size} bytes)")


def main():
    if len(sys.argv) < 3:
        print("Usage: python dfpf_repack.py <original_header.~h> <extracted_dir> [output_name]")
        print()
        print("Example:")
        print("  python dfpf_repack.py ../../Win/Packs/Man_Script.~h ./Man_Script_extracted Man_Script_new")
        sys.exit(1)

    original_header = sys.argv[1]
    extracted_dir = sys.argv[2]
    output_name = sys.argv[3] if len(sys.argv) > 3 else None

    if output_name is None:
        output_name = Path(extracted_dir).stem + "_repacked"

    try:
        repacker = DFPFRepacker(output_name)

        # Load metadata from original header to preserve structure
        repacker.load_from_header(original_header)

        # Load actual file data from extracted directory
        repacker.load_from_extracted(extracted_dir)

        # Repack
        repacker.repack(output_name)

        print("\nRepacking complete!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
