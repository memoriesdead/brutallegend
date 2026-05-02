# Brutal Legend Modding - Simple Guide

**For: Normal People Who Want To Mod The Game**

---

## What We Did

We reverse engineered Brutal Legend. That means we figured out how the game works from the inside out.

### Think of it like this:

| Real World | Game |
|-----------|------|
| Blueprints | File formats |
| Ingredients | Game data |
| Recipe | How to modify |

We found the game's **blueprints** and now we can:
- Take the game apart (extract)
- Change things (modify)
- Put it back together (repack)
- Add new stuff (create mods)

---

## What You Can Do NOW

### 1. Extract Game Content
Pull anything out of the game - models, textures, audio, missions.

**Command:**
```bash
python dfpf_extract.py "Win/Packs/Man_Script.~h" output_folder/
```

### 2. Edit Prototypes (Units, Buildings, Vehicles)
Prototypes = how the game defines characters and objects.

**Example:** Change how much health a unit has.

```bash
# Show a unit's stats
python proto_editor.py show A01_Avatar

# Change health from 400 to 500
python proto_editor.py edit A01_Avatar --set "CoDamageable:MaxHealth=500"

# Export changes
python proto_editor.py export --output all_modified.proto
```

### 3. Create New Units
Make your own soldiers, vehicles, buildings.

```bash
# Create a new soldier
python proto_editor.py create MySoldier --parent Character --template infantry

# Edit it
python proto_editor.py edit MySoldier --set "CoTeam:Faction=kFT_A"
```

### 4. Edit Missions
Create new campaign missions or modify existing ones.

```bash
# List all missions
python mission_editor.py list

# Create a new mission
python mission_editor.py create MyMission --template campaign --mission-code P1_999
```

### 5. Edit Terrain (Maps)
Change the landscape, hills, valleys.

```bash
# View a heightfield
python heightfield_view.py terrain.Heightfield output.png

# Edit terrain (raise/lower)
python terrain_editor.py paint terrain.Heightfield -x 64 -y 64 -r 10 -s 0.5 -m raise
```

### 6. Repack Everything
Put modified files back into the game.

```bash
# Repack a bundle
python dfpf_repack.py "Win/Packs/00Startup.~h" extracted_folder/ output_name
```

---

## What Is Everything?

### Bundles (~h/.~p files)
The game stores content in **bundles**. Think of them like ZIP files.

- `Win/Packs/00Startup.~h` - Core game stuff
- `Win/Packs/Man_Script.~h` - Mission scripts
- `Win/Packs/RgS_World.~h` - Map data

### Prototypes
How the game defines **what something is**.

```
Prototype A01_Avatar : Character { ... }
     ↑              ↑       ↑
   Name         Parent    What it does
```

### Missions
Lua scripts that tell the game what to do in a mission.

### Heightfields
**128x128 pixel images** that define terrain height. Think of it like a grayscale map:
- White = high
- Black = low

### DDS Files
Compressed image files the game uses for textures and heightmaps.

---

## How To Make A Mod

### Step 1: Extract
Pull content from a bundle.

### Step 2: Modify
Change what you want using the tools.

### Step 3: Repack
Put it back in a bundle.

### Step 4: Test
Copy to `Win/Mods/` and run the game.

---

## Mod Folder Location

```
Steam/steamapps/common/BrutalLegend/
└── Win/
    ├── Packs/          ← Original game bundles
    └── Mods/          ← YOUR MODS GO HERE
```

**Important:** Create the `Mods` folder yourself if it doesn't exist.

---

## Quick Commands Reference

| What | Command |
|------|---------|
| Extract bundle | `python dfpf_extract.py <bundle.~h> <output/>` |
| List prototypes | `python proto_editor.py list` |
| Show unit | `python proto_editor.py show <Name>` |
| Edit unit | `python proto_editor.py edit <Name> --set "Property=Value"` |
| Create unit | `python proto_editor.py create <Name> --parent <Parent> --template <type>` |
| Validate proto | `python proto_editor.py validate` |
| Export proto | `python proto_editor.py export --output <file>` |
| List missions | `python mission_editor.py list <folder/>` |
| Create mission | `python mission_editor.py create <Name> --template <type>` |
| View terrain | `python heightfield_view.py <file.Heightfield> <output.png>` |
| Edit terrain | `python terrain_editor.py paint <file.Heightfield> -m raise --strength 0.5` |
| Repack bundle | `python dfpf_repack.py <original.~h> <folder/> <output>` |

---

## What Works

| Feature | Status |
|--------|--------|
| Extract game content | ✅ WORKS |
| Edit prototypes | ✅ WORKS |
| Create new units | ✅ WORKS |
| Edit missions | ✅ WORKS |
| Edit terrain | ✅ WORKS |
| Repack bundles | ✅ WORKS |
| Load mods | 🔶 UNTESTED |
| Co-op mid-game | ❌ NOT DONE |
| Workshop support | ❌ NOT DONE |

---

## Troubleshooting

### "Command not found"
Make sure you're in the right folder and Python is installed.

### "File not found"
Check the path to the bundle is correct.

### "Game crashes"
You may have made an error in the data. Try again with a smaller change.

---

## Need Help?

Ask in the project discussions. Include:
- What you tried to do
- What happened
- What the error message said (if any)

---

## Summary

**YES, you can mod the game now.**

The tools are ready. The process is:
1. Extract
2. Modify
3. Repack
4. Test

The only thing not verified is whether the game will actually load your mods from `Win/Mods/`. That's the next test to do.
