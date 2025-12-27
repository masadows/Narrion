import json
from pathlib import Path
import shutil

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta
from shiboken6 import isValid

from themes import DEFAULT_FONT
from widgets.color_wrapper import color
from widgets.section_header import SectionHeader

from .blocks import (
    BaseBlock,
    ChecklistBlock,
    ImageBlock,
    TableBlock,
    TextBlock,
    TimelineBlock,
)

NOTES_BASE_DIR = None


@color
class NotesTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DropOnly)

        self.setColumnCount(1)
        self.setMinimumWidth(0)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

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

    def changeFontColor(self, icon_color):
        if isValid(self):
            iterator = QTreeWidgetItemIterator(self)
            while iterator.value():
                item = iterator.value()
                path = Path(item.data(0, 256))
                if path.is_dir():
                    item.setIcon(0, qta.icon("fa5s.folder", color=icon_color))
                else:
                    item.setIcon(0, qta.icon("fa5s.file-alt", color=icon_color))

                iterator += 1


@color
class NoteEditorController:
    def __init__(self, container_layout):
        self.icon_buttons = list()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.blocks_layout = QVBoxLayout(self.scroll_content)
        self.blocks_layout.setAlignment(Qt.AlignTop)
        self.blocks_layout.setSpacing(20)
        self.scroll_area.setWidget(self.scroll_content)

        container_layout.addWidget(self.scroll_area)

        self.toolbar_layout = QHBoxLayout()
        self.create_block_btn("fa5s.paragraph", "Dodaj tekst", self.add_text_block)
        self.create_block_btn("fa5s.image", "Dodaj obraz", self.add_image_block)
        self.create_block_btn("fa5s.check-square", "Dodaj listę zadań", self.add_checklist_block)
        self.create_block_btn("fa5s.table", "Dodaj tabelę", self.add_table_block)
        self.create_block_btn("fa6s.timeline", "Dodaj oś czasu", self.add_timeline_block)

        container_layout.addLayout(self.toolbar_layout)

        self.current_file = None
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_note)

    def create_block_btn(self, icon_name, tooltip, func):
        btn = QPushButton()
        btn.clicked.connect(func)
        btn.setIcon(qta.icon(icon_name, color=DEFAULT_FONT["icon_color"]))
        btn.setIconSize(QSize(24, 24))
        btn.setToolTip(tooltip)
        btn.icon_name = icon_name
        self.icon_buttons.append(btn)
        self.toolbar_layout.addWidget(btn)

    def add_block_widget(self, block: BaseBlock):
        self.blocks_layout.addWidget(block)
        self.schedule_auto_save()

    def remove_block(self, block: BaseBlock):
        block.deleteLater()
        self.schedule_auto_save()

    def move_block_up(self, block: BaseBlock):
        idx = self.blocks_layout.indexOf(block)
        if idx > 0:
            self.blocks_layout.removeWidget(block)
            self.blocks_layout.insertWidget(idx - 1, block)
            self.scroll_area.ensureWidgetVisible(block)
            self.schedule_auto_save()

    def move_block_down(self, block: BaseBlock):
        idx = self.blocks_layout.indexOf(block)
        if idx < self.blocks_layout.count() - 1:
            self.blocks_layout.removeWidget(block)
            self.blocks_layout.insertWidget(idx + 1, block)
            self.scroll_area.ensureWidgetVisible(block)
            self.schedule_auto_save()

    def add_text_block(self):
        self.add_block_widget(TextBlock(self, self.remove_block))

    def add_image_block(self):
        self.add_block_widget(ImageBlock(self, self.remove_block))

    def add_checklist_block(self):
        self.add_block_widget(ChecklistBlock(self, self.remove_block))

    def add_table_block(self):
        self.add_block_widget(TableBlock(self, self.remove_block))

    def add_timeline_block(self):
        self.add_block_widget(TimelineBlock(self, self.remove_block))

    def clear_editor(self):
        while self.blocks_layout.count():
            child = self.blocks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_placeholder(self, text):
        self.clear_editor()
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        self.blocks_layout.addWidget(lbl)
        self.blocks_layout.addStretch()

    def load_note(self, path: Path):
        self.current_file = path
        self.clear_editor()
        try:
            content = path.read_text("utf-8")
            data = json.loads(content)

            if "blocks" not in data:
                if data.get("text"):
                    tb = TextBlock(self, self.remove_block)
                    tb.editor.setText(data.get("text"))
                    self.blocks_layout.addWidget(tb)
                if data.get("checkboxes"):
                    cb = ChecklistBlock(self, self.remove_block)
                    cb.load_data({"items": data.get("checkboxes")})
                    self.blocks_layout.addWidget(cb)
            else:
                for block_data in data["blocks"]:
                    b_type = block_data.get("type")
                    widget = None
                    if b_type == "text":
                        widget = TextBlock(self, self.remove_block)
                    elif b_type == "image":
                        widget = ImageBlock(self, self.remove_block)
                    elif b_type == "checklist":
                        widget = ChecklistBlock(self, self.remove_block)
                    elif b_type == "table":
                        widget = TableBlock(self, self.remove_block)
                    elif b_type == "timeline":
                        widget = TimelineBlock(self, self.remove_block)

                    if widget:
                        widget.load_data(block_data)
                        self.blocks_layout.addWidget(widget)

        except Exception as e:
            print(f"Błąd ładowania: {e}")

    def schedule_auto_save(self):
        if self.current_file:
            self.save_timer.start(1000)

    def save_note(self):
        if not self.current_file:
            return

        blocks_data = []
        for i in range(self.blocks_layout.count()):
            widget = self.blocks_layout.itemAt(i).widget()
            if isinstance(widget, BaseBlock):
                blocks_data.append(widget.get_data())

        data = {"blocks": blocks_data}
        try:
            self.current_file.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            print(f"Błąd zapisu: {e}")

    def changeFontColor(self, icon_color):
        for btn in self.icon_buttons:
            if isValid(btn):
                btn.setIcon(qta.icon(btn.icon_name, color=icon_color))


def build(current_session: str) -> QWidget:
    global NOTES_BASE_DIR
    NOTES_BASE_DIR = Path("data/notes") / current_session
    NOTES_BASE_DIR.mkdir(parents=True, exist_ok=True)

    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(4, 4, 4, 4)

    splitter = QSplitter(Qt.Horizontal)

    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 0, 0)

    left_layout.addWidget(SectionHeader("Notatki"))
    search = QLineEdit()
    search.setPlaceholderText("Szukaj notatek...")
    left_layout.addWidget(search)

    tree = NotesTree()
    refresh_tree(tree)
    left_layout.addWidget(tree)

    btns = QHBoxLayout()
    btn_new_note = QPushButton("Nowa notatka")
    btn_new_folder = QPushButton("Nowy folder")
    btn_delete = QPushButton("Usuń")

    btns.addWidget(btn_new_note)
    btns.addWidget(btn_new_folder)
    btns.addWidget(btn_delete)
    left_layout.addLayout(btns)

    right_widget = QWidget()
    right_layout = QVBoxLayout(right_widget)
    right_layout.setContentsMargins(0, 0, 0, 0)

    right_layout.addWidget(SectionHeader("Edytor notatki"))
    editor_controller = NoteEditorController(right_layout)

    splitter.addWidget(left_widget)
    splitter.addWidget(right_widget)

    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 4)

    h.addWidget(splitter)

    tree.itemClicked.connect(lambda item: open_note_handler(item, editor_controller))

    btn_new_note.clicked.connect(lambda: create_new_note(tree))
    btn_new_folder.clicked.connect(lambda: create_new_folder(tree))
    btn_delete.clicked.connect(lambda: delete_item(tree, editor_controller))
    search.textChanged.connect(lambda text: filter_notes(tree, text))

    iterator = QTreeWidgetItemIterator(tree)
    first_note_item = None

    while iterator.value():
        item = iterator.value()
        path = Path(item.data(0, 256))
        if path.is_file() and path.suffix == ".json":
            first_note_item = item
            break
        iterator += 1

    if first_note_item:
        tree.setCurrentItem(first_note_item)
        open_note_handler(first_note_item, editor_controller)
    else:
        editor_controller.show_placeholder(
            "Brak notatek.\n\nKliknij 'Nowa notatka', aby rozpocząć."
        )
    return w


def open_note_handler(item: QTreeWidgetItem, controller: NoteEditorController):
    path = Path(item.data(0, 256))

    if path.is_dir():
        controller.current_file = None
        controller.show_placeholder(
            f"Wybrano folder: '{path.name}'\n\nWybierz plik z listy lub utwórz nową notatkę."
        )

    elif path.is_file() and path.suffix == ".json":
        controller.load_note(path)

    else:
        controller.current_file = None
        controller.clear_editor()


def add_folder_items(parent_item: QTreeWidgetItem, folder_path: Path):
    for item in sorted(folder_path.iterdir()):
        display_name = item.stem if item.is_file() and item.suffix == ".json" else item.name

        child_item = QTreeWidgetItem([display_name])
        child_item.setData(0, 256, str(item))

        if item.is_dir():
            icon = qta.icon("fa5s.folder", color=DEFAULT_FONT["icon_color"])
            child_item.setIcon(0, icon)
            add_folder_items(child_item, item)
        else:
            icon = qta.icon("fa5s.file-alt", color=DEFAULT_FONT["icon_color"])
            child_item.setIcon(0, icon)

        parent_item.addChild(child_item)


def refresh_tree(tree: QTreeWidget):
    tree.clear()
    for item in sorted(NOTES_BASE_DIR.iterdir()):
        display_name = item.stem if item.is_file() and item.suffix == ".json" else item.name

        top_item = QTreeWidgetItem([display_name])
        top_item.setData(0, 256, str(item))

        if item.is_dir():
            icon = qta.icon("fa5s.folder", color=DEFAULT_FONT["icon_color"])
            top_item.setIcon(0, icon)
            add_folder_items(top_item, item)
        else:
            icon = qta.icon("fa5s.file-alt", color=DEFAULT_FONT["icon_color"])
            top_item.setIcon(0, icon)

        tree.addTopLevelItem(top_item)


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
            new_file.write_text(json.dumps({"blocks": []}, indent=2), encoding="utf-8")
            refresh_tree(tree)


def create_new_folder(tree: QTreeWidget):
    target_folder = get_target_folder(tree)
    name, ok = QInputDialog.getText(tree, "Nowy folder", "Nazwa folderu:")
    if ok and name.strip():
        new_folder = target_folder / name.strip()
        new_folder.mkdir(parents=True, exist_ok=True)
        refresh_tree(tree)


def delete_item(tree: QTreeWidget, controller: NoteEditorController):
    item = tree.currentItem()
    if item is None:
        return
    path = Path(item.data(0, 256))
    if not path.exists():
        return

    reply = QMessageBox.question(
        tree, "Usuń", f"Czy na pewno usunąć '{path.name}'?", QMessageBox.Yes | QMessageBox.No
    )
    if reply != QMessageBox.Yes:
        return

    if path.is_file():
        path.unlink()
        if controller.current_file == path:
            controller.current_file = None
            controller.show_placeholder("Plik został usunięty.")
    else:
        shutil.rmtree(path)
        if controller.current_file and path in controller.current_file.parents:
            controller.current_file = None
            controller.show_placeholder("Folder nadrzędny został usunięty.")

    refresh_tree(tree)


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
