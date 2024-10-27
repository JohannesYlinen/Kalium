import os
import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtWidgets import QDialog, QMessageBox

from utils.json_editor import JSONEditor

class EditorWindow(QDialog):
    fileSaved = Signal()
    def __init__(self, parent=None, file_path: str=None):
        super().__init__(parent)
        self.file_path = file_path
        self.saved = True
        self.setWindowTitle("File editor")
        self.setGeometry(400, 50, 450, 600)
        self.setMinimumSize(300, 300)
        # self.setWindowFlags(Qt.Window)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint)
        self._init_ui()
        self.editor.textChanged.connect(self._editor_text_changed)
        self.setFocus()

    def _editor_text_changed(self):
        self.saved = False

    def load_json(self, file_path):
        self.file_path = file_path
        self.editor.load_json(file_path)
        self.label.setText("Currently editing: <b>" + os.path.basename(file_path) + "</b>")

    def _init_ui(self):
        self.setProperty("class", "window")

        self.label = QLabel("Currently editing:")
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.editor = JSONEditor()
        self.editor.setStyleSheet(self.editor.styleSheet() + "padding: 0 0;")


        if self.file_path:
            self.load_json(self.file_path)

        save_btn = QPushButton("Save")
        save_btn.setFocusPolicy(Qt.TabFocus)
        save_btn.setAutoDefault(True)
        save_btn.clicked.connect(self._save)

        close_btn = QPushButton("Close")
        close_btn.setFocusPolicy(Qt.TabFocus)
        close_btn.setAutoDefault(True)
        close_btn.clicked.connect(self._close_pressed)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(close_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.editor)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _new_message_box(self, title: str, text: str, buttons_flag: int, default_flag: int):
        q = QMessageBox(self)
        q.setWindowTitle(title)
        q.setText(text)
        q.setStandardButtons(buttons_flag)
        q.setDefaultButton(default_flag)
        q.setIcon(QMessageBox.NoIcon)
        return q.exec()

    def _new_error_box(self, error_msg):
        return self._new_message_box("Error", error_msg, QMessageBox.Ok, QMessageBox.Ok)

    def _is_valid_json(self, string) -> tuple[bool, str]:
        try:
            json.loads(string)
            return (True, "")
        except json.JSONDecodeError as e:
            error_msg = f"JSONDecodeError: {e.msg}: line {e.lineno} column {e.colno} (char {e.pos})"
            return (False, error_msg)


    def _save(self) -> bool:
        valid, errors = self._is_valid_json(self.editor.toPlainText())
        if valid:
            self.editor.save_json()
            self.saved = True
            self.fileSaved.emit()
            return True
        else:
            self._new_error_box(errors)
            return False
    
    def _close_pressed(self):
        if self.saved:
            self.accept()
            return
        
        reply = self._new_message_box(
            "Close editor", "Finish editing file?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        if reply == QMessageBox.Save and self._save():
            self.accept()
        elif reply == QMessageBox.Discard:
            self.accept()
        else:
            return

    def closeEvent(self, event):
        self._close_pressed()
        event.ignore() # if canceled 

    def reject(self):
        return