# Model Format Specification

**Status:** In Progress
**Game:** Brutal Legend
**Engine:** Buddha (Double Fine)
**Updated:** 2026-04-01

---

## Overview

Brutal Legend uses Double Fine proprietary model format within DFPF V5 containers.

## Container Format: DFPF V5

- Magic: dfpf at offset 0
- Version: 5 (at offset 4)
- Model assets stored as MeshSet (Version 8)
- Compression: ZLIB (type 8), Uncompressed (type 4), Xbox XMem (type 12)

## Model Asset Types

| Type | Ver | Description |
|------|-----|-------------|
| MeshSet | 8 | 3D geometry |
| Material | 13 | Surface materials |
| Stance | 3 | Pose data |
| Outfit | 0 | Outfit variants |
| ComboPose | 1 | Combat poses |
| AnimMap | 1 | Animation mapping |

## Bundle Sizes

| Bundle | Header | Data |
|--------|--------|------|
| Man_Trivial | 717 KB | 13.6 MB |
| RgS_World | 498 KB | 409 MB |

## Known Characters (a01_avatar)

- Eddie Riggs (protagonist)
- Lemmy Kilmister as Kill Master
- Rob Halford as Lionwhyte
- Ozzy Osbourne as Guardian of Metal
- Doviculus (antagonist)

## Texture Format

- DDS (DirectDraw Surface) format
- Stored in Man_Gfx bundle
- Multiple LOD levels (i1, i3, i5, etc.)

## References

- DFPF_ANALYSIS.md - Container format details
- DFPF_SPEC.md - Format specification
