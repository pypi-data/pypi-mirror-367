import sys
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QFormLayout, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt
from .model import ConfigModel

class ServerInstanceWidget(QWidget):
    def __init__(self, server_instance):
        super().__init__()
        self.server = server_instance
        self.layout = QFormLayout(self)
        # Host
        self.host_edit = QLineEdit(self.server.get_value('host'))
        self._set_default_style('host', self.host_edit)
        self.host_edit.textChanged.connect(lambda val: self._on_edit('host', val, self.host_edit))
        self.layout.addRow("Host", self.host_edit)
        # Autostart
        self.autostart_box = QCheckBox()
        self.autostart_box.setChecked(self.server.get_value('autostart'))
        self._set_default_style('autostart', self.autostart_box)
        self.autostart_box.stateChanged.connect(lambda _: self._on_edit('autostart', self.autostart_box.isChecked(), self.autostart_box))
        self.layout.addRow("Autostart", self.autostart_box)
        # Initial Delay
        self.initial_delay_edit = QLineEdit(str(self.server.get_value('initial_delay_sec')))
        self._set_default_style('initial_delay_sec', self.initial_delay_edit)
        self.initial_delay_edit.textChanged.connect(lambda val: self._on_edit('initial_delay_sec', val, self.initial_delay_edit))
        self.layout.addRow("Initial Delay (s)", self.initial_delay_edit)
        # Response Delay
        self.delay_edit = QLineEdit(str(self.server.get_value('response_delay_sec')))
        self._set_default_style('response_delay_sec', self.delay_edit)
        self.delay_edit.textChanged.connect(lambda val: self._on_edit('response_delay_sec', val, self.delay_edit))
        self.layout.addRow("Response Delay (s)", self.delay_edit)
        # Route
        self.route_edit = QLineEdit(self.server.get_value('route'))
        self._set_default_style('route', self.route_edit)
        self.route_edit.textChanged.connect(lambda val: self._on_edit('route', val, self.route_edit))
        self.layout.addRow("Route", self.route_edit)
        # Methoden (Checkboxen horizontal)
        self.methods_checks = []
        self.methods_layout = QHBoxLayout()
        default_methods = self.server.defaults.get('methodes', [])
        current_methods = self.server.get_value('methodes') or []
        for m in default_methods:
            cb = QCheckBox(m)
            cb.setChecked(m in current_methods)
            cb.stateChanged.connect(self._on_methods_changed)
            self.methods_checks.append(cb)
            self.methods_layout.addWidget(cb)
        self.layout.addRow("Methoden", self.methods_layout)
        # Response (großes Textfeld)
        self.response_edit = QTextEdit(self.server.get_value('response') if self.server.get_value('response') else "")
        self.response_edit.setMinimumHeight(120)
        self._set_default_style('response', self.response_edit)
        self.response_edit.textChanged.connect(lambda: self._on_edit('response', self.response_edit.toPlainText(), self.response_edit))
        self.response_edit.focusOutEvent = self._response_focus_out_event
        self.layout.addRow("Response", self.response_edit)
        # Initiale Validierung und Pretty-Print
        self._validate_and_pretty_response()

    def _set_default_style(self, key, widget):
        if self.server.is_default(key):
            widget.setStyleSheet("color: gray;")
        else:
            widget.setStyleSheet("")

    def _on_edit(self, key, value, widget):
        # Wenn Feld geleert wird, auf Default zurücksetzen
        if isinstance(widget, QLineEdit) and value.strip() == "":
            value = self.server.defaults.get(key, "")
            widget.setText(str(value))
        if key == 'response_delay_sec':
            try:
                value = float(value)
            except Exception:
                pass
        self.server.set_value(key, value)
        self._set_default_style(key, widget)

    def _on_methods_changed(self):
        selected = [cb.text() for cb in self.methods_checks if cb.isChecked()]
        if not selected:
            # Mindestens eine Checkbox muss ausgewählt sein
            self.methods_checks[0].setChecked(True)
            selected = [self.methods_checks[0].text()]
        self.server.set_value('methodes', selected)
        # Info-Label entfernt

    # _reset_defaults entfernt

    def _validate_and_pretty_response(self):
        text = self.response_edit.toPlainText()
        try:
            parsed = json.loads(text)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            self.response_edit.setPlainText(pretty)
            self.response_edit.setStyleSheet("")
        except Exception:
            self.response_edit.setStyleSheet("background-color: #ffcccc;")

    def _response_focus_out_event(self, event):
        # Wenn Response-Feld geleert wird, auf Default zurücksetzen
        text = self.response_edit.toPlainText()
        if text.strip() == "":
            default = self.server.defaults.get('response', "")
            self.response_edit.setPlainText(default)
        self._validate_and_pretty_response()
        super(QTextEdit, self.response_edit).focusOutEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    config = ConfigModel("config.yaml")
    if config.servers:
        w = ServerInstanceWidget(config.servers[0])
        w.setWindowTitle("Server-Instanz (Demo)")
        w.show()
        sys.exit(app.exec())
    else:
        print("Keine Server-Instanz in config.yaml gefunden.")
