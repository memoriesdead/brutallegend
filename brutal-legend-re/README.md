# Brutal Legend Reverse Engineering

Open source project to reverse engineer, document, and extend Brutal Legend using its native Buddha engine.

## Quick Links

- [TODO.md](./TODO.md) - Master project checklist
- [docs/](./docs/) - Technical documentation
- [tools/](./tools/) - Reverse engineering tools

## What Is This?

A community-driven effort to:
1. **Reverse engineer** Brutal Legend's Buddha engine
2. **Document** all file formats, functions, and systems
3. **Create tools** for modding and content creation
4. **Enable** new maps, missions, characters, and story content

## Project Goals

- ✅ Create new maps and levels
- ✅ Add new missions and story content
- ✅ Enable full modding support
- ✅ Build a spiritual successor capability
- ✅ Steam Workshop integration

## Engine Details

| Component | Technology |
|-----------|------------|
| Engine | Buddha (Double Fine proprietary) |
| Middleware | FMOD (audio), Havok (physics), Scaleform (UI), Bink (video) |
| Container Format | DFPF (.~h/.~p pairs) |
| Scripting | Lua |
| Platform | Windows (primary), Steam PC version |

## Current Status

**Phase: Planning Complete**

See [TODO.md](./TODO.md) for full milestone schedule.

## Documentation

- [docs/formats/DFPF_SPEC.md](docs/formats/DFPF_SPEC.md) - Container format
- [docs/formats/PROTO_SPEC.md](docs/formats/PROTO_SPEC.md) - Prototype system
- [docs/formats/MISSION_API.md](docs/formats/MISSION_API.md) - Mission scripting
- [docs/formats/](docs/formats/) - File format specifications

## Toolchain

| Tool | Purpose |
|------|---------|
| Ghidra | Disassembler/decompiler |
| rizin/Cutter | Reverse engineering framework |
| x64dbg | Windows debugger |
| ImHex | Hex editor |
| Kaitai Struct | Binary format specifications |

## Getting Started

See [docs/tutorials/01_GETTING_STARTED.md](docs/tutorials/01_GETTING_STARTED.md)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

MIT - See [LICENSE](./LICENSE)
