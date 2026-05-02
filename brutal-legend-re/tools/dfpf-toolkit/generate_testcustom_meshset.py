#!/usr/bin/env python3
"""
TestCustom MeshSet Generator for Brutal Legend Skirmish Maps

Based on analysis of sk_1 through sk_9 MeshSet text format from Man_Trivial bundle.

Format Structure:
==================
MeshSet{Key=Value;Key=Value;...}

Key fields:
- HighMipForceDistance=0 (int)
- _NonMagicalLODCache=[LODData{...},LODData{...},...] (array of LOD structures)
- _HasFoliageSubsets=0 (int, boolean)
- _BlendshapeLOD=0 (int)
- _BoundingBox=<<x,y,z>,<x,y,z>> (min/max corner of bounding box)
- BoundingBoxScale=<x,y,z> (usually <1,1,1>)
- VisualType=kVT_SetDressing or kVT_Vehicle (enum)
- MaxVisibleLOD=4 (int)
- _MipConstantUV1=float
- _NonMagicalLODCacheSize=1 (int)
- CameraAlphaBoundingBox=<<x,y,z>,<x,y,z>> (same as BoundingBox typically)
- _MipConstantUV0=float
- _BoundingSphere=<<x,y,z>,r> (center and radius)

LODData structure:
- Flags=int (1073 for full detail, 16 for reduced, 0 for empty)
- MaxJoint=int (-1 for static, positive for skinned)
- Mesh=@path (reference to mesh resource, @ means reference)
- Materials=[@mat1,@mat2,...] (array of material references)

Example sk_1:
MeshSet{HighMipForceDistance=0;_NonMagicalLODCache=[LODData{Flags=1073;MaxJoint=-1;Mesh=@vehicles/n02_zeppelin/model/gibs/spinefrontb_debria;Materials=[@environments/materials/general/misc_zeppelinbody,@vehicles/n02_zeppelin/materials/externalflames,@environments/materials/general/wood_zeppelinframe];},LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];},LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];},LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];},LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];}];_HasFoliageSubsets=0;_BlendshapeLOD=0;_BoundingBox=<<-0.93383294,-1.87673,-3.2481518>,<1.09671,1.4036341,2.9158649>>;BoundingBoxScale=<1,1,1>;VisualType=kVT_SetDressing;MaxVisibleLOD=4;_MipConstantUV1=0.00080609397;_NonMagicalLODCacheSize=1;CameraAlphaBoundingBox=<<-0.93383294,-1.87673,-3.2481518>,<1.09671,1.4036341,2.9158649>>;_MipConstantUV0=0.00080609397;_BoundingSphere=<<0.081438482,-0.23654801,-0.16614354>,3.6358972>;}

Notes:
- sk_9 uses VisualType=kVT_Vehicle and MaxJoint=31 (full zeppelin mesh, skinned)
- sk_1 through sk_8 use VisualType=kVT_SetDressing (static dressing meshes)
- First LODData entry contains the actual mesh (Flags=1073 or 16)
- Subsequent LODData entries are empty (Flags=0, Mesh=@, Materials=[])
- The text format uses ';' as field separator, ',' as array element separator
"""

import struct


def generate_meshset_text(
    map_name="TestCustom",
    mesh_path="@vehicles/n02_zeppelin/model/gibs/spinefrontb_debria",
    materials=None,
    bounding_box_min=(-1.0, -2.0, -3.0),
    bounding_box_max=(1.0, 1.5, 3.0),
    bounding_sphere_center=(0.0, -0.2, -0.2),
    bounding_sphere_radius=3.5,
    visual_type="kVT_SetDressing",
    mip_constant_uv0=0.0008,
    mip_constant_uv1=0.0008,
    flags=1073,
    max_joint=-1,
):
    """
    Generate a MeshSet text entry for a custom skirmish map.

    Args:
        map_name: Name of the map (used for comments only)
        mesh_path: Path to the mesh resource (e.g., @vehicles/n02_zeppelin/model/gibs/...)
        materials: List of material paths. If None, uses default zeppelin materials.
        bounding_box_min: Tuple (x, y, z) for bounding box minimum corner
        bounding_box_max: Tuple (x, y, z) for bounding box maximum corner
        bounding_sphere_center: Tuple (x, y, z) for bounding sphere center
        bounding_sphere_radius: Float radius for bounding sphere
        visual_type: String enum - "kVT_SetDressing" or "kVT_Vehicle"
        mip_constant_uv0: Float mip constant for UV0
        mip_constant_uv1: Float mip constant for UV1
        flags: Int LOD flags (1073 for full detail, 16 for reduced)
        max_joint: Int -1 for static mesh, >=0 for skinned

    Returns:
        String containing the MeshSet text format entry
    """

    if materials is None:
        materials = [
            "@environments/materials/general/misc_zeppelinbody",
            "@vehicles/n02_zeppelin/materials/externalflames",
            "@environments/materials/general/wood_zeppelinframe",
        ]

    # Build LODData entries
    # First LOD is the actual mesh
    lod0 = f"LODData{{Flags={flags};MaxJoint={max_joint};Mesh={mesh_path};Materials=["
    lod0 += ",".join(materials)
    lod0 += "];}"

    # Subsequent 4 LODs are empty (required for MaxVisibleLOD=4)
    empty_lods = []
    for _ in range(4):
        empty_lods.append("LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];}")

    lod_cache = "[" + ",".join([lod0] + empty_lods) + "]"

    # Build the full MeshSet
    meshset = "MeshSet{"
    meshset += f"HighMipForceDistance=0;"
    meshset += f"_NonMagicalLODCache={lod_cache};"
    meshset += "_HasFoliageSubsets=0;"
    meshset += "_BlendshapeLOD=0;"
    meshset += f"_BoundingBox=<<{bounding_box_min[0]},{bounding_box_min[1]},{bounding_box_min[2]}>"
    meshset += f",<{bounding_box_max[0]},{bounding_box_max[1]},{bounding_box_max[2]}>>;"
    meshset += "BoundingBoxScale=<1,1,1>;"
    meshset += f"VisualType={visual_type};"
    meshset += "MaxVisibleLOD=4;"
    meshset += f"_MipConstantUV1={mip_constant_uv1};"
    meshset += "_NonMagicalLODCacheSize=1;"
    meshset += f"CameraAlphaBoundingBox=<<{bounding_box_min[0]},{bounding_box_min[1]},{bounding_box_min[2]}>"
    meshset += f",<{bounding_box_max[0]},{bounding_box_max[1]},{bounding_box_max[2]}>>;"
    meshset += f"_MipConstantUV0={mip_constant_uv0};"
    meshset += f"_BoundingSphere=<<{bounding_sphere_center[0]},{bounding_sphere_center[1]},{bounding_sphere_center[2]}>,{bounding_sphere_radius}>;"
    meshset += "}"

    return meshset


def create_dfpf_entry(meshset_text, file_extension_index=3):
    """
    Create a DFPF file entry for the MeshSet.

    For Man_Trivial bundle, skirmish maps use file_type_index 3 (MusicNameTable)
    or 4 (VoiceSettings), but the content is MeshSet text.

    Args:
        meshset_text: The MeshSet text string
        file_extension_index: The file type index (3 for MusicNameTable, 4 for VoiceSettings)

    Returns:
        Tuple of (header_bytes, data_bytes) ready for DFPF insertion
    """
    # Text data encoded as UTF-8
    text_bytes = meshset_text.encode('utf-8')

    # 4-byte size header (little endian)
    size_header = struct.pack("<I", len(text_bytes))

    # Full data = size header + text
    data_bytes = size_header + text_bytes

    return data_bytes


def main():
    print("=" * 80)
    print("TestCustom MeshSet Generator for Brutal Legend Skirmish Maps")
    print("=" * 80)

    # Generate a basic TestCustom entry based on sk_1 format
    print("\n--- Generating TestCustom MeshSet (based on sk_1 format) ---\n")

    meshset = generate_meshset_text(
        map_name="TestCustom",
        mesh_path="@vehicles/n02_zeppelin/model/gibs/spinefrontb_debria",
        materials=[
            "@environments/materials/general/misc_zeppelinbody",
            "@vehicles/n02_zeppelin/materials/externalflames",
            "@environments/materials/general/wood_zeppelinframe",
        ],
        bounding_box_min=(-0.93, -1.88, -3.25),
        bounding_box_max=(1.10, 1.40, 2.92),
        bounding_sphere_center=(0.08, -0.24, -0.17),
        bounding_sphere_radius=3.64,
        visual_type="kVT_SetDressing",
        flags=1073,
        max_joint=-1,
    )

    print("Generated MeshSet text:")
    print(meshset)
    print()

    # Create DFPF entry data
    data_bytes = create_dfpf_entry(meshset, file_extension_index=3)

    print(f"\nDFPF entry data size: {len(data_bytes)} bytes")
    print(f"Text content size: {len(meshset)} bytes")

    # Save to file
    output_path = "TestCustom_meshset.txt"
    with open(output_path, 'w') as f:
        f.write(meshset)
    print(f"\nSaved MeshSet text to: {output_path}")

    # Also save binary version
    bin_path = "TestCustom_meshset.bin"
    with open(bin_path, 'wb') as f:
        f.write(data_bytes)
    print(f"Saved DFPF entry to: {bin_path}")

    # Show comparison with sk_1
    print("\n" + "=" * 80)
    print("FORMAT COMPARISON: sk_1 vs TestCustom")
    print("=" * 80)

    sk_1_meshset = '''MeshSet{HighMipForceDistance=0;_NonMagicalLODCache=[LODData{Flags=1073;MaxJoint=-1;Mesh=@vehicles/n02_zeppelin/model/gibs/spinefrontb_debria;Materials=[@environments/materials/general/misc_zeppelinbody,@vehicles/n02_zeppelin/materials/externalflames,@environments/materials/general/wood_zeppelinframe];},LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];},LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];},LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];},LODData{Flags=0;MaxJoint=-1;Mesh=@;Materials=[];}];_HasFoliageSubsets=0;_BlendshapeLOD=0;_BoundingBox=<<-0.93383294,-1.87673,-3.2481518>,<1.09671,1.4036341,2.9158649>>;BoundingBoxScale=<1,1,1>;VisualType=kVT_SetDressing;MaxVisibleLOD=4;_MipConstantUV1=0.00080609397;_NonMagicalLODCacheSize=1;CameraAlphaBoundingBox=<<-0.93383294,-1.87673,-3.2481518>,<1.09671,1.4036341,2.9158649>>;_MipConstantUV0=0.00080609397;_BoundingSphere=<<0.081438482,-0.23654801,-0.16614354>,3.6358972>;}'''

    print("\nsk_1 length:", len(sk_1_meshset))
    print("TestCustom length:", len(meshset))
    print("\nsk_1 starts with:", sk_1_meshset[:100])
    print("TestCustom starts with:", meshset[:100])


if __name__ == "__main__":
    main()