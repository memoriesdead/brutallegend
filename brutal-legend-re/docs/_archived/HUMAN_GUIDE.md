# Brutal Legend Modding - Plain English Guide

## What Did We Actually Do?

We took apart the game like a car mechanic. Now we know:
- Where every part is
- How it connects
- What each part does

---

## Can We Mod It? Yes and No.

### ✅ THESE WE CAN MOD

| You Want To... | Can We? | How |
|----------------|---------|-----|
| Change unit health, damage, speed | YES | Edit prototype files |
| Create new soldiers/vehicles | YES | Use prototype editor |
| Edit map terrain (hills, valleys) | YES | Use terrain editor |
| Create new missions | YES | Use mission editor |
| Change textures (skins, materials) | YES | Extract, edit, repack DDS files |
| Add/replace audio | YES | Extract audio with tool |
| Replace existing models | YES | Edit model files |

### ❌ THESE WE CANNOT MOD

| You Want To... | Why Not? |
|---------------|----------|
| Add new voice acting | Audio system too complicated |
| Make bigger maps | Game engine limits map size |
| Join game mid-play | Network code not cracked |
| Add grass that moves/grows | Grass is a shader (code), not data |
| Change combat mechanics | Combat rules are hardcoded |
| Add new animations | Animation system tied to code |

---

## Think Of It Like This

### Game = House
- **Foundation** = Game engine (Buddha) - CANNOT change
- **Walls** = Game systems (combat, networking) - CANNOT change
- **Furniture** = Content (units, textures, missions) - CAN change
- **Paint** = Textures on furniture - CAN change

**We can rearrange furniture and repaint. We can't move walls or change the foundation.**

---

## What Can Actually Change?

### CREATIVELY
- ✅ New custom units (your own soldier types)
- ✅ New missions with your own objectives
- ✅ Terrain edits (reshape the land)
- ✅ Texture replacers (custom skins)
- ✅ Repainted maps (different terrain colors)

### GAMEPLAY
- ✅ Change unit stats (health, damage, speed)
- ✅ Create new unit types
- ✅ Design new missions
- 🔶 Modify existing voice lines (replace file, not add new)
- ❌ Add new voice acting (can't add new audio files to game)

### MULTIPLAYER
- ❌ Mid-game join (network code not cracked)
- ❌ True co-op campaign (network protocol unknown)
- 🔶 Host/join at start (might work if mod loader works)

---

## What We Made

Think of these as power tools:

| Tool | What It Does |
|------|--------------|
| **dfpf_extract.py** | Unpacks game bundles (like unzipping) |
| **dfpf_repack.py** | Repacks bundles (like re-zipping) |
| **proto_editor.py** | Edits unit/vehicle/building definitions |
| **mission_editor.py** | Creates new missions |
| **terrain_editor.py** | Changes map height |
| **heightfield_view.py** | Views terrain |
| **fsb_extract.py** | Extracts audio files |

---

## How To Actually Make A Mod

### 1. EXTRACT
Take game files out of bundle.
```
python dfpf_extract.py game_bundle.~h output_folder/
```

### 2. EDIT
Change what you want using power tools.

### 3. REPACK
Put files back into bundle.
```
python dfpf_repack.py original_bundle.~h modified_folder/ mymod
```

### 4. TEST
Put your mod in the Mods folder and run game.

---

## Real Examples

### "I want to make my own soldier"
```bash
# Create new soldier
python proto_editor.py create SuperSoldier --parent Character --template infantry

# Give him 1000 health
python proto_editor.py edit SuperSoldier --set "CoDamageable:MaxHealth=1000"

# Export
python proto_editor.py export --output all_modified.proto

# Then repack into 00Startup bundle
```

### "I want to create a new mission"
```bash
# Create mission from template
python mission_editor.py create MyMission --template campaign --mission-code P1_999

# Edit it with mission_editor.py
# Then repack into Man_Script bundle
```

### "I want to change terrain"
```bash
# View terrain
python heightfield_view.py map.Heightfield output.png

# Edit terrain (raise a hill)
python terrain_editor.py paint map.Heightfield -x 64 -y 64 -r 10 -s 0.5 -m raise

# Export and repack
```

---

## What's Still Missing?

| Feature | Status |
|---------|--------|
| Mod loader (auto-load from folder) | 🔶 Need to test |
| Network code (mid-game join) | ❌ Not done |
| Voice system (add new audio) | ❌ Not done |
| Bigger maps | ❌ Engine limit |

---

## TL;DR Summary

**WE CAN:**
- Take apart the game
- Change textures
- Change terrain
- Create new units
- Create new missions
- Change unit stats
- Replace audio

**WE CANNOT:**
- Add new voice acting
- Make bigger maps
- Enable mid-game joining
- Change game engine
- Add new shaders
- Modify combat rules

---

## Bottom Line

**We can mod 70-80% of the CONTENT. We cannot mod the ENGINE.**

Think of it like Skyrim modding vs. making a new game engine. We can add mods to the game, but we can't make the game do things it wasn't designed to do.

**We reverse engineered the GAME. We didn't reverse engineer the GAME ENGINE.**

---

## Can A Normal Person Do This?

**Kind of.** You need to:
1. Install Python
2. Follow the commands
3. Be careful not to break things

It's not point-and-click. But it's also not coding from scratch.

**If you can follow a recipe, you can mod.**
