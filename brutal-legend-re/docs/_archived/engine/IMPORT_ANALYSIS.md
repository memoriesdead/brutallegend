# BrutalLegend.exe - Import Analysis

**File:** BrutalLegend.exe (in Steam game directory)  
**Size:** 13,180,928 bytes  
**Architecture:** x86 (32-bit)  
**Build Date:** Mon May 6 13:42:41 2013  
**Internal Name:** Buddha.exe

---

## Summary

| Attribute | Value |
|-----------|-------|
| Machine | x86 (32-bit) |
| PE Signature | PE |
| Subsystem | (not extracted) |
| Entry Point | (not extracted) |
| Timestamp | 2013-05-06 13:42:41 |

---

## Section Layout

| Section | Size |
|---------|------|
| .text | 10,612,224 (0xA33000) |
| .rdata | 1,245,184 (0x128000) |
| .data | 875,008 (0xD6000) |
| .reloc | 786,432 (0xC0000) |
| .rsrc | 86,016 (0x15000) |

---

## Imported DLLs

### 1. binkw32.dll (RAD Video Tools - Bink Video)
| Function | Description |
|----------|-------------|
| _BinkWait@4 | Wait for Bink video |
| _BinkNextFrame@4 | Advance to next frame |
| _BinkGetFrameBuffersInfo@8 | Get frame buffer info |
| _BinkShouldSkip@4 | Check if frame should be skipped |
| _BinkPause@8 | Pause playback |
| _BinkSetVolume@12 | Set volume |
| _BinkOpenDirectSound@4 | Open DirectSound for Bink |
| _BinkSetMemory@8 | Set memory for Bink |
| _BinkDoFrame@4 | Render frame |
| _BinkSetIO@4 | Set I/O mode |
| _BinkSetSoundTrack@8 | Set sound track |
| _BinkOpen@8 | Open Bink file |
| _BinkClose@4 | Close Bink file |
| _BinkSetSoundSystem@8 | Set sound system |
| _BinkRegisterFrameBuffers@8 | Register frame buffers |
| _BinkSetIOSize@4 | Set I/O size |

### 2. IMM32.dll (Input Method Manager)
| Function | Description |
|----------|-------------|
| ImmReleaseContext | Release IME context |
| ImmGetContext | Get IME context |
| ImmSetCompositionStringW | Set composition string |
| ImmNotifyIME | Notify IME of change |
| ImmGetCompositionStringW | Get composition string |
| ImmGetCandidateListW | Get candidate list |
| ImmAssociateContext | Associate input context |
| ImmGetIMEFileNameA | Get IME file name |

### 3. VERSION.dll (Version Management)
| Function | Description |
|----------|-------------|
| GetFileVersionInfoSizeA | Get version info size |
| GetFileVersionInfoA | Get version info |
| VerQueryValueA | Query version value |

### 4. steam_api.dll (Steamworks API)
| Function | Description |
|----------|-------------|
| SteamAPI_RegisterCallResult | Register Steam callback |
| SteamAPI_UnregisterCallResult | Unregister callback |
| SteamMatchmaking | Get matchmaking interface |
| SteamNetworking | Get networking interface |
| SteamAPI_Init | Initialize Steam API |
| SteamAPI_RestartAppIfNecessary | Check for Steam relaunch |
| SteamAPI_Shutdown | Shutdown Steam API |
| SteamAPI_UnregisterCallback | Unregister callback |
| SteamAPI_RegisterCallback | Register callback |
| SteamUtils | Get utils interface |
| SteamFriends | Get friends interface |
| SteamApps | Get apps interface |
| SteamUserStats | Get user stats interface |
| SteamUser | Get user interface |
| SteamAPI_RunCallbacks | Run Steam callbacks |

### 5. KERNEL32.dll (Windows Kernel)
#### Threading & Synchronization
| Function | Description |
|----------|-------------|
| CreateThread | Create new thread |
| CreateSemaphoreA/W | Create semaphore |
| CreateMutexA | Create mutex |
| CreateEventA | Create event |
| CreateWaitableTimerA | Create waitable timer |
| SetWaitableTimer | Set timer |
| ResumeThread | Resume suspended thread |
| SuspendThread | Suspend thread |
| SetThreadPriority | Set thread priority |
| SetThreadAffinityMask | Set CPU affinity |
| SwitchToThread | Yield to other threads |
| ExitThread | Exit current thread |
| TerminateProcess | Terminate process |
| GetCurrentThread | Get current thread handle |
| GetCurrentThreadId | Get current thread ID |
| GetExitCodeThread | Get thread exit code |
| TlsAlloc/TlsGetValue/TlsSetValue/TlsFree | Thread local storage |
| InitializeCriticalSectionAndSpinCount | Init crit section |
| EnterCriticalSection | Enter crit section |
| LeaveCriticalSection | Leave crit section |
| DeleteCriticalSection | Delete crit section |
| TryEnterCriticalSection | Try enter crit section |
| InterlockedIncrement/Decrement | Atomic operations |
| InterlockedExchange | Atomic exchange |
| InterlockedExchangeAdd | Atomic add |
| InterlockedCompareExchange | Atomic compare-exchange |
| WaitForSingleObject | Wait on object |
| WaitForMultipleObjectsEx | Wait on multiple objects |

#### Memory Functions
| Function | Description |
|----------|-------------|
| VirtualAlloc | Allocate virtual memory |
| VirtualFree | Free virtual memory |
| VirtualQuery | Query virtual memory info |
| GlobalAlloc | Global memory alloc |
| GlobalLock/GlobalUnlock | Lock/unlock global mem |
| HeapSetInformation | Set heap info |

#### File I/O
| Function | Description |
|----------|-------------|
| CreateFileA/W | Create/open file |
| ReadFile | Read from file |
| ReadFileEx | Async read |
| WriteFile | Write to file |
| SetFilePointer/SetFilePointerEx | Set file position |
| GetFileSize/GetFileSizeEx | Get file size |
| SetEndOfFile | Set EOF |
| FlushFileBuffers | Flush file buffers |
| GetFileTime | Get file timestamps |
| GetFileAttributesExA | Get file attributes |
| DeleteFileA | Delete file |
| RemoveDirectoryA | Remove directory |
| CreateDirectoryA | Create directory |
| GetDiskFreeSpaceA | Get disk space |
| GetTempPathA | Get temp path |
| CopyFileA | Copy file (not directly imported) |

#### Memory-Mapped Files
> **Note:** MapViewOfFile not explicitly imported - may be used via LoadLibrary

#### Module & Process
| Function | Description |
|----------|-------------|
| GetModuleHandleA/W | Get module handle |
| GetModuleFileNameA | Get module path |
| GetProcAddress | Get function address |
| LoadLibraryA/W | Load DLL |
| FreeLibrary | Free loaded DLL |
| GetCurrentProcess | Get current process |
| GetCurrentProcessId | Get current PID |
| ExitProcess | Exit process |
| DuplicateHandle | Duplicate handle |
| GetStartupInfoW | Get startup info |

#### System Info
| Function | Description |
|----------|-------------|
| GetSystemInfo | Get system info |
| GetVersionExA | Get OS version |
| IsProcessorFeaturePresent | Check CPU features |
| GetTickCount | Get tick count |
| GetTimeZoneInformation | Get timezone |
| QueryPerformanceCounter/Frequency | High-res timer |

#### Debug & Error
| Function | Description |
|----------|-------------|
| OutputDebugStringA/W | Output debug string |
| SetErrorMode | Set error mode |
| GetLastError | Get last error |
| SetLastError | Set last error |
| RaiseException | Raise exception |
| UnhandledExceptionFilter | Handle unhandled |
| SetUnhandledExceptionFilter | Set exception filter |

#### String & Locale
| Function | Description |
|----------|-------------|
| WideCharToMultiByte | Convert WCHAR to MB |
| MultiByteToWideChar | Convert MB to WCHAR |
| CompareStringA | Compare strings |
| FormatMessageA/W | Format message |
| SetEnvironmentVariableA | Set env variable |
| GetEnvironmentVariableA | Get env variable |

### 6. USER32.dll (Windows User Interface)
#### Window Management
| Function | Description |
|----------|-------------|
| CreateWindowExA/W | Create window |
| DestroyWindow | Destroy window |
| ShowWindow | Show/hide window |
| SetWindowPos | Set window position |
| SetWindowTextW | Set window title |
| GetWindowTextLengthW | Get title length |
| GetWindowTextW | Get window title |
| GetWindowRect | Get window rect |
| GetClientRect | Get client rect |
| MoveWindow | Move window |
| SetWindowLongA/W | Set window long |
| GetWindowLongA/W | Get window long |
| GetParent | Get parent window |
| SetParent | Set parent window |
| GetDesktopWindow | Get desktop window |
| GetForegroundWindow | Get foreground window |
| SetForegroundWindow | Set foreground window |
| GetFocus | Get focus window |
| SetCapture | Set mouse capture |
| ReleaseCapture | Release mouse capture |
| ClientToScreen | Convert coords |
| ScreenToClient | Convert coords |
| MapWindowPoints | Map window points |
| IsZoomed | Check if maximized |
| IsClipboardFormatAvailable | Check clipboard |
| OpenClipboard | Open clipboard |
| EmptyClipboard | Empty clipboard |
| SetClipboardData | Set clipboard data |
| GetClipboardData | Get clipboard data |
| CloseClipboard | Close clipboard |
| GetClipboardSequenceNumber | Clipboard seq # |

#### Message Handling
| Function | Description |
|----------|-------------|
| PeekMessageA/W | Peek message |
| GetMessageW | Get message |
| TranslateMessage | Translate message |
| DispatchMessageA/W | Dispatch message |
| PostQuitMessage | Post quit message |
| SendMessageA/W | Send message |
| SendMessageCallback | Send with callback |
| DefWindowProcA/W | Default window proc |
| CallWindowProcW | Call window proc |
| RegisterClassA/W/ExW | Register window class |
| UnregisterClassA/W | Unregister class |

#### Display & Monitor
| Function | Description |
|----------|-------------|
| EnumDisplaySettingsA/W | Enum display settings |
| ChangeDisplaySettingsExW | Change display settings |
| EnumDisplayDevicesW | Enum display devices |

#### Cursor & Input
| Function | Description |
|----------|-------------|
| SetCursorPos | Set cursor position |
| SetCursor | Set cursor |
| GetCursor | Get cursor |
| LoadCursorA/W | Load cursor |
| ShowCursor | Show/hide cursor |
| ClipCursor | Clip cursor |
| GetKeyState | Get key state |
| MapVirtualKeyA/W/ExA | Map virtual key |
| GetKeyboardLayout | Get keyboard layout |

#### Dialogs & Controls
| Function | Description |
|----------|-------------|
| DialogBoxIndirectParamW | Show dialog |
| EndDialog | End dialog |
| SetRect | Set rectangle |
| CreateIconIndirect | Create icon |
| LoadImageA/W | Load image |
| CreateIconFromResource | Create icon |
| DestroyIcon | Destroy icon |
| RegisterDeviceNotificationW | Register device |
| UnregisterDeviceNotification | Unregister device |
| RegisterRawInputDevices | Register raw input |
| GetRawInputData | Get raw input |

#### Window Regions
| Function | Description |
|----------|-------------|
| SetWindowRgn | Set window region |
| CreateRectRgn | Create rect region |
| CombineRgn | Combine regions |

#### Other
| Function | Description |
|----------|-------------|
| AdjustWindowRect/Ex | Adjust window rect |
| ValidateRect | Validate rect |
| GetUpdateRect | Get update rect |
| SetPropW/GetPropW | Set/get property |
| GetMenu | Get menu |

### 7. GDI32.dll (Graphics Device Interface)
| Function | Description |
|----------|-------------|
| BitBlt | Bit block transfer |
| CreateCompatibleDC | Create compatible DC |
| CreateCompatibleBitmap | Create compatible bitmap |
| CreateDIBSection | Create DIB section |
| CreateBitmap | Create bitmap |
| CreateDCW | Create DC |
| DeleteDC | Delete DC |
| DeleteObject | Delete GDI object |
| SelectObject | Select object |
| GetDIBits | Get DIB bits |
| GetDeviceGammaRamp | Get gamma ramp |
| SetDeviceGammaRamp | Set gamma ramp |
| SwapBuffers | Swap OpenGL buffers |
| SetPixelFormat | Set pixel format |
| DescribePixelFormat | Describe pixel format |
| ChoosePixelFormat | Choose pixel format |
| GetStockObject | Get stock object |
| AddFontResourceExA | Add font resource |

### 8. ADVAPI32.dll (Advanced API)
| Function | Description |
|----------|-------------|
| RegOpenKeyA | Open registry key |
| RegOpenKeyExA | Open registry key (extended) |
| RegQueryValueExA | Query registry value |
| RegEnumKeyA | Enumerate registry keys |
| RegCloseKey | Close registry key |
| GetUserNameW | Get user name |

### 9. SHELL32.dll (Shell)
| Function | Description |
|----------|-------------|
| DragFinish | Finish drag operation |
| DragQueryFileW | Query drag file |
| DragAcceptFiles | Accept drag files |
| ExtractIconA | Extract icon |

### 10. ole32.dll (COM)
| Function | Description |
|----------|-------------|
| CoInitialize | Initialize COM |
| CoUninitialize | Uninitialize COM |
| CoCreateInstance | Create COM object |
| CoSetProxyBlanket | Set proxy blanket |
| CLSIDFromString | Convert string to CLSID |
| CoTaskMemFree | Free COM task memory |
| PropVariantClear | Clear propvariant |

### 11. OLEAUT32.dll (COM Automation)
- Ordinal 2, 6 (unknown functions)

### 12. MSVCR100.dll (Microsoft Visual C++ 2010 Runtime)
#### String Functions
| Function | Description |
|----------|-------------|
| strcmp | Compare strings |
| strlen | String length |
| strcpy/strcpy_s | Copy string |
| strcat/strcat_s | Concatenate string |
| strncpy/strncpy_s | Copy n chars |
| strncat | Concatenate n chars |
| strchr | Find character |
| strstr | Find substring |
| strrchr | Find char (reverse) |
| strspn | String span |
| strcspn | Complementary span |
| strtok | Tokenize string |
| strcoll | String collate |
| strerror | Get error string |
| sprintf/sprintf_s | Format string |
| snprintf/_snprintf | Safe format |
| vsprintf | Vararg format |
| _strlwr | Convert to lower |
| _stricmp | Case-insensitive cmp |
| strncmp | Compare n chars |

#### Memory Functions
| Function | Description |
|----------|-------------|
| malloc | Allocate memory |
| free | Free memory |
| realloc | Reallocate memory |
| calloc | Allocate zeroed |
| memcpy/memmove | Copy memory |
| memset | Set memory |
| memcmp | Compare memory |
| memchr | Find byte |

#### Character Classification
| Function | Description |
|----------|-------------|
| isalnum | Is alphanumeric |
| isalpha | Is alphabetic |
| isdigit | Is digit |
| islower | Is lowercase |
| isupper | Is uppercase |
| isspace | Is whitespace |
| ispunct | Is punctuation |
| iscntrl | Is control char |
| isxdigit | Is hex digit |
| iswalnum | Wide alnum |
| iswspace | Wide space |
| tolower | To lowercase |
| toupper | To uppercase |

#### Math Functions
| Function | Description |
|----------|-------------|
| sin/cos/tan | Trigonometry |
| asin/acos/atan/atan2 | Inverse trig |
| sinh/cosh/tanh | Hyperbolic |
| exp/log/log10 | Exponential/log |
| pow | Power |
| sqrt | Square root |
| fabs | Absolute value |
| ceil/floor | Ceiling/floor |
| modf | Modulo (float) |
| ldexp | Load exponent |
| frexp | Get exponent |

#### File I/O (C Runtime)
| Function | Description |
|----------|-------------|
| fopen/fopen_s | Open file |
| fclose | Close file |
| fread | Read from file |
| fwrite | Write to file |
| fseek | Seek position |
| ftell | Tell position |
| fflush | Flush file |
| feof | End of file |
| ferror | File error |
| fgets/fputs | Get/put string |
| getc/ungetc | Get character |
| fprintf/fscanf | Format I/O |
| printf/scanf | Print/scan |
| sprintf/sscanf | String format |
| clearerr | Clear errors |
| rewind | Rewind file |

#### Date/Time
| Function | Description |
|----------|-------------|
| time64/_time64 | Get time |
| _ftime64 | File time |
| _gmtime64 | GM time |
| _localtime64 | Local time |
| _mktime64 | Make time |
| _difftime64 | Time difference |
| clock | CPU clock |
| strftime | Format time |
| setlocale | Set locale |
| localeconv | Get locale |

#### Threading (CRT)
| Function | Description |
|----------|-------------|
| _beginthreadex | Create thread |
| _endthreadex | End thread |
| _configthreadlocale | Configure thread locale |

#### Exception Handling
| Function | Description |
|----------|-------------|
| _CxxThrowException | Throw exception |
| _except_handler3 | Exception handler |
| _except_handler4_common | Exception handler |
| _invoke_watson | Invoke Watson |
| longjmp | Long jump |
| _setjmp3 | Set jump |

#### Other
| Function | Description |
|----------|-------------|
| _onexit | At-exit callback |
| _initterm/_initterm_e | Init term |
| _XcptFilter | Exception filter |
| _cexit/_exit | Exit functions |
| _amsg_exit | Assert message exit |
| _purecall | Pure call handler |
| _commode | Comm mode |
| _fmode | File mode |
| _controlfp_s | Control FPU |
| _set_SSE2_enable | Enable SSE2 |
| _errno | Get errno |
| qsort | Quick sort |
| remove | Remove file |
| rename | Rename file |
| _mkdir | Make directory |
| _fullpath | Full path |
| _findfirst64i32 | Find first |
| _findnext64i32 | Find next |
| getenv | Get env variable |
| _getcwd | Get working dir |
| _msize | Get block size |
| _aligned_malloc | Aligned alloc |
| _aligned_free | Aligned free |

### 13. WSOCK32.dll (Windows Sockets)
All ordinal exports (network functions via ordinals)

### 14. d3d9.dll (Direct3D 9)
| Function | Description |
|----------|-------------|
| Direct3DCreate9 | Create D3D9 interface |

### 15. d3dx9_43.dll (Direct3D Extensions 9)
| Function | Description |
|----------|-------------|
| D3DXCreateSprite | Create sprite |
| D3DXCreateFontA | Create font |
| D3DXCreateTextureFromFileExA | Load texture |
| D3DXCreateTextureFromFileInMemoryEx | Load texture from memory |
| D3DXCreateCubeTextureFromFileInMemoryEx | Load cube texture |
| D3DXCreateVolumeTextureFromFileInMemoryEx | Load volume texture |
| D3DXSaveTextureToFileInMemory | Save texture |
| D3DXAssembleShader | Assemble shader |
| D3DXLoadSurfaceFromMemory | Load surface |

### 16. DINPUT8.dll (DirectInput 8)
| Function | Description |
|----------|-------------|
| DirectInput8Create | Create DirectInput8 |

### 17. MSACM32.dll (Audio Compression Manager)
| Function | Description |
|----------|-------------|
| acmStreamOpen | Open audio codec stream |
| acmStreamSize | Get stream size |
| acmStreamPrepareHeader | Prepare stream header |
| acmStreamUnprepareHeader | Unprepare header |
| acmStreamConvert | Convert audio data |
| acmFormatSuggest | Suggest audio format |

### 18. WINMM.dll (Windows MultiMedia)
#### Wave Input
| Function | Description |
|----------|-------------|
| waveInOpen | Open wave input |
| waveInClose | Close wave input |
| waveInPrepareHeader | Prepare header |
| waveInUnprepareHeader | Unprepare header |
| waveInAddBuffer | Add buffer |
| waveInStart | Start recording |
| waveInReset | Reset wave input |
| waveInGetDevCapsA/W | Get device capabilities |
| waveInGetNumDevs | Get number of devices |

#### Wave Output
| Function | Description |
|----------|-------------|
| waveOutOpen | Open wave output |
| waveOutClose | Close wave output |
| waveOutPrepareHeader | Prepare header |
| waveOutUnprepareHeader | Unprepare header |
| waveOutWrite | Write audio |
| waveOutReset | Reset output |
| waveOutGetPosition | Get position |
| waveOutGetDevCapsA/W | Get device caps |
| waveOutGetErrorTextW | Get error text |
| waveOutGetNumDevs | Get number of devices |

#### Time
| Function | Description |
|----------|-------------|
| timeGetTime | Get time |
| timeBeginPeriod | Begin timer period |

### 19. MSVCP100.dll (Microsoft Visual C++ 2010 STL)
| Function | Description |
|----------|-------------|
| ?_Xlength_error@std@@YAXPBD@Z | STL length error |
| ?_Xout_of_range@std@@YAXPBD@Z | STL out of range |
| ?_Orphan_all@_Container_base0@std@@QAEXXZ | Container orphan |

---

## Internal Engine Exports (Buddha.exe)

The executable exports 611 functions under the internal name **Buddha.exe**:

### File I/O Classes
- **GBufferedFile** - Buffered file I/O
- **GSysFile** - System file I/O  
- **GZLibFile** - zlib-compressed file I/O

### Threading & Synchronization
- **GThread** - Thread management
- **GMutex** - Mutex implementation
- **GSemaphore** - Semaphore implementation
- **GEvent** - Event implementation
- **GWaitCondition** - Condition variable
- **GWaitable** - Base waitable interface

### Memory & Reference Counting
- **GRefCountBaseImpl** - Reference counting implementation
- **GAcquireInterface** - Interface acquisition

### Graphics
- **GImage** - Image handling
- **GImageBase** - Image base class
- **GColor** - Color manipulation
- **GMatrix2D** - 2D transformation matrix

### Other
- **GFxLoader** - Scaleform GFx loader
- **GSysFile** - System file

### SDL Functions
611 SDL functions exported including:
- SDL_Init, SDL_Quit - Initialization
- SDL_CreateWindow, SDL_DestroyWindow - Window management
- SDL_CreateRenderer, SDL_RenderPresent - Rendering
- SDL_PollEvent, SDL_WaitEvent - Event handling
- SDL_GameController* - Game controller support
- SDL_Joystick* - Joystick support
- SDL_Haptic* - Haptic feedback
- SDL_Audio* - Audio subsystem
- SDL_GL_* - OpenGL integration
- SDL_RWFrom* - Custom I/O

---

## String References Found

### FMOD References (embedded, loaded dynamically)
`
FMOD
FMODEx
FMOD_CODEC_STATE
FMOD_DSP_STATE
FMOD_NONBLOCKING
FMOD_OUTPUT_STATE
fmod_async
fmod_autocleanup
fmod_buckethash
fmod_channelgroupi
fmod_channelpool
fmod_codec
fmod_codec_fsb
fmod_codec_mpeg
fmod_codec_wav
fmod_compositioncore
fmod_dsp_codec
fmod_dsp_codecpool
fmod_dsp_delay
fmod_dsp_echo
fmod_dsp_pitchshift
fmod_dsp_resampler
fmod_dsp_vstplugin
fmod_dsp_winampplugin
fmod_eventcategoryi
fmod_eventenvelope
fmod_eventgroupi
fmod_eventi
fmod_eventimpl_complex
fmod_eventimpl_simple
fmod_eventinstancepool
fmod_eventlayer
fmod_eventparameteri
fmod_eventprojecti
fmod_eventsound
fmod_eventsystemi
fmod_eventuserproperty
fmod_file
fmod_globals
fmod_memory
fmod_musicsystemi
fmod_output_asio
fmod_output_dsound
fmod_output_nosound
fmod_output_software
fmod_output_wasapi
fmod_output_wavwriter
fmod_output_winmm
fmod_profile
fmod_reverbi
fmod_sample_software
fmod_segmentplayer
fmod_soundbank
fmod_sounddef
fmod_soundgroupi
fmod_soundi
fmod_string
fmod_systemi
fmod_thread
fmod2011
fmode
fmodoutput
`

### Lua References (embedded, loaded dynamically)
`
lua_debug
luaopen_
`

### Compression (zlib)
`
deflate
zlib
Uncompress
`

### FSB (FMOD Sample Bank) References
`
FSB
FSB2
FSB3
FSB4
`

---

## Key Findings

### Engine Technology Stack
1. **Renderer:** SDL 2.x + Direct3D 9 + OpenGL (via SDL_GL)
2. **Audio:** FMOD Ex (embedded library), ACM for audio codecs
3. **Video:** Bink Video (RAD Tools)
4. **Compression:** zlib
5. **Scripting:** Lua (embedded)
6. **Input:** DirectInput 8, SDL Input subsystems
7. **Platform:** Steamworks API integration

### Architecture Notes
- **32-bit executable** - Uses x87 floating point, stdcall calling convention
- **Visual Studio 2010 (MSVC 10.0)** - Build environment
- **No external FMOD DLL** - FMOD is statically linked or embedded
- **No external Lua DLL** - Lua is embedded within the executable
- **Custom zlib wrapper** - GZLibFile class provides zlib integration

### Memory Management
- VirtualAlloc/VirtualFree for direct memory allocation
- Heap functions via MSVCR100 (malloc/free)
- Custom GZLibFile for compressed file I/O

### File I/O Pattern
- GSysFile for low-level file operations
- GBufferedFile for buffered I/O
- GZLibFile for compressed streams
- Standard C runtime fopen/fread for some operations

---

## Debug Symbols (.pdb)

**No PDB debug files found** in the game directory.

The executable may have been built with:
- Embedded PDB path (not found)
- No debug symbols
- Debug symbols stripped before distribution

---

## Analysis Notes

- The executable exports functions for **Buddha.exe** (internal engine name)
- FMOD and Lua are **not loaded as separate DLLs** - they appear to be statically linked or embedded
- The game uses **SDL 2.x** as its primary windowing and input framework
- Bink video codec handling is via **binkw32.dll** (RAD Video Tools)
- Direct3D 9 is used for 3D rendering with D3DX extensions for texture handling
- The game has extensive **Steam integration** via steam_api.dll

---

*Analysis Date: 2026-04-01*  
*Tool: dumpbin.exe (Visual Studio 2022 Community)*