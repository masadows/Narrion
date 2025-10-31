from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QMouseEvent, QTextCursor
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
    QWidget,
)

from widgets.section_header import SectionHeader


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

    tree = build_notes_tree()
    left.addWidget(tree)

    right = QVBoxLayout()
    right.addWidget(SectionHeader("Edytor notatki"))
    editor = QTextEdit()
    editor.setPlaceholderText("Wybierz notatkę z lewej, aby zobaczyć zawartość...")
    right.addWidget(editor)
    connect_checkbox_toggling(editor)

    editor.current_file = None
    editor.save_timer = QTimer()
    editor.save_timer.setSingleShot(True)
    editor.save_timer.timeout.connect(lambda: save_current_note(editor))

    btns = QHBoxLayout()
    btn_new_note = QPushButton("Nowa notatka")
    btn_new_folder = QPushButton("Nowy folder")
    btn_delete = QPushButton("Usuń")
    btn_add_checkbox = QPushButton("☑ Dodaj checkbox")
    btns.addWidget(btn_new_note)
    btns.addWidget(btn_new_folder)
    btns.addWidget(btn_delete)
    btns.addWidget(btn_add_checkbox)
    left.addLayout(btns)

    tree.itemClicked.connect(lambda item: open_note_in_editor(item, editor))
    btn_new_note.clicked.connect(lambda: create_new_note(tree))
    btn_new_folder.clicked.connect(lambda: create_new_folder(tree))
    btn_delete.clicked.connect(lambda: delete_item(tree, editor))
    btn_add_checkbox.clicked.connect(lambda: insert_checkbox(editor))
    search.textChanged.connect(lambda text: filter_notes(tree, text))
    editor.textChanged.connect(lambda: schedule_auto_save(editor))

    h.addLayout(left, 1)
    h.addLayout(right, 2)
    return w


def add_folder_items(parent_item: QTreeWidgetItem, folder_path: Path):
    for item in sorted(folder_path.iterdir()):
        child_item = QTreeWidgetItem([item.name])
        child_item.setData(0, 256, str(item))
        parent_item.addChild(child_item)
        if item.is_dir():
            add_folder_items(child_item, item)


def build_notes_tree() -> QTreeWidget:
    tree = QTreeWidget()
    tree.setHeaderHidden(True)
    for item in sorted(NOTES_BASE_DIR.iterdir()):
        top_item = QTreeWidgetItem([item.name])
        top_item.setData(0, 256, str(item))
        tree.addTopLevelItem(top_item)
        if item.is_dir():
            add_folder_items(top_item, item)
    return tree


def open_note_in_editor(item: QTreeWidgetItem, editor: QTextEdit):
    path = Path(item.data(0, 256))
    if path.is_file():
        try:
            content = path.read_text(encoding="utf-8")
            editor.blockSignals(True)
            editor.setPlainText(content)
            editor.blockSignals(False)
            editor.current_file = path
        except Exception as e:
            editor.setPlainText(f"Błąd przy otwieraniu pliku:\n{e}")
            editor.current_file = None
    else:
        editor.setPlainText("")
        editor.current_file = None


def schedule_auto_save(editor: QTextEdit):
    if editor.current_file is None:
        return
    editor.save_timer.start(500)


def save_current_note(editor: QTextEdit):
    if not editor.current_file:
        return
    try:
        text = editor.toPlainText()
        Path(editor.current_file).write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"❌ Błąd zapisu pliku: {e}")


def insert_checkbox(editor: QTextEdit):
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.End)
    cursor.insertText("☐ ")


def connect_checkbox_toggling(editor: QTextEdit):
    original_mouse_release = editor.mouseReleaseEvent

    def new_mouse_release(event: QMouseEvent):
        cursor = editor.cursorForPosition(event.position().toPoint())
        cursor.select(QTextCursor.LineUnderCursor)
        line = cursor.selectedText()
        if line.startswith("☐"):
            cursor.insertText(line.replace("☐", "☑", 1))
        elif line.startswith("☑"):
            cursor.insertText(line.replace("☑", "☐", 1))
        save_current_note(editor)
        original_mouse_release(event)

    editor.mouseReleaseEvent = new_mouse_release


def get_target_folder(tree: QTreeWidget) -> Path:
    item = tree.currentItem()
    if item is None:
        return NOTES_BASE_DIR
    path = Path(item.data(0, 256))
    if path.is_dir():
        return path
    else:
        return path.parent


def create_new_note(tree: QTreeWidget):
    target_folder = get_target_folder(tree)
    name, ok = QInputDialog.getText(tree, "Nowa notatka", "Nazwa pliku (bez .txt):")
    if ok and name.strip():
        new_file = target_folder / f"{name.strip()}.txt"
        if not new_file.exists():
            new_file.write_text("", encoding="utf-8")
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

    reply = QMessageBox.question(
        tree,
        "Usuń",
        f"Czy na pewno chcesz usunąć '{path.name}'?",
        QMessageBox.Yes | QMessageBox.No,
    )
    if reply == QMessageBox.Yes:
        try:
            if path.is_file():
                path.unlink()
                if editor.current_file == path:
                    editor.setPlainText("")
                    editor.current_file = None
            else:
                import shutil

                shutil.rmtree(path)
            refresh_tree(tree)
        except Exception as e:
            QMessageBox.critical(tree, "Błąd", f"Nie udało się usunąć: {e}")


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


def refresh_tree(tree: QTreeWidget):
    tree.clear()
    for item in sorted(NOTES_BASE_DIR.iterdir()):
        top_item = QTreeWidgetItem([item.name])
        top_item.setData(0, 256, str(item))
        tree.addTopLevelItem(top_item)
        if item.is_dir():
            add_folder_items(top_item, item)
