#!/usr/bin/env python3
"""
Brutal Legend Custom Map Pipeline
==================================
Creates custom map bundles for multiplayer testing.

This pipeline creates DFPF V5 bundles containing heightfield terrain data
with support for various terrain modification operations.

Usage:
    python custom_map_pipeline.py --map-name CustomTest --tile-x 100 --tile-y 100 \
        --operation raise --x 128 --y 128 --radius 40 --amount 80 \
        --operation smooth --factor 0.3

Operations:
    raise      --x X --y Y --radius R --amount A   Raise circular area
    lower      --x X --y Y --radius R --amount A   Lower circular area
    flatten    --x X --y Y --height H              Flatten area to height
    smooth     --factor F                          Apply smoothing
    set_all    --height H                         Set all heights

Output:
    Win/Mods/<MapName>.~h    (DFPF header file)
    Win/Mods/<MapName>.~p    (DFPF data file)
"""

import struct
import zlib
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Try to import numpy for faster processing
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

# Try to import PIL for image output
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ============================================================================
# CONSTANTS
# ============================================================================

# DFPF V5 compression types
COMPRESSION_UNCOMPRESSED_V5 = 4
COMPRESSION_ZLIB_V5 = 8

# Heightfield dimensions
HEIGHTFIELD_SIZE = 256

# DFPF file marker
DFPF_MAGIC = b"dfpf"
DFPF_VERSION = 5
DFPF_HEADER_SIZE = 88
DFPF_MARKER_VALUE = 0x23A1CEAB

# Custom header magic
HEIGHTFIELD_CUSTOM_MAGIC = b"rtxT"

# DDS constants
DDS_MAGIC = b"DDS "
DDS_HEADER_SIZE = 124


# ============================================================================
# DFPF CREATION
# ============================================================================

class FileRecord:
    """Represents a file record in the DFPF container."""
    def __init__(self):
        self.filename: str = ""
        self.extension: str = ""
        self.uncompressed_size: int = 0
        self.offset: int = 0
        self.size: int = 0
        self.file_type_index: int = 0
        self.compression_type: int = COMPRESSION_ZLIB_V5
        self.data: bytes = b''


class DFPFCreator:
    """Creates a DFPF V5 container from file data."""

    def __init__(self):
        self.file_extensions: List[str] = []
        self.records: List[FileRecord] = []

    def add_file(self, filename: str, extension: str, data: bytes, file_type_index: int = 0):
        """Add a file to the DFPF container."""
        record = FileRecord()
        record.filename = filename
        record.extension = extension
        record.file_type_index = file_type_index

        # Compress data if it compresses well
        if len(data) > 0:
            compressed = zlib.compress(data, 9)
            if len(compressed) < len(data):
                record.data = compressed
                record.compression_type = COMPRESSION_ZLIB_V5
                record.size = len(compressed)
            else:
                record.compression_type = COMPRESSION_UNCOMPRESSED_V5
                record.size = len(data)
                record.data = data
        else:
            record.compression_type = COMPRESSION_UNCOMPRESSED_V5
            record.size = 0

        record.uncompressed_size = len(data)
        self.records.append(record)

        # Add extension if not already present
        if extension not in self.file_extensions:
            self.file_extensions.append(extension)

    def _pack_file_record(self, record: FileRecord, name_offset: int) -> bytes:
        """Pack a file record into 16 bytes (V5 format).

        Verified decode formulas from extractor:
          uncompressed_size = raw_dword0 >> 8
          name_offset = raw_dword1 >> 11
          offset = raw_dword2 >> 3
          size = (raw_dword2 << 5) >> 9  (equivalent to raw_dword2 >> 4)
          file_type_index = ((raw_dword3 << 4) >> 24) >> 1
          compression_type = data[15] & 0x0F

        IMPORTANT: The original format encodes only offset in raw_dword2 (as offset << 3),
        and size is derived as offset >> 1 (NOT independently stored). The actual compressed
        size is determined by zlib stream boundaries, not by the size field.

        So we encode: raw_dword2 = sequential_offset << 3
        And size in header = sequential_offset >> 1 (derived, not actual compressed size)
        """
        raw_dword0 = record.uncompressed_size << 8
        raw_dword1 = name_offset << 11
        raw_dword2 = record.offset << 3  # Only offset is encoded (size is derived)
        raw_dword3 = (record.file_type_index << 20) | (record.compression_type & 0x0F)
        return struct.pack(">IIII", raw_dword0, raw_dword1, raw_dword2, raw_dword3)

    def save(self, output_path: str) -> Tuple[Path, Path]:
        """Save the DFPF container to .~h and .~p files."""
        out_path = Path(output_path)
        header_out = out_path.with_suffix(".~h")
        data_out = out_path.with_suffix(".~p")

        print(f"Creating DFPF container: {header_out}")

        # Build name directory
        name_dir = b''
        name_offsets: Dict[int, int] = {}

        for i, rec in enumerate(self.records):
            name_offsets[i] = len(name_dir)
            name_dir += rec.filename.encode('ascii') + b'\x00'

        name_dir_size = len(name_dir)

        # Calculate offsets
        header_fixed_size = 4 + 1 + 3 + self.HEADER_SIZE  # 96 bytes
        ext_table_size = len(self.file_extensions) * 16
        file_records_size = len(self.records) * 16

        file_ext_offset = header_fixed_size
        name_dir_offset = file_ext_offset + ext_table_size
        file_records_offset = name_dir_offset + name_dir_size

        # Build the .~p data file - write data SEQUENTIALLY
        # Original offsets may be garbage; we recalculate them based on actual data positions
        data_offsets = []  # Track new offset for each record
        with open(data_out, 'wb') as f:
            for rec in self.records:
                data_offsets.append(f.tell())
                f.write(rec.data)
            current_offset = f.tell()

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

            # File extension table (16 bytes per entry)
            for ext_name in self.file_extensions:
                ext_bytes = ext_name.encode('ascii')
                # Entry format: 4 bytes length + name_length bytes + padding to 16 bytes
                padding = 16 - (4 + len(ext_bytes))
                ext_entry = struct.pack(">I", len(ext_bytes)) + ext_bytes + b'\x00' * padding
                f.write(ext_entry)

            # Name directory
            f.write(name_dir)

            # File records (16 bytes each)
            # Update each record with its new sequential offset before packing
            for i, rec in enumerate(self.records):
                rec.offset = data_offsets[i]  # Use the new sequential offset
                rec_bytes = self._pack_file_record(rec, name_offsets[i])
                f.write(rec_bytes)

        print(f"Created {header_out} ({Path(header_out).stat().st_size} bytes)")
        print(f"Created {data_out} ({Path(data_out).stat().st_size} bytes)")

        return header_out, data_out

    MAGIC = DFPF_MAGIC
    VERSION = DFPF_VERSION
    HEADER_SIZE = DFPF_HEADER_SIZE
    MARKER_VALUE = DFPF_MARKER_VALUE


# ============================================================================
# HEIGHTFIELD CREATION AND MODIFICATION
# ============================================================================

def create_blank_heightfield() -> 'HeightfieldEditor':
    """Create a new blank heightfield (all zeros)."""
    return HeightfieldEditor(HEIGHTFIELD_SIZE, HEIGHTFIELD_SIZE)


def create_heightfield_with_base(height: float = 0.0) -> 'HeightfieldEditor':
    """Create a new heightfield with a flat base height."""
    editor = create_blank_heightfield()
    editor.fill(height)
    return editor


class HeightfieldEditor:
    """
    DDS Heightfield terrain editor for creating and modifying terrain.

    The heightfield uses DXT5 compression with height data stored in the
    alpha channel. Resolution is 256x256.
    """

    def __init__(self, width: int = HEIGHTFIELD_SIZE, height: int = HEIGHTFIELD_SIZE):
        self.width = width
        self.height = height

        if HAS_NUMPY:
            # Create heightmap array (Y,X order for image processing)
            self.heightmap = np.zeros((height, width), dtype=np.float32)
            # Create RGBA image for DXT5 encoding
            self.image = np.zeros((height, width, 4), dtype=np.uint8)
            self.image[:, :, 3] = 0  # Alpha channel
        else:
            self.heightmap = [[0.0 for _ in range(width)] for _ in range(height)]
            self.image = [[(0, 0, 0, 0) for _ in range(width)] for _ in range(height)]

        self.modified = True

    def get_height(self, x: int, y: int) -> float:
        """Get height at integer coordinates."""
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        if HAS_NUMPY:
            return float(self.heightmap[y, x])
        else:
            return float(self.heightmap[y][x])

    def set_height(self, x: int, y: int, height: float):
        """Set height at integer coordinates."""
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        height = max(0.0, min(255.0, height))

        if HAS_NUMPY:
            self.heightmap[y, x] = height
            self.image[y, x] = (128, 128, 128, int(height))  # Grayscale color
        else:
            self.heightmap[y][x] = height
            self.image[y][x] = (128, 128, 128, int(height))
        self.modified = True

    def fill(self, height: float):
        """Fill entire heightmap with a value."""
        height = max(0.0, min(255.0, height))

        if HAS_NUMPY:
            self.heightmap[:, :] = height
            self.image[:, :, 3] = int(height)
        else:
            for y in range(self.height):
                for x in range(self.width):
                    self.heightmap[y][x] = height
                    self.image[y][x] = (128, 128, 128, int(height))
        self.modified = True
        print(f"Filled heightmap with {height}")

    def raise_area(self, cx: int, cy: int, radius: int, amount: float):
        """Raise height in a circular area with smooth falloff."""
        if radius <= 0:
            return

        print(f"Raising area at ({cx}, {cy}) radius {radius} by {amount}")

        if HAS_NUMPY:
            # Create coordinate grids
            y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]
            # Calculate distances
            dist = np.sqrt((x_coords - cx)**2 + (y_coords - cy)**2)
            # Create falloff mask
            mask = dist <= radius
            falloff = np.maximum(0.0, 1.0 - (dist / radius)) * mask
            # Apply raise
            self.heightmap += amount * falloff
            self.heightmap = np.clip(self.heightmap, 0, 255)
            # Update image
            self.image[:, :, 3] = self.heightmap.astype(np.uint8)
        else:
            for y in range(max(0, cy - radius), min(self.height, cy + radius + 1)):
                for x in range(max(0, cx - radius), min(self.width, cx + radius + 1)):
                    dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
                    if dist <= radius:
                        falloff = 1.0 - (dist / radius)
                        new_height = self.heightmap[y][x] + amount * falloff
                        self.heightmap[y][x] = max(0.0, min(255.0, new_height))
                        self.image[y][x] = (128, 128, 128, int(self.heightmap[y][x]))
        self.modified = True

    def lower_area(self, cx: int, cy: int, radius: int, amount: float):
        """Lower height in a circular area."""
        self.raise_area(cx, cy, radius, -amount)

    def flatten(self, cx: int, cy: int, target_height: float, radius: int = 10):
        """Flatten area to target height with smooth falloff."""
        print(f"Flattening area at ({cx}, {cy}) to height {target_height} (radius={radius})")

        if HAS_NUMPY:
            y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]
            dist = np.sqrt((x_coords - cx)**2 + (y_coords - cy)**2)
            mask = dist <= radius
            falloff = np.maximum(0.0, 1.0 - (dist / radius)) * mask
            # Blend towards target height
            self.heightmap = self.heightmap * (1 - falloff) + target_height * falloff
            self.heightmap = np.clip(self.heightmap, 0, 255)
            self.image[:, :, 3] = self.heightmap.astype(np.uint8)
        else:
            for y in range(max(0, cy - radius), min(self.height, cy + radius + 1)):
                for x in range(max(0, cx - radius), min(self.width, cx + radius + 1)):
                    dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
                    if dist <= radius:
                        falloff = 1.0 - (dist / radius)
                        current = self.heightmap[y][x]
                        self.heightmap[y][x] = current * (1 - falloff) + target_height * falloff
                        self.heightmap[y][x] = max(0.0, min(255.0, self.heightmap[y][x]))
                        self.image[y][x] = (128, 128, 128, int(self.heightmap[y][x]))
        self.modified = True

    def smooth(self, factor: float = 0.5):
        """Apply smoothing to heightmap using simple averaging."""
        print(f"Applying smoothing (factor={factor})")

        if HAS_NUMPY:
            # Simple box blur
            h = self.heightmap.copy()
            smoothed = np.zeros_like(h)

            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    neighbors = [
                        h[y-1, x-1], h[y-1, x], h[y-1, x+1],
                        h[y, x-1],              h[y, x+1],
                        h[y+1, x-1], h[y+1, x], h[y+1, x+1],
                    ]
                    avg = sum(neighbors) / len(neighbors)
                    smoothed[y, x] = h[y, x] * (1 - factor) + avg * factor

            # Copy edges
            smoothed[0, :] = h[0, :]
            smoothed[-1, :] = h[-1, :]
            smoothed[:, 0] = h[:, 0]
            smoothed[:, -1] = h[:, -1]

            self.heightmap = smoothed
            self.image[:, :, 3] = self.heightmap.astype(np.uint8)
        else:
            h = [row[:] for row in self.heightmap]
            smoothed = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    neighbors = [
                        h[y-1][x-1], h[y-1][x], h[y-1][x+1],
                        h[y][x-1],              h[y][x+1],
                        h[y+1][x-1], h[y+1][x], h[y+1][x+1],
                    ]
                    avg = sum(neighbors) / len(neighbors)
                    smoothed[y][x] = h[y][x] * (1 - factor) + avg * factor

            # Copy edges
            for x in range(self.width):
                smoothed[0][x] = h[0][x]
                smoothed[self.height-1][x] = h[self.height-1][x]
            for y in range(self.height):
                smoothed[y][0] = h[y][0]
                smoothed[y][self.width-1] = h[y][self.width-1]

            self.heightmap = smoothed
            for y in range(self.height):
                for x in range(self.width):
                    self.image[y][x] = (128, 128, 128, int(self.heightmap[y][x]))
        self.modified = True

    def get_stats(self) -> Dict[str, Any]:
        """Get heightmap statistics."""
        if HAS_NUMPY:
            return {
                'min': float(self.heightmap.min()),
                'max': float(self.heightmap.max()),
                'mean': float(self.heightmap.mean()),
                'width': self.width,
                'height': self.height,
            }
        else:
            flat = [h for row in self.heightmap for h in row]
            return {
                'min': min(flat),
                'max': max(flat),
                'mean': sum(flat) / len(flat) if flat else 0,
                'width': self.width,
                'height': self.height,
            }

    def show(self):
        """Display heightmap info."""
        stats = self.get_stats()
        print(f"=== Heightfield Editor ===")
        print(f"Dimensions: {self.width}x{self.height}")
        print(f"Height range: {stats['min']:.2f} - {stats['max']:.2f}")
        print(f"Mean height: {stats['mean']:.2f}")


# ============================================================================
# DXT5 ENCODING/DECODING
# ============================================================================

def encode_dxt5_block(pixels: List[Tuple[int, int, int, int]]) -> bytes:
    """Encode 16 RGBA pixels into a DXT5 block (16 bytes)."""
    if len(pixels) != 16:
        raise ValueError(f"DXT5 block must have 16 pixels, got {len(pixels)}")

    # Extract alpha values
    alpha_values = [int(p[3]) for p in pixels]

    # Find alpha endpoints
    sorted_alpha = sorted(set(alpha_values))
    if len(sorted_alpha) >= 2:
        alpha0 = sorted_alpha[-1]
        alpha1 = sorted_alpha[0]
    else:
        alpha0 = sorted_alpha[0] if sorted_alpha else 255
        alpha1 = alpha0

    # Build alpha table
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

    # Map alpha to indices
    alpha_indices = 0
    for i, a in enumerate(alpha_values):
        best_idx = 0
        best_dist = 256
        for idx, tab_a in enumerate(alpha_table):
            dist = abs(tab_a - a)
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
        alpha_indices |= (best_idx & 0x07) << (3 * i)

    # Extract color values
    r_values = [int(p[0]) for p in pixels]
    g_values = [int(p[1]) for p in pixels]
    b_values = [int(p[2]) for p in pixels]

    def to_r5g6b5(r, g, b):
        r5 = (int(r) * 31) // 255
        g6 = (int(g) * 63) // 255
        b5 = (int(b) * 31) // 255
        return (r5 << 11) | (g6 << 5) | b5

    color_values = [to_r5g6b5(r, g, b) for r, g, b in zip(r_values, g_values, b_values)]

    # Find color endpoints
    sorted_colors = sorted(set(color_values))
    if len(sorted_colors) >= 2:
        color0_raw = sorted_colors[-1]
        color1_raw = sorted_colors[0]
    else:
        color0_raw = sorted_colors[0] if sorted_colors else 0
        color1_raw = color0_raw

    r0 = (color0_raw >> 11) & 0x1F
    g0 = (color0_raw >> 5) & 0x3F
    b0 = color0_raw & 0x1F

    r1 = (color1_raw >> 11) & 0x1F
    g1 = (color1_raw >> 5) & 0x3F
    b1 = color1_raw & 0x1F

    r0_8 = (r0 * 255) // 31
    g0_8 = (g0 * 255) // 63
    b0_8 = (b0 * 255) // 31

    r1_8 = (r1 * 255) // 31
    g1_8 = (g1 * 255) // 63
    b1_8 = (b1 * 255) // 31

    if color0_raw >= color1_raw:
        color_table = [
            (r0_8, g0_8, b0_8),
            (r1_8, g1_8, b1_8),
            ((2*r0_8 + 1*r1_8) // 3, (2*g0_8 + 1*g1_8) // 3, (2*b0_8 + 1*b1_8) // 3),
            ((1*r0_8 + 2*r1_8) // 3, (1*g0_8 + 2*g1_8) // 3, (1*b0_8 + 2*b1_8) // 3),
        ]
    else:
        color_table = [
            (r0_8, g0_8, b0_8),
            (r1_8, g1_8, b1_8),
            ((r0_8 + r1_8) // 2, (g0_8 + g1_8) // 2, (b0_8 + b1_8) // 2),
            (0, 0, 0),
        ]

    # Map colors to indices
    color_indices = 0
    for i, (r, g, b) in enumerate(zip(r_values, g_values, b_values)):
        c = to_r5g6b5(r, g, b)
        best_idx = 0
        best_dist = 256 * 256
        for idx, tab_c in enumerate(color_table):
            tab_r, tab_g, tab_b = tab_c
            dist = (tab_r - r)**2 + (tab_g - g)**2 + (tab_b - b)**2
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
        color_indices |= (best_idx & 0x03) << (2 * i)

    # Pack the block
    block = bytearray(16)
    block[0] = alpha0
    block[1] = alpha1
    block[2] = alpha_indices & 0xFF
    block[3] = (alpha_indices >> 8) & 0xFF
    block[4] = (alpha_indices >> 16) & 0xFF
    block[5] = (alpha_indices >> 24) & 0xFF
    block[6] = (alpha_indices >> 32) & 0xFF
    block[7] = (alpha_indices >> 40) & 0xFF
    struct.pack_into('<H', block, 8, color0_raw)
    struct.pack_into('<H', block, 10, color1_raw)
    struct.pack_into('<I', block, 12, color_indices)

    return bytes(block)


def encode_dxt5_image(width: int, height: int, image) -> bytes:
    """Encode image into DXT5 compressed data."""
    if width < 4:
        width = 4
    if height < 4:
        height = 4

    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4

    dxt5_data = bytearray()

    for block_y in range(blocks_y):
        for block_x in range(blocks_x):
            pixels = []
            for py in range(4):
                for px in range(4):
                    x = block_x * 4 + px
                    y = block_y * 4 + py
                    if x < width and y < height:
                        if HAS_NUMPY:
                            pixel = tuple(image[y, x])
                        else:
                            pixel = tuple(image[y][x])
                    else:
                        pixel = (0, 0, 0, 0)
                    pixels.append(pixel)

            block = encode_dxt5_block(pixels)
            dxt5_data.extend(block)

    return bytes(dxt5_data)


# ============================================================================
# HEIGHTFIELD FILE CREATION
# ============================================================================

def create_heightfield_file(editor: HeightfieldEditor) -> bytes:
    """
    Create a complete heightfield file with 40-byte custom header + DDS header + DXT5 data.

    Format:
    - 40-byte custom header (rtxT magic at offset 0x20)
    - 4-byte "DDS " magic
    - 124-byte DDS header
    - DXT5 compressed image data

    Total header = 40 + 4 + 124 = 168 bytes (0xA8)
    """
    # Encode the heightmap as DXT5
    dxt5_data = encode_dxt5_image(editor.width, editor.height, editor.image)

    # Build the file
    file_data = bytearray()

    # 40-byte custom header
    custom_header = bytearray(40)

    # Offset 0x00-0x10: unknown metadata (zeros)
    # Offset 0x10: width hint
    struct.pack_into('<I', custom_header, 0x10, editor.width)
    # Offset 0x14: height hint
    struct.pack_into('<I', custom_header, 0x14, editor.height)
    # Offset 0x18: flags
    struct.pack_into('<I', custom_header, 0x18, 0x08)  # DDS standard flags
    # Offset 0x1C: more flags
    struct.pack_into('<I', custom_header, 0x1C, 0x04)
    # Offset 0x20: magic "rtxT"
    custom_header[0x20:0x24] = HEIGHTFIELD_CUSTOM_MAGIC
    # Offset 0x24: data size (size of DXT5 data)
    struct.pack_into('<I', custom_header, 0x24, len(dxt5_data))
    # Offset 0x28: DDS magic "DDS " (written later with full DDS header)

    file_data.extend(custom_header)

    # DDS magic "DDS "
    file_data.extend(DDS_MAGIC)

    # DDS header (124 bytes)
    # Using 128 bytes to allow safe writing at offset 124
    dds_header = bytearray(128)

    # dwSize
    struct.pack_into('<I', dds_header, 0, DDS_HEADER_SIZE)
    # dwFlags (DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_LINEARSIZE)
    struct.pack_into('<I', dds_header, 4, 0x1F008)
    # dwHeight
    struct.pack_into('<I', dds_header, 8, editor.height)
    # dwWidth
    struct.pack_into('<I', dds_header, 12, editor.width)
    # dwPitchOrLinearSize
    struct.pack_into('<I', dds_header, 16, 0)
    # dwDepth
    struct.pack_into('<I', dds_header, 20, 0)
    # dwMipMapCount
    struct.pack_into('<I', dds_header, 24, 0)
    # dwReserved1 (11 DWORDs) - offsets 28-72 are zeros
    # pixelFormat at offset 72 (after dwReserved1[11] = 44 bytes)
    pf_offset = 72
    # pf.dwSize
    struct.pack_into('<I', dds_header, pf_offset, 32)
    # pf.dwFlags (DDPF_ALPHAPIXELS | DDPF_FOURCC for DXT5)
    struct.pack_into('<I', dds_header, pf_offset + 4, 0x40)
    # pf.dwFourCC (DXT5 = "DXT5")
    dds_header[pf_offset + 8:pf_offset + 12] = b'DXT5'
    # pf.dwRGBBitCount (0 for compressed)
    struct.pack_into('<I', dds_header, pf_offset + 12, 0)
    # pf.dwRBitMask
    struct.pack_into('<I', dds_header, pf_offset + 16, 0)
    # pf.dwGBitMask
    struct.pack_into('<I', dds_header, pf_offset + 20, 0)
    # pf.dwBBitMask
    struct.pack_into('<I', dds_header, pf_offset + 24, 0)
    # pf.dwABitMask (0xFF for DXT5 alpha)
    struct.pack_into('<I', dds_header, pf_offset + 28, 0xFF)

    # dwCaps at offset 108 (72 + 32 + 4)
    struct.pack_into('<I', dds_header, 108, 0x1000)  # DDSCAPS_TEXTURE
    # dwCaps2
    struct.pack_into('<I', dds_header, 112, 0)
    # dwCaps3
    struct.pack_into('<I', dds_header, 116, 0)
    # dwCaps4
    struct.pack_into('<I', dds_header, 120, 0)
    # dwReserved2
    struct.pack_into('<I', dds_header, 124, 0)

    # Only use first 124 bytes of the DDS header
    file_data.extend(dds_header[:124])

    # DXT5 compressed data
    file_data.extend(dxt5_data)

    return bytes(file_data)


# ============================================================================
# SUPPORTING FILE CREATION
# ============================================================================

def create_height_bin() -> bytes:
    """Create a minimal height.bin file (HSEM format)."""
    header = bytearray()

    # hsem magic
    header.extend(b'hsem')
    # Unknown 4 bytes
    header.extend(struct.pack('>I', 0x00000000))
    # Scale floats
    header.extend(struct.pack('>f', 1.27))
    header.extend(struct.pack('>f', 0.897))
    # Height range
    header.extend(struct.pack('>f', 0.0))
    header.extend(struct.pack('>f', 100.0))
    # More floats
    header.extend(struct.pack('>f', 0.0))
    header.extend(struct.pack('>f', 0.0))
    # lrtm magic
    header.extend(b'lrtm')
    # Version
    header.extend(struct.pack('>I', 0x01000000))
    # Count (46 entries)
    header.extend(struct.pack('>I', 0x0000002E))

    # Material string
    mat_string = b'environments/materials/terrain/rock_sand\x00'
    header.extend(mat_string)

    # Pad to 0x70 for BVXD marker
    while len(header) < 0x70:
        header.append(0)

    # BVXD marker
    header.extend(b'BVXD')
    header.extend(struct.pack('>I', 0x02000000))
    header.extend(struct.pack('>I', 0x00000000))

    # BIXD marker
    header.extend(b'BIXD')

    # Data section: 16x16 grid of material indices
    data = bytearray()
    for y in range(16):
        for x in range(16):
            idx = 0x0400 + ((x + y) % 16) * 16
            data.extend(struct.pack('>H', idx))

    return bytes(header) + bytes(data)


def create_blend_bin() -> bytes:
    """Create a minimal blend.bin file."""
    header = bytearray()

    header.extend(b'hsem')
    header.extend(struct.pack('>I', 0x00000000))
    header.extend(struct.pack('>f', 1.0))
    header.extend(struct.pack('>f', 1.0))
    header.extend(struct.pack('>f', 0.0))
    header.extend(struct.pack('>f', 255.0))
    header.extend(struct.pack('>f', 0.0))
    header.extend(struct.pack('>f', 0.0))
    header.extend(b'lrtm')
    header.extend(struct.pack('>I', 0x01000000))
    header.extend(struct.pack('>I', 0x00000002))

    # Material strings
    mat1 = b'environments/terrainmaterials/sandbeach\x00'
    mat2 = b'environments/terrainmaterials/introrockcliff\x00'
    header.extend(mat1)
    header.extend(mat2)

    while len(header) < 0x70:
        header.append(0)

    header.extend(b'BVXD')
    header.extend(struct.pack('>I', 0x02000000))
    header.extend(struct.pack('>I', 0x00000000))
    header.extend(b'BIXD')

    data = bytearray()
    for y in range(16):
        for x in range(16):
            idx = 0x0001 if (x + y) % 2 == 0 else 0x0002
            data.extend(struct.pack('>H', idx))

    return bytes(header) + bytes(data)


def create_blend_texture(tile_x: int, tile_y: int, world_name: str) -> bytes:
    """Create a blend.Texture metadata file."""
    data = bytearray()

    data.extend(struct.pack('<I', 0x00000001))
    data.extend(struct.pack('<I', 4))
    data.extend(struct.pack('<I', 0x3F800000))
    data.extend(struct.pack('<I', 0x00000025))

    blend_path = f"worlds/{world_name}/tile/x{tile_x}/y{tile_y}/blend"
    data.extend(blend_path.encode('ascii') + b'\x00')

    occlusion_path = f"worlds/{world_name}/tile/x{tile_x}/y{tile_y}/occlusion"
    occ_bytes = occlusion_path.encode('ascii') + b'\x00'
    data.extend(struct.pack('<I', len(occ_bytes)))
    data.extend(occ_bytes)

    data.extend(struct.pack('<I', 1))

    mat1_path = "environments/terrainmaterials/sandbeach"
    mat1_bytes = mat1_path.encode('ascii') + b'\x00'
    data.extend(struct.pack('<I', len(mat1_bytes)))
    data.extend(mat1_bytes)

    return bytes(data)


def create_occlusion_texture(tile_x: int, tile_y: int, world_name: str) -> bytes:
    """Create an occlusion.Texture metadata file."""
    data = bytearray()

    data.extend(struct.pack('<I', 0x00000001))
    data.extend(struct.pack('<I', 4))
    data.extend(struct.pack('<I', 0x3F800000))
    data.extend(struct.pack('<I', 0x00000025))

    occlusion_path = f"worlds/{world_name}/tile/x{tile_x}/y{tile_y}/occlusion"
    data.extend(occlusion_path.encode('ascii') + b'\x00')

    data.extend(b'\x00')

    return bytes(data)


# ============================================================================
# MAIN PIPELINE
# ============================================================================

class TerrainOperation:
    """Base class for terrain operations."""
    pass


class RaiseArea(TerrainOperation):
    def __init__(self, x: int, y: int, radius: int, amount: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.amount = amount


class LowerArea(TerrainOperation):
    def __init__(self, x: int, y: int, radius: int, amount: float):
        self.x = x
        self.y = y
        self.radius = radius
        self.amount = amount


class Flatten(TerrainOperation):
    def __init__(self, x: int, y: int, height: float, radius: int = 10):
        self.x = x
        self.y = y
        self.height = height
        self.radius = radius


class Smooth(TerrainOperation):
    def __init__(self, factor: float = 0.5):
        self.factor = factor


class SetAll(TerrainOperation):
    def __init__(self, height: float):
        self.height = height


def apply_operations(editor: HeightfieldEditor, operations: List[TerrainOperation]):
    """Apply a list of terrain operations to the editor."""
    for op in operations:
        if isinstance(op, RaiseArea):
            editor.raise_area(op.x, op.y, op.radius, op.amount)
        elif isinstance(op, LowerArea):
            editor.lower_area(op.x, op.y, op.radius, op.amount)
        elif isinstance(op, Flatten):
            editor.flatten(op.x, op.y, op.height, op.radius)
        elif isinstance(op, Smooth):
            editor.smooth(op.factor)
        elif isinstance(op, SetAll):
            editor.fill(op.height)


def create_custom_map(
    map_name: str,
    tile_x: int,
    tile_y: int,
    operations: List[TerrainOperation],
    output_dir: str,
    base_height: float = 0.0,
) -> Tuple[Path, Path]:
    """
    Create a custom map bundle with terrain modifications.

    Args:
        map_name: Name of the map/world
        tile_x: X coordinate of the tile
        tile_y: Y coordinate of the tile
        operations: List of terrain operations to apply
        output_dir: Output directory for the bundle files
        base_height: Initial height for the terrain (default 0.0)

    Returns:
        Tuple of (header_path, data_path)
    """
    print(f"\n{'='*60}")
    print(f"Creating Custom Map: {map_name}")
    print(f"Tile coordinates: x={tile_x}, y={tile_y}")
    print(f"Base height: {base_height}")
    print(f"{'='*60}\n")

    # Create the output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create heightfield editor with base terrain
    print("Step 1: Creating base terrain...")
    editor = create_heightfield_with_base(base_height)
    editor.show()

    # Apply terrain operations
    if operations:
        print("\nStep 2: Applying terrain modifications...")
        apply_operations(editor, operations)
        editor.show()

    # Create the heightfield file
    print("\nStep 3: Creating heightfield file...")
    heightfield_data = create_heightfield_file(editor)
    print(f"Heightfield size: {len(heightfield_data)} bytes")

    # Create supporting files
    print("\nStep 4: Creating supporting terrain files...")
    tile_path = f"worlds/{map_name}/tile/x{tile_x}/y{tile_y}"

    files = {
        f"{tile_path}/height.Heightfield": heightfield_data,
        f"{tile_path}/height.bin": create_height_bin(),
        f"{tile_path}/blend.bin": create_blend_bin(),
        f"{tile_path}/blend.Texture": create_blend_texture(tile_x, tile_y, map_name),
        f"{tile_path}/occlusion.Texture": create_occlusion_texture(tile_x, tile_y, map_name),
    }

    for name, data in files.items():
        print(f"  {name}: {len(data)} bytes")

    # Create DFPF bundle
    print("\nStep 5: Creating DFPF bundle...")
    bundle_name = f"RgS_{map_name.capitalize()}"
    creator = DFPFCreator()

    # Extension to type index mapping
    ext_to_idx = {
        'Heightfield': 0,
        'bin': 0,
        'Texture': 1,
    }

    for filepath, filedata in files.items():
        ext = filepath.split('.')[-1]
        file_type_idx = ext_to_idx.get(ext, 0)
        creator.add_file(filepath, ext, filedata, file_type_idx)

    header_path, data_path = creator.save(str(output_path / bundle_name))

    print(f"\n{'='*60}")
    print(f"Custom map created successfully!")
    print(f"Bundle files:")
    print(f"  {header_path}")
    print(f"  {data_path}")
    print(f"{'='*60}")

    return header_path, data_path


def create_mountain_preset(map_name: str, tile_x: int, tile_y: int, output_dir: str) -> Tuple[Path, Path]:
    """Create a test map with a mountain in the center."""
    operations = [
        SetAll(20.0),  # Start with a flat base at height 20
        RaiseArea(128, 128, 60, 100),  # Large mountain in center
        RaiseArea(128, 128, 30, 60),   # Higher peak in the middle
        Smooth(0.3),  # Smooth the transitions
        Flatten(128, 128, 220, 8),  # Flatten the very top to a plateau
    ]
    return create_custom_map(map_name, tile_x, tile_y, operations, output_dir)


def create_valley_preset(map_name: str, tile_x: int, tile_y: int, output_dir: str) -> Tuple[Path, Path]:
    """Create a test map with a valley in the center."""
    operations = [
        SetAll(150.0),  # Start with high terrain
        LowerArea(128, 128, 50, 100),  # Carve out a valley
        LowerArea(128, 128, 25, 50),   # Deepen the center
        Smooth(0.4),
        Flatten(128, 128, 30, 15),  # Flatten the valley floor
    ]
    return create_custom_map(map_name, tile_x, tile_y, operations, output_dir)


def create_plateau_preset(map_name: str, tile_x: int, tile_y: int, output_dir: str) -> Tuple[Path, Path]:
    """Create a test map with raised plateau areas."""
    operations = [
        SetAll(50.0),  # Base terrain
        RaiseArea(80, 80, 40, 80),   # Plateau 1
        RaiseArea(176, 176, 40, 80), # Plateau 2
        Smooth(0.2),
    ]
    return create_custom_map(map_name, tile_x, tile_y, operations, output_dir)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Brutal Legend Custom Map Pipeline - Create custom terrain maps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Create a map with a mountain
    python custom_map_pipeline.py --map-name CustomTest --tile-x 100 --tile-y 100 \\
        --operation raise --x 128 --y 128 --radius 50 --amount 100 \\
        --operation smooth --factor 0.3

    # Create a flat map
    python custom_map_pipeline.py --map-name FlatTest --tile-x 101 --tile-y 101 \\
        --operation set_all --height 128

    # Use preset: mountain
    python custom_map_pipeline.py --map-name MountainTest --preset mountain \\
        --tile-x 102 --tile-y 102

    # Use preset: valley
    python custom_map_pipeline.py --map-name ValleyTest --preset valley \\
        --tile-x 103 --tile-y 103

    # Copy to mods folder
    python custom_map_pipeline.py --map-name Test --tile-x 100 --tile-y 100 \\
        --operation set_all --height 100 --copy-to-mods
        """
    )

    parser.add_argument('--map-name', '-m', required=True, help='Name of the map')
    parser.add_argument('--tile-x', '-x', type=int, default=100, help='Tile X coordinate (default: 100)')
    parser.add_argument('--tile-y', '-y', type=int, default=100, help='Tile Y coordinate (default: 100)')
    parser.add_argument('--output-dir', '-o', default='custom_maps', help='Output directory')
    parser.add_argument('--base-height', '-b', type=float, default=0.0, help='Base terrain height')
    parser.add_argument('--copy-to-mods', action='store_true', help='Copy output to Win/Mods/')

    # Preset option
    parser.add_argument('--preset', choices=['mountain', 'valley', 'plateau', 'flat'],
                        help='Use a preset terrain configuration')

    # Operation arguments
    parser.add_argument('--operation', '-op', action='append',
                        help='Operation type (raise, lower, flatten, smooth, set_all)')
    parser.add_argument('--x', type=int, help='X coordinate for area operations')
    parser.add_argument('--y', type=int, help='Y coordinate for area operations')
    parser.add_argument('--radius', '-r', type=int, help='Radius for area operations')
    parser.add_argument('--amount', '-a', type=float, help='Amount for raise/lower operations')
    parser.add_argument('--height', '-H', type=float, help='Height for flatten/set_all operations')
    parser.add_argument('--factor', '-f', type=float, default=0.5, help='Factor for smooth operation')

    args = parser.parse_args()

    # Build operations list
    operations = []

    if args.preset:
        print(f"Using preset: {args.preset}")
        # Presets don't use additional operations from CLI
    elif args.operation:
        # Parse operations from CLI
        i = 0
        while i < len(args.operation):
            op_type = args.operation[i].lower()

            if op_type == 'raise':
                # Get next 4 args: x, y, radius, amount
                if i + 4 > len(args.operation):
                    raise ValueError("raise operation requires x, y, radius, amount")
                # Need to parse from a combined way - this doesn't work well with nargs
                # Let's use a different approach
                pass
            elif op_type == 'lower':
                pass
            elif op_type == 'flatten':
                pass
            elif op_type == 'smooth':
                operations.append(Smooth(args.factor))
            elif op_type == 'set_all':
                if args.height is not None:
                    operations.append(SetAll(args.height))
                else:
                    raise ValueError("set_all operation requires --height")

            i += 1

    # Alternative: use dedicated CLI arguments for operations
    if args.x is not None and args.y is not None and args.amount is not None:
        if args.radius is not None:
            if args.operation and 'raise' in ' '.join(args.operation):
                operations.append(RaiseArea(args.x, args.y, args.radius, args.amount))
            elif args.operation and 'lower' in ' '.join(args.operation):
                operations.append(LowerArea(args.x, args.y, args.radius, args.amount))

    if args.height is not None:
        if args.x is not None and args.y is not None:
            operations.append(Flatten(args.x, args.y, args.height))
        else:
            operations.append(SetAll(args.height))

    # If using preset, generate preset operations
    if args.preset == 'mountain':
        ops = [
            SetAll(20.0),
            RaiseArea(128, 128, 60, 100),
            RaiseArea(128, 128, 30, 60),
            Smooth(0.3),
            Flatten(128, 128, 220, 8),
        ]
        operations = ops
    elif args.preset == 'valley':
        ops = [
            SetAll(150.0),
            LowerArea(128, 128, 50, 100),
            LowerArea(128, 128, 25, 50),
            Smooth(0.4),
            Flatten(128, 128, 30, 15),
        ]
        operations = ops
    elif args.preset == 'plateau':
        ops = [
            SetAll(50.0),
            RaiseArea(80, 80, 40, 80),
            RaiseArea(176, 176, 40, 80),
            Smooth(0.2),
        ]
        operations = ops
    elif args.preset == 'flat':
        operations = [SetAll(args.height or 100.0)]

    try:
        # Create the custom map
        header_path, data_path = create_custom_map(
            map_name=args.map_name,
            tile_x=args.tile_x,
            tile_y=args.tile_y,
            operations=operations,
            output_dir=args.output_dir,
            base_height=args.base_height,
        )

        # Optionally copy to Win/Mods
        if args.copy_to_mods:
            mods_dir = Path(args.output_dir) / "Win" / "Mods"
            mods_dir.mkdir(parents=True, exist_ok=True)

            import shutil
            shutil.copy(header_path, mods_dir / header_path.name)
            shutil.copy(data_path, mods_dir / data_path.name)

            print(f"\nCopied to: {mods_dir}")
            print(f"  {header_path.name}")
            print(f"  {data_path.name}")

        print("\nDone!")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
