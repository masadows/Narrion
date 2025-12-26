import json
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta
from shiboken6 import isValid

from themes import DEFAULT_FONT
from widgets.color_wrapper import color
from widgets.section_header import SectionHeader


@color
class CharacterWidget(QWidget):
    def __init__(self, campaign, name, char_type="Player"):
        super().__init__()
        self.name = name
        self.char_type = char_type
        self.file_path = Path(f"data/sessions/{campaign}/characters/{char_type}/{name}.json")
        self.current_image_path = None

        self.layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)

        header_layout = QHBoxLayout()
        header_layout.addWidget(SectionHeader(name))

        self.change_btn = QPushButton()
        self.change_btn.setIcon(qta.icon("mdi.file-account", color=DEFAULT_FONT["icon_color"]))
        self.change_btn.setToolTip("Zmień kartę postaci (PDF/Obraz)")
        self.change_btn.setIconSize(QSize(24, 24))
        self.change_btn.setMaximumWidth(40)
        self.change_btn.clicked.connect(self.changePlayerFile)
        header_layout.addWidget(self.change_btn)
        container_layout.addLayout(header_layout)

        stats_layout = QHBoxLayout()

        stats_layout.addWidget(QLabel("HP:"))
        self.hp_input = QLineEdit()
        self.hp_input.setMaxLength(7)
        self.hp_input.setMaximumWidth(80)
        self.hp_input.editingFinished.connect(self.save_data)
        stats_layout.addWidget(self.hp_input)

        stats_layout.addWidget(QLabel("AC:"))
        self.ac_input = QLineEdit()
        self.ac_input.setMaxLength(5)
        self.ac_input.setMaximumWidth(50)
        self.ac_input.editingFinished.connect(self.save_data)
        stats_layout.addWidget(self.ac_input)

        stats_layout.addStretch()
        container_layout.addLayout(stats_layout)

        self.stat_input = QLineEdit()
        self.stat_input.setPlaceholderText("Krótki opis / Klasa / Poziom")
        self.stat_input.editingFinished.connect(self.save_data)
        container_layout.addWidget(self.stat_input)

        self.text_edit = QTextEdit()
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.textChanged.connect(self.adjustTextEditHeight)
        self.text_edit.textChanged.connect(self.save_data)
        container_layout.addWidget(self.text_edit)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.hide()
        container_layout.addWidget(self.image_label)

        container_layout.addStretch()
        scroll.setWidget(container)
        self.layout.addWidget(scroll)

        self.pdf_doc = None
        self.original_pixmap = None

        self.load_data()

    def load_data(self):
        if not self.file_path.exists():
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.stat_input.blockSignals(True)
            self.text_edit.blockSignals(True)

            self.stat_input.setText(data.get("short_description", ""))
            self.text_edit.setHtml(data.get("description", ""))

            self.hp_input.setText(data.get("stats_hp", ""))
            self.ac_input.setText(data.get("stats_ac", ""))

            saved_image_path = data.get("image_path", None)
            if saved_image_path and Path(saved_image_path).exists():
                self.current_image_path = saved_image_path
                self.load_visual_from_path(saved_image_path)

            self.adjustTextEditHeight()
            self.stat_input.blockSignals(False)
            self.text_edit.blockSignals(False)

        except Exception as e:
            print(f"Błąd ładowania postaci {self.name}: {e}")

    def save_data(self):
        data = {
            "name": self.name,
            "type": self.char_type,
            "short_description": self.stat_input.text(),
            "description": self.text_edit.toHtml(),
            "image_path": self.current_image_path,
            "stats_hp": self.hp_input.text(),
            "stats_ac": self.ac_input.text(),
        }

        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd zapisu postaci {self.name}: {e}")

    def adjustTextEditHeight(self):
        te = self.text_edit
        doc_height = te.document().size().height()
        margins = te.contentsMargins().top() + te.contentsMargins().bottom()
        height = max(int(doc_height + margins + 10), 100)
        te.setFixedHeight(height)

    def changePlayerFile(self):
        path_file, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz kartę postaci",
            "",
            "PDF i obrazy (*.pdf *.png *.jpg *.jpeg *.bmp *.gif);;Wszystkie pliki (*)",
        )
        if not path_file:
            return

        self.current_image_path = path_file
        self.load_visual_from_path(path_file)

        self.save_data()

    def load_visual_from_path(self, path):
        if path.lower().endswith(".pdf"):
            self.loadPdfAsPixmap(path)
        else:
            self.loadImage(path)

    def loadPdfAsPixmap(self, path):
        self.pdf_doc = QPdfDocument(self)
        try:
            self.pdf_doc.load(path)
        except Exception:
            return

        if self.pdf_doc.status() != QPdfDocument.Status.Ready:
            return

        images = []
        total_height = 0
        max_width = 0

        for i in range(self.pdf_doc.pageCount()):
            page_size = self.pdf_doc.pagePointSize(i)
            width_px = int(page_size.width() * 4 / 3)
            height_px = int(page_size.height() * 4 / 3)

            image = self.pdf_doc.render(i, QSize(width_px, height_px))
            if image.isNull():
                continue
            images.append(image)
            total_height += image.height()
            max_width = max(max_width, image.width())

        if not images:
            return

        combined = QPixmap(max_width, total_height)
        combined.fill(QColor("white"))
        painter = QPainter(combined)
        y_offset = 0
        for img in images:
            painter.drawImage(0, y_offset, img)
            y_offset += img.height()
        painter.end()

        self.original_pixmap = combined
        self.updateImageSize()
        self.image_label.show()

    def loadImage(self, path):
        self.original_pixmap = QPixmap(path)
        if self.original_pixmap.isNull():
            return

        self.updateImageSize()
        self.image_label.show()
        self.pdf_doc = None

    def updateImageSize(self):
        if self.original_pixmap is None or self.original_pixmap.isNull():
            self.image_label.hide()
            return
        scaled = self.original_pixmap.scaledToWidth(self.width() - 70, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.image_label.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImageSize()

    def changeFontColor(self, icon_color):
        if isValid(self.change_btn):
            self.change_btn.setIcon(qta.icon("mdi.file-account", color=icon_color))
