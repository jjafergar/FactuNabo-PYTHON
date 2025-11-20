"""
Diálogos reutilizables (health check, visor JSON, progreso).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QLineEdit,
    QDateEdit,
    QFormLayout,
    QFrame,
    QCalendarWidget,
    QToolButton,
    QMenu,
    QScrollArea,
)

from app.ui.widgets import AnimatedButton
from app.core.resources import COLOR_PRIMARY, COLOR_SECONDARY_TEXT, COLOR_CARD


class HealthCheckDialog(QDialog):
    def __init__(self, results: Iterable[dict], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Diagnóstico del sistema")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        title = QLabel("Resultados de las comprobaciones")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setProperty("class", "ModernList")
        layout.addWidget(self.list_widget)

        for item in results:
            nombre = item.get("nombre", "Chequeo")
            estado = item.get("estado", "DESCONOCIDO")
            detalle = item.get("detalle", "")
            text = f"{nombre} – {estado}\n{detalle}"
            lw_item = QListWidgetItem(text)
            lw_item.setData(Qt.UserRole, item)
            if estado.upper() == "OK":
                lw_item.setForeground(Qt.darkGreen)
            elif estado.upper() == "ADVERTENCIA":
                lw_item.setForeground(Qt.darkYellow)
            else:
                lw_item.setForeground(Qt.red)
            self.list_widget.addItem(lw_item)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)


class JsonViewerDialog(QDialog):
    def __init__(self, json_path: Path, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(json_path.name)
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.addWidget(QLabel(f"Archivo: {json_path}"))
        header.addStretch()
        layout.addLayout(header)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.text_edit.setPlainText(formatted)
        except Exception as exc:
            self.text_edit.setPlainText(f"No se pudo cargar el JSON:\n{exc}")


class BackupSummaryDialog(QDialog):
    def __init__(self, backup_path: Path, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Copia de seguridad")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        label = QLabel(f"Copia creada en:\n{backup_path}")
        label.setWordWrap(True)
        layout.addWidget(label)

        open_button = AnimatedButton("Abrir Carpeta")
        open_button.clicked.connect(lambda: self._open_parent(backup_path))
        layout.addWidget(open_button, alignment=Qt.AlignRight)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

    def _open_parent(self, backup_path: Path):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl

        QDesktopServices.openUrl(QUrl.fromLocalFile(str(backup_path.parent)))


RECTIFICATIVA_MOTIVOS = [
    ("01", "01 · Número de la factura"),
    ("02", "02 · Serie de la factura"),
    ("03", "03 · Fecha de expedición"),
    ("04", "04 · Nombre/Razón social Emisor"),
    ("05", "05 · Nombre/Razón social Receptor"),
    ("06", "06 · Identificación fiscal Emisor"),
    ("07", "07 · Identificación fiscal Receptor"),
    ("08", "08 · Domicilio Emisor"),
    ("09", "09 · Domicilio Receptor"),
    ("10", "10 · Detalle de la operación"),
    ("11", "11 · Porcentaje impositivo a aplicar"),
    ("12", "12 · Cuota tributaria a aplicar"),
    ("13", "13 · Fecha/Periodo a aplicar"),
    ("14", "14 · Clase de factura"),
    ("15", "15 · Literales legales"),
    ("16", "16 · Base imponible"),
    ("17", "17 · Cálculo de cuotas repercutidas"),
    ("18", "18 · Cálculo de cuotas retenidas"),
    ("19", "19 · Base modificada por devoluciones"),
    ("20", "20 · Base modificada por descuentos/bonificaciones"),
    ("21", "21 · Base modificada por resolución firme"),
    ("22", "22 · Base modificada por cuotas impagadas (concurso)"),
]

RECTIFICATIVA_TIPO_FACTURA = [
    ("R1", "R1 · Rectificación por error de IVA / Art. 80 Uno Dos Seis"),
    ("R2", "R2 · Rectificación Art. 80.3 (créditos incobrables)"),
    ("R3", "R3 · Rectificación Art. 80.4"),
    ("R4", "R4 · Rectificación por otros motivos"),
    ("R5", "R5 · Rectificación en facturas simplificadas"),
]

RECTIFICATIVA_TIPO_OPERACION = [
    ("I", "I · Rectificación por diferencias"),
    ("S", "S · Rectificación por sustitución"),
]


class RectificativaDialog(QDialog):
    """
    Diálogo asistido para capturar los datos obligatorios de una factura rectificativa
    sin necesidad de modificarlos en la macro original.
    """

    def __init__(self, invoice_id: str, empresa: str, defaults: dict | None = None, suggestion: dict | None = None, parent: QWidget | None = None, needs_historical_excel: bool = False, invoice_year: int | None = None, excel_year: int | None = None, on_load_historical_excel: callable | None = None):
        super().__init__(parent)
        self.setWindowTitle("Rectificativa asistida")
        self.setMinimumWidth(560)
        self.setMinimumHeight(820)
        self.resize(980, 980)
        self.result: dict | None = None
        self.suggestion = suggestion or {}
        self.original_summary = self.suggestion.get("original_summary") or {}
        self.needs_historical_excel = needs_historical_excel
        self.invoice_year = invoice_year
        self.excel_year = excel_year
        self.on_load_historical_excel = on_load_historical_excel
        self.invoice_id = invoice_id
        self.updated_suggestion = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        card = QFrame()
        card.setProperty("class", "ConfigGroup")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 32)
        card_layout.setSpacing(20)

        title = QLabel("Rectificativa asistida")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        card_layout.addWidget(title)

        subtitle = QLabel(f"Factura seleccionada: <b>{invoice_id}</b><br/>Empresa emisora: <b>{empresa}</b>")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLOR_SECONDARY_TEXT};")
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)

        # [NUEVO] Mostrar advertencia y botón para cargar Excel histórico
        if self.needs_historical_excel and self.invoice_year and self.excel_year:
            warning_frame = QFrame()
            warning_frame.setObjectName("HistoricalExcelWarning")
            warning_frame.setStyleSheet(
                """
                QFrame#HistoricalExcelWarning {
                    background: rgba(255,193,7,0.15);
                    border: 1px solid rgba(255,193,7,0.4);
                    border-radius: 10px;
                    padding: 12px;
                }
                QFrame#HistoricalExcelWarning QLabel {
                    color: #856404;
                }
                """
            )
            warning_layout = QVBoxLayout(warning_frame)
            warning_layout.setContentsMargins(12, 12, 12, 12)
            warning_layout.setSpacing(8)
            
            warning_text = QLabel(
                f"⚠️ La factura <b>{invoice_id}</b> parece ser del año <b>{self.invoice_year}</b>, "
                f"pero el Excel actual contiene facturas del año <b>{self.excel_year}</b>.\n\n"
                f"La factura original no se encontró en el histórico del Excel actual.\n\n"
                f"<b>Carga el Excel del año {self.invoice_year}</b> para buscar la factura original automáticamente."
            )
            warning_text.setWordWrap(True)
            warning_layout.addWidget(warning_text)
            
            load_excel_btn = AnimatedButton(f"📁 Cargar Excel del año {self.invoice_year}")
            load_excel_btn.setProperty("class", "PrimaryButton")
            load_excel_btn.clicked.connect(self._on_load_historical_excel)
            warning_layout.addWidget(load_excel_btn)
            
            card_layout.addWidget(warning_frame)

        if self.suggestion.get("message"):
            info_frame = QFrame()
            info_frame.setObjectName("SuggestionFrame")
            info_frame.setStyleSheet(
                """
                QFrame#SuggestionFrame {
                    background: rgba(160,191,110,0.15);
                    border-radius: 10px;
                    padding: 12px;
                }
                QFrame#SuggestionFrame QLabel {
                    color: #2D2D2D;
                }
                """
            )
            info_layout = QHBoxLayout(info_frame)
            info_layout.setContentsMargins(0, 0, 0, 0)
            self.info_label = QLabel(self.suggestion["message"])
            self.info_label.setWordWrap(True)
            info_layout.addWidget(self.info_label)
            card_layout.addWidget(info_frame)
        else:
            self.info_label = None

        if self.original_summary:
            card_layout.addWidget(self._build_original_summary(self.original_summary))

        quick_row = QHBoxLayout()
        quick_row.setSpacing(8)
        quick_row.addWidget(QLabel("Acciones rápidas:"))
        quick_row.addStretch()
        card_layout.addLayout(quick_row)

        self.quick_hint_label = QLabel("Selecciona una acción rápida para rellenar los campos más habituales.")
        self.quick_hint_label.setStyleSheet(f"color: {COLOR_SECONDARY_TEXT}; font-style: italic;")

        quick_buttons = QHBoxLayout()
        quick_buttons.setSpacing(6)
        actions = [
            ("Conceptos actualizados", {"tipo_factura": "R4", "factura_rectificativa_tipo": "I", "factura_rectificativa_codigo": "10"}, "Usa esta opción cuando solo cambias descripciones o conceptos sin tocar importes."),
            ("Ajustar importes/IVA", {"tipo_factura": "R1", "factura_rectificativa_tipo": "I", "factura_rectificativa_codigo": "16"}, "Usa R1 cuando ajustas importes, bases imponibles o tipos de IVA."),
            ("Cambios de datos", {"tipo_factura": "R4", "factura_rectificativa_tipo": "I", "factura_rectificativa_codigo": "05"}, "Empléala si actualizas datos del receptor o del emisor."),
            ("Sustitución completa", {"tipo_factura": "R4", "factura_rectificativa_tipo": "S", "factura_rectificativa_codigo": "16"}, "Utilízala cuando anulas la original e introduces una nueva con importes negativos y positivos."),
        ]
        self.quick_actions = actions
        for label, payload, hint in actions:
            btn = AnimatedButton(label)
            btn.setProperty("class", "SecondaryButton")
            btn.setFixedHeight(30)
            btn.clicked.connect(lambda _, data=payload, text=hint: self._apply_quick_action(data, text))
            quick_buttons.addWidget(btn)
        card_layout.addLayout(quick_buttons)
        card_layout.addWidget(self.quick_hint_label)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.numero_edit = QLineEdit()
        self.numero_edit.setPlaceholderText("Número de la factura original")
        form.addRow("Factura original:", self.numero_edit)

        self.ejercicio_edit = QLineEdit()
        self.ejercicio_edit.setPlaceholderText("Ejercicio (ej. 2024)")
        self.ejercicio_edit.setMaxLength(4)
        form.addRow("Ejercicio original:", self.ejercicio_edit)

        self.fecha_edit = QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDisplayFormat("dd/MM/yyyy")
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setObjectName("RectificativaDateEdit")
        self._decorate_calendar_popup(self.fecha_edit.calendarWidget())
        form.addRow("Fecha factura original:", self.fecha_edit)

        self.tipo_factura_combo = QComboBox()
        for code, text in RECTIFICATIVA_TIPO_FACTURA:
            self.tipo_factura_combo.addItem(text, code)
        form.addRow("Tipo de rectificativa:", self.tipo_factura_combo)

        self.motivo_combo = QComboBox()
        for code, text in RECTIFICATIVA_MOTIVOS:
            self.motivo_combo.addItem(text, code)
        form.addRow("Motivo oficial:", self.motivo_combo)

        self.tipo_operacion_combo = QComboBox()
        for code, text in RECTIFICATIVA_TIPO_OPERACION:
            self.tipo_operacion_combo.addItem(text, code)
        form.addRow("Modalidad:", self.tipo_operacion_combo)

        self.justificacion_edit = QTextEdit()
        self.justificacion_edit.setPlaceholderText("Justificación adicional (opcional, se añadirá a la observación/texto libre).")
        self.justificacion_edit.setFixedHeight(90)
        self.justificacion_edit.setObjectName("RectificativaJustificacion")
        self.justificacion_edit.setStyleSheet(
            """
            QTextEdit#RectificativaJustificacion {
                border: 1px solid rgba(0,0,0,0.12);
                border-radius: 8px;
                padding: 8px;
                background: rgba(255,255,255,0.92);
            }
            QTextEdit#RectificativaJustificacion:focus {
                border: 1px solid #A0BF6E;
                background: rgba(255,255,255,1.0);
            }
            """
        )
        form.addRow("Justificación adicional:", self.justificacion_edit)

        card_layout.addLayout(form)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(card)
        root.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        buttons.addStretch()
        ok_btn = AnimatedButton("Aceptar")
        ok_btn.clicked.connect(self._on_accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setProperty("class", "LinkButton")
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        root.addLayout(buttons)

        self._apply_suggestion(self.suggestion, defaults or {})
        if defaults:
            self._apply_defaults(defaults)

    def _decorate_calendar_popup(self, calendar: QCalendarWidget):
        if not calendar:
            return
        calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        calendar.setStyleSheet(
            f"""
            QCalendarWidget QWidget {{
                background-color: {COLOR_CARD};
            }}
            QCalendarWidget QToolButton {{
                color: {COLOR_PRIMARY};
                font-weight: 600;
                padding: 6px;
                border-radius: 6px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: rgba(160,191,110,0.12);
            }}
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {{
                width: 24px;
                color: {COLOR_SECONDARY_TEXT};
            }}
            QCalendarWidget QTableView {{
                selection-background-color: {COLOR_PRIMARY};
                selection-color: white;
                border: 0px;
            }}
            QCalendarWidget QTableView:item {{
                padding: 6px;
            }}
            QCalendarWidget QMenu {{
                background-color: {COLOR_CARD};
                color: #000000;
                border: 1px solid rgba(0,0,0,0.12);
                font-weight: 600;
            }}
            QCalendarWidget QMenu::item {{
                padding: 6px 10px;
                color: #000000;
                font-weight: normal;
            }}
            QCalendarWidget QMenu::item:selected {{
                background-color: rgba(160,191,110,0.18);
                color: #000000;
                font-weight: 600;
            }}
            """
        )
        calendar.setSelectedDate(self.fecha_edit.date())

        month_button = calendar.findChild(QToolButton, "qt_calendar_monthbutton")
        if month_button:
            month_button.setPopupMode(QToolButton.InstantPopup)

        year_button = calendar.findChild(QToolButton, "qt_calendar_yearbutton")
        if year_button:
            year_button.setPopupMode(QToolButton.InstantPopup)
            year_menu = QMenu(calendar)
            year_menu.setStyleSheet(
                """
                QMenu {{
                    background-color: rgba(255,255,255,0.98);
                    border: 1px solid rgba(0,0,0,0.12);
                }}
                QMenu::item {{
                    padding: 6px 12px;
                    color: #000000;
                }}
                QMenu::item:selected {{
                    background-color: rgba(160,191,110,0.18);
                    color: #000000;
                    font-weight: 600;
                }}
                """
            )

            def populate_year_menu():
                year_menu.clear()
                current_year = self.fecha_edit.date().year()
                start = current_year - 8
                end = current_year + 9
                for year in range(start, end):
                    action = year_menu.addAction(str(year))
                    action.setData(year)

            def on_year_selected(action):
                year = action.data()
                if year is None:
                    return
                current_date = self.fecha_edit.date()
                month = current_date.month()
                day = current_date.day()
                max_day = QDate(year, month, 1).daysInMonth()
                new_date = QDate(year, month, min(day, max_day))
                self.fecha_edit.setDate(new_date)
                calendar.setSelectedDate(new_date)

            year_menu.aboutToShow.connect(populate_year_menu)
            year_menu.triggered.connect(on_year_selected)
            year_button.setMenu(year_menu)

    def _apply_defaults(self, defaults: dict) -> None:
        numero = defaults.get("factura_rectificativa_numero")
        if numero:
            self.numero_edit.setText(str(numero))

        ejercicio = defaults.get("factura_rectificativa_ejercicio")
        if ejercicio:
            self.ejercicio_edit.setText(str(ejercicio))

        fecha = defaults.get("factura_rectificativa_fecha_emision")
        if fecha:
            try:
                qdate = QDate.fromString(str(fecha), "yyyy-MM-dd")
                if not qdate.isValid():
                    qdate = QDate.fromString(str(fecha), "dd/MM/yyyy")
                if qdate.isValid():
                    self.fecha_edit.setDate(qdate)
            except Exception:
                pass

        tipo_factura = defaults.get("tipo_factura")
        if tipo_factura:
            idx = self.tipo_factura_combo.findData(str(tipo_factura))
            if idx >= 0:
                self.tipo_factura_combo.setCurrentIndex(idx)

        motivo = defaults.get("factura_rectificativa_codigo")
        if motivo:
            idx = self.motivo_combo.findData(str(motivo))
            if idx >= 0:
                self.motivo_combo.setCurrentIndex(idx)

        tipo_operacion = defaults.get("factura_rectificativa_tipo")
        if tipo_operacion:
            idx = self.tipo_operacion_combo.findData(str(tipo_operacion))
            if idx >= 0:
                self.tipo_operacion_combo.setCurrentIndex(idx)

        justificacion = defaults.get("justificacion", "")
        if justificacion:
            self.justificacion_edit.setPlainText(str(justificacion))

    def _apply_suggestion(self, suggestion: dict, defaults: dict):
        if not suggestion:
            return

        existing_tipo = defaults.get("tipo_factura") if defaults else None
        suggested_tipo = suggestion.get("tipo_factura")
        if suggested_tipo and not existing_tipo:
            idx = self.tipo_factura_combo.findData(suggested_tipo)
            if idx >= 0:
                self.tipo_factura_combo.setCurrentIndex(idx)

        existing_modalidad = defaults.get("factura_rectificativa_tipo") if defaults else None
        suggested_modalidad = suggestion.get("factura_rectificativa_tipo")
        if suggested_modalidad and not existing_modalidad:
            idx = self.tipo_operacion_combo.findData(suggested_modalidad)
            if idx >= 0:
                self.tipo_operacion_combo.setCurrentIndex(idx)

        existing_motivo = defaults.get("factura_rectificativa_codigo") if defaults else None
        suggested_motivo = suggestion.get("factura_rectificativa_codigo")
        if suggested_motivo and not existing_motivo:
            idx = self.motivo_combo.findData(suggested_motivo)
            if idx >= 0:
                self.motivo_combo.setCurrentIndex(idx)

        original = suggestion.get("original_summary") or {}
        if original:
            if not self.numero_edit.text().strip():
                self.numero_edit.setText(str(original.get("num_factura", "")))
            if not self.ejercicio_edit.text().strip():
                self.ejercicio_edit.setText(str(original.get("ejercicio", "")))
            fecha_raw = original.get("fecha")
            if fecha_raw:
                for fmt in ("yyyy-MM-dd", "yyyy/MM/dd", "dd/MM/yyyy"):
                    qdate = QDate.fromString(str(fecha_raw), fmt)
                    if qdate.isValid():
                        self.fecha_edit.setDate(qdate)
                        break
            elif original.get("fecha_formateada"):
                qdate = QDate.fromString(original["fecha_formateada"], "dd/MM/yyyy")
                if qdate.isValid():
                    self.fecha_edit.setDate(qdate)

    def _apply_quick_action(self, payload: dict, hint: str):
        tipo = payload.get("tipo_factura")
        modalidad = payload.get("factura_rectificativa_tipo")
        motivo = payload.get("factura_rectificativa_codigo")

        if tipo:
            idx = self.tipo_factura_combo.findData(tipo)
            if idx >= 0:
                self.tipo_factura_combo.setCurrentIndex(idx)
        if modalidad:
            idx = self.tipo_operacion_combo.findData(modalidad)
            if idx >= 0:
                self.tipo_operacion_combo.setCurrentIndex(idx)
        if motivo:
            idx = self.motivo_combo.findData(motivo)
            if idx >= 0:
                self.motivo_combo.setCurrentIndex(idx)

        if hint:
            self.quick_hint_label.setText(hint)

    def _build_original_summary(self, data: dict) -> QFrame:
        frame = QFrame()
        frame.setObjectName("OriginalSummaryFrame")
        frame.setStyleSheet(
            """
            QFrame#OriginalSummaryFrame {
                background: rgba(0,0,0,0.04);
                border-radius: 10px;
                padding: 12px;
            }
            """
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title = QLabel("Factura original")
        title.setStyleSheet("font-weight: 600;")
        layout.addWidget(title)

        cliente = data.get("cliente") or "—"
        fecha = data.get("fecha_formateada") or "—"
        source_tag = data.get("fuente")
        if source_tag in ("hist_row", "conceptos", "histórico"):
            fuente = "Hoja histórico"
        elif source_tag in ("db", "base_datos"):
            fuente = "Histórico FactuNabo"
        else:
            fuente = "Histórico FactuNabo"
        lines = [
            f"Cliente: {cliente}",
            f"Fecha emisión: {fecha}",
            f"Base: {data.get('base_texto', '—')} · IVA: {data.get('iva_texto', '—')}",
            f"Total: {data.get('importe_texto', '—')}",
            f"Datos obtenidos de: {fuente}",
        ]
        for line in lines:
            label = QLabel(line)
            label.setStyleSheet(f"color: {COLOR_SECONDARY_TEXT};")
            layout.addWidget(label)

        return frame

    def _on_load_historical_excel(self):
        """Abre un diálogo para seleccionar el Excel histórico y lo carga."""
        if not self.on_load_historical_excel:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleccionar Excel del año {self.invoice_year}",
            "",
            "Archivos Excel (*.xlsx *.xlsm);;Todos los archivos (*.*)"
        )
        
        if not file_path:
            return
        
        # Mostrar mensaje de carga
        msg = QMessageBox(self)
        msg.setWindowTitle("Cargando Excel histórico")
        msg.setText("Cargando el Excel histórico y buscando la factura original...")
        msg.setStandardButtons(QMessageBox.NoButton)
        msg.show()
        msg.repaint()
        QApplication.processEvents()
        
        try:
            # Cargar el Excel histórico
            updated_suggestion = self.on_load_historical_excel(file_path)
            
            if updated_suggestion and updated_suggestion.get("diagnostic", {}).get("original_found"):
                # Se encontró la factura original
                self.updated_suggestion = updated_suggestion
                self.suggestion = updated_suggestion
                self.original_summary = updated_suggestion.get("original_summary") or {}
                
                # Buscar el card layout para actualizar el diálogo
                scroll = self.findChild(QScrollArea)
                if scroll:
                    card = scroll.findChild(QFrame, "ConfigGroup")
                    if card:
                        card_layout = card.layout()
                        if card_layout:
                            # Eliminar el frame de advertencia si existe
                            for i in range(card_layout.count()):
                                item = card_layout.itemAt(i)
                                if item:
                                    widget = item.widget()
                                    if widget and widget.objectName() == "HistoricalExcelWarning":
                                        widget.deleteLater()
                                        break
                            
                            # Añadir el resumen de la factura original si no existe ya
                            if self.original_summary:
                                # Verificar si ya existe un frame de resumen original
                                has_original_frame = False
                                for i in range(card_layout.count()):
                                    item = card_layout.itemAt(i)
                                    if item:
                                        widget = item.widget()
                                        if widget and widget.objectName() == "OriginalSummaryFrame":
                                            has_original_frame = True
                                            # Actualizar el frame existente
                                            widget.deleteLater()
                                            break
                                
                                # Añadir el nuevo frame de resumen
                                original_frame = self._build_original_summary(self.original_summary)
                                # Insertar después del subtitle (índice 1) o después de la advertencia si existía
                                insert_index = 2
                                card_layout.insertWidget(insert_index, original_frame)
                            
                            # Actualizar el mensaje de sugerencia si existe
                            if updated_suggestion.get("message"):
                                info_frame = card.findChild(QFrame, "SuggestionFrame")
                                if info_frame:
                                    info_label = info_frame.findChild(QLabel)
                                    if info_label:
                                        info_label.setText(updated_suggestion["message"])
                                else:
                                    # Crear nuevo frame de sugerencia
                                    info_frame = QFrame()
                                    info_frame.setObjectName("SuggestionFrame")
                                    info_frame.setStyleSheet(
                                        """
                                        QFrame#SuggestionFrame {
                                            background: rgba(160,191,110,0.15);
                                            border-radius: 10px;
                                            padding: 12px;
                                        }
                                        QFrame#SuggestionFrame QLabel {
                                            color: #2D2D2D;
                                        }
                                        """
                                    )
                                    info_layout = QHBoxLayout(info_frame)
                                    info_layout.setContentsMargins(0, 0, 0, 0)
                                    info_label = QLabel(updated_suggestion["message"])
                                    info_label.setWordWrap(True)
                                    info_layout.addWidget(info_label)
                                    # Insertar después del resumen original
                                    card_layout.insertWidget(3, info_frame)
                
                # Actualizar los campos con los datos encontrados
                self._apply_suggestion(updated_suggestion, {})
                
                msg.close()
                QMessageBox.information(
                    self,
                    "Excel histórico cargado",
                    f"✅ Se encontró la factura original en el Excel del año {self.invoice_year}.\n\n"
                    f"Los datos se han actualizado automáticamente."
                )
            else:
                msg.close()
                QMessageBox.warning(
                    self,
                    "Factura no encontrada",
                    f"⚠️ No se encontró la factura {self.invoice_id} en el Excel seleccionado.\n\n"
                    f"Verifica que el Excel sea del año correcto y que contenga la factura original."
                )
        except Exception as e:
            msg.close()
            QMessageBox.critical(
                self,
                "Error",
                f"❌ Error al cargar el Excel histórico:\n\n{str(e)}"
            )

    def _on_accept(self):
        numero = self.numero_edit.text().strip()
        ejercicio = self.ejercicio_edit.text().strip()
        if not numero:
            QMessageBox.warning(self, "Dato requerido", "Indica el número de la factura original.")
            return

        if ejercicio and not ejercicio.isdigit():
            QMessageBox.warning(self, "Dato inválido", "El ejercicio debe contener únicamente dígitos (por ejemplo 2024).")
            return

        fecha_iso = self.fecha_edit.date().toString("yyyy-MM-dd")
        self.result = {
            "tipo_factura": self.tipo_factura_combo.currentData(),
            "factura_rectificativa_numero": numero,
            "factura_rectificativa_ejercicio": ejercicio,
            "factura_rectificativa_fecha_emision": fecha_iso,
            "factura_rectificativa_codigo": self.motivo_combo.currentData(),
            "factura_rectificativa_tipo": self.tipo_operacion_combo.currentData(),
            "justificacion": self.justificacion_edit.toPlainText().strip(),
        }
        self.accept()


