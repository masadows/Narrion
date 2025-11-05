from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
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
        icon = qta.icon("mdi.file-account")
        change_btn.setIcon(icon)
        change_btn.setToolTip("Zmień kartę postaci")
        change_btn.setIconSize(QSize(24, 24))
        change_btn.setMaximumWidth(40)
        change_btn.clicked.connect(self.changePlayerFlie)
        header_layout.addWidget(change_btn)

        container_layout.addLayout(header_layout)
        container_layout.addWidget(QLineEdit())
        text_edit = QTextEdit()
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        text_edit.textChanged.connect(
            lambda te=text_edit: te.setFixedHeight(
                max(
                    int(
                        te.document().size().height()
                        + te.contentsMargins().top()
                        + te.contentsMargins().bottom()
                        + 4
                    ),
                    70,
                )
            )
        )
        container_layout.addWidget(text_edit)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.hide()
        container_layout.addWidget(self.image_label)

        self.pdf_doc = QPdfDocument(self)

        self.pdf_view = QPdfView(self)
        self.pdf_view.setDocument(self.pdf_doc)
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)

        self.pdf_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pdf_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)

        self.setPdfSize()

        container_layout.addWidget(self.pdf_view)

        container_layout.addStretch()
        scroll.setWidget(container)
        self.layout.addWidget(scroll)

    def changePlayerFlie(self):
        path_file, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz kartę postaci",
            "",
            "PDF i obrazy (*.pdf *.png *.jpg *.jpeg *.bmp *.gif);;Wszystkie pliki (*)",
        )

        if path_file.lower().split(".")[-1] == "pdf":
            self.pdf_doc.load(path_file)
            self.image_label.setPixmap(QPixmap())
            self.image_label.hide()
        else:
            self.pdf_doc = QPdfDocument()
            self.original_pixmap = QPixmap(path_file)
            self.updateImageSize()

    def setPdfSize(self):
        if self.pdf_doc.status() == QPdfDocument.Status.Ready:
            page_width_pt = self.pdf_doc.pagePointSize(0).width() + 20
            scale = self.pdf_view.width() * 72 / (96 * page_width_pt)

            self.pdf_view.setZoomFactor(scale)

            total_height = (
                sum(
                    self.pdf_doc.pagePointSize(i).height() * scale * 96 / 72
                    for i in range(self.pdf_doc.pageCount())
                )
                + 40
            )
            self.pdf_view.setFixedHeight(int(total_height))
        else:
            self.pdf_view.setFixedHeight(0)

    def updateImageSize(self):
        if self.original_pixmap:
            self.image_label.show()
            scaled = self.original_pixmap.scaled(
                self.image_label.width() - 30,
                self.original_pixmap.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "pdf_view") and self.pdf_view:
            self.setPdfSize()

        if self.image_label.pixmap():
            pixmap = self.image_label.pixmap()
            if not pixmap.isNull():
                self.updateImageSize()
