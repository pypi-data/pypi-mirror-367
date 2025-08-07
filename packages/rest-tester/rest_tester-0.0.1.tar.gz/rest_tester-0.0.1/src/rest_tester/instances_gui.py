import importlib
import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QSplitter, QTabWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt, QEvent
from .gui_model import ConfigModel, ServerInstance, ClientInstance, ServerInstanceWidget, ClientInstanceWidget

class InstanceTabWidget(QWidget):
    def __init__(self, config, is_server=True, manager=None):
        super().__init__()
        self.config = config
        self.is_server = is_server
        self.manager = manager
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._on_close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.tabBar().installEventFilter(self)
        self.tabs.tabBarDoubleClicked = getattr(self.tabs, 'tabBarDoubleClicked', None)
        if hasattr(self.tabs, 'tabBarDoubleClicked'):
            self.tabs.tabBarDoubleClicked.connect(self._on_tab_rename)

        # Buttons
        self.add_btn = QPushButton("New")
        self.reset_btn = QPushButton("Reset")
        self.update_btn = QPushButton("Start/Update")
        self.stop_btn = QPushButton("Stop")
        self.del_btn = QPushButton("Remove")
        self.add_btn.clicked.connect(self._add_instance)
        self.reset_btn.clicked.connect(self._reset_instance)
        if self.is_server:
            self.update_btn.clicked.connect(self._update_endpoint)
            self.stop_btn.clicked.connect(self._stop_endpoint)
        else:
            self.update_btn.clicked.connect(self._start_client_request)
            self.stop_btn.clicked.connect(self._stop_client_request)
        self.del_btn.clicked.connect(self._delete_instance)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.del_btn)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self._init_tabs()
        self._update_delete_button()
        # Autostart: Endpunkte/Clients beim Start registrieren
        if self.is_server and self.manager:
            for inst in self.config.servers:
                if inst.get_value('autostart'):
                    self._register_endpoint(inst)
        elif not self.is_server and self.manager:
            for inst in getattr(self.config, 'clients', []):
                if inst.get_value('autostart'):
                    self._start_client(inst)
    def eventFilter(self, obj, event):
        if obj == self.tabs.tabBar() and event.type() == QEvent.MouseButtonDblClick:
            # Verwende die neue API: event.position().toPoint() statt event.pos()
            index = self.tabs.tabBar().tabAt(event.position().toPoint())
            if index >= 0:
                self._on_tab_rename(index)
            return True
        return super().eventFilter(obj, event)

    def _on_tab_rename(self, index):
        tab_bar = self.tabs.tabBar()
        old_name = self.tabs.tabText(index)
        editor = QLineEdit(old_name, tab_bar)
        editor.setGeometry(tab_bar.tabRect(index))
        editor.setFocus()
        editor.selectAll()
        editor.editingFinished.connect(lambda: self._finish_tab_rename(index, editor))
        editor.show()

    def _finish_tab_rename(self, index, editor):
        new_name = editor.text().strip()
        if not new_name:
            editor.deleteLater()
            return
        # Eindeutigkeit prüfen
        all_names = [self.tabs.tabText(i) for i in range(self.tabs.count())]
        if new_name in all_names and new_name != self.tabs.tabText(index):
            QMessageBox.warning(self, "Name existiert", "Der Name muss eindeutig sein!")
            editor.deleteLater()
            return
        
        # Alten Namen für Thread-Referenz merken
        old_name = self.tabs.tabText(index)
        
        self.tabs.setTabText(index, new_name)
        # Instanzname im Model aktualisieren
        if self.is_server:
            server_inst = self.config.servers[index]
            old_server_name = server_inst.name
            server_inst.name = new_name
            
            # Bei Server-Threads: Prüfe ob ein Endpoint mit diesem Namen läuft
            if self.manager and hasattr(self.manager, 'rename_endpoint_reference'):
                # Hole die aktuellen Server-Parameter
                host, port, route, _, _, _, _ = self._get_endpoint_params(server_inst)
                # Da sich nur der Name ändert, nicht die Endpoint-Parameter,
                # müssen wir den Endpoint nicht umbenennen - der Name ist nur für die GUI
                # Der Server läuft weiter mit den gleichen Host/Port/Route Parametern
                pass
        else:
            self.config.clients[index].name = new_name
            # Bei Client-Threads: Referenz im Manager aktualisieren
            if self.manager and old_name in self.manager.clients:
                # Hole den laufenden Thread mit dem alten Namen
                thread = self.manager.clients[old_name]
                # Aktualisiere den Namen im Thread selbst
                thread.name = new_name
                # Verschiebe die Referenz im Manager Dictionary
                self.manager.clients[new_name] = thread
                del self.manager.clients[old_name]
        
        editor.deleteLater()
        # Config speichern, damit Änderung persistent ist
        if hasattr(self.config, 'save'):
            self.config.save()

    def _get_client_params(self, inst):
        host_port = inst.get_value('host')
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            host = host.strip()
            port = int(port)
            host = f"{host}:{port}"
        else:
            host = host_port
        route = inst.get_value('route')
        method = inst.get_value('methode')
        request_data = inst.get_value('request')
        period_sec = float(inst.get_value('period_sec') or 1.0)
        loop = bool(inst.get_value('loop'))
        initial_delay_sec = float(inst.get_value('initial_delay_sec') or 0.0)
        return inst.name, host, route, method, request_data, period_sec, loop, initial_delay_sec

    def _start_client(self, inst):
        if not self.manager:
            return
        name, host, route, method, request_data, period_sec, loop, initial_delay_sec = self._get_client_params(inst)
        self.manager.start_client(name, host, route, method, request_data, period_sec, loop, initial_delay_sec=initial_delay_sec)

    def _start_client_request(self):
        idx = self.tabs.currentIndex()
        if idx < 0 or self.is_server or not self.manager:
            return
        inst = getattr(self.config, 'clients', [])[idx]
        self._start_client(inst)

    def _stop_client_request(self):
        idx = self.tabs.currentIndex()
        if idx < 0 or self.is_server or not self.manager:
            return
        inst = getattr(self.config, 'clients', [])[idx]
        self.manager.stop_client(inst.name)

    def _stop_endpoint(self):
        idx = self.tabs.currentIndex()
        if idx < 0 or not self.is_server or not self.manager:
            return
        inst = self.config.servers[idx]
        self._remove_endpoint(inst)

    def _get_endpoint_params(self, inst):
        # Host: host:port
        host_port = inst.get_value('host')
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host = host_port
            port = 5000
        route = inst.get_value('route')
        methods = inst.get_value('methodes')
        response = inst.get_value('response')
        response_delay_sec = float(inst.get_value('response_delay_sec') or 0.0)
        initial_delay_sec = float(inst.get_value('initial_delay_sec') or 0.0)
        return host, port, route, methods, response, response_delay_sec, initial_delay_sec

    def _register_endpoint(self, inst):
        from .service.endpoint_utils import make_generic_handler
        host, port, route, methods, response, response_delay_sec, initial_delay_sec = self._get_endpoint_params(inst)
        try:
            import json
            response_json = json.loads(response) if response else {}
        except Exception:
            response_json = {"error": "invalid response json"}
        handler = make_generic_handler(response_json, response_delay_sec)

        # put call with potential initial delay in background thread
        thread = threading.Thread(target=self.manager.add_endpoint, args=(host, port, route, methods, initial_delay_sec, handler))
        thread.start()

    def _remove_endpoint(self, inst):
        host, port, route, _, _, _, _ = self._get_endpoint_params(inst)
        self.manager.remove_endpoint(host, port, route)

    def _update_endpoint(self):
        idx = self.tabs.currentIndex()
        if idx < 0 or not self.is_server or not self.manager:
            return
        inst = self.config.servers[idx]
        self._register_endpoint(inst)

    def _init_tabs(self):
        self.tabs.clear()
        # Korrigiere Zugriff auf Clients
        instances = self.config.servers if self.is_server else getattr(self.config, 'clients', [])
        for inst in instances:
            widget = ServerInstanceWidget(inst) if self.is_server else ClientInstanceWidget(inst)
            self.tabs.addTab(widget, inst.name)

    def _add_instance(self):
        base = "Server" if self.is_server else "Client"
        if self.is_server:
            existing = [inst.name for inst in self.config.servers]
            defaults = self.config.defaults
        else:
            existing = [inst.name for inst in getattr(self.config, 'clients', [])]
            defaults = self.config.raw['defaults']['client']
            server_methods = self.config.raw['defaults']['server']['methodes']
        idx = 1
        while f"{base}{idx}" in existing:
            idx += 1
        name = f"{base}{idx}"
        if self.is_server:
            inst = ServerInstance(name, defaults)
            self.config.servers.append(inst)
            widget = ServerInstanceWidget(inst)
        else:
            inst = ClientInstance(name, defaults, server_methods)
            self.config.clients.append(inst)
            widget = ClientInstanceWidget(inst)
        self.tabs.addTab(widget, name)
        self.tabs.setCurrentIndex(self.tabs.count()-1)
        self._update_delete_button()

    def _reset_instance(self):
        idx = self.tabs.currentIndex()
        if idx < 0:
            return
        widget = self.tabs.widget(idx)
        # Unterscheide zwischen Server und Client
        if self.is_server:
            for key in widget.server.defaults:
                widget.server.set_value(key, widget.server.defaults[key])
            widget.host_edit.setText(widget.server.get_value('host'))
            widget.autostart_box.setChecked(widget.server.get_value('autostart'))
            widget.delay_edit.setText(str(widget.server.get_value('response_delay_sec')))
            widget.route_edit.setText(widget.server.get_value('route'))
            default_methods = widget.server.defaults.get('methodes', [])
            for i, cb in enumerate(widget.methods_checks):
                cb.setChecked(cb.text() in default_methods)
            widget.response_edit.setPlainText(widget.server.get_value('response') if widget.server.get_value('response') else "")
        else:
            for key in widget.client.defaults:
                widget.client.set_value(key, widget.client.defaults[key])
            widget.host_edit.setText(widget.client.get_value('host'))
            widget.autostart_box.setChecked(widget.client.get_value('autostart'))
            widget.loop_box.setChecked(widget.client.get_value('loop'))
            widget.period_edit.setText(str(widget.client.get_value('period_sec')))
            widget.route_edit.setText(widget.client.get_value('route'))
            for i, cb in enumerate(widget.methode_checks):
                cb.setChecked(cb.text() == widget.client.get_value('methode'))
            widget.request_edit.setPlainText(widget.client.get_value('request') if widget.client.get_value('request') else "")

    def _delete_instance(self):
        if self.tabs.count() <= 1:
            return  # Keine Warnung mehr, Button ist dann sowieso disabled
        idx = self.tabs.currentIndex()
        if idx < 0:
            return
        if self.is_server and self.manager:
            inst = self.config.servers[idx]
            self._remove_endpoint(inst)
        elif not self.is_server and self.manager:
            inst = getattr(self.config, 'clients', [])[idx]
            # Stoppe ggf. laufenden Client-Thread vor dem Löschen
            self.manager.stop_client(inst.name)
        # Zugriff auf Clients robust machen
        if self.is_server:
            instances = self.config.servers
        else:
            instances = getattr(self.config, 'clients', [])
        del instances[idx]
        self.tabs.removeTab(idx)
        self._update_delete_button()

    def _on_close_tab(self, idx):
        self.tabs.setCurrentIndex(idx)
        self._delete_instance()

    def _on_tab_changed(self, idx):
        self._update_delete_button()

    def _update_delete_button(self):
        self.del_btn.setEnabled(self.tabs.count() > 1)

class MainWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        from .service.rest_server_manager import RestServerManager
        from .service.rest_client_manager import RestClientManager
        self.manager = RestServerManager() #TODO: renaming to avoid confusion
        self.client_manager = RestClientManager()
        self.setWindowTitle("Rest Client / Server Tester")
        splitter = QSplitter(Qt.Horizontal)
        self.server_tabs = InstanceTabWidget(config, is_server=True, manager=self.manager)
        self.client_tabs = InstanceTabWidget(config, is_server=False, manager=self.client_manager)
        splitter.addWidget(self.server_tabs)
        splitter.addWidget(self.client_tabs)
        layout = QVBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def closeEvent(self, event):
        self.config.save()
        if hasattr(self, 'manager') and self.manager:
            self.manager.shutdown_all()
        if hasattr(self, 'client_manager') and self.client_manager:
            self.client_manager.stop_all()
        event.accept()
