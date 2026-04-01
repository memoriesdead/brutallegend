@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul
cd /d "%~dp0"
cl /LD /EHsc /O2 /W3 buddha_mod.cpp kernel32.lib user32.lib /Fe:buddha_mod.dll
cl /EHsc /O2 /W3 load_mod.cpp kernel32.lib user32.lib /Fe:load_mod.exe
