# JUDO i-soft PRO / PRO L – Home Assistant Integration

Lokale Home-Assistant-Integration für JUDO i-soft PRO und i-soft PRO L über die REST-Schnittstelle des Connectivity-Moduls.

## Enthalten

- Gesamtwassermenge und Weichwassermenge in **m³**
- Salzgewicht in **kg**
- Salzreichweite in Tagen
- Wunschwasserhärte
- Härteeinheit als Dropdown (`°dH` / `°fH`)
- Salzmangel-Warnschwelle
- maximale Entnahmedauer
- maximale Entnahmemenge
- maximaler Volumenstrom
- Szenenauswahl als Dropdown
- Szenendauer als Dropdown
- Szene aktivieren
- Regeneration starten
- Leckageschutz öffnen / schließen
- Software-Version korrekt dekodiert
- Gerätetyp-Erkennung für `0x58`, `0x4B`, `0x4C`
- vorbereitete `6900`-Abfrage
- fertiges Lovelace-Dashboard `dashboard.yaml`

## Abfragekonzept

Alle REST-Anfragen laufen über eine zentrale Warteschlange. Es wird nie mehr als ein Kommando pro Sekunde gestartet. Die Grundwerte werden alle 10 Minuten gelesen. Schlägt eine einzelne Abfrage fehl, bleibt der letzte erfolgreiche Wert im Cache erhalten.

Nach Änderungen an Einstellungen wird der betreffende Read-Befehl fünf Sekunden später erneut abgefragt.

## REST-Befehle

Für die dokumentierten PRO-/PRO-L-Funktionen werden unter anderem verwendet:

| Funktion | Read | Write |
|---|---:|---:|
| Wunschwasserhärte | `5100` | `30 00 + Wert` |
| Härteeinheit | `2300` | `24 00 + Einheit` |
| Salzvorrat | `5600` | `56 00 + Gramm` |
| Salzmangel-Warnung | `5700` | `57 00 + Tage` |
| Max. Entnahmedauer | `3E00` | `3E 00 + Minuten` |
| Max. Entnahmemenge | `3F00` | `3F 00 + Liter` |
| Max. Volumenstrom | `4000` | `40 00 + L/h` |
| Leckageschutz schließen | – | `3C00` |
| Leckageschutz öffnen | – | `3D00` |
| Regeneration | – | `350000` |
| Szene | – | `36 00 + Szene + Dauer` |
| Gesamtwasser | `2800` | – |
| Weichwasser | `2900` | – |
| Gerätetyp | `FF00` | – |
| Software-Version | `0100` | – |
| Inbetriebnahmedatum | `0E00` | – |
| Betriebsstunden | `2500` | – |
| Zukunftiges Gruppenkommando | `6900` | – |

## Gerätetypen

- `0x58` → i-soft PRO
- `0x4B` → i-soft PRO
- `0x4C` → i-soft PRO L

## Software-Version

Die drei Versionsbytes werden in der von JUDO dokumentierten Reihenfolge interpretiert. Beispiel: `0C0001` wird als `1.0.12` angezeigt.

## 6900

`6900` ist bereits Bestandteil der Abfrage und wird separat behandelt. Wenn die Anlage das Kommando noch nicht unterstützt, entsteht nur ein eigener Fehler für `6900`; die übrigen Abfragen laufen weiter.

Da für `6900` in der aktuell verfügbaren öffentlichen JUDO-PRO-Kommandotabelle noch keine feste Feld-/Bytebelegung dokumentiert ist, wird die Antwort momentan sicher und ohne erfundene Feldnamen ausgewertet als:

- Rohdaten HEX
- Byte-Anzahl
- alle 16-bit-Little-Endian-Werte
- alle 32-bit-Little-Endian-Werte

Sobald die exakte 6900-Felddefinition vorliegt, können diese Rohwerte eindeutig als z. B. Status, Durchfluss, Temperatur oder weitere Werte benannt und skaliert werden.

## Installation über HACS

Repository als benutzerdefiniertes Repository hinzufügen und als **Integration** installieren. Danach Home Assistant neu starten und die Integration über **Einstellungen → Geräte & Dienste → Integration hinzufügen** einrichten.

Beispiel:

- IP: `192.168.176.2`
- Port: `80`
- Benutzer: `admin`
- Passwort: `Connectivity`

## Dashboard

`dashboard.yaml` ist ein großes Beispiel-Dashboard mit Übersicht, Wasser-/Salzbereich, vollständiger Steuerung sowie einer eigenen 6900-/Diagnose-Seite. Die Karten verwenden ausschließlich Standard-Home-Assistant-Karten.

## Wichtiger Hinweis zu alten REST-Sensoren

Wenn die neue Integration verwendet wird, sollten alte parallele `rest:`-Sensoren für dieselbe JUDO-Anlage deaktiviert werden. Sonst laufen die Abfragen doppelt und die gewünschte Begrenzung auf maximal ein Kommando pro Sekunde wird außerhalb der Integration umgangen.

## Lizenz

MIT. Copyright (c) 2026 JUDO1936.
