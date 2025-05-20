## Projekt Big Data – Analiza danych demograficznych

# Założenia projektu
Projekt polega na stworzeniu systemu analitycznego do pobierania, przetwarzania i analizy danych demograficznych (np. liczba ludności w krajach świata). Dane pobierane są z zewnętrznego API, następnie przetwarzane i zapisywane do bazy danych oraz plików pośrednich. Wyniki analizy prezentowane są w formie raportów tekstowych oraz wizualizacji (wykresy, mapy cieplne). Projekt umożliwia również eksport wyników do plików CSV, co ułatwia integrację z narzędziami BI.

# Struktura projektu
-  data/raw/ – surowe dane pobrane z API (JSON)
-  data/processed/ – przetworzone dane
-  output/figures/ – wygenerowane wykresy i mapy cieplne
-  output/reports/ – raporty tekstowe z analizy
-  output/csv/ – pliki CSV z danymi do dalszej analizy (np. w Excelu lub Power BI)
-  src/ – kod źródłowy (moduły do pobierania, przetwarzania, analizy i wizualizacji danych)
-  main.py – główny plik uruchamiający projekt


#   Instrukcja uruchomienia

  # 1. Zainstaluj wymagane biblioteki:
    pip install requests pandas matplotlib seaborn scikit-learn reportlab fpdf2 borb openpyxl


  # 2. Uruchom projekt:
    python main.py

  # 3. Wyniki znajdziesz w katalogach:

- Wykresy: output/figures/
- Raporty: output/reports/
- Pliki CSV: output/csv/

# Eksport do CSV
Wyniki analizy (np. dane do wykresów, tabele przestawne, top 5 krajów) są automatycznie - - zapisywane do plików CSV w katalogu output/csv/. Dzięki temu możesz łatwo zaimportować je do narzędzi BI (np. Power BI, Tableau, Excel) i przeprowadzić dalszą analizę lub wizualizację.

# Najważniejsze funkcjonalności
- Pobieranie danych z API i zapis do pliku JSON
- Przetwarzanie i czyszczenie danych
- Analiza statystyczna i prognozowanie (ML)
- Generowanie wykresów i map cieplnych
- Eksport wyników do raportów tekstowych i plików CSV
- Możliwość łatwej integracji z narzędziami BI
# Top 5 krajów
W raporcie oraz plikach CSV znajdziesz zestawienie top 5 krajów według wybranych kryteriów (np. - największy wzrost populacji).

# Dokumentacja
Kod jest opatrzony komentarzami i docstringami. Szczegółowe założenia oraz opis działania projektu znajdują się w tym pliku README.