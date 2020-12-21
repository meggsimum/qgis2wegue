import json


class WegueConfiguration:
    """Contains parameters of a Wegue configuration"""

    def __init__(self):
        self.title = "Vue.js / OpenLayers WebGIS"
        self.baseColor = "green darken-3"
        self.logo = "https://dummyimage.com/100x100/aaa/fff&text=Wegue"
        self.logoSize = 100
        self.footerTextLeft = "Powered by <a href='https://meggsimum.de/wegue/' target='_blank'>Wegue WebGIS</a>"
        self.footerTextRight = "meggsimum"
        self.showCopyrightYear = True
        self.mapZoom = 2
        self.mapCenter = (0, 0)
        self.mapLayers = []
        self.modules = {}

    def to_file(self, path):
        """Store Wegue configuration as JSON file"""

        with open(path, "w") as path:
            json.dump(self.__dict__, path, indent=2, ensure_ascii=False)

    def add_map_geodata_drag_drop(self):
        self.mapGeodataDragDop = {
            "formats": ["GeoJSON", "KML"],
            "zoomToData": True,
            "replaceData": True,
            "displayInLayerList": True,
            "layerName": "Uploaded Data"
        }

    def add_permalink(self):
        self.permalink =  {
            "location": "hash",
            "layers": True,
            "extent": False,
            "projection": "EPSG:4326",
            "paramPrefix": "",
            "history": True
        }        

    def add_layer_list(self):
        self.modules["wgu-layerlist"] = {
            "target": "menu",
            "win": True,
            "draggable": False
        }

    def add_measuretool(self):
        self.modules["wgu-measuretool"] = {
            "target": "menu",
            "win": True,
            "draggable": False,
            "strokeColor": "#c62828",
            "fillColor": "rgba(198,40,40,0.2)",
            "sketchStrokeColor": "rgba(198,40,40,0.8)",
            "sketchFillColor": "rgba(198,40,40,0.1)",
            "sketchVertexStrokeColor": "#c62828",
            "sketchVertexFillColor": "rgba(198,40,40,0.2)"
        }

    def add_infoclick(self):
        self.modules["wgu-infoclick"] = {
            "target": "menu",
            "win": True,
            "draggable": False,
            "initPos": {
                "left": 8,
                "top": 74
            }
        }

    def add_button_zoom_to_extent(self):
        self.modules["wgu-zoomtomaxextent"] = {
            "target": "toolbar",
            "darkLayout": True
        }

    def add_help_window(self):
        self.modules["wgu-helpwin"] = {
            "target": "toolbar",
            "darkLayout": True
        }

    def add_geocoder(self):
        self.modules["wgu-geocoder"] = {
            "target": "toolbar",
            "darkLayout": True,
            "minChars": 2,
            "queryDelay": 200,
            "selectZoom": 16,
            "debug": False,
            "placeHolder": "Search address",
            "provider": "osm",
            "providerOptions": {
                "lang": "en-US",
                "countrycodes": "",
                "limit": 6
            }
        }

    def add_geolocator(self):
        self.modules["wgu-geolocator"] = {
            "target": "toolbar",
            "darkLayout": True
        }

