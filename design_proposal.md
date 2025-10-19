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
| 4           | 20.10 – 26.10.2025      |                |
| 5           | 27.10 – 02.11.2025      |                |
| 6           | 03.11 – 09.11.2025      |                |
| 7           | 10.11 – 16.11.2025      |                |
| 8           | 17.11 – 23.11.2025      |                |
| 9           | 24.11 – 30.11.2025      |                |
| 10          | 01.12 – 07.12.2025      |                |
| 11          | 08.12 – 14.12.2025      |                |
| 12          | 15.12 – 21.12.2025      |                |
| 13          | 22.12 – 28.12.2025      |                |
| 14          | 29.12.2025 – 04.01.2026 |                |
| 15          | 05.01 – 11.01.2026      |                |
| 16          | 12.01 – 18.01.2026      |                |

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
        - tensorflow
        - PyMuPDF
        - Pillow
        - google-api-python-client + google-auth
        - pytest
    - Flake8
    - Black
    - venv


## Zakres eksperymentów

- Przygotowanie danych
    - Zebranie danych (obrazy z podpisami będącymi krótkimi opisami)
    - Czyszczenie i standaryzacja danych
    - Przygotowanie danych syntetycznych przy pomocy zewnętrznego modelu do stworzenia opisów obrazów
- Przetestowanie różnych modeli i porównanie ich jakości przy pomocy metryk (np. podobieństwo cosinusowe)
- Integracja z aplikacją
    - Testy obciążeniowe
    - Testy użyteczności
- Testy jednostkowe

## Bibliografia