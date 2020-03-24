# QGIS2Wegue 

A QGIS plugin for creating [Wegue](https://github.com/meggsimum/wegue) configurations based on a QGIS project.

## Disclaimer

This plugin is still work in progress. Supported formats so far:
- `WMS`
- `WFS` (soon supported in Wegue)
- `XYZ`
- `KML`
- `GeoJSON`

## Installation for Developers

The installation works basically same for Windows, Linux and Mac:

1. Enter your QGIS plugin directory with `cd PATH/TO/YOUR/QGIS/PLUGIN/DIRECTORY` The path depends on your QGIS installation. Typical locations are:
    - Windows (standalone installation): `C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
    - Windows (Network Installation): `C:\OSGeo4W64\apps\qgis\python\plugins`
    - Ubuntu/Debian: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`

2. Download QGIS2Wegue: `git clone https://github.com/meggsimum/qgis2wegue`

3. Restart QGIS

4. Open the plugin manager and activate the plugin - the plugin should show up in the toolbar

Update the plugin with `git pull https://github.com/meggsimum/qgis2wegue` and restart QGIS


## Usage

- Add all your desired layers to QGIS
- Open the plugin, chose a filepath and click `OK`
- Now you have a configuration file that works with Wegue 