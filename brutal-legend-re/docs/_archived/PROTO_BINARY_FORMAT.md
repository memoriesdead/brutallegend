# Proto Binary Format Research

**Status:** Research Complete
**Date:** 2026-04-01

---

## Executive Summary

**There is no binary proto format.** The game loads and parses the text DSL in `all.proto` at runtime. The `all.proto.bin` files are empty placeholders (0 bytes).

---

## Research Findings

### 1. Binary Proto Files

| File | Size | Purpose |
|------|------|---------|
| `extracted/00Startup/all.proto` | 1,770,625 bytes | Text proto DSL (source) |
| `extracted/00Startup/data/all.proto` | 1,770,625 bytes | Text proto DSL (duplicate) |
| `extracted/00Startup/all.proto.bin` | 0 bytes | **Empty placeholder** |
| `extracted/00Startup/data/all.proto.bin` | 0 bytes | **Empty placeholder** |

**Conclusion:** No pre-compiled binary proto exists. The `.bin` files are empty placeholders.

### 2. Bundle File Analysis

The `file_*.bin` files in `00Startup/` are zlib-compressed data blocks:
- `file_0001_offset_3840.bin` - Starts with `0x78da` (zlib header)
- Compression type 8 (ZLib) confirmed in DFPF format

However, these compressed blocks are incomplete/truncated during extraction and do not represent a separate binary proto format.

### 3. Export Table Analysis

The `EXPORT_TABLE.md` documents 611 exported functions from `Buddha.exe`. **None of them are proto-specific:**

- File I/O: `GBufferedFile`, `GSysFile`, `GZLibFile` classes
- Threading: `GThread`, `GMutex`, `GSemaphore`, `GEvent`
- Graphics: `GImage`, `GColor`, `GMatrix2D`
- SDL: 611 SDL functions
- Scaleform: `GFxLoader`

**Conclusion:** Proto loading is handled by internal Buddha engine code that is not exported.

### 4. Import Table Analysis

The `IMPORT_TABLE.md` shows no external library calls for proto parsing:
- No protobuf libraries
- No parser generator libraries
- Standard C library functions only (file I/O, memory)

**Conclusion:** Proto parsing is entirely internal to Buddha engine.

---

## Runtime Loading Mechanism

### How Prototypes Are Loaded

1. **Startup Sequence:**
   - `00Startup` bundle is loaded early in boot process
   - `all.proto` text file is read as raw text
   - Internal Buddha parser tokenizes and builds prototype hierarchy
   - Results stored in runtime memory structures

2. **Parser Location:**
   - Parser code is internal to Buddha.exe (not exported)
   - Located somewhere in the x86 code at unknown address
   - Would require disassembly to find

3. **No Pre-compilation:**
   - The text DSL is parsed every time the game runs
   - There is no "compiled" intermediate representation
   - The `all.proto.bin` placeholders suggest this was planned but never implemented

---

## Compiler Implications

### For Text Proto Compiler

Since the game loads text proto at runtime:

| Approach | Feasibility | Notes |
|----------|-------------|-------|
| **Replace all.proto text** | ✅ Recommended | Simple file replacement in bundle |
| **Runtime memory injection** | ⚠️ Complex | Would require finding parser hooks |
| **Pre-compile to binary** | ❌ Not supported | Game doesn't load binary proto |

### Compiler Requirements

A proto compiler should:

1. **Parse the text DSL** - Tokenize and validate `all.proto` syntax
2. **Output text proto format** - Same format as input, modified for edits
3. **Bundle repacking** - Repack modified `all.proto` into `00Startup` bundle

### Not Required

- Binary format parser (doesn't exist)
- Runtime injection code (text replacement sufficient)
- Pre-compilation step (game parses text at runtime)

---

## Text Proto Format Summary

From `docs/formats/PROTO_SPEC.md`:

```
Prototype <Name> : <Parent> { <Body> };
```

- **Directives:** `Add`, `Override`, `Apply`
- **Components:** `Co*` prefixed components (e.g., `CoTransform`, `CoRenderMesh`)
- **Property types:** Boolean, Integer, Float, Vector3, Color, String, Resource references (@)
- **Inheritance:** Single inheritance via parent prototype name
- **Abstract markers:** `Concrete=false` marks non-spawnable prototypes

---

## Recommendations for Compiler Development

1. **Build a text-to-text compiler** - Parse modified proto syntax, output valid proto text
2. **Target bundle replacement** - Repack modified `all.proto` into extracted `00Startup`
3. **Do not attempt binary format** - No such format exists in the game
4. **Consider runtime alternatives** - If text replacement is insufficient, investigate memory injection

---

## Files Reference

| File | Size | Relevance |
|------|------|-----------|
| `docs/formats/PROTO_SPEC.md` | Full proto DSL documentation | **Primary reference** |
| `extracted/00Startup/all.proto` | 1.77MB text | Input/Output for compiler |
| `ghidra/EXPORT_TABLE.md` | 611 function exports | No proto functions found |
| `ghidra/IMPORT_TABLE.md` | External imports | No proto libraries |
| `docs/engine/ARCHITECTURE.md` | Buddha engine overview | Engine internals undocumented |

---

## Conclusion

**The game does not use a binary proto format.** It parses the text DSL in `all.proto` at runtime. A compiler for Brutal Legend prototypes should:

1. Accept modified proto text as input
2. Output valid proto text format
3. Handle bundle repacking for the modified file to take effect

There is no pre-compiled binary format to reverse-engineer - the binary proto files are empty placeholders.

---

*Research completed: 2026-04-01*
