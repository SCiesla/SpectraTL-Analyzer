# SpectraTL-Analyzer : Program analizujący widma termoluminescencyjne 
![](https://github.com/SCiesla/SpectraTL-Analyzer/blob/main/images/Start.png)
## Cel programu

Program powstał, aby ułatwić analizę T_max T_stop szerzej opisaną w literaturze [1]. Procedurę termicznego oczyszczania (Tmax-Tsop) można skrótowo opisać ogrzewaniem materiału do pewniej temperatury T_stop (w celu uwolnienia elektronów z pułapek sieci krystalicznej) i następnie przystępuje się do wykonania widma termoluminescencji (TL). Temperatury T_stop zmieniają się np. od 50oC do 200oC z krokiem 10oC. 

Powoduje to utworzenie dużej ilości widm do analizy przez co ta procedura staje się czasochłonna i często jest pomijana przez badaczy. 

**Program powstał w celu przyśpieszenia i zautomatyzowania analizy widm** z wykorzystaniem języka Python wraz z kilkoma bibliotekami (Pandas, Numpy, Matplotlib). 

## Funkcje

1. Organizacja plików otrzymanych z aparatury pomiarowej = Selekcja i wybór odpowiedmich danych a następnie zapisywanie danych uporządkowanych do osobnego pliku  
