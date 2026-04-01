#!/usr/bin/env python3
"""
Brutal Legend Heightfield Terrain Viewer

Parses and visualizes heightfield terrain data from Brutal Legend.
Heightfield files are 128x128 DXT5 compressed DDS textures with custom header.

Usage:
    python heightfield_view.py <input.Heightfield> [output.png]
    python heightfield_view.py <input.Heightfield> [output.png] --wire3d
    python heightfield_view.py --batch <directory> [output_dir]
"""

import struct
import sys
import os
from pathlib import Path
from typing import Tuple, Optional

# Try to import optional dependencies
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

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# DDS Pixel Format Flags
DDS_ALPHA_PIXELS = 0x00000001
DDS_FOURCC = 0x00000004
DDS_RGB = 0x00000040
DDS_RGBA = 0x00000041

# DXT5/BC3 Constants
DXT5_BLOCK_SIZE = 16  # bytes per 4x4 block
DXT5_BLOCK_WIDTH = 4
DXT5_BLOCK_HEIGHT = 4


def read_dds_header(data: bytes) -> dict:
    """Parse DDS header from binary data."""
    if len(data) < 128:
        raise ValueError(f"DDS data too small: {len(data)} bytes")

    # DDS Header starts at offset 0 within DDS data
    magic = data[0:4]
    if magic != b'DDS ':
        raise ValueError(f"Invalid DDS magic: {magic}")

    header = struct.unpack('<I', data[4:8])[0]  # dwSize
    flags = struct.unpack('<I', data[8:12])[0]
    height = struct.unpack('<I', data[12:16])[0]
    width = struct.unpack('<I', data[16:20])[0]
    pitch = struct.unpack('<I', data[20:24])[0]
    depth = struct.unpack('<I', data[24:28])[0]
    mipmaps = struct.unpack('<I', data[28:32])[0]

    # DDS pixel format (DDPIXELFORMAT) is at offset 76 within DDS header
    # Structure: dwSize(4), dwFlags(4), dwFourCC(4), dwRGBBitCount(4), ...
    # So dwFlags is at offset 76+4=80, dwFourCC at 76+8=84
    pf_flags = struct.unpack('<I', data[76+4:76+8])[0]
    pf_fourcc = data[76+8:76+12]
    pf_rgbbitcount = struct.unpack('<I', data[76+12:76+16])[0]
    pf_rbitmask = struct.unpack('<I', data[76+16:76+20])[0]
    pf_gbitmask = struct.unpack('<I', data[76+20:76+24])[0]
    pf_bbitmask = struct.unpack('<I', data[76+24:76+28])[0]
    pf_abitmask = struct.unpack('<I', data[76+28:76+32])[0]

    return {
        'magic': magic,
        'header_size': header,
        'flags': flags,
        'height': height,
        'width': width,
        'pitch': pitch,
        'depth': depth,
        'mipmaps': mipmaps,
        'pf_flags': pf_flags,
        'pf_fourcc': pf_fourcc,
        'pf_rgbbitcount': pf_rgbbitcount,
        'pf_rbitmask': pf_rbitmask,
        'pf_gbitmask': pf_gbitmask,
        'pf_bbitmask': pf_bbitmask,
        'pf_abitmask': pf_abitmask,
    }


def decode_dxt5_block(block: bytes) -> np.ndarray:
    """
    Decode a single DXT5 (BC3) compressed block to RGBA pixels.
    Returns a 4x4 numpy array of RGBA values (0-255).
    """
    if len(block) < 16:
        raise ValueError(f"DXT5 block too small: {len(block)} bytes")

    # DXT5 alpha block
    alpha0 = block[0]
    alpha1 = block[1]

    # 6 bytes of alpha indices (48 bits)
    alpha_indices = struct.unpack('<Q', block[0:6] + b'\x00\x00')[0]

    # Extract 8 alpha values
    if alpha0 > alpha1:
        alpha_table = [
            alpha0,
            alpha1,
            (6 * alpha0 + 1 * alpha1) // 7,
            (5 * alpha0 + 2 * alpha1) // 7,
            (4 * alpha0 + 3 * alpha1) // 7,
            (3 * alpha0 + 4 * alpha1) // 7,
            (2 * alpha0 + 5 * alpha1) // 7,
            (1 * alpha0 + 6 * alpha1) // 7,
        ]
    else:
        alpha_table = [
            alpha0,
            alpha1,
            (4 * alpha0 + 1 * alpha1) // 5,
            (3 * alpha0 + 2 * alpha1) // 5,
            (2 * alpha0 + 3 * alpha1) // 5,
            (1 * alpha0 + 4 * alpha1) // 5,
            0,
            255,
        ]

    # DXT5 color block
    color0 = struct.unpack('<H', block[8:10])[0]
    color1 = struct.unpack('<H', block[10:12])[0]

    # RGB565 to RGB888
    def rgb565_to_rgb(v):
        r = ((v >> 11) & 0x1F) * 255 // 31
        g = ((v >> 5) & 0x3F) * 255 // 63
        b = (v & 0x1F) * 255 // 31
        return (r, g, b)

    c0 = rgb565_to_rgb(color0)
    c1 = rgb565_to_rgb(color1)

    # Color table
    if color0 > color1:
        color_table = [
            c0,
            c1,
            ((2 * c0[0] + c1[0]) // 3, (2 * c0[1] + c1[1]) // 3, (2 * c0[2] + c1[2]) // 3),
            ((c0[0] + 2 * c1[0]) // 3, (c0[1] + 2 * c1[1]) // 3, (c0[2] + 2 * c1[2]) // 3),
        ]
    else:
        color_table = [
            c0,
            c1,
            ((c0[0] + c1[0]) // 2, (c0[1] + c1[1]) // 2, (c0[2] + c1[2]) // 2),
            (0, 0, 0),
        ]

    # Color indices (32 bits for 16 pixels, 2 bits each)
    color_indices = struct.unpack('<I', block[12:16])[0]

    # Alpha indices (bits extracted from 48-bit field, 3 bits each)
    alpha_values = []
    for i in range(16):
        bit_pos = i * 3
        idx = (alpha_indices >> bit_pos) & 0x07
        alpha_values.append(alpha_table[idx])

    # Build 4x4 output
    pixels = np.zeros((4, 4, 4), dtype=np.uint8)
    for y in range(4):
        for x in range(4):
            pixel_idx = y * 4 + x

            # Color index (2 bits)
            color_idx = (color_indices >> (pixel_idx * 2)) & 0x03
            color = color_table[color_idx]

            # Alpha value
            alpha = alpha_values[pixel_idx]

            pixels[y, x] = (color[0], color[1], color[2], alpha)

    return pixels


def decode_dxt5(data: bytes, width: int, height: int) -> np.ndarray:
    """
    Decode full DXT5 compressed image.
    Returns RGBA numpy array of shape (height, width, 4).
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4

    output = np.zeros((height, width, 4), dtype=np.uint8)

    offset = 0
    for by in range(blocks_y):
        for bx in range(blocks_x):
            block = data[offset:offset + 16]
            if len(block) < 16:
                break

            pixels = decode_dxt5_block(block)

            # Copy block to output image
            for py in range(4):
                for px in range(4):
                    img_y = by * 4 + py
                    img_x = bx * 4 + px
                    if img_y < height and img_x < width:
                        output[img_y, img_x] = pixels[py, px]

            offset += 16

    return output


def parse_heightfield(filepath: str) -> dict:
    """
    Parse a Brutal Legend Heightfield file.

    Returns dict with:
        - width, height: dimensions
        - data: numpy array of height values (grayscale 0-255)
        - raw_rgba: raw RGBA data from DDS
        - extra_data: bytes after DDS data
    """
    with open(filepath, 'rb') as f:
        raw_data = f.read()

    total_size = len(raw_data)
    print(f"File size: {total_size} bytes")

    # Custom header parsing
    custom_header = raw_data[0:16]
    print(f"Custom header: {custom_header.hex()}")

    width = struct.unpack('<I', raw_data[16:20])[0]
    height = struct.unpack('<I', raw_data[20:24])[0]
    print(f"Dimensions: {width}x{height}")

    # Check for rtxT magic at offset 0x20
    magic = raw_data[0x20:0x24]
    if magic == b'rtxT':
        print(f"Magic: 'rtxT' (Texture backwards) at offset 0x20")

    # DDS data starts at offset 0x28 (40 bytes after file start)
    dds_offset = 0x28
    dds_data = raw_data[dds_offset:]

    # Parse DDS header
    dds_header = read_dds_header(dds_data)
    print(f"DDS Format: fourcc={dds_header['pf_fourcc']}, flags=0x{dds_header['pf_flags']:08X}")

    # DDS pixel data starts at offset 128 from DDS start (DDS header is 128 bytes per terrain spec)
    pixel_data_offset = 128
    pixel_data = dds_data[pixel_data_offset:]

    print(f"Pixel data size: {len(pixel_data)} bytes")

    # Decode DXT5
    if dds_header['pf_fourcc'] == b'DXT5' or dds_header['pf_flags'] & 0x04:
        rgba_data = decode_dxt5(pixel_data, width, height)
        print(f"Decoded DXT5 to RGBA: {rgba_data.shape}")
    else:
        raise ValueError(f"Unsupported format: {dds_header['pf_fourcc']}")

    # Extract height data - DXT5 stores data in various channels
    # For heightfields, typically the red channel or alpha contains height
    # We'll use the red channel as primary height source
    height_values = rgba_data[:, :, 0].copy()

    # Also try alpha channel
    alpha_values = rgba_data[:, :, 3].copy()

    # Extra binary data after DDS pixel data
    # DDS header is 128 bytes starting at 0x28, pixel data follows
    # Calculate actual pixel data size (including all mipmaps)
    pixel_data_end = dds_offset + pixel_data_offset + len(pixel_data)
    extra_data = b''
    if total_size > pixel_data_end:
        extra_data = raw_data[pixel_data_end:]
        print(f"Extra binary data: {len(extra_data)} bytes at offset 0x{pixel_data_end:x}")

    return {
        'width': width,
        'height': height,
        'data': height_values,
        'alpha': alpha_values,
        'raw_rgba': rgba_data,
        'extra_data': extra_data,
        'custom_header': custom_header,
        'dds_header': dds_header,
    }


def create_grayscale_image(height_data: np.ndarray, output_path: str):
    """Save height data as grayscale PNG."""
    if not HAS_PIL:
        raise ImportError("PIL required for image output. Install with: pip install pillow")

    # Normalize to 0-255
    img_data = height_data.astype(np.uint8)

    img = Image.fromarray(img_data)
    img.save(output_path)
    print(f"Saved grayscale image: {output_path}")


def create_colored_image(rgba_data: np.ndarray, output_path: str):
    """Save height data as colored RGBA PNG."""
    if not HAS_PIL:
        raise ImportError("PIL required for image output. Install with: pip install pillow")

    img = Image.fromarray(rgba_data)
    img.save(output_path)
    print(f"Saved RGBA image: {output_path}")


def create_3d_wireframe(height_data: np.ndarray, output_path: str, title: str = "Heightfield"):
    """Create 3D wireframe visualization."""
    if not HAS_MATPLOTLIB:
        raise ImportError("matplotlib required for 3D output. Install with: pip install matplotlib")

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Create mesh grid
    rows, cols = height_data.shape
    x = np.arange(cols)
    y = np.arange(rows)
    X, Y = np.meshgrid(x, y)

    # Plot wireframe
    ax.plot_surface(X, Y, height_data, cmap='terrain', linewidth=0.5, alpha=0.8)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Height')
    ax.set_title(title)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved 3D visualization: {output_path}")


def batch_convert(input_dir: str, output_dir: str):
    """Batch convert all Heightfield files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path.parent / f"{input_path.name}_output"

    output_path.mkdir(parents=True, exist_ok=True)

    heightfield_files = list(input_path.glob("*.Heightfield"))
    print(f"Found {len(heightfield_files)} Heightfield files")

    for hf_file in heightfield_files:
        print(f"\nProcessing: {hf_file.name}")
        try:
            result = parse_heightfield(str(hf_file))

            # Save grayscale
            base_name = hf_file.stem
            output_base = output_path / base_name

            create_grayscale_image(result['data'], str(output_base.with_suffix('.png')))

            # Save RGBA
            create_colored_image(result['raw_rgba'], str(output_base.with_suffix('.rgba.png')))

            print(f"  -> {output_base.stem}.png")

        except Exception as e:
            print(f"  ERROR: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Brutal Legend Heightfield Terrain Viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  View a heightfield (uses green channel by default):
    python heightfield_view.py file_0106_offset_1495552.Heightfield output.png

  Create 3D wireframe visualization:
    python heightfield_view.py file_0106_offset_1495552.Heightfield output.png --wire3d

  Batch convert directory:
    python heightfield_view.py --batch RgS_World/ output/

  Show raw channel statistics:
    python heightfield_view.py file.Heightfield --show-channels

  Use alpha channel for height:
    python heightfield_view.py file.Heightfield output.png --channel a
        """
    )

    parser.add_argument('input', nargs='?', help='Input Heightfield file')
    parser.add_argument('output', nargs='?', help='Output PNG file (default: input_stem.png)')
    parser.add_argument('--wire3d', action='store_true', help='Create 3D wireframe visualization')
    parser.add_argument('--batch', action='store_true', help='Batch mode: input is directory')
    parser.add_argument('--show-channels', action='store_true', help='Display channel information')
    parser.add_argument('--channel', choices=['r', 'g', 'b', 'a'], default='g',
                        help='Which channel to use for height (default: g)')

    args = parser.parse_args()

    if not HAS_NUMPY:
        print("ERROR: numpy required. Install with: pip install numpy")
        sys.exit(1)

    if not HAS_PIL:
        print("ERROR: Pillow required. Install with: pip install pillow")
        sys.exit(1)

    if args.batch:
        if not args.input:
            print("ERROR: --batch requires input directory")
            sys.exit(1)
        batch_convert(args.input, args.output)
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)

    # Default output filename
    if not args.output:
        output_path = input_path.parent / f"{input_path.stem}.png"
    else:
        output_path = Path(args.output)

    print(f"Parsing: {input_path}")
    result = parse_heightfield(str(input_path))

    # Select channel for height data
    channel_map = {'r': 0, 'g': 1, 'b': 2, 'a': 3}
    channel_idx = channel_map[args.channel]
    height_data = result['raw_rgba'][:, :, channel_idx]

    if args.show_channels:
        print(f"\nChannel analysis:")
        print(f"  Red:    min={result['raw_rgba'][:,:,0].min()}, max={result['raw_rgba'][:,:,0].max()}, mean={result['raw_rgba'][:,:,0].mean():.1f}")
        print(f"  Green:  min={result['raw_rgba'][:,:,1].min()}, max={result['raw_rgba'][:,:,1].max()}, mean={result['raw_rgba'][:,:,1].mean():.1f}")
        print(f"  Blue:   min={result['raw_rgba'][:,:,2].min()}, max={result['raw_rgba'][:,:,2].max()}, mean={result['raw_rgba'][:,:,2].mean():.1f}")
        print(f"  Alpha:  min={result['raw_rgba'][:,:,3].min()}, max={result['raw_rgba'][:,:,3].max()}, mean={result['raw_rgba'][:,:,3].mean():.1f}")
        print(f"\nUsing channel '{args.channel}' for height visualization")

    # Create 2D output
    create_grayscale_image(height_data, str(output_path))

    # Create 3D if requested
    if args.wire3d:
        if not HAS_MATPLOTLIB:
            print("WARNING: matplotlib not available, skipping 3D visualization")
        else:
            create_3d_wireframe(height_data, str(output_path.with_suffix('.3d.png')),
                               title=f"Heightfield: {input_path.name}")

    print(f"\nDone! Output: {output_path}")


if __name__ == '__main__':
    main()
