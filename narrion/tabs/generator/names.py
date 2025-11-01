import fantasynames as names
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class NameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.function_map = {
            "Human": names.human,
            "Dwarf": names.dwarf,
            "Elf": names.elf,
            "Hobbit": names.hobbit,
            "French": names.french,
            "Anglo": names.anglo,
        }
        self.v = QVBoxLayout(self)
        self.box = QGroupBox()
        self.grid = QGridLayout(self.box)
        self.labels = []

        for i in range(16):
            label = QLabel("")
            label.setWordWrap(True)
            self.labels.append(label)
            self.grid.addWidget(label, i // 4, (i % 3) * 2, 1, 2)

        self.grid.addWidget(QLabel("Type:"), 4, 0)
        self.grid.addWidget(QLabel("Sex:"), 5, 0)

        name_type_select = QComboBox()
        name_type_select.addItems(["Human", "Dwarf", "Elf", "Hobbit", "French", "Anglo"])
        name_type_select.currentTextChanged.connect(self.select_generator_type)
        self.grid.addWidget(name_type_select, 4, 1, 1, 2)

        sex_type_select = QComboBox()
        sex_type_select.addItems(["male", "female", "sometimes"])
        sex_type_select.currentTextChanged.connect(self.select_sex)
        self.grid.addWidget(sex_type_select, 5, 1, 1, 2)

        self.button = QPushButton("Generate")
        self.button.setObjectName("rollButton")
        self.button.clicked.connect(self.generate_names)
        self.button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid.addWidget(self.button, 4, 3, 2, 3)

        self.v.addWidget(self.box)
        self.function = names.human
        self.sex = "male"

    def select_generator_type(self, type: str):
        self.function = self.function_map[type]

    def select_sex(self, sex: str):
        self.sex = sex if sex != "sometimes" else "any"

    def generate_names(self, *args, **kwargs):
        for label in self.labels:
            label.setText(self.function(self.sex))


def build() -> QWidget:
    return NameWidget()
