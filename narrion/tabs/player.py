from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QTextEdit,
    QScrollArea,
    QLabel,
)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from pathlib import Path
from widgets.section_header import SectionHeader
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class PlayerWidget(QWidget):
    def __init__(self, name):
        super().__init__()
        self.layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        container_layout.addWidget(SectionHeader(name))
        container_layout.addWidget(QLineEdit())
        container_layout.addWidget(QTextEdit())

        pdf_path = Path(__file__).parent / "solucja.pdf"
        if pdf_path.exists():
            self.pdf_doc = QPdfDocument(self)
            self.pdf_doc.load(str(pdf_path))

            self.pdf_view = QPdfView(self)
            self.pdf_view.setDocument(self.pdf_doc)
            self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)

            self.pdf_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.pdf_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

            dpi = 96
            total_height = (
                sum(
                    self.pdf_doc.pagePointSize(i).height() * dpi / 72 * self.pdf_view.zoomFactor()
                    for i in range(self.pdf_doc.pageCount())
                )
                + self.pdf_view.documentMargins().bottom()
                + self.pdf_view.documentMargins().top()
            )

            self.pdf_view.setMinimumHeight(total_height)
            self.pdf_view.setMaximumHeight(total_height)

            container_layout.addWidget(self.pdf_view)
        else:
            container_layout.addWidget(QLabel(f"Nie znaleziono pliku PDF: {pdf_path.name}"))

        container_layout.addStretch()
        scroll.setWidget(container)
        self.layout.addWidget(scroll)

    def resizeEvent(self, event):
        """Automatycznie przelicza zoom PDF przy zmianie rozmiaru okna."""
        super().resizeEvent(event)

        if self.pdf_view and self.pdf_doc:
            dpi = 96
            total_height = (
                sum(
                    self.pdf_doc.pagePointSize(i).height() * dpi / 72 * self.pdf_view.zoomFactor()
                    for i in range(self.pdf_doc.pageCount())
                )
                + self.pdf_view.documentMargins().bottom()
                + self.pdf_view.documentMargins().top()
            )

            self.pdf_view.setMinimumHeight(total_height)
            self.pdf_view.setMaximumHeight(total_height)
