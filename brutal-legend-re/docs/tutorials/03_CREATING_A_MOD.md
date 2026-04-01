# Creating Your First Mod

**Status:** 🔴 Planning  
**Prerequisites:** Extracted assets  

---

## Simple Mod: Character Swap

### 1. Locate all.proto

In `00Startup.~h/.~p`, find `all.proto`

### 2. Understand Prototype Format

See [docs/formats/PROTO_SPEC.md](../formats/PROTO_SPEC.md)

### 3. Make Your Change

Example: Replace Eddie with Doviculus
- Find `Prototype A01_Avatar :` section
- Replace contents with `Prototype D01_Avatar :` data

### 4. Repack

```bash
dfpf-toolkit repack 00Startup.~h -i ./modified/ -o 00Startup_new.~h
```

### 5. Install Mod

Copy to `Win\Packs\` folder

---

## Testing

- [ ] Single player loads
- [ ] Character displays correctly
- [ ] No crashes

---

## Troubleshooting

- Disable checksum: `BuddhaDefault.cfg` → `net.bEnableBackgroundChecksum = false`
- Check game logs for errors

---

## Next Steps

- [04_ADVANCED_REVERSING.md](../tutorials/04_ADVANCED_REVERSING.md)
