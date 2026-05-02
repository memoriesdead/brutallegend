## Debugging & Developer Tools
*Identified via string analysis and memory dumps. These tools were likely used by Double Fine developers for testing and balancing.*

### 1. Debug Menu & Overlay
*   **`allowDebugMenu`** (`0x00e73ba0`): Master toggle for the in-game debug menu. Likely checked by the input handler to determine if the debug overlay should be drawn or if debug keybinds are active.
*   **`ToggleDebugUI`** (`0x00e973e0`): Function or command to show/hide the debug information overlay.
*   **`DebugRender_ToggleTagEnabled`** (`0x00e89610`): Toggles specific rendering tags, such as hitboxes, bone names, or collision spheres.

### 2. Debug Text Categories (`kDEBUGTEXT_...`)
*These strings control what specific information is displayed on the debug overlay. They are likely used in a lookup table or switch statement within the rendering loop.*
*   `kDEBUGTEXT_Graphics`: FPS, draw calls, GPU stats.
*   `kDEBUGTEXT_Profiler`: CPU timing for various game systems.
*   `kDEBUGTEXT_PlayerPosition`: Current coordinates and orientation.
*   `kDEBUGTEXT_Camera`: Camera state, target, and FOV.
*   `kDEBUGTEXT_SAI`: Strategic AI decision-making logs.
*   `kDEBUGTEXT_Net`: Networking latency and packet info.
*   `kDEBUGTEXT_Memory`: Heap usage and fragmentation.

### 3. Cheats & Developer Commands
*   **`enableDebugFlying`** (`0x00e73a00`): Enables "noclip" or free-camera mode, allowing the player/dev to fly through the map.
*   **`bDisplayDebugUnitHealth`** (`0x00e73928`): Forces health bars or numeric health values to be visible for all units.
*   **`DebugTeamSkirmish`** (`0x00e741fc`): Likely a command to instantly start a test battle or skirmish map.
*   **`devMaps`** (`0x00e74210`): Enables access to development-only maps or test levels.

### 4. How to Find the Debug Menu Keybind
To find the key that opens the debug menu:
1.  In Ghidra, find the cross-references to **`allowDebugMenu`** (`0x00e73ba0`).
2.  Look for the function that reads this flag. It will likely be part of the **Input Handling** system.
3.  Trace back from that function to find where it checks for specific key codes (e.g., `VK_F1`, `VK_OEM_3` for the tilde key).
