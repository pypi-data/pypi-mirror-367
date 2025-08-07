import json
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QCheckBox, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt
from .model import ClientInstance

class ClientInstanceWidget(QWidget):
    def __init__(self, client_instance):
        super().__init__()
        self.client = client_instance
        self.layout = QFormLayout(self)
        # Host
        self.host_edit = QLineEdit(self.client.get_value('host'))
        self._set_default_style('host', self.host_edit)
        self.host_edit.textChanged.connect(lambda val: self._on_edit('host', val, self.host_edit))
        self.layout.addRow("Host", self.host_edit)
        # Autostart
        self.autostart_box = QCheckBox()
        self.autostart_box.setChecked(self.client.get_value('autostart'))
        self._set_default_style('autostart', self.autostart_box)
        self.autostart_box.stateChanged.connect(lambda _: self._on_edit('autostart', self.autostart_box.isChecked(), self.autostart_box))
        self.layout.addRow("Autostart", self.autostart_box)
        # Initial Delay
        self.initial_delay_edit = QLineEdit(str(self.client.get_value('initial_delay_sec')))
        self._set_default_style('initial_delay_sec', self.initial_delay_edit)
        self.initial_delay_edit.textChanged.connect(lambda val: self._on_edit('initial_delay_sec', val, self.initial_delay_edit))
        self.layout.addRow("Initial Delay (s)", self.initial_delay_edit)
        # Loop
        self.loop_box = QCheckBox()
        self.loop_box.setChecked(self.client.get_value('loop'))
        self._set_default_style('loop', self.loop_box)
        self.loop_box.stateChanged.connect(lambda _: self._on_edit('loop', self.loop_box.isChecked(), self.loop_box))
        self.layout.addRow("Loop", self.loop_box)
        # Period_sec
        self.period_edit = QLineEdit(str(self.client.get_value('period_sec')))
        self._set_default_style('period_sec', self.period_edit)
        self.period_edit.textChanged.connect(lambda val: self._on_edit('period_sec', val, self.period_edit))
        self.layout.addRow("Period (s)", self.period_edit)
        # Route
        self.route_edit = QLineEdit(self.client.get_value('route'))
        self._set_default_style('route', self.route_edit)
        self.route_edit.textChanged.connect(lambda val: self._on_edit('route', val, self.route_edit))
        self.layout.addRow("Route", self.route_edit)
        # Methode (Checkboxen horizontal, exklusiv)
        self.methode_checks = []
        self.methode_layout = QHBoxLayout()
        for m in self.client.server_methods:
            cb = QCheckBox(m)
            cb.setChecked(m == self.client.get_value('methode'))
            cb.stateChanged.connect(self._on_methode_changed)
            self.methode_checks.append(cb)
            self.methode_layout.addWidget(cb)
        self.layout.addRow("Methode", self.methode_layout)
        # Request (großes Textfeld)
        self.request_edit = QTextEdit(self.client.get_value('request') if self.client.get_value('request') else "")
        self.request_edit.setMinimumHeight(120)
        self._set_default_style('request', self.request_edit)
        self.request_edit.textChanged.connect(lambda: self._on_edit('request', self.request_edit.toPlainText(), self.request_edit))
        self.request_edit.focusOutEvent = self._request_focus_out_event
        self.layout.addRow("Request", self.request_edit)
        self._validate_and_pretty_request()

    def _set_default_style(self, key, widget):
        if self.client.is_default(key):
            widget.setStyleSheet("color: gray;")
        else:
            widget.setStyleSheet("")

    def _on_edit(self, key, value, widget):
        if isinstance(widget, QLineEdit) and value.strip() == "":
            value = self.client.defaults.get(key, "")
            widget.setText(str(value))
        if key == 'period_sec':
            try:
                value = float(value)
            except Exception:
                pass
        self.client.set_value(key, value)
        self._set_default_style(key, widget)

    def _on_methode_changed(self):
        # Exklusive Auswahl: Nur eine Checkbox darf aktiv sein
        sender = self.sender()
        if sender.isChecked():
            for cb in self.methode_checks:
                if cb is not sender:
                    cb.setChecked(False)
            self.client.set_value('methode', sender.text())
        else:
            # Mindestens eine Checkbox muss aktiv bleiben
            if not any(cb.isChecked() for cb in self.methode_checks):
                sender.setChecked(True)

    def _validate_and_pretty_request(self):
        text = self.request_edit.toPlainText()
        try:
            parsed = json.loads(text)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            self.request_edit.setPlainText(pretty)
            self.request_edit.setStyleSheet("")
        except Exception:
            self.request_edit.setStyleSheet("background-color: #ffcccc;")

    def _request_focus_out_event(self, event):
        text = self.request_edit.toPlainText()
        if text.strip() == "":
            default = self.client.defaults.get('request', "")
            self.request_edit.setPlainText(default)
        self._validate_and_pretty_request()
        super(QTextEdit, self.request_edit).focusOutEvent(event)
