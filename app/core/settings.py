from __future__ import annotations

"""
Wrapper ligero sobre QSettings para centralizar claves y valores por defecto.
Guarda la configuración en un archivo .ini dentro de la carpeta de la aplicación
para que se copie junto con el ejecutable.
"""

import os
import sys
from typing import Any, Optional

from PySide6.QtCore import QSettings, QStandardPaths


class AppSettings:
    """
    Pequeño helper para acceder a QSettings con claves centralizadas.
    Usa formato INI para guardar en la carpeta de la aplicación (portable).
    """

    ORGANIZATION = "FactuNabo"
    APPLICATION = "FactuNaboApp"
    CONFIG_FILENAME = "config.ini"

    KEY_ACCENT_COLOR = "accent_color"
    KEY_SPACING = "spacing"
    KEY_THEME = "theme"
    KEY_PDF_DEST = "pdf_destination"
    KEY_API_URL = "api/url"
    KEY_API_TOKEN = "api/token"
    KEY_API_USER = "api/user"
    KEY_API_TIMEOUT = "api/timeout"
    KEY_TEMPLATE_URL = "templates/update_url"

    def __init__(self) -> None:
        # Determinar la ruta de la carpeta de la aplicación
        if getattr(sys, "frozen", False):
            # Ejecutable compilado: usar la carpeta del .exe
            app_dir = os.path.dirname(sys.executable)
        else:
            # Desarrollo: usar la carpeta del proyecto
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Ruta completa del archivo de configuración
        config_path = os.path.join(app_dir, self.CONFIG_FILENAME)
        
        # Usar QSettings con formato INI para guardar en archivo (portable)
        self._settings = QSettings(config_path, QSettings.IniFormat)

    def value(self, key: str, default: Optional[Any] = None) -> Any:
        return self._settings.value(key, default)

    def set_value(self, key: str, value: Any) -> None:
        self._settings.setValue(key, value)

    # Compatibilidad con código existente (nomenclatura Qt)
    def setValue(self, key: str, value: Any) -> None:
        self.set_value(key, value)

    def remove(self, key: str) -> None:
        self._settings.remove(key)

    def sync(self) -> None:
        """Sincroniza los cambios con el archivo de configuración."""
        self._settings.sync()
        # Asegurar que el archivo se escriba inmediatamente
        # QSettings debería hacerlo automáticamente, pero forzamos la escritura
        try:
            # Obtener la ruta del archivo de configuración
            config_path = self._settings.fileName()
            if config_path:
                # Verificar que el archivo existe y es escribible
                import os
                config_dir = os.path.dirname(config_path)
                if config_dir and not os.path.exists(config_dir):
                    os.makedirs(config_dir, exist_ok=True)
        except Exception:
            # Si hay error, no hacer nada - QSettings debería manejar la escritura
            pass


def get_settings() -> AppSettings:
    return AppSettings()


__all__ = ["AppSettings", "get_settings"]

