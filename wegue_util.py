import re
from owslib.wms import WebMapService
from .wegueConfUtils import (create_vector_layer,
                             create_wfs,
                             create_wms,
                             create_xyz)
from urllib.parse import parse_qs
from qgis.core import (QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)


def center2webmercator(center_point, qgis_instance):
    """Converts a point geometry to EPSG:3857"""

    crs_source = qgis_instance.crs()

    # define WebMercator(EPSG:3857)
    crs_destination = QgsCoordinateReferenceSystem("EPSG:3857")

    # transformation object
    xform = QgsCoordinateTransform(crs_source,
                                   crs_destination,
                                   qgis_instance)

    # forward transformation: src -> dest
    return xform.transform(center_point)


def scale2zoom(scale):
    """Returns approximate zoom level for webmaps"""

    # Scale to Zoom conversion
    # taken from https://wiki.openstreetmap.org/wiki/Zoom_levels
    scale_dict = {
        500000000: 0,
        250000000: 1,
        150000000: 2,
        70000000: 3,
        35000000: 4,
        15000000: 5,
        10000000: 6,
        4000000	: 7,
        2000000	: 8,
        1000000: 9,
        500000: 10,
        250000: 11,
        150000: 12,
        70000: 13,
        35000: 14,
        15000: 15,
        8000: 16,
        4000: 17,
        2000: 18
    }
    scale_list = scale_dict.keys()

    # get closest scale
    closest_scale = min(scale_list, key=lambda x: abs(x - scale))

    # query respective zoom level
    return scale_dict[closest_scale]


def get_wfs_properties(source):
    """Extracts the WFS properties from the layer source"""

    # manually converting source into dict
    source = source.strip()
    items = source.split(" ")

    # built property dict
    props = {}
    for i in items:
        # extract keys and values
        spl = i.split("=")
        k, v = spl[0], spl[1]

        # remove single quote
        v = v.replace("'", "")

        # handle keys that appear
        props[k] = v
    return props


def get_geometry_type_name(layer):
    """
    Translates QGIS Geometry Type codes into human-readable
    geometry types: "Point", "LineString", "Polygon"
    """
    geom_type = layer.geometryType()

    result = ""
    if geom_type == 0:
        result = "Point"
    elif geom_type == 1:
        result = "LineString"
    elif geom_type == 2:
        result = "Polygon"

    return result


def extract_wegue_layer_config(layer):
    """
    Extracts all relevant information from a QGIS layer
    and converts it to a Wegue layer configuration
    """

    providerType = layer.providerType().lower()
    source = layer.source()

    # same for all types
    name = layer.name()

    if providerType == "wms":
        # Raster layer distinction proudly taken from the great qgis2web
        # project. All credits to the qgis2web devs
        # https://github.com/tomchadwin/qgis2web
        layer_props = parse_qs(source)

        # XYZ
        if "type" in layer_props and layer_props["type"][0] == "xyz":
            url = layer_props["url"][0]

            # in case no attribution is available
            attributions = ""
            if "referer" in layer_props:
                attributions = layer_props["referer"][0]

            return create_xyz(
                name, url, attributions=attributions)

        # WMTS - currently not supported in Wegue
        elif "tileMatrixSet" in layer_props:
            pass

        # WMS
        else:

            d = parse_qs(source)

            url_get_capabilities = d['url'][0]
            layers_wms_property = d['layers'][0]

            # request getMap URL via OWSLib
            wms = WebMapService(url_get_capabilities)
            url_get_map = wms.getOperationByName('GetMap').methods[0]['url']

            return create_wms(name, url_get_map, layers_wms_property)

    # KML or GeoJSON
    elif providerType == "ogr":

        url = source.split("|")[0]

        if(url.endswith(".kml") |
                url.endswith(".json") |
                url.endswith(".geojson")):

            url = source.split("|")[0]

            geometry_type_name = get_geometry_type_name(layer)

            formatMapping = "GeoJSON"
            if url.endswith(".kml"):
                formatMapping = "KML"

            return create_vector_layer(
                name, url, formatMapping,
                geometryTypeName=geometry_type_name)

    # WFS
    elif providerType == "wfs":

        props = get_wfs_properties(source)

        typename = props["typename"]
        url = props["url"]

        geometry_type_name = get_geometry_type_name(layer)

        # Extent
        source_extent = layer.sourceExtent()
        minx = source_extent.xMinimum()
        miny = source_extent.yMinimum()
        maxx = source_extent.xMaximum()
        maxy = source_extent.yMaximum()
        extent = [minx, miny, maxx, maxy]

        return create_wfs(
            name, url, typename,
            geometryTypeName=geometry_type_name,
            extent=extent)

    # Provider Type not supported
    else:
        return None
