from pathlib import Path
import shutil
import json

from PySide6.QtCore import QTimer
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QCheckBox,
    QScrollArea,
)

from widgets.section_header import SectionHeader

NOTES_BASE_DIR = None


class NotesTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DropOnly)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            target_folder = NOTES_BASE_DIR
            item = self.itemAt(event.position().toPoint())
            if item:
                path = Path(item.data(0, 256))
                if path.is_dir():
                    target_folder = path
                else:
                    target_folder = path.parent

            for url in event.mimeData().urls():
                src_path = Path(url.toLocalFile())
                if src_path.is_file() and src_path.suffix == ".json":
                    dest_path = target_folder / src_path.name
                    shutil.copy(src_path, dest_path)

            refresh_tree(self)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


def build(current_session: str) -> QWidget:
    global NOTES_BASE_DIR
    NOTES_BASE_DIR = Path("data/notes") / current_session
    NOTES_BASE_DIR.mkdir(parents=True, exist_ok=True)

    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(4, 4, 4, 4)

    left = QVBoxLayout()
    left.addWidget(SectionHeader("Notatki"))
    search = QLineEdit()
    search.setPlaceholderText("Szukaj notatek...")
    left.addWidget(search)

    tree = NotesTree()
    refresh_tree(tree)
    left.addWidget(tree)

    right = QVBoxLayout()
    right.addWidget(SectionHeader("Edytor notatki"))

    editor = QTextEdit()
    editor.setPlaceholderText("Wybierz notatkę z lewej, aby zobaczyć zawartość...")
    editor.setReadOnly(True)
    right.addWidget(editor)

    checkbox_area = QScrollArea()
    checkbox_area.setWidgetResizable(True)
    checkbox_container = QWidget()
    checkbox_layout = QVBoxLayout(checkbox_container)
    checkbox_area.setWidget(checkbox_container)
    right.addWidget(checkbox_area)

    btn_add_checkbox = QPushButton("Dodaj checkbox")
    btn_add_checkbox.setEnabled(False)
    right.addWidget(btn_add_checkbox)

    editor.current_file = None
    editor.checkbox_layout = checkbox_layout
    editor.save_timer = QTimer()
    editor.save_timer.setSingleShot(True)
    editor.save_timer.timeout.connect(lambda: save_current_note(editor))

    btns = QHBoxLayout()
    btn_new_note = QPushButton("Nowa notatka (.json)")
    btn_new_folder = QPushButton("Nowy folder")
    btn_delete = QPushButton("Usuń")
    btn_export = QPushButton("Eksportuj")
    btn_import = QPushButton("Importuj")

    btns.addWidget(btn_new_note)
    btns.addWidget(btn_new_folder)
    btns.addWidget(btn_delete)
    btns.addWidget(btn_export)
    btns.addWidget(btn_import)
    left.addLayout(btns)

    tree.itemClicked.connect(lambda item: open_note_in_editor(item, editor, checkbox_layout, btn_add_checkbox))
    btn_new_note.clicked.connect(lambda: create_new_note(tree))
    btn_new_folder.clicked.connect(lambda: create_new_folder(tree))
    btn_delete.clicked.connect(lambda: delete_item(tree, editor))
    btn_export.clicked.connect(lambda: export_note(editor))
    btn_import.clicked.connect(lambda: import_note(tree))
    btn_add_checkbox.clicked.connect(lambda: add_checkbox(editor, checkbox_layout))

    search.textChanged.connect(lambda text: filter_notes(tree, text))
    editor.textChanged.connect(lambda: schedule_auto_save(editor))

    h.addLayout(left, 1)
    h.addLayout(right, 2)
    return w


def add_folder_items(parent_item: QTreeWidgetItem, folder_path: Path):
    for item in sorted(folder_path.iterdir()):
        display_name = item.stem if item.is_file() and item.suffix == ".json" else item.name
        child_item = QTreeWidgetItem([display_name])
        child_item.setData(0, 256, str(item))
        parent_item.addChild(child_item)
        if item.is_dir():
            add_folder_items(child_item, item)


def refresh_tree(tree: QTreeWidget):
    tree.clear()
    for item in sorted(NOTES_BASE_DIR.iterdir()):
        display_name = item.stem if item.is_file() and item.suffix == ".json" else item.name
        top_item = QTreeWidgetItem([display_name])
        top_item.setData(0, 256, str(item))
        tree.addTopLevelItem(top_item)
        if item.is_dir():
            add_folder_items(top_item, item)


def open_note_in_editor(item: QTreeWidgetItem, editor: QTextEdit, checkbox_layout, add_checkbox_button):
    path = Path(item.data(0, 256))

    if path.is_dir():
        editor.setPlainText("")
        editor.setPlaceholderText("Wybierz notatkę z lewej, aby zobaczyć zawartość...")
        editor.setReadOnly(True)
        editor.current_file = None
        clear_checkboxes(checkbox_layout)
        add_checkbox_button.setEnabled(False)
        return

    try:
        data = json.loads(path.read_text("utf-8"))
    except Exception as e:
        editor.setText(f"Błąd JSON:\n{e}")
        editor.setReadOnly(True)
        return

    editor.blockSignals(True)
    editor.setPlaceholderText("")
    editor.setPlainText(data.get("text", ""))
    editor.setReadOnly(False)
    editor.blockSignals(False)
    editor.current_file = path

    clear_checkboxes(checkbox_layout)
    for entry in data.get("checkboxes", []):
        cb = QCheckBox(entry.get("text", ""))
        cb.setChecked(entry.get("checked", False))
        cb.stateChanged.connect(lambda _, e=editor: save_current_note(e))
        checkbox_layout.addWidget(cb)

    add_checkbox_button.setEnabled(True)


def clear_checkboxes(layout):
    while layout.count() > 0:
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()


def add_checkbox(editor, checkbox_layout):
    text, ok = QInputDialog.getText(None, "Checkbox", "Opis:")
    if ok and text.strip():
        cb = QCheckBox(text.strip())
        cb.stateChanged.connect(lambda _, e=editor: save_current_note(e))
        checkbox_layout.addWidget(cb)
        save_current_note(editor)


def schedule_auto_save(editor: QTextEdit):
    if editor.current_file is None:
        return
    editor.save_timer.start(500)


def collect_checkbox_data(layout):
    result = []
    for i in range(layout.count()):
        widget = layout.itemAt(i).widget()
        if isinstance(widget, QCheckBox):
            result.append({
                "text": widget.text(),
                "checked": widget.isChecked()
            })
    return result


def save_current_note(editor: QTextEdit):
    if not editor.current_file:
        return
    try:
        data = {
            "text": editor.toPlainText(),
            "checkboxes": collect_checkbox_data(editor.checkbox_layout)
        }
        editor.current_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print("Błąd zapisu:", e)


def get_target_folder(tree: QTreeWidget) -> Path:
    item = tree.currentItem()
    if item is None:
        return NOTES_BASE_DIR
    path = Path(item.data(0, 256))
    return path if path.is_dir() else path.parent


def create_new_note(tree: QTreeWidget):
    target_folder = get_target_folder(tree)
    name, ok = QInputDialog.getText(tree, "Nowa notatka", "Nazwa pliku (bez .json):")
    if ok and name.strip():
        new_file = target_folder / f"{name.strip()}.json"
        if not new_file.exists():
            new_file.write_text(json.dumps({"text": "", "checkboxes": []}, indent=2), encoding="utf-8")
            refresh_tree(tree)


def create_new_folder(tree: QTreeWidget):
    target_folder = get_target_folder(tree)
    name, ok = QInputDialog.getText(tree, "Nowy folder", "Nazwa folderu:")
    if ok and name.strip():
        new_folder = target_folder / name.strip()
        new_folder.mkdir(parents=True, exist_ok=True)
        refresh_tree(tree)


def delete_item(tree: QTreeWidget, editor: QTextEdit):
    item = tree.currentItem()
    if item is None:
        return
    path = Path(item.data(0, 256))
    if not path.exists():
        return

    reply = QMessageBox.question(tree, "Usuń", f"Czy na pewno chcesz usunąć '{path.name}'?",
                                 QMessageBox.Yes | QMessageBox.No)
    if reply != QMessageBox.Yes:
        return

    if path.is_file():
        path.unlink()
        if editor.current_file == path:
            editor.setPlaceholderText("Wybierz notatkę z lewej, aby zobaczyć zawartość...")
            editor.setReadOnly(True)
            editor.setPlainText("")
            editor.current_file = None
            clear_checkboxes(editor.checkbox_layout)
    else:
        shutil.rmtree(path)

    refresh_tree(tree)


def export_note(editor: QTextEdit):
    if editor.current_file is None:
        QMessageBox.warning(editor, "Brak notatki", "Nie wybrano żadnej notatki!")
        return

    path, _ = QFileDialog.getSaveFileName(editor, "Eksportuj notatkę", editor.current_file.name, "JSON (*.json)")
    if path:
        shutil.copy(editor.current_file, path)
        QMessageBox.information(editor, "Sukces", "Wyeksportowano!")


def import_note(tree: QTreeWidget):
    source_file, _ = QFileDialog.getOpenFileName(tree, "Importuj notatkę", "", "JSON (*.json)")
    if not source_file:
        return

    target_folder = get_target_folder(tree)
    dest = target_folder / Path(source_file).name

    shutil.copy(source_file, dest)
    refresh_tree(tree)
    QMessageBox.information(tree, "Sukces", f"Zaimportowano: {dest.name}")


def filter_notes(tree: QTreeWidget, text: str):
    text = text.lower()
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        filter_tree_item(item, text)


def filter_tree_item(item: QTreeWidgetItem, text: str) -> bool:
    visible = text in item.text(0).lower()
    for i in range(item.childCount()):
        child = item.child(i)
        child_visible = filter_tree_item(child, text)
        visible = visible or child_visible
    item.setHidden(not visible)
    return visible
