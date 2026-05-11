# SL Viewer Builder a feasibility study

Moderne Python-Desktop-Anwendung zum Konfigurieren und Bauen von Second-Life-basierten Viewern.

## Features

- Moderne ttkbootstrap Oberflaeche
- Auswahl unterstuetzter Viewer-Repositories
- In-App Download (git clone / git pull)
- Autobuild Integration
- Build-Konfiguration
- Live-Status ueber WebSocket
- Logging
- Fehlerbehandlung
- Unit- und Integration-Tests

## Unterstuetzte Viewer

- Second Life Viewer
- Firestorm Viewer
- Alchemy Viewer
- Kokua Viewer
- Singularity Viewer
- Cool VL Viewer
- Black Dragon Viewer
- Catznip Viewer

## Voraussetzungen

- Python 3.13
- Git
- CMake
- Visual Studio Build Tools (Windows)
- Autobuild installiert

## Installation

```bash
git clone https://github.com/secondlife/viewer.git
git clone https://github.com/secondlife/autobuild.git
```

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Anwendung starten

```powershell
python app.py
```

## Tests

```powershell
pytest
```

## Sicherheit

- Keine Secrets im Code speichern
- Nur lokale Kommunikation
- Eingaben werden validiert
