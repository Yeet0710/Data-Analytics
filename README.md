# Analyseprojekt: Zahlungsbereitschaft und Zahlungsarten in Deutschland

## Projektbeschreibung

Dieses Projekt untersucht, wie sich die Zahlungsbereitschaft in Deutschland in den letzten Jahren verändert hat. Im Mittelpunkt stehen dabei zwei Fragestellungen:

1. **Hat sich der durchschnittliche Warenkorbwert verändert?**
   → Analyse von Konsumausgaben und Umsätzen im Lebensmitteleinzelhandel sowie im Bereich Bekleidung und Nahrungsmittel, jeweils nominal und inflationsbereinigt.

2. **Welche Zahlungsarten gewinnen an Bedeutung?**
   → Analyse von Statistiken zu Zahlungsarten im stationären Einzelhandel (2016–2024) und im Online-Handel (2019–2023). Der Fokus liegt auf Trends wie dem Rückgang der Bargeldnutzung, dem Anstieg von Kartenzahlungen und der zunehmenden Bedeutung von E-Wallets sowie Buy Now Pay Later (BNPL).

## Datengrundlage

Die Auswertungen basieren auf öffentlich verfügbaren Statistiken (z. B. Statista, Studien zum Konsumverhalten). Eingesetzte Datensätze umfassen:

* Inflationsraten in Deutschland (2000–2024)
* Nettoumsätze im Lebensmitteleinzelhandel (2002–2023)
* Konsumausgaben privater Haushalte für Bekleidung und Nahrungsmittel (1991–2024)
* Umsatzentwicklung im Einzelhandel (2000–2025)
* Anteile von Zahlungsarten im Einzelhandel (2016–2024)
* Umfragen zu bevorzugten Online-Zahlungsarten (2019, 2021, 2023)

## Methodik

* Einlesen und Bereinigung der Daten mit **pandas**
* Berechnung inflationsbereinigter Werte anhand der Konsumentenpreisindizes
* Visualisierung von Trends mit **matplotlib**
* Vergleich nominaler und realer Entwicklungen zur Unterscheidung zwischen Preissteigerung und tatsächlichem Konsumzuwachs
* Zusammenführung von Zeitreihen stationärer und digitaler Zahlungsarten

## Ergebnisse (Kurzfassung)

* **Warenkorbwert**: Nominal deutlich gestiegen, real jedoch nur moderat. Stabile bis steigende Zahlungsbereitschaft für Lebensmittel, stagnierend bis rückläufig bei Bekleidung.
* **Zahlungsarten**: Bargeld verliert, Kartenzahlungen und E-Wallets gewinnen. BNPL bleibt in Deutschland weiterhin stark genutzt.

## Ziel des Projekts

Das Projekt liefert eine datenbasierte Antwort auf die übergeordnete Forschungsfrage:
**„Wie hat sich die Zahlungsbereitschaft in Deutschland in den letzten fünf Jahren verändert?“**
Es kombiniert ökonomische Daten mit Verbraucherumfragen und zeigt, wie sich sowohl die Höhe der Ausgaben als auch die bevorzugten Zahlungsarten verschoben haben.
