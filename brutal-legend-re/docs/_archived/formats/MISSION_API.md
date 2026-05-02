# Mission Scripting API

**Status:** 🟢 Documented  
**Game:** Brutal Legend  
**File:** Man_Script.~h/.~p  
**Extracted:** 102/266 Lua scripts (41 zlib streams + uncompressed files)
**Last Updated:** 2026-04-01

---

## Overview

Brutal Legend uses a **Lua-based mission scripting system** built on the Buddha engine. Missions control story progression, objectives, combat encounters, and events.

### Key Files

- `Man_Script.~h/.~p` - Contains 266 Lua scripts
- `missionbase.lua` - Base class for all missions (818 lines)
- `scriptbase.lua` - Core scripting utilities
- `missiondescriptors.lua` - Mission definitions and configuration

---

## Mission Structure

### Class Hierarchy

```lua
-- Base class (from ScriptBase)
local Ob = CreateObject("ScriptBase")

-- Mission classes inherit from:
CreateObject("Missions.PrimaryMission")   -- Main campaign missions
CreateObject("Missions.SecondaryMission") -- Side missions
CreateObject("MissionBase")              -- Generic mission base
```

### Mission Properties

```lua
Ob.MissionCode = "P1_010"              -- Unique mission identifier
Ob.MissionIntroLineCode = "TOJE001TEXT" -- Intro text code
Ob.MissionObjectiveLineCode = "TOJE026TEXT" -- Objective text code
Ob.DialogResource = RESOURCE("Missions/Campaign/Dialog/P1_010", "DialogSets")
Ob.CompleteCheckpointLoc = "P1_010_MissionEnd"
Ob.IsAbortCheckpoint = false
Ob.AbortCheckpointLoc = "P1_010_Locator_AltarActionStart"
```

### Mission Array (for multi-part missions)

```lua
Ob.Missions = {
    { MissionName = "P1_010/P1_010_TempleInterior" },
    { MissionName = "P1_010/P1_010_DriveToBridge" },
    { MissionName = "P1_010/P1_010_LampreyArenaIntro", Data = "Lamprey" },
}
```

---

## Mission Callbacks

### Core Callbacks

| Callback | Description |
|----------|-------------|
| `OnMissionStart(loadFromSave, alreadyStarted)` | Called when mission begins |
| `OnMissionComplete()` | Called when all objectives finished |
| `OnMissionEnd()` | Called when mission exits |
| `OnMissionFail()` | Called when mission fails |
| `OnAbortResult(bAbandoning)` | Called on mission abort |
| `OnMissionAreaStatus(eStatus)` | Called when entering/leaving mission area |
| `OnCutsceneDone(cs)` | Called when cutscene ends |

### Notification Callbacks

| Callback | Description |
|----------|-------------|
| `OnKilled(entity)` | Entity was killed |
| `OnTimerExpired(id)` | Timer finished |
| `OnTriggerEntered(trigger, entity)` | Entity entered trigger |
| `OnTriggerExited(trigger, entity)` | Entity exited trigger |
| `OnEntityOnScreen(entity)` | Entity appeared on screen |
| `OnEntityHealthLevelReached()` | Health threshold reached |
| `OnDialogSetDone(setname)` | Dialog finished |
| `OnMessageReceived(messageName, messageData, entity)` | Message received |

---

## Game API

### Player Functions

```lua
game.GetPlayer(playerIndex)              -- Get player entity
game.GetPlayerPos()                      -- Get player position
game.GetLocalPlayerIndex()               -- Get local player index
game.GetTeamType(entity)                 -- Get team number
game.TeleportPlayer(player, locator)     -- Teleport to locator
game.TeleportPlayer(player, x, y, z)    -- Teleport to coordinates
```

### Mission Functions

```lua
game.StartMission(missionName, mission)   -- Start a sub-mission
game.EndMission(mission)                 -- End current mission
game.EndMission(mission, bForce)        -- Force end mission
game.GetActiveMission()                  -- Get current mission
game.GetGameMission()                    -- Get game mission object
game.GetMissionName(mission)             -- Get mission name
game.IsMissionComplete(missionCode)      -- Check if mission done
game.GetPercentageGameCompleted()         -- Get completion percentage
```

### Spawn Functions

```lua
game.SpawnAtPosition(proto, domain, x, y, z, team, bAddToPopcap)
game.SpawnAtEntity(proto, domain, locator, team, bAddToPopcap, bSetAtTerrain)
game.SpawnSimple(proto, domain)          -- Spawn simple entity
game.DropDeuce(player, bDestroy, proto, domain, locator) -- Drop Deuce companion
```

### Notification Functions

```lua
game.AddNotification(notification, mission) -- Add notification
game.RemoveNotification(handle, mission)    -- Remove notification
game.QueueCommand(command, bWait)         -- Queue game command
```

### Order Functions

```lua
game.OrderGroupToMove(group, x, y, z, bFormUp)
game.OrderGroupToAttackGroup(attackerGroup, defenderGroup, bFormUp)
game.OrderGroupTo defend(group, x, y, z)
game.OrderGroupToCharge(group, target)
```

### Camera Functions

```lua
game.CameraHintClear(player)
game.CameraSnapToIdeal(player)
game.GetAbsPosition(entity)
```

### Team Constants

```lua
kTEAM_Player0      -- Player team
kTEAM_Hostile      -- Enemy team
kTEAM_Neutral      -- Neutral team
```

---

## Dialog API

```lua
dialog.SetDialogSetForDialogType(player, dialogType, dialogResource, callback)
dialog.Play(player, dialogResource, dialogName)
dialog.SetEntityForDialog(dialogName, entity)

-- Notification callbacks used:
NotifyOnDialogSetDone -- Dialog finished playing
```

---

## HUD API

```lua
hud.DisplayElement(element, bShow)     -- Show/hide HUD element
hud.SetElementText(element, text)       -- Set element text
hud.EnableElement(element, bEnable)    -- Enable/disable element

-- Common HUD elements:
kHUD_All, kHUD_Hints, kHUD_Health, kHUD_Solos
```

---

## Sound/Music API

```lua
sound.LoadGroup(groupName, bStream)     -- Load sound group
sound.MuteCategory(category, bMute)     -- Mute sound category

music.EnableAmbient(bEnable)            -- Toggle ambient music
music.SetCurrent(musicResource)         -- Set current music
music.GotoState(state)                  -- Go to music state
music.EnableStageBattleMusic(bEnable)   -- Toggle stage battle music

playlist.EnablePlaylistManager(bEnable)  -- Toggle playlist
```

---

## RTTI API (Entity System)

```lua
rtti.GetEntityNamed(name)               -- Get entity by name
rtti.GetClassName(entity)               -- Get entity class
rtti.GetName(entity)                    -- Get entity name
rtti.IsA(entity, className)             -- Check if entity is class
rtti.GetComponent(entity, componentName) -- Get component
rtti.IterEntities()                     -- Iterate all entities
rtti.IterComponents(entity)              -- Iterate entity components
rtti.SendMessage(message, entity)        -- Send message to entity
rtti.CreateMessage(messageName)          -- Create message
rtti.GetAttribute(component, attrName)   -- Get component attribute
rtti.SetAttribute(component, attrName, value) -- Set attribute
```

---

## Objective API

```lua
game.AddObjective(objectiveText, mission) -- Add objective
game.RemoveObjective(objectiveHandle)    -- Remove objective
game.RemoveAllObjectives(mission)        -- Remove all objectives
game.UpdateObjective(objectiveHandle, text) -- Update objective text
```

---

## Profile/Unlock API

```lua
profile.UnlockAchievement(achievementId)
frontend.SetConceptArtUnlockStat(unlockId, value)
```

---

## Ability/Tech API

```lua
game.LearnAbility(abilityId)            -- Learn ability
game.UnlearnAbility(abilityId)         -- Unlearn ability
game.UnlearnAllRockSolos()               -- Unlearn all solos
game.LockAllUpgrades(teamNum)            -- Lock all upgrades

-- Ability constants:
kPA_Movement, kPA_Camera, kPA_BasicControls
kPA_EnteredVehicle, kPA_ExitedVehicle
kPA_MeleeAttack, kPA_MeleeBlock, kPA_ZTarget
kPA_Boost, kPA_Nitro

-- Order constants:
kOA_AnyOrder, kOA_FollowOrder, kOA_ChargeOrder, kOA_DefendOrder
```

---

## PROTO Helper

```lua
PROTO("PrototypeName")                  -- Get prototype by name
RESOURCE("Path", "Type")                -- Get resource
```

---

## Example Mission

```lua
local Ob = CreateObject("Missions.PrimaryMission")

Ob.MissionCode = "P1_010"
Ob.MissionIntroLineCode = "TOJE001TEXT"
Ob.MissionObjectiveLineCode = "TOJE026TEXT"
Ob.DialogResource = RESOURCE("Missions/Campaign/Dialog/P1_010", "DialogSets")

function Ob:OnMissionStart(loadFromSave, alreadyStarted)
    if not alreadyStarted then
        Trace("Starting p1_010")
        
        local player = game.GetPlayer(0)
        local locator = rtti.GetEntityNamed("P1_010_Locator_Start")
        game.TeleportPlayer(player, locator)
        
        -- Set objective
        self.objective = game.AddObjective("Drive to the bridge", self)
        
        -- Play dialog
        dialog.Play(player, self.DialogResource, "IntroDialog")
    end
end

function Ob:OnKilled(entity)
    -- Check if objective enemy killed
end

function Ob:OnMissionComplete()
    Trace("Mission complete!")
    game.EndMission(self)
    profile.UnlockAchievement(kACHV_PROG_P1_010)
end
```

---

## Secondary Mission Types

### Ambush Mission
```lua
CreateObject("MissionBase")  -- Base type
Ob.RewardAmount = 25         -- Cash reward
Ob.IsCheckpoint = true       -- Creates checkpoint
Ob.AmbushMissions = {"S1_11", "S1_17", ...}  -- Available ambush missions
```

### Race Mission
```lua
Ob.OpponentProto = "PrototypeName"  -- Opponent to race
Ob:NotifyOnPlayerOrder(...)         -- Track player orders
Ob:nextMilestone(instigator)         -- Progress callback
```

### Holdout Mission
```lua
Ob.StartEnemySpawnTimer()            -- Start enemy waves
Ob.StartNextWave()                   -- Spawn next wave
Ob:GetElapsedTime()                  -- Get time elapsed
Ob:AddTime(time)                     -- Add time
```

### Hunt Mission
```lua
Ob:setupContactDialog()             -- Setup contact dialog
Ob:enableMissionAbilities()          -- Enable abilities
Ob:WinIt()                           -- Win condition
```

---

## Extractable Scripts Inventory

### Total Scripts Found: 266

### Categories:
- Base scripts: 3 (buddhastartup, missionbase, scriptbase)
- Mission scripts: 240+
- Comp opponents: 8
- Utilities: 12+

### Primary Mission Chapters:
- P1_010 through P1_120: Act 1 missions (14 chapters)
- P2_010 through P2_060: Act 2 missions (12 chapters)

### Stage Missions:
- S1_01 through S1_32: Stage 1 missions (32 missions)
- S2_01 through S2_24: Stage 2 missions (24 missions)

### Secondary Mission Types:
- ambushmission.lua
- chasedown.lua
- escortmission.lua
- holdoutmission.lua
- huntmission.lua
- mortardefensemission.lua
- outpostdefensephase1/2.lua
- racemission.lua
- recordedracemission.lua

---

## Notes

- Scripts use **Lua 5.x** with custom Buddha engine extensions
- Missions inherit from `CreateObject()` classes
- Uses **notification system** for event handling
- **RTTI system** provides entity/component access
- **Stage Battle mode** uses RTS-style group commands

---

*Documented from extracted Lua source analysis - 2026-04-01*

