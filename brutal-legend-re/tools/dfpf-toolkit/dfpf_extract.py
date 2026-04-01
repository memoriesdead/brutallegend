#!/usr/bin/env python3
"""
DFPF V5 Extractor for Brutal Legend
Based on Kaitai spec dfpf_v5.ksy and DoubleFine Explorer Pascal code by Bennyboy

This script extracts files from DFPF V5 container format used by Brutal Legend.
It reads .~h header files and extracts from corresponding .~p data files.
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


class DFPFHeader:
    def __init__(self, data: bytes):
        if len(data) < 88:
            raise ValueError(f"Header too short: {len(data)} bytes")

        self.file_extension_offset = struct.unpack(">Q", data[0:8])[0]
        self.name_dir_offset = struct.unpack(">Q", data[8:16])[0]
        self.file_extension_count = struct.unpack(">I", data[16:20])[0]
        self.name_dir_size = struct.unpack(">I", data[20:24])[0]
        self.num_files = struct.unpack(">I", data[24:28])[0]
        self.marker1 = struct.unpack(">I", data[28:32])[0]
        self.blank_bytes1 = struct.unpack(">I", data[32:36])[0]
        self.blank_bytes2 = struct.unpack(">I", data[36:40])[0]
        self.junk_data_offset = struct.unpack(">Q", data[40:48])[0]
        self.file_records_offset = struct.unpack(">Q", data[48:56])[0]
        self.footer_offset1 = struct.unpack(">Q", data[56:64])[0]
        self.footer_offset2 = struct.unpack(">Q", data[64:72])[0]
        self.unknown = struct.unpack(">I", data[72:76])[0]
        self.marker2 = struct.unpack(">I", data[76:80])[0]


class FileRecord:
    def __init__(self, data: bytes, name_dir_offset: int, record_index: int = 0):
        if len(data) < 16:
            raise ValueError(f"File record too short: {len(data)} bytes")

        raw_dword0 = struct.unpack(">I", data[0:4])[0]
        raw_dword1 = struct.unpack(">I", data[4:8])[0]
        raw_dword2 = struct.unpack(">I", data[8:12])[0]
        raw_dword3 = struct.unpack(">I", data[12:16])[0]

        self.uncompressed_size = raw_dword0 >> 8
        self.raw_name_offset = raw_dword1 >> 11  # Original formula from Kaitai spec
        self.offset = raw_dword2 >> 3
        self.size = (raw_dword2 << 5) >> 9
        self.file_type_index = ((raw_dword3 << 4) >> 24) >> 1
        self.compression_type = data[15] & 0x0F

        self.name_position = name_dir_offset + self.raw_name_offset
        self.record_index = record_index  # Store record index for sequential lookup

        self.compressed = self.compression_type in (
            COMPRESSION_ZLIB_V5,
            COMPRESSION_XMEMCOMPRESS_XBOX,
        )

        self.compression_name = {
            1: "uncompressed_v6",
            2: "zlib_v2",
            4: "uncompressed_v5",
            8: "zlib_v5",
            12: "xmemcompress_xbox",
        }.get(self.compression_type, f"unknown({self.compression_type})")

        self.filename: str = ""
        self.extension: str = ""
        self.full_filename: str = ""


class FileExtensionEntry:
    def __init__(self, data: bytes, offset: int):
        if len(data) < 16:
            raise ValueError(
                f"Extension entry too short: {len(data)} bytes at offset {offset}"
            )

        name_length = struct.unpack(">I", data[0:4])[0]
        self.name = (
            data[4 : 4 + name_length].decode("ascii", errors="replace").rstrip("\x00")
        )
        self.unknown = data[4 + name_length : 16]


class DFPFExtractor:
    MAGIC = b"dfpf"

    def __init__(self, header_path: str):
        self.header_path = Path(header_path)
        self.data_path = self.header_path.with_suffix(".~p")

        if not self.header_path.exists():
            raise FileNotFoundError(f"Header file not found: {self.header_path}")
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

        self.header: Optional[DFPFHeader] = None
        self.file_records: List[FileRecord] = []
        self.file_extensions: List[str] = []
        self.names: Dict[int, str] = {}

    def parse(self) -> None:
        print(f"Parsing DFPF V5 bundle: {self.header_path}")
        print(f"Data file: {self.data_path}")

        with open(self.header_path, "rb") as f:
            magic = f.read(4)
            if magic != self.MAGIC:
                raise ValueError(f"Invalid magic: {magic!r} (expected {self.MAGIC!r})")

            version = struct.unpack("B", f.read(1))[0]
            print(f"Version: {version}")

            if version != 5:
                raise ValueError(f"Only DFPF V5 supported (got version {version})")

            # Skip 3 bytes of padding - header actually starts at byte 8 (after magic+version+padding)
            f.read(3)
            header_data = f.read(88)
            self.header = DFPFHeader(header_data)

            print(f"Number of files: {self.header.num_files}")
            print(f"File extension count: {self.header.file_extension_count}")

            f.seek(self.header.file_extension_offset)
            self.file_extensions = []
            for i in range(self.header.file_extension_count):
                # Extension entries are variable-length: 4 bytes name_length + name_length bytes + 12 bytes unknown
                name_length_bytes = f.read(4)
                if len(name_length_bytes) < 4:
                    break
                name_length = struct.unpack(">I", name_length_bytes)[0]
                name_bytes = f.read(name_length)
                name = name_bytes.decode("ascii", errors="replace").rstrip("\x00")
                self.file_extensions.append(name)
                # Skip 12 unknown bytes
                f.read(12)

            ext_names = [e.encode('ascii', errors='replace').decode('ascii') for e in self.file_extensions]
            print(f"File extensions ({len(ext_names)}): {', '.join(ext_names[:5])}...")

            f.seek(self.header.name_dir_offset)
            name_dir_data = f.read(self.header.name_dir_size)

            # Names are stored as null-terminated strings within name_dir_data
            # Store by absolute file position (name_dir_offset + buffer offset)
            buf_offset = 0
            while buf_offset < len(name_dir_data):
                null_pos = name_dir_data.find(b"\x00", buf_offset)
                if null_pos == -1:
                    break
                name = name_dir_data[buf_offset:null_pos].decode("ascii", errors="replace")
                # Store by absolute file position
                self.names[self.header.name_dir_offset + buf_offset] = name
                # Next name starts after this null (don't skip buf_offset + 1 - that's wrong)
                buf_offset = null_pos + 1

            f.seek(self.header.file_records_offset)
            self.file_records = []

            # Build ordered list of string values for sequential lookup
            # The DFPF format appears to map records to strings sequentially
            # (record i corresponds to string i in the name directory)
            ordered_names = []
            for str_pos, name in sorted(self.names.items()):
                ordered_names.append(name)

            for i in range(self.header.num_files):
                record_data = f.read(16)
                record = FileRecord(record_data, self.header.name_dir_offset, i)

                # Primary method: use sequential mapping (record i -> string i)
                # This works correctly for this DFPF format
                if i < len(ordered_names):
                    record.filename = ordered_names[i]
                elif record.name_position in self.names:
                    # Fallback: try position-based lookup
                    record.filename = self.names[record.name_position]
                else:
                    record.filename = f"file_{i:04d}_offset_{record.name_position}"

                if record.file_type_index < len(self.file_extensions):
                    record.extension = self.file_extensions[record.file_type_index]
                else:
                    record.extension = "bin"

                record.full_filename = f"{record.filename}.{record.extension}"
                self.file_records.append(record)

            print(f"Parsed {len(self.file_records)} file records")

    def extract_file(self, record: FileRecord, output_dir: Path) -> Path:
        output_path = output_dir / record.full_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Read data - use a larger buffer since record.size may be inaccurate
        # For compressed files, read up to max(uncompressed_size, record.size * 2) or 1MB
        read_size = max(record.size, min(record.uncompressed_size * 2, 1024 * 1024)) if record.size > 0 else 65536
        with open(self.data_path, "rb") as f:
            f.seek(record.offset)
            data = f.read(read_size)

        if record.compressed:
            if record.compression_type == COMPRESSION_ZLIB_V5:
                try:
                    # Use decompressobj to handle truncated/inaccurate size
                    decompressor = zlib.decompressobj(zlib.MAX_WBITS)
                    decompressed = decompressor.decompress(data)
                    actual_compressed = len(data) - len(decompressor.unused_data)

                    if len(decompressed) != record.uncompressed_size:
                        print(f"  Warning: Size mismatch for {record.full_filename}")
                    with open(output_path, "wb") as f:
                        f.write(decompressed)
                except zlib.error as e:
                    print(f"  Error decompressing {record.full_filename}: {e}")
                    # Try raw deflate as fallback
                    try:
                        decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
                        decompressed = decompressor.decompress(data)
                        with open(output_path, "wb") as f:
                            f.write(decompressed)
                    except Exception as e2:
                        print(f"  Second decompression attempt failed: {e2}")
                        with open(output_path, "wb") as f:
                            f.write(data)
            elif record.compression_type == COMPRESSION_XMEMCOMPRESS_XBOX:
                print(
                    f"  Warning: XMemCompress not implemented for {record.full_filename}"
                )
                with open(output_path, "wb") as f:
                    f.write(data)
            else:
                with open(output_path, "wb") as f:
                    f.write(data)
        else:
            with open(output_path, "wb") as f:
                f.write(data)

        return output_path

    def extract_all(self, output_dir: Optional[str] = None) -> List[Path]:
        if output_dir is None:
            output_dir = self.header_path.stem + "_extracted"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\nExtracting {len(self.file_records)} files to {output_path}")
        extracted = []

        for i, record in enumerate(self.file_records):
            if (i + 1) % 100 == 0 or i == 0:
                print(
                    f"  Extracting file {i + 1}/{len(self.file_records)}: {record.full_filename}"
                )

            try:
                path = self.extract_file(record, output_path)
                extracted.append(path)
            except Exception as e:
                print(f"  Error extracting {record.full_filename}: {e}")

        print(f"\nExtracted {len(extracted)} files to {output_path}")
        return extracted

    def find_file(self, filename: str) -> Optional[FileRecord]:
        filename_lower = filename.lower()
        for record in self.file_records:
            if (
                record.full_filename.lower() == filename_lower
                or record.filename.lower() == filename_lower
            ):
                return record
        return None

    def extract_by_name(
        self, filename: str, output_dir: Optional[str] = None
    ) -> Optional[Path]:
        record = self.find_file(filename)
        if record is None:
            print(f"File not found: {filename}")
            return None

        if output_dir is None:
            output_dir = self.header_path.stem + "_single"

        return self.extract_file(record, Path(output_dir))


def main():
    if len(sys.argv) < 2:
        search_paths = [
            Path("Win/Packs/00Startup.~h"),
            Path("../../../Win/Packs/00Startup.~h"),
            Path("brutal-legend-re/Win/Packs/00Startup.~h"),
        ]

        header_path = None
        for path in search_paths:
            if path.exists():
                header_path = path
                break

        if header_path is None:
            print("Usage: python dfpf_extract.py <header_file.~h> [output_dir]")
            print("\nPlease specify a .~h header file to extract.")
            sys.exit(1)
    else:
        header_path = Path(sys.argv[1])

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        extractor = DFPFExtractor(str(header_path))
        extractor.parse()

        proto_record = extractor.find_file("all.proto")
        if proto_record:
            print(f"\nFound all.proto! Extracting to separate directory...")
            proto_dir = "all_proto_extracted"
            path = extractor.extract_by_name("all.proto", proto_dir)
            if path:
                print(f"Extracted all.proto to: {path}")

        extracted = extractor.extract_all(output_dir)
        print("\nExtraction complete!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
