#!/usr/bin/env python3
"""
blend.Texture Parser for Brutal Legend Terrain

Parses the blend.Texture format used for terrain albedo/blend textures.
Provides information about embedded paths and material layers.

Usage:
    python blend_texture_parse.py <blend.Texture file>
    python blend_texture_parse.py --scan <directory>  # Scan for all blend.Texture files
"""

import struct
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict


class BlendTextureParser:
    """Parser for blend.Texture terrain texture metadata files."""

    MAGIC = 0x00000001
    VERSION = 4

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data: bytes = b''
        self.header: Dict[str, int] = {}
        self.blend_path: str = ""
        self.occlusion_path: str = ""
        self.materials: List[str] = []
        self.unknown_floats: List[float] = []
        self.valid: bool = False
        self.error: str = ""

    def parse(self) -> bool:
        """Parse the blend.Texture file."""
        try:
            with open(self.filepath, 'rb') as f:
                self.data = f.read()
        except Exception as e:
            self.error = f"Failed to read file: {e}"
            return False

        if len(self.data) < 16:
            self.error = "File too small for header"
            return False

        # Parse header
        self.header = {
            'magic': struct.unpack('<I', self.data[0:4])[0],
            'version': struct.unpack('<I', self.data[4:8])[0],
            'flags': struct.unpack('<I', self.data[8:12])[0],
            'unknown': struct.unpack('<I', self.data[12:16])[0],
        }

        if self.header['magic'] != self.MAGIC:
            self.error = f"Invalid magic: 0x{self.header['magic']:08X}"
            return False

        # Parse strings
        pos = 0x10

        # First string is null-terminated (blend path)
        end = self.data.find(b'\x00', pos)
        if end == -1:
            self.error = "Could not find end of first string"
            return False

        self.blend_path = self.data[pos:end].decode('ascii', errors='replace')
        pos = end + 1

        # Find all embedded strings by scanning for 'environments/' or 'worlds/'
        self.materials = []
        self.unknown_floats = []

        i = pos
        while i < len(self.data) - 20:
            # Look for environment material paths (13 bytes)
            if self.data[i:i+13] == b'environments/':
                # Found start of material string
                start = i
                end_pos = start
                while end_pos < len(self.data) and self.data[end_pos] != 0:
                    end_pos += 1
                s = self.data[start:end_pos].decode('ascii', errors='replace')
                if ('terrainmaterials' in s or '/materials/' in s) and s not in self.materials:
                    self.materials.append(s)
                i = end_pos + 1
            # Look for worlds/ path (occlusion or other) - 7 bytes
            elif self.data[i:i+7] == b'worlds/':
                # Could be occlusion path
                start = i
                end_pos = start
                while end_pos < len(self.data) and self.data[end_pos] != 0:
                    end_pos += 1
                s = self.data[start:end_pos].decode('ascii', errors='replace')
                if 'occlusion' in s:
                    self.occlusion_path = s
                i = end_pos + 1
            else:
                i += 1

        self.valid = True
        return True

    def print_info(self):
        """Print parsed information."""
        print(f"=== blend.Texture Parser ===")
        print(f"File: {self.filepath}")
        print(f"Size: {len(self.data)} bytes")
        print()

        if not self.valid:
            print(f"ERROR: {self.error}")
            return

        print("Header:")
        print(f"  Magic:    0x{self.header['magic']:08X}")
        print(f"  Version:  {self.header['version']}")
        print(f"  Flags:    0x{self.header['flags']:08X}")
        print(f"  Unknown:  0x{self.header['unknown']:08X}")
        print()

        print("Paths:")
        print(f"  Blend:      {self.blend_path}")
        print(f"  Occlusion:  {self.occlusion_path}")
        print()

        print(f"Materials ({len(self.materials)}):")
        for i, mat in enumerate(self.materials):
            print(f"  {i+1}. {mat}")

        print()

    def get_tile_coords(self) -> Optional[Tuple[int, int]]:
        """Extract tile coordinates from blend path."""
        import re
        match = re.search(r'x(-?\d+)/y(-?\d+)', self.blend_path)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None

    def get_world_name(self) -> Optional[str]:
        """Extract world name from blend path."""
        import re
        match = re.search(r'worlds/([^/]+)', self.blend_path)
        if match:
            return match.group(1)
        return None


def scan_directory(directory: str) -> List[BlendTextureParser]:
    """Scan a directory for blend.Texture files."""
    parsers = []
    dirpath = Path(directory)

    if not dirpath.exists():
        print(f"Directory not found: {directory}")
        return parsers

    # Find all blend.Texture files
    for blend_file in dirpath.rglob("blend.Texture"):
        parser = BlendTextureParser(str(blend_file))
        if parser.parse():
            parsers.append(parser)

    return parsers


def create_mapping_file(parsers: List[BlendTextureParser], output_path: str):
    """Create a mapping file from generic Heightfield names to real paths."""
    with open(output_path, 'w') as f:
        f.write("# blend.Texture to Path Mapping\n")
        f.write("# Format: generic_name -> real_path\n\n")

        for parser in parsers:
            coords = parser.get_tile_coords()
            world = parser.get_world_name()
            if coords and world:
                x, y = coords
                # Heightfield path would be: worlds/<world>/tile/x<x>/y<y>/height.bin
                heightfield_path = f"worlds/{world}/tile/x{x}/y{y}/height.bin"
                blend_path = f"worlds/{world}/tile/x{x}/y{y}/blend.Texture"
                occlusion_path = f"worlds/{world}/tile/x{x}/y{y}/occlusion.Texture"

                f.write(f"# {blend_path}\n")
                f.write(f"height: {heightfield_path}\n")
                f.write(f"blend: {blend_path}\n")
                f.write(f"occlusion: {occlusion_path}\n\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage examples:")
        print("  python blend_texture_parse.py path/to/blend.Texture")
        print("  python blend_texture_parse.py --scan extracted/RgS_World/worlds")
        sys.exit(1)

    if sys.argv[1] == '--scan':
        if len(sys.argv) < 3:
            print("Error: --scan requires a directory argument")
            sys.exit(1)

        directory = sys.argv[2]
        print(f"Scanning directory: {directory}")
        print()

        parsers = scan_directory(directory)
        print(f"Found {len(parsers)} blend.Texture files\n")

        for parser in parsers:
            parser.print_info()

        if parsers:
            # Create mapping file
            output_path = "blend_texture_mapping.txt"
            create_mapping_file(parsers, output_path)
            print(f"\nMapping file created: {output_path}")

    else:
        filepath = sys.argv[1]
        parser = BlendTextureParser(filepath)
        if parser.parse():
            parser.print_info()

            # Try to extract tile coordinates
            coords = parser.get_tile_coords()
            if coords:
                x, y = coords
                print(f"Tile coordinates: x={x}, y={y}")
                print(f"Expected heightfield: worlds/{parser.get_world_name()}/tile/x{x}/y{y}/height.bin")
        else:
            print(f"Failed to parse: {parser.error}")
            sys.exit(1)


if __name__ == "__main__":
    main()