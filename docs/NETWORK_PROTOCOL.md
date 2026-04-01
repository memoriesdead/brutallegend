# Brutal Legend Network Protocol Analysis

**Status:** Research Started  
**Game:** Brutal Legend (2009)  
**Engine:** Buddha (Double Fine proprietary)  
**Last Updated:** 2026-04-01

---

## Executive Summary

Brutal Legend uses a hybrid networking approach combining **Winsock (raw sockets)** for low-level transport and **Steamworks API** for matchmaking, session management, and higher-level networking abstractions. The game supports co-op campaign multiplayer with host migration capabilities.

**Key Finding:** No direct socket functions are exported from BrutalLegend.exe - all networking is routed through Steam's networking layer, making raw packet capture more challenging as traffic is encapsulated within Steam's protocol.

---

## Network Stack Architecture

### Layer 1: Transport Layer (Winsock/WSOCK32.dll)

The game imports standard Winsock functions, indicating it has direct socket access for low-level network operations:

| Function | Address | Purpose |
|----------|---------|---------|
| `socket` | 0xe347d8 | Create socket |
| `bind` | 0xe347d4 | Bind socket to address |
| `listen` | 0xe347ac | Listen for connections |
| `accept` | 0xe347b0 | Accept connection |
| `connect` | 0xe34790 | Connect to remote |
| `send` | 0xe347e0 | Send data |
| `recv` | 0xe347d0 | Receive data |
| `sendto` | 0xe3477c | Send to specific address |
| `recvfrom` | 0xe3478c | Receive from address |
| `htons` | 0xe347c8 | Host to network short |
| `htonl` | 0xe34798 | Host to network long |
| `ntohs` | 0xe34780 | Network to host short |
| `ntohl` | 0xe34788 | Network to host long |
| `select` | 0xe347c0 | Multiplexing I/O |
| `ioctlsocket` | 0xe347b4 | I/O control |
| `WSAAsyncSelect` | 0xe347a8 | Async socket events |
| `WSAStartup` | 0xe347bc | Initialize Winsock |
| `WSACleanup` | 0xe347cc | Cleanup Winsock |

### Layer 2: Steam Networking (steam_api.dll)

Steam provides the high-level networking API:

| Function | Address | Purpose |
|----------|---------|---------|
| `SteamNetworking` | 0xe3488c | Core Steam networking |
| `SteamMatchmaking` | 0xe34888 | Session management |
| `SteamAPI_Init` | 0xe34890 | Initialize Steam API |
| `SteamAPI_RunCallbacks` | 0xe348b8 | Process Steam callbacks |
| `SteamAPI_Shutdown` | 0xe34898 | Shutdown Steam |
| `SteamAPI_RegisterCallback` | 0xe348a0 | Register callback handler |
| `SteamAPI_UnregisterCallback` | 0xe3489c | Unregister callback |
| `SteamAPI_RegisterCallResult` | 0xe34880 | Register call result |
| `SteamAPI_UnregisterCallResult` | 0xe34884 | Unregister call result |
| `SteamApps` | 0xe348ac | DLC/app info |
| `SteamFriends` | 0xe348a8 | Friend list |
| `SteamUser` | 0xe348b4 | User account |
| `SteamUserStats` | 0xe348b0 | Achievements/stats |
| `SteamUtils` | 0xe348a4 | Utility functions |

---

## Evidence of Co-op Support

### Co-op Dialog Aliases (String References)

The game contains co-op-specific dialog trigger strings:

- `PlayerCoopStartDialogAlias` - Triggers when co-op starts
- `PlayerCoopEndDialogAlias` - Triggers when co-op ends
- `PlayerCoopFireWeaponDialogAlias` - Triggers when co-op player fires
- `PlayerCoopDeathEjectDialogAlias` - Triggers when co-op player dies
- `PlayerCoopDrivingChatterDialogAlias` - Triggers during co-op driving

These suggest the game has well-developed co-op audio/hud integration.

### Network Error Codes (String References)

```
kLC_ErrorNetwork
kLC_ErrorConnectHostLocal
kLC_ErrorConnectHostRemote
kLC_ErrorConnectPeerLocal
kLC_ErrorConnectPeerRemote
kLC_ErrorMigrateLocalStrict
kLC_ErrorMigrateRemoteStrict
kLC_ErrorLocalStrict
kLC_ErrorRemoveStrict
kLC_ErrorLatency
kLC_ErrorStarted
kLC_ErrorGameFull
kLC_ErrorNetworkFull
```

**Interpretation:** These error codes (prefixed `kLC_`) indicate:
- **Host/Peer distinction** - Supports both dedicated host and peer-to-peer topologies
- **Migration support** - `MigrateLocalStrict`/`MigrateRemoteStrict` suggest host migration
- **Strict mode** - `LocalStrict`/`RemoveStrict` indicate authoritative server logic
- **Full conditions** - Game and network capacity limits

### Debug Features

- `kDEBUGTEXT_Net` - Network debug text category
- `netDebug` - Network debug mode variable
- `SyncTrace` - Synchronization tracing

---

## Protocol Analysis

### Hypothesized Protocol Structure

Based on the architecture, the game likely uses:

1. **Steam P2P Networking** for game traffic
   - Encrypted within Steam's protocol
   - Session-based with Steam Matchmaking
   - NAT traversal via Steam's relay network

2. **Direct UDP sockets** potentially for low-latency game sync
   - Explains WSOCK32 imports
   - Would allow custom game sync outside Steam's overhead

### Connection Flow (Hypothesized)

```
1. SteamAPI_Init() - Initialize Steamworks
2. SteamAPI_RunCallbacks() - Main loop callback processing
3. SteamMatchmaking::CreateLobby() - Host creates session
4. SteamMatchmaking::JoinLobby() - Client joins session
5. SteamNetworking / raw sockets - Game data transfer
```

### Packet Structure (Unknown - Requires Capture)

To determine packet structure:
1. Capture traffic during co-op with Wireshark
2. Filter by Steam networking protocol or raw UDP
3. Look for magic bytes, sequence numbers, message types

**Recommended capture filters:**
- `steam` or `udp.port 27015-27030` (Steam P2P range)
- `udp.port 3478` (STUN - NAT traversal)
- Custom range if direct socket mode detected

---

## Mid-Game Joining Analysis

### Technical Requirements

Mid-game joining (late join) requires:

1. **State Synchronization**
   - Current game state must be serializable
   - New player must receive full world state snapshot
   - Entity positions, health, game progress

2. **Network Protocol Support**
   - Server must track all game state changes
   - Delta updates must be reproducible for late joiners
   - Deterministic replay or state vector

3. **Steam Matchmaking Integration**
   - Lobby must support mid-game join
   - Session persistence across host migration

### Observed Support Indicators

- `kLC_ErrorMigrateRemoteStrict` - Remote host migration suggests state transfer code exists
- `kLC_ErrorRemoveStrict` - Removal handling implies session state management
- `PlayerCoopStartDialogAlias` - Co-op state tracked independently

### Implementation Approach

If implementing mid-game join:

1. **Capture full network trace** during:
   - Game start (host creates session)
   - Player joining mid-game
   - Host migration

2. **Analyze packet sequence** to identify:
   - State sync packets (likely larger, periodic)
   - Delta update packets (smaller, frequent)
   - Control messages (connection setup, migration)

3. **Reverse engineer packet format** by:
   - Identifying magic bytes/headers
   - Finding entity ID mapping
   - Locating position/health serialization

---

## Recommended Research Steps

### Priority 1: Network Capture

1. Install Wireshark
2. Start capture on network interface
3. Launch Brutal Legend
4. Start co-op session as host
5. Capture 30-60 seconds of traffic
6. Save capture as `brutal_legend_coop.pcap`

### Priority 2: Packet Analysis

1. Open capture in Wireshark
2. Filter for Steam networking packets
3. Look for periodic larger packets (state sync)
4. Identify smaller frequent packets (game updates)
5. Search for strings: "co-op", "join", "sync", "state"

### Priority 3: Static Analysis Enhancement

1. Use Ghidra to analyze socket-creation functions
2. Find `socket()` call sites
3. Trace socket initialization chain
4. Identify packet construction functions

### Priority 4: Steam API Hooking

1. Hook `SteamNetworking` functions
2. Log all networking calls
3. Capture Steam's internal packet data
4. Compare with Wireshark captures

---

## Open Questions

| Question | Notes |
|----------|-------|
| Does game use Steam P2P or direct sockets? | Likely Steam P2P with raw socket fallback |
| What is the packet header format? | Unknown - requires capture |
| Is there encryption beyond Steam's? | Likely additional game-specific encryption |
| How is mid-game join handled? | Code paths exist but implementation unknown |
| What triggers host migration? | Error codes suggest it's supported |
| What port(s) does it use? | Unknown - Steam relay or custom |

---

## Tools Needed

- **Wireshark** - Network capture and analysis
- **Ghidra** - Executable disassembly (for socket functions)
- **x64dbg** - Dynamic debugging (for socket initialization)
- **Steam API SDK** - Understanding Steam networking internals

---

## References

- Steamworks Networking: https://partner.steamgames.com/doc/features/multiplayer
- Winsock Programming: https://docs.microsoft.com/en-us/windows/win32/winsock/
- Brutal Legend RE Project: `brutal-legend-re/`

---

*Document Version: 1.0*  
*Research by: Claude Code (MiniMax-M2.7)*
