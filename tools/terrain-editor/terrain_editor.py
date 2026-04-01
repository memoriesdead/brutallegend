#!/usr/bin/env python3
"""
Brutal Legend Terrain Editor
============================
A terrain editor for creating and editing Brutal Legend maps.

Supports:
- Loading and decoding .Heightfield files
- Displaying terrain as 2D grayscale image
- Basic terrain painting (raise/lower)
- Saving back as .Heightfield format
- Stitching multiple tiles together
- Export to standard image formats

Heightfield Format:
- 40-byte custom header + DDS texture (128x128 DXT5)
- Width/Height: 128 pixels
- Format: DXT5 (GPU-compressed)
- Additional metadata after DDS data
"""

import struct
import os
import sys
from typing import Optional, Tuple, List
from dataclasses import dataclass
import argparse
import math

# Optional: Pillow for image display and export
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: Pillow not installed. Image display/export will be limited.")

# Optional: numpy for numerical operations
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not installed. Some features will be limited.")


# DDS Pixel Format Flags
DDPF_ALPHAPIXELS = 0x00000001
DDPF_FOURCC = 0x00000004
DDPF_RGB = 0x00000040

# DDS Header Flags
DDSD_CAPS = 0x00000001
DDSD_HEIGHT = 0x00000002
DDSD_WIDTH = 0x00000004
DDSD_PIXELFORMAT = 0x00001000
DDSD_MIPMAPCOUNT = 0x00020000
DDSD_LINEARSIZE = 0x00080000
DDSD_DEPTH = 0x00800000

# Known FourCC codes
FOURCC_DXT1 = b'DXT1'
FOURCC_DXT3 = b'DXT3'
FOURCC_DXT5 = b'DXT5'


@dataclass
class DDS_HEADER:
    """DDS file header

    Standard DDS header layout:
    - 0x00-0x03: size (124)
    - 0x04-0x07: flags
    - 0x08-0x0B: height
    - 0x0C-0x0F: width
    - 0x10-0x13: pitch/linear_size
    - 0x14-0x17: depth
    - 0x18-0x1B: mipmap_count
    - 0x1C-0x47: reserved1 (44 bytes, 11 DWORDs)
    - 0x48-0x4B: pf_size (32)
    - 0x4C-0x4F: pf_flags
    - 0x50-0x53: pf_four_cc ('DXT5')
    - 0x54-0x57: pf_rgb_bit_count
    - 0x58-0x5B: pf_r_bit_mask
    - 0x5C-0x5F: pf_g_bit_mask
    - 0x60-0x63: pf_b_bit_mask
    - 0x64-0x67: pf_a_bit_mask
    - 0x68-0x6B: caps
    - 0x6C-0x6F: caps2
    - 0x70-0x73: caps3
    - 0x74-0x77: caps4
    - 0x78-0x7B: reserved2
    Total: 124 bytes
    """
    size: int
    flags: int
    height: int
    width: int
    pitch_or_linear_size: int
    depth: int
    mip_map_count: int
    reserved1: bytes
    pf_size: int
    pf_flags: int
    pf_four_cc: int
    pf_rgb_bit_count: int
    pf_r_bit_mask: int
    pf_g_bit_mask: int
    pf_b_bit_mask: int
    pf_a_bit_mask: int
    caps: int
    caps2: int
    caps3: int
    caps4: int
    reserved2: int

    @staticmethod
    def from_bytes(data: bytes) -> 'DDS_HEADER':
        if len(data) < 116:
            raise ValueError(f"DDS header too short: {len(data)} bytes")

        offset = 0
        size = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        flags = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        height = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        width = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        pitch_or_linear_size = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        depth = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        mip_map_count = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        reserved1 = data[offset:offset+44]; offset += 44  # 11 DWORDs (44 bytes)

        pf_size = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        pf_flags = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        pf_four_cc = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        pf_rgb_bit_count = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        pf_r_bit_mask = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        pf_g_bit_mask = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        pf_b_bit_mask = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        pf_a_bit_mask = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4

        caps = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        caps2 = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        caps3 = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        caps4 = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
        reserved2 = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4

        return DDS_HEADER(
            size=size, flags=flags, height=height, width=width,
            pitch_or_linear_size=pitch_or_linear_size, depth=depth,
            mip_map_count=mip_map_count, reserved1=reserved1,
            pf_size=pf_size, pf_flags=pf_flags, pf_four_cc=pf_four_cc,
            pf_rgb_bit_count=pf_rgb_bit_count, pf_r_bit_mask=pf_r_bit_mask,
            pf_g_bit_mask=pf_g_bit_mask, pf_b_bit_mask=pf_b_bit_mask,
            pf_a_bit_mask=pf_a_bit_mask, caps=caps, caps2=caps2,
            caps3=caps3, caps4=caps4, reserved2=reserved2
        )

    def get_four_cc(self) -> bytes:
        """Get FourCC code as bytes"""
        return struct.pack('<I', self.pf_four_cc)

    def is_dxt5(self) -> bool:
        """Check if format is DXT5"""
        return self.pf_flags & DDPF_FOURCC and self.get_four_cc() == FOURCC_DXT5

    def is_dxt1(self) -> bool:
        """Check if format is DXT1"""
        return self.pf_flags & DDPF_FOURCC and self.get_four_cc() == FOURCC_DXT1


@dataclass
class HeightfieldHeader:
    """Custom header for Brutal Legend Heightfield files

    Layout based on analysis of extracted .Heightfield files:
    - 0x00-0x07: 8 bytes unknown metadata
    - 0x08-0x0b: 4 bytes type marker (typically 0x0b)
    - 0x0c-0x0f: 4 bytes unknown
    - 0x10-0x13: 4 bytes width hint (0x80 = 128)
    - 0x14-0x17: 4 bytes height hint (0x80 = 128)
    - 0x18-0x1f: 8 bytes unknown
    - 0x20-0x23: 4 bytes 'rtxT' marker
    - 0x24-0x27: 4 bytes data size (DXT5 data size)
    Total: 40 bytes

    NOTE: The 'DDS ' magic at 0x28 is NOT part of this header.
    """
    metadata: bytes  # 8 bytes: unknown metadata
    type_marker: int  # 4 bytes at 0x08: typically 0x0b
    unknown_0c: bytes  # 4 bytes at 0x0c: unknown
    width_hint: int  # 4 bytes at 0x10: 0x80 = 128
    height_hint: int  # 4 bytes at 0x14: 0x80 = 128
    unknown_18: bytes  # 8 bytes at 0x18: unknown
    texture_marker: int  # 4 bytes at 0x20: 'rtxT' (0x54787472)
    data_size: int  # 4 bytes at 0x24: size of DDS data

    @staticmethod
    def from_bytes(data: bytes) -> 'HeightfieldHeader':
        if len(data) < 40:
            raise ValueError(f"Heightfield header too short: {len(data)} bytes, need 40")

        return HeightfieldHeader(
            metadata=data[0x00:0x08],
            type_marker=struct.unpack('<I', data[0x08:0x0c])[0],
            unknown_0c=data[0x0c:0x10],
            width_hint=struct.unpack('<I', data[0x10:0x14])[0],
            height_hint=struct.unpack('<I', data[0x14:0x18])[0],
            unknown_18=data[0x18:0x20],
            texture_marker=struct.unpack('<I', data[0x20:0x24])[0],
            data_size=struct.unpack('<I', data[0x24:0x28])[0]
        )

    def validate(self) -> bool:
        """Validate header fields"""
        valid = True
        if self.type_marker != 0x0b:
            print(f"Warning: type_marker is 0x{self.type_marker:02x}, expected 0x0b")
            valid = False
        if self.width_hint != 128:
            print(f"Warning: width_hint is {self.width_hint}, expected 128")
            valid = False
        if self.height_hint != 128:
            print(f"Warning: height_hint is {self.height_hint}, expected 128")
            valid = False
        if self.texture_marker != 0x54787472:  # 'rtxT'
            print(f"Warning: texture_marker is 0x{self.texture_marker:08x}, expected 0x54787472 ('rtxT')")
            valid = False
        return valid


class DXT5Decompressor:
    """DXT5 texture decompressor for extracting height data"""

    @staticmethod
    def decompress_dxt5(block: bytes) -> List[Tuple[int, int, int, int]]:
        """
        Decompress a single DXT5 block (16 bytes) to 16 RGBA values.
        DXT5 YCoCg format stores height in Y channel.
        """
        if len(block) < 16:
            raise ValueError(f"DXT5 block too short: {len(block)} bytes")

        # DXT5 alpha block (8 bytes)
        alpha0 = block[0]
        alpha1 = block[1]

        # 8 alphas encoded in 3 bits each (stretched)
        alpha_table = [
            alpha0, alpha1,
            (6 * alpha0 + 1 * alpha1) // 7 if alpha0 > alpha1 else (4 * alpha0 + 1 * alpha1) // 5,
            (5 * alpha0 + 2 * alpha1) // 7 if alpha0 > alpha1 else (3 * alpha0 + 2 * alpha1) // 5,
            (4 * alpha0 + 3 * alpha1) // 7 if alpha0 > alpha1 else (2 * alpha0 + 3 * alpha1) // 5,
            (3 * alpha0 + 4 * alpha1) // 7 if alpha0 > alpha1 else (1 * alpha0 + 4 * alpha1) // 5,
            (2 * alpha0 + 5 * alpha1) // 7 if alpha0 > alpha1 else (1 * alpha0 + 3 * alpha1) // 4,
            (1 * alpha0 + 6 * alpha1) // 7 if alpha0 > alpha1 else (alpha1 if alpha0 > alpha1 else 0),
        ]

        # Decode alpha indices
        alpha_bits = struct.unpack('<Q', block[0:8])[0]
        alpha_indices = []
        for i in range(16):
            idx = (alpha_bits >> (3 * i)) & 0x07
            alpha_indices.append(alpha_table[idx])

        # DXT5 color block (8 bytes)
        c0 = struct.unpack('<H', block[8:10])[0]
        c1 = struct.unpack('<H', block[10:12])[0]

        # Extract RGB565 colors
        r0 = (c0 >> 11) * 255 // 31
        g0 = ((c0 >> 5) & 0x3F) * 255 // 63
        b0 = (c0 & 0x1F) * 255 // 31
        r1 = (c1 >> 11) * 255 // 31
        g1 = ((c1 >> 5) & 0x3F) * 255 // 63
        b1 = (c1 & 0x1F) * 255 // 31

        # Color lookup table
        if c0 > c1:
            color_table = [
                (r0, g0, b0),
                (r1, g1, b1),
                ((2*r0 + r1) // 3, (2*g0 + g1) // 3, (2*b0 + b1) // 3),
                ((r0 + 2*r1) // 3, (g0 + 2*g1) // 3, (b0 + 2*b1) // 3),
            ]
        else:
            color_table = [
                (r0, g0, b0),
                (r1, g1, b1),
                ((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2),
                (0, 0, 0),  # Transparent
            ]

        # Decode color indices
        color_bits = struct.unpack('<I', block[12:16])[0]
        pixels = []
        for i in range(16):
            idx = (color_bits >> (2 * i)) & 0x03
            r, g, b = color_table[idx]
            a = alpha_indices[i]
            pixels.append((r, g, b, a))

        return pixels

    @staticmethod
    def decompress_texture(width: int, height: int, data: bytes) -> bytes:
        """
        Decompress full DXT5 texture to RGBA.
        DXT5 stores data in 4x4 blocks.
        """
        if width % 4 != 0 or height % 4 != 0:
            raise ValueError(f"Dimensions must be multiples of 4: {width}x{height}")

        blocks_x = width // 4
        blocks_y = height // 4
        output = bytearray(width * height * 4)

        block_idx = 0
        for by in range(blocks_y):
            for bx in range(blocks_x):
                block_start = block_idx * 16
                block = data[block_start:block_start + 16]
                if len(block) < 16:
                    block = block + bytes(16 - len(block))

                pixels = DXT5Decompressor.decompress_dxt5(block)

                # Write pixels to output (4x4 block)
                for py in range(4):
                    for px in range(4):
                        x = bx * 4 + px
                        y = by * 4 + py
                        if x < width and y < height:
                            idx = (y * width + x) * 4
                            p = pixels[py * 4 + px]
                            output[idx] = p[0]      # R
                            output[idx + 1] = p[1]  # G
                            output[idx + 2] = p[2]  # B
                            output[idx + 3] = p[3]  # A

                block_idx += 1

        return bytes(output)

    @staticmethod
    def compress_texture_to_dxt5(width: int, height: int, rgba_data: bytes) -> bytes:
        """
        Compress RGBA texture to DXT5 format.
        Returns compressed data bytes.
        """
        if width % 4 != 0 or height % 4 != 0:
            raise ValueError(f"Dimensions must be multiples of 4: {width}x{height}")

        blocks_x = width // 4
        blocks_y = height // 4
        output = bytearray()

        for by in range(blocks_y):
            for bx in range(blocks_x):
                # Extract 4x4 block
                block_pixels = []
                for py in range(4):
                    for px in range(4):
                        x = bx * 4 + px
                        y = by * 4 + py
                        idx = (y * width + x) * 4
                        r = rgba_data[idx]
                        g = rgba_data[idx + 1]
                        b = rgba_data[idx + 2]
                        a = rgba_data[idx + 3]
                        block_pixels.append((r, g, b, a))

                # Compress block to DXT5
                compressed = DXT5Decompressor.compress_dxt5_block(block_pixels)
                output.extend(compressed)

        return bytes(output)

    @staticmethod
    def compress_dxt5_block(pixels: List[Tuple[int, int, int, int]]) -> bytes:
        """
        Compress 16 RGBA pixels to a DXT5 block.
        Uses YCoCg-like encoding where alpha is treated as height.
        """
        if len(pixels) != 16:
            raise ValueError(f"Expected 16 pixels, got {len(pixels)}")

        # DXT5 alpha block encoding
        alpha_values = [p[3] for p in pixels]
        alpha0 = max(alpha_values)
        alpha1 = min(alpha_values)

        # Sort and create alpha table
        if alpha0 == alpha1:
            alpha_table = [alpha0, alpha1] + [0] * 6
        else:
            mid = (alpha0 + alpha1) // 2
            alpha_table = [alpha0, alpha1, mid, mid, mid, mid, mid, mid]

        # Encode alpha block
        alpha_bits = 0
        for i, a in enumerate(alpha_values):
            # Find closest alpha in table (first 2 entries have priority)
            if a == alpha0:
                idx = 0
            elif a == alpha1:
                idx = 1
            else:
                # Find closest among remaining
                best_dist = 256
                best_idx = 0
                for j in range(2, 8):
                    dist = abs(a - alpha_table[j])
                    if dist < best_dist:
                        best_dist = dist
                        best_idx = j
                idx = best_idx
            alpha_bits |= (idx << (3 * i))

        alpha_block = struct.pack('<Q', alpha_bits)

        # DXT5 color block encoding (RGB565)
        r_values = [p[0] for p in pixels]
        g_values = [p[1] for p in pixels]
        b_values = [p[2] for p in pixels]

        # Use Y (green) channel as primary for height
        # Convert to RGB565
        def to_rgb565(r, g, b):
            r5 = r * 31 // 255
            g6 = g * 63 // 255
            b5 = b * 31 // 255
            return (r5 << 11) | (g6 << 5) | b5

        # Color selection based on luminance
        luma = [(0.299*p[0] + 0.587*p[1] + 0.114*p[2]) for p in pixels]
        sorted_indices = sorted(range(16), key=lambda i: luma[i])

        # Select corner colors
        c0_idx = sorted_indices[-1]
        c1_idx = sorted_indices[0]
        c0 = to_rgb565(*pixels[c0_idx][:3])
        c1 = to_rgb565(*pixels[c1_idx][:3])

        # Create color table
        r0 = (c0 >> 11) * 255 // 31
        g0 = ((c0 >> 5) & 0x3F) * 255 // 63
        b0 = (c0 & 0x1F) * 255 // 31
        r1 = (c1 >> 11) * 255 // 31
        g1 = ((c1 >> 5) & 0x3F) * 255 // 63
        b1 = (c1 & 0x1F) * 255 // 31

        if c0 > c1:
            color_table = [
                (r0, g0, b0),
                (r1, g1, b1),
                ((2*r0 + r1) // 3, (2*g0 + g1) // 3, (2*b0 + b1) // 3),
                ((r0 + 2*r1) // 3, (g0 + 2*g1) // 3, (b0 + 2*b1) // 3),
            ]
        else:
            color_table = [
                (r0, g0, b0),
                (r1, g1, b1),
                ((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2),
                (0, 0, 0),
            ]

        # Encode color indices
        color_bits = 0
        for i in range(16):
            p = pixels[i][:3]
            best_dist = 256 * 256
            best_idx = 0
            for j, ct in enumerate(color_table):
                dist = (p[0]-ct[0])**2 + (p[1]-ct[1])**2 + (p[2]-ct[2])**2
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j
            color_bits |= (best_idx << (2 * i))

        color_block = struct.pack('<I', color_bits)

        return alpha_block + struct.pack('<H', c0) + struct.pack('<H', c1) + color_block


class Heightfield:
    """Represents a Brutal Legend Heightfield file"""

    # File layout:
    # - 0x00-0x27: Custom header (40 bytes)
    # - 0x28-0x2B: 'DDS ' magic
    # - 0x2C-0xA7: DDS header structure (120 bytes without magic)
    # - 0xA8: DXT5 compressed data (approximately)
    HEADER_SIZE = 40
    DDS_HEADER_OFFSET = 0x2C  # DDS header structure starts here (after magic)
    DDS_HEADER_SIZE = 124     # DDS header structure size (without magic)
    DDS_DATA_OFFSET = 0xA8    # DXT5 data starts here

    def __init__(self):
        self.header: Optional[HeightfieldHeader] = None
        self.dds_header: Optional[DDS_HEADER] = None
        self.dxt5_data: Optional[bytes] = None
        self.extra_data: Optional[bytes] = None
        self.width: int = 128
        self.height: int = 128
        self.rgba_data: Optional[bytes] = None  # Decompressed RGBA

    @classmethod
    def load(cls, filepath: str) -> 'Heightfield':
        """Load a Heightfield file from disk"""
        hf = cls()

        with open(filepath, 'rb') as f:
            data = f.read()

        # File layout: 40-byte custom header + 128-byte DDS header + DXT5 data
        min_size = cls.HEADER_SIZE + cls.DDS_HEADER_SIZE
        if len(data) < min_size:
            raise ValueError(f"File too small: {len(data)} bytes, need at least {min_size}")

        # Parse custom header (40 bytes at 0x00)
        hf.header = HeightfieldHeader.from_bytes(data[0:cls.HEADER_SIZE])
        hf.header.validate()

        # Verify DDS magic at 0x28
        dds_magic = struct.unpack('<I', data[0x28:0x2C])[0]
        if dds_magic != 0x20534444:  # 'DDS '
            raise ValueError(f"Invalid DDS magic: 0x{dds_magic:08X}, expected 0x20534444 ('DDS ')")

        # Parse DDS header (128 bytes at 0x28, includes magic + structure)
        hf.dds_header = DDS_HEADER.from_bytes(data[cls.DDS_HEADER_OFFSET:cls.DDS_HEADER_OFFSET + cls.DDS_HEADER_SIZE])

        if not hf.dds_header.is_dxt5():
            raise ValueError(f"Only DXT5 format supported, found: {hf.dds_header.get_four_cc()}")

        hf.width = hf.dds_header.width
        hf.height = hf.dds_header.height

        # DXT5 data starts at 0xA8 = 168
        dds_data_offset = cls.DDS_DATA_OFFSET
        dds_data_size = hf.header.data_size

        if len(data) >= dds_data_offset + dds_data_size:
            hf.dxt5_data = data[dds_data_offset:dds_data_offset + dds_data_size]
            hf.extra_data = data[dds_data_offset + dds_data_size:]
        else:
            # Try to calculate DXT5 size
            expected_dxt5_size = ((hf.width + 3) // 4) * ((hf.height + 3) // 4) * 16
            hf.dxt5_data = data[dds_data_offset:dds_data_offset + expected_dxt5_size]
            hf.extra_data = data[dds_data_offset + expected_dxt5_size:]

        # Decompress DXT5 to RGBA
        hf.rgba_data = DXT5Decompressor.decompress_texture(hf.width, hf.height, hf.dxt5_data)

        return hf

    def save(self, filepath: str):
        """Save Heightfield to disk"""
        if self.rgba_data is None:
            raise ValueError("No RGBA data to save")

        # Compress RGBA to DXT5
        self.dxt5_data = DXT5Decompressor.compress_texture_to_dxt5(self.width, self.height, self.rgba_data)

        # Calculate sizes
        dxt5_size = len(self.dxt5_data)
        extra_size = len(self.extra_data) if self.extra_data else 0
        total_size = self.HEADER_SIZE + self.DDS_HEADER_SIZE + dxt5_size + extra_size

        # Ensure header values are set
        if self.header is None:
            self.header = HeightfieldHeader(
                metadata=bytes(8),
                type_marker=0x0b,
                unknown_0c=bytes(4),
                width_hint=self.width,
                height_hint=self.height,
                unknown_18=bytes(8),
                texture_marker=0x54787472,  # 'rtxT'
                data_size=dxt5_size
            )
        else:
            self.header.width_hint = self.width
            self.header.height_hint = self.height
            self.header.data_size = dxt5_size

        if self.dds_header is None:
            self.dds_header = DDS_HEADER(
                size=124,
                flags=DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT,
                height=self.height,
                width=self.width,
                pitch_or_linear_size=0,
                depth=0,
                mip_map_count=1,
                reserved1=bytes(44),
                pf_size=32,
                pf_flags=DDPF_ALPHAPIXELS | DDPF_FOURCC,
                pf_four_cc=struct.unpack('<I', FOURCC_DXT5)[0],
                pf_rgb_bit_count=0,
                pf_r_bit_mask=0,
                pf_g_bit_mask=0,
                pf_b_bit_mask=0,
                pf_a_bit_mask=0xFF,
                caps=DDSD_CAPS | DDSD_PIXELFORMAT,
                caps2=0,
                caps3=0,
                caps4=0,
                reserved2=0
            )

        # Write file
        with open(filepath, 'wb') as f:
            # Write custom header (40 bytes at offset 0x00)
            f.write(self.header.metadata)
            f.write(struct.pack('<I', self.header.type_marker))
            f.write(self.header.unknown_0c)
            f.write(struct.pack('<I', self.header.width_hint))
            f.write(struct.pack('<I', self.header.height_hint))
            f.write(self.header.unknown_18)
            f.write(struct.pack('<I', self.header.texture_marker))
            f.write(struct.pack('<I', self.header.data_size))

            # Write 'DDS ' magic at offset 0x28
            f.write(b'DDS ')

            # Write DDS header structure
            dds = self.dds_header
            f.write(struct.pack('<I', dds.size))
            f.write(struct.pack('<I', dds.flags))
            f.write(struct.pack('<I', dds.height))
            f.write(struct.pack('<I', dds.width))
            f.write(struct.pack('<I', dds.pitch_or_linear_size))
            f.write(struct.pack('<I', dds.depth))
            f.write(struct.pack('<I', dds.mip_map_count))
            f.write(dds.reserved1)
            f.write(struct.pack('<I', dds.pf_size))
            f.write(struct.pack('<I', dds.pf_flags))
            f.write(struct.pack('<I', dds.pf_four_cc))
            f.write(struct.pack('<I', dds.pf_rgb_bit_count))
            f.write(struct.pack('<I', dds.pf_r_bit_mask))
            f.write(struct.pack('<I', dds.pf_g_bit_mask))
            f.write(struct.pack('<I', dds.pf_b_bit_mask))
            f.write(struct.pack('<I', dds.pf_a_bit_mask))
            f.write(struct.pack('<I', dds.caps))
            f.write(struct.pack('<I', dds.caps2))
            f.write(struct.pack('<I', dds.caps3))
            f.write(struct.pack('<I', dds.caps4))
            f.write(struct.pack('<I', dds.reserved2))

            # Write DXT5 data
            f.write(self.dxt5_data)

            # Write extra data
            if self.extra_data:
                f.write(self.extra_data)

    def get_height_map(self) -> List[List[float]]:
        """Extract grayscale height values (0.0 to 1.0) from RGBA data"""
        if self.rgba_data is None:
            return []

        height_map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                idx = (y * self.width + x) * 4
                # Use alpha channel as height (per DXT5 YCoCg format)
                height = self.rgba_data[idx + 3] / 255.0
                row.append(height)
            height_map.append(row)

        return height_map

    def set_height_map(self, height_map: List[List[float]]):
        """Set height values from grayscale height map"""
        if len(height_map) != self.height or len(height_map[0]) != self.width:
            raise ValueError(f"Height map dimensions must be {self.height}x{self.width}")

        self.rgba_data = bytearray(self.width * self.height * 4)
        for y in range(self.height):
            for x in range(self.width):
                idx = (y * self.width + x) * 4
                h = int(height_map[y][x] * 255)
                h = max(0, min(255, h))
                self.rgba_data[idx] = h       # R
                self.rgba_data[idx + 1] = h   # G
                self.rgba_data[idx + 2] = h   # B
                self.rgba_data[idx + 3] = h   # A (height)

    def get_grayscale_image(self) -> 'Image.Image':
        """Get terrain as PIL grayscale image"""
        if not HAS_PIL:
            raise ImportError("Pillow is required for image conversion")

        height_map = self.get_height_map()
        img = Image.new('L', (self.width, self.height))
        for y in range(self.height):
            for x in range(self.width):
                pixel = int(height_map[y][x] * 255)
                img.putpixel((x, y), pixel)

        return img

    def apply_brush(self, cx: int, cy: int, radius: float, strength: float, mode: str = 'raise'):
        """
        Apply a brush stroke at (cx, cy) with given radius and strength.

        Args:
            cx: Center X coordinate
            cy: Center Y coordinate
            radius: Brush radius in pixels
            strength: Effect strength (0.0 to 1.0)
            mode: 'raise', 'lower', or 'smooth'
        """
        if self.rgba_data is None:
            return

        if mode not in ('raise', 'lower', 'smooth'):
            raise ValueError(f"Unknown mode: {mode}")

        height_map = self.get_height_map()
        new_height_map = [[h for h in row] for row in height_map]

        r2 = radius * radius
        for y in range(max(0, int(cy - radius)), min(self.height, int(cy + radius + 1))):
            for x in range(max(0, int(cx - radius)), min(self.width, int(cx + radius + 1))):
                dx = x - cx
                dy = y - cy
                dist2 = dx * dx + dy * dy
                if dist2 <= r2:
                    dist = math.sqrt(dist2)
                    falloff = 1.0 - (dist / radius)
                    factor = strength * falloff

                    if mode == 'raise':
                        new_height_map[y][x] = min(1.0, height_map[y][x] + factor)
                    elif mode == 'lower':
                        new_height_map[y][x] = max(0.0, height_map[y][x] - factor)
                    elif mode == 'smooth':
                        # Average with neighbors
                        neighbors = []
                        for ny in range(max(0, y-1), min(self.height, y+2)):
                            for nx in range(max(0, x-1), min(self.width, x+2)):
                                if (nx, ny) != (x, y):
                                    neighbors.append(height_map[ny][nx])
                        if neighbors:
                            avg = sum(neighbors) / len(neighbors)
                            new_height_map[y][x] = height_map[y][x] * (1 - factor) + avg * factor

        self.set_height_map(new_height_map)

    def flatten(self, x0: int, y0: int, x1: int, y1: int, target_height: float):
        """Flatten a rectangular region to target height"""
        height_map = self.get_height_map()

        x0 = max(0, min(x0, self.width - 1))
        y0 = max(0, min(y0, self.height - 1))
        x1 = max(0, min(x1, self.width))
        y1 = max(0, min(y1, self.height))

        for y in range(y0, y1):
            for x in range(x0, x1):
                height_map[y][x] = target_height

        self.set_height_map(height_map)

    def export_image(self, filepath: str, format: str = 'PNG'):
        """Export terrain as image file"""
        if not HAS_PIL:
            raise ImportError("Pillow is required for image export")

        img = self.get_grayscale_image()
        img.save(filepath, format=format)
        print(f"Exported terrain to {filepath}")


class TerrainTile:
    """Represents a terrain tile with coordinate information"""

    def __init__(self, x: int, y: int, heightfield: Optional[Heightfield] = None):
        self.x = x
        self.y = y
        self.heightfield = heightfield

    @property
    def coord_string(self) -> str:
        return f"x{self.x}/y{self.y}"


class TerrainWorld:
    """Manages a collection of terrain tiles"""

    def __init__(self):
        self.tiles: dict[Tuple[int, int], TerrainTile] = {}
        self.tile_size = 128

    def add_tile(self, tile: TerrainTile):
        """Add a tile to the world"""
        self.tiles[(tile.x, tile.y)] = tile

    def get_tile(self, x: int, y: int) -> Optional[TerrainTile]:
        """Get tile at coordinates"""
        return self.tiles.get((x, y))

    def load_tile(self, x: int, y: int, filepath: str) -> TerrainTile:
        """Load a tile from Heightfield file"""
        hf = Heightfield.load(filepath)
        tile = TerrainTile(x, y, hf)
        self.add_tile(tile)
        return tile

    def get_world_size(self) -> Tuple[int, int, int, int]:
        """Get world bounds: (min_x, min_y, max_x, max_y)"""
        if not self.tiles:
            return 0, 0, 0, 0

        xs = [t.x for t in self.tiles.values()]
        ys = [t.y for t in self.tiles.values()]
        return min(xs), min(ys), max(xs), max(ys)

    def stitch_tiles(self) -> Optional[Heightfield]:
        """
        Stitch all tiles together into a single heightfield.
        Returns combined Heightfield.
        """
        if not self.tiles:
            return None

        min_x, min_y, max_x, max_y = self.get_world_size()
        num_tiles_x = max_x - min_x + 1
        num_tiles_y = max_y - min_y + 1

        combined_width = num_tiles_x * self.tile_size
        combined_height = num_tiles_y * self.tile_size

        # Create combined heightfield
        combined = Heightfield()
        combined.width = combined_width
        combined.height = combined_height
        combined.rgba_data = bytearray(combined_width * combined_height * 4)

        # Place each tile
        for tile in self.tiles.values():
            if tile.heightfield is None or tile.heightfield.rgba_data is None:
                continue

            dest_x = (tile.x - min_x) * self.tile_size
            dest_y = (tile.y - min_y) * self.tile_size

            for y in range(self.tile_size):
                for x in range(self.tile_size):
                    src_idx = (y * self.tile_size + x) * 4
                    dest_idx = ((dest_y + y) * combined_width + dest_x + x) * 4
                    combined.rgba_data[dest_idx] = tile.heightfield.rgba_data[src_idx]
                    combined.rgba_data[dest_idx + 1] = tile.heightfield.rgba_data[src_idx + 1]
                    combined.rgba_data[dest_idx + 2] = tile.heightfield.rgba_data[src_idx + 2]
                    combined.rgba_data[dest_idx + 3] = tile.heightfield.rgba_data[src_idx + 3]

        return combined

    def export_stitched(self, filepath: str):
        """Export stitched world as image"""
        combined = self.stitch_tiles()
        if combined:
            combined.export_image(filepath)
            print(f"Exported stitched world ({combined.width}x{combined.height}) to {filepath}")


class TerrainEditor:
    """Interactive terrain editor with brush painting"""

    def __init__(self, heightfield: Optional[Heightfield] = None):
        self.heightfield = heightfield or Heightfield()
        self.modified = False
        self.current_brush_radius = 10.0
        self.current_brush_strength = 0.5
        self.current_mode = 'raise'

    def load_file(self, filepath: str):
        """Load Heightfield from file"""
        self.heightfield = Heightfield.load(filepath)
        self.modified = False
        print(f"Loaded {filepath} ({self.heightfield.width}x{self.heightfield.height})")

    def save_file(self, filepath: str):
        """Save Heightfield to file"""
        self.heightfield.save(filepath)
        self.modified = False
        print(f"Saved {filepath}")

    def paint(self, x: int, y: int):
        """Apply brush stroke at position"""
        self.heightfield.apply_brush(
            x, y,
            radius=self.current_brush_radius,
            strength=self.current_brush_strength,
            mode=self.current_mode
        )
        self.modified = True

    def set_brush(self, radius: float, strength: float):
        """Set brush parameters"""
        self.current_brush_radius = radius
        self.current_brush_strength = strength

    def export_image(self, filepath: str):
        """Export current terrain as image"""
        self.heightfield.export_image(filepath)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Brutal Legend Terrain Editor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s edit input.Heightfield output.Heightfield --brush-size 5 --raise
  %(prog)s visualize input.Heightfield
  %(prog)s load file.Heightfield
  %(prog)s show file.Heightfield
  %(prog)s paint file.Heightfield -x 64 -y 64 -r 10 -s 0.5 -m raise
  %(prog)s save file.Heightfield -o output.Heightfield
  %(prog)s export file.Heightfield -o terrain.png
  %(prog)s stitch dir/ -o stitched.png
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # edit command (primary use case)
    edit_parser = subparsers.add_parser('edit', help='Edit terrain with brush tool')
    edit_parser.add_argument('input', help='Input .Heightfield file')
    edit_parser.add_argument('output', help='Output .Heightfield file')
    edit_parser.add_argument('--brush-size', type=int, default=5, dest='brush_size',
                              help='Brush radius in pixels (default: 5)')
    edit_parser.add_argument('--strength', type=float, default=0.5,
                              help='Brush strength 0.0-1.0 (default: 0.5)')
    edit_parser.add_argument('--raise', action='store_true', dest='raise_mode',
                              help='Raise terrain (default)')
    edit_parser.add_argument('--lower', action='store_true', dest='lower_mode',
                              help='Lower terrain')
    edit_parser.add_argument('--smooth', action='store_true',
                              help='Smooth terrain')
    edit_parser.add_argument('--center', type=int, nargs=2, default=[64, 64], metavar=('X', 'Y'),
                              help='Brush center coordinates (default: 64 64)')
    edit_parser.add_argument('--export', metavar='FILE',
                              help='Export edited terrain to image file')

    # visualize command (primary use case)
    viz_parser = subparsers.add_parser('visualize', help='Visualize terrain')
    viz_parser.add_argument('file', help='Heightfield file to visualize')
    viz_parser.add_argument('--3d', action='store_true', help='Show 3D visualization')
    viz_parser.add_argument('--output', help='Save visualization to file')
    viz_parser.add_argument('--export', help='Export to image file')

    # load command
    load_parser = subparsers.add_parser('load', help='Load a Heightfield file')
    load_parser.add_argument('file', help='Heightfield file to load')

    # show command
    show_parser = subparsers.add_parser('show', help='Display terrain info')
    show_parser.add_argument('file', help='Heightfield file to show')

    # paint command
    paint_parser = subparsers.add_parser('paint', help='Paint terrain')
    paint_parser.add_argument('file', help='Heightfield file to paint')
    paint_parser.add_argument('-x', '--x', type=int, default=64, help='X coordinate')
    paint_parser.add_argument('-y', '--y', type=int, default=64, help='Y coordinate')
    paint_parser.add_argument('-r', '--radius', type=float, default=10.0, help='Brush radius')
    paint_parser.add_argument('-s', '--strength', type=float, default=0.5, help='Brush strength (0-1)')
    paint_parser.add_argument('-m', '--mode', choices=['raise', 'lower', 'smooth'], default='raise', help='Paint mode')

    # save command
    save_parser = subparsers.add_parser('save', help='Save a Heightfield file')
    save_parser.add_argument('file', help='Heightfield file to save')
    save_parser.add_argument('-o', '--output', required=True, help='Output file')

    # export command
    export_parser = subparsers.add_parser('export', help='Export terrain as image')
    export_parser.add_argument('file', help='Heightfield file to export')
    export_parser.add_argument('-o', '--output', required=True, help='Output image file')
    export_parser.add_argument('-f', '--format', default='PNG', help='Image format (PNG, TIF, JPG)')

    # stitch command
    stitch_parser = subparsers.add_parser('stitch', help='Stitch multiple tiles together')
    stitch_parser.add_argument('dir', help='Directory containing Heightfield files')
    stitch_parser.add_argument('-o', '--output', required=True, help='Output image file')
    stitch_parser.add_argument('--pattern', default='*.Heightfield', help='File pattern')

    args = parser.parse_args()

    if args.command == 'edit':
        # Primary edit command
        editor = TerrainEditor()
        editor.load_file(args.input)

        # Determine brush mode
        if args.smooth:
            mode = 'smooth'
        elif args.lower_mode:
            mode = 'lower'
        else:
            mode = 'raise'

        editor.set_brush(args.brush_size, args.strength)
        editor.current_mode = mode

        cx, cy = args.center
        editor.paint(cx, cy)

        editor.save_file(args.output)
        print(f"Edited terrain: {args.input} -> {args.output}")
        print(f"  Mode: {mode}, Brush size: {args.brush_size}, Strength: {args.strength}")
        print(f"  Center: ({cx}, {cy})")

        if args.export:
            editor.export_image(args.export)
            print(f"  Exported preview to: {args.export}")

    elif args.command == 'visualize':
        # Primary visualize command
        hf = Heightfield.load(args.file)
        print(f"Heightfield: {args.file}")
        print(f"  Dimensions: {hf.width}x{hf.height}")
        print(f"  DXT5 data size: {len(hf.dxt5_data)} bytes")

        if args.output or args.export:
            output_file = args.output or args.export
            hf.export_image(output_file)
            print(f"  Exported to: {output_file}")
        elif HAS_PIL:
            img = hf.get_grayscale_image()
            img.show()
            print(f"  Displaying grayscale preview...")

        if args._3d:
            try:
                import matplotlib.pyplot as plt
                from mpl_toolkits.mplot3d import Axes3D

                if HAS_NUMPY:
                    X, Y = np.meshgrid(range(hf.height), range(hf.width))
                    Z = np.array(hf.get_height_map())

                    fig = plt.figure(figsize=(12, 10))
                    ax = fig.add_subplot(111, projection='3d')
                    surf = ax.plot_surface(X, Y, Z, cmap='terrain', linewidth=0, antialiased=True)
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    ax.set_zlabel('Height')
                    ax.set_title(f'Brutal Legend Heightfield - {args.file}')
                    fig.colorbar(surf, shrink=0.5, aspect=5)
                    plt.show()
                    print(f"  Displaying 3D visualization...")
                else:
                    print("3D visualization requires numpy")
            except ImportError as e:
                print(f"Cannot create 3D visualization: {e}")

    elif args.command == 'load':
        editor = TerrainEditor()
        editor.load_file(args.file)
        print(f"Use 'show' command to view terrain details")

    elif args.command == 'show':
        hf = Heightfield.load(args.file)
        print(f"Heightfield: {args.file}")
        print(f"  Dimensions: {hf.width}x{hf.height}")
        print(f"  Type marker: 0x{hf.header.type_marker:02x}")
        print(f"  Width hint: {hf.header.width_hint}")
        print(f"  Height hint: {hf.header.height_hint}")
        print(f"  Texture marker: 0x{hf.header.texture_marker:08x} ('rtxT')")
        print(f"  Data size: {hf.header.data_size} bytes")
        print(f"  DDS format: {hf.dds_header.get_four_cc()}")
        print(f"  DXT5 data size: {len(hf.dxt5_data)} bytes")
        print(f"  Extra data size: {len(hf.extra_data)} bytes")

        if HAS_PIL:
            img = hf.get_grayscale_image()
            img.show()
            print(f"  Showing grayscale preview...")

    elif args.command == 'paint':
        editor = TerrainEditor()
        editor.load_file(args.file)
        editor.set_brush(args.radius, args.strength)
        editor.current_mode = args.mode
        editor.paint(args.x, args.y)

        # Save to same file
        editor.save_file(args.file)
        print(f"Painted at ({args.x}, {args.y}) with r={args.radius}, s={args.strength}, mode={args.mode}")

    elif args.command == 'save':
        hf = Heightfield.load(args.file)
        hf.save(args.output)
        print(f"Saved to {args.output}")

    elif args.command == 'export':
        hf = Heightfield.load(args.file)
        hf.export_image(args.output, args.format)

    elif args.command == 'stitch':
        import glob
        world = TerrainWorld()
        pattern = os.path.join(args.dir, args.pattern)
        files = glob.glob(pattern)

        for filepath in files:
            hf = Heightfield.load(filepath)
            idx = len(world.tiles)
            tile_x = idx % 10
            tile_y = idx // 10
            tile = TerrainTile(tile_x, tile_y, hf)
            world.add_tile(tile)

        world.export_stitched(args.output)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
