#!/usr/bin/env python3
"""
FSB Audio Extractor for Brutal Legend
Decrypts and decompresses FSB5 audio files from the game.

FSB5 format details:
- Magic: "FSB5" or "FSB4"
- Encryption key: "DFm3t4lFTW" (bytes: 44 46 6D 33 74 34 6C 46 54 57)
- Decryption: reverse bits of each byte, then XOR with key
- FSB5 header:
  - magic (4 bytes)
  - version (u32)
  - num_samples (u32)
  - sample_header_size (u32)
  - name_size (u32)
  - datasize (u32)
  - mode (u32)
"""

import struct
import zlib
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Encryption key: DFm3t4lFTW
FSB_KEY = bytes([0x44, 0x46, 0x6D, 0x33, 0x74, 0x34, 0x6C, 0x46, 0x54, 0x57])


class FSBFile:
    def __init__(self):
        self.filename: str = ""
        self.offset: int = 0
        self.size: int = 0
        self.channels: int = 2
        self.frequency: int = 44100
        self.codec: str = "MPEG"


class FSBExtractor:
    MAGIC_FSB5 = b"FSB5"
    MAGIC_FSB4 = b"FSB4"

    def __init__(self, fsb_path: str):
        self.fsb_path = Path(fsb_path)
        self.files: List[FSBFile] = []
        self.encrypted: bool = False
        self.version: str = ""
        self.num_samples: int = 0
        self.sample_header_size: int = 0
        self.name_size: int = 0
        self.datasize: int = 0
        self.mode: int = 0
        self.name_offset: int = 0
        self.header_data: bytes = b""
        self.decrypted_header: Optional[bytes] = None

    def reverse_bits_in_byte(self, input_byte: int) -> int:
        """Reverse the bits in a byte."""
        result = 0
        for _ in range(8):
            result = (result << 1) | (input_byte & 1)
            input_byte >>= 1
        return result

    def decrypt_bytes(self, data: bytes, key_offset: int = 0) -> bytes:
        """Decrypt FSB data using the FSB key."""
        result = bytearray(len(data))
        key_len = len(FSB_KEY)

        for i in range(len(data)):
            j = (key_offset + i) % key_len
            reversed_byte = self.reverse_bits_in_byte(data[i])
            result[i] = reversed_byte ^ FSB_KEY[j]

        return bytes(result)

    def is_encrypted(self, data: bytes) -> bool:
        """Check if the FSB file is encrypted."""
        return not (data[:4] == self.MAGIC_FSB5 or data[:4] == self.MAGIC_FSB4)

    def parse_header(self, data: bytes) -> None:
        """Parse FSB header from decrypted data."""
        if len(data) < 60:
            raise ValueError(f"Header too short: {len(data)} bytes")

        magic = data[:4]
        if magic not in (self.MAGIC_FSB5, self.MAGIC_FSB4):
            raise ValueError(f"Invalid FSB magic: {magic!r}")

        self.version = magic.decode('ascii')

        pos = 4
        version_num = struct.unpack("<I", data[pos:pos+4])[0]
        pos += 4

        self.num_samples = struct.unpack("<I", data[pos:pos+4])[0]
        pos += 4

        self.sample_header_size = struct.unpack("<I", data[pos:pos+4])[0]
        pos += 4

        self.name_size = struct.unpack("<I", data[pos:pos+4])[0]
        pos += 4

        self.datasize = struct.unpack("<I", data[pos:pos+4])[0]
        pos += 4

        self.mode = struct.unpack("<I", data[pos:pos+4])[0]
        pos += 4

        # Skip 32 bytes (hash and other stuff)
        pos += 32

        # Name offset: 60 + sample_header_size for FSB5
        if self.version == "FSB5":
            self.name_offset = 60 + self.sample_header_size
        else:  # FSB4
            self.name_offset = 48 + self.sample_header_size

        self.header_data = data

    def get_fsb5_offset(self, in_value: int) -> int:
        """Calculate FSB5 offset from encoded value."""
        return (in_value >> 7) * 0x20

    def parse_fsb5_files(self) -> None:
        """Parse FSB5 file entries."""
        pos = 60  # Start of sample headers

        for i in range(self.num_samples):
            if pos + 8 > len(self.header_data):
                break

            offset_raw = struct.unpack("<I", self.header_data[pos:pos+4])[0]
            samples = struct.unpack("<I", self.header_data[pos+4:pos+8])[0] >> 2

            file_type = offset_raw & 0x7F
            offset = self.get_fsb5_offset(offset_raw)
            channels = ((file_type >> 5) & 0x0F) + 1

            # Get frequency from type
            freq_type = (file_type >> 1) & 0x0F
            freq_table = [4000, 8000, 11000, 12000, 16000, 22050, 24000, 32000, 44100, 48000, 96000]
            frequency = freq_table[freq_type] if freq_type < len(freq_table) else 44100

            # Handle extra header data
            extra_type = file_type & 1
            extra_len = 0
            while extra_type and extra_len == 0:
                if pos + 8 > len(self.header_data):
                    break
                temp_dword = struct.unpack("<I", self.header_data[pos+8:pos+12])[0]
                extra_type = temp_dword & 1
                extra_len = (temp_dword & 0xFFFFFF) >> 1
                temp_dword_upper = temp_dword >> 24

                extra_pos = pos + 12
                if temp_dword_upper == 2:  # channels
                    channels = self.header_data[extra_pos]
                elif temp_dword_upper == 4:  # frequency
                    frequency = struct.unpack("<I", self.header_data[extra_pos:extra_pos+4])[0]
                elif temp_dword_upper == 6:  # unknown
                    pass
                elif temp_dword_upper == 20:  # xwma
                    pass

                pos += 4
                extra_pos = pos + extra_len

            pos += 8  # move past offset and samples

            # Get file size
            if pos + 4 <= len(self.header_data):
                size_raw = struct.unpack("<I", self.header_data[pos:pos+4])[0]
                if size_raw == 0:
                    size = self.datasize  # Fallback
                else:
                    size = self.get_fsb5_offset(size_raw) + (self.name_offset + self.name_size)
                    size = size - (self.name_offset + self.name_size + offset)
            else:
                size = self.datasize

            pos += 4

            # Get filename
            name_ptr_offset = self.name_offset + (i * 4)
            if name_ptr_offset + 4 <= len(self.header_data):
                name_offset_val = struct.unpack("<I", self.header_data[name_ptr_offset:name_ptr_offset+4])[0]
                name_pos = self.name_offset + self.name_size + name_offset_val

                # Read null-terminated string
                name_end = self.header_data.find(b'\x00', name_pos)
                if name_end == -1:
                    name_end = name_pos + 255
                filename = self.header_data[name_pos:name_end].decode('ascii', errors='replace')
            else:
                filename = f"audio_{i:04d}"

            fsb_file = FSBFile()
            fsb_file.filename = filename + ".mp3"
            fsb_file.offset = (self.name_offset + self.name_size) + offset
            fsb_file.size = size
            fsb_file.channels = channels
            fsb_file.frequency = frequency
            fsb_file.codec = "MPEG"

            self.files.append(fsb_file)

    def parse_fsb4_files(self) -> None:
        """Parse FSB4 file entries."""
        pos = 48  # Start of sample headers
        file_offset = 48 + self.sample_header_size

        for i in range(self.num_samples):
            if pos + 80 > len(self.header_data):
                break

            record_size = struct.unpack("<H", self.header_data[pos:pos+2])[0]
            pos += 2

            # Read filename (30 bytes)
            filename = self.header_data[pos:pos+30].decode('ascii', errors='replace').rstrip('\x00')
            pos += 30

            samples = struct.unpack("<I", self.header_data[pos:pos+4])[0]
            pos += 4

            size = struct.unpack("<I", self.header_data[pos:pos+4])[0]
            pos += 4

            # Skip loopstart and loopend (8 bytes)
            pos += 8

            mode = struct.unpack("<I", self.header_data[pos:pos+4])[0]
            pos += 4

            frequency = struct.unpack("<I", self.header_data[pos:pos+4])[0]
            pos += 4

            # Skip unused data (24 bytes)
            pos += 24

            if record_size > 80:
                pos += (record_size - 80)

            # Determine codec
            codec = "PCM16"
            if mode & 0x200:  # FSOUND_DELTA
                codec = "MPEG"

            # Get channels
            channels = 1
            if mode & 0x40:  # FSOUND_STEREO
                channels = 2

            # Get file extension
            ext = "WAV"
            if codec == "MPEG":
                ext = "MP3"

            fsb_file = FSBFile()
            fsb_file.filename = filename + "." + ext.lower()
            fsb_file.offset = file_offset
            fsb_file.size = size
            fsb_file.channels = channels
            fsb_file.frequency = frequency
            fsb_file.codec = codec

            if i == 0:
                file_offset = file_offset
            else:
                pass  # offset already set from previous

            file_offset += size

            self.files.append(fsb_file)

    def parse(self) -> None:
        """Parse the FSB file."""
        print(f"Parsing FSB: {self.fsb_path}")

        with open(self.fsb_path, 'rb') as f:
            raw_data = f.read()

        # Check if encrypted
        if self.is_encrypted(raw_data):
            print("File is encrypted, decrypting...")
            self.encrypted = True

            # Decrypt first 20 bytes to check magic
            decrypted_check = self.decrypt_bytes(raw_data[:20], 0)
            magic = decrypted_check[:4]

            if magic not in (self.MAGIC_FSB5, self.MAGIC_FSB4):
                raise ValueError(f"Decryption failed, invalid magic: {magic!r}")

            # Read more bytes to determine header size
            if magic == self.MAGIC_FSB5:
                # Read header sizes to calculate full header size
                pos = 12
                sample_header_size = struct.unpack("<I", decrypted_check[pos:pos+4])[0]
                pos += 4
                name_size = struct.unpack("<I", decrypted_check[pos:pos+4])[0]
                pos += 4
                header_size = 60 + sample_header_size + name_size
            else:  # FSB4
                pos = 8
                sample_header_size = struct.unpack("<I", decrypted_check[pos:pos+4])[0]
                header_size = 48 + sample_header_size

            # Decrypt full header
            self.decrypted_header = self.decrypt_bytes(raw_data[:header_size], 0)
        else:
            print("File is not encrypted")
            self.encrypted = False

            if raw_data[:4] == self.MAGIC_FSB5:
                pos = 12
                sample_header_size = struct.unpack("<I", raw_data[pos:pos+4])[0]
                pos += 4
                name_size = struct.unpack("<I", raw_data[pos:pos+4])[0]
                header_size = 60 + sample_header_size + name_size
            else:  # FSB4
                pos = 8
                sample_header_size = struct.unpack("<I", raw_data[pos:pos+4])[0]
                header_size = 48 + sample_header_size

            self.decrypted_header = raw_data[:header_size]

        self.parse_header(self.decrypted_header)

        if self.version == "FSB5":
            self.parse_fsb5_files()
        else:
            self.parse_fsb4_files()

        print(f"Found {len(self.files)} audio files")

    def extract_file(self, fsb_file: FSBFile, output_dir: Path) -> Path:
        """Extract a single audio file."""
        output_path = output_dir / fsb_file.filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.fsb_path, 'rb') as f:
            f.seek(fsb_file.offset)
            data = f.read(fsb_file.size)

        if self.encrypted:
            # Decrypt the audio data using its offset as key offset
            data = self.decrypt_bytes(data, fsb_file.offset)

        # Write the raw data (MPEG or PCM)
        with open(output_path, 'wb') as f:
            f.write(data)

        return output_path

    def extract_all(self, output_dir: Optional[str] = None) -> List[Path]:
        """Extract all audio files."""
        if output_dir is None:
            output_dir = self.fsb_path.stem + "_audio_extracted"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\nExtracting {len(self.files)} audio files to {output_path}")
        extracted = []

        for i, fsb_file in enumerate(self.files):
            if (i + 1) % 100 == 0 or i == 0:
                print(f"  Extracting file {i + 1}/{len(self.files)}: {fsb_file.filename}")

            try:
                path = self.extract_file(fsb_file, output_path)
                extracted.append(path)
            except Exception as e:
                print(f"  Error extracting {fsb_file.filename}: {e}")

        print(f"\nExtracted {len(extracted)} files to {output_path}")
        return extracted


def main():
    if len(sys.argv) < 2:
        print("Usage: python fsb_extract.py <fsb_file.fsb> [output_dir]")
        print()
        print("Example:")
        print("  python fsb_extract.py audio.fsb ./extracted_audio")
        sys.exit(1)

    fsb_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        extractor = FSBExtractor(fsb_path)
        extractor.parse()

        extracted = extractor.extract_all(output_dir)
        print("\nExtraction complete!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
