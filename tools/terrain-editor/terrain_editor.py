#!/usr/bin/env python3
"""
Brutal Legend Terrain Editor
============================
A tool for editing heightfield terrain data for Brutal Legend maps.

Commands:
  view        - Display heightfield data as text summary
  edit-height - Raise/lower terrain in a region by a delta value
  smooth      - Apply box blur to terrain region
  export-image - Export as PNG visualization

Heightfield Format:
- 40-byte custom header + DDS header + DXT5 compressed data
- DXT5 texture with 16-bit height values in alpha channel
- Block size: 4x4 pixels per block, 16 bytes per block
"""

import struct
import sys
import os
import argparse
from typing import Optional, Tuple, List

# Optional: Pillow for image export
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: Pillow not installed. Image export disabled.")

# Optional: numpy for numerical operations
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not installed. Using pure Python (slower).")


# Constants for DDS format
DDS_MAGIC = 0x20534444  # 'DDS '
DXT5_BLOCK_SIZE = 16  # 4x4 pixels per block
CUSTOM_HEADER_SIZE = 40
DDS_HEADER_SIZE = 124


class HeightfieldHeader:
    """Custom 40-byte header for Brutal Legend Heightfield files."""

    def __init__(self):
        self.metadata = bytes(8)
        self.type_marker = 0x0b
        self.unknown_0c = bytes(4)
        self.width_hint = 128
        self.height_hint = 128
        self.unknown_18 = bytes(8)
        self.texture_marker = 0x54787472  # 'rtxT'
        self.data_size = 0

    @staticmethod
    def parse(data: bytes) -> 'HeightfieldHeader':
        """Parse header from 40-byte buffer."""
        if len(data) < 40:
            raise ValueError(f"Header too short: {len(data)} bytes, need 40")

        hdr = HeightfieldHeader()
        hdr.metadata = data[0x00:0x08]
        hdr.type_marker = struct.unpack('<I', data[0x08:0x0C])[0]
        hdr.unknown_0c = data[0x0C:0x10]
        hdr.width_hint = struct.unpack('<I', data[0x10:0x14])[0]
        hdr.height_hint = struct.unpack('<I', data[0x14:0x18])[0]
        hdr.unknown_18 = data[0x18:0x20]
        hdr.texture_marker = struct.unpack('<I', data[0x20:0x24])[0]
        hdr.data_size = struct.unpack('<I', data[0x24:0x28])[0]
        return hdr

    def to_bytes(self) -> bytes:
        """Serialize header to 40 bytes."""
        out = bytearray(40)
        out[0x00:0x08] = self.metadata
        out[0x08:0x0C] = struct.pack('<I', self.type_marker)
        out[0x0C:0x10] = self.unknown_0c
        out[0x10:0x14] = struct.pack('<I', self.width_hint)
        out[0x14:0x18] = struct.pack('<I', self.height_hint)
        out[0x18:0x20] = self.unknown_18
        out[0x20:0x24] = struct.pack('<I', self.texture_marker)
        out[0x24:0x28] = struct.pack('<I', self.data_size)
        return bytes(out)

    def validate(self) -> bool:
        """Check header fields are valid for a heightfield DDS."""
        valid = True
        if self.type_marker != 0x0b:
            print(f"Warning: type_marker is 0x{self.type_marker:02X}, expected 0x0B")
            valid = False
        if self.texture_marker != 0x54787472:
            print(f"Warning: texture_marker is 0x{self.texture_marker:08X}, expected 0x54787472 ('rtxT')")
            valid = False
        return valid


def decode_dxt5_block(block: bytes) -> List[int]:
    """
    Decode DXT5 block (16 bytes) to 16 alpha values.
    DXT5 stores color in R5G6B5 and uses alpha channel for height.
    Returns list of 16 alpha values (0-255).
    """
    if len(block) < 16:
        raise ValueError(f"Block too short: {len(block)} bytes")

    alpha0 = block[0]
    alpha1 = block[1]

    # Build alpha interpolation table
    if alpha0 > alpha1:
        alpha_table = [
            alpha0,
            alpha1,
            (6*alpha0 + 1*alpha1) // 7,
            (5*alpha0 + 2*alpha1) // 7,
            (4*alpha0 + 3*alpha1) // 7,
            (3*alpha0 + 4*alpha1) // 7,
            (2*alpha0 + 5*alpha1) // 7,
            (1*alpha0 + 6*alpha1) // 7,
        ]
    else:
        alpha_table = [
            alpha0,
            alpha1,
            (4*alpha0 + 1*alpha1) // 5,
            (3*alpha0 + 2*alpha1) // 5,
            (2*alpha0 + 3*alpha1) // 5,
            (1*alpha0 + 4*alpha1) // 5,
            0,
            255,
        ]

    # Decode alpha indices (3 bits per pixel, 16 pixels)
    alpha_bits = struct.unpack('<Q', block[0:8])[0]
    alphas = []
    for i in range(16):
        idx = (alpha_bits >> (3 * i)) & 0x07
        alphas.append(alpha_table[idx])

    return alphas


def encode_dxt5_block(alphas: List[int]) -> bytes:
    """
    Encode 16 alpha values into a DXT5 block (16 bytes).
    Uses simple endpoint encoding.
    """
    if len(alphas) != 16:
        raise ValueError(f"Expected 16 alphas, got {len(alphas)}")

    # Find min/max alpha values as endpoints
    alpha0 = max(alphas)
    alpha1 = min(alphas)

    # Build interpolation table
    if alpha0 > alpha1:
        alpha_table = [
            alpha0,
            alpha1,
            (6*alpha0 + 1*alpha1) // 7,
            (5*alpha0 + 2*alpha1) // 7,
            (4*alpha0 + 3*alpha1) // 7,
            (3*alpha0 + 4*alpha1) // 7,
            (2*alpha0 + 5*alpha1) // 7,
            (1*alpha0 + 6*alpha1) // 7,
        ]
    else:
        alpha_table = [
            alpha0,
            alpha1,
            (4*alpha0 + 1*alpha1) // 5,
            (3*alpha0 + 2*alpha1) // 5,
            (2*alpha0 + 3*alpha1) // 5,
            (1*alpha0 + 4*alpha1) // 5,
            0,
            255,
        ]

    # Encode alpha indices
    alpha_bits = 0
    for i, a in enumerate(alphas):
        if a == alpha0:
            idx = 0
        elif a == alpha1:
            idx = 1
        else:
            best_dist = 256
            best_idx = 2
            for j in range(2, 8):
                dist = abs(a - alpha_table[j])
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j
            idx = best_idx
        alpha_bits |= (idx << (3 * i))

    # Color endpoints (placeholder - use first pixel's color)
    color0 = 0xFFFF  # R5G6B5 white
    color1 = 0x0000  # R5G6B5 black

    # Color indices (all same color for heightfield)
    color_bits = 0x55555555  # All index 1

    out = bytearray(16)
    struct.pack_into('<Q', out, 0, alpha_bits)
    struct.pack_into('<H', out, 8, color0)
    struct.pack_into('<H', out, 10, color1)
    struct.pack_into('<I', out, 12, color_bits)
    return bytes(out)


def decode_dxt5_texture(width: int, height: int, data: bytes) -> List[List[int]]:
    """
    Decode DXT5 texture to 2D heightmap (alpha channel as height).
    Returns heightmap as list of lists of integers (0-255).
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4

    heightmap = [[0] * width for _ in range(height)]

    for by in range(blocks_y):
        for bx in range(blocks_x):
            block_offset = (by * blocks_x + bx) * DXT5_BLOCK_SIZE
            if block_offset + DXT5_BLOCK_SIZE > len(data):
                break

            block = data[block_offset:block_offset + DXT5_BLOCK_SIZE]
            alphas = decode_dxt5_block(block)

            # Place 4x4 block into heightmap
            start_x = bx * 4
            start_y = by * 4
            for py in range(4):
                for px in range(4):
                    x = start_x + px
                    y = start_y + py
                    if x < width and y < height:
                        heightmap[y][x] = alphas[py * 4 + px]

    return heightmap


def encode_dxt5_texture(width: int, height: int, heightmap: List[List[int]]) -> bytes:
    """
    Encode heightmap into DXT5 texture.
    Takes 2D heightmap (list of lists of 0-255) and returns compressed DXT5 bytes.
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4

    output = bytearray()
    for by in range(blocks_y):
        for bx in range(blocks_x):
            # Extract 4x4 block alphas
            alphas = []
            for py in range(4):
                for px in range(4):
                    x = bx * 4 + px
                    y = by * 4 + py
                    if x < width and y < height:
                        alphas.append(heightmap[y][x])
                    else:
                        alphas.append(0)

            block = encode_dxt5_block(alphas)
            output.extend(block)

    return bytes(output)


class Heightfield:
    """
    Represents a Brutal Legend Heightfield DDS file.

    File structure:
    - 0x00-0x27: 40-byte custom header
    - 0x28-0x2B: 'DDS ' magic
    - 0x2C-0xA7: 124-byte DDS header
    - 0xA8+: DXT5 compressed data
    """

    DDS_OFFSET = 0x28
    DATA_OFFSET = 0xA8

    def __init__(self):
        self.custom_header = HeightfieldHeader()
        self.width = 128
        self.height = 128
        self.dxt5_data = b''
        self.extra_data = b''
        self.heightmap: List[List[int]] = []

    @classmethod
    def load(cls, filepath: str) -> 'Heightfield':
        """Load a heightfield DDS file."""
        hf = cls()

        try:
            with open(filepath, 'rb') as f:
                data = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Heightfield file not found: {filepath}")
        except IOError as e:
            raise IOError(f"Error reading heightfield: {e}")

        if len(data) < 0xA8:
            raise ValueError(f"File too small: {len(data)} bytes (expected at least 168)")

        # Parse custom header
        hf.custom_header = HeightfieldHeader.parse(data[0:CUSTOM_HEADER_SIZE])

        # Verify DDS magic
        dds_magic = struct.unpack('<I', data[0x28:0x2C])[0]
        if dds_magic != DDS_MAGIC:
            raise ValueError(f"Invalid DDS magic: 0x{dds_magic:08X}, expected 0x{DDS_MAGIC:08X} ('DDS ')")

        # Parse DDS header to get dimensions
        dds_flags = struct.unpack('<I', data[0x2C:0x30])[0]
        dds_height = struct.unpack('<I', data[0x30:0x34])[0]
        dds_width = struct.unpack('<I', data[0x34:0x38])[0]
        pf_flags = struct.unpack('<I', data[0x50:0x54])[0]
        pf_fourcc = struct.unpack('<I', data[0x54:0x58])[0]

        # Check for DXT5 format
        if pf_fourcc != 0x35545844:  # 'DXT5'
            raise ValueError(f"Only DXT5 format supported, got: 0x{pf_fourcc:08X}")

        hf.width = dds_width
        hf.height = dds_height

        # Calculate expected DXT5 data size
        blocks_x = (hf.width + 3) // 4
        blocks_y = (hf.height + 3) // 4
        expected_dxt5_size = blocks_x * blocks_y * DXT5_BLOCK_SIZE

        # Extract DXT5 data (use header data_size if available)
        if hf.custom_header.data_size > 0:
            dxt5_size = min(hf.custom_header.data_size, len(data) - cls.DATA_OFFSET)
        else:
            dxt5_size = min(expected_dxt5_size, len(data) - cls.DATA_OFFSET)

        hf.dxt5_data = data[cls.DATA_OFFSET:cls.DATA_OFFSET + dxt5_size]

        # Extra data after DXT5
        extra_offset = cls.DATA_OFFSET + len(hf.dxt5_data)
        if extra_offset < len(data):
            hf.extra_data = data[extra_offset:]

        # Decode heightmap
        hf.heightmap = decode_dxt5_texture(hf.width, hf.height, hf.dxt5_data)

        return hf

    def save(self, filepath: str):
        """Save heightfield to DDS file."""
        # Encode heightmap to DXT5
        self.dxt5_data = encode_dxt5_texture(self.width, self.height, self.heightmap)
        self.custom_header.data_size = len(self.dxt5_data)
        self.custom_header.width_hint = self.width
        self.custom_header.height_hint = self.height

        try:
            with open(filepath, 'wb') as f:
                # Write custom header (40 bytes)
                f.write(self.custom_header.to_bytes())

                # Write 'DDS ' magic
                f.write(b'DDS ')

                # Write DDS header (124 bytes)
                dds_header = bytearray(124)
                struct.pack_into('<I', dds_header, 0, 124)  # dwSize
                struct.pack_into('<I', dds_header, 4, 0x21007)  # dwFlags
                struct.pack_into('<I', dds_header, 8, self.height)  # dwHeight
                struct.pack_into('<I', dds_header, 12, self.width)  # dwWidth
                struct.pack_into('<I', dds_header, 16, 0)  # dwPitchOrLinearSize
                struct.pack_into('<I', dds_header, 20, 0)  # dwDepth
                struct.pack_into('<I', dds_header, 24, 1)  # dwMipMapCount
                # reserved1 (44 bytes of zeros) at offset 28
                struct.pack_into('<I', dds_header, 72, 32)  # pf.dwSize
                struct.pack_into('<I', dds_header, 76, 0x04 | 0x40000)  # pf.dwFlags (FOURCC)
                struct.pack_into('<I', dds_header, 80, 0x35545844)  # pf.dwFourCC ('DXT5')
                struct.pack_into('<I', dds_header, 84, 0)  # pf.dwRGBBitCount
                struct.pack_into('<I', dds_header, 88, 0)  # pf.dwRBitMask
                struct.pack_into('<I', dds_header, 92, 0)  # pf.dwGBitMask
                struct.pack_into('<I', dds_header, 96, 0)  # pf.dwBBitMask
                struct.pack_into('<I', dds_header, 100, 0xFF)  # pf.dwABitMask
                struct.pack_into('<I', dds_header, 108, 0x1000 | 0x04)  # dwCaps (COMPLEX | TEXTURE)
                struct.pack_into('<I', dds_header, 112, 0)  # dwCaps2
                struct.pack_into('<I', dds_header, 116, 0)  # dwCaps3
                struct.pack_into('<I', dds_header, 120, 0)  # dwCaps4
                f.write(dds_header)

                # Write DXT5 data
                f.write(self.dxt5_data)

                # Write extra data
                if self.extra_data:
                    f.write(self.extra_data)

        except IOError as e:
            raise IOError(f"Error saving heightfield: {e}")

    def get_stats(self) -> dict:
        """Calculate heightfield statistics."""
        if not self.heightmap:
            return {'min': 0, 'max': 0, 'avg': 0, 'width': self.width, 'height': self.height}

        min_h = 255
        max_h = 0
        total = 0
        count = 0

        for row in self.heightmap:
            for h in row:
                if h > 0:
                    min_h = min(min_h, h)
                    max_h = max(max_h, h)
                    total += h
                    count += 1

        if count == 0:
            return {'min': 0, 'max': 0, 'avg': 0, 'width': self.width, 'height': self.height}

        return {
            'min': min_h,
            'max': max_h,
            'avg': total / count,
            'width': self.width,
            'height': self.height
        }

    def edit_height_region(self, x1: int, y1: int, x2: int, y2: int, delta: int):
        """
        Raise or lower terrain in a rectangular region.

        Args:
            x1, y1: Top-left corner (inclusive)
            x2, y2: Bottom-right corner (exclusive)
            delta: Height change (+ve to raise, -ve to lower)
        """
        # Clamp coordinates
        x1 = max(0, min(x1, self.width))
        y1 = max(0, min(y1, self.height))
        x2 = max(0, min(x2, self.width))
        y2 = max(0, min(y2, self.height))

        if x1 >= x2 or y1 >= y2:
            print(f"Warning: Invalid region ({x1},{y1})-({x2},{y2}), skipping")
            return

        print(f"Editing region: ({x1},{y1}) to ({x2},{y2}), delta={delta}")

        for y in range(y1, y2):
            for x in range(x1, x2):
                new_h = self.heightmap[y][x] + delta
                self.heightmap[y][x] = max(0, min(255, new_h))

    def smooth_region(self, x1: int, y1: int, x2: int, y2: int, iterations: int = 1):
        """
        Apply box blur to a rectangular region.

        Args:
            x1, y1: Top-left corner (inclusive)
            x2, y2: Bottom-right corner (exclusive)
            iterations: Number of blur passes
        """
        # Clamp coordinates
        x1 = max(0, min(x1, self.width))
        y1 = max(0, min(y1, self.height))
        x2 = max(0, min(x2, self.width))
        y2 = max(0, min(y2, self.height))

        if x1 >= x2 or y1 >= y2:
            print(f"Warning: Invalid region ({x1},{y1})-({x2},{y2}), skipping")
            return

        print(f"Smoothing region: ({x1},{y1}) to ({x2},{y2}), iterations={iterations}")

        for _ in range(iterations):
            # Create copy for averaging
            smoothed = [row[:] for row in self.heightmap]

            for y in range(y1, y2):
                for x in range(x1, x2):
                    # Box blur: average of 3x3 neighborhood
                    sum_h = 0
                    count = 0
                    for ny in range(max(0, y-1), min(self.height, y+2)):
                        for nx in range(max(0, x-1), min(self.width, x+2)):
                            sum_h += self.heightmap[ny][nx]
                            count += 1
                    smoothed[y][x] = sum_h // count

            self.heightmap = smoothed

    def export_image(self, filepath: str):
        """Export heightfield as grayscale PNG image."""
        if not HAS_PIL:
            raise ImportError("Pillow not installed, cannot export image")

        # Normalize heightmap to 0-255
        stats = self.get_stats()
        img_data = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                h = self.heightmap[y][x]
                # Normalize based on min/max
                if stats['max'] > stats['min']:
                    normalized = int((h - stats['min']) / (stats['max'] - stats['min']) * 255)
                else:
                    normalized = h
                row.append(normalized)
            img_data.append(row)

        img = Image.new('L', (self.width, self.height))
        for y in range(self.height):
            for x in range(self.width):
                img.putpixel((x, y), img_data[y][x])

        img.save(filepath, 'PNG')
        print(f"Exported heightfield to {filepath}")


def validate_input_file(filepath: str) -> bool:
    """Check if file exists and appears to be a valid heightfield DDS."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return False

    if not filepath.endswith('.Heightfield'):
        print(f"Warning: File does not have .Heightfield extension: {filepath}")

    try:
        with open(filepath, 'rb') as f:
            data = f.read(0xA8)

        if len(data) < 0xA8:
            print(f"Error: File too small to be a valid heightfield: {len(data)} bytes")
            return False

        # Check for 'rtxT' marker at 0x20
        texture_marker = struct.unpack('<I', data[0x20:0x24])[0]
        if texture_marker != 0x54787472:
            print(f"Warning: 'rtxT' marker not found at offset 0x20")
            print(f"  Found: 0x{texture_marker:08X}")
            return False

        # Check for 'DDS ' magic at 0x28
        dds_magic = struct.unpack('<I', data[0x28:0x2C])[0]
        if dds_magic != DDS_MAGIC:
            print(f"Warning: 'DDS ' magic not found at offset 0x28")
            print(f"  Found: 0x{dds_magic:08X}")
            return False

        return True

    except IOError as e:
        print(f"Error reading file: {e}")
        return False


def cmd_view(args):
    """Display heightfield data as text summary."""
    if not validate_input_file(args.input):
        return 1

    print(f"\nLoading heightfield: {args.input}")
    print("-" * 50)

    try:
        hf = Heightfield.load(args.input)
    except Exception as e:
        print(f"Error loading heightfield: {e}")
        return 1

    stats = hf.get_stats()

    print(f"File: {args.input}")
    print(f"Dimensions: {stats['width']} x {stats['height']}")
    print(f"Min height: {stats['min']}")
    print(f"Max height: {stats['max']}")
    print(f"Avg height: {stats['avg']:.2f}")
    print(f"Custom header type marker: 0x{hf.custom_header.type_marker:02X}")
    print(f"Custom header width hint: {hf.custom_header.width_hint}")
    print(f"Custom header height hint: {hf.custom_header.height_hint}")
    print(f"DXT5 data size: {len(hf.dxt5_data)} bytes")
    print(f"Extra data size: {len(hf.extra_data)} bytes")

    # Show a small sample of the heightmap
    if args.verbose and hf.heightmap:
        print("\nHeightmap sample (top-left 8x8):")
        for y in range(min(8, hf.height)):
            row = []
            for x in range(min(8, hf.width)):
                row.append(f"{hf.heightmap[y][x]:3d}")
            print("  " + " ".join(row))

    print("-" * 50)
    return 0


def cmd_edit_height(args):
    """Raise or lower terrain in a region."""
    if not validate_input_file(args.input):
        return 1

    print(f"\nEditing heightfield: {args.input}")
    print("-" * 50)

    try:
        hf = Heightfield.load(args.input)
    except Exception as e:
        print(f"Error loading heightfield: {e}")
        return 1

    stats_before = hf.get_stats()
    print(f"Before: min={stats_before['min']}, max={stats_before['max']}, avg={stats_before['avg']:.2f}")

    # Apply height edit
    hf.edit_height_region(args.x1, args.y1, args.x2, args.y2, args.delta)

    stats_after = hf.get_stats()
    print(f"After: min={stats_after['min']}, max={stats_after['max']}, avg={stats_after['avg']:.2f}")

    # Save
    print(f"\nSaving to: {args.output}")
    try:
        hf.save(args.output)
        print("Save complete.")
    except Exception as e:
        print(f"Error saving heightfield: {e}")
        return 1

    # Optional export
    if args.export:
        try:
            hf.export_image(args.export)
        except Exception as e:
            print(f"Warning: Export failed: {e}")

    print("-" * 50)
    return 0


def cmd_smooth(args):
    """Apply box blur to terrain region."""
    if not validate_input_file(args.input):
        return 1

    print(f"\nSmoothing heightfield: {args.input}")
    print("-" * 50)

    try:
        hf = Heightfield.load(args.input)
    except Exception as e:
        print(f"Error loading heightfield: {e}")
        return 1

    stats_before = hf.get_stats()
    print(f"Before: min={stats_before['min']}, max={stats_before['max']}, avg={stats_before['avg']:.2f}")

    # Apply smoothing
    hf.smooth_region(args.x1, args.y1, args.x2, args.y2, args.iterations)

    stats_after = hf.get_stats()
    print(f"After: min={stats_after['min']}, max={stats_after['max']}, avg={stats_after['avg']:.2f}")

    # Save
    print(f"\nSaving to: {args.output}")
    try:
        hf.save(args.output)
        print("Save complete.")
    except Exception as e:
        print(f"Error saving heightfield: {e}")
        return 1

    print("-" * 50)
    return 0


def cmd_export_image(args):
    """Export heightfield as PNG visualization."""
    if not validate_input_file(args.input):
        return 1

    print(f"\nExporting heightfield: {args.input}")

    try:
        hf = Heightfield.load(args.input)
        hf.export_image(args.output)
    except Exception as e:
        print(f"Error exporting heightfield: {e}")
        return 1

    return 0


def main():
    """Main entry point with argparse CLI."""
    parser = argparse.ArgumentParser(
        description='Brutal Legend Terrain Editor - Edit heightfield terrain data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s view input.Heightfield
  %(prog)s edit-height input.Heightfield output.Heightfield --x1 0 --y1 0 --x2 64 --y2 64 --delta 20
  %(prog)s smooth input.Heightfield output.Heightfield --x1 32 --y1 32 --x2 96 --y2 96
  %(prog)s export-image input.Heightfield --output terrain.png
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # view command
    view_parser = subparsers.add_parser('view', help='Display heightfield data as text summary')
    view_parser.add_argument('input', help='Input .Heightfield file')
    view_parser.add_argument('--verbose', '-v', action='store_true', help='Show heightmap sample')

    # edit-height command
    edit_parser = subparsers.add_parser('edit-height', help='Raise/lower terrain in a region')
    edit_parser.add_argument('input', help='Input .Heightfield file')
    edit_parser.add_argument('output', help='Output .Heightfield file')
    edit_parser.add_argument('--x1', type=int, required=True, help='Top-left X coordinate')
    edit_parser.add_argument('--y1', type=int, required=True, help='Top-left Y coordinate')
    edit_parser.add_argument('--x2', type=int, required=True, help='Bottom-right X coordinate')
    edit_parser.add_argument('--y2', type=int, required=True, help='Bottom-right Y coordinate')
    edit_parser.add_argument('--delta', type=int, required=True, help='Height change (+/-)')
    edit_parser.add_argument('--export', help='Export result to PNG file')

    # smooth command
    smooth_parser = subparsers.add_parser('smooth', help='Apply box blur to terrain region')
    smooth_parser.add_argument('input', help='Input .Heightfield file')
    smooth_parser.add_argument('output', help='Output .Heightfield file')
    smooth_parser.add_argument('--x1', type=int, required=True, help='Top-left X coordinate')
    smooth_parser.add_argument('--y1', type=int, required=True, help='Top-left Y coordinate')
    smooth_parser.add_argument('--x2', type=int, required=True, help='Bottom-right X coordinate')
    smooth_parser.add_argument('--y2', type=int, required=True, help='Bottom-right Y coordinate')
    smooth_parser.add_argument('--iterations', type=int, default=1, help='Number of blur passes (default: 1)')

    # export-image command
    export_parser = subparsers.add_parser('export-image', help='Export as PNG visualization')
    export_parser.add_argument('input', help='Input .Heightfield file')
    export_parser.add_argument('--output', '-o', required=True, help='Output PNG file')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == 'view':
        return cmd_view(args)
    elif args.command == 'edit-height':
        return cmd_edit_height(args)
    elif args.command == 'smooth':
        return cmd_smooth(args)
    elif args.command == 'export-image':
        return cmd_export_image(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
