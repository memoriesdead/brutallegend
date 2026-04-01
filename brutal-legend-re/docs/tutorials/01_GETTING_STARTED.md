# Getting Started with Brutal Legend RE

**Status:** 🔴 Planning  
**Prerequisites:** None yet  

---

## Step 1: Install Toolchain

### Required Tools

| Tool | Download | Purpose |
|------|----------|---------|
| Ghidra | https://github.com/NationalSecurityAgency/ghidra | Disassembler/decompiler |
| x64dbg | https://x64dbg.com/ | Debugger |
| ImHex | https://github.com/WerWolv/ImHex | Hex editor |
| Kaitai Struct | https://kaitai.io/ | Binary format specs |
| Visual Studio 2022 | https://visualstudio.microsoft.com/ | C++ development |
| Python 3.10+ | https://python.org/ | Scripts |

### Optional Tools

| Tool | Download | Purpose |
|------|----------|---------|
| rizin/Cutter | https://rizin.re/ | Alternative RE framework |
| Detect It Easy | https://horsicq.github.io/ | File type detection |
| Binwalk | https://github.com/ReFirmLabs/binwalk | Entropy analysis |

---

## Step 2: Clone Reference Codebase

```bash
git clone https://github.com/bgbennyboy/DoubleFine-Explorer.git
```

This tool's source code documents the DFPF format.

---

## Step 3: Locate Game Files

Steam installation typically at:
```
C:\Program Files (x86)\Steam\steamapps\common\Brutal Legend\
```

Key directories:
```
Win\Packs\          # DFPF bundle files
Data\Config\        # Configuration files
```

---

## Step 4: Extract Game Assets

See [02_EXTRACTING_ASSETS.md](../tutorials/02_EXTRACTING_ASSETS.md)

---

## Step 5: Begin Analysis

1. Load `BrutalLegend.exe` in Ghidra
2. Run full auto-analysis
3. Start with DFPF loading functions

---

## Next Steps

- [02_EXTRACTING_ASSETS.md](../tutorials/02_EXTRACTING_ASSETS.md)
- [03_CREATING_A_MOD.md](../tutorials/03_CREATING_A_MOD.md)
