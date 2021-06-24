# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['prueba.py'],
             pathex=['C:\\Users\\Rodrigo\\Documents\\SIDER\\Scrap Optimization'],
             binaries=[],
             datas=[('Images', 'Images'), ('scrap.db', '.'), ('CERT', 'CERT')],
             hiddenimports=['babel.numbers','python-certifi-win32'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Kedalion',
          debug=False,
          bootloader_ignore_signals=False,
          icon='Images\kedalionicon.ico',
          console=True,
          strip=False,
          upx=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='prueba')
