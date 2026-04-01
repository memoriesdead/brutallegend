#!/usr/bin/env python3
"""
Brutal Legend Heightfield Viewer

Parses and visualizes .Heightfield DDS texture files from Brutal Legend.
DXT5 compressed 128x128 textures with custom 40-byte header.

Usage:
    python heightfield_view.py <input.Heightfield> [output.png] [--3d]
    python heightfield_view.py <input.Heightfield> --batch
"""

import struct
import sys
import os
from pathlib import Path

# Try to import numpy, fallback to pure Python
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not found, using pure Python (slower)")

# Try to import PIL for image output
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL not found, will use raw output")


def parse_custom_header(data):
    """Parse the 40-byte custom header before DDS header."""
    if len(data) < 40:
        raise ValueError(f"File too small for custom header: {len(data)} bytes")

    offset = 0
    header = {}

    # Bytes 0-15: Unknown metadata (mostly zeros)
    header['unknown_metadata'] = data[0:16]

    # Byte 8: type marker (0x0b observed)
    header['type_marker'] = data[8]

    # Offset 0x10: Width hint (0x80 = 128)
    header['width_hint'] = struct.unpack('<I', data[0x10:0x14])[0]

    # Offset 0x14: Height hint (0x80 = 128)
    header['height_hint'] = struct.unpack('<I', data[0x14:0x18])[0]

    # Offset 0x1C: Flags
    header['flags'] = struct.unpack('<I', data[0x1C:0x20])[0]

    # Offset 0x20: "rtxT" magic (Texture backwards)
    header['magic'] = data[0x20:0x24].decode('ascii', errors='replace')

    # Offset 0x24: Data size
    header['data_size'] = struct.unpack('<I', data[0x24:0x28])[0]

    # Offset 0x28: "DDS " magic
    dds_magic = data[0x28:0x2C]
    if dds_magic != b'DDS ':
        raise ValueError(f"Expected 'DDS ' magic at offset 0x28, got {dds_magic}")

    return header


def parse_dds_header(data, offset=0x2C):
    """
    Parse DDS header starting at the dwSize field (after 'DDS ' magic).

    Standard DDS header is 124 bytes, starting 4 bytes after the 'DDS ' magic.
    """
    header = {}

    # dwSize (always 124)
    dwSize = struct.unpack('<I', data[offset:offset+4])[0]
    header['dwSize'] = dwSize

    # dwFlags
    header['dwFlags'] = struct.unpack('<I', data[offset+4:offset+8])[0]

    # dwHeight
    header['dwHeight'] = struct.unpack('<I', data[offset+8:offset+12])[0]

    # dwWidth
    header['dwWidth'] = struct.unpack('<I', data[offset+12:offset+16])[0]

    # dwPitchOrLinearSize
    header['dwPitchOrLinearSize'] = struct.unpack('<I', data[offset+16:offset+20])[0]

    # dwDepth
    header['dwDepth'] = struct.unpack('<I', data[offset+20:offset+24])[0]

    # dwMipMapCount
    header['dwMipMapCount'] = struct.unpack('<I', data[offset+24:offset+28])[0]

    # dwReserved1 (11 DWORDs = 44 bytes)
    header['dwReserved1'] = data[offset+28:offset+72]

    # Pixel Format (32 bytes starting at offset 72 from dwSize)
    pf_offset = offset + 72
    header['pf'] = {}
    header['pf']['dwSize'] = struct.unpack('<I', data[pf_offset:pf_offset+4])[0]
    header['pf']['dwFlags'] = struct.unpack('<I', data[pf_offset+4:pf_offset+8])[0]
    header['pf']['dwFourCC'] = data[pf_offset+8:pf_offset+12]
    header['pf']['dwRGBBitCount'] = struct.unpack('<I', data[pf_offset+12:pf_offset+16])[0]
    header['pf']['dwRBitMask'] = struct.unpack('<I', data[pf_offset+16:pf_offset+20])[0]
    header['pf']['dwGBitMask'] = struct.unpack('<I', data[pf_offset+20:pf_offset+24])[0]
    header['pf']['dwBBitMask'] = struct.unpack('<I', data[pf_offset+24:pf_offset+28])[0]
    header['pf']['dwABitMask'] = struct.unpack('<I', data[pf_offset+28:pf_offset+32])[0]

    # dwCaps (offset 108 from dwSize)
    header['dwCaps'] = struct.unpack('<I', data[offset+108:offset+112])[0]
    header['dwCaps2'] = struct.unpack('<I', data[offset+112:offset+116])[0]

    return header


def decode_dxt5_block(block_data):
    """
    Decode a single DXT5 block (16 bytes) to 16 RGBA pixels.

    DXT5 format (128 bits per 4x4 block):
    - Bytes 0-1: Alpha endpoints (2 x 8-bit)
    - Bytes 2-7: Alpha indices (3 bits per pixel, 16 pixels, packed)

    For color (bytes 8-15):
    - Bytes 8-9: Color endpoint 0 (R5G6B5)
    - Bytes 10-11: Color endpoint 1 (R5G6B5)
    - Bytes 12-15: Color indices (2 bits per pixel, 16 pixels, packed)
    """
    if len(block_data) != 16:
        raise ValueError(f"DXT5 block must be 16 bytes, got {len(block_data)}")

    # Decode alpha
    alpha0 = block_data[0]
    alpha1 = block_data[1]

    # Alpha interpolation table (8 alpha values)
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

    # Decode alpha indices (48 bits = 6 bytes, 16 x 3-bit values)
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

    # R5G6B5 to RGB888
    r0 = (color0_raw >> 11) & 0x1F
    g0 = (color0_raw >> 5) & 0x3F
    b0 = color0_raw & 0x1F

    r1 = (color1_raw >> 11) & 0x1F
    g1 = (color1_raw >> 5) & 0x3F
    b1 = color1_raw & 0x1F

    # Scale to 8-bit
    r0 = (r0 * 255) // 31
    g0 = (g0 * 255) // 63
    b0 = (b0 * 255) // 31

    r1 = (r1 * 255) // 31
    g1 = (g1 * 255) // 63
    b1 = (b1 * 255) // 31

    # Color interpolation table (4 color values)
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
            0,  # Reserved
        ]

    # Decode color indices (32 bits, 16 x 2-bit values)
    color_indices = struct.unpack('<I', block_data[12:16])[0]

    # Build pixel array
    pixels = []
    for i in range(16):
        alpha_idx = (alpha_indices >> (3 * i)) & 0x07
        color_idx = (color_indices >> (2 * i)) & 0x03

        alpha = alpha_table[alpha_idx]
        if color_idx == 3 and color0_raw < color1_raw:
            # In transparent mode, this is black
            r, g, b = 0, 0, 0
        else:
            r, g, b = color_table[color_idx]

        pixels.append((r, g, b, alpha))

    return pixels


def decode_dxt5_image(width, height, dxt5_data):
    """Decode entire DXT5 image."""

    # For DXT5, block size is 4x4, minimum size is 8 bytes
    if width < 4:
        width = 4
    if height < 4:
        height = 4

    # Calculate number of blocks
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4

    # Create output array
    if HAS_NUMPY:
        image = np.zeros((height, width, 4), dtype=np.uint8)
    else:
        image = [[(0, 0, 0, 0) for _ in range(width)] for _ in range(height)]

    block_size = 16  # DXT5 uses 16 bytes per 4x4 block

    for block_y in range(blocks_y):
        for block_x in range(blocks_x):
            block_offset = (block_y * blocks_x + block_x) * 16

            if block_offset + 16 > len(dxt5_data):
                break

            block_data = dxt5_data[block_offset:block_offset + 16]
            pixels = decode_dxt5_block(block_data)

            # Place pixels in image
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


def extract_heightmap(image):
    """
    Extract height values from RGBA image.

    For heightfields, the alpha channel often contains height info,
    or we can use luminance: Y = 0.299*R + 0.587*G + 0.114*B
    """
    if HAS_NUMPY:
        # Use alpha channel as primary height source
        height = image[:, :, 3].astype(np.float32)

        # If alpha is mostly constant, use luminance
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
                    # Likely unused, use 0
                    h = 0
                else:
                    # Use alpha as height
                    h = a
                height_row.append(h)
            height.append(height_row)
        return height


def create_grayscale_image(heightmap, output_path):
    """Create a grayscale visualization of the heightmap."""
    if HAS_NUMPY:
        height = np.array(heightmap)
        # Normalize to 0-255
        if height.max() > height.min():
            height = ((height - height.min()) / (height.max() - height.min()) * 255).astype(np.uint8)
        else:
            height = np.zeros_like(height, dtype=np.uint8)

        if HAS_PIL:
            img = Image.fromarray(height, mode='L')
            img.save(output_path)
            print(f"Saved grayscale image to {output_path}")
        else:
            # Save as raw PGM
            with open(output_path, 'wb') as f:
                f.write(b'P5\n')
                f.write(f"{height.shape[1]}\n".encode())
                f.write(f"{height.shape[0]}\n".encode())
                f.write(b'255\n')
                f.write(height.tobytes())
            print(f"Saved PGM image to {output_path}")
    else:
        height = heightmap
        max_h = max(max(row) for row in height) if height else 1
        min_h = min(min(row) for row in height) if height else 0

        if HAS_PIL:
            width = len(height[0]) if height else 0
            height_n = len(height)
            img_data = []
            for row in height:
                for h in row:
                    if max_h > min_h:
                        val = int((h - min_h) / (max_h - min_h) * 255)
                    else:
                        val = 0
                    img_data.append(val)
            img = Image.new('L', (width, height_n))
            img.putdata(img_data)
            img.save(output_path)
            print(f"Saved grayscale image to {output_path}")
        else:
            # Fallback: save as ASCII PGM
            with open(output_path, 'w') as f:
                f.write("P2\n")
                f.write(f"{len(height[0]) if height else 0} {len(height)}\n")
                f.write("255\n")
                for row in height:
                    for h in row:
                        if max_h > min_h:
                            val = int((h - min_h) / (max_h - min_h) * 255)
                        else:
                            val = 0
                        f.write(f"{val} ")
                    f.write("\n")
            print(f"Saved ASCII PGM image to {output_path}")


def create_3d_visualization(heightmap, output_path):
    """Create a 3D wireframe/surface visualization using matplotlib."""
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        if HAS_NUMPY:
            X, Y = np.meshgrid(range(heightmap.shape[1]), range(heightmap.shape[0]))
            Z = heightmap

            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')

            # Plot surface
            surf = ax.plot_surface(X, Y, Z, cmap='terrain', linewidth=0, antialiased=True)

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Height')
            ax.set_title('Brutal Legend Heightfield Terrain')

            fig.colorbar(surf, shrink=0.5, aspect=5)
            plt.savefig(output_path, dpi=150)
            plt.close()

            print(f"Saved 3D visualization to {output_path}")
        else:
            print("3D visualization requires numpy. Install with: pip install numpy matplotlib")
    except ImportError as e:
        print(f"Cannot create 3D visualization: {e}")
        print("Install matplotlib: pip install matplotlib")


def analyze_heightfield(filepath):
    """Analyze a heightfield file and return its properties."""
    with open(filepath, 'rb') as f:
        data = f.read()

    print(f"\nAnalyzing: {filepath}")
    print(f"File size: {len(data)} bytes")

    # Parse custom header
    custom = parse_custom_header(data)
    print(f"\nCustom Header:")
    print(f"  Type marker: 0x{custom['type_marker']:02x}")
    print(f"  Width hint: {custom['width_hint']}")
    print(f"  Height hint: {custom['height_hint']}")
    print(f"  Magic: {custom['magic']}")
    print(f"  Data size: {custom['data_size']}")

    # Parse DDS header
    dds = parse_dds_header(data)
    print(f"\nDDS Header:")
    print(f"  dwSize: {dds['dwSize']}")
    print(f"  dwFlags: 0x{dds['dwFlags']:08x}")
    print(f"  dwWidth: {dds['dwWidth']}")
    print(f"  dwHeight: {dds['dwHeight']}")
    print(f"  dwMipMapCount: {dds['dwMipMapCount']}")
    print(f"  Pixel Format: {dds['pf']['dwFourCC'].decode('ascii', errors='replace')}")

    # Calculate expected data offsets
    custom_header_size = 40
    dds_header_size = 128  # 124 + 4 for magic
    dxt5_offset = custom_header_size + dds_header_size  # = 0xA8

    print(f"\nData Layout:")
    print(f"  Custom header: 0x00 - 0x27 (40 bytes)")
    print(f"  DDS header: 0x28 - 0xA7 (128 bytes)")
    print(f"  DXT5 data offset: 0x{dxt5_offset:02x} ({dxt5_offset} bytes)")

    expected_dxt5_size = (dds['dwWidth'] // 4) * (dds['dwHeight'] // 4) * 8
    print(f"  Expected DXT5 size: {expected_dxt5_size} bytes")

    # Extra data after DXT5
    extra_offset = dxt5_offset + expected_dxt5_size
    extra_size = len(data) - extra_offset
    print(f"  Extra data offset: 0x{extra_offset:04x}, size: {extra_size} bytes")

    return {
        'custom': custom,
        'dds': dds,
        'dxt5_offset': dxt5_offset,
        'data': data
    }


def process_heightfield(filepath, output_path=None, mode='grayscale'):
    """Process a heightfield file and generate visualization."""
    info = analyze_heightfield(filepath)

    if info['dds']['pf']['dwFourCC'] != b'DXT5':
        raise ValueError(f"Only DXT5 format supported, got {info['dds']['pf']['dwFourCC']}")

    width = info['dds']['dwWidth']
    height = info['dds']['dwHeight']
    dxt5_offset = info['dxt5_offset']

    # Extract DXT5 compressed data
    # For 128x128 with 8 mipmaps, main image is first mip
    # Block size = (width/4) * (height/4) * 8 = 32 * 32 * 8 = 8192 bytes
    block_size = (width // 4) * (height // 4) * 8

    dxt5_data = info['data'][dxt5_offset:dxt5_offset + block_size]
    print(f"\nExtracted DXT5 data: {len(dxt5_data)} bytes")

    # Decode DXT5
    print("Decoding DXT5 image...")
    image = decode_dxt5_image(width, height, dxt5_data)
    print(f"Decoded image: {width}x{height}")

    # Extract heightmap
    print("Extracting heightmap...")
    heightmap = extract_heightmap(image)

    # Generate output path if not provided
    if output_path is None:
        base = Path(filepath).stem
        if mode == 'grayscale':
            output_path = f"{base}_heightmap.png"
        elif mode == '3d':
            output_path = f"{base}_3d.png"

    # Create visualization
    if mode == 'grayscale':
        create_grayscale_image(heightmap, output_path)
    elif mode == '3d':
        create_3d_visualization(heightmap, output_path)

    return heightmap, image


def batch_process(input_dir, output_dir=None, mode='grayscale'):
    """Batch process all .Heightfield files in a directory."""
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Error: Directory not found: {input_dir}")
        return

    heightfield_files = list(input_path.glob("*.Heightfield"))
    print(f"Found {len(heightfield_files)} .Heightfield files")

    if not heightfield_files:
        return

    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path

    for hf_file in heightfield_files:
        try:
            if output_dir:
                base = hf_file.stem
                if mode == 'grayscale':
                    out_file = output_path / f"{base}_heightmap.png"
                elif mode == '3d':
                    out_file = output_path / f"{base}_3d.png"
            else:
                out_file = None

            print(f"\n{'='*60}")
            process_heightfield(str(hf_file), str(out_file) if out_file else None, mode)
        except Exception as e:
            print(f"Error processing {hf_file}: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='View and analyze Brutal Legend heightfield terrain data'
    )
    parser.add_argument('input', help='Input .Heightfield file or directory for batch')
    parser.add_argument('output', nargs='?', help='Output PNG file (optional)')
    parser.add_argument('--3d', dest='viz3d', action='store_true', help='Generate 3D surface visualization')
    parser.add_argument('--batch', action='store_true', help='Batch process directory')
    parser.add_argument('--analyze', action='store_true', help='Only analyze, do not generate output')

    args = parser.parse_args()

    mode = '3d' if args.viz3d else 'grayscale'

    if args.batch or os.path.isdir(args.input):
        batch_process(args.input, args.output, mode)
    else:
        if args.analyze:
            analyze_heightfield(args.input)
        else:
            process_heightfield(args.input, args.output, mode)


if __name__ == '__main__':
    main()
