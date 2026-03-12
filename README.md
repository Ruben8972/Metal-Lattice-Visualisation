# Metallgitter Visualisierung

Interaktive Visualisierung von BCC/FCC/HCP-Gittern mit PyVista.

## Lokal starten

```powershell
python main.py
```

Alternativ nach Installation:

```powershell
metallgitter-vis
```

## Tests

```powershell
python -m pytest -q
```

## Release mit Windows `.exe`

Die GitHub Action `release-windows-exe.yml` baut bei Tags `v*` automatisch eine `.exe` und hängt sie an den Release.

Beispiel:

```powershell
git tag v0.2.0
git push origin v0.2.0
```

Danach findest du die Datei `Metallgitter-Visualisierung.exe` unter:
- GitHub Release Assets (beim Tag)
- Actions Artifacts (zusätzlich)
