# views/home_view.py
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QTextEdit, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QTimer
from controllers import patient_controller as pc
from utils.normalize import normalize_name

class HomeView(QWidget):
    def __init__(self, controller, base=None):
        super().__init__()
        self.ctrl = controller
        self.base = base

        root = QVBoxLayout()
        top = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or ID...")
        self.search_input.setFixedHeight(36)
        self.btn_new = QPushButton("New Patient")
        self.btn_new.setFixedHeight(36)
        top.addWidget(self.search_input)
        top.addWidget(self.btn_new)
        root.addLayout(top)

        # message area or list area
        self.msg_label = QLabel("")            # used for database-not-found or no-patients messages
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        root.addWidget(self.msg_label)

        # list of patients
        self.list = QListWidget()
        self.list.setUniformItemSizes(True)
        root.addWidget(self.list, stretch=1)

        # details area
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setFixedHeight(160)
        root.addWidget(self.details)

        self.setLayout(root)

        # debounce timer
        self._deb = QTimer(singleShot=True)
        self._deb.setInterval(180)
        self._deb.timeout.connect(self._do_search)
        self.search_input.textChanged.connect(self._on_text_changed)

        # wire new button
        self.btn_new.clicked.connect(self.ctrl.show_new)

        # initial load
        self._load_initial()

        self.list.itemActivated.connect(self._on_item_activated)

    def _load_initial(self):
        # DB not found -> show message; still allow New Patient to create DB later
        try:
            patients = pc.get_all_patients()
        except RuntimeError as e:
            if str(e) == "database-not-found":
                self.msg_label.setText("-database-not-found-  (click New Patient to create DB)")
                self.list.clear()
                return
            raise
        if not patients:
            self.msg_label.setText("-no-patients-in-the-database-")
            self.list.clear()
            return
        self.msg_label.setText("")
        self._populate_list(patients)

    def _on_text_changed(self, txt):
        self._pending = txt
        self._deb.start()

    def _do_search(self):
        q = (self._pending or "").strip()
        if q == "":
            # reset to full list
            try:
                patients = pc.get_all_patients()
            except RuntimeError:
                self.msg_label.setText("-database-not-found-")
                self.list.clear()
                return
            if not patients:
                self.msg_label.setText("-no-patients-in-the-database-")
                self.list.clear()
                return
            self.msg_label.setText("")
            self._populate_list(patients)
            return

        # numeric -> ID prefix
        if q.isdigit():
            try:
                allp = pc.get_all_patients()
            except RuntimeError:
                self.msg_label.setText("-database-not-found-")
                self.list.clear()
                return
            results = [p for p in allp if str(p.id).startswith(q)]
        else:
            # use DB prefix search for production
            try:
                results = pc.search_by_prefix(q)
            except RuntimeError:
                self.msg_label.setText("-database-not-found-")
                self.list.clear()
                return

        if not results:
            self.list.clear()
            self.msg_label.setText("-no-patients-in-the-database-" if not pc.db_exists() else "No matches")
            return
        self.msg_label.setText("")
        self._populate_list(results)

    def _populate_list(self, patients):
        self.list.clear()
        for p in patients:
            item = QListWidgetItem(f"{p.id} — {p.name} (age:{p.age or '-'})")
            item.setData(Qt.UserRole, p.id)
            self.list.addItem(item)

    def _on_item_activated(self, item):
        pid = item.data(Qt.UserRole)
        if not pid:
            return
        try:
            p = pc.get_patient_by_id(int(pid))
        except RuntimeError:
            self.msg_label.setText("-database-not-found-")
            return
        if not p:
            self.details.setPlainText("Patient not found.")
            return
        text = (
            f"ID: {p.id}\n"
            f"Reference No: {getattr(p, 'reference_no', None) or '-'}\n"
            f"Name: {p.name}\n"
            f"Age: {p.age or '-'}\n"
            f"Sex: {p.sex or '-'}\n"
            f"Contact: {p.contact_number or '-'}\n"
            f"WhatsApp: {getattr(p, 'whatsapp_number', None) or '-'}\n"
            f"Email: {getattr(p, 'email', None) or '-'}\n"
            f"Children: {getattr(p, 'num_children', None) or 0} "
            f"(M:{getattr(p, 'num_male_children', None) or 0}, F:{getattr(p, 'num_female_children', None) or 0})\n"
            f"Children Ages: {getattr(p, 'children_ages', None) or '-'}\n"
        )
        self.details.setPlainText(text)
