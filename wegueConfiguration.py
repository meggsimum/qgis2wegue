import json
import uuid


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
        self.modules = {}

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
            if value != "":
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
            json.dump(self.__dict__, path, indent=2, ensure_ascii=False)

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
                      opacity="",
                      attributions=""):

        if not lid:
            lid = self._create_layer_id(name)

        xyz_conf = {
            'type': 'XYZ',
            'name': name,
            'url': url,
            'lid': lid,
            'displayInLayerList': displayInLayerList,
            'visible': visible,
            'opacity': opacity,
            'attributions': attributions
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
                         hoverAttribute="",
                         geometryTypeName=""):
        """
        :param format: allowed values: "MVT", "GeoJSON", "TopoJSON", "KML"
        :param lid: layer id
        :param style: OpenLayers style
        :param geometryTypeName: if style is empty and geometryType specific default style will be applied. Allowed values "Point", "LineString", "Polygon"
        :return:
        """

        if not lid:
            lid = self._create_layer_id(name)

        if not style and geometryTypeName:
            style = self._assign_default_style(geometryTypeName)

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

    def _assign_default_style(self, geometryType):
        style = ""
        if geometryType == 'Point':
            style = {
                "radius": 4,
                "strokeColor": "rgb(207, 16, 32)",
                "strokeWidth": 1,
                "fillColor": "rgba(207, 16, 32, 0.6)"
            }
        elif geometryType == 'LineString':
            style = {
                "strokeColor": "blue",
                "strokeWidth": 2
            }
        elif geometryType == 'Polygon':
            style = {
                "strokeColor": "gray",
                "strokeWidth": 1,
                "fillColor": "rgba(20,20,20,0.1)"
            }
        return style


    def add_wms_layer(self,
                      name,
                      layers,
                      url,
                      transparent=True,
                      singleTile=False,
                      projection="EPSG:3857",
                      attributions="",
                      isBaseLayer=False,
                      visible=True,
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

    def add_wfs_layer(self, name, url,
                      typeName,
                      formatConfig="",
                      wfs_format="GML3",
                      version="",
                      projection="",
                      lid="",
                      displayInLayerList=True,
                      visible=True,
                      opacity="",
                      extent="",
                      style="",
                      attributions="",
                      loadOnlyVisible="",
                      maxFeatures="",
                      geometryTypeName=""
                      ):
        """
        :param style: OpenLayers style
        :param geometryTypeName: if style is empty and geometryType specific default style will be applied. Allowed values "Point", "LineString", "Polygon"
        :return:
        """
        if not lid:
            lid = self._create_layer_id(name)

        if not style and geometryTypeName:
            style = self._assign_default_style(geometryTypeName)    

        wfs_conf = {
            "type": "WFS",
            "lid": lid,
            "name": name,
            "url": url,
            "displayInLayerList": displayInLayerList,
            "visible": visible,
            "opacity": opacity,
            "extent": extent,
            "style": style,
            "attributions": attributions,
            "projection": projection,
            "version": version,
            "format": wfs_format,
            "formatConfig": formatConfig,
            "typeName": typeName,
            "loadOnlyVisible": loadOnlyVisible,
            "maxFeatures": maxFeatures
        }
        self.mapLayers.append(wfs_conf)

    def _create_layer_id(self, name):
        """Creates a layer id based on the name of the layer
        :param name: the layer's full name
        :return: layer identification name without spaces
                 and special characters
        """

        lid = name.strip().lower()

        # replace some special characters
        lid = lid.replace('ä', 'ae')
        lid = lid.replace('ö', 'oe')
        lid = lid.replace('ü', 'üe')
        lid = lid.replace('ß', 'ss')
        lid = lid.replace('é', 'e')

        # replace whitespace with underscore
        lid = lid.replace(" ", "_")

        # replace other characters with underscore
        lid = lid.replace("-", "_")
        lid = lid.replace(":", "_")

        # only one underscore in a row
        while "__" in lid:
            lid = lid.replace("__", "_")

        # only keep ascii characters
        lid = lid.encode('utf-8').decode('ascii', 'ignore')

        # in case all characters have been removed
        if lid == '':
            lid = uuid.uuid1()

        return lid

    def add_layer_list(self):
        self.modules['wgu-layerlist'] = {
            "target": "menu",
            "win": True,
            "draggable": False
        }

    def add_measuretool(self):
        self.modules['wgu-measuretool'] = {
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
        self.modules['wgu-infoclick'] = {
            "target": "menu",
            "win": True,
            "draggable": False,
            "initPos": {
                "left": 8,
                "top": 74
            }
        }

    def add_button_zoom_to_extent(self):
        self.modules['wgu-zoomtomaxextent'] = {
            "target": "toolbar",
            "darkLayout": True
        }

    def add_help_window(self):
        self.modules['wgu-helpwin'] = {
            "target": "toolbar",
            "darkLayout": True
        }

    def add_geocoder(self):
        self.modules['wgu-geocoder'] = {
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
