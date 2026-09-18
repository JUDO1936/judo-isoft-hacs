# JUDO i-soft PRO / L – Home Assistant Integration

**Eine vollständig lokale Home Assistant Custom Component zur Überwachung und Steuerung von JUDO i-soft Wasserenthärtungsanlagen.**

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg?logo=homeassistant)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained-yes-brightgreen.svg)]()

---

## Inhaltsverzeichnis

* [Über das Projekt](#über-das-projekt)
* [Funktionen](#funktionen)
* [Voraussetzungen](#voraussetzungen)
* [Repository-Struktur](#repository-struktur)
* [Sensoren](#sensoren)
* [Dienste](#dienste)
* [Installation](#installation)
* [Einrichtung](#einrichtung)
* [Dashboard](#dashboard)
* [Kommunikation](#kommunikation)
* [Bekannte Einschränkungen](#bekannte-einschränkungen)
* [Fehlerbehebung](#fehlerbehebung)
* [Lizenz](#lizenz)
* [Rechtlicher Hinweis](#rechtlicher-hinweis)

---

## Über das Projekt

Die **JUDO i-soft PRO / L Home Assistant Integration** ermöglicht die lokale Überwachung und Steuerung kompatibler JUDO Wasserenthärtungsanlagen direkt aus Home Assistant.

Die Kommunikation erfolgt vollständig über die lokale REST-Schnittstelle der Anlage. Eine Verbindung zu einer externen Cloud ist für den Betrieb der Integration nicht erforderlich.

Nach der Einrichtung werden die verfügbaren Betriebs-, Verbrauchs- und Systemdaten als Home Assistant Entitäten bereitgestellt.

Zusätzlich stehen Home Assistant Services zur Verfügung, mit denen ausgewählte Funktionen der Anlage automatisiert oder direkt über das Home Assistant Dashboard gesteuert werden können.

### Unterstützte Anlagen

* JUDO i-soft PRO
* JUDO i-soft PRO L

Die tatsächlich verfügbaren Funktionen und Werte können abhängig von Modell, Firmware-Version und Gerätekonfiguration variieren.

---

## Funktionen

### Lokale Kommunikation

* Kommunikation ausschließlich innerhalb des lokalen Netzwerks
* Keine zwingende Cloud-Verbindung
* Direkter Zugriff auf die REST-Schnittstelle der Anlage
* Integration in bestehende Home Assistant Automatisierungen

### Überwachung

Unter anderem können folgende Informationen ausgelesen werden:

* Gesamtwasserverbrauch
* Weichwassermenge
* Tagesverbrauch
* Monatsverbrauch
* Salzvorrat
* Salzreichweite
* Salzverbrauch
* Wasserhärte
* Entnahmemengen
* Volumenstrom
* Gerätestatus
* Seriennummer
* Firmware-Version

### Steuerung

Je nach unterstützter Gerätefunktion können unter anderem folgende Aktionen ausgeführt werden:

* Zielwasserhärte ändern
* Manuelle Regeneration starten
* Leckageschutz schließen
* Leckageschutz öffnen
* Wasserprofile beziehungsweise Szenen aktivieren
* Urlaubsmodus aktivieren
* Maximale Entnahmemenge einstellen
* Maximalen Volumenstrom einstellen

---

## Voraussetzungen

Für den Betrieb werden benötigt:

* Home Assistant
* Eine kompatible JUDO i-soft PRO oder i-soft L Anlage
* Netzwerkverbindung zwischen Home Assistant und der JUDO Anlage
* Lokale IP-Adresse der Anlage
* Zugangsdaten der Anlage

Die Integration ist für den Betrieb innerhalb eines lokalen Netzwerks ausgelegt.

---

## Repository-Struktur

Das Repository ist für die Verwendung mit HACS und Home Assistant entsprechend strukturiert:

```text
.
├── hacs.json
├── README.md
├── LICENSE
├── dashboard.yaml
└── custom_components/
    └── judo_isoft/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── manifest.json
        └── sensor.py
```

---

# Sensoren

Nach erfolgreicher Einrichtung erstellt die Integration die verfügbaren Sensoren automatisch in Home Assistant.

Die genaue Anzahl und Verfügbarkeit der Sensoren kann abhängig von Modell und Firmware-Version variieren.

| Entität                                 | Name               | Einheit | Beschreibung                                               |
| --------------------------------------- | ------------------ | ------: | ---------------------------------------------------------- |
| `sensor.i_soft_gesamtwassermenge`       | Gesamtwassermenge  |      m³ | Gesamte erfasste Wassermenge                               |
| `sensor.i_soft_weichwassermenge`        | Weichwassermenge   |      m³ | Menge des aufbereiteten Weichwassers                       |
| `sensor.i_soft_wasser_tag`              | Tagesverbrauch     |       L | Wasserverbrauch des aktuellen Tages                        |
| `sensor.i_soft_wasser_monat`            | Monatsverbrauch    |       L | Wasserverbrauch des aktuellen Monats                       |
| `sensor.i_soft_salzgewicht`             | Salzgewicht        |      kg | Aktueller Salzvorrat                                       |
| `sensor.i_soft_salzreichweite`          | Salzreichweite     |    Tage | Geschätzte verbleibende Salzreichweite                     |
| `sensor.i_soft_salz_tag`                | Salzverbrauch Tag  |       g | Ermittelter täglicher Salzverbrauch                        |
| `sensor.i_soft_salzmangel_warnschwelle` | Warnschwelle Salz  |    Tage | Eingestellter Schwellenwert für die Salzreichweitenwarnung |
| `sensor.i_soft_wunschwasserhaerte`      | Wunschwasserhärte  |     °dH | Aktuell eingestellte Zielwasserhärte                       |
| `sensor.i_soft_max_entnahmedauer`       | Max. Entnahmedauer |     min | Maximale zulässige Entnahmedauer                           |
| `sensor.i_soft_max_entnahmemenge`       | Max. Entnahmemenge |       L | Maximales Entnahmevolumen                                  |
| `sensor.i_soft_max_volumenstrom`        | Max. Volumenstrom  |     L/h | Maximal zulässiger Durchfluss                              |
| `sensor.i_soft_geraetenummer`           | Seriennummer       |       – | Eindeutige Gerätenummer                                    |
| `sensor.i_soft_firmware_version`        | Firmware-Version   |       – | Aktuell installierte Firmware                              |

> Hinweis: Die verfügbaren Werte können je nach Anlagenmodell und installierter Firmware abweichen.

---

# Dienste

Die Integration stellt eigene Home Assistant Services unter der Domain `judo_isoft` zur Verfügung.

Die Services können beispielsweise über Automatisierungen, Skripte oder das Home Assistant Dashboard verwendet werden.

| Service                             | Parameter                             | Beschreibung                              |
| ----------------------------------- | ------------------------------------- | ----------------------------------------- |
| `judo_isoft.set_wunschwasserhaerte` | `haerte` – Integer 0–30               | Setzt die Zielwasserhärte                 |
| `judo_isoft.start_regeneration`     | keine                                 | Startet eine manuelle Regeneration        |
| `judo_isoft.close_leak_protection`  | keine                                 | Schließt das Leckageschutzventil          |
| `judo_isoft.open_leak_protection`   | keine                                 | Öffnet das Leckageschutzventil            |
| `judo_isoft.activate_scenes`        | `szene`, `dauer_hex`                  | Aktiviert ein definiertes Wasserprofil    |
| `judo_isoft.start_holiday_mode`     | `tage` – Integer 1–30                 | Aktiviert den Urlaubsmodus                |
| `judo_isoft.set_max_volume`         | `liter` – Integer 100–3000            | Setzt die maximale Entnahmemenge          |
| `judo_isoft.set_max_flow`           | `liter_pro_stunde` – Integer 500–5000 | Setzt den maximal zulässigen Volumenstrom |

### Beispiel: Zielwasserhärte ändern

```yaml
service: judo_isoft.set_wunschwasserhaerte
data:
  haerte: 8
```

### Beispiel: Regeneration starten

```yaml
service: judo_isoft.start_regeneration
```

---

# Installation

## Methode 1: Installation über HACS

Die Installation über HACS ist die empfohlene Variante.

1. Öffnen Sie **HACS** in Home Assistant.
2. Öffnen Sie das Menü über die drei Punkte.
3. Wählen Sie **Benutzerdefinierte Repositories**.
4. Fügen Sie die GitHub-Adresse dieses Repositories ein.
5. Wählen Sie als Kategorie **Integration**.
6. Fügen Sie das Repository hinzu.
7. Suchen Sie nach **JUDO i-soft PRO / L**.
8. Installieren Sie die Integration.
9. Starten Sie Home Assistant anschließend neu.

Nach dem Neustart sollte die Integration unter **Einstellungen → Geräte & Dienste** verfügbar sein.

---

## Methode 2: Manuelle Installation

1. Laden Sie das Repository als ZIP-Datei herunter.
2. Entpacken Sie das Archiv.
3. Kopieren Sie den Ordner

```text
custom_components/judo_isoft/
```

in das Home Assistant Verzeichnis:

```text
/config/custom_components/judo_isoft/
```

Die Verzeichnisstruktur muss anschließend beispielsweise so aussehen:

```text
/config/
└── custom_components/
    └── judo_isoft/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── manifest.json
        └── sensor.py
```

4. Starten Sie Home Assistant neu.

---

# Einrichtung

Nach der Installation:

1. Öffnen Sie **Einstellungen → Geräte & Dienste**.
2. Klicken Sie auf **Integration hinzufügen**.
3. Suchen Sie nach **JUDO i-soft PRO / L**.
4. Geben Sie die lokale IP-Adresse der JUDO Anlage ein.
5. Geben Sie die Zugangsdaten ein.
6. Bestätigen Sie die Einrichtung.

### Standard-Zugangsdaten

Sofern diese auf der Anlage nicht geändert wurden:

```text
Benutzer: admin
Passwort: Connectivity
```

> Aus Sicherheitsgründen wird empfohlen, die Zugangsdaten der Anlage nach Möglichkeit nicht unverändert zu lassen.

---

# Dashboard

Dem Repository liegt mit `dashboard.yaml` ein Beispiel für ein Home Assistant Dashboard bei.

Ein einfaches Steuerungs-Panel kann beispielsweise so aussehen:

```yaml
type: entities
title: JUDO i-soft Steuerung
show_header_toggle: false
entities:
  - entity: sensor.i_soft_wunschwasserhaerte
    name: Zielwasserhärte

  - type: button
    name: Manuelle Regeneration
    icon: mdi:autorenew
    action_name: Starten
    tap_action:
      action: call-service
      service: judo_isoft.start_regeneration

  - type: button
    name: Leckageschutz schließen
    icon: mdi:valve-closed
    action_name: Schließen
    tap_action:
      action: call-service
      service: judo_isoft.close_leak_protection
```

Das Dashboard kann individuell erweitert und an die eigene Home Assistant Installation angepasst werden.

---

# Kommunikation

Die Integration verwendet die lokale Kommunikationsschnittstelle der JUDO Anlage.

Die Kommunikation erfolgt dabei direkt zwischen Home Assistant und dem Gerät:

```text
Home Assistant
      |
      | Lokales Netzwerk
      |
      v
JUDO i-soft PRO / L
      |
      | REST-Schnittstelle
      |
      v
Betriebs- und Gerätedaten
```

Eine externe Cloud ist für die grundlegende Kommunikation der Integration nicht erforderlich.

---

# Bekannte Einschränkungen

## Abhängigkeit von der Firmware

Die von der JUDO Anlage bereitgestellten Funktionen und Daten können sich abhängig von der installierten Firmware unterscheiden.

Daher kann es vorkommen, dass einzelne Werte oder Befehle bei bestimmten Firmware-Versionen nicht verfügbar sind.

## API-Befehle

Nicht jeder dokumentierte oder aus älteren Softwareständen bekannte API-Befehl steht zwingend in jeder Firmware-Version zur Verfügung.

Insbesondere können sich Befehle, Parameter oder Rückgabewerte zwischen verschiedenen Softwareständen ändern.

## Netzwerkkommunikation

Die Stabilität der Kommunikation hängt unter anderem von folgenden Faktoren ab:

* Netzwerkverbindung
* IP-Erreichbarkeit der Anlage
* Firmware-Version
* Anzahl und Häufigkeit der Anfragen
* Reaktionszeit der REST-Schnittstelle

Bei Problemen mit der Kommunikation sollte zunächst geprüft werden, ob die JUDO Anlage aus dem Home Assistant Netzwerk erreichbar ist.

---

# Fehlerbehebung

## Die Integration wird nicht angezeigt

Prüfen Sie:

```text
/config/custom_components/judo_isoft/
```

und stellen Sie sicher, dass sich darin mindestens die erforderlichen Python-Dateien und `manifest.json` befinden.

Anschließend Home Assistant neu starten.

---

## Keine Werte werden angezeigt

Prüfen Sie zunächst:

1. Ist die IP-Adresse der JUDO Anlage korrekt?
2. Ist die Anlage im Netzwerk erreichbar?
3. Sind die Zugangsdaten korrekt?
4. Ist die REST-Schnittstelle der Anlage verfügbar?
5. Gibt es Fehlermeldungen in den Home Assistant Logs?

Die Home Assistant Logs finden Sie unter:

**Einstellungen → System → Protokolle**

---

## Einzelne Werte fehlen

Wenn einzelne Sensoren keine Werte liefern, kann dies unter anderem daran liegen, dass der entsprechende Wert von der verwendeten Firmware nicht bereitgestellt wird.

In diesem Fall sollte zunächst die Firmware-Version der Anlage geprüft werden.

---

# Sicherheitshinweise

Die Integration ermöglicht teilweise die Steuerung von Funktionen der Wasserenthärtungsanlage.

Automatisierungen sollten daher sorgfältig konfiguriert und getestet werden.

Insbesondere bei Funktionen wie:

* Regeneration
* Leckageschutz
* maximaler Entnahmemenge
* maximalem Volumenstrom

sollten unbeabsichtigte Auslösungen vermieden werden.

Die Integration sollte ausschließlich in Netzwerken eingesetzt werden, in denen der Zugriff auf die Anlage entsprechend abgesichert ist.

---

# Lizenz

Dieses Projekt wird unter der **MIT-Lizenz** veröffentlicht.

Die vollständigen Lizenzbedingungen sind in der Datei `LICENSE` enthalten.

---

# Rechtlicher Hinweis

Dieses Projekt ist ein **inoffizielles Community-Projekt**.

Es besteht keine offizielle Verbindung, Partnerschaft oder Unterstützung durch die **JUDO Wasseraufbereitung GmbH**, sofern dies nicht ausdrücklich angegeben ist.

JUDO und i-soft sind Marken beziehungsweise Produktbezeichnungen ihrer jeweiligen Rechteinhaber.

Die Verwendung dieser Integration erfolgt auf eigene Verantwortung. Vor produktivem Einsatz sollten alle Funktionen und Automatisierungen mit der jeweiligen Anlage und deren Firmware getestet werden.

---

# Support und Weiterentwicklung

Bei Fehlern, Problemen oder Verbesserungsvorschlägen können Issues im GitHub-Repository erstellt werden.

Bitte geben Sie bei einem Fehler möglichst folgende Informationen an:

* Home Assistant Version
* Version der JUDO i-soft Integration
* Anlagenmodell
* Firmware-Version
* verwendete Kommunikationsart
* relevante Fehlermeldungen aus den Home Assistant Logs
* Beschreibung des erwarteten und tatsächlichen Verhaltens

Bitte veröffentlichen Sie keine Passwörter, Zugangsdaten oder andere vertrauliche Informationen in Issues.

---

## Projektstatus

Das Projekt befindet sich in der laufenden Weiterentwicklung.

Funktionen und unterstützte API-Befehle können sich mit zukünftigen Versionen der Integration und der JUDO Firmware ändern.
