from qgis.core import QgsApplication, QgsMessageLog, QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem

import re
from urllib.parse import parse_qs


def center2webmercator(center, qgis_instance):
    """
    Input the center point of the QGIS canvas.
    The QGIS instance object, for computing the source CRS
    and the transformation object.
    Outputs: The Same point in WebMercator(EPSG:3857)
    """

    crs_source = qgis_instance.crs()

    # TODO apparently QgsCoordinateReferenceSystem is deprecated
    
    # define WebMercator(EPSG:3857)
    crs_destination = QgsCoordinateReferenceSystem(3857)

    # transformation object
    xform = QgsCoordinateTransform(crs_source,
                                   crs_destination,
                                   qgis_instance)

    # forward transformation: src -> dest
    center_3857 = xform.transform(center)
    return center_3857


def scale2zoom(scale):
    """
    Takes the scale from QGIS.
    Computes the zoom level for webmaps.
    Only approximation.
    """

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


def identify_wegue_layer_type(layer):
    """
    Matches QGIS layer type to Wegue type
    Wegue types:
    - vector
    - wms
    - xyz
    - (osm)
    """

    wegue_layer_type = 'unknown'
    providerType = layer.providerType().lower()
    if providerType == 'wms':
        # Raster layer distinction proudly taken from the great qgis2web
        # project. All creadits to the qgis2web devs
        # https://github.com/tomchadwin/qgis2web
        source = layer.source()
        d = parse_qs(source)
        if "type" in d and d["type"][0] == "xyz":
            wegue_layer_type = 'XYZ'
        elif "tileMatrixSet" in d:
            wegue_layer_type = 'WMTS' # currently not supported in Wegue
        else:
            wegue_layer_type = 'WMS'

    elif providerType == 'ogr':
        # TODO: find out if vector is in "MVT", "GeoJSON", "TopoJSON", "KML"

        # TODO: use layer name - currently unused
        name = layer.name()


        url = layer.source().split('|')[0]

        if(url.endswith('.kml')):
            wegue_layer_type = 'KML'
        elif(url.endswith('.json') | url.endswith('.geojson')):
            wegue_layer_type = 'GeoJSON'

    return wegue_layer_type


def get_wms_getmap_url(wmsLayer):
    """
    Detects the Get-Map URL for a QGIS WMS layer
    """

    wms_getmap_url = None

    # derive WMS GetMap URL from layer metdata
    htmlMetadata = wmsLayer.htmlMetadata()
    match = re.search('GetMapUrl<\/td><td>(.*)<\/td><\/tr><tr><td>GetFeatureInfoUrl', htmlMetadata)

    layersGroup = match.groups(0)
    wms_getmap_url = ''.join(layersGroup)

    # use source URL as fallback
    if wms_getmap_url is None:
        wms_getmap_url = re.search(r"url=(.*?)(?:&|$)", source).groups(0)[0]

    return wms_getmap_url