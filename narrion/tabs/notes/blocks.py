import base64
import os
from typing import Any, Dict

from PySide6.QtCore import QPoint, QRect, QSize, Qt, QTimer
from PySide6.QtGui import (
    QFont,
    QPainter,
    QPalette,
    QPen,
    QPixmap,
    QTextBlockFormat,
    QTextCharFormat,
    QTextListFormat,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStyle,
    QStyleOption,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta
from shiboken6 import isValid

from themes import DEFAULT_FONT
from widgets.color_wrapper import color


@color
class BaseBlock(QWidget):
    '''Base class for all note blocks.'''
    def __init__(self, parent_editor, delete_callback):
        super().__init__()
        self.parent_editor = parent_editor
        self.delete_callback = delete_callback
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.header_layout = QHBoxLayout()

        self.btn_up = QPushButton()
        self.btn_up.setIcon(qta.icon("fa5s.arrow-up", color=DEFAULT_FONT["icon_color"]))
        self.btn_up.setFixedSize(24, 24)
        self.btn_up.setToolTip("Przesuń w górę")
        self.btn_up.clicked.connect(lambda: self.parent_editor.move_block_up(self))

        self.btn_down = QPushButton()
        self.btn_down.setIcon(qta.icon("fa5s.arrow-down", color=DEFAULT_FONT["icon_color"]))
        self.btn_down.setFixedSize(24, 24)
        self.btn_down.setToolTip("Przesuń w dół")
        self.btn_down.clicked.connect(lambda: self.parent_editor.move_block_down(self))

        self.btn_delete = QPushButton()
        self.btn_delete.setIcon(qta.icon("fa5s.trash-alt", color=DEFAULT_FONT["icon_color"]))
        self.btn_delete.setFixedSize(24, 24)
        self.btn_delete.setToolTip("Usuń blok")
        self.btn_delete.clicked.connect(lambda: self.delete_callback(self))

        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_up)
        self.header_layout.addWidget(self.btn_down)
        self.header_layout.addSpacing(8)
        self.header_layout.addWidget(self.btn_delete)

        self.layout.addLayout(self.header_layout)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.content_widget)

        self.setAttribute(Qt.WA_StyledBackground, True)

    def paintEvent(self, event):
        '''Custom paint event to ensure proper styling.'''
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def get_data(self) -> Dict[str, Any]:
        return {}

    def load_data(self, data: Dict[str, Any]):
        pass

    def signal_change(self):
        '''Notify parent editor of changes for auto-saving.'''
        if self.parent_editor:
            self.parent_editor.schedule_auto_save()

    def changeFontColor(self, icon_color):
        '''Update icon colors based on theme.'''
        if isValid(self.btn_up):
            self.btn_up.setIcon(qta.icon("fa5s.arrow-up", color=icon_color))
        if isValid(self.btn_down):
            self.btn_down.setIcon(qta.icon("fa5s.arrow-down", color=icon_color))
        if isValid(self.btn_delete):
            self.btn_delete.setIcon(qta.icon("fa5s.trash-alt", color=icon_color))


@color
class TextBlock(BaseBlock):
    '''Rich text block with formatting options.'''
    def __init__(self, parent_editor, delete_callback):
        super().__init__(parent_editor, delete_callback)

        current_style = self.styleSheet()
        qss_path = os.path.join(os.path.dirname(__file__), "text_style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(current_style + f.read())

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 5)
        toolbar_layout.setSpacing(2)

        self.combo_style = QComboBox()
        self.combo_style.addItems(["Normalny", "Nagłówek 1", "Nagłówek 2", "Nagłówek 3"])
        self.combo_style.setMinimumWidth(120)
        self.combo_style.currentIndexChanged.connect(self.change_style)
        toolbar_layout.addWidget(self.combo_style)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        toolbar_layout.addWidget(line)

        self.btn_bold = self.create_format_button("fa5s.bold", "Pogrubienie", self.toggle_bold)
        self.btn_italic = self.create_format_button("fa5s.italic", "Kursywa", self.toggle_italic)
        self.btn_underline = self.create_format_button(
            "fa5s.underline", "Podkreślenie", self.toggle_underline
        )

        toolbar_layout.addWidget(self.btn_bold)
        toolbar_layout.addWidget(self.btn_italic)
        toolbar_layout.addWidget(self.btn_underline)

        toolbar_layout.addSpacing(10)

        self.btn_list_bullet = self.create_format_button(
            "fa5s.list-ul", "Lista punktowana", lambda: self.toggle_list(QTextListFormat.ListDisc)
        )
        self.btn_list_number = self.create_format_button(
            "fa5s.list-ol",
            "Lista numerowana",
            lambda: self.toggle_list(QTextListFormat.ListDecimal),
        )
        toolbar_layout.addWidget(self.btn_list_bullet)
        toolbar_layout.addWidget(self.btn_list_number)

        toolbar_layout.addSpacing(10)

        self.align_group = QButtonGroup(self)
        self.btn_align_left = self.create_format_button(
            "fa5s.align-left", "Do lewej", lambda: self.set_align(Qt.AlignLeft)
        )
        self.btn_align_center = self.create_format_button(
            "fa5s.align-center", "Wyśrodkuj", lambda: self.set_align(Qt.AlignCenter)
        )
        self.btn_align_right = self.create_format_button(
            "fa5s.align-right", "Do prawej", lambda: self.set_align(Qt.AlignRight)
        )

        self.align_group.addButton(self.btn_align_left)
        self.align_group.addButton(self.btn_align_center)
        self.align_group.addButton(self.btn_align_right)
        self.btn_align_left.setChecked(True)

        toolbar_layout.addWidget(self.btn_align_left)
        toolbar_layout.addWidget(self.btn_align_center)
        toolbar_layout.addWidget(self.btn_align_right)

        toolbar_layout.addStretch()
        self.content_layout.addLayout(toolbar_layout)

        self.editor = QTextEdit()
        self.editor.setMinimumHeight(100)
        self.editor.textChanged.connect(self.signal_change)
        self.editor.cursorPositionChanged.connect(self.update_toolbar_state)

        self.content_layout.addWidget(self.editor)

    def create_format_button(self, icon_name, tooltip, slot):
        '''Helper to create a formatting button.'''
        btn = QToolButton()
        btn.setIcon(qta.icon(icon_name, color=DEFAULT_FONT["icon_color"]))
        btn.setIconSize(QSize(14, 14))
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.clicked.connect(slot)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.icon_name = icon_name
        return btn

    def toggle_bold(self):
        '''Toggle bold formatting.'''
        is_checked = self.btn_bold.isChecked()
        fmt = self.editor.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if is_checked else QFont.Normal)
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def toggle_italic(self):
        '''Toggle italic formatting.'''
        is_checked = self.btn_italic.isChecked()
        fmt = self.editor.currentCharFormat()
        fmt.setFontItalic(is_checked)
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def toggle_underline(self):
        '''Toggle underline formatting.'''
        is_checked = self.btn_underline.isChecked()
        fmt = self.editor.currentCharFormat()
        fmt.setFontUnderline(is_checked)
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def toggle_list(self, list_style):
        '''Toggle list formatting.'''
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()

        current_list = cursor.currentList()
        if current_list:
            format = current_list.format()
            if format.style() == list_style:
                cursor.setBlockFormat(QTextBlockFormat())
            else:
                new_format = QTextListFormat()
                new_format.setStyle(list_style)
                current_list.setFormat(new_format)
        else:
            list_fmt = QTextListFormat()
            list_fmt.setStyle(list_style)
            cursor.createList(list_fmt)

        cursor.endEditBlock()
        self.editor.setFocus()

    def set_align(self, alignment):
        '''Set text alignment.'''
        self.editor.setAlignment(alignment)
        self.editor.setFocus()

    def change_style(self):
        '''Change text style based on combo box selection.'''
        idx = self.combo_style.currentIndex()
        self.editor.blockSignals(True)

        fmt = QTextCharFormat()
        if idx == 0:
            fmt.setFontWeight(QFont.Normal)
            fmt.setFontPointSize(11)
        elif idx == 1:
            fmt.setFontPointSize(24)
            fmt.setFontWeight(QFont.Bold)
        elif idx == 2:
            fmt.setFontPointSize(18)
            fmt.setFontWeight(QFont.Bold)
        elif idx == 3:
            fmt.setFontPointSize(14)
            fmt.setFontWeight(QFont.Bold)

        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.blockSignals(False)
        self.editor.setFocus()
        self.update_toolbar_state()

    def update_toolbar_state(self):
        '''Update toolbar button states based on current text format.'''
        self.btn_bold.blockSignals(True)
        self.btn_italic.blockSignals(True)
        self.btn_underline.blockSignals(True)
        self.combo_style.blockSignals(True)
        self.align_group.blockSignals(True)

        fmt = self.editor.currentCharFormat()

        self.btn_bold.setChecked(fmt.fontWeight() == QFont.Bold)
        self.btn_italic.setChecked(fmt.fontItalic())
        self.btn_underline.setChecked(fmt.fontUnderline())

        size = fmt.fontPointSize()
        if size == 24:
            index = 1
        elif size == 18:
            index = 2
        elif size == 14:
            index = 3
        else:
            index = 0
        self.combo_style.setCurrentIndex(index)

        align = self.editor.alignment()
        if align & Qt.AlignLeft:
            self.btn_align_left.setChecked(True)
        elif align & Qt.AlignCenter:
            self.btn_align_center.setChecked(True)
        elif align & Qt.AlignRight:
            self.btn_align_right.setChecked(True)

        cursor = self.editor.textCursor()
        current_list = cursor.currentList()
        self.btn_list_bullet.setChecked(False)
        self.btn_list_number.setChecked(False)
        if current_list:
            style = current_list.format().style()
            if style == QTextListFormat.ListDisc:
                self.btn_list_bullet.setChecked(True)
            elif style == QTextListFormat.ListDecimal:
                self.btn_list_number.setChecked(True)

        self.btn_bold.blockSignals(False)
        self.btn_italic.blockSignals(False)
        self.btn_underline.blockSignals(False)
        self.combo_style.blockSignals(False)
        self.align_group.blockSignals(False)

    def get_data(self):
        '''Get the rich text content as HTML.'''
        return {"type": "text", "html": self.editor.toHtml()}

    def load_data(self, data):
        '''Load rich text content from HTML.'''
        self.editor.setHtml(data.get("html", ""))

    def changeFontColor(self, icon_color):
        '''Update icon colors based on theme.'''
        super().changeFontColor(icon_color)
        buttons = [
            self.btn_bold,
            self.btn_italic,
            self.btn_underline,
            self.btn_list_bullet,
            self.btn_list_number,
            self.btn_align_left,
            self.btn_align_center,
            self.btn_align_right,
        ]
        for btn in buttons:
            icon_name = btn.icon_name
            if icon_name and isValid(btn):
                btn.setIcon(qta.icon(icon_name, color=icon_color))


@color
class ImageBlock(BaseBlock):
    '''Image block allowing image upload and display.'''
    def __init__(self, parent_editor, delete_callback):
        super().__init__(parent_editor, delete_callback)

        self.btn_load = QPushButton("Wybierz obraz")
        self.btn_load.clicked.connect(self.load_image_from_file)
        self.content_layout.addWidget(self.btn_load)

        self.image_label = QLabel("Brak obrazu")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.image_label)

        self.current_base64 = None

    def load_image_from_file(self):
        '''Load an image from file and convert to base64.'''
        path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz obraz", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            with open(path, "rb") as image_file:
                self.current_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            self.display_image()
            self.signal_change()

    def display_image(self):
        '''Display the image from base64 data.'''
        if self.current_base64:
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(self.current_base64))
            scaled = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
            self.image_label.setText("")
        else:
            self.image_label.setText("Brak obrazu")

    def get_data(self):
        return {"type": "image", "data": self.current_base64}

    def load_data(self, data):
        self.current_base64 = data.get("data")
        self.display_image()


class ChecklistBlock(BaseBlock):
    '''Checklist block with add/remove item functionality.'''
    def __init__(self, parent_editor, delete_callback):
        super().__init__(parent_editor, delete_callback)

        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(2)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addLayout(self.items_layout)

        self.btn_add = QPushButton("+ Dodaj element")
        self.btn_add.clicked.connect(lambda: self.add_item())
        self.content_layout.addWidget(self.btn_add)

    def add_item(self, text="", checked=False):
        '''Add a new checklist item.'''
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        cb = QCheckBox()
        cb.setChecked(checked)
        cb.stateChanged.connect(self.signal_change)

        le = QLineEdit(text)
        le.setPlaceholderText("Zadanie...")
        le.textChanged.connect(self.signal_change)

        btn_del = QPushButton()
        btn_del.setIcon(qta.icon("fa5s.times", color=DEFAULT_FONT["icon_color"]))
        btn_del.setFixedSize(24, 24)
        btn_del.setFlat(True)
        btn_del.clicked.connect(lambda: self.remove_item(row))

        row.addWidget(cb)
        row.addWidget(le)
        row.addWidget(btn_del)

        container = QWidget()
        container.setLayout(row)
        self.items_layout.addWidget(container)
        self.signal_change()

    def remove_item(self, layout_item):
        '''Remove a checklist item.'''
        for i in range(self.items_layout.count()):
            item = self.items_layout.itemAt(i)
            widget = item.widget()
            if widget.layout() == layout_item:
                widget.deleteLater()
                self.signal_change()
                break

    def get_data(self):
        '''Get checklist data.'''
        items = []
        for i in range(self.items_layout.count()):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                row_layout = widget.layout()
                cb = row_layout.itemAt(0).widget()
                le = row_layout.itemAt(1).widget()
                items.append({"text": le.text(), "checked": cb.isChecked()})
        return {"type": "checklist", "items": items}

    def load_data(self, data):
        '''Load checklist data.'''
        for item in data.get("items", []):
            self.add_item(item.get("text", ""), item.get("checked", False))

    def changeFontColor(self, icon_color):
        '''Update delete button icon colors based on theme.'''
        super().changeFontColor(icon_color)
        if isValid(self):
            for i in range(self.items_layout.count()):
                container = self.items_layout.itemAt(i).widget()
                if container:
                    layout = container.layout()
                    if layout.count() >= 3:
                        btn = layout.itemAt(2).widget()
                        if isinstance(btn, QPushButton):
                            btn.setIcon(qta.icon("fa5s.times", color=icon_color))


@color
class TableBlock(BaseBlock):
    '''Table block with dynamic row/column addition.'''
    def __init__(self, parent_editor, delete_callback):
        super().__init__(parent_editor, delete_callback)

        ctrl_layout = QHBoxLayout()
        btn_add_row = QPushButton("+ Wiersz")
        btn_add_col = QPushButton("+ Kolumna")

        btn_add_row.clicked.connect(lambda: (self.add_row(), self.adjust_table_height()))
        btn_add_col.clicked.connect(self.add_col)

        ctrl_layout.addWidget(btn_add_row)
        ctrl_layout.addWidget(btn_add_col)
        ctrl_layout.addStretch()

        self.content_layout.addLayout(ctrl_layout)

        self.table = QTableWidget(2, 2)

        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        header.sectionDoubleClicked.connect(self.change_header_title)

        self.table.itemChanged.connect(self.signal_change)

        self.content_layout.addWidget(self.table)

        self.table.setHorizontalHeaderLabels(["Kolumna 1", "Kolumna 2"])

        self.adjust_table_height()

    def change_header_title(self, index):
        '''Change the title of a table column header.'''
        old_name = self.table.horizontalHeaderItem(index).text()
        new_name, ok = QInputDialog.getText(
            self, "Edytuj nagłówek", "Nazwa kolumny:", text=old_name
        )

        if ok and new_name:
            self.table.horizontalHeaderItem(index).setText(new_name)
            self.signal_change()

    def adjust_table_height(self):
        '''Adjust the table height based on the number of rows.'''
        header_height = self.table.horizontalHeader().height()
        row_height = self.table.rowHeight(0) if self.table.rowCount() > 0 else 30
        total_height = header_height + (self.table.rowCount() * row_height) + 4

        self.table.setMinimumHeight(max(70, total_height))
        self.table.setMaximumHeight(max(70, total_height))

    def add_row(self):
        '''Add a new row to the table.'''
        self.table.insertRow(self.table.rowCount())
        self.signal_change()

    def add_col(self):
        '''Add a new column to the table.'''
        col_count = self.table.columnCount()
        self.table.insertColumn(col_count)
        self.table.setHorizontalHeaderItem(col_count, QTableWidgetItem(f"Kolumna {col_count + 1}"))
        self.signal_change()

    def get_data(self):
        '''Get table data.'''
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        data = []
        for r in range(rows):
            row_data = []
            for c in range(cols):
                item = self.table.item(r, c)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        headers = []
        col_widths = []
        for c in range(cols):
            item = self.table.horizontalHeaderItem(c)
            headers.append(item.text() if item else str(c + 1))
            col_widths.append(self.table.columnWidth(c))

        return {
            "type": "table",
            "rows": rows,
            "cols": cols,
            "data": data,
            "headers": headers,
            "col_widths": col_widths,
        }

    def load_data(self, data):
        '''Load table data.'''
        self.table.blockSignals(True)
        rows = data.get("rows", 2)
        cols = data.get("cols", 2)

        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        headers = data.get("headers", [])
        while len(headers) < cols:
            headers.append(f"Kolumna {len(headers) + 1}")
        self.table.setHorizontalHeaderLabels(headers)

        grid = data.get("data", [])
        for r, row_data in enumerate(grid):
            for c, text in enumerate(row_data):
                self.table.setItem(r, c, QTableWidgetItem(text))

        col_widths = data.get("col_widths", [])
        for c, width in enumerate(col_widths):
            if c < cols:
                self.table.setColumnWidth(c, width)

        self.table.blockSignals(False)
        self.adjust_table_height()


class TimelineWidget(QWidget):
    '''Custom widget to visualize a timeline of events.'''
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(220)
        self.events = []
        self.setAttribute(Qt.WA_StyledBackground, True)

    def set_events(self, events):
        '''Set the list of events to display on the timeline.'''
        self.events = events
        min_width = max(600, len(events) * 160 + 100)
        self.setMinimumWidth(min_width)
        self.update()

    def paintEvent(self, event):
        '''Custom paint event to draw the timeline and events.'''
        painter = QPainter()
        if not painter.begin(self):
            return

        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect()

            palette = self.palette()

            main_color = palette.color(QPalette.WindowText)

            dot_color = palette.color(QPalette.Highlight)
            stem_color = palette.color(QPalette.AlternateBase)

            center_y = rect.height() // 2
            margin_x = 50

            painter.setPen(QPen(main_color, 2))
            painter.drawLine(margin_x, center_y, rect.width() - margin_x, center_y)

            if not self.events:
                return

            count = len(self.events)
            available_width = rect.width() - (2 * margin_x)

            if count > 1:
                step_x = available_width / (count - 1)
            else:
                step_x = 0

            for i, (date_txt, title_txt) in enumerate(self.events):
                current_x = margin_x + (i * step_x) if count > 1 else rect.width() // 2

                painter.setBrush(dot_color)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPoint(int(current_x), center_y), 5, 5)

                is_top = i % 2 == 0

                stem_height = 30
                text_width = 140
                text_height = 60

                painter.setPen(QPen(stem_color, 1, Qt.DotLine))

                if is_top:
                    painter.drawLine(
                        int(current_x), center_y, int(current_x), center_y - stem_height
                    )
                    rect_date = QRect(
                        int(current_x - text_width / 2),
                        center_y - stem_height - 20,
                        text_width,
                        20,
                    )
                    rect_title = QRect(
                        int(current_x - text_width / 2),
                        center_y - stem_height - 20 - text_height,
                        text_width,
                        text_height,
                    )
                    align_date = Qt.AlignHCenter | Qt.AlignBottom
                    align_title = Qt.AlignHCenter | Qt.AlignBottom | Qt.TextWordWrap
                else:
                    painter.drawLine(
                        int(current_x), center_y, int(current_x), center_y + stem_height
                    )
                    rect_date = QRect(
                        int(current_x - text_width / 2), center_y + stem_height, text_width, 20
                    )
                    rect_title = QRect(
                        int(current_x - text_width / 2),
                        center_y + stem_height + 20,
                        text_width,
                        text_height,
                    )
                    align_date = Qt.AlignHCenter | Qt.AlignTop
                    align_title = Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap

                painter.setPen(main_color)

                font_date = QFont("Arial")
                font_date.setPixelSize(11)
                font_date.setBold(True)
                painter.setFont(font_date)
                painter.drawText(rect_date, align_date, date_txt)

                font_title = QFont("Arial")
                font_title.setPixelSize(11)
                font_title.setBold(False)
                painter.setFont(font_title)
                painter.drawText(rect_title, align_title, title_txt)

        except Exception as e:
            print(f"Błąd rysowania: {e}")
        finally:
            painter.end()


@color
class TimelineBlock(BaseBlock):
    '''Timeline block allowing event addition and visualization.'''
    def __init__(self, parent_editor, delete_callback):
        super().__init__(parent_editor, delete_callback)

        self.icon_buttons = list()

        self.container_layout = QVBoxLayout()
        self.content_layout.addLayout(self.container_layout)

        self.input_widget = QWidget()
        self.input_layout = QVBoxLayout(self.input_widget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(2)

        scroll_input = QScrollArea()
        scroll_input.setWidgetResizable(True)
        scroll_input.setWidget(self.input_widget)
        scroll_input.setMinimumHeight(120)
        scroll_input.setMaximumHeight(200)

        self.btn_add_event = QPushButton("Dodaj Zdarzenie")
        self.btn_add_event.clicked.connect(lambda: self.add_event_input())

        self.container_layout.addWidget(self.btn_add_event)
        self.container_layout.addWidget(scroll_input)

        self.events_layout = QVBoxLayout()
        self.events_layout.setAlignment(Qt.AlignTop)
        self.input_layout.addLayout(self.events_layout)

        self.viz_scroll = QScrollArea()
        self.viz_scroll.setWidgetResizable(True)
        self.viz_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viz_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.viz_scroll.setMinimumHeight(240)

        self.timeline_viz = TimelineWidget()
        self.viz_scroll.setWidget(self.timeline_viz)

        self.container_layout.addWidget(self.viz_scroll)

    def add_event_input(self, date="", title=""):
        '''Add a new event input row.'''
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        date_edit = QLineEdit(date)
        date_edit.setPlaceholderText("Data")
        date_edit.setFixedWidth(70)

        title_edit = QLineEdit(title)
        title_edit.setPlaceholderText("Opis (długi tekst...)")

        btn_up = QPushButton()
        btn_up.setIcon(qta.icon("fa5s.arrow-up", color=DEFAULT_FONT["icon_color"]))
        btn_up.setFixedWidth(24)
        btn_up.icon_name = "fa5s.arrow-up"

        btn_down = QPushButton()
        btn_down.setIcon(qta.icon("fa5s.arrow-down", color=DEFAULT_FONT["icon_color"]))
        btn_down.setFixedWidth(24)
        btn_down.icon_name = "fa5s.arrow-down"

        btn_del = QPushButton()
        btn_del.setIcon(qta.icon("fa5s.times", color=DEFAULT_FONT["icon_color"]))
        btn_del.setFixedSize(24, 24)
        btn_del.setFlat(True)
        btn_del.icon_name = "fa5s.times"
        self.icon_buttons.extend([btn_up, btn_down, btn_del])

        row.addWidget(btn_up)
        row.addWidget(btn_down)
        row.addWidget(date_edit)
        row.addWidget(title_edit)
        row.addWidget(btn_del)

        container = QWidget()
        container.setLayout(row)

        date_edit.textChanged.connect(self.refresh_visualization)
        title_edit.textChanged.connect(self.refresh_visualization)

        btn_del.clicked.connect(lambda: self.remove_event(container))
        btn_up.clicked.connect(lambda: self.move_event(container, -1))
        btn_down.clicked.connect(lambda: self.move_event(container, 1))

        self.events_layout.addWidget(container)

        QTimer.singleShot(10, lambda: self.refresh_visualization())

    def move_event(self, widget, direction):
        '''Move an event up or down in the list.'''
        idx = self.events_layout.indexOf(widget)
        new_idx = idx + direction

        if 0 <= new_idx < self.events_layout.count():
            self.events_layout.removeWidget(widget)
            self.events_layout.insertWidget(new_idx, widget)
            self.refresh_visualization()

    def remove_event(self, widget):
        '''Remove an event input row.'''
        widget.deleteLater()
        QTimer.singleShot(50, self.refresh_visualization)

    def refresh_visualization(self):
        '''Refresh the timeline visualization based on current events.'''
        events = []
        for i in range(self.events_layout.count()):
            w = self.events_layout.itemAt(i).widget()
            if w:
                layout = w.layout()
                d = layout.itemAt(2).widget().text()
                t = layout.itemAt(3).widget().text()
                events.append((d, t))

        self.timeline_viz.set_events(events)
        self.signal_change()

    def get_data(self):
        '''Get timeline data.'''
        events = []
        for i in range(self.events_layout.count()):
            w = self.events_layout.itemAt(i).widget()
            if w:
                layout = w.layout()
                events.append(
                    {
                        "date": layout.itemAt(2).widget().text(),
                        "title": layout.itemAt(3).widget().text(),
                    }
                )
        return {"type": "timeline", "events": events}

    def load_data(self, data):
        '''Load timeline data.'''
        for ev in data.get("events", []):
            self.add_event_input(ev.get("date", ""), ev.get("title", ""))

    def changeFontColor(self, icon_color):
        '''Update icon colors based on theme.'''
        super().changeFontColor(icon_color)
        if isValid(self):
            for btn in self.icon_buttons:
                btn.setIcon(qta.icon(btn.icon_name, color=icon_color))
