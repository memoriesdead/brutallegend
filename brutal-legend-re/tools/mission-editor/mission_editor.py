#!/usr/bin/env python3
"""
Brutal Legend Mission Script Editor

A tool to analyze, edit, and create new mission scripts for Brutal Legend.
"""

import argparse
import os
import re
import sys
import glob as glob_module
from pathlib import Path
from typing import Optional


# ============================================================================
# MISSION PARSER
# ============================================================================

class MissionParser:
    """Parse Brutal Legend mission scripts and extract structure."""

    # Regex patterns for mission components
    PATTERNS = {
        'class': re.compile(r"CreateObject\(['\"]([^'\"]+)['\"]\)"),
        'mission_code': re.compile(r"Ob\.MissionCode\s*=\s*['\"]([^'\"]+)['\"]"),
        'intro_line': re.compile(r"Ob\.MissionIntroLineCode\s*=\s*['\"]([^'\"]+)['\"]"),
        'objective_line': re.compile(r"Ob\.MissionObjectiveLineCode\s*=\s*['\"]([^'\"]+)['\"]"),
        'dialog_resource': re.compile(r"Ob\.DialogResource\s*=\s*RESOURCE\(['\"]([^'\"]+)['\"]"),
        'checkpoint': re.compile(r"Ob\.CompleteCheckpointLoc\s*=\s*['\"]([^'\"]+)['\"]"),
        'abort_checkpoint': re.compile(r"Ob\.AbortCheckpointLoc\s*=\s*['\"]([^'\"]+)['\"]"),
        'is_abort': re.compile(r"Ob\.IsAbortCheckpoint\s*=\s*(true|false)"),
        'sub_mission': re.compile(r"MissionName\s*=\s*['\"]([^'\"]+)['\"]"),
        'sub_mission_data': re.compile(r"MissionName\s*=\s*['\"][^'\"]+['\"].*?Data\s*=\s*['\"]([^'\"]+)['\"]"),
        'function': re.compile(r"function\s+Ob:(\w+)\s*\("),
        'entity_get': re.compile(r"rtti\.GetEntityNamed\s*\(['\"]([^'\"]+)['\"]\)"),
        'spawn_position': re.compile(r"game\.SpawnAtPosition\s*\(\s*PROTO\s*\(\s*['\"]([^'\"]+)['\"]"),
        'spawn_entity': re.compile(r"game\.SpawnAtEntity\s*\(\s*PROTO\s*\(\s*['\"]([^'\"]+)['\"]"),
        'teleport': re.compile(r"game\.TeleportPlayer\s*\([^)]+\)\s*--\s*([^\n]+)"),
        'objective_add': re.compile(r"game\.AddObjective\s*\(\s*['\"]([^'\"]+)['\"]"),
        'ability': re.compile(r"game\.(Learn|Unlearn)Ability\s*\(\s*(kPA_\w+)"),
        'solo': re.compile(r"game\.LearnRockSolo\s*\(\s*['\"]([^'\"]+)['\"]"),
        'order': re.compile(r"game\.(Learn|Set)Order\s*\(\s*(kOA_\w+)"),
        'tech': re.compile(r"game\.LearnTech\s*\(\s*[^,]+,\s*['\"]([^'\"]+)['\"]"),
        'achievement': re.compile(r"profile\.UnlockAchievement\s*\(\s*(kACHV_\w+)"),
        'music': re.compile(r"music\.\w+\s*\(\s*[^)]+\)"),
        'sound': re.compile(r"sound\.(LoadGroup|UnloadGroup|MuteCategory)\s*\(\s*['\"]([^'\"]+)['\"]"),
        'dialog': re.compile(r"dialog\.\w+\s*\([^)]+\)"),
        'hud': re.compile(r"hud\.\w+\s*\([^)]+\)"),
        'trigger_entered': re.compile(r"notify\s*\(\s*['\"]NotifyOnTriggerEntered['\"]\s*,\s*['\"]([^'\"]+)['\"]"),
        'trigger_exited': re.compile(r"notify\s*\(\s*['\"]NotifyOnTriggerExited['\"]\s*,\s*['\"]([^'\"]+)['\"]"),
        'timer': re.compile(r"StartTimer\s*\(\s*\d+\s*,\s*\d+\s*\)"),
        'notification': re.compile(r"game\.(Add|Remove)Notification"),
        'team': re.compile(r"(kTEAM_Player0|kTEAM_Hostile|kTEAM_Neutral)"),
    }

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.content = ""
        self.lines = []
        self.parse_result = {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'class_type': None,
            'mission_code': None,
            'intro_line': None,
            'objective_line': None,
            'dialog_resource': None,
            'complete_checkpoint': None,
            'abort_checkpoint': None,
            'is_abort_checkpoint': None,
            'sub_missions': [],
            'callbacks': [],
            'entities_referenced': [],
            'entities_spawned': [],
            'objectives': [],
            'abilities_learned': [],
            'abilities_unlearned': [],
            'solos_learned': [],
            'orders_set': [],
            'tech_learned': [],
            'achievements': [],
            'music_functions': [],
            'sound_groups': [],
            'hud_calls': [],
            'triggers_entered': [],
            'triggers_exited': [],
            'teams_used': [],
            'warnings': [],
            'errors': [],
        }

    def parse(self) -> dict:
        """Parse the mission file and return structured data."""
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                self.content = f.read()
        except Exception as e:
            self.parse_result['errors'].append(f"Failed to read file: {e}")
            return self.parse_result

        if not self.content:
            self.parse_result['errors'].append("File is empty")
            return self.parse_result

        self.lines = self.content.split('\n')

        # Extract components
        self._extract_class_type()
        self._extract_mission_properties()
        self._extract_sub_missions()
        self._extract_callbacks()
        self._extract_entities()
        self._extract_game_calls()

        return self.parse_result

    def _extract_class_type(self):
        """Extract the CreateObject class type."""
        match = self.PATTERNS['class'].search(self.content)
        if match:
            self.parse_result['class_type'] = match.group(1)

    def _extract_mission_properties(self):
        """Extract mission properties like MissionCode, IntroLineCode, etc."""
        patterns = [
            ('mission_code', 'mission_code'),
            ('intro_line', 'intro_line'),
            ('objective_line', 'objective_line'),
            ('dialog_resource', 'dialog_resource'),
            ('checkpoint', 'complete_checkpoint'),
            ('abort_checkpoint', 'abort_checkpoint'),
            ('is_abort', 'is_abort_checkpoint'),
        ]

        for pattern_name, result_name in patterns:
            match = self.PATTERNS[pattern_name].search(self.content)
            if match:
                value = match.group(1)
                if pattern_name == 'is_abort':
                    value = value.lower() == 'true'
                self.parse_result[result_name] = value

    def _extract_sub_missions(self):
        """Extract sub-missions from the Ob.Missions array."""
        # Find the Missions table
        missions_match = re.search(r"Ob\.Mission[s]?\s*=\s*\{([^}]+)\}", self.content, re.DOTALL)
        if missions_match:
            missions_content = missions_match.group(1)
            # Find all MissionName entries
            for match in self.PATTERNS['sub_mission'].finditer(missions_content):
                mission_name = match.group(1)
                # Check for associated Data
                data_match = self.PATTERNS['sub_mission_data'].search(missions_content)
                data = data_match.group(1) if data_match else None
                self.parse_result['sub_missions'].append({
                    'name': mission_name,
                    'data': data
                })

    def _extract_callbacks(self):
        """Extract mission callbacks (OnMissionStart, OnMissionComplete, etc.)."""
        for match in self.PATTERNS['function'].finditer(self.content):
            callback_name = match.group(1)
            if callback_name.startswith('On') or callback_name.startswith('NotifyOn'):
                self.parse_result['callbacks'].append(callback_name)

    def _extract_entities(self):
        """Extract entity references and spawns."""
        # GetEntityNamed calls
        for match in self.PATTERNS['entity_get'].finditer(self.content):
            entity_name = match.group(1)
            if entity_name not in self.parse_result['entities_referenced']:
                self.parse_result['entities_referenced'].append(entity_name)

        # SpawnAtPosition
        for match in self.PATTERNS['spawn_position'].finditer(self.content):
            proto_name = match.group(1)
            self.parse_result['entities_spawned'].append({
                'type': 'position',
                'prototype': proto_name
            })

        # SpawnAtEntity
        for match in self.PATTERNS['spawn_entity'].finditer(self.content):
            proto_name = match.group(1)
            self.parse_result['entities_spawned'].append({
                'type': 'entity',
                'prototype': proto_name
            })

    def _extract_game_calls(self):
        """Extract various game API calls."""
        # Objectives
        for match in self.PATTERNS['objective_add'].finditer(self.content):
            self.parse_result['objectives'].append(match.group(1))

        # Abilities
        for match in self.PATTERNS['ability'].finditer(self.content):
            action, ability = match.groups()
            if action == 'Learn':
                if ability not in self.parse_result['abilities_learned']:
                    self.parse_result['abilities_learned'].append(ability)
            else:
                if ability not in self.parse_result['abilities_unlearned']:
                    self.parse_result['abilities_unlearned'].append(ability)

        # Solos
        for match in self.PATTERNS['solo'].finditer(self.content):
            solo = match.group(1)
            if solo not in self.parse_result['solos_learned']:
                self.parse_result['solos_learned'].append(solo)

        # Achievements
        for match in self.PATTERNS['achievement'].finditer(self.content):
            achievement = match.group(1)
            if achievement not in self.parse_result['achievements']:
                self.parse_result['achievements'].append(achievement)

        # Music functions
        for match in self.PATTERNS['music'].finditer(self.content):
            self.parse_result['music_functions'].append(match.group(0))

        # Sound groups
        for match in self.PATTERNS['sound'].finditer(self.content):
            func_name, group_name = match.groups()
            if group_name not in self.parse_result['sound_groups']:
                self.parse_result['sound_groups'].append(group_name)

        # HUD calls
        for match in self.PATTERNS['hud'].finditer(self.content):
            self.parse_result['hud_calls'].append(match.group(0))

        # Triggers
        for match in self.PATTERNS['trigger_entered'].finditer(self.content):
            trigger = match.group(1)
            if trigger not in self.parse_result['triggers_entered']:
                self.parse_result['triggers_entered'].append(trigger)

        for match in self.PATTERNS['trigger_exited'].finditer(self.content):
            trigger = match.group(1)
            if trigger not in self.parse_result['triggers_exited']:
                self.parse_result['triggers_exited'].append(trigger)

        # Teams used
        for match in self.PATTERNS['team'].finditer(self.content):
            team = match.group(1)
            if team not in self.parse_result['teams_used']:
                self.parse_result['teams_used'].append(team)


# ============================================================================
# MISSION VALIDATOR
# ============================================================================

class MissionValidator:
    """Validate mission scripts for common errors and issues."""

    REQUIRED_CALLBACKS = ['OnMissionStart']
    RECOMMENDED_CALLBACKS = ['OnMissionComplete']

    def __init__(self, parse_result: dict):
        self.parse_result = parse_result
        self.issues = []

    def validate(self) -> dict:
        """Run all validation checks and return issues."""
        self._check_mission_code()
        self._check_required_callbacks()
        self._check_class_type()
        self._check_objectives()
        self._check_sub_missions()
        self._check_spawn_consistency()
        self._check_lua_syntax()

        return {
            'valid': len(self.issues) == 0,
            'issues': self.issues,
            'warnings': [i for i in self.issues if i['severity'] == 'warning'],
            'errors': [i for i in self.issues if i['severity'] == 'error'],
        }

    def _add_issue(self, severity: str, message: str, location: str = None):
        """Add a validation issue."""
        issue = {
            'severity': severity,
            'message': message,
        }
        if location:
            issue['location'] = location
        self.issues.append(issue)

    def _check_mission_code(self):
        """Check that MissionCode is present and valid."""
        if not self.parse_result['mission_code']:
            self._add_issue('error', 'Missing MissionCode property')
            return

        code = self.parse_result['mission_code']
        # Check format (e.g., P1_010, S1_18, etc.)
        if not re.match(r'^[PSCpcs]?\d[_\d]+$', code, re.IGNORECASE):
            self._add_issue('warning', f'MissionCode format may be invalid: {code}')

    def _check_required_callbacks(self):
        """Check for required callback functions."""
        callbacks = self.parse_result['callbacks']
        for required in self.REQUIRED_CALLBACKS:
            if required not in callbacks:
                self._add_issue('error', f'Missing required callback: {required}')

        for recommended in self.RECOMMENDED_CALLBACKS:
            if recommended not in callbacks:
                self._add_issue('warning', f'Recommended callback missing: {recommended}')

    def _check_class_type(self):
        """Check that class type is valid."""
        class_type = self.parse_result['class_type']
        if not class_type:
            self._add_issue('error', 'Missing CreateObject class declaration')
            return

        valid_prefixes = [
            'Missions.PrimaryMission',
            'Missions.SecondaryMission',
            'MissionBase',
            'Missions.AmbushMission',
            'Missions.RaceMission',
            'Missions.HoldoutMission',
            'Missions.HuntMission',
        ]

        if not any(class_type.startswith(prefix) for prefix in valid_prefixes):
            self._add_issue('warning', f'Unusual class type: {class_type}')

    def _check_objectives(self):
        """Check objectives setup."""
        if not self.parse_result['objectives'] and not self.parse_result['objective_line']:
            self._add_issue('warning', 'No objectives defined (no AddObjective calls or MissionObjectiveLineCode)')

    def _check_sub_missions(self):
        """Check sub-missions array if present."""
        sub_missions = self.parse_result['sub_missions']
        if sub_missions:
            # Check that multi-part missions have OnMissionComplete
            if 'OnMissionComplete' not in self.parse_result['callbacks']:
                self._add_issue('warning', 'Multi-part mission (has sub-missions) but missing OnMissionComplete')

    def _check_spawn_consistency(self):
        """Check for spawn-related consistency issues."""
        spawned = self.parse_result['entities_spawned']
        referenced = self.parse_result['entities_referenced']

        # Check if entities are spawned but not referenced or vice versa
        for entity in referenced:
            if entity.startswith('TV_') or entity.startswith('Locator_'):
                # These are typically trigger volumes and locators
                continue
            # This is informational, not an error

    def _check_lua_syntax(self):
        """Basic Lua syntax check."""
        content = self.parse_result.get('filepath', '')
        if not content:
            return

        # Check for unbalanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            self._add_issue('error', f'Unbalanced braces: {open_braces} open, {close_braces} close')

        # Check for unbalanced parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        if open_parens != close_parens:
            self._add_issue('error', f'Unbalanced parentheses: {open_parens} open, {close_parens} close')

        # Check for unbalanced quotes
        single_quotes = content.count("'")
        if single_quotes % 2 != 0:
            self._add_issue('error', 'Unbalanced single quotes')

        double_quotes = content.count('"')
        if double_quotes % 2 != 0:
            self._add_issue('error', 'Unbalanced double quotes')


# ============================================================================
# TEMPLATE GENERATOR
# ============================================================================

class TemplateGenerator:
    """Generate new mission scripts from templates."""

    TEMPLATES = {
        'campaign': """local Ob = CreateObject('Missions.PrimaryMission')

-- Mission Configuration
Ob.MissionCode = '{mission_code}'
Ob.MissionIntroLineCode = '{intro_line}'
Ob.MissionObjectiveLineCode = '{objective_line}'
Ob.DialogResource = RESOURCE('Missions/Campaign/Dialog/{mission_code}', 'DialogSets')
Ob.CompleteCheckpointLoc = '{mission_code}_MissionEnd'
Ob.IsAbortCheckpoint = false
Ob.AbortCheckpointLoc = '{mission_code}_Locator_AbortPoint'

function Ob:OnMissionStart(loadFromSave, alreadyStarted)
    if not alreadyStarted then
        Trace("Starting {mission_code}")

        -- Teleport player to start location
        local player = game.GetPlayer(0)
        local locator = rtti.GetEntityNamed('{mission_code}_Locator_Start')
        if locator then
            game.TeleportPlayer(player, locator)
        end

        -- Set main objective
        self.objective = game.AddObjective("{objective_text}", self)
    end

    -- Load mission-specific sounds
    sound.LoadGroup("Scripted/{mission_code}", false)

    -- Disable ambient music during mission
    music.EnableAmbient(false)
end

function Ob:OnMissionComplete()
    Trace("{mission_code} completed!")
    game.EndMission(self)
    profile.UnlockAchievement(kACHV_PROG_{mission_code_achievement})
end

function Ob:OnMissionEnd()
    -- Clean up sounds
    sound.UnloadGroup("Scripted/{mission_code}")

    -- Re-enable ambient music
    music.EnableAmbient(true)

    -- Call parent
    Ob.Parent.OnMissionEnd(self)
end

return Ob
""",

        'stage': """local Ob = CreateObject('MissionBase')

-- Mission Configuration
Ob.MissionCode = '{mission_code}'
Ob.StageMission = true

function Ob:OnMissionStart(loadFromSave, alreadyStarted)
    if not alreadyStarted then
        Trace("Starting stage mission {mission_code}")

        -- Initialize stage battle
        local player = game.GetPlayer(0)
        game.SetTeamType(player, kTEAM_Player0)
    end

    -- Load sounds
    sound.LoadGroup("Scripted/{mission_code}", false)
end

function Ob:OnMissionComplete()
    Trace("Stage mission {mission_code} complete!")
    game.EndMission(self)
end

function Ob:OnMissionEnd()
    sound.UnloadGroup("Scripted/{mission_code}")
    Ob.Parent.OnMissionEnd(self)
end

return Ob
""",

        'ambush': """local Ob = CreateObject('Missions.SecondaryMissions.AmbushMission')

-- Mission Configuration
Ob.IsCheckpoint = true
Ob.StartLineCode = '{start_line}'
Ob.LoseLineCode = '{lose_line}'
Ob.WinLineCode = '{win_line}'

-- Trigger volumes
Ob.sWarningTrigger = "{mission_code}_TV_Warning"
Ob.sCancelTrigger = "{mission_code}_TV_Cancel"

-- Allowed enemy prototypes
Ob.ClumpSeeds = MakeClumpSeeds(
    PROTO('L02_HeadbangerSquad'),
    PROTO('L05_FistSquad')
)

function Ob:OnMissionStart(loadFromSave, alreadyStarted)
    if not alreadyStarted then
        Trace("Starting ambush mission {mission_code}")
    end
    Ob.Parent.OnMissionStart(self, loadFromSave, alreadyStarted)
end

function Ob:OnMissionComplete()
    Trace("Ambush {mission_code} completed!")
    game.EndMission(self)
end

return Ob
""",

        'race': """local Ob = CreateObject('MissionBase')

Ob.OpponentProto = PROTO('{opponent_proto}')
Ob.RaceTrack = RESOURCE('{track_resource}', 'RaceTracks')
Ob.RaceLaps = {num_laps}

function Ob:OnMissionStart(loadFromSave, alreadyStarted)
    if not alreadyStarted then
        Trace("Starting race mission {mission_code}")

        -- Spawn opponent
        local opponent = game.SpawnAtPosition(
            Ob.OpponentProto,
            game.GetKnownDomain(kKD_GameMission),
            0, 0, 0,
            kTEAM_Hostile,
            false
        )
    end
    Ob.Parent.OnMissionStart(self, loadFromSave, alreadyStarted)
end

function Ob:nextMilestone(instigator)
    -- Called when player reaches a checkpoint
    Trace("Race checkpoint reached")
end

function Ob:OnMissionComplete()
    Trace("Race {mission_code} won!")
    game.EndMission(self)
    profile.UnlockAchievement(kACHV_PROG_RACE_WIN)
end

return Ob
""",

        'holdout': """local Ob = CreateObject('MissionBase')

Ob.WaveTimer = {wave_timer}
Ob.MaxWaves = {max_waves}

function Ob:OnMissionStart(loadFromSave, alreadyStarted)
    if not alreadyStarted then
        Trace("Starting holdout mission {mission_code}")

        -- Start enemy spawn timer
        self:StartEnemySpawnTimer()
    end
    Ob.Parent.OnMissionStart(self, loadFromSave, alreadyStarted)
end

function Ob:StartNextWave()
    -- Spawn next enemy wave
    Trace("Spawning wave " .. self.CurrentWave)
end

function Ob:OnMissionComplete()
    Trace("Holdout {mission_code} survived!")
    game.EndMission(self)
    local elapsed = self:GetElapsedTime()
    profile.UnlockAchievement(kACHV_PROG_HOLDOUT_WIN)
end

return Ob
""",

        'hunt': """local Ob = CreateObject('MissionBase')

Ob.HuntTarget = PROTO('{hunt_target}')
Ob.HuntArea = "{hunt_area}"

function Ob:OnMissionStart(loadFromSave, alreadyStarted)
    if not alreadyStarted then
        Trace("Starting hunt mission {mission_code}")
        self:setupContactDialog()
        self:enableMissionAbilities()
    end
    Ob.Parent.OnMissionStart(self, loadFromSave, alreadyStarted)
end

function Ob:WinIt()
    -- Win condition: target killed
    Trace("Hunt target eliminated!")
    game.EndMission(self)
end

function Ob:setupContactDialog()
    -- Set up initial dialog
end

return Ob
""",
    }

    def __init__(self):
        pass

    def generate(self, template_name: str, mission_code: str, **kwargs) -> str:
        """Generate a mission script from a template."""
        if template_name not in self.TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(self.TEMPLATES.keys())}")

        template = self.TEMPLATES[template_name]

        # Set defaults
        defaults = {
            'mission_code': mission_code.upper(),
            'mission_code_lower': mission_code.lower(),
            'intro_line': f'{mission_code.upper()}INTRO',
            'objective_line': f'{mission_code.upper()}OBJ',
            'objective_text': 'Complete the mission objectives',
            'start_line': 'SMMB012TEXT',
            'lose_line': 'SMMB013TEXT',
            'win_line': 'SMMB014TEXT',
            'opponent_proto': 'L02_HeadbangerSquad',
            'track_resource': 'Tracks/DefaultTrack',
            'num_laps': '3',
            'wave_timer': '30',
            'max_waves': '5',
            'hunt_target': 'L05_FistSquad',
            'hunt_area': 'HuntArea',
        }

        # Override defaults with provided kwargs
        defaults.update(kwargs)

        # Format mission code for achievement
        mission_code_clean = mission_code.upper().replace('_', '')
        defaults['mission_code_achievement'] = mission_code_clean

        try:
            return template.format(**defaults)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def list_templates(self) -> list:
        """List available template names."""
        return list(self.TEMPLATES.keys())

    def get_template_info(self, template_name: str) -> str:
        """Get description of a template."""
        info = {
            'campaign': 'Primary campaign mission with full mission callbacks',
            'stage': 'Stage battle mission for RTS-style combat',
            'ambush': 'Secondary ambush mission with warning/cancel triggers',
            'race': 'Race mission with checkpoints and timing',
            'holdout': 'Holdout mission with wave-based enemy spawns',
            'hunt': 'Hunt mission to track and eliminate a target',
        }
        return info.get(template_name, 'Unknown template')


# ============================================================================
# CLI INTERFACE
# ============================================================================

def list_missions(missions_path: str) -> None:
    """List all mission scripts in a directory."""
    # Find all .lua files in missions directories
    missions_path = Path(missions_path)

    missions = []

    if missions_path.is_file():
        # Single file
        if missions_path.suffix == '.lua':
            missions.append(str(missions_path))
    elif missions_path.is_dir():
        # Directory - find mission directories and .lua files
        for lua_file in sorted(missions_path.rglob('*.lua')):
            # Skip empty files
            if lua_file.stat().st_size > 0:
                missions.append(str(lua_file))

    if not missions:
        print(f"No mission scripts found in {missions_path}")
        return

    print(f"Found {len(missions)} mission script(s):\n")

    # Categorize missions
    by_category = {'campaign': [], 'stage': [], 'other': []}

    for mission_path in missions:
        parser = MissionParser(mission_path)
        try:
            result = parser.parse()
            code = result.get('mission_code') or os.path.basename(mission_path)
            class_type = result.get('class_type', 'Unknown')

            if 'Primary' in class_type or 'campaign' in mission_path.lower():
                category = 'campaign'
            elif 'Secondary' in class_type or class_type.startswith('Missions.S'):
                category = 'stage'
            else:
                category = 'other'

            by_category[category].append((code, mission_path, class_type))
        except Exception as e:
            by_category['other'].append((os.path.basename(mission_path), mission_path, f'Parse error: {e}'))

    for category, items in by_category.items():
        if items:
            print(f"\n{category.upper()} ({len(items)}):")
            for code, path, class_type in sorted(items):
                print(f"  {code:15} | {class_type:40} | {path}")


def parse_mission(mission_path: str, verbose: bool = False) -> None:
    """Parse and display mission script structure."""
    if not os.path.exists(mission_path):
        print(f"Error: File not found: {mission_path}")
        return

    parser = MissionParser(mission_path)
    result = parser.parse()

    print(f"\n{'='*60}")
    print(f"MISSION PARSE RESULT: {result['filename']}")
    print(f"{'='*60}\n")

    # Basic info
    print("BASIC INFO:")
    print(f"  Filename:    {result['filename']}")
    print(f"  Class Type:  {result['class_type'] or 'Unknown'}")
    print(f"  Mission Code: {result['mission_code'] or 'Not set'}")
    print()

    # Mission Properties
    print("MISSION PROPERTIES:")
    print(f"  Intro Line Code:      {result['intro_line'] or 'Not set'}")
    print(f"  Objective Line Code:  {result['objective_line'] or 'Not set'}")
    print(f"  Dialog Resource:      {result['dialog_resource'] or 'Not set'}")
    print(f"  Complete Checkpoint:  {result['complete_checkpoint'] or 'Not set'}")
    print(f"  Abort Checkpoint:     {result['abort_checkpoint'] or 'Not set'}")
    print(f"  Is Abort Checkpoint:  {result['is_abort_checkpoint']}")
    print()

    # Sub-missions
    if result['sub_missions']:
        print(f"SUB-MISSIONS ({len(result['sub_missions'])}):")
        for i, sub in enumerate(result['sub_missions'], 1):
            data_str = f" (Data: {sub['data']})" if sub['data'] else ""
            print(f"  {i}. {sub['name']}{data_str}")
        print()

    # Callbacks
    print(f"CALLBACKS ({len(result['callbacks'])}):")
    if result['callbacks']:
        for cb in sorted(result['callbacks']):
            print(f"  - {cb}")
    else:
        print("  None found")
    print()

    if verbose:
        # Entities
        print(f"ENTITIES REFERENCED ({len(result['entities_referenced'])}):")
        if result['entities_referenced']:
            for entity in sorted(result['entities_referenced'])[:20]:
                print(f"  - {entity}")
            if len(result['entities_referenced']) > 20:
                print(f"  ... and {len(result['entities_referenced']) - 20} more")
        else:
            print("  None found")
        print()

        # Spawned entities
        print(f"ENTITIES SPAWNED ({len(result['entities_spawned'])}):")
        if result['entities_spawned']:
            for spawn in result['entities_spawned'][:10]:
                print(f"  - {spawn['prototype']} ({spawn['type']})")
            if len(result['entities_spawned']) > 10:
                print(f"  ... and {len(result['entities_spawned']) - 10} more")
        else:
            print("  None found")
        print()

        # Objectives
        print(f"OBJECTIVES ({len(result['objectives'])}):")
        if result['objectives']:
            for obj in result['objectives']:
                print(f"  - {obj}")
        else:
            print("  None found")
        print()

        # Abilities
        if result['abilities_learned']:
            print(f"ABILITIES LEARNED ({len(result['abilities_learned'])}):")
            for ability in result['abilities_learned']:
                print(f"  + {ability}")
            print()

        if result['abilities_unlearned']:
            print(f"ABILITIES UNLEARNED ({len(result['abilities_unlearned'])}):")
            for ability in result['abilities_unlearned']:
                print(f"  - {ability}")
            print()

        # Solos
        if result['solos_learned']:
            print(f"SOLOS LEARNED ({len(result['solos_learned'])}):")
            for solo in result['solos_learned']:
                print(f"  + {solo}")
            print()

        # Achievements
        if result['achievements']:
            print(f"ACHIEVEMENTS ({len(result['achievements'])}):")
            for ach in result['achievements']:
                print(f"  * {ach}")
            print()

        # Sound groups
        if result['sound_groups']:
            print(f"SOUND GROUPS ({len(result['sound_groups'])}):")
            for group in result['sound_groups']:
                print(f"  - {group}")
            print()

        # Triggers
        if result['triggers_entered']:
            print(f"TRIGGERS ENTERED ({len(result['triggers_entered'])}):")
            for trigger in result['triggers_entered']:
                print(f"  > {trigger}")
            print()

        if result['triggers_exited']:
            print(f"TRIGGERS EXITED ({len(result['triggers_exited'])}):")
            for trigger in result['triggers_exited']:
                print(f"  < {trigger}")
            print()

        # Teams
        if result['teams_used']:
            print(f"TEAMS USED ({len(result['teams_used'])}):")
            for team in result['teams_used']:
                print(f"  - {team}")
            print()

    # Validation
    print("VALIDATION:")
    validator = MissionValidator(result)
    validation = validator.validate()

    if validation['valid']:
        print("  No issues found!")
    else:
        if validation['errors']:
            print("  ERRORS:")
            for issue in validation['errors']:
                loc_str = f" ({issue.get('location', 'unknown location')})" if 'location' in issue else ""
                print(f"    [ERROR] {issue['message']}{loc_str}")
        if validation['warnings']:
            print("  WARNINGS:")
            for issue in validation['warnings']:
                print(f"    [WARNING] {issue['message']}")

    print()


def create_mission(output_path: str, template: str, mission_code: str = None, **kwargs) -> None:
    """Create a new mission script from a template."""
    generator = TemplateGenerator()

    # Determine mission code from output filename if not provided
    if not mission_code:
        if output_path:
            # Extract from filename
            basename = os.path.basename(output_path)
            mission_code = os.path.splitext(basename)[0].upper()

    if not mission_code:
        mission_code = "NEW_MISSION"

    try:
        content = generator.generate(template, mission_code, **kwargs)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Created mission script: {output_path}")
        print(f"  Template: {template}")
        print(f"  Mission Code: {mission_code}")
        print()
        print("NOTE: Review and update the generated script before use!")
    except ValueError as e:
        print(f"Error: {e}")


def validate_mission(mission_path: str) -> None:
    """Validate a mission script and report issues."""
    if not os.path.exists(mission_path):
        print(f"Error: File not found: {mission_path}")
        return

    parser = MissionParser(mission_path)
    result = parser.parse()
    validator = MissionValidator(result)
    validation = validator.validate()

    print(f"\nValidation: {result['filename']}")
    print(f"Result: {'PASSED' if validation['valid'] else 'FAILED'}")

    if validation['issues']:
        print()
        for issue in validation['issues']:
            prefix = "ERROR" if issue['severity'] == 'error' else "WARNING"
            print(f"  [{prefix}] {issue['message']}")

    if not validation['issues']:
        print("  No issues found!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Brutal Legend Mission Script Editor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list data/script/missions/
  %(prog)s parse data/script/missions/p1_010/p1_010.lua
  %(prog)s create mymission.lua --template campaign --mission-code MYM001
  %(prog)s validate data/script/missions/p1_010/p1_010.lua
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List mission scripts in a directory')
    list_parser.add_argument('path', help='Path to missions directory or file')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse and display mission structure')
    parse_parser.add_argument('path', help='Path to mission script')
    parse_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new mission from template')
    create_parser.add_argument('output', help='Output file path')
    create_parser.add_argument('-t', '--template', default='campaign',
                               choices=['campaign', 'stage', 'ambush', 'race', 'holdout', 'hunt'],
                               help='Mission template to use')
    create_parser.add_argument('--mission-code', help='Mission code (e.g., P1_010)')
    create_parser.add_argument('--intro-line', help='Intro text line code')
    create_parser.add_argument('--objective-line', help='Objective text line code')
    create_parser.add_argument('--objective-text', help='Objective text')
    create_parser.add_argument('--start-line', help='Ambush start line code')
    create_parser.add_argument('--lose-line', help='Ambush lose line code')
    create_parser.add_argument('--win-line', help='Ambush win line code')
    create_parser.add_argument('--opponent-proto', help='Race/Hunt opponent prototype')
    create_parser.add_argument('--hunt-target', help='Hunt target prototype')
    create_parser.add_argument('--hunt-area', help='Hunt area trigger name')
    create_parser.add_argument('--track-resource', help='Race track resource')
    create_parser.add_argument('--num-laps', type=int, default=3, help='Number of race laps')
    create_parser.add_argument('--wave-timer', type=int, default=30, help='Holdout wave timer')
    create_parser.add_argument('--max-waves', type=int, default=5, help='Holdout max waves')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a mission script')
    validate_parser.add_argument('path', help='Path to mission script')

    # Templates command (list available templates)
    templates_parser = subparsers.add_parser('templates', help='List available mission templates')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'list':
        list_missions(args.path)
    elif args.command == 'parse':
        parse_mission(args.path, args.verbose)
    elif args.command == 'create':
        create_kwargs = {}
        if args.intro_line:
            create_kwargs['intro_line'] = args.intro_line
        if args.objective_line:
            create_kwargs['objective_line'] = args.objective_line
        if args.objective_text:
            create_kwargs['objective_text'] = args.objective_text
        if args.start_line:
            create_kwargs['start_line'] = args.start_line
        if args.lose_line:
            create_kwargs['lose_line'] = args.lose_line
        if args.win_line:
            create_kwargs['win_line'] = args.win_line
        if args.opponent_proto:
            create_kwargs['opponent_proto'] = args.opponent_proto
        if args.hunt_target:
            create_kwargs['hunt_target'] = args.hunt_target
        if args.hunt_area:
            create_kwargs['hunt_area'] = args.hunt_area
        if args.track_resource:
            create_kwargs['track_resource'] = args.track_resource
        if args.num_laps:
            create_kwargs['num_laps'] = str(args.num_laps)
        if args.wave_timer:
            create_kwargs['wave_timer'] = str(args.wave_timer)
        if args.max_waves:
            create_kwargs['max_waves'] = str(args.max_waves)

        create_mission(args.output, args.template, args.mission_code, **create_kwargs)
    elif args.command == 'validate':
        validate_mission(args.path)
    elif args.command == 'templates':
        generator = TemplateGenerator()
        print("\nAvailable Mission Templates:\n")
        for tmpl in generator.list_templates():
            print(f"  {tmpl:12} - {generator.get_template_info(tmpl)}")
        print()


if __name__ == '__main__':
    main()
