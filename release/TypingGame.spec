# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

import sys

project_root = os.path.abspath(os.getcwd())
python_base = sys.base_prefix

# python3.dll is the stable ABI shim required by python314.dll at load time
extra_binaries = [
    (os.path.join(python_base, 'python3.dll'), '.'),
]


a = Analysis(
    [os.path.join(project_root, 'typing_game.py')],
    pathex=[project_root],
    binaries=extra_binaries,
    datas=[],
    hiddenimports=['pygame'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TypingGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    contents_directory='.',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TypingGame',
)
