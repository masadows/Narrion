"""Battlemap Browser and Semantic Search GUI.

This module implements the main graphical interface for managing, indexing,
and searching RPG battlemaps. It acts as the frontend for the CLIP-based
semantic search engine, allowing users to:
- Scan directories for image files.
- Index images using the neural network (lazy-loaded).
- Perform text-to-image semantic searches (e.g., "snowy mountain").
- Manage a list of favorite maps.
"""

import os
import pickle
import json

import numpy as np
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta
from shiboken6 import isValid

from themes import DEFAULT_FONT
from widgets.color_wrapper import color
from widgets.scalable_image import ScalableImageLabel
from widgets.section_header import SectionHeader

from .model_logic import ModelLogic


@color
class BattlemapsWidget(QWidget):
    """Main widget for browsing and searching battlemaps.

    This class integrates the UI with the backend logic (`ModelLogic`).
    It handles file system operations, caching of vector embeddings,
    and the visual presentation of search results.

    Attributes:
        logic (ModelLogic | None): Instance of the AI logic handler. None until initialized.
        cache_data (dict): Dictionary mapping filenames to numpy embedding vectors.
        favorites (set): Set of file paths marked as favorites.
        current_folder (str | None): Path to the currently opened directory.
        image_paths (list): Parallel list to embeddings, storing full file paths.
        embeddings_np (np.ndarray | None): Matrix of all image embeddings for fast search.
    """

    def __init__(self):
        """Initialize the battlemap widget and load persistent data."""
        super().__init__()
        self.load_settings()

        self.logic = None
        self.cache_data = {}
        self.favorites = set()
        self.current_folder = None

        self.image_paths = []
        self.embeddings_np = None

        self.icon_star_solid = qta.icon("fa5s.star", color=DEFAULT_FONT["icon_color"])
        self.icon_star_outline = qta.icon("fa6.star", color=DEFAULT_FONT["icon_color"])
        self.icon_folder = qta.icon("fa5s.folder-open", color=DEFAULT_FONT["icon_color"])
        self.icon_search = qta.icon("fa5s.search", color=DEFAULT_FONT["icon_color"])
        self.icon_scan = qta.icon("fa5s.sync-alt", color=DEFAULT_FONT["icon_color"])
        self.icon_reset = qta.icon("fa5s.times", color=DEFAULT_FONT["icon_color"])
        self.icon_file = qta.icon("fa5s.image", color=DEFAULT_FONT["icon_color"])

        self.load_favorites()
        self.init_ui()

    def load_settings(self):
        with open("./data/settings.json", "r") as file:
            self.settings = json.load(file)

    def save_settings(self):
        with open("./data/settings.json", "w") as file:
            json.dump(self.settings, file, indent=4)

    def ensure_model_loaded(self) -> bool:
        """Lazy load the AI model logic.

        Checks if the model is already loaded. If not, attempts to initialize
        `ModelLogic`, which triggers ONNX session creation. Shows a wait cursor
        during loading.

        Returns:
            bool: True if model is loaded successfully (or was already loaded),
                False if initialization failed.
        """
        if self.logic is not None:
            return True

        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.logic = ModelLogic(model_folder="onnx-clip")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Błąd modelu", f"Nie udało się załadować modelu AI:\n{e}")
            self.logic = None
            return False
        finally:
            QGuiApplication.restoreOverrideCursor()

    def init_ui(self):
        """Set up the user interface layout and signals."""
        v = QVBoxLayout(self)
        v.setContentsMargins(4, 4, 4, 4)

        header = QHBoxLayout()
        header.addWidget(SectionHeader("Battlemapy"))
        header.addStretch()

        self.btn_scan = QPushButton("Skanuj folder")
        self.btn_scan.setIcon(self.icon_scan)
        self.btn_scan.clicked.connect(self.scan_folder)
        header.addWidget(self.btn_scan)
        v.addLayout(header)

        splitter = QSplitter(Qt.Horizontal)

        left_frame = QWidget()
        l_layout = QVBoxLayout(left_frame)

        list_header = QHBoxLayout()
        list_header.addWidget(QLabel("Lista map:"))

        self.btn_show_favs = QPushButton("Tylko ulubione")
        self.btn_show_favs.setIcon(self.icon_star_solid)
        self.btn_show_favs.setCheckable(True)
        self.btn_show_favs.clicked.connect(self.toggle_list_view)
        list_header.addWidget(self.btn_show_favs)

        l_layout.addLayout(list_header)

        self.map_list = QListWidget()
        self.map_list.currentItemChanged.connect(self.update_preview)
        l_layout.addWidget(self.map_list)

        self.btn_favorite_action = QPushButton("Dodaj do ulubionych")
        self.btn_favorite_action.setIcon(self.icon_star_outline)
        self.btn_favorite_action.clicked.connect(self.toggle_current_favorite)
        self.btn_favorite_action.setEnabled(False)
        l_layout.addWidget(self.btn_favorite_action)

        right_frame = QWidget()
        r_layout = QVBoxLayout(right_frame)
        r_layout.addWidget(QLabel("Podgląd graficzny"))
        self.preview_label = ScalableImageLabel("Wybierz mapę")
        self.preview_label.setMinimumSize(100, 100)
        r_layout.addWidget(self.preview_label)
        r_layout.setStretch(1, 1)

        self.btn_open_loc = QPushButton("Otwórz folder pliku")
        self.btn_open_loc.setIcon(self.icon_folder)
        self.btn_open_loc.clicked.connect(self.open_file_location)
        self.btn_open_loc.setEnabled(False)
        r_layout.addWidget(self.btn_open_loc)

        r_layout.addStretch()

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

        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(self.icon_reset)
        self.btn_reset.setToolTip("Wyczyść wyszukiwanie i pokaż wszystkie")
        self.btn_reset.setFixedWidth(30)
        self.btn_reset.clicked.connect(self.reset_view)
        search_h.addWidget(self.btn_reset)

        search_h.addWidget(QLabel("Ile wyników:"))
        self.spin_limit = QSpinBox()
        self.spin_limit.setRange(1, 100)
        self.spin_limit.setValue(self.settings.get("spin_limit"))
        self.spin_limit.valueChanged.connect(self.on_spin_limit_changed)
        self.spin_limit.setToolTip("Ile najlepiej dopasowanych obrazków pokazać?")
        search_h.addWidget(self.spin_limit)

        self.btn_search = QPushButton("Szukaj")
        self.btn_search.setIcon(self.icon_search)
        self.btn_search.clicked.connect(self.perform_search)
        search_h.addWidget(self.btn_search)
        v.addLayout(search_h)
        self.scan_folder(first_open=True)

    def load_favorites(self):
        """Load favorites set from a pickle file."""
        if os.path.exists("data/favorites.pkl"):
            try:
                with open("data/favorites.pkl", "rb") as f:
                    self.favorites = pickle.load(f)
            except Exception:
                self.favorites = set()

    def on_spin_limit_changed(self, value):
        self.settings["spin_limit"] = value
        self.save_settings()

    def save_favorites(self):
        """Save current favorites set to a pickle file."""
        try:
            with open("data/favorites.pkl", "wb") as f:
                pickle.dump(self.favorites, f)
        except Exception as e:
            print(f"Błąd zapisu ulubionych: {e}")

    def toggle_current_favorite(self):
        """Toggle the favorite status of the currently selected map.

        Updates the internal set, saves to disk, and refreshes the UI button state.
        If in 'Show Only Favorites' mode, removing an item removes it from the list.
        """
        item = self.map_list.currentItem()
        if not item:
            return

        path = item.data(Qt.UserRole)
        if not path:
            return

        if path in self.favorites:
            self.favorites.remove(path)
            self.btn_favorite_action.setText("Dodaj do ulubionych")
            self.btn_favorite_action.setIcon(self.icon_star_outline)

            if self.btn_show_favs.isChecked():
                row = self.map_list.row(item)
                self.map_list.takeItem(row)
        else:
            self.favorites.add(path)
            self.btn_favorite_action.setText("Usuń z ulubionych")
            self.btn_favorite_action.setIcon(self.icon_star_solid)

        self.save_favorites()
        self.update_list_item_appearance(item)

    def toggle_list_view(self):
        """Switch between showing all maps and showing only favorites."""
        if self.btn_show_favs.isChecked():
            self.show_only_favorites()
            self.btn_show_favs.setText("Pokaż wszystkie")
        else:
            self.rebuild_search_index()
            self.btn_show_favs.setText("Tylko ulubione")

    def show_only_favorites(self):
        """Filter the list widget to display only favorite items."""
        self.map_list.clear()
        if not self.favorites:
            self.map_list.addItem("(Brak ulubionych)")
            return

        for path in self.favorites:
            if os.path.exists(path):
                name = os.path.basename(path)
                item = QListWidgetItem(name)
                item.setIcon(self.icon_star_solid)
                item.setData(Qt.UserRole, path)
                self.map_list.addItem(item)
            else:
                pass

    def open_file_location(self):
        """Open the OS file explorer at the selected map's location."""
        item = self.map_list.currentItem()
        if not item:
            return
        path = item.data(Qt.UserRole)

        if path and os.path.exists(path):
            folder_path = os.path.dirname(path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        else:
            QMessageBox.warning(self, "Błąd", "Plik nie istnieje lub ścieżka jest błędna.")

    def reset_view(self):
        """Reset search filters and show all maps from the current folder."""
        self.search_input.clear()
        self.btn_show_favs.setChecked(False)
        self.btn_show_favs.setText("Tylko ulubione")

        if self.cache_data:
            self.rebuild_search_index()
        else:
            self.map_list.clear()

    def scan_folder(self, first_open = False):
        """Open a directory dialog and scan for images to index."""
        if not self.ensure_model_loaded():
            return
        
        if first_open:
            folder = self.settings.get("image_path")
        else:
            folder = QFileDialog.getExistingDirectory(self, "Wybierz folder z mapami")
        if not folder:
            return
        
        self.settings["image_path"] = folder
        self.save_settings()

        self.current_folder = folder

        cache_file_path = os.path.join(folder, "map_index.pkl")
        self.cache_data = {}

        if os.path.exists(cache_file_path):
            try:
                with open(cache_file_path, "rb") as f:
                    self.cache_data = pickle.load(f)
            except Exception as e:
                print(f"Błąd odczytu cache: {e}")

        valid_ext = (".jpg", ".jpeg", ".png", ".webp")
        files_on_disk = [f for f in os.listdir(folder) if f.lower().endswith(valid_ext)]
        files_set = set(files_on_disk)

        cached_set = set(self.cache_data.keys())

        new_files = list(files_set - cached_set)
        deleted_files = list(cached_set - files_set)

        if deleted_files:
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

            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Błąd indeksowania: {e}")
            finally:
                self.btn_scan.setText("Skanuj folder")
                self.btn_scan.setEnabled(True)

        self.rebuild_search_index()
        if not first_open:
            QMessageBox.information(
                self,
                "Gotowe",
                f"Baza gotowa.\nRazem map: {len(self.cache_data)}\n"
                f"(Nowych: {len(new_files)}, Usuniętych: {len(deleted_files)})",
            )

    def rebuild_search_index(self):
        """Prepare internal data structures for search and populate the UI list.

        Flattens the `cache_data` dictionary into `self.embeddings_np` (numpy array)
        for vectorized operations and populates the QListWidget with all maps.
        """
        self.map_list.clear()
        self.image_paths = []
        embeddings_list = []

        if not self.cache_data:
            return

        for filename, vector in self.cache_data.items():
            full_path = os.path.join(self.current_folder, filename)

            self.image_paths.append(full_path)
            embeddings_list.append(vector)

            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, full_path)

            if full_path in self.favorites:
                item.setIcon(self.icon_star_solid)
            else:
                item.setIcon(self.icon_file)

            self.map_list.addItem(item)

        if embeddings_list:
            self.embeddings_np = np.vstack(embeddings_list)

    def perform_search(self):
        """Execute semantic search based on text input.

        Computes the dot product (cosine similarity) between the text embedding
        of the query and the pre-computed image embeddings. Sorts results
        by score and updates the list widget to show the top matches.
        """
        query = self.search_input.text()
        if not query or self.embeddings_np is None or self.embeddings_np is None:
            return

        if not self.ensure_model_loaded():
            return

        self.btn_show_favs.setChecked(False)
        self.btn_show_favs.setText("Tylko ulubione")

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

                if path in self.favorites:
                    item.setIcon(self.icon_star_solid)
                else:
                    item.setIcon(self.icon_file)

                self.map_list.addItem(item)

            if self.map_list.count() > 0:
                self.map_list.setCurrentRow(0)

        except Exception as e:
            print(f"Błąd szukania: {e}")

    def update_preview(self, current_item: QListWidgetItem, previous_item: QListWidgetItem):
        """Handle selection changes in the list widget.

        Updates the `ScalableImageLabel` with the selected image and updates
        action buttons (Favorite/Open Location) based on the selection.

        Args:
            current_item (QListWidgetItem): The newly selected item.
            previous_item (QListWidgetItem): The previously selected item (unused).
        """
        if not current_item:
            self.btn_favorite_action.setEnabled(False)
            self.btn_open_loc.setEnabled(False)
            return

        path = current_item.data(Qt.UserRole)

        if not path and self.current_folder:
            text = current_item.text()
            if "] " in text:
                text = text.split("] ", 1)[1]
            path = os.path.join(self.current_folder, text)
            current_item.setData(Qt.UserRole, path)

        if path and os.path.exists(path):
            self.preview_label.set_image(path)

            self.btn_open_loc.setEnabled(True)
            self.btn_favorite_action.setEnabled(True)

            if path in self.favorites:
                self.btn_favorite_action.setText("Usuń z ulubionych")
                self.btn_favorite_action.setIcon(self.icon_star_solid)
            else:
                self.btn_favorite_action.setText("Dodaj do ulubionych")
                self.btn_favorite_action.setIcon(self.icon_star_outline)

    def update_list_item_appearance(self, item: QListWidgetItem):
        """Refresh the icon of a specific list item based on favorite status.

        Args:
            item (QListWidgetItem): The item to update.
        """
        path = item.data(Qt.UserRole)
        is_fav = path in self.favorites

        if is_fav:
            item.setIcon(self.icon_star_solid)
        else:
            item.setIcon(self.icon_file)

    def changeFontColor(self, icon_color: str):
        """Theme change callback to update icon colors.

        Args:
            icon_color (str): Hex code or name of the new color.
        """
        if isValid(self):
            self.icon_star_solid = qta.icon("fa5s.star", color=icon_color)
            self.icon_star_outline = qta.icon("fa6.star", color=icon_color)
            self.icon_folder = qta.icon("fa5s.folder-open", color=icon_color)
            self.icon_search = qta.icon("fa5s.search", color=icon_color)
            self.icon_scan = qta.icon("fa5s.sync-alt", color=icon_color)
            self.icon_reset = qta.icon("fa5s.times", color=icon_color)
            self.icon_file = qta.icon("fa5s.image", color=icon_color)

            self.btn_scan.setIcon(self.icon_scan)
            self.btn_show_favs.setIcon(self.icon_star_solid)
            self.btn_open_loc.setIcon(self.icon_folder)
            self.btn_reset.setIcon(self.icon_reset)
            self.btn_search.setIcon(self.icon_search)

            if self.btn_favorite_action.text() == "Dodaj do ulubionych":
                self.btn_favorite_action.setIcon(self.icon_star_outline)
            else:
                self.btn_favorite_action.setIcon(self.icon_star_solid)

            for i in range(self.map_list.count()):
                item = self.map_list.item(i)
                path = item.data(Qt.UserRole)

                if path in self.favorites:
                    item.setIcon(self.icon_star_solid)
                else:
                    item.setIcon(self.icon_file)


def build() -> QWidget:
    """Factory function to create the BattlemapsWidget.

    Returns:
        QWidget: A new instance of BattlemapsWidget.
    """
    return BattlemapsWidget()
