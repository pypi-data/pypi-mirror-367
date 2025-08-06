# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('../golding_NEURON/cells', 'golding_NEURON/cells'), ('cell_pics', 'cell_pics'), ('../golding_NEURON/logs', 'golding_NEURON/logs'), ('../golding_NEURON/golding_NEURON_default_config.json', 'golding_NEURON')]
binaries = [('nrnivmodl', '.')]
hiddenimports = []
tmp_ret = collect_all('neuron')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('golding_NEURON')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('setuptools')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['ap_adjuster.py'],
    pathex=['../golding_NEURON'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='GoldingMSO',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icns/icon_1024x1024_1024x1024.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GoldingMSO',
)
app = BUNDLE(
    coll,
    name='GoldingMSO.app',
    icon='icns/icon_1024x1024_1024x1024.icns',
    bundle_identifier=None,
)
