#!/usr/bin/env python3
"""
Brutal Legend Terrain Editor

Loads and edits terrain height data from two formats:
1. DDS Heightfield (.Heightfield): 40-byte custom header + DXT5 compressed texture
2. MeshSet (.bin): "hsem" magic header + material/vertex data

Usage:
    python terrain_editor.py <input_file> [--info]
    python terrain_editor.py <input_file> --show
    python terrain_editor.py <input_file> --set HEIGHT
    python terrain_editor.py <input_file> --smooth [factor=0.5]
    python terrain_editor.py <input_file> --raise x y radius height
    python terrain_editor.py <input_file> --lower x y radius height
    python terrain_editor.py <input_file> --flatten x y height
    python terrain_editor.py --extract-bundle <bundle.~h> <world_path> <output_dir>
"""

import struct
import sys
import os
import zlib
import argparse
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass

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
# DDS HEIGHTFIELD FORMAT
# ============================================================================

@dataclass
class CustomHeader:
    """40-byte proprietary header before DDS data."""
    unknown_metadata: bytes
    type_marker: int
    width_hint: int
    height_hint: int
    flags: int
    magic: str  # "rtxT"
    data_size: int


@dataclass
class DDSHeader:
    """Standard DDS header (124 bytes + 'DDS ' magic)."""
    dwSize: int
    dwFlags: int
    dwHeight: int
    dwWidth: int
    dwPitchOrLinearSize: int
    dwDepth: int
    dwMipMapCount: int
    dwReserved1: bytes
    pf: Dict[str, Any]
    dwCaps: int
    dwCaps2: int


def parse_custom_header(data: bytes) -> CustomHeader:
    """Parse the 40-byte custom header before DDS header."""
    if len(data) < 40:
        raise ValueError(f"File too small for custom header: {len(data)} bytes")

    return CustomHeader(
        unknown_metadata=data[0:16],
        type_marker=data[8],
        width_hint=struct.unpack('<I', data[0x10:0x14])[0],
        height_hint=struct.unpack('<I', data[0x14:0x18])[0],
        flags=struct.unpack('<I', data[0x1C:0x20])[0],
        magic=data[0x20:0x24].decode('ascii', errors='replace'),
        data_size=struct.unpack('<I', data[0x24:0x28])[0],
    )


def parse_dds_header(data: bytes, offset: int = 0x2C) -> DDSHeader:
    """Parse DDS header starting at the dwSize field (after 'DDS ' magic)."""
    pf_offset = offset + 72
    return DDSHeader(
        dwSize=struct.unpack('<I', data[offset:offset+4])[0],
        dwFlags=struct.unpack('<I', data[offset+4:offset+8])[0],
        dwHeight=struct.unpack('<I', data[offset+8:offset+12])[0],
        dwWidth=struct.unpack('<I', data[offset+12:offset+16])[0],
        dwPitchOrLinearSize=struct.unpack('<I', data[offset+16:offset+20])[0],
        dwDepth=struct.unpack('<I', data[offset+20:offset+24])[0],
        dwMipMapCount=struct.unpack('<I', data[offset+24:offset+28])[0],
        dwReserved1=data[offset+28:offset+72],
        pf={
            'dwSize': struct.unpack('<I', data[pf_offset:pf_offset+4])[0],
            'dwFlags': struct.unpack('<I', data[pf_offset+4:pf_offset+8])[0],
            'dwFourCC': data[pf_offset+8:pf_offset+12],
            'dwRGBBitCount': struct.unpack('<I', data[pf_offset+12:pf_offset+16])[0],
            'dwRBitMask': struct.unpack('<I', data[pf_offset+16:pf_offset+20])[0],
            'dwGBitMask': struct.unpack('<I', data[pf_offset+20:pf_offset+24])[0],
            'dwBBitMask': struct.unpack('<I', data[pf_offset+24:pf_offset+28])[0],
            'dwABitMask': struct.unpack('<I', data[pf_offset+28:pf_offset+32])[0],
        },
        dwCaps=struct.unpack('<I', data[offset+108:offset+112])[0],
        dwCaps2=struct.unpack('<I', data[offset+112:offset+116])[0],
    )


def decode_dxt5_block(block_data: bytes) -> List[Tuple[int, int, int, int]]:
    """Decode a single DXT5 block (16 bytes) to 16 RGBA pixels."""
    if len(block_data) != 16:
        raise ValueError(f"DXT5 block must be 16 bytes, got {len(block_data)}")

    # Decode alpha
    alpha0 = block_data[0]
    alpha1 = block_data[1]

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

    alpha_indices = 0
    alpha_indices |= block_data[2]
    alpha_indices |= block_data[3] << 8
    alpha_indices |= block_data[4] << 16
    alpha_indices |= block_data[5] << 24
    alpha_indices |= block_data[6] << 32
    alpha_indices |= block_data[7] << 40

    # Decode color
    color0_raw = struct.unpack('<H', block_data[8:10])[0]
    color1_raw = struct.unpack('<H', block_data[10:12])[0]

    r0 = (color0_raw >> 11) & 0x1F
    g0 = (color0_raw >> 5) & 0x3F
    b0 = color0_raw & 0x1F

    r1 = (color1_raw >> 11) & 0x1F
    g1 = (color1_raw >> 5) & 0x3F
    b1 = color1_raw & 0x1F

    r0 = (r0 * 255) // 31
    g0 = (g0 * 255) // 63
    b0 = (b0 * 255) // 31

    r1 = (r1 * 255) // 31
    g1 = (g1 * 255) // 63
    b1 = (b1 * 255) // 31

    if color0_raw >= color1_raw:
        color_table = [
            (r0, g0, b0),
            (r1, g1, b1),
            ((2*r0 + 1*r1) // 3, (2*g0 + 1*g1) // 3, (2*b0 + 1*b1) // 3),
            ((1*r0 + 2*r1) // 3, (1*g0 + 2*g1) // 3, (1*b0 + 2*b1) // 3),
        ]
    else:
        color_table = [
            (r0, g0, b0),
            (r1, g1, b1),
            ((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2),
            (0, 0, 0),
        ]

    color_indices = struct.unpack('<I', block_data[12:16])[0]

    pixels = []
    for i in range(16):
        alpha_idx = (alpha_indices >> (3 * i)) & 0x07
        color_idx = (color_indices >> (2 * i)) & 0x03

        alpha = alpha_table[alpha_idx]
        if color_idx == 3 and color0_raw < color1_raw:
            r, g, b = 0, 0, 0
        else:
            r, g, b = color_table[color_idx]

        pixels.append((r, g, b, alpha))

    return pixels


def decode_dxt5_image(width: int, height: int, dxt5_data: bytes):
    """Decode entire DXT5 image."""
    if width < 4:
        width = 4
    if height < 4:
        height = 4

    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4

    if HAS_NUMPY:
        image = np.zeros((height, width, 4), dtype=np.uint8)
    else:
        image = [[(0, 0, 0, 0) for _ in range(width)] for _ in range(height)]

    block_size = 16

    for block_y in range(blocks_y):
        for block_x in range(blocks_x):
            block_offset = (block_y * blocks_x + block_x) * 16

            if block_offset + 16 > len(dxt5_data):
                break

            block_data = dxt5_data[block_offset:block_offset + 16]
            pixels = decode_dxt5_block(block_data)

            start_x = block_x * 4
            start_y = block_y * 4

            for py in range(4):
                for px in range(4):
                    x = start_x + px
                    y = start_y + py
                    if x < width and y < height:
                        pixel_idx = py * 4 + px
                        if HAS_NUMPY:
                            image[y, x] = list(pixels[pixel_idx])
                        else:
                            image[y][x] = pixels[pixel_idx]

    return image


def encode_dxt5_block(pixels: List[Tuple[int, int, int, int]]) -> bytes:
    """Encode 16 RGBA pixels into a DXT5 block (16 bytes)."""
    if len(pixels) != 16:
        raise ValueError(f"DXT5 block must have 16 pixels, got {len(pixels)}")

    # Extract alpha values (ensure Python int to avoid numpy overflow)
    alpha_values = [int(p[3]) for p in pixels]

    # Find alpha endpoints (min and max)
    sorted_alpha = sorted(set(alpha_values))
    if len(sorted_alpha) >= 2:
        alpha0 = sorted_alpha[-1]  # Max
        alpha1 = sorted_alpha[0]   # Min
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

    # Map alpha to table indices
    alpha_indices = 0
    for i, a in enumerate(alpha_values):
        # Find closest alpha in table
        best_idx = 0
        best_dist = 256
        for idx, tab_a in enumerate(alpha_table):
            dist = abs(tab_a - a)
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
        alpha_indices |= (best_idx & 0x07) << (3 * i)

    # Extract color values (ensure Python int to avoid numpy overflow)
    r_values = [int(p[0]) for p in pixels]
    g_values = [int(p[1]) for p in pixels]
    b_values = [int(p[2]) for p in pixels]

    # Convert to R5G6B5
    def to_r5g6b5(r, g, b):
        r5 = (int(r) * 31) // 255
        g6 = (int(g) * 63) // 255
        b5 = (int(b) * 31) // 255
        return (r5 << 11) | (g6 << 5) | b5

    color_values = [to_r5g6b5(r, g, b) for r, g, b in zip(r_values, g_values, b_values)]

    # Find color endpoints
    sorted_colors = sorted(set(color_values))
    if len(sorted_colors) >= 2:
        # Use the two extreme colors as endpoints
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

    # Map colors to table indices
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


def extract_heightmap(image) -> Any:
    """Extract height values from RGBA image (alpha channel)."""
    if HAS_NUMPY:
        height = image[:, :, 3].astype(np.float32)
        if height.max() == height.min():
            height = 0.299 * image[:, :, 0].astype(np.float32) + \
                    0.587 * image[:, :, 1].astype(np.float32) + \
                    0.114 * image[:, :, 2].astype(np.float32)
        return height
    else:
        height = []
        for row in image:
            height_row = []
            for pixel in row:
                r, g, b, a = pixel
                if a == 0 and r == 0 and g == 0 and b == 0:
                    h = 0
                else:
                    h = a
                height_row.append(h)
            height.append(height_row)
        return height


def apply_heightmap(image, heightmap: Any) -> Any:
    """Apply heightmap values to image alpha channel."""
    if HAS_NUMPY:
        height = np.array(heightmap, dtype=np.float32)
        height = np.clip(height, 0, 255).astype(np.uint8)
        image[:, :, 3] = height
        return image
    else:
        for y in range(len(heightmap)):
            for x in range(len(heightmap[y])):
                h = int(max(0, min(255, heightmap[y][x])))
                image[y][x] = image[y][x][:3] + (h,)
        return image


class DDSHeightfield:
    """DDS Heightfield terrain file with 40-byte custom header."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data: bytes = b''
        self.custom_header: Optional[CustomHeader] = None
        self.dds_header: Optional[DDSHeader] = None
        self.width: int = 0
        self.height: int = 0
        self.image: Any = None
        self.heightmap: Any = None
        self.modified: bool = False

    def parse(self) -> bool:
        """Parse a DDS heightfield file."""
        try:
            with open(self.filepath, 'rb') as f:
                self.data = f.read()
        except Exception as e:
            print(f"Failed to read file: {e}")
            return False

        if len(self.data) < 0xA8:  # 40 + 128 = 168 bytes minimum
            print(f"File too small: {len(self.data)} bytes")
            return False

        # Verify DDS magic
        if self.data[0x28:0x2C] != b'DDS ':
            print(f"Invalid DDS magic: {self.data[0x28:0x2C]!r}")
            return False

        self.custom_header = parse_custom_header(self.data)
        self.dds_header = parse_dds_header(self.data)

        self.width = self.dds_header.dwWidth
        self.height = self.dds_header.dwHeight

        # Extract DXT5 data
        dxt5_offset = 0xA8  # 40 + 128
        block_size = (self.width // 4) * (self.height // 4) * 8
        dxt5_data = self.data[dxt5_offset:dxt5_offset + block_size]

        # Decode
        self.image = decode_dxt5_image(self.width, self.height, dxt5_data)
        self.heightmap = extract_heightmap(self.image)

        return True

    def get_height(self, x: int, y: int) -> float:
        """Get height at integer coordinates."""
        if HAS_NUMPY:
            return float(self.heightmap[y, x])
        else:
            return float(self.heightmap[y][x])

    def set_height(self, x: int, y: int, height: float):
        """Set height at integer coordinates."""
        if HAS_NUMPY:
            self.heightmap[y, x] = height
        else:
            self.heightmap[y][x] = height
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
        """Display heightmap info and optionally render image."""
        stats = self.get_stats()
        print(f"=== DDS Heightfield: {self.filepath.name} ===")
        print(f"Dimensions: {self.width}x{self.height}")
        print(f"Height range: {stats['min']:.2f} - {stats['max']:.2f}")
        print(f"Mean height: {stats['mean']:.2f}")
        print(f"Custom header magic: {self.custom_header.magic}")
        print(f"DXT5 format: {self.dds_header.pf['dwFourCC'].decode('ascii', errors='replace')}")

        if HAS_PIL:
            # Create grayscale visualization
            if HAS_NUMPY:
                h = np.array(self.heightmap)
                if h.max() > h.min():
                    h = ((h - h.min()) / (h.max() - h.min()) * 255).astype(np.uint8)
                else:
                    h = np.zeros_like(h, dtype=np.uint8)
                img = Image.fromarray(h, mode='L')
                out_path = str(self.filepath.with_suffix('')) + '_heightmap.png'
                img.save(out_path)
                print(f"Saved heightmap preview: {out_path}")
            else:
                print("PIL not available for visualization")

    def smooth(self, factor: float = 0.5):
        """Apply smoothing to heightmap."""
        if not HAS_NUMPY:
            print("Smoothing requires numpy")
            return

        h = self.heightmap.copy()
        smoothed = h.copy()

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                neighbors = [
                    h[y-1, x-1], h[y-1, x], h[y-1, x+1],
                    h[y, x-1],              h[y, x+1],
                    h[y+1, x-1], h[y+1, x], h[y+1, x+1],
                ]
                avg = sum(neighbors) / len(neighbors)
                smoothed[y, x] = h[y, x] * (1 - factor) + avg * factor

        self.heightmap = smoothed
        self.image = apply_heightmap(self.image, self.heightmap)
        self.modified = True
        print(f"Applied smoothing (factor={factor})")

    def raise_area(self, cx: int, cy: int, radius: int, amount: float):
        """Raise height in a circular area."""
        if not HAS_NUMPY:
            print(" raise_area requires numpy")
            return

        for y in range(max(0, cy - radius), min(self.height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(self.width, cx + radius + 1)):
                dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
                if dist <= radius:
                    falloff = 1.0 - (dist / radius)
                    self.heightmap[y, x] += amount * falloff

        self.image = apply_heightmap(self.image, self.heightmap)
        self.modified = True
        print(f"Raised area at ({cx}, {cy}) radius {radius} by {amount}")

    def lower_area(self, cx: int, cy: int, radius: int, amount: float):
        """Lower height in a circular area."""
        self.raise_area(cx, cy, radius, -amount)

    def flatten(self, cx: int, cy: int, target_height: float):
        """Flatten area to target height."""
        if not HAS_NUMPY:
            print("Flatten requires numpy")
            return

        radius = 5  # Flatten radius
        for y in range(max(0, cy - radius), min(self.height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(self.width, cx + radius + 1)):
                dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
                if dist <= radius:
                    falloff = 1.0 - (dist / radius)
                    current = self.heightmap[y, x]
                    self.heightmap[y, x] = current * (1 - falloff) + target_height * falloff

        self.image = apply_heightmap(self.image, self.heightmap)
        self.modified = True
        print(f"Flattened area at ({cx}, {cy}) to height {target_height}")

    def fill(self, height: float):
        """Fill entire heightmap with a value."""
        if HAS_NUMPY:
            self.heightmap[:, :] = height
        else:
            for y in range(len(self.heightmap)):
                for x in range(len(self.heightmap[y])):
                    self.heightmap[y][x] = height
        self.image = apply_heightmap(self.image, self.heightmap)
        self.modified = True
        print(f"Filled heightmap with {height}")

    def save(self, output_path: Optional[str] = None):
        """Save modified heightfield back to DDS format."""
        if output_path is None:
            output_path = str(self.filepath)

        # Re-encode image to DXT5
        dxt5_data = encode_dxt5_image(self.width, self.height, self.image)

        # Rebuild file
        with open(self.filepath, 'rb') as f:
            original = f.read()

        # Keep headers, replace DXT5 data
        dxt5_offset = 0xA8
        new_data = original[:dxt5_offset] + dxt5_data

        with open(output_path, 'wb') as f:
            f.write(new_data)

        print(f"Saved to: {output_path}")
        self.modified = False


# ============================================================================
# MESHSET (.bin) FORMAT
# ============================================================================

class MeshSetTerrain:
    """MeshSet terrain file with 'hsem' magic header."""

    HSEM_MAGIC = b'hsem'
    LRTM_MAGIC = b'lrtm'
    BVXD_MAGIC = b'BVXD'
    BIXD_MAGIC = b'BIXD'

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data: bytes = b''
        self.width: int = 0
        self.height: int = 0
        self.materials: List[str] = []
        self.material_indices: Any = None
        self.modified: bool = False

    def parse(self) -> bool:
        """Parse a MeshSet terrain .bin file."""
        try:
            with open(self.filepath, 'rb') as f:
                self.data = f.read()
        except Exception as e:
            print(f"Failed to read file: {e}")
            return False

        if len(self.data) < 0x80:
            print(f"File too small: {len(self.data)} bytes")
            return False

        if self.data[0:4] != self.HSEM_MAGIC:
            print(f"Invalid magic: {self.data[0:4]!r} (expected {self.HSEM_MAGIC!r})")
            return False

        # Parse header
        # Offset 0x08-0x10: scale values
        scale_x = struct.unpack('>f', self.data[0x08:0x0C])[0]
        scale_y = struct.unpack('>f', self.data[0x0C:0x10])[0]

        # Offset 0x10-0x18: height range
        height_min = struct.unpack('>f', self.data[0x10:0x14])[0]
        height_max = struct.unpack('>f', self.data[0x14:0x18])[0]

        # Check for lrtm marker at 0x20
        if self.data[0x20:0x24] != self.LRTM_MAGIC:
            print(f"Warning: Expected lrtm magic at 0x20, got {self.data[0x20:0x24]!r}")

        # Version at 0x24
        version = struct.unpack('>I', self.data[0x24:0x28])[0]

        # Count at 0x28
        count = struct.unpack('>I', self.data[0x28:0x2C])[0]

        # Extract material strings
        self.materials = []
        pos = 0x2C
        while pos < len(self.data) and len(self.materials) < count:
            end = self.data.find(b'\x00', pos)
            if end == -1:
                break
            name = self.data[pos:end].decode('ascii', errors='replace')
            if name:
                self.materials.append(name)
            pos = end + 1

        # Find BVXD marker (typically at 0x70)
        bvxd_pos = self.data.find(self.BVXD_MAGIC, 0x30)
        if bvxd_pos == -1:
            print("Warning: BVXD marker not found")
            return False

        # Find BIXD marker
        bixd_pos = self.data.find(self.BIXD_MAGIC, bvxd_pos + 4)
        if bixd_pos == -1:
            print("Warning: BIXD marker not found")
            return False

        # Data section starts after BIXD + 4 bytes header
        data_start = bixd_pos + 8

        # Determine grid size from data
        data_size = len(self.data) - data_start
        # Each entry is 2 bytes (uint16)
        entries = data_size // 2

        # Assume square grid
        grid_size = int(entries ** 0.5)
        if grid_size * grid_size != entries:
            print(f"Warning: Data size {entries} is not a perfect square")
            grid_size = 16  # fallback

        self.width = grid_size
        self.height = grid_size

        # Parse material indices
        self.material_indices = []
        for i in range(entries):
            idx = struct.unpack('>H', self.data[data_start + i*2:data_start + i*2 + 2])[0]
            self.material_indices.append(idx)

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get material index statistics."""
        if HAS_NUMPY and self.material_indices is not None:
            arr = np.array(self.material_indices)
            return {
                'min': int(arr.min()),
                'max': int(arr.max()),
                'mean': float(arr.mean()),
                'unique': len(np.unique(arr)),
                'width': self.width,
                'height': self.height,
            }
        elif self.material_indices:
            flat = list(self.material_indices)
            return {
                'min': min(flat),
                'max': max(flat),
                'mean': sum(flat) / len(flat),
                'unique': len(set(flat)),
                'width': self.width,
                'height': self.height,
            }
        return {}

    def show(self):
        """Display MeshSet terrain info."""
        stats = self.get_stats()
        print(f"=== MeshSet Terrain: {self.filepath.name} ===")
        print(f"Dimensions: {self.width}x{self.height}")
        print(f"Materials ({len(self.materials)}):")
        for i, mat in enumerate(self.materials):
            print(f"  {i}: {mat}")
        if stats:
            print(f"Index range: {stats['min']} - {stats['max']}")
            print(f"Unique indices: {stats['unique']}")


# ============================================================================
# DFPF BUNDLE EXTRACTION
# ============================================================================

COMPRESSION_UNCOMPRESSED_V5 = 4
COMPRESSION_ZLIB_V5 = 8


class DFPFBundleExtractor:
    """Extract terrain files from DFPF bundles using the dfpf_extract module."""

    def __init__(self, header_path: str):
        self.header_path = Path(header_path)
        self.data_path = self.header_path.with_suffix(".~p")
        self.file_records: List[Dict] = []
        self._extractor = None

    def parse(self) -> bool:
        """Parse DFPF bundle header using dfpf_extract.DFPFExtractor."""
        try:
            # Import and use the existing dfpf_extract module
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent / 'dfpf-toolkit'))
            from dfpf_extract import DFPFExtractor

            self._extractor = DFPFExtractor(str(self.header_path))
            self._extractor.parse()
            return True

        except Exception as e:
            print(f"Failed to parse bundle: {e}")
            return False

    def extract_terrain_files(self, world_path: str, output_dir: str) -> List[Path]:
        """Extract terrain files matching a world path pattern."""
        if self._extractor is None:
            print("Bundle not parsed")
            return []

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        extracted = []
        for record in self._extractor.file_records:
            if world_path in record.filename:
                try:
                    out_file = self._extractor.extract_file(record, output_path)
                    extracted.append(out_file)
                except Exception as e:
                    print(f"Failed to extract {record.full_filename}: {e}")

        return extracted


# ============================================================================
# MAIN CLI
# ============================================================================

def detect_format(filepath: str) -> str:
    """Detect terrain file format."""
    with open(filepath, 'rb') as f:
        header = f.read(40)

    if header[0:4] == b'hsem':
        return 'meshset'
    elif header[0:4] == b'\x00\x00\x00\x00' and len(header) >= 40:
        # Could be DDS with custom header
        with open(filepath, 'rb') as f:
            f.seek(0x28)
            dds_magic = f.read(4)
        if dds_magic == b'DDS ':
            return 'dds'
    elif header[0x20:0x24] == b'rtxT':
        return 'dds'

    return 'unknown'


def main():
    parser = argparse.ArgumentParser(
        description='Brutal Legend Terrain Editor - Load and edit terrain height data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python terrain_editor.py terrain.Heightfield --info
    python terrain_editor.py terrain.Heightfield --show
    python terrain_editor.py terrain.Heightfield --smooth 0.3
    python terrain_editor.py terrain.Heightfield --raise-area 64 64 10 50
    python terrain_editor.py terrain.Heightfield --lower-area 64 64 10 30
    python terrain_editor.py terrain.Heightfield --flatten 64 64 128
    python terrain_editor.py terrain.Heightfield --set 200
    python terrain_editor.py --extract-bundle RgS_World.~h "worlds/continent3" output/
        """
    )

    parser.add_argument('input', nargs='?', help='Input terrain file')
    parser.add_argument('--info', action='store_true', help='Show terrain info')
    parser.add_argument('--show', action='store_true', help='Display heightmap details')
    parser.add_argument('--smooth', type=float, nargs='?', const=0.5, default=None, help='Smooth heightmap')
    parser.add_argument('--raise-area', nargs=4, metavar=('X', 'Y', 'RADIUS', 'AMOUNT'), type=float, help='Raise circular area')
    parser.add_argument('--lower-area', nargs=4, metavar=('X', 'Y', 'RADIUS', 'AMOUNT'), type=float, help='Lower circular area')
    parser.add_argument('--flatten', nargs=3, metavar=('X', 'Y', 'HEIGHT'), type=float, help='Flatten area to height')
    parser.add_argument('--set', type=float, help='Set all heights to value')
    parser.add_argument('--save', '-o', dest='save', nargs='?', const=None, metavar='FILE', help='Output file (default: overwrite input)')
    parser.add_argument('--extract-bundle', nargs=3, metavar=('BUNDLE', 'WORLD_PATH', 'OUTPUT'), help='Extract terrain from DFPF bundle')

    args = parser.parse_args()

    # Handle bundle extraction
    if args.extract_bundle:
        bundle_path, world_path, output_dir = args.extract_bundle
        print(f"Extracting terrain files matching: {world_path}")
        extractor = DFPFBundleExtractor(bundle_path)
        if extractor.parse():
            extracted = extractor.extract_terrain_files(world_path, output_dir)
            print(f"Extracted {len(extracted)} terrain files to: {output_dir}")
        return 0

    if not args.input:
        parser.print_help()
        return 1

    filepath = Path(args.input)
    if not filepath.exists():
        print(f"File not found: {filepath}")
        return 1

    fmt = detect_format(str(filepath))
    print(f"Detected format: {fmt}")

    if fmt == 'dds':
        terrain = DDSHeightfield(str(filepath))
        if not terrain.parse():
            print("Failed to parse DDS heightfield")
            return 1

        if args.info or args.show:
            terrain.show()

        if args.smooth is not None:
            terrain.smooth(args.smooth)

        if args.raise_area:
            x, y, radius, amount = args.raise_area
            terrain.raise_area(int(x), int(y), int(radius), amount)

        if args.lower_area:
            x, y, radius, amount = args.lower_area
            terrain.lower_area(int(x), int(y), int(radius), amount)

        if args.flatten:
            x, y, height = args.flatten
            terrain.flatten(int(x), int(y), height)

        if args.set is not None:
            terrain.fill(args.set)

        if terrain.modified:
            terrain.save(args.save)

    elif fmt == 'meshset':
        terrain = MeshSetTerrain(str(filepath))
        if not terrain.parse():
            print("Failed to parse MeshSet terrain")
            return 1

        if args.info or args.show:
            terrain.show()

        print("Note: MeshSet editing not yet implemented (materials only, no height)")
        print("MeshSet files contain material indices, not height values directly.")

    else:
        print(f"Unknown terrain format")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
