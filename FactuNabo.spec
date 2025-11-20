# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import PySide6

project_root = Path.cwd()

# Verificar que los archivos existan antes de incluirlos
def get_data_files():
    """Obtiene la lista de archivos de datos, verificando que existan"""
    files = []
    
    # Archivos de configuración y estilos (en la raíz)
    for file in ['styles.qss', 'EsquemaProformas.xsd']:
        file_path = project_root / file
        if file_path.exists():
            files.append((str(file_path), '.'))
        else:
            print(f"⚠️ ADVERTENCIA: No se encuentra {file}")
    
    # Documentación (en la raíz)
    doc_files = [
        'ESTADO_APLICACION.md',
        'GUIA_RAPIDA.md',
        'MANUAL_USUARIO.md',
        'MANUAL_TECNICO.md',
        'README.md',
        'README_Integracion_Macro.md',
    ]
    for file in doc_files:
        file_path = project_root / file
        if file_path.exists():
            files.append((str(file_path), '.'))
        else:
            print(f"⚠️ ADVERTENCIA: No se encuentra {file}")
    
    # Recursos y plantillas (carpetas completas)
    for folder in ['Plantillas Facturas', 'resources']:
        folder_path = project_root / folder
        if folder_path.exists() and folder_path.is_dir():
            files.append((str(folder_path), folder))
        else:
            print(f"⚠️ ADVERTENCIA: No se encuentra la carpeta {folder}")
    
    return files

data_files = get_data_files()

# Añadir traducciones de Qt necesarias para los diálogos en español
translations_dir = Path(PySide6.__file__).resolve().parent / "translations"
translations = []
for qm_name in ("qtbase_es.qm", "qt_es.qm"):
    qm_path = translations_dir / qm_name
    if qm_path.exists():
        translations.append((str(qm_path), f"translations/{qm_name}"))

datas = data_files + translations

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Módulos que PyInstaller podría no detectar automáticamente
        'app.core.resources',
        'app.core.settings',
        'app.core.logging',
        'app.services.database',
        'app.services.validators',
        'app.services.stats',
        'app.services.maintenance',
        'app.ui.dialogs',
        'app.ui.widgets',
        'macro_adapter',
        'prueba',
        'worker',
        'pdf_downloader',
        'login_dialog',
        'modern_dialogs',
        'dialog_shim',
        'offline_queue',
        'xml.etree.ElementTree',
        'xml.etree.cElementTree',
        'unicodedata',
        'hashlib',
        'json',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos no necesarios para reducir tamaño
        'tkinter',
        'matplotlib',
        'scipy',
        'scikit-learn',
        'PIL',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'unittest',
        'doctest',
        'pdb',
        'pydoc',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FactuNabo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(project_root / 'resources' / 'logo.ico')],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FactuNabo',
)
