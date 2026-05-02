# Brütal Legend - Protocol Specification

**Status:** DRAFT - Contains hypothesized elements
**Priority:** Low (multiplayer modding not yet a focus)

---

## Purpose

This document outlines what would need to be reversed to enable custom multiplayer functionality, modding support, or LAN play for Brütal Legend.

---

## Known Multiplayer Functions (from Import Analysis)

### Steamworks Functions

These functions are imported from `steam_api.dll` and represent the game's Steam integration:

#### Initialization
```
SteamAPI_Init
SteamAPI_Shutdown
SteamAPI_RunCallbacks
SteamAPI_RegisterCallback
SteamAPI_UnregisterCallback
SteamAPI_RegisterCallResult
SteamAPI_UnregisterCallResult
```

#### Networking Interface
```
SteamNetworking  -->  ISteamNetworking
```

Likely used for:
- P2P packet sending/receiving
- Socket management
- Connection state tracking

#### Matchmaking Interface
```
SteamMatchmaking  -->  ISteamMatchmaking
```

Likely used for:
- Lobby creation/joining
- Player list management
- Lobby metadata

#### Other Interfaces
```
SteamFriends      -->  ISteamFriends
SteamUser         -->  ISteamUser
SteamUtils        -->  ISteamUtils
SteamApps         -->  ISteamApps
SteamUserStats    -->  ISteamUserStats
```

---

## Hypothesized Packet Flow

### Lobby Creation

```
Client A                    Steam                    Client B
   |                          |                          |
   |----- CreateLobby() ----->|                          |
   |<---- LobbyCreated -------|                          |
   |                          |                          |
   |                    Someone Joins                    |
   |                          |                          |
   |<--- LobbyMemberJoined ---|<--- JoinLobby() ---------|
   |                          |                          |
   |                    Handshake                         |
   |                          |                          |
   |<====== P2P Connection Established =======>|
   |                          |                          |
   |----- JoinRequest ------>|<----- JoinRequest -------|
   |<---- JoinResponse -------|----> JoinResponse ------>|
   |                          |                          |
```

### Game Start Sequence

```
Host                        Clients
   |                            |
   |-- SEND_GAME_START -------->|  (Lobby locked)
   |-- SYNC_INITIAL_STATE ----->|
   |   (Full world state)       |
   |<-- SYNC_ACK ---------------|
   |                            |
   |======= GAME LOOP ==========|
   |                            |
   |-- WORLD_UPDATE ----------->|  (Periodic, ~10-30 Hz)
   |<-- PLAYER_INPUT -----------|
   |                            |
```

---

## Reversing Checklist

### Phase 1: Basic Connectivity

- [ ] Confirm port usage (capture traffic with sniffer)
- [ ] Identify if Steam P2P or raw sockets
- [ ] Document lobby data structure
- [ ] Find join handshake packets

### Phase 2: Game State

- [ ] Capture initial state sync packet
- [ ] Identify entity format
- [ ] Find world update format
- [ ] Document timing/heartbeat

### Phase 3: Gameplay

- [ ] Identify input packet format
- [ ] Find player action packets
- [ ] Identify game-specific protocols (battles, objectives)
- [ ] Find audio/voice protocol (if any)

---

## What We DON'T Know

1. **Packet formats** - No binary format documentation exists
2. **Encryption** - Unknown if Steam P2P adds encryption
3. **Port numbers** - Actual ports used unconfirmed
4. **Protocol version** - Unknown if protocol has versioning
5. **Anti-cheat** - Unknown what validation exists

---

## Tools Needed for Further Discovery

1. **network_sniffer.py** - Basic packet capture (see `tools/network-sniffer/`)
2. **Wireshark** - Detailed protocol analysis
3. **IDA Pro / Ghidra** - Binary analysis of network code
4. **Steam API dump** - Static analysis of Steam calls

---

## Open Questions

1. Does the game use Steam's built-in relay or direct connections?
2. Is there any custom encryption beyond Steam's?
3. What is the maximum player count per lobby?
4. Does the host have special authority, or is there peer-to-peer logic?
5. Are there dedicated server builds, or only listen servers?

---

## Related Documentation

- `NETWORK_PROTOCOL.md` - General network architecture
- `tools/network-sniffer/network_sniffer.py` - Packet capture utility
- `docs/engine/IMPORT_ANALYSIS.md` - Steam API imports reference

---

*Part of the Brütal Legend Reverse Engineering Project*
