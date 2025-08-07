# CSV-Magic

CSV-Magic ist eine IPython-Erweiterung, die das Jupyter Magic Command **csv** zur Verfügung stellt.
Der Inhalt der Zelle wird als CSV-Daten intepretiert und als Tabelle visualisiert.

## ToDo

- Deployen auf PyPi, dabei markdown-it-py dependency beachten!

## Initialisiserung im Jupyter Notebook 

``%load_ext csv`` zum Laden der Erweiterung

## Aufruf einer Aufgabe

```python
%%csv
a,b,c
1,2,3
4,"5,6",7.8
``` 