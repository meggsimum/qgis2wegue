import json
import logging

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)


class WegueConfiguration:
    """
    Contains parameters of a Wegue configuration
    """

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
        self.modules = {"wgu-layerlist":
                        {
                            "target": "menu",
                            "win": True,
                            "draggable": False
                        },
                        "wgu-measuretool": {
                            "target": "menu",
                            "win": True,
                            "draggable": False,
                            "strokeColor": "#c62828",
                            "fillColor": "rgba(198,40,40,0.2)",
                            "sketchStrokeColor": "rgba(198,40,40,0.8)",
                            "sketchFillColor": "rgba(198,40,40,0.1)",
                            "sketchVertexStrokeColor": "#c62828",
                            "sketchVertexFillColor": "rgba(198,40,40,0.2)"
                        },
                        "wgu-infoclick": {
                            "target": "menu",
                            "win": True,
                            "draggable": False,
                            "initPos": {
                                "left": 8,
                                "top": 74
                            }
                        },
                        "wgu-zoomtomaxextent": {
                            "target": "toolbar",
                            "darkLayout": True
                        },
                        "wgu-helpwin": {
                            "target": "toolbar",
                            "darkLayout": True
                        }}

    def as_dict(self):
        """
        :return: dict of Wegue configuration
        """
        return self.__dict__

    def _remove_empty_keys(self, conf):
        # TODO: solve more elegantly

        final_conf = {}

        for key in conf:
            value = conf[key]
            if value:
                final_conf[key] = value

        return final_conf

    def to_file(self, path):
        """
        Store Wegue configuration as JSON file
        :param path:
        """
        
        # TODO solve more elegantly
        fixed_layers = []
        for layer in self.mapLayers:
            layer = self._remove_empty_keys(layer)
            fixed_layers.append(layer)
        
        self.mapLayers = fixed_layers

        with open(path, 'w') as path:
            json.dump(self.__dict__, path, indent=2)

        logging.info('Wrote Wegue Configuration to: \n{}'.format(path))

    def is_valid(self):
        """
        :return: if Wegue configuration is valid
        """
        if not self.mapLayers:
            return False
        return True

    def add_xyz_layer(self,
                      name,
                      url,
                      lid="",
                      displayInLayerList=True,
                      visible=True,
                      opacity=""):

        if not lid:
            lid = self._create_layer_id(name)

        xyz_conf = {
            'name': name,
            'url': url,
            'lid': lid,
            'displayInLayerList': displayInLayerList,
            'visible': visible,
            'opacity': opacity
        }
        self.mapLayers.append(xyz_conf)

    def add_osm_layer(self,
                      name="OpenStreetMap Standard",
                      lid="",
                      displayInLayerList=True,
                      visible=True,
                      opacity=""):

        if not lid:
            lid = self._create_layer_id(name)

        osm_conf = {
            "type": 'OSM',
            "name": name,
            "lid": lid,
            "displayInLayerList": displayInLayerList,
            "visible": visible,
            "opacity": opacity
        }
        self.mapLayers.append(osm_conf)

    def add_vector_layer(self,
                         name,
                         format,
                         url,
                         lid="",
                         style="",
                         displayInLayerList=True,
                         visible=True,
                         opacity="",
                         extent="",
                         formatConfig="",
                         attributions="",
                         hoverable=False,
                         hoverAttribute=""):
        """
        :param format: allowed values: "MVT", "GeoJSON", "TopoJSON", "KML"
        :param lid: layer id
        :param style: OpenLayers style
        :return:
        """

        if not lid:
            lid = self._create_layer_id(name)

        if not style:
            style = {
                "radius": 4,
                "strokeColor": "rgb(207, 16, 32)",
                "strokeWidth": 1,
                "fillColor": "rgba(207, 16, 32, 0.6)"
            }

        vector_conf = {
            "type": "VECTOR",
            "name": name,
            "lid": lid,
            "displayInLayerList": displayInLayerList,
            "extent": extent,
            "visible": visible,
            "opacity": opacity,
            "url": url,
            "format": format,
            "formatConfig": formatConfig,
            "attributions": attributions,
            "style": style,
            "hoverable": hoverable,
            "hoverAttribute": hoverAttribute
        }

        self.mapLayers.append(vector_conf)

    # TODO: make parameters in same order as for other functions
    def add_wms_layer(self,
                      name,
                      layers,
                      url,
                      transparent=True,
                      singleTile=False,
                      projection="EPSG:3857",
                      attributions="",
                      isBaseLayer=False,
                      visible=False,
                      opacity="",
                      displayInLayerList=True,
                      extent="",
                      lid="",
                      tiled="",
                      serverType=""):
        """
        :param lid: if empty, it will be autocreated from the layer name
        """

        if not lid:
            lid = self._create_layer_id(name)

        wms_conf = {
            "type": "WMS",
            "lid": lid,
            "name": name,
            "format": "image/png",
            "layers": layers,
            "tiled": tiled,
            "url": url,
            "transparent": transparent,
            "singleTile": singleTile,
            "projection": projection,
            "attributions": attributions,
            "isBaseLayer": isBaseLayer,
            "visible": visible,
            "opacity": opacity,
            "displayInLayerList": displayInLayerList,
            "extent": extent,
            "serverType": serverType
        }
        self.mapLayers.append(wms_conf)

    # TODO: replace umlauts and similar characters
    def _create_layer_id(self, name):
        """Creates a layer id based on the name of the layer
        :param name: the layer's full name
        :return: layer identification name without spaces and special characters
        """
        lid = ''.join(e for e in name if e.isalnum())
        lid = lid.lower()
        return lid

    def add_example_layers(self):
        """
        Add example layers. Only for testing.
        :return:
        """
        example_layers = [{
            "type": "WMS",
            "lid": "ahocevar-wms",
            "name": "WMS (ahocevar)",
            "format": "image/png",
            "layers": "topp:states",
            "url": "https://ahocevar.com/geoserver/wms",
            "transparent": True,
            "singleTile": False,
            "projection": "EPSG:3857",
            "attribution": "",
            "isBaseLayer": False,
            "visible": False,
            "displayInLayerList": True
        }]

        self.add_osm_layer()
        self.mapLayers.extend(example_layers)
