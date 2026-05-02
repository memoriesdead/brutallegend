@echo off
cd /d "C:\Users\Kevin\OneDrive\Desktop\steam\steamapps\common\BrutalLegend"
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x86
cl /EHsc /O2 /W3 load_mod.cpp kernel32.lib user32.lib advapi32.lib /Fe:load_mod.exe
