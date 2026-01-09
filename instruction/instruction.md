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
### Wybieranie motywu
Możliwe jest zmienie motywu kolorystycznego aplikacji poprzez kliknięcie rozwijanej listy obok napisu `Motyw:` w lewym, górnym rogu aplikacji, a następnie wybranie interesującej nas opcji.

![Zmiana motywu](./images/motyw.png)
### Kampania
#### Tworzenie kampanii
1. Wchodzimy w zakładkę `Kampanie RPG`.
2. Wybieramy `Nowa kampania`.
3. Wpisujemy nazwę kampanii w polu tekstowym.
4. Zatwierdzamy przyciskiem `Ok`.
5. Aby wejść do informacji związanych z daną kampanią, dwukrotnie na nią klikamy.

![Kampania](./images/kampania.png)

#### Przemieszczanie się po kampanii
Aby wyjść z kampanii i wybrać inną, należy użyć przycisku `Wróć do listy kampanii`.

W naszej kampanii mamy 3 bazowe zakładki:
- Notatki - zawierają wszystkie notatki związane z daną kampanią, umożliwiają tworzenie, edycję oraz usuwanie notatek.
- Gracze - Zakładka pozwalająca na dodawanie graczy biorących udział w rozgrywce
- Baza NPC - Zakładka umożliwiająca zarządzanie NPC'ami

Widok kampanii:

![Widok kampanii](./images/widok_kampanii.png)

#### Notatki
Nową notatkę dodajemy korzystając z przycisku `Nowa notatka`, zostanie ona umieszczona w uprzednio wybranym przez z nas z drzewka folderze. Nowy folder możemy dodać przyciskiem `Nowy folder`.
Każda notatka może zawierać różne elementy:
- tekst - pozwala na notowanie informacji
- obraz - umożliwia dołączenia obrazu
- checkbox - pozwala tworzyć listę z checkboxami
- tabela - prosta tabela z wierszami i kolumnami
- oś czasu - pozwala łatwiej śledzić chronologię wydarzeń

Element do notatki dodajemy, wybierając jeden z przycisków znajdujących się na dole okna. Po wybraniu przycisku w oknie pojawia się nowy element, który możemy edytować. Nowo dodany element zostaje umieszczony na końcu notatek. Elementem możemy zarządzać korzystając z przycisków po prawej stronie, na górze elementu - możemy przesuwać je góra/dół lub usuwać.

![Notatki](./images/notatki.png)

#### Gracze oraz NPC
Obsługa Graczy oraz NPC'ów jest analogiczna.
Aby dodać nową postać, w odpowiednim oknie wybieramy przycisk `Dodaj`, ukaże się nam wtedy okno, do którego musimy wprowadzić nazwę gracza/NPC'a. Edytować ich można wybierając danego z listy po lewo i wpisując jego parametry:
- HP
- AC
- Krótki opis
- Opis

### Battlemapy
Zakładka `Battlemapy` pozwala na łatwe wyszukiwanie interesującej nas mapy ze zbioru.

Aby skorzystać z wyszukiwarki, korzystamy z przyisku `Skanuj folder`. Przy pierwszym uruchomieniu należy poczekać, aż zostanie pobrany model odpowiezialny za analizę obrazów. Po załadowaniu obrazu otwarte zostanie okno, pozwalające na wybranie folderu zawierającego nasze battlemapy. Po otwarciu folderu, możemy skorzystać z wyszukiwarki. Na dole okna należy wpisać jaka mapa nas interesuje np. "rzeka lawy". Następnie wybieramy ile wyników chcemy dostać i przyciskamy `Szukaj`. Model zwróci nam `n` obrazów najbardziej pasujących do naszej frazy. Następnie możemy wybrać obraz i skorzystać z `Otwórz folder pliku`, dzięki czemu łatwo odnajdziemy w folderze nasz obraz.

![Battlemapy](./images/battlemapy.png)

### Terminarz
Terminarz jest oknem pozwalającym na łatwe zapisywanie naszych eventów do kalendarza google oraz ich odczytywania. Po wejściu do tej zakładki wyświetlony zostanie kalendarz, z zaznaczonymi na zielono dniami, w które odbywają się stworzone przez nas eventy. Listę eventów możemy wyświetlić po prawej stronie, klikając na dany dzień. Event można usunąć, wybierając go z listy po prawo, a następnie przyciskając `Usuń wydarzenie`. Nowy event dodajemy wybierając `Dodaj wydarzenie`, a następnie uzupełniając jego tytuł oraz datę. Po dodaniu wydarzenia kalendarz się odświeży, a wydarzenie będzie już dodane do kalendarza Google. Przemieszczać się po kalendarzu możemy za pomocą strzałek lub wybierając konkretny, interesujący nas miesiąc.

![Terminarz](./images/terminarz.png)

### Kości
Wybierając zakładkę `Kości` nasze okno aplikacji zostaje podzielone i po prawej stronie pojawia się interfejs pozwalający na rzucanie kośćmi. Po równoległym otwarciu `Kości` i `Trackera` możliwe jest ich przeciąganie i różne umieszczanie w oknie po prawo. Zakładka ta umożliwia rzucanie różnego rodzaju kośćmi:
- 2-ścienną,
- 4-ścienną,
- 8-ścienną,
- 10-ścienną,
- 12-ścienną,
- 20-ścienną,
- 100-ścienną.
oraz dodawanie do wyniku bonusu. Możliwe jest również rzucanie wieloma kośćmi na raz.

Aby dodać daną kość do rzutu, wystarczy na nią kliknąć. W okienku poniżej wyświetli się napis pokazujący jaką kość wybraliśmy. Napis jest skonstruowany w formie: `xdy`, gdzie `x` oznacza liczbę kostek danego typu, `d` jest separatorem, a `y` oznacza ilość ścian kostki, np.

`2d20` - oznacza rzut 2 kostkami o 20 ścianach.

Możliwe jest też ustalenie bonusu, który w oknie wyświetla się jako `+z`, gdzie z to ilość punktów dodanych do wyniku. Aby rzucić kośćmi wybieramy przycisk `Rzuć!`. W oknie na górze pojawi się wynik w formacie np. dla rzutu `2d2 + 1d4 + 1`:

`Rzut 2d2+1d4+1: [[2, 1], [4]] => 8` - czyli:
- `[2, 1]` - dla 2 kości 2 ściennych wynikami jest 2 oraz 1
- `[4]` - dla 1 kości 4 ściennej wynikiem jest 4
- `8` - wynikiem rzutu jest 9, ponieważ 2+1+4+bonus(1) = 8

Aby użyć innych kości, należy wybrać przycisk `RESET` i znów wybrać kości, których chcemy użyć.

![Alt text](./images/kosci.png)

### Tracker inicjatywy
Wybierając `Tracker`, podobnie jak okno `Kości`, zostaje on wyświetlony po prawej stronie naszego okna aplikacji. Możliwe jest dostosowanie położenia obydwu modułów w oknie po prawo, poprzez ich przeciąganie. `Tracker` służy do monitorowania kolejności akcji graczy oraz NPC'ów. Postacie dodajemy do trackera za pomocą przycisku `+`. Wyświetlone zostanie okno, w którym musimy wybrać do jakiej kampanii i jaką postać chemy dodać. Możemy również od razu dodać nową, wcześniej nie stworzną postać, poprzez wybranie przycisku `Dodaj postać ręcznie`. Następnie musimy ustalić wartość inicjatywy dla nowo dodanej postaci. Domyślnie postać jest dodawana ze statustem `Żywy`. Po dodaniu wszystkich postaci możemy wykonać ruch wybierając przycisk `->`. Podczas gry możemy edytować inicjatywę oraz status postaci, klikając dwukrotnie na ich wartość przy danej postaci. Postać ze statusem `Ogłuszone` lub `Martwy` zostanie pominięta w ruchu.

![Alt text](./images/tracker.png)