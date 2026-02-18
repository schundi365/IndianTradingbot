# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('templates', 'templates'), ('src', 'src'), ('models', 'models'), ('bot_config.json', '.')]
binaries = []
hiddenimports = ['MetaTrader5', 'pandas', 'numpy', 'flask', 'werkzeug', 'jinja2', 'click', 'itsdangerous', 'markupsafe', 'logging', 'threading', 'datetime', 'pathlib', 'json', 'pickle', 'xgboost', 'xgboost.sklearn', 'xgboost.core', 'xgboost.compat', 'sklearn', 'sklearn.ensemble', 'sklearn.tree', 'joblib', 'src.mt5_trading_bot', 'src.config_manager', 'src.adaptive_risk_manager', 'src.volume_analyzer', 'src.dynamic_sl_manager', 'src.dynamic_tp_manager', 'src.scalping_manager', 'src.split_order_calculator', 'src.trailing_strategies', 'src.enhanced_indicators', 'src.ml_signal_generator', 'src.ml_integration']
tmp_ret = collect_all('flask')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('werkzeug')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jinja2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['web_dashboard.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tensorboard', 'tensorflow', 'torch', 'matplotlib', 'scipy', 'IPython', 'jupyter', 'pytest', 'xgboost.testing'],
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
    name='GEM_Trading_Bot',
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
    icon='NONE',
)
