# views/new_patient_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QSpinBox,
    QComboBox, QPushButton, QHBoxLayout, QMessageBox, QDateEdit,
    QGroupBox, QGridLayout, QApplication, QScrollArea
)
from PySide6.QtCore import Qt, QObject, QEvent, QTimer
from datetime import date as pydate
from controllers import patient_controller as pc
from database import models as dbmodels

class NewPatientView(QWidget):
    class _AppWheelFilter(QObject):
        """Application-level filter: swallow wheel events for spinboxes that are not focused."""
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.Wheel:
                try:
                    from PySide6.QtWidgets import QSpinBox
                    if isinstance(obj, QSpinBox):
                        if not obj.hasFocus():
                            return True
                except Exception:
                    pass
            return super().eventFilter(obj, event)

    def __init__(self, controller):
        super().__init__()
        self.ctrl = controller

        QApplication.instance().installEventFilter(NewPatientView._AppWheelFilter(self))

        # ===== MAIN LAYOUT =====
        root = QVBoxLayout()
        self.setLayout(root)

        header = QLabel("New Patient")
        header.setStyleSheet("font-size:18px; font-weight:600; padding:6px 0;")
        root.addWidget(header)

        # ===== SCROLL AREA =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(scroll, 1)

        # Create inner widget that holds the form
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        form_layout = QVBoxLayout(scroll_widget)

        # ===== PATIENT FORM =====
        form = QFormLayout()
        form_layout.addLayout(form)

        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDate(pydate.today())
        self.input_date.setDisplayFormat("yyyy-MM-dd")
        self.input_name = QLineEdit()
        self.input_referred = QLineEdit()

        self.input_age = QSpinBox()
        self.input_age.setRange(0,150)
        self.input_age.setValue(30)
        self._fix_spinbox_focus_behavior(self.input_age)

        self.input_sex = QComboBox(); self.input_sex.addItems(["", "Male", "Female", "Other"])
        self.input_sex_other = QLineEdit(); self.input_sex_other.setVisible(False)
        self.input_sex.currentTextChanged.connect(lambda t: self.input_sex_other.setVisible(t=="Other"))
        self.input_diet = QComboBox(); self.input_diet.addItems(["", "Veg", "Non Veg", "Egg"])
        self.input_marital = QComboBox(); self.input_marital.addItems(["", "Single", "Married", "Divorced", "Widow/Widower"])
        self.input_religion = QComboBox(); self.input_religion.addItems(["", "Hindu", "Muslim", "Sikh", "Christian", "Buddhism", "Jainism", "Other"])
        self.input_religion_other = QLineEdit(); self.input_religion_other.setVisible(False)
        self.input_religion.currentTextChanged.connect(lambda t: self.input_religion_other.setVisible(t=="Other"))
        self.input_occupation = QLineEdit()
        self.input_address = QLineEdit()
        self.input_contact = QLineEdit()

        # contact fields
        self.input_whatsapp = QLineEdit()
        self.input_email = QLineEdit()
        self.input_reference = QLineEdit()

        # children fields
        self.input_num_children = QSpinBox(); self.input_num_children.setRange(0, 20); self.input_num_children.setValue(0)
        self._fix_spinbox_focus_behavior(self.input_num_children)
        self.input_num_male = QSpinBox(); self.input_num_male.setRange(0, 20); self.input_num_male.setValue(0)
        self._fix_spinbox_focus_behavior(self.input_num_male)
        self.input_num_female = QSpinBox(); self.input_num_female.setRange(0, 20); self.input_num_female.setValue(0)
        self._fix_spinbox_focus_behavior(self.input_num_female)

        self._children_age_widgets = []
        self._children_age_container = QGroupBox("Children Details")
        self._children_age_container_layout = QGridLayout()
        self._children_age_container.setLayout(self._children_age_container_layout)
        self._children_age_container.setVisible(False)

        self.input_num_children.valueChanged.connect(self._on_total_children_changed)
        self.input_num_male.valueChanged.connect(self._on_male_changed)
        self.input_num_female.valueChanged.connect(self._on_female_changed)

        # FORM FIELDS
        form.addRow("Date", self.input_date)
        form.addRow("Name*", self.input_name)
        form.addRow("Referred By", self.input_referred)
        form.addRow("Age", self.input_age)
        form.addRow("Sex", self.input_sex)
        form.addRow("", self.input_sex_other)
        form.addRow("Diet", self.input_diet)
        form.addRow("Marital Status", self.input_marital)
        form.addRow("Religion", self.input_religion)
        form.addRow("", self.input_religion_other)
        form.addRow("Occupation", self.input_occupation)
        form.addRow("Address", self.input_address)
        form.addRow("Contact Number", self.input_contact)
        form.addRow("WhatsApp Number", self.input_whatsapp)
        form.addRow("Email", self.input_email)
        form.addRow("Reference No.", self.input_reference)
        form.addRow("Total Children", self.input_num_children)
        self._male_row_label = QLabel("Male Children")
        self._female_row_label = QLabel("Female Children")
        form.addRow(self._male_row_label, self.input_num_male)
        form.addRow(self._female_row_label, self.input_num_female)
        self._male_row_label.setVisible(False)
        self.input_num_male.setVisible(False)
        self._female_row_label.setVisible(False)
        self.input_num_female.setVisible(False)

        form_layout.addWidget(self._children_age_container)

        # ===== BUTTONS =====
        hb = QHBoxLayout()
        self.btn_back = QPushButton("Back")
        self.btn_save = QPushButton("Save Patient")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_back.clicked.connect(self.ctrl.show_home)
        hb.addWidget(self.btn_back)
        hb.addWidget(self.btn_save)
        root.addLayout(hb)

    # -------------------------
    # Focus fix helper
    # -------------------------
    def _fix_spinbox_focus_behavior(self, spinbox):
        spinbox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        try:
            le = spinbox.lineEdit()
            if le:
                le.deselect()
        except Exception:
            pass
        def _on_val_changed(_):
            QTimer.singleShot(0, spinbox.clearFocus)
            try:
                le2 = spinbox.lineEdit()
                if le2:
                    le2.deselect()
            except Exception:
                pass
        spinbox.valueChanged.connect(_on_val_changed)


    # -------------------------
    # Dynamic UI handlers
    # -------------------------
    def _on_total_children_changed(self, total: int):
        """Show/hide male/female controls and adjust ranges according to total."""
        total = int(total)
        if total <= 0:
            self._male_row_label.setVisible(False)
            self.input_num_male.setVisible(False)
            self._female_row_label.setVisible(False)
            self.input_num_female.setVisible(False)
            # hide age container and clear ages
            self._children_age_container.setVisible(False)
            self._clear_age_widgets()
            # reset male/female to zero for clarity
            self.input_num_male.blockSignals(True)
            self.input_num_female.blockSignals(True)
            self.input_num_male.setValue(0)
            self.input_num_female.setValue(0)
            self.input_num_male.blockSignals(False)
            self.input_num_female.blockSignals(False)
            return

        # show male/female controls
        self._male_row_label.setVisible(True)
        self.input_num_male.setVisible(True)
        self._female_row_label.setVisible(True)
        self.input_num_female.setVisible(True)

        # set maximums so male + female cannot individually exceed total
        self.input_num_male.setMaximum(total)
        self.input_num_female.setMaximum(total)

        # also adjust the complementary maximums based on current values
        m = self.input_num_male.value()
        f = self.input_num_female.value()
        # ensure neither is greater than total
        if m > total:
            self.input_num_male.setValue(total)
            m = total
        if f > total:
            self.input_num_female.setValue(total)
            f = total

        # rebuild age fields according to current male/female values
        self._rebuild_age_widgets(m, f)

    def _on_male_changed(self, m: int):
        """When male count changes, adjust female max and rebuild ages."""
        total = self.input_num_children.value()
        m = int(m)
        # female max cannot exceed total - m
        self.input_num_female.setMaximum(max(0, total - m))
        # ensure current female value is within max
        if self.input_num_female.value() > self.input_num_female.maximum():
            self.input_num_female.setValue(self.input_num_female.maximum())
        # rebuild ages
        f = self.input_num_female.value()
        self._rebuild_age_widgets(m, f)
    
    def _on_female_changed(self, f: int):
        """When female count changes, adjust male max and rebuild ages."""
        total = self.input_num_children.value()
        f = int(f)
        self.input_num_male.setMaximum(max(0, total - f))
        if self.input_num_male.value() > self.input_num_male.maximum():
            self.input_num_male.setValue(self.input_num_male.maximum())
        m = self.input_num_male.value()
        self._rebuild_age_widgets(m, f)

    def _clear_age_widgets(self):
        """Remove all age widgets from the container and reset tracking list."""
        while self._children_age_container_layout.count():
            item = self._children_age_container_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        self._children_age_widgets = []

    def _rebuild_age_widgets(self, male_count: int, female_count: int):
        """Create age spinboxes for each child (male first, then female)."""
        total_present = male_count + female_count
        if total_present == 0:
            self._children_age_container.setVisible(False)
            self._clear_age_widgets()
            return

        # show container
        self._children_age_container.setVisible(True)
        # clear existing widgets
        self._clear_age_widgets()

        row = 0
        col = 0
        # create male age fields
        for i in range(male_count):
            lbl = QLabel(f"Male {i+1} age")
            sp = QSpinBox(); sp.setRange(0, 120); sp.setValue(0)
            self._fix_spinbox_focus_behavior(sp)
            self._children_age_container_layout.addWidget(lbl, row, col); col += 1
            self._children_age_container_layout.addWidget(sp, row, col); col = 0; row += 1
            self._children_age_widgets.append(sp)
        # create female age fields
        for i in range(female_count):
            lbl = QLabel(f"Female {i+1} age")
            sp = QSpinBox(); sp.setRange(0, 120); sp.setValue(0)
            self._fix_spinbox_focus_behavior(sp)
            self._children_age_container_layout.addWidget(lbl, row, col); col += 1
            self._children_age_container_layout.addWidget(sp, row, col); col = 0; row += 1
            self._children_age_widgets.append(sp)

    # -------------------------
    # Save / validation
    # -------------------------
    def _on_save(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required")
            return
        qdate = self.input_date.date().toString("yyyy-MM-dd")
        try:
            visit_date = pydate.fromisoformat(qdate)
        except:
            visit_date = pydate.today()
        sex_choice = self.input_sex.currentText()
        sex = self.input_sex_other.text().strip() if sex_choice == "Other" else (sex_choice or None)
        religion_choice = self.input_religion.currentText()
        religion = self.input_religion_other.text().strip() if religion_choice == "Other" else (religion_choice or None)

        # children counts
        total_children = self.input_num_children.value()
        male_children = self.input_num_male.value()
        female_children = self.input_num_female.value()

        # validation: male + female must equal total
        if total_children != (male_children + female_children):
            QMessageBox.warning(
                self,
                "Validation",
                f"Total Children ({total_children}) must equal Male ({male_children}) + Female ({female_children})."
            )
            return

        # collect ages from dynamic widgets (order: males then females as built)
        children_ages_list = []
        for sp in self._children_age_widgets:
            children_ages_list.append(str(sp.value()))
        children_ages_str = ", ".join(children_ages_list) if children_ages_list else None

        # If DB missing, create DB (production decision: automatically create on first save)
        from database.database import db_exists, create_db
        if not db_exists():
            create_db(dbmodels.Base)

        try:
            patient = pc.add_patient(
                name=name,
                visit_date=visit_date,
                reference_no=self.input_reference.text().strip() or None,
                referred_by=self.input_referred.text().strip() or None,
                age=self.input_age.value() or None,
                sex=sex,
                diet=self.input_diet.currentText() or None,
                marital_status=self.input_marital.currentText() or None,
                religion=religion,
                occupation=self.input_occupation.text().strip() or None,
                address=self.input_address.text().strip() or None,
                contact_number=self.input_contact.text().strip() or None,
                whatsapp_number=self.input_whatsapp.text().strip() or None,
                email=self.input_email.text().strip() or None,
                num_children=total_children if total_children > 0 else None,
                num_male_children=male_children if male_children > 0 else None,
                num_female_children=female_children if female_children > 0 else None,
                children_ages=children_ages_str,
            )
            QMessageBox.information(self, "Saved", f"Patient saved (id: {patient.id})")
            # after save -> go to home which will show the list and prefill search
            self.ctrl.show_home(prefill=patient.name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save patient:\n{e}")
