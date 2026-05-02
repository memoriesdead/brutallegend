# Extracting Game Assets

**Status:** 🔴 Planning  
**Tools Needed:** DoubleFineTool, dfpf-toolkit  

---

## Method 1: DoubleFine Explorer (GUI)

1. Download DoubleFine Explorer
2. Open `Brutal Legend` game folder
3. Select a `.~h/.~p` file pair
4. Click "Save All Files"

---

## Method 2: Command Line (dfpf-toolkit - TODO)

```bash
dfpf-toolkit extract "00Startup.~h" -o ./extracted/
```

---

## Key Bundles to Extract

| Bundle | Contents |
|--------|----------|
| `00Startup.~h/.~p` | Core prototypes (all.proto), essential scripts |
| `Man_Script.~h/.~p` | Mission Lua scripts |
| `Man_Trivial.~h/.~p` | Characters, models, textures |
| `Cutscenes\.~h/.~p` | Bink video files |

---

## Cataloging File Types

After extraction, catalog all unique file extensions:

```bash
find ./extracted -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
```

---

## Next Steps

- [03_CREATING_A_MOD.md](../tutorials/03_CREATING_A_MOD.md)
