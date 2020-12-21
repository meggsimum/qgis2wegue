# Changelog

## v1.0.0 - 2020-12-23

- add more configurations:
  - `mapGeodataDragDop`: enables Wegue to drag&drop vector files like GeoJSON or KML as new layer
  - `permalink`: adds an updated permalink to the URL
  - `geolocator`: a button where the user can locate him/her self
- add sample QGIS project to repository
- remove `experimental` flag for QGIS plugin repo

## v1.0.0-beta - 2020-05-31

First public version with basic functionality:

- support for `WMS`, `XYZ`, `KML`, `GeoJSON`, `WFS`
- text input field for `Title`, `Footer Left`, `Footer Right`
- color picker for base color
- checkboxes for optional modules in the map
- validation of output path e.g. if the naming is correct