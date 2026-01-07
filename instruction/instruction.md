# Narrion Assystent mistrza gier RPG

Narzędzie wspierające Mistrzów Gry podczas sesji RPG. Aplikacja pomaga zarządzać informacjami o świecie gry, postaciach i wydarzeniach, a jednocześnie usprawnia organizację sesji i rozgrywkę - zarówno podczas przygotowań, jak i w trakcie samej sesji.

## Wymagania
Przed uruchomienie aplikacji należy się upewnić, że posiadamy zainstalowane:

- Python **3.12**
- UV
- Make

## Instalacja

1. Sklonowanie repozytorium
```bash
git clone https://github.com/masadows/Narrion.git
cd Narrion
```

2. Instalacja zależności
```bash
make requirements.txt
```

3. (Optional) Konfiguracja kalendarza

    1. Stworzenie własnego tokena dostępu do Google API:
    [Google API docs]()
    2. Skopiuj uzyskany plik `credentials.json` do katalogu `Narrion/data`

3. Uruchomienie aplikacji
```bash
make run
```

## Uruchamianie testów
To run tests use command:
```bash
make test
```

## Instrukcja korzystania z aplikacji
### Tworzenie kampanii
1. Wchodzimy w zakładkę `Kampanie RPG`.
2. Wybieramy `Nowa kampania`.
3. Wpisujemy nazwę kampanii w polu tekstowym.
4. Zatwierdzamy przyciskiem `Ok`.
5. Aby wejść do informacji związanych z daną kampanią, dwukrotnie na nią klikamy.

### Przemieszczanie się po kampanii
Aby wyjść z kampanii i wybrać inną, należy użyć przycisku `Wróć do listy kampanii`.

W naszej kampanii mamy 3 bazowe zakładki:
- Notatki - zawierają wszystkie notatki związane z daną kampanią, umożliwiają tworzenie, edycję oraz usuwanie notatek. Każda notatka może zawierać różne elementy:
    - tekst - pozwala na notowanie informacji
    - obraz - umożliwia dołączenia obrazu
    - checkbox - pozwala tworzyć listę z checkboxami
    - tabela - prosta tabela z wierszami i kolumnami
    - oś czasu - pozwala łatwiej śledzić chronologię wydarzeń

- Gracze - Zakładka pozwalająca na dodawanie graczy biorących udział w rozgrywce
- Baza NPC - Zakładka umożliwiająca zarządzanie NPC'ami
