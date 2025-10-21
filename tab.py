from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTabWidget

class DetachableTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.tabBarDoubleClicked.connect(self.detach_tab)

    def detach_tab(self, index):
        widget = self.widget(index)
        title = self.tabText(index)
        self.removeTab(index)

        win = QDialog()
        win.setWindowTitle(title)
        layout = QVBoxLayout(win)
        layout.addWidget(widget)

        restore_btn = QPushButton("Przywróć do głównego okna")
        layout.addWidget(restore_btn)

        def restore():
            self.addTab(widget, title)
            win.close()

        restore_btn.clicked.connect(restore)
        win.show()
