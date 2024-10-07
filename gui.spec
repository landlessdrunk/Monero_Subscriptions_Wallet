# -*- mode: python ; coding: utf-8 -*-
import platform

def get_platform(os=platform.system()):
    os = os.lower()
    if os == 'darwin':
        return 'Mac'
    if os == 'windows':
        return 'Windows'
    else:
        return 'Linux'

import urllib.request
import tarfile
import zipfile
monero_url = 'https://downloads.getmonero.org/cli/linux64'
filename = 'monero.tar.bz2'
if get_platform() == 'Mac':
    monero_url = 'https://downloads.getmonero.org/cli/mac64'
elif get_platform() == 'Windows':
    monero_url = 'https://downloads.getmonero.org/cli/win64'
    filename = 'monero.zip'

url_open = urllib.request.Request(monero_url, {}, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
with urllib.request.urlopen(url_open) as response:
    with open(filename, 'wb') as fn:
        fn.write(response.read())

if get_platform() == 'Mac' or get_platform() == 'Linux':
    with tarfile.open(filename, 'r:bz2') as f:
        extract_name = None
        folder_name = None
        for fn in f.getnames():
            if '/' not in fn:
                folder_name = fn
            if 'monero-wallet-rpc' in fn:
                extract_name = fn
        f.extract(extract_name)

    os.rename(extract_name, 'monero-wallet-rpc')
    os.remove(filename)
    os.rmdir(folder_name)

if get_platform() == 'Windows':
    with zipfile.ZipFile(filename, 'r') as z:
        extract_name = None
        for fn in z.namelist():
            if 'monero-wallet-rpc' in fn:
                extract_name = fn
        z.extract(extract_name)

    os.rename(extract_name, 'monero-wallet-rpc')
    os.remove(filename)

a = Analysis(
    ['gui.py'],
    pathex=['./'],
    binaries=[],
    datas=[('./monero_theme.json', '.'), ('./assets/*', 'assets/'), ('./monero-wallet-rpc', '.')],
    hiddenimports=['TKinter', 'PIL._tkinter_finder', 'babel.numbers'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gui',
)
