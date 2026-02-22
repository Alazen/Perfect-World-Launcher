# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


datas = [
    ('perfect_world_launcher_v24.0\\launcher\\ui\\settings.json', 'launcher/ui'),
]

hiddenimports = collect_submodules('launcher')


a = Analysis(
    ['perfect_world_launcher_v24.0\\perfect_world_launcher_v24.0.py'],
    pathex=['perfect_world_launcher_v24.0'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_copy_settings.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PerfectWorldLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets\\pw_launcher_icon_3.ico',
)

