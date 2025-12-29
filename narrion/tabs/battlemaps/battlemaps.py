from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, 
    QSplitter, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QListWidgetItem, QSpinBox
)

from widgets.placeholders import make_placeholder
from widgets.section_header import SectionHeader

from .model_logic import ModelLogic
import pickle
import os
import numpy as np


class BattlemapsWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.logic = None
        self.cache_data = {} 
        self.current_folder = None
        
        self.image_paths = []
        self.embeddings_np = None

        try:
            self.logic = ModelLogic(model_folder_name="onnx-clip") 
            print("Model załadowany poprawnie.")
        except Exception as e:
            print(f"Błąd modelu: {e}")

        self.init_ui()

    def init_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(4, 4, 4, 4)

        header = QHBoxLayout()
        header.addWidget(SectionHeader("Battlemapy"))
        header.addStretch()
        
        self.btn_scan = QPushButton("Skanuj folder")
        self.btn_scan.clicked.connect(self.scan_folder)
        header.addWidget(self.btn_scan)
        v.addLayout(header)

        splitter = QSplitter(Qt.Horizontal)

        left_frame = QWidget()
        l_layout = QVBoxLayout(left_frame)
        l_layout.addWidget(QLabel("Wyniki wyszukiwania:"))
        self.map_list = QListWidget()
        self.map_list.currentItemChanged.connect(self.update_preview)
        l_layout.addWidget(self.map_list)
        l_layout.addWidget(QPushButton("Dodaj do ulubionych"))

        right_frame = QWidget()
        r_layout = QVBoxLayout(right_frame)
        r_layout.addWidget(QLabel("Podgląd graficzny"))
        self.preview_label = QLabel("Brak podglądu")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px dashed gray; background: #f0f0f0;")
        self.preview_label.setMinimumSize(360, 280)
        r_layout.addWidget(self.preview_label)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_frame)
        splitter.setStretchFactor(1, 2)
        v.addWidget(splitter)

        search_h = QHBoxLayout()
        search_h.addWidget(QLabel("Wyszukaj po opisie:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("np. rzeka lawy")
        self.search_input.returnPressed.connect(self.perform_search)
        search_h.addWidget(self.search_input)

        search_h.addWidget(QLabel("Ile wyników:"))
        self.spin_limit = QSpinBox()
        self.spin_limit.setRange(1, 100)
        self.spin_limit.setValue(5)
        self.spin_limit.setToolTip("Ile najlepiej dopasowanych obrazków pokazać?")
        search_h.addWidget(self.spin_limit)
        
        self.btn_search = QPushButton("Szukaj")
        self.btn_search.clicked.connect(self.perform_search)
        search_h.addWidget(self.btn_search)
        v.addLayout(search_h)


    def scan_folder(self):
        if not self.logic:
            QMessageBox.critical(self, "Błąd", "Model AI nie jest załadowany!")
            return

        folder = QFileDialog.getExistingDirectory(self, "Wybierz folder z mapami")
        if not folder:
            return

        self.current_folder = folder
        
        cache_file_path = os.path.join(folder, "map_index.pkl")
        self.cache_data = {}

        if os.path.exists(cache_file_path):
            try:
                with open(cache_file_path, "rb") as f:
                    self.cache_data = pickle.load(f)
                print(f"Załadowano indeks: {len(self.cache_data)} map.")
            except Exception as e:
                print(f"Błąd odczytu cache (tworzę nowy): {e}")

        valid_ext = ('.jpg', '.jpeg', '.png', '.webp')
        files_on_disk = [f for f in os.listdir(folder) if f.lower().endswith(valid_ext)]
        files_set = set(files_on_disk)
        
        cached_set = set(self.cache_data.keys())
        
        new_files = list(files_set - cached_set)
        deleted_files = list(cached_set - files_set)

        if deleted_files:
            print(f"Usuwam {len(deleted_files)} nieistniejących plików z indeksu...")
            for f in deleted_files:
                del self.cache_data[f]

        if new_files:
            self.btn_scan.setText(f"Przetwarzanie {len(new_files)} nowych...")
            self.btn_scan.setEnabled(False)
            self.repaint()

            try:
                for idx, filename in enumerate(new_files):
                    full_path = os.path.join(folder, filename)
                    vector = self.logic.process_image(full_path)
                    
                    self.cache_data[filename] = vector
                    
                    if idx % 5 == 0:
                        self.btn_scan.setText(f"Przetwarzanie {idx}/{len(new_files)}...")
                        self.repaint()
                
                with open(cache_file_path, "wb") as f:
                    pickle.dump(self.cache_data, f)
                print("Zapisano zaktualizowany indeks na dysku.")

            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Błąd indeksowania: {e}")
            finally:
                self.btn_scan.setText("Skanuj folder")
                self.btn_scan.setEnabled(True)
        else:
            print("Brak nowych plików. Używam danych z cache.")

        self.rebuild_search_index()
        
        QMessageBox.information(self, "Gotowe", 
            f"Baza gotowa.\nRazem map: {len(self.cache_data)}\n"
            f"(Nowych: {len(new_files)}, Usuniętych: {len(deleted_files)})")

    def rebuild_search_index(self):
        """Konwertuje słownik cache na macierze numpy do szukania"""
        self.map_list.clear()
        self.image_paths = []
        embeddings_list = []

        if not self.cache_data:
            return

        for filename, vector in self.cache_data.items():
            full_path = os.path.join(self.current_folder, filename)
            
            self.image_paths.append(full_path)
            embeddings_list.append(vector)
            
            self.map_list.addItem(filename)

        if embeddings_list:
            self.embeddings_np = np.vstack(embeddings_list)

    def perform_search(self):
        query = self.search_input.text()
        if not query or self.embeddings_np is None:
            return

        try:
            text_vec = self.logic.process_text(query)
            
            scores = (text_vec @ self.embeddings_np.T).squeeze()
            if scores.ndim == 0: 
                scores = np.array([scores])
            
            sorted_indices = scores.argsort()[::-1]

            limit = self.spin_limit.value()
            top_indices = sorted_indices[:limit]

            self.map_list.clear()
            for idx in top_indices:
                score = scores[idx]
                path = self.image_paths[idx]
                name = os.path.basename(path)
                
                item = QListWidgetItem(f"[{score:.2f}] {name}")
                item.setData(Qt.UserRole, path)
                self.map_list.addItem(item)

            if self.map_list.count() > 0:
                self.map_list.setCurrentRow(0)

        except Exception as e:
            print(f"Błąd szukania: {e}")

    def update_preview(self, current_item, previous_item):
        if not current_item: 
            return
        path = current_item.data(Qt.UserRole)

        if not path and self.current_folder:
            text = current_item.text()
            if "]" in text: 
                text = text.split("] ", 1)[1]
            path = os.path.join(self.current_folder, text)

        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            scaled = pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled)


def build() -> QWidget:
    return BattlemapsWidget()