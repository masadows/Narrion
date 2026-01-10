# Analiza modeli ML (tekst-obraz)
Nasza aplikacja pozwala na wyszukiwanie map po ich opisie w języku naturalnym.
Jest to możliwe dzięki wykorzystaniu modeli uczenia maszynowego, które potrafią przekształcić zarówno obrazy, jak i teksty na wektory we wspólnej przestrzeni wielowymiarowej.

## Analizowane modele
W ramach projektu wyselekcjonowaliśmy modele, poddając je ocenie pod kątem ich przydatności do naszego zastosowania oraz możliwości sprzętowych.
Poniżej znajduje się lista rozważanych modeli wraz z krótkimi opisami:
- **EmbeddingGemma**
    - [model](https://huggingface.co/headwAI/embeddinggemma-300m)
    - [artykuł](https://arxiv.org/pdf/2509.20354)
    - Koder tekstu opracowany przez Google na podstawie modelów Gemini, zoptymalizowany pod kątem wydajności w środowiskach o ograniczonych zasobach. Model ten jest zaprojektowany do generowania wysokiej jakości osadzeń tekstowych przy niskim zużyciu pamięci i mocy obliczeniowej.
- **TinyBERT**
    - [model](https://huggingface.co/huawei-noah/TinyBERT_General_4L_312D)
    - [artykuł](https://arxiv.org/pdf/1909.10351)
    - Koder tekstu będący zdestylowaną wersją modelu BERT. TinyBERT jest znacznie mniejszy (7.5 razy) i szybszy (9.4 razy) niż oryginalny BERT, oferując jednocześnie zbliżoną jakość rozumienia języka naturalnego (96.8%).
- **distilBERT**
    - [model](https://huggingface.co/docs/transformers/model_doc/distilbert)
    - [artykuł](https://arxiv.org/pdf/1910.01108)
    - Koder tekstu będący zdestylowaną wersją modelu BERT, który jest o 40% mniejszy i o 60% szybszy, zachowując przy tym 97% zdolności rozumienia języka oryginalnego modelu.
- **MobileViT**
    - [model](https://huggingface.co/docs/transformers/v4.21.3/en/model_doc/mobilevit)
    - [artykuł](https://arxiv.org/pdf/2110.02178)
    - Lekki koder obrazów zaprojektowany z myślą o zastosowaniach na urządzeniach mobilnych. MobileViT łączy cechy konwolucyjnych sieci neuronowych (CNN) i Transformerów (ViT), umożliwiając efektywne przetwarzanie obrazów przy ograniczonych zasobach obliczeniowych. Na zbiorze ImageNet-1k model MobileVit osiąga dokładność top-1 na poziomie 78.4% przy znacznie mniejszym rozmiarze i szybszym czasie inferencji w porównaniu do tradycyjnych modeli ViT. Jest to wynik o 3.2% lepszy niż MobileNetV3 (oparty o CNN) oraz o 6.2% lepszy niż DeIT (oprarty o ViT) - wszystkie trzy modele mają podobną liczbę parametrów.
- **EfficientNet**
    - [model](https://huggingface.co/docs/transformers/en/model_doc/efficientnet)
    - [artykuł](https://arxiv.org/pdf/1905.11946)
    - Koder obrazów znany z wysokiej dokładności i efektywności oraz skalowalności. Wersja B7 modelu EfficientNet osiąga 84.3% dokładności top-1 na zbiorze ImageNet, będąc jednocześnie 8.4 razy mniejsza i 6.1 razy szybsza niż tradycyjne konwolucyjne sieci neuronowe (ConvNet).
- **ResNet50**
    - [model](https://huggingface.co/microsoft/resnet-50)
    - [artykuł](https://arxiv.org/pdf/1512.03385)
    - Koder obrazów oparty na architekturze ResNet, która wprowadza pojęcie "residual learning" (uczenie resztkowe) poprzez zastosowanie połączeń skrótowych (shortcut connections). ResNet50, składający się z 50 warstw, jest szeroko stosowany w zadaniach związanych z rozpoznawaniem obrazów i osiąga wysoką dokładność na różnych benchmarkach.
- **CLIP**
    - [model](https://huggingface.co/docs/transformers/model_doc/clip)
    - [artykuł](https://arxiv.org/pdf/2103.00020)
    - Model łączący koder tekstu i obrazów, umożliwiający efektywne wyszukiwanie obrazów na podstawie opisów tekstowych. CLIP jest szeroko stosowany w zadaniach związanych z multimodalnym uczeniem maszynowym. Został on wytrenowany poprzez kontrastowe uczenie na ogromnym zbiorze danych składającym się z par obraz-tekst, co oznacza, że reprezentacje obrazów i odpowiadające im opisy tekstowe są mapowane na podobne wektory w przestrzeni.

## Zbiór danych
Do trenowania i oceny modeli wykorzystaliśmy zbiór danych składający się z obrazów battlemap wraz z odpowiadającymi im krótkimi oraz długimi opisami tekstowymi.
Zbiór danych został zebrany z różnych źródeł internetowych oraz uzupełniony o syntetycznie wygenerowane opisy przy pomocy zewnętrznego modelu generującego tekst na podstawie obrazów - [Qwen2-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct).
- [Zbiór map (1.57k) z krótkimi opisami](https://huggingface.co/datasets/nishanthc/dnd_map_dataset_v0.1)
- [Zbiór map (202) z długimi opisami](https://huggingface.co/datasets/Angry-Wizard/rpg_grid_maps)
- [Zbiór map z nazwami plików jako opisami](https://drive.google.com/drive/folders/1QiBxKfHjNdYvmuw6mMfigqunJZrn50QH)

W ten sposób powstał zbiór danych zawierający 4957 obrazów wraz z odpowiadającymi im krótkimi oraz długimi opisami tekstowymi.
Został on podzielony na zbiór treningowy (80%), walidacyjny (10%) oraz testowy (10%).
Notebook z przygotowaniem zbioru danych znajduje się w folderze `notebooks` pod nazwą `Dataset_processing.ipynb`.

## Testowanie modeli
Różne konfiguracje modeli zostały dotrenowane na przygotowanym zbiorze danych (wymiennie stosując krótkie lub długie opisy), a następnie przetestowane. Notebooki z eksperymentami znajdują się w folderze `notebooks`.
- CLIP - [notebook](notebooks/CLIP_experiments.ipynb)
- EmbeddingGemma-MobileViT - [notebook](notebooks/EmbeddingGemma_MobileViT_experiments.ipynb)
- TinyBERT-EfficientNet - [notebook](notebooks/TinyBERT_EfficientNet_experiments.ipynb)
- distilBERT-ResNet50 - [notebook](notebooks/distilBERT_ResNet50_experiments.ipynb)

### Wyniki eksperymentów
Poniżej przedstawiamy podsumowanie wyników uzyskanych przez poszczególne modele po trenowaniu na naszym zbiorze danych:
| Model                      | Loss       | Image Retrieval Accuracy | Text Retrieval Accuracy |
|----------------------------|------------|--------------------------|-------------------------|
| bazowy CLIP                | 2.6953     | 33.01%                   | 40.82%                  |
| **dotrenowany CLIP**       | **1.1513** | **68.16%**               | **68.55%**              |
| EmbeddingGemma-MobileViT   | 1.5858     | 52.02%                   | 48.59%                  |
| TinyBERT-EfficientNet      | 2.2046     | 28.83%                   | 27.82%                  |
| distilBERT-ResNet50        | 2.687      | 25.8%                    | 20.8%                   |

## Wybór modelu do aplikacji
Na podstawie przeprowadzonych eksperymentów wybraliśmy model CLIP jako najbardziej odpowiedni do naszego zastosowania.
Model ten osiągnął najlepsze wyniki pod względem dokładności wyszukiwania obrazów na podstawie tekstu, co jest kluczowe dla funkcjonalności naszej aplikacji.
Dodatkowo w naszym osobistym odczuciu wyniki zwracane przez model CLIP były najbardziej zgodne z oczekiwaniami użytkowników.

## Integracja modelu z aplikacją
Model CLIP został zintegrowany z aplikacją i jest wykorzystywany do wyszukiwania battlemap na podstawie opisów tekstowych.
Integracja modelu z aplikacją została przeprowadzona w module `battlemaps`, gdzie zaimplementowano funkcje odpowiedzialne za przetwarzanie zapytań tekstowych oraz wyszukiwanie odpowiednich obrazów w bazie danych.