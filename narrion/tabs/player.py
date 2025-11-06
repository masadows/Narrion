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

from widgets.section_header import SectionHeader


class CharacterWidget(QWidget):
    def __init__(self, name):
        super().__init__()
        self.layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)

        header_layout = QHBoxLayout()
        header_layout.addWidget(SectionHeader(name))
        change_btn = QPushButton()
        change_btn.setIcon(qta.icon("mdi.file-account"))
        change_btn.setToolTip("Zmień kartę postaci")
        change_btn.setIconSize(QSize(24, 24))
        change_btn.setMaximumWidth(40)
        change_btn.clicked.connect(self.changePlayerFile)
        header_layout.addWidget(change_btn)
        container_layout.addLayout(header_layout)

        container_layout.addWidget(QLineEdit())

        self.text_edit = QTextEdit()
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.textChanged.connect(self.adjustTextEditHeight)
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

    def adjustTextEditHeight(self):
        te = self.text_edit
        height = max(
            int(
                te.document().size().height()
                + te.contentsMargins().top()
                + te.contentsMargins().bottom()
                + 4
            ),
            70,
        )
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

        if path_file.lower().endswith(".pdf"):
            self.loadPdfAsPixmap(path_file)
        else:
            self.loadImage(path_file)

    def loadPdfAsPixmap(self, path):
        self.pdf_doc = QPdfDocument(self)
        self.pdf_doc.load(path)
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
        self.updateImageSize()
        self.image_label.show()
        self.pdf_doc = None

    def updateImageSize(self):
        if self.original_pixmap is None:
            self.image_label.hide()
            return
        scaled = self.original_pixmap.scaledToWidth(self.width() - 70, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)
        self.image_label.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImageSize()
