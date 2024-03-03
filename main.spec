# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    [
        'main.py',
        'multiPageHandler.py',
        'home_page.py',
        'create_well.py',
        'well_table.py',
        'preview.py',
        'theis_page.py',
        'cooper_jacob_page.py',
        'theis_recovery_page.py',
        'about_us_page.py',
        'help.py'
    ],
    pathex=[],
    binaries=[],
    datas = [
        ('database.db', '.'),
        ('icon.ico', '.'),
        ('aquaprobe_logo.png', '.'),
        ('Home_image1.gif', '.'),
        ('logo.png', '.'),
        ('ministry_of_education_logo.png', '.'),
        ('New_Sinhgad_Logo_2013_300-removebg-preview.png', '.'),
        ('sih_logo.png', '.'),
        ('carousel_images', 'carousel_images'),
        ('about_us.ui', '.'),
        ('cooper_jacob.ui', '.'),
        ('create_well.ui', '.'),
        ('help.ui', '.'),
        ('home_page.ui', '.'),
        ('preview.ui', '.'),
        ('read_well.ui', '.'),
        ('theis.ui', '.'),
        ('theis_recovery.ui', '.'),
        ('update_well.ui', '.'),
        ('well_table.ui', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['gevent'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.datas,
    [],
    exclude_binaries=True,
    name='AquaProbe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
