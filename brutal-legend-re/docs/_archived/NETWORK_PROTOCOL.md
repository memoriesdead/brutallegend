# Brütal Legend - Network Protocol Documentation

**Game:** Brütal Legend
**Executable:** BrutalLegend.exe (Buddha.exe internal)
**Platform:** Steam
**Analysis Status:** EARLY STAGE - Limited information available

---

## Overview

This document covers what is known about Brütal Legend's multiplayer and network protocol implementation. The game uses **Steamworks API** for multiplayer functionality and **Windows Sockets (Winsock/WSOCK32)** for low-level networking.

**Key Caveat:** This document contains hypothesized elements based on Steamworks patterns. The actual packet formats and protocol details have NOT been reversed yet.

---

## Known Network Architecture

### From Import Analysis (IMPORT_ANALYSIS.md)

The game imports the following network-related functions:

#### Steamworks API (steam_api.dll)

| Function | Purpose |
|----------|---------|
| `SteamAPI_Init` | Initialize Steam API |
| `SteamAPI_Shutdown` | Shutdown Steam API |
| `SteamAPI_RunCallbacks` | Process Steam callbacks |
| `SteamAPI_RegisterCallback` | Register callback handler |
| `SteamAPI_UnregisterCallback` | Unregister callback handler |
| `SteamAPI_RegisterCallResult` | Register Steam call result handler |
| `SteamAPI_UnregisterCallResult` | Unregister call result handler |
| `SteamNetworking` | Get ISteamNetworking interface |
| `SteamMatchmaking` | Get ISteamMatchmaking interface |
| `SteamFriends` | Get ISteamFriends interface |
| `SteamUser` | Get ISteamUser interface |
| `SteamUtils` | Get ISteamUtils interface |
| `SteamApps` | Get ISteamApps interface |
| `SteamUserStats` | Get ISteamUserStats interface |

#### Windows Sockets (WSOCK32.dll)

All exports are via ordinals (not analyzed in detail). This suggests:
- Custom socket wrapper classes
- Possible direct Winsock usage for game-specific networking

---

## Steamworks Integration

### Likely ISteamNetworking Functions

Based on standard Steamworks patterns, the game probably uses:

```
ISteamNetworking:
- SendP2PPacket() / ReadP2PPacket()     - Peer-to-peer messaging
- AcceptP2PSession()                    - Accept incoming connection
- CloseP2PSession()                    - Close session
- GetP2PSessionState()                 - Get connection state
- CreateListenSocket()                - Listen for connections
- CreateP2PConnectionSocket()         - Connect to peer
```

### Likely ISteamMatchmaking Functions

```
ISteamMatchmaking:
- CreateLobby()                        - Create multiplayer lobby
- JoinLobby()                          - Join existing lobby
- LeaveLobby()                         - Leave lobby
- RequestLobbyList()                   - Get available lobbies
- SetLobbyData()                       - Set lobby metadata
- GetLobbyData()                       - Get lobby metadata
- GetLobbyMemberList()                 - List players in lobby
- InviteUserToLobby()                  - Invite friend to lobby
```

### Likely ISteamFriends Functions

```
ISteamFriends:
- GetPersonaName()                    - Get player name
- SetPersonaName()                     - Set player name
- GetFriendGamePlayed()                - Check if friend is in game
```

---

## Hypothesized Multiplayer Flow

This section documents our HYPOTHESIZED multiplayer flow based on standard game networking patterns and Steamworks conventions. **This has NOT been verified by packet capture or reverse engineering.**

### 1. Lobby Creation Flow

```
Host Player                           Steam Backend
    |                                      |
    |-- CreateLobby() -------------------->|
    |<-- Lobby ID --------------------------|
    |                                      |
    |-- SetLobbyData("hostname", name) --->|
    |-- SetLobbyData("gamemode", "coop") -->|
    |-- SetLobbyData("map", "stage1") ---->|
    |                                      |
    |-- CreateListenSocket() ------------->|
    |<-- Listen Socket Ready --------------|
```

### 2. Player Join Flow

```
Client Player       Host Player         Steam Backend
    |                    |                     |
    |-- RequestLobbyList()------------------->|
    |<-- Lobby List---------------------------|
    |                    |                     |
    |-- JoinLobby() ------------------------>|
    |               |-- LobbyMemberJoined --->|
    |<-- JoinOK ---------------------------|
    |                    |                     |
    |-- GetLobbyData() --|<--------------------|
    |<-- Host Info --------------------------|
    |                    |                     |
    |-- CreateP2PConnectionSocket() ------->|
    |               |-- IncomingConnection -->|
    |<-- Connection Established ------------|
    |                    |                     |
    |-- AcceptP2PSession() ----------------->|
    |-- SendP2PPacket(JOIN_REQUEST) ------->|
    |               |-- ReadP2PPacket() ----|
    |               |-- SendP2PPacket(JOIN_ACCEPT) -->|
    |<-- ReadP2PPacket(JOIN_ACCEPT) -------|
```

### 3. Game State Synchronization (Hypothesized)

```
Game Start:
- Host sends INITIAL_STATE packet to all clients
- Clients respond with SYNC_REQUEST for missing data
- Host sends SYNC_RESPONSE with full state

During Gameplay:
- Host is authoritative
- Clients send INPUT packets (movement, actions)
- Host broadcasts WORLD_UPDATE packets
- Periodic STATE_HASH packets for anti-cheat
```

---

## Known Issues with Multiplayer

Based on community reports and Steam forums:

1. **No LAN Play** - Game does not support direct IP connections
2. **NAT Traversal** - Relies entirely on Steam's P2P networking
3. **Firewall Issues** - Some users report connection problems
4. **Host Migration** - Does not appear to be implemented
5. **Cross-Platform** - Not supported (Windows only)

---

## Port Usage (Unverified)

Based on Steam general behavior, these ports **may** be used:

| Port | Service | Status |
|------|---------|--------|
| 27015 | Steam Master Server | Possible |
| 27016 | Steam Client | Possible |
| 27017-27030 | Steam Relay | Possible |
| 27031-27039 | Steam Dedicated Server | Unlikely (no dedicated server) |

**Note:** Actual port usage has NOT been verified by packet capture.

---

## Network Traffic Capture

### Tools Available

See `tools/network-sniffer/network_sniffer.py` for a Python-based packet capture utility.

### Methodology

To discover actual protocol details:

1. Run the sniffer during multiplayer session
2. Capture traffic on Steam-related ports
3. Analyze packet sizes and timing
4. Look for patterns in payload sizes
5. Compare with hypothesized flows above

### Expected Challenges

1. **Steam encryption** - P2P traffic may be encrypted
2. **Protocol complexity** - Game-specific protocol unknown
3. **State synchronization** - Large binary state transfers
4. **Real-time requirements** - Latency-sensitive traffic

---

## Reverse Engineering Targets

To enable custom multiplayer/modding support, the following need to be reversed:

### High Priority

1. **Lobby Data Format**
   - How is lobby metadata structured?
   - What fields does the game use?

2. **Join Handshake**
   - What packets are exchanged during connection?
   - How does host authenticate clients?

3. **Game State Sync**
   - What triggers state synchronization?
   - What is the format of world updates?

### Medium Priority

4. **Input Protocol**
   - How are player inputs encoded?
   - What is the input packet format?

5. **Entity State Format**
   - How are game objects synchronized?
   - What data is sent per entity?

### Low Priority (Speculative)

6. **Audio Chat**
   - Does game use Steam voice or custom?
   - What codecs are used?

---

## References

- Steamworks Documentation: https://partner.steamgames.com/
- ISteamNetworking: https://partner.steamgames.com/doc/api/steam_api#ISteamNetworking
- ISteamMatchmaking: https://partner.steamgames.com/doc/api/steam_api#ISteamMatchmaking

---

## Document History

| Date | Changes |
|------|---------|
| 2026-04-01 | Initial document created |

---

*This document is part of the Brütal Legend Reverse Engineering project.*
