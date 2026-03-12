# Metallgitter Visualisierung

Interaktive Visualisierung von BCC/FCC/HCP Gittern mit PyVista.

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

## Lokaler Release-Check (ohne Push/Tag)

Damit testest du lokal genau den gleichen Build-Typ wie im GitHub Release:

```powershell
.\scripts\release-check.ps1
```

Optional:

```powershell
.\scripts\release-check.ps1 -SkipTests
.\scripts\release-check.ps1 -OpenDist
```

## Release mit Windows `.exe`

Die GitHub Action `release-windows-exe.yml` baut bei Tags `v*` automatisch eine `.exe` und haengt sie an den Release.

Beispiel:

```powershell
git tag v0.2.3
git push origin v0.2.3
```

Danach findest du `Metallgitter-Visualisierung.exe` unter:
- GitHub Release Assets (beim Tag)
- Actions Artifacts (zusaetzlich)
