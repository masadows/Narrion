# Design proposal
## Temat
Narzędzie wspierające Mistrza Gry podczas prowadzenia sesji RPG.
Aplikacja ma usprawnić zarządzanie informacjami o świecie gry, postaciach i wydarzeniach, a także ułatwić organizację sesji i prowadzenie rozgrywki zarówno w czasie przygotowań, jak i podczas samej sesji.
## Harmonogram
| Nr tygodnia | Daty                    | Plan działania |
| ----------- | ----------------------- | -------------- |
| 1           | 29.10 – 05.10.2025      |        -       |
| 2           | 06.10 – 12.10.2025      |        -       |
| 3           | 13.10 – 19.10.2025      |        -       |
| 4           | 20.10 – 26.10.2025      | Kości, tracker inicjatywy, wstęp do notatek |
| 5           | 27.10 – 02.11.2025      | Przegląd modeli tekst-obraz, dodanie motywów aplikacji |
| 6           | 03.11 – 09.11.2025      | Prezentacja prototypu, Karty postaci/NPC |
| 7           | 10.11 – 16.11.2025      | Integracja kart postaci z trackerem, przetworzenie zbiorów do modeli |
| 8           | 17.11 – 23.11.2025      | Trenowanie i ewaluacja modeli |
| 9           | 24.11 – 30.11.2025      | Trenowanie i ewaluacja modeli |
| 10          | 01.12 – 07.12.2025      | Porównywanie modeli |
| 11          | 08.12 – 14.12.2025      | Integracja modelu z aplikacją |
| 12          | 15.12 – 21.12.2025      | Terminarz      |
| 13          | 22.12 – 28.12.2025      | Testy i poprawki aplikacji |
| 14          | 29.12.2025 – 04.01.2026 | Testy i poprawki aplikacji |
| 15          | 05.01 – 11.01.2026      | Testy i poprawki aplikacji |
| 16          | 12.01 – 18.01.2026      | Oddanie projektu |

## Funkcjonalność
 
1. Notatki
 
    - Tworzenie, edycja i organizacja notatek (foldery, tagi, wyszukiwanie).
    - Eksport/import notatek do pliku.
 
2. Karty postaci
 
    - Dodawanie i wyświetlanie kart postaci w formacie PDF.
    - Przypisywanie kart do graczy lub NPC.
 
3. Battlemapy
 
    - Zapisywanie ścieżek do plików z mapami.
    - Wyszukiwanie map po opisie dzięki lokalnemu modelowi ML (tekst–obraz).
    - Lista ulubionych map oraz podgląd graficzny.
 
4. Tracker inicjatywy
 
    - Zarządzanie kolejnością postaci w walce (gracze, potwory, NPC).
    - Edycja wartości inicjatywy
    - Zarządzanie statusem postaci (martwy, oszołomiony, żywy)
 
5. Rzut kośćmi
    - obsługa notacji rzutów (np. 1d20+5, 3d6+2).
    - możliwość rzutu wieloma kośćmi na raz.
 
6. Baza NPC
 
    - Tworzenie i przechowywanie NPC oraz potworów (karty postaci, opisy, rola w świecie).
 
7. Terminarz sesji
 
    - Planowanie terminów sesji wbudowanym kalendarzu.
    - Synchronizacja wydarzeń z Google Calendar.
 
## Stack technologiczny
- Python
    - biblioteki
        - Pyside6
        - QtAwesome
        - numpy
        - pytorch
        - datasets
        - transformers
        - PyMuPDF
        - Pillow
        - google-api-python-client + google-auth
        - pytest
    - narzędzia
      - uv
      - ruff

## Zakres eksperymentów

- Przygotowanie danych
    - Zebranie danych (obrazy z podpisami będącymi krótkimi opisami)
    - Czyszczenie i standaryzacja danych
    - Przygotowanie danych syntetycznych przy pomocy zewnętrznego modelu do stworzenia opisów obrazów
- Przetestowanie różnych modeli i porównanie ich jakości przy pomocy metryk (np. podobieństwo cosinusowe)
- Integracja z aplikacją
    - Testy obciążeniowe
    - Testy użytecznościowe - czy model zwraca sensowne wyniki z perspektywy użytkownika
- Testy jednostkowe


## Bibliografia
- [Zbiór map (1.57k) z krótkimi opisami](https://huggingface.co/datasets/nishanthc/dnd_map_dataset_v0.1)
- [Zbiór map (202) z długimi opisami](https://huggingface.co/datasets/Angry-Wizard/rpg_grid_maps)
- [Zbiór map z nazwami plików jako opisami](https://drive.google.com/drive/folders/1QiBxKfHjNdYvmuw6mMfigqunJZrn50QH)
- [PySide6](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html)

- [EmbeddingGemma-300m model](https://huggingface.co/headwAI/embeddinggemma-300m) 
- [EmbeddingGemma artykuł](https://arxiv.org/pdf/2509.20354) <-- model od Google będący koderem tekstu. Tworzony podobnie do modelów Gemini i dostosowany do śodowisk z limitowanymi zasobami.
- [TinyBERT model](https://huggingface.co/huawei-noah/TinyBERT_General_4L_312D)
- [TinyBERT artykuł](https://arxiv.org/pdf/1909.10351) <-- mały model będący koderem tekstu. Twórcy chwalą się, że jest 9.4 raza szybszy i 7.5 raza mniejszy niż podstawowy BERT jednocześnie osiągając zbliżone wyniki.
- [DistliBERT model](https://huggingface.co/docs/transformers/model_doc/distilbert)
- [DistliBERT artykuł](https://arxiv.org/pdf/1910.01108) <-- kolejna mniejsza wersja modelu BERT zmniejszająca rozmiar o 40% i przyspieszająca o 60% przy zachowaniu 97% rozumienia języka
- [CLIP model](https://huggingface.co/docs/transformers/model_doc/clip) 
- [CLIP artykuł](https://arxiv.org/pdf/2103.00020) <-- model łączący koder tekstu i obrazów
- [EfficientNet model](https://huggingface.co/docs/transformers/en/model_doc/efficientnet)
- [EfficientNet artykuł](https://arxiv.org/pdf/1905.11946) <-- koder obrazów. W pracy został zaproponowana nowa metoda skalowania, która w wersji B7 osiąga 84% top-1 dokładności na zbiorze ImageNet będąc przy tym 8.4 raza mniejszy i 6.1 raza szybszy niż ConvNet
- [MobileViT model](https://huggingface.co/docs/transformers/v4.21.3/en/model_doc/mobilevit)
- [MobileViT artykuł](https://arxiv.org/pdf/2110.02178) <-- mały koder obrazów dostosowany do zadań na telefonach
- [ConvNeXt](https://huggingface.co/facebook/convnextv2-nano-22k-384)
- [ConvNeXt](https://arxiv.org/pdf/2301.00808)