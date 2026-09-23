# JUDO i-soft PRO / PRO L – Home Assistant Integration

<div align="center">

**Lokale Home-Assistant-Integration für JUDO i-soft PRO, i-soft PRO mit Leckageschutz und i-soft PRO L**

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-41BDF5?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistant&logoColor=white)](https://hacs.xyz/)
[![Version](https://img.shields.io/badge/version-2.5.51-00AEEF)](https://github.com/JUDO1936/judo-isoft_PRO-hacs)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

</div>

---

## Übersicht

Die **JUDO i-soft PRO / PRO L Integration** ermöglicht die lokale Einbindung von JUDO i-soft Enthärtungsanlagen in [Home Assistant](https://www.home-assistant.io/).

Die Kommunikation erfolgt direkt über die lokale REST-Schnittstelle des Connectivity-Moduls.

Es wird keine Cloud-Verbindung benötigt.

Die Integration wurde speziell darauf ausgelegt, die JUDO-Anlage möglichst schonend und zuverlässig abzufragen. Alle REST-Kommandos eines Gerätes werden über eine zentrale Warteschlange abgearbeitet.

Dadurch werden parallele REST-Anfragen vermieden und die Kommunikation auf **maximal ein gestartetes Kommando pro Sekunde und Gerät** begrenzt.

---

# Funktionen

## Überwachung

Die Integration stellt unter anderem folgende Werte zur Verfügung:

- Gesamtwassermenge
- Weichwassermenge
- Salzgewicht
- Salzreichweite
- Wunschwasserhärte
- aktuell eingestellte Härteeinheit
- Salzmangel-Warnschwelle
- maximale Entnahmedauer
- maximale Entnahmemenge
- maximaler Volumenstrom
- Software-Version
- Gerätetyp
- Device ID
- Betriebsstunden
- aktive Szene
- globaler Leckageschutzstatus
- Leckagegrund
- aktueller Wasserdurchfluss
- aktuelle Wassertemperatur

### Einheiten

| Wert | Einheit |
|---|---|
| Gesamtwasser | m³ |
| Weichwasser | m³ |
| Salzgewicht | kg |
| Salzreichweite | Tage |
| Wasserdurchfluss | L/h |
| Wassertemperatur | °C |
| Betriebsstunden | h |

---

# Steuerung

Die Integration stellt neben Sensoren auch native Home-Assistant-Steuerelemente bereit.

## Szenen

- Szene auswählen
- Szenendauer auswählen
- Szene aktivieren
- Regeneration starten

## Leckageschutz

- Leckageschutz schließen
- Leckageschutz öffnen
- globalen Leckageschutzstatus anzeigen
- Leckagegrund anzeigen

Es gibt bewusst keinen einfachen EIN/AUS-Schalter für den Leckageschutz.

Öffnen und Schließen sind getrennte Aktionen, damit die Bedienung eindeutig bleibt.

## Wasserhärte

- Wunschwasserhärte einstellen
- aktuelle Wunschwasserhärte anzeigen
- Härteeinheit auswählen

## Leckageschutz-Grenzwerte

Die folgenden Einstellungen werden als Home-Assistant-`number`-Entities bereitgestellt und können dadurch als Schieberegler verwendet werden:

- maximale Entnahmedauer
- maximale Entnahmemenge
- maximaler Volumenstrom

## Salz

- Salzvorrat anzeigen
- Salzvorrat einstellen
- Salzreichweite anzeigen
- Salzmangel-Warnschwelle einstellen

---

# Unterstützte Geräte

Die Integration unterstützt die dokumentierten Gerätetypen der JUDO i-soft PRO-Familie.

| Gerätecode | Gerät |
|---|---|
| `0x58` | JUDO i-soft PRO |
| `0x4B` | JUDO i-soft PRO |
| `0x4C` | JUDO i-soft PRO L |

Der Gerätetyp wird automatisch über das JUDO-REST-Kommando `FF` erkannt.

---

# Installation über HACS

## Voraussetzungen

- Home Assistant
- Home Assistant **2024.1 oder neuer**
- HACS
- JUDO i-soft PRO / PRO L mit erreichbarer lokaler REST-Schnittstelle

## Installation

### 1. HACS öffnen

In Home Assistant:

**HACS → Integrationen**

öffnen.

### 2. Repository suchen

Nach

```text
JUDO i-soft PRO / PRO L
```

suchen.

Falls das Repository noch nicht in HACS vorhanden ist, kann es als Custom Repository hinzugefügt werden:

```text
https://github.com/JUDO1936/judo-isoft_PRO-hacs
```

### 3. Integration installieren

Die Integration installieren und anschließend Home Assistant neu starten.

---

# Einrichtung

Nach dem Neustart:

**Einstellungen → Geräte & Dienste → Integration hinzufügen**

und

```text
JUDO i-soft PRO / PRO L
```

auswählen.

## Eingabefelder

Bei der Einrichtung werden folgende Daten abgefragt:

| Einstellung | Beispiel |
|---|---|
| Gerätename | `JUDO i-soft PRO Büro` |
| IP-Adresse | `192.168.176.2` |
| Port | `80` |
| Benutzername | `admin` |
| Passwort | `Connectivity` |

Der **Gerätename steht beim Einrichten an erster Stelle**.

Beispiel:

```text
Gerätename:
JUDO i-soft PRO Büro

IP-Adresse:
192.168.176.2

Port:
80

Benutzername:
admin

Passwort:
Connectivity
```

Nach dem Absenden wird zunächst versucht, die JUDO-Anlage zu erreichen.

Die Integration liest dabei unter anderem den Gerätetyp und die Device ID aus.

---

# Mehrere JUDO-Anlagen

Mehrere JUDO-Anlagen können unabhängig voneinander eingerichtet werden.

Beispiel:

| Home-Assistant-Gerät | IP-Adresse |
|---|---|
| JUDO i-soft PRO Büro | `192.168.176.2` |
| JUDO i-soft PRO Werkstatt | `192.168.176.3` |
| JUDO i-soft PRO L Keller | `192.168.176.4` |

Jede Anlage erhält einen eigenen Config Entry und ein eigenes Home-Assistant-Gerät.

Die Geräte können dadurch unabhängig voneinander überwacht und gesteuert werden.

---

# IP-Adresse und Verbindung

Die Kommunikation erfolgt direkt zur eingetragenen IP-Adresse.

Beispiel:

```text
http://192.168.176.2:80
```

Die Integration verwendet dabei die lokale REST-Schnittstelle der JUDO-Anlage.

Es ist keine Internetverbindung zur JUDO-Cloud erforderlich.

---

# IP-Adresse später ändern

Die Verbindungseinstellungen werden über den Home-Assistant-Config-Entry verwaltet.

Damit kann eine bestehende JUDO-Konfiguration angepasst werden, ohne die gesamte Integration neu installieren zu müssen.

Nach einer Änderung der Verbindungsdaten wird der Config Entry neu geladen.

> Hinweis: Die Unterstützung der nachträglichen Änderung einzelner Verbindungsparameter hängt von der aktuell installierten Version der Integration ab. Der Config Flow ist so aufgebaut, dass Konfigurationen über einen bestehenden Config Entry verwaltet werden.

---

# Device ID

Die JUDO Device ID wird über das REST-Kommando

```text
06
```

ausgelesen.

In Home Assistant wird sie als diagnostischer Sensor bereitgestellt:

```text
Device ID
```

Die Device ID wird außerdem beim Einrichten verwendet, um das physische JUDO-Gerät eindeutig zu erkennen.

---

# Kommunikationskonzept

Ein Schwerpunkt der Integration ist eine möglichst stabile Kommunikation mit der JUDO-Anlage.

## Maximal ein Kommando pro Sekunde

Für jedes konfigurierte Gerät gilt:

```text
max. 1 REST-Kommando / Sekunde
```

Die Kommandos werden nicht parallel an das Gerät gesendet.

Die Warteschlange gilt für:

- normale Leseabfragen
- Schreibbefehle
- Szenen
- Regeneration
- Leckageschutz-Aktionen
- Wiederholungsabfragen

## Regelmäßige Abfrage

Die normalen Werte werden grundsätzlich alle:

```text
10 Minuten
```

aktualisiert.

## Nachabfrage nach Änderungen

Bei bestimmten Einstellwerten wird nach einer Änderung zusätzlich eine erneute Abfrage durchgeführt.

Die vorgesehene Verzögerung beträgt:

```text
5 Sekunden
```

Dadurch kann Home Assistant nach einem Schreibvorgang kontrollieren, welchen Wert die JUDO-Anlage tatsächlich übernommen hat.

## Wiederholungen

Bei einem vorübergehenden Kommunikationsfehler wird der betreffende REST-Aufruf einmal wiederholt.

Die Wiederholung läuft ebenfalls durch die zentrale Befehlswarteschlange.

## Letzten gültigen Wert behalten

Ein einzelner fehlgeschlagener REST-Aufruf soll nicht sofort dazu führen, dass ein zuvor gültiger Messwert verschwindet.

Die Integration arbeitet deshalb mit den zuletzt erfolgreich empfangenen Werten.

Das ist insbesondere bei kurzen Netzwerkproblemen wichtig.

---

# Unterstützte REST-Kommandos

Die Integration verwendet die dokumentierten REST-Kommandos der JUDO i-soft PRO / PRO L.

| Funktion | Kommando |
|---|---|
| Wasserhärte lesen | `51` |
| Wasserhärte schreiben | `30` |
| Härteeinheit lesen | `23` |
| Härteeinheit schreiben | `24` |
| Salzvorrat / Reichweite | `56` |
| Salzmangel-Warnung | `57` |
| maximale Entnahmedauer | `3E` |
| maximale Entnahmemenge | `3F` |
| maximaler Volumenstrom | `40` |
| Leckageschutz schließen | `3C` |
| Leckageschutz öffnen | `3D` |
| Regeneration | `35` |
| Szene aktivieren | `36` |
| Gesamtwasser | `28` |
| Weichwasser | `29` |
| Gerätetyp | `FF` |
| Device ID | `06` |
| Software-Version | `01` |
| Betriebsstunden | `25` |
| Gerätestatus | `6900` |

---

# Wasserwerte

## Gesamtwassermenge

Das JUDO-Kommando:

```text
28
```

liefert die Gesamtwassermenge.

Die Integration wandelt den vom Gerät gelieferten Literwert in:

```text
m³
```

um.

## Weichwassermenge

Das Kommando:

```text
29
```

liefert die Weichwassermenge.

Auch dieser Wert wird in:

```text
m³
```

angezeigt.

---

# Salz

## Salzgewicht

Das Kommando:

```text
56
```

liefert unter anderem:

- Salzgewicht
- Salzreichweite

Das Salzgewicht wird in:

```text
kg
```

angezeigt.

## Salzreichweite

Die vom Gerät gelieferte Reichweite wird in:

```text
Tagen
```

angezeigt.

## Salzmangel-Warnschwelle

Die Warnschwelle wird über:

```text
57
```

gelesen und geschrieben.

In Home Assistant kann die Einstellung über eine `number`-Entity verändert werden.

---

# Wasserhärte

## Wunschwasserhärte

Die Wunschwasserhärte wird über:

```text
51
```

gelesen.

Zum Schreiben wird verwendet:

```text
30
```

In Home Assistant steht dafür eine `number`-Entity zur Verfügung.

## Härteeinheiten

Die JUDO-Dokumentation definiert folgende Einheiten:

| Code | Einheit |
|---:|---|
| `0` | °dH |
| `1` | °eH |
| `2` | °fH |
| `3` | gpg |
| `4` | ppm |
| `5` | mmol |
| `6` | mval |

Die Einheit kann über ein Home-Assistant-`select` ausgewählt werden.

---

# Leckageschutz

Die Integration unterscheidet zwischen:

1. dem aktuellen globalen Status
2. dem Leckagegrund
3. den Aktionen zum Öffnen und Schließen

Dadurch wird die tatsächliche Gerätesituation nicht mit einem künstlichen Home-Assistant-Schalter verwechselt.

---

# JUDO Gerätestatus – 6900

Das JUDO-Kommando:

```text
6900
```

liefert den aktuellen Gerätestatus.

Die Antwort enthält mehrere Datenfelder.

Die Integration dekodiert daraus gezielt die für Home Assistant relevanten Werte.

## Aktive Szene

Die aktive Szene wird aus dem Gerätestatus gelesen.

| Code | Szene |
|---|---|
| `0` | Alltag meistern |
| `1` | Körper pflegen |
| `2` | Garten bewässern |
| `3` | Urlaub genießen |
| `4` | Wäsche waschen |
| `5` | Hochdruckreinigen |
| `6` | Pool befüllen |
| `7` | Heizung befüllen |
| `8` | Custom Szene 1 |
| `9` | Custom Szene 2 |
| `A` | Custom Szene 3 |

## Aktueller Wasserdurchfluss

Der aktuelle Wasserdurchfluss wird aus dem 6900-Gerätestatus gelesen.

Anzeige in:

```text
L/h
```

Home Assistant Entity:

```text
Aktueller Wasserdurchfluss
```

## Wassertemperatur

Die aktuelle Wassertemperatur wird ebenfalls aus dem 6900-Gerätestatus gelesen.

Anzeige in:

```text
°C
```

Home Assistant Entity:

```text
Wassertemperatur
```

## Leckageschutzstatus

Der globale Leckageschutzstatus wird als Bitmaske übertragen.

Die dokumentierten Werte sind:

| Bit | Bedeutung |
|---:|---|
| `0x00` | deaktiviert |
| `0x01` | Volumenstrom |
| `0x02` | Menge |
| `0x04` | Zeit |
| `0x08` | Mikroleckageprüfung |
| `0x10` | Schließen bei Mikroleckage |
| `0x20` | externe Sensoren |

Die Integration dekodiert diese Bits und stellt einen verständlichen Sensorwert bereit.

## Leckagegrund

Der Leckagegrund wird ebenfalls aus einer Bitmaske dekodiert.

| Bit | Bedeutung |
|---:|---|
| `0x00` | kein Grund |
| `0x01` | Volumenstrom überschritten |
| `0x02` | Menge überschritten |
| `0x04` | Zeit überschritten |
| `0x08` | externer Kabelsensor |
| `0x10` | manuell geschlossen |
| `0x20` | manuelle Mikroleckage |
| `0x40` | automatische Mikroleckage |
| `0x80` | Homeguard-Meldung |

Bei mehreren gesetzten Bits werden die entsprechenden Informationen gemeinsam ausgewertet.

---

# Szenen

Die Szenen werden als Home-Assistant-`select` bereitgestellt.

## Szenenauswahl

```text
Alltag meistern
Körper pflegen
Garten bewässern
Urlaub genießen
Wäsche waschen
Hochdruckreinigen
Pool befüllen
Heizung befüllen
Custom Szene 1
Custom Szene 2
Custom Szene 3
```

# Szenendauer

Folgende Werte stehen zur Verfügung:

| JUDO-Wert | Anzeige |
|---|---|
| `000F` | 00:15 |
| `001E` | 00:30 |
| `002D` | 00:45 |
| `0100` | 01:00 |
| `0200` | 02:00 |
| `0600` | 06:00 |
| `0C00` | 12:00 |
| `FFFF` | Unbegrenzt |

Die Auswahl der Szene und der Dauer erfolgt getrennt.

Mit der Aktion **Szene aktivieren** werden beide Einstellungen an die JUDO-Anlage übertragen.

---

# Regeneration

Die manuelle Regeneration wird über das dokumentierte JUDO-Kommando:

```text
35
```

ausgelöst.

In Home Assistant steht dafür eine eigene Button-Entity zur Verfügung:

```text
Regeneration starten
```

---

# Leckageschutz öffnen / schließen

Die beiden Aktionen sind getrennt.

## Schließen

```text
3C
```

## Öffnen

```text
3D
```

In Home Assistant erscheinen dafür zwei Buttons:

```text
Leckageschutz schließen
Leckageschutz öffnen
```

Nach einer Aktion wird der Gerätestatus erneut abgefragt.

---

# Einstellbare Grenzwerte

## Maximale Entnahmedauer

JUDO-Kommando:

```text
3E
```

Einheit:

```text
Minuten
```

## Maximale Entnahmemenge

JUDO-Kommando:

```text
3F
```

Einheit:

```text
Liter
```

## Maximaler Volumenstrom

JUDO-Kommando:

```text
40
```

Einheit:

```text
L/h
```

---

# Dashboard

Das Repository enthält zusätzlich ein Beispiel-Dashboard:

```text
dashboard.yaml
```

Das Dashboard ist nach den folgenden Bereichen aufgebaut:

1. **Anlage & Infodaten**
2. **Szenen & Regeneration**
3. **Leckageschutz & Urlaubsmodus**
4. **Wasserhärte Einstellungen**
5. **Grenzwerte – Leckageschutz**
6. **Salzvorrat & Warnschwelle**
7. **Wasser & Verbrauch**
8. **Verlauf**

## Dashboard-Bereiche

### Anlage & Infodaten

Enthält:

- aktive Szene
- globaler Leckageschutz
- Gerätetyp
- Device ID
- Software-Version
- Betriebsstunden

### Szenen & Regeneration

Enthält:

- Szene
- Dauer
- Szene aktivieren
- Regeneration starten

### Leckageschutz

Enthält:

- globalen Status
- Leckagegrund
- schließen
- öffnen

### Wasserhärte

Enthält:

- Wunschwasserhärte
- aktuelle Härte
- Härteeinheit

### Grenzwerte

Enthält:

- maximale Entnahmedauer
- maximale Entnahmemenge
- maximalen Volumenstrom

### Salz

Enthält:

- Salzgewicht
- Salzreichweite
- Salzvorrat
- Salzmangel-Warnschwelle

### Wasser

Enthält:

- Gesamtwassermenge
- Weichwassermenge
- aktueller Wasserdurchfluss
- Wassertemperatur

### Verlauf

Das Beispiel-Dashboard enthält einen 7-Tage-Verlauf für:

- Gesamtwasser
- Weichwasser
- Wasserdurchfluss
- Wassertemperatur
- aktive Szene
- Leckageschutz

---

# Branding

Die Integration enthält eigene JUDO-Bilder.

Die Dateien befinden sich innerhalb der Integration unter:

```text
custom_components/
└── judo_isoft_pro/
    └── brand/
        ├── icon.png
        └── logo.png
```

Zusätzlich sind die Bilder für die mitgelieferten statischen Inhalte vorhanden:

```text
www/
└── judo_isoft_pro/
    ├── icon.png
    └── logo.png
```

Die ursprünglichen JUDO-Branding-Dateien werden dabei verwendet.

---

# Struktur des Repositorys

```text
JUDO i-soft PRO / PRO L
│
├── custom_components/
│   └── judo_isoft_pro/
│       ├── __init__.py
│       ├── api.py
│       ├── button.py
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── manifest.json
│       ├── number.py
│       ├── protocol.py
│       ├── select.py
│       ├── sensor.py
│       │
│       ├── brand/
│       │   ├── icon.png
│       │   └── logo.png
│       │
│       └── translations/
│           ├── de.json
│           └── en.json
│
├── www/
│   └── judo_isoft_pro/
│       ├── icon.png
│       └── logo.png
│
├── dashboard.yaml
├── hacs.json
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

# Aktualisierungsverhalten

Die Integration arbeitet mit einem zentralen Coordinator.

Vereinfacht:

```text
JUDO i-soft PRO
       |
       | REST
       v
   JUDO API
       |
       v
 JUDO Coordinator
       |
       +-- Sensoren
       +-- Numbers
       +-- Selects
       +-- Buttons
```

Dadurch greifen nicht mehrere Entities unabhängig voneinander auf die JUDO-Anlage zu.

Die Kommunikation wird zentral kontrolliert.

---

# Entfernte bzw. bewusst nicht bereitgestellte Entitäten

Die aktuelle Version konzentriert sich auf tatsächlich benötigte Werte.

Nicht mehr als eigene öffentliche Entities vorgesehen sind unter anderem:

- separater Verbindungsstatus-Sensor
- Inbetriebnahmedatum
- rohe 6900-Hex-Daten
- einzelne rohe 6900-Byte-Sensoren
- generische 6900-16-Bit-Sensoren
- generische 6900-32-Bit-Sensoren
- künstlicher Leckageschutz-EIN/AUS-Switch

Stattdessen werden die relevanten Informationen sinnvoll dekodiert und als nutzbare Home-Assistant-Entities bereitgestellt.

---

# Software-Version

Die JUDO-Software-Version wird aus den drei vom Gerät gelieferten Bytes dekodiert.

Beispiel:

```text
0C0001
```

wird zu:

```text
1.0.12
```

Die Byte-Reihenfolge wird dabei entsprechend der JUDO-Dokumentation berücksichtigt.

---

# Lokale Kommunikation

Die Integration arbeitet lokal.

Es ist keine externe JUDO-Cloud erforderlich.

Die Verbindung erfolgt über:

```text
Home Assistant
      |
      | LAN
      v
JUDO Connectivity
      |
      v
JUDO i-soft PRO / PRO L
```

Die Zugangsdaten werden im Home-Assistant-Config-Entry gespeichert.

---

# Fehlerbehebung

## Integration erscheint nicht

Prüfen:

```text
/config/custom_components/judo_isoft_pro/
```

muss unter anderem enthalten:

```text
manifest.json
__init__.py
config_flow.py
const.py
```

Danach Home Assistant neu starten.

## „Invalid handler specified“

Dieser Fehler deutet darauf hin, dass Home Assistant den Config-Flow der Integration nicht registrieren konnte.

Prüfen:

1. Ist `config_flow.py` vorhanden?
2. Enthält `manifest.json`:

```json
"config_flow": true
```

3. Ist die Domain korrekt:

```json
"domain": "judo_isoft_pro"
```

4. Ist der Ordnername korrekt:

```text
judo_isoft_pro
```

5. Wurde Home Assistant nach der Installation neu gestartet?

## „cannot import name CONF_NAME“

Die Konstante muss in:

```text
custom_components/judo_isoft_pro/const.py
```

vorhanden sein:

```python
CONF_NAME = "name"
```

Die aktuelle Version enthält diese Konstante bereits.

## Keine Verbindung zur JUDO-Anlage

Prüfen:

- IP-Adresse
- Port
- Benutzername
- Passwort
- Netzwerkverbindung
- REST-Schnittstelle des JUDO-Gerätes
- Firewall
- Connectivity-Modul

## Sensor bleibt auf letztem Wert

Das kann bei einem einzelnen Kommunikationsfehler absichtlich passieren.

Die Integration hält den zuletzt erfolgreich empfangenen Wert, anstatt ihn sofort zu löschen.

Bei einer später erfolgreichen Abfrage wird der Wert aktualisiert.

## 6900-Werte fehlen

Prüfen:

- JUDO-Gerät erreichbar?
- REST-Schnittstelle aktiv?
- unterstützt die verwendete Software den dokumentierten Gerätestatus?
- ist die Antwort des Gerätes gültig?

Die 6900-Daten werden nur einmal innerhalb des normalen Polling-Zyklus abgefragt.

---

# REST-API-Dokumentation

Die Integration basiert auf der bereitgestellten JUDO-REST-API-Dokumentation.

Darin sind unter anderem beschrieben:

- Gerätekonfiguration
- Wasserhärte
- Härteeinheiten
- Salz
- Leckageschutz
- Szenen
- Regeneration
- Wasserzähler
- Gerätestatus
- Device ID
- Software-Version
- Betriebsstunden

Die Integration verwendet ausschließlich die für die aktuelle Home-Assistant-Integration benötigten Funktionen.

---

# Version 2.5.51

## Änderungen

### Device ID

Die JUDO Device ID aus Kommando:

```text
06
```

ist wieder als diagnostischer Sensor verfügbar.

### Config Flow

Der Config Flow wurde so aufgebaut, dass:

- der Gerätename zuerst eingegeben wird
- mehrere JUDO-Geräte eingerichtet werden können
- die Verbindung beim Einrichten getestet wird
- die JUDO Device ID zur Identifikation verwendet werden kann

### Kommunikation

- zentrale REST-Warteschlange
- maximal 1 Kommando pro Sekunde und Gerät
- einmalige Wiederholung bei transienten Fehlern
- 5-Sekunden-Nachabfrage bei relevanten Änderungen
- letzter gültiger Wert bleibt bei einzelnen Fehlern erhalten

### 6900

Die 6900-Antwort wird gezielt dekodiert.

Bereitgestellt werden:

- aktive Szene
- globaler Leckageschutzstatus
- Leckagegrund
- aktueller Wasserdurchfluss
- aktuelle Wassertemperatur

### Werte

- Wasser in m³
- Salz in kg
- Durchfluss in L/h
- Temperatur in °C
- vollständige Härteeinheiten
- korrekte Software-Versionsdekodierung

### Bedienung

Numerische Einstellungen werden als Home-Assistant-`number`-Entities bereitgestellt.

---

# Entwicklung

Das Projekt ist als Home-Assistant-Custom-Integration aufgebaut.

Die Kommunikation ist in mehrere Bereiche getrennt:

```text
api.py
```

Kommunikation mit der JUDO REST API.

```text
protocol.py
```

Dekodierung und Interpretation der JUDO-Daten.

```text
coordinator.py
```

Zentrale Abfrage- und Kommunikationslogik.

```text
sensor.py
```

Messwerte und Statusinformationen.

```text
number.py
```

Einstellbare numerische Werte.

```text
select.py
```

Szenen und Härteeinheiten.

```text
button.py
```

Aktionen wie Regeneration und Leckageschutz.

```text
config_flow.py
```

Einrichtung der JUDO-Anlage über die Home-Assistant-Oberfläche.

---

# Hinweise

Diese Integration verwendet die lokale REST-Schnittstelle der JUDO-Anlage.

Die genaue Verfügbarkeit einzelner Funktionen kann von:

- Gerätemodell
- Firmware
- Connectivity-Modul
- aktivierter REST-Schnittstelle
- Softwarestand

abhängen.

Nicht jedes JUDO-Gerät muss zwangsläufig sämtliche dokumentierten REST-Funktionen in jedem Softwarestand bereitstellen.

---

# Lizenz

Dieses Projekt steht unter der MIT License.

```text
MIT License

Copyright (c) 2026 JUDO1936
```

Siehe:

```text
LICENSE
```

für den vollständigen Lizenztext.

---

# Haftungshinweis

Die Integration dient der Überwachung und Bedienung einer JUDO-Wasseraufbereitungsanlage über deren lokale REST-Schnittstelle.

Vor der Verwendung von Schreib- oder Steuerfunktionen sollte überprüft werden, ob die verwendeten REST-Kommandos und Einstellungen für die jeweilige Anlage geeignet sind.

Insbesondere Funktionen wie:

- Regeneration
- Leckageschutz öffnen
- Leckageschutz schließen
- Szenenaktivierung
- Änderung von Grenzwerten

können das Verhalten der angeschlossenen Anlage beeinflussen.

---

# Beiträge und Fehler melden

Fehler, Verbesserungsvorschläge und Erweiterungen können über das GitHub-Repository eingereicht werden.

**Repository:**

https://github.com/JUDO1936/judo-isoft_PRO-hacs

**Issues:**

https://github.com/JUDO1936/judo-isoft_PRO-hacs/issues

Bitte bei einem Fehler möglichst folgende Informationen angeben:

- Home-Assistant-Version
- Integrationsversion
- JUDO-Gerät
- Firmware-Version
- relevante Logmeldung
- verwendetes REST-Kommando, falls bekannt
- Beschreibung des erwarteten und tatsächlichen Verhaltens

Keine Passwörter oder andere Zugangsdaten in Issues veröffentlichen.

---

# JUDO i-soft PRO / PRO L

**Lokale REST-Integration für Home Assistant**

```text
JUDO i-soft PRO
JUDO i-soft PRO mit Leckageschutz
JUDO i-soft PRO L
```

**Version:** `2.5.51`

**Integration:** `judo_isoft_pro`

**IoT-Klasse:** `local_polling`

**Lizenz:** MIT
