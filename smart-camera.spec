# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for Smart Meeting Camera
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect MediaPipe data files (models)
mediapipe_datas = collect_data_files('mediapipe', include_py_files=False)

# Collect all mediapipe submodules
mediapipe_hiddenimports = collect_submodules('mediapipe')

# Additional hidden imports
hidden_imports = [
    'cv2',
    'numpy',
    'pyvirtualcam',
    'tkinter',
    'tkinter.ttk',
    'tkinter.font',
    'PIL',
    'PIL._tkinter_finder',
] + mediapipe_hiddenimports

# Data files to include
added_files = [
    ('resources/icon.png', 'resources'),
]

# Add MediaPipe data files
added_files.extend(mediapipe_datas)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'pytest',
        'setuptools',
    ],
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
    name='smart-camera',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for GUI-only mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='smart-camera',
)
