# SpectraTL-Analyzer : Program analizujący widma termoluminescencyjne 
![](https://github.com/SCiesla/SpectraTL-Analyzer/blob/main/images/Start.png)
## Cel programu

Program powstał, aby ułatwić analizę T_max T_stop szerzej opisaną w literaturze [1]. Procedurę termicznego oczyszczania (Tmax-Tsop) można skrótowo opisać ogrzewaniem materiału do pewniej temperatury T_stop (w celu uwolnienia elektronów z pułapek sieci krystalicznej) i następnie przystępuje się do wykonania widma termoluminescencji (TL). Temperatury T_stop zmieniają się np. od 50oC do 200oC z krokiem 10oC. 

Powoduje to utworzenie dużej ilości widm do analizy przez co ta procedura staje się czasochłonna i często jest pomijana przez badaczy. 

**Program powstał w celu przyśpieszenia i zautomatyzowania analizy widm** z wykorzystaniem języka Python wraz z kilkoma bibliotekami (Pandas, Numpy, Matplotlib). 

## Funkcje
### 1. INTiBS folder
1. Organizacja plików otrzymanych z aparatury pomiarowej poprzez selekcję i wybór odpowiedmich danych a następnie zapisanie ich do nowo utworzonych folderów.   
![](https://github.com/SCiesla/SpectraTL-Analyzer/blob/main/images/func1.png)
Każdy nowo utworzony plik ma nazwę odpowiadajacą temperaturze T_stop. 
Ponadto funkcja tworzy jeden połączony plik z danymi, który można wykorzsytać w dalszej analizie


### 2. Analysis

Analiza widm przebiega dla każdej temperatury T_stop. Na początku program ładuje odpowiednie dane i szuka pierwszego maksimum intensywności na widmie i odpowiadającą mu temperaturę (T_max). Przykłady działania funkcji wynajdywania pierwszego maksimum poniżej. 

![](https://github.com/SCiesla/SpectraTL-Analyzer/blob/main/images/T_stop__120_TSTOP.png)

Następnie wybierane są punkty odpowiadające 15% temperatury maksymalnej a wartości na osiach X i Y zostają przekształcone. Oś X => 1/kT a oś Y na Log(Int). 
![](https://github.com/SCiesla/SpectraTL-Analyzer/blob/main/images/T_stop__170_IRM_TI.png)

![](https://github.com/SCiesla/SpectraTL-Analyzer/blob/main/images/T_stop__200_IRM_lnkT.png)
Następnie zostaje przyfitowana funkcja liniowa dla odcinka niebędącego szumem. Wartość współczynnika kierunkowego tej prostej równa jest energii aktywacji w materiale. 

### 3. Zapis wyników

Dla każdej z tych serii widm powstaje wykres podsumowaujący ich energie aktywacji wraz z temperaturą maksymalną. 

![](https://github.com/SCiesla/SpectraTL-Analyzer/blob/main/images/TmaxTstopEnergy.png)
